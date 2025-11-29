#!/usr/bin/env python3
"""
Agent Server - Internal API for Claude Code agents
Runs inside each agent container on port 8000 (internal Docker network only)

SECURITY: This server is NOT exposed externally. All access goes through
the authenticated Trinity backend at /api/agents/{name}/chat

The HTML UI has been removed for security - use the Trinity web interface instead.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import subprocess
import os
import json
from datetime import datetime
from pathlib import Path
import logging
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread pool for running blocking subprocess operations
# This allows FastAPI to handle other requests (like /api/activity polling) during execution
_executor = ThreadPoolExecutor(max_workers=2)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Claude Agent API",
    description="Internal API for Claude Code agent (not exposed externally)",
    version="2.0.0"
)

# CORS - only needed for internal Docker network communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Backend communicates via internal network
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Data Models
# ============================================================================

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = None

class ChatRequest(BaseModel):
    message: str
    stream: bool = False
    model: Optional[str] = None  # Model to use: sonnet, opus, haiku, or full model name

class CredentialUpdateRequest(BaseModel):
    credentials: dict  # {"VAR_NAME": "value", ...}
    mcp_config: Optional[str] = None  # Pre-generated .mcp.json content (if provided)

class AgentInfo(BaseModel):
    name: str
    status: str
    claude_version: Optional[str] = None
    mcp_servers: List[str] = []
    uptime: Optional[str] = None

class ExecutionLogEntry(BaseModel):
    """A single entry in the execution log (tool_use or tool_result)"""
    id: str
    type: str  # "tool_use" or "tool_result"
    tool: str
    input: Optional[Dict[str, Any]] = None
    success: Optional[bool] = None
    duration_ms: Optional[int] = None
    timestamp: str

class ExecutionMetadata(BaseModel):
    """Metadata about the Claude Code execution"""
    cost_usd: Optional[float] = None
    duration_ms: Optional[int] = None
    num_turns: Optional[int] = None
    tool_count: int = 0
    session_id: Optional[str] = None
    # Token tracking for context window
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    context_window: int = 200000  # Default max context


# ============================================================================
# Session Activity Models (for real-time monitoring)
# ============================================================================

class TimelineEntry(BaseModel):
    """A single entry in the session activity timeline"""
    id: str
    tool: str
    input: Optional[Dict[str, Any]] = None
    input_summary: str
    output_summary: Optional[str] = None
    duration_ms: Optional[int] = None
    started_at: str
    ended_at: Optional[str] = None
    success: Optional[bool] = None
    status: str  # "running" | "completed"


class ActiveTool(BaseModel):
    """Currently running tool"""
    name: str
    input_summary: str
    started_at: str


class SessionTotals(BaseModel):
    """Aggregate totals for the session"""
    calls: int = 0
    duration_ms: int = 0
    started_at: Optional[str] = None


class SessionActivity(BaseModel):
    """Session-wide activity tracking"""
    status: str = "idle"  # "running" | "idle"
    active_tool: Optional[ActiveTool] = None
    tool_counts: Dict[str, int] = {}
    timeline: List[TimelineEntry] = []
    totals: SessionTotals = SessionTotals()


class ToolCallDetail(BaseModel):
    """Full detail for a single tool call (for drill-down)"""
    id: str
    tool: str
    input: Optional[Dict[str, Any]] = None
    output: Optional[str] = None
    duration_ms: Optional[int] = None
    started_at: str
    ended_at: Optional[str] = None
    success: Optional[bool] = None

class ChatResponse(BaseModel):
    """Enhanced chat response with execution log"""
    response: str
    execution_log: List[ExecutionLogEntry] = []
    metadata: ExecutionMetadata
    timestamp: str

# ============================================================================
# Agent State
# ============================================================================

class AgentState:
    def __init__(self):
        self.conversation_history: List[ChatMessage] = []
        self.agent_name = os.getenv("AGENT_NAME", "unknown")
        self.claude_code_available = self._check_claude_code()
        self.session_started = False  # Track if we've started a conversation
        # Session-level token tracking
        self.session_total_cost: float = 0.0
        self.session_total_output_tokens: int = 0
        self.session_context_tokens: int = 0  # Latest context size
        self.session_context_window: int = 200000  # Max context
        # Model selection (persists across session)
        self.current_model: Optional[str] = os.getenv("CLAUDE_MODEL", None)  # Default from env or None
        # Session activity tracking (for real-time monitoring)
        self.session_activity = self._create_empty_activity()
        # Store full tool outputs for drill-down (separate from timeline summaries)
        self.tool_outputs: Dict[str, str] = {}

    def _create_empty_activity(self) -> Dict:
        """Create empty session activity structure"""
        return {
            "status": "idle",
            "active_tool": None,
            "tool_counts": {},
            "timeline": [],
            "totals": {
                "calls": 0,
                "duration_ms": 0,
                "started_at": None
            }
        }

    def _check_claude_code(self) -> bool:
        """Check if Claude Code CLI is available"""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Claude Code check failed: {e}")
            return False

    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append(
            ChatMessage(
                role=role,
                content=content,
                timestamp=datetime.now()
            )
        )

    def reset_session(self):
        """Reset conversation state and token tracking"""
        self.conversation_history = []
        self.session_started = False
        self.session_total_cost = 0.0
        self.session_total_output_tokens = 0
        self.session_context_tokens = 0
        # Note: current_model is NOT reset - it persists until explicitly changed
        # Reset session activity tracking
        self.session_activity = self._create_empty_activity()
        self.tool_outputs = {}

agent_state = AgentState()

# ============================================================================
# Session Activity Helpers
# ============================================================================

def get_tool_name(tool: str, input_data: Dict[str, Any]) -> str:
    """Get display name for tool, adding prefixes for MCP and sub-agents"""
    # Check if it's an MCP tool (usually has specific patterns)
    if tool.startswith("mcp__"):
        # Convert mcp__server__tool to mcp:server
        parts = tool.split("__")
        if len(parts) >= 2:
            return f"mcp:{parts[1]}"
        return f"mcp:{tool}"

    # Check if it's a Task (sub-agent)
    if tool == "Task":
        subagent_type = input_data.get("subagent_type", "")
        if subagent_type:
            return f"Task:{subagent_type}"
        return "Task"

    return tool


def get_input_summary(tool: str, input_data: Dict[str, Any]) -> str:
    """Generate a human-readable summary of tool input"""
    if not input_data:
        return "..."

    if tool == "Read":
        path = input_data.get("file_path", "")
        return shorten_path(path)
    elif tool == "Edit":
        path = input_data.get("file_path", "")
        return shorten_path(path)
    elif tool == "Write":
        path = input_data.get("file_path", "")
        return shorten_path(path)
    elif tool == "Glob":
        return input_data.get("pattern", "...")
    elif tool == "Grep":
        pattern = input_data.get("pattern", "")
        return f'"{pattern[:30]}"' if pattern else "..."
    elif tool == "Bash":
        cmd = input_data.get("command", "")
        return cmd[:50] + ("..." if len(cmd) > 50 else "")
    elif tool == "Task":
        return input_data.get("description", input_data.get("prompt", "...")[:50])
    elif tool == "WebFetch":
        url = input_data.get("url", "")
        return shorten_url(url)
    elif tool == "WebSearch":
        return input_data.get("query", "...")[:40]
    elif tool == "TodoWrite":
        return "Updating todos"
    elif tool == "AskUserQuestion":
        return "Asking question"
    else:
        # For MCP tools or unknown tools, try to get first param
        for key, value in input_data.items():
            if isinstance(value, str) and len(value) < 50:
                return f"{key}: {value[:30]}"
            elif isinstance(value, str):
                return f"{key}: {value[:30]}..."
        return "..."


def shorten_path(path: str) -> str:
    """Shorten file path for display"""
    if not path:
        return "..."
    parts = path.split('/')
    if len(parts) <= 2:
        return path
    return f".../{'/'.join(parts[-2:])}"


def shorten_url(url: str) -> str:
    """Shorten URL for display"""
    if not url:
        return "..."
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.hostname or url[:30]
    except:
        return url[:30]


def truncate_output(output: str, max_length: int = 500) -> str:
    """Truncate output for summary, preserving beginning"""
    if not output:
        return ""
    if len(output) <= max_length:
        return output
    return output[:max_length] + "..."


def start_tool_execution(tool_id: str, tool: str, input_data: Dict[str, Any]):
    """Record start of a tool execution"""
    now = datetime.now()
    display_name = get_tool_name(tool, input_data)
    input_summary = get_input_summary(tool, input_data)

    # Set session as running
    agent_state.session_activity["status"] = "running"
    agent_state.session_activity["active_tool"] = {
        "name": display_name,
        "input_summary": input_summary,
        "started_at": now.isoformat()
    }

    # Initialize totals.started_at if this is the first call
    if agent_state.session_activity["totals"]["started_at"] is None:
        agent_state.session_activity["totals"]["started_at"] = now.isoformat()

    # Add to timeline (newest first)
    timeline_entry = {
        "id": tool_id,
        "tool": display_name,
        "input": input_data,
        "input_summary": input_summary,
        "output_summary": None,
        "duration_ms": None,
        "started_at": now.isoformat(),
        "ended_at": None,
        "success": None,
        "status": "running"
    }
    # Insert at beginning (newest first)
    agent_state.session_activity["timeline"].insert(0, timeline_entry)

    # Update tool counts
    if display_name not in agent_state.session_activity["tool_counts"]:
        agent_state.session_activity["tool_counts"][display_name] = 0
    agent_state.session_activity["tool_counts"][display_name] += 1

    # Update totals
    agent_state.session_activity["totals"]["calls"] += 1


def complete_tool_execution(tool_id: str, success: bool, output: str = None):
    """Record completion of a tool execution"""
    now = datetime.now()

    # Find the timeline entry
    for entry in agent_state.session_activity["timeline"]:
        if entry["id"] == tool_id and entry["status"] == "running":
            started_at = datetime.fromisoformat(entry["started_at"])
            duration_ms = int((now - started_at).total_seconds() * 1000)

            entry["ended_at"] = now.isoformat()
            entry["duration_ms"] = duration_ms
            entry["success"] = success
            entry["status"] = "completed"
            entry["output_summary"] = truncate_output(output) if output else None

            # Update total duration
            agent_state.session_activity["totals"]["duration_ms"] += duration_ms
            break

    # Store full output for drill-down
    if output:
        agent_state.tool_outputs[tool_id] = output

    # Clear active tool
    agent_state.session_activity["active_tool"] = None

    # Check if there are any other running tools
    has_running = any(e["status"] == "running" for e in agent_state.session_activity["timeline"])
    if not has_running:
        agent_state.session_activity["status"] = "idle"


# ============================================================================
# Claude Code Integration
# ============================================================================

def parse_stream_json_output(output: str) -> tuple[str, List[ExecutionLogEntry], ExecutionMetadata]:
    """
    Parse stream-json output from Claude Code.

    Stream-json format emits one JSON object per line:
    - {"type": "init", "session_id": "abc123", ...}
    - {"type": "user", "message": {...}}
    - {"type": "assistant", "message": {"content": [{"type": "tool_use", ...}, ...]}}
    - {"type": "result", "total_cost_usd": 0.003, ...}

    Returns: (response_text, execution_log, metadata)
    """
    execution_log: List[ExecutionLogEntry] = []
    metadata = ExecutionMetadata()
    response_text = ""
    tool_start_times: Dict[str, datetime] = {}  # Track when tools started

    for line in output.strip().split('\n'):
        if not line.strip():
            continue

        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse line as JSON: {line[:100]}")
            continue

        msg_type = msg.get("type")

        if msg_type == "init":
            metadata.session_id = msg.get("session_id")

        elif msg_type == "result":
            # Final result message with stats
            metadata.cost_usd = msg.get("total_cost_usd")
            metadata.duration_ms = msg.get("duration_ms")
            metadata.num_turns = msg.get("num_turns")
            response_text = msg.get("result", response_text)

            # Extract token usage from result.usage
            usage = msg.get("usage", {})
            metadata.input_tokens = usage.get("input_tokens", 0)
            metadata.output_tokens = usage.get("output_tokens", 0)
            metadata.cache_creation_tokens = usage.get("cache_creation_input_tokens", 0)
            metadata.cache_read_tokens = usage.get("cache_read_input_tokens", 0)

            # Extract context window from modelUsage (if available)
            model_usage = msg.get("modelUsage", {})
            for model_name, model_data in model_usage.items():
                if "contextWindow" in model_data:
                    metadata.context_window = model_data["contextWindow"]
                    break

        elif msg_type == "assistant":
            message_content = msg.get("message", {}).get("content", [])

            for content_block in message_content:
                block_type = content_block.get("type")

                if block_type == "tool_use":
                    # Tool is being called
                    tool_id = content_block.get("id", str(uuid.uuid4()))
                    tool_name = content_block.get("name", "Unknown")
                    tool_input = content_block.get("input", {})
                    timestamp = datetime.now()

                    tool_start_times[tool_id] = timestamp

                    execution_log.append(ExecutionLogEntry(
                        id=tool_id,
                        type="tool_use",
                        tool=tool_name,
                        input=tool_input,
                        timestamp=timestamp.isoformat()
                    ))

                    # Update session activity
                    start_tool_execution(tool_id, tool_name, tool_input)

                elif block_type == "tool_result":
                    # Tool result returned
                    tool_id = content_block.get("tool_use_id", "")
                    is_error = content_block.get("is_error", False)
                    timestamp = datetime.now()

                    # Extract output content for session activity
                    tool_output = ""
                    result_content = content_block.get("content", [])
                    if isinstance(result_content, list):
                        for item in result_content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                tool_output = item.get("text", "")
                                break
                    elif isinstance(result_content, str):
                        tool_output = result_content

                    # Calculate duration if we have start time
                    duration_ms = None
                    if tool_id in tool_start_times:
                        delta = timestamp - tool_start_times[tool_id]
                        duration_ms = int(delta.total_seconds() * 1000)

                    # Find the corresponding tool_use entry to get tool name
                    tool_name = "Unknown"
                    for entry in execution_log:
                        if entry.id == tool_id and entry.type == "tool_use":
                            tool_name = entry.tool
                            break

                    execution_log.append(ExecutionLogEntry(
                        id=tool_id,
                        type="tool_result",
                        tool=tool_name,
                        success=not is_error,
                        duration_ms=duration_ms,
                        timestamp=timestamp.isoformat()
                    ))

                    # Update session activity
                    complete_tool_execution(tool_id, not is_error, tool_output)

                elif block_type == "text":
                    # Claude's text response - accumulate it
                    text = content_block.get("text", "")
                    if text:
                        if response_text:
                            response_text += "\n" + text
                        else:
                            response_text = text

    # Count unique tools used
    tool_use_count = len([e for e in execution_log if e.type == "tool_use"])
    metadata.tool_count = tool_use_count

    return response_text, execution_log, metadata


def process_stream_line(line: str, execution_log: List[ExecutionLogEntry], metadata: ExecutionMetadata,
                         tool_start_times: Dict[str, datetime], response_parts: List[str]) -> None:
    """
    Process a single line of stream-json output in real-time.
    Updates session activity, execution_log, metadata, and response_parts in place.
    """
    if not line.strip():
        return

    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse line as JSON: {line[:100]}")
        return

    msg_type = msg.get("type")

    if msg_type == "init":
        metadata.session_id = msg.get("session_id")

    elif msg_type == "result":
        # Final result message with stats
        metadata.cost_usd = msg.get("total_cost_usd")
        metadata.duration_ms = msg.get("duration_ms")
        metadata.num_turns = msg.get("num_turns")
        result_text = msg.get("result", "")
        if result_text:
            response_parts.clear()
            response_parts.append(result_text)

        # Extract token usage from result.usage
        usage = msg.get("usage", {})
        metadata.input_tokens = usage.get("input_tokens", 0)
        metadata.output_tokens = usage.get("output_tokens", 0)
        metadata.cache_creation_tokens = usage.get("cache_creation_input_tokens", 0)
        metadata.cache_read_tokens = usage.get("cache_read_input_tokens", 0)

        # Extract context window from modelUsage (if available)
        model_usage = msg.get("modelUsage", {})
        for model_name, model_data in model_usage.items():
            if "contextWindow" in model_data:
                metadata.context_window = model_data["contextWindow"]
                break

    elif msg_type == "assistant" or msg_type == "user":
        # Handle both assistant and user message types
        # tool_use appears in assistant messages, tool_result may appear in either
        message_content = msg.get("message", {}).get("content", [])

        for content_block in message_content:
            block_type = content_block.get("type")

            if block_type == "tool_use":
                # Tool is being called - update IMMEDIATELY
                tool_id = content_block.get("id", str(uuid.uuid4()))
                tool_name = content_block.get("name", "Unknown")
                tool_input = content_block.get("input", {})
                timestamp = datetime.now()

                tool_start_times[tool_id] = timestamp

                execution_log.append(ExecutionLogEntry(
                    id=tool_id,
                    type="tool_use",
                    tool=tool_name,
                    input=tool_input,
                    timestamp=timestamp.isoformat()
                ))

                # Update session activity in real-time
                start_tool_execution(tool_id, tool_name, tool_input)
                logger.debug(f"Tool started: {tool_name} ({tool_id})")

            elif block_type == "tool_result":
                # Tool result returned - update IMMEDIATELY
                tool_id = content_block.get("tool_use_id", "")
                is_error = content_block.get("is_error", False)
                timestamp = datetime.now()

                # Extract output content for session activity
                tool_output = ""
                result_content = content_block.get("content", [])
                if isinstance(result_content, list):
                    for item in result_content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            tool_output = item.get("text", "")
                            break
                elif isinstance(result_content, str):
                    tool_output = result_content

                # Calculate duration if we have start time
                duration_ms = None
                if tool_id in tool_start_times:
                    delta = timestamp - tool_start_times[tool_id]
                    duration_ms = int(delta.total_seconds() * 1000)

                # Find the corresponding tool_use entry to get tool name
                tool_name = "Unknown"
                for entry in execution_log:
                    if entry.id == tool_id and entry.type == "tool_use":
                        tool_name = entry.tool
                        break

                execution_log.append(ExecutionLogEntry(
                    id=tool_id,
                    type="tool_result",
                    tool=tool_name,
                    success=not is_error,
                    duration_ms=duration_ms,
                    timestamp=timestamp.isoformat()
                ))

                # Update session activity in real-time
                complete_tool_execution(tool_id, not is_error, tool_output)
                logger.debug(f"Tool completed: {tool_name} ({tool_id}) - success={not is_error}")

            elif block_type == "text":
                # Claude's text response - accumulate it
                text = content_block.get("text", "")
                if text:
                    response_parts.append(text)


async def execute_claude_code(prompt: str, stream: bool = False, model: Optional[str] = None) -> tuple[str, List[ExecutionLogEntry], ExecutionMetadata]:
    """
    Execute Claude Code in headless mode with the given prompt.

    Uses streaming subprocess to update session activity in REAL-TIME as tools execute.

    Uses: claude --print --output-format stream-json
    Uses --continue flag for subsequent messages to maintain conversation context
    Uses --model to select Claude model (sonnet, opus, haiku, or full model name)

    Returns: (response_text, execution_log, metadata)
    """

    if not agent_state.claude_code_available:
        raise HTTPException(
            status_code=503,
            detail="Claude Code is not available in this container"
        )

    try:
        # Get ANTHROPIC_API_KEY from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="ANTHROPIC_API_KEY not configured in agent container"
            )

        # Update model if specified (persists for session)
        if model:
            agent_state.current_model = model
            logger.info(f"Model set to: {model}")

        # Build command - use --continue for subsequent messages
        # Use stream-json for detailed execution log (requires --verbose)
        cmd = ["claude", "--print", "--output-format", "stream-json", "--verbose", "--dangerously-skip-permissions"]

        # Add model selection if set
        if agent_state.current_model:
            cmd.extend(["--model", agent_state.current_model])
            logger.info(f"Using model: {agent_state.current_model}")

        if agent_state.session_started:
            # Continue the existing conversation
            cmd.append("--continue")
            logger.info("Continuing existing conversation session")
        else:
            # First message in session
            agent_state.session_started = True
            logger.info("Starting new conversation session")

        # Initialize tracking structures
        execution_log: List[ExecutionLogEntry] = []
        metadata = ExecutionMetadata()
        tool_start_times: Dict[str, datetime] = {}
        response_parts: List[str] = []

        # Mark session as potentially running (will be set to running when first tool starts)
        logger.info(f"Starting Claude Code with streaming: {' '.join(cmd[:5])}...")

        # Use Popen for real-time streaming instead of blocking run()
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )

        # Write prompt to stdin and close it
        process.stdin.write(prompt)
        process.stdin.close()

        # Helper function that reads subprocess output (runs in thread pool)
        def read_subprocess_output():
            """Blocking function to read subprocess output line by line"""
            try:
                for line in iter(process.stdout.readline, ''):
                    if not line:
                        break
                    # Process each line immediately - updates session_activity in real-time
                    process_stream_line(line, execution_log, metadata, tool_start_times, response_parts)
            except Exception as e:
                logger.error(f"Error reading Claude output: {e}")

            # Wait for process to complete and get stderr
            stderr = process.stderr.read()
            return_code = process.wait()
            return stderr, return_code

        # Run the blocking subprocess reading in a thread pool to allow FastAPI
        # to handle other requests (like /api/activity polling) during execution
        loop = asyncio.get_event_loop()
        stderr_output, return_code = await loop.run_in_executor(_executor, read_subprocess_output)

        # Check for errors
        if return_code != 0:
            logger.error(f"Claude Code failed (exit {return_code}): {stderr_output[:500]}")
            raise HTTPException(
                status_code=500,
                detail=f"Claude Code execution failed: {stderr_output[:200] if stderr_output else 'Unknown error'}"
            )

        # Build final response text
        response_text = "\n".join(response_parts) if response_parts else ""

        if not response_text:
            raise HTTPException(
                status_code=500,
                detail="Claude Code returned empty response"
            )

        # Count unique tools used
        tool_use_count = len([e for e in execution_log if e.type == "tool_use"])
        metadata.tool_count = tool_use_count

        # Log metadata for debugging
        total_context = metadata.input_tokens + metadata.cache_creation_tokens + metadata.cache_read_tokens
        logger.info(f"Claude response: cost=${metadata.cost_usd}, duration={metadata.duration_ms}ms, tools={metadata.tool_count}, context={total_context}/{metadata.context_window}")

        return response_text, execution_log, metadata

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Claude Code execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

# ============================================================================
# API Endpoints (Internal use only - accessed via Trinity backend proxy)
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - no UI, just API info"""
    return {
        "service": "Trinity Agent API",
        "agent": agent_state.agent_name,
        "status": "running",
        "note": "This is an internal API. Use the Trinity web interface to chat with agents.",
        "endpoints": {
            "chat": "POST /api/chat",
            "history": "GET /api/chat/history",
            "info": "GET /api/agent/info",
            "health": "GET /health"
        }
    }

@app.get("/api/agent/info")
async def get_agent_info():
    """Get agent information"""

    # Read agent config if available
    config_path = "/config/agent-config.yaml"
    mcp_servers = []

    if os.path.exists(config_path):
        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
                mcp_servers = config.get("agent", {}).get("mcp_servers", [])
        except Exception as e:
            logger.error(f"Failed to read agent config: {e}")

    return AgentInfo(
        name=agent_state.agent_name,
        status="running",
        claude_version="2.0.49" if agent_state.claude_code_available else None,
        mcp_servers=mcp_servers,
        uptime=None  # TODO: Calculate uptime
    )

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Send a message to Claude Code and get response with execution log"""

    # Add user message to history
    agent_state.add_message("user", request.message)

    # Execute Claude Code - now returns (response, execution_log, metadata)
    response_text, execution_log, metadata = await execute_claude_code(
        request.message,
        stream=request.stream,
        model=request.model
    )

    # Add assistant response to history
    agent_state.add_message("assistant", response_text)

    # Update session-level stats
    if metadata.cost_usd:
        agent_state.session_total_cost += metadata.cost_usd
    agent_state.session_total_output_tokens += metadata.output_tokens
    agent_state.session_context_tokens = (
        metadata.input_tokens +
        metadata.cache_creation_tokens +
        metadata.cache_read_tokens
    )
    agent_state.session_context_window = metadata.context_window

    # Return enhanced response with execution log and session stats
    return {
        "response": response_text,
        "execution_log": [entry.model_dump() for entry in execution_log],
        "metadata": metadata.model_dump(),
        "session": {
            "total_cost_usd": agent_state.session_total_cost,
            "context_tokens": agent_state.session_context_tokens,
            "context_window": agent_state.session_context_window,
            "message_count": len(agent_state.conversation_history),
            "model": agent_state.current_model
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/chat/history")
async def get_chat_history():
    """Get conversation history"""
    return agent_state.conversation_history

@app.get("/api/chat/session")
async def get_session_info():
    """Get current session information including token usage"""
    return {
        "session_started": agent_state.session_started,
        "message_count": len(agent_state.conversation_history),
        "total_cost_usd": agent_state.session_total_cost,
        "context_tokens": agent_state.session_context_tokens,
        "context_window": agent_state.session_context_window,
        "context_percent": round(
            (agent_state.session_context_tokens / agent_state.session_context_window) * 100, 1
        ) if agent_state.session_context_window > 0 else 0,
        "model": agent_state.current_model
    }

class ModelRequest(BaseModel):
    model: str  # Model alias: sonnet, opus, haiku, or full model name

@app.get("/api/model")
async def get_model():
    """Get the current model being used"""
    return {
        "model": agent_state.current_model,
        "available_models": ["sonnet", "opus", "haiku"],
        "note": "Model aliases: sonnet (Sonnet 4.5), opus (Opus 4.5), haiku. Add [1m] suffix for 1M context (e.g., sonnet[1m])"
    }

@app.put("/api/model")
async def set_model(request: ModelRequest):
    """Set the model to use for subsequent messages"""
    valid_aliases = ["sonnet", "opus", "haiku", "sonnet[1m]", "opus[1m]", "haiku[1m]"]

    # Accept aliases or full model names (e.g., claude-sonnet-4-5-20250929)
    if request.model in valid_aliases or request.model.startswith("claude-"):
        agent_state.current_model = request.model
        logger.info(f"Model changed to: {request.model}")
        return {
            "status": "success",
            "model": agent_state.current_model,
            "note": "Model will be used for subsequent messages"
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model: {request.model}. Use aliases (sonnet, opus, haiku) or full model names."
        )

@app.delete("/api/chat/history")
async def clear_chat_history():
    """Clear conversation history and reset session"""
    agent_state.reset_session()
    return {
        "status": "cleared",
        "session_reset": True,
        "session": {
            "total_cost_usd": 0.0,
            "context_tokens": 0,
            "context_window": agent_state.session_context_window,
            "message_count": 0
        }
    }

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming chat (internal use)"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Add user message
            agent_state.add_message("user", message["content"])

            # Send response with execution log
            response_text, execution_log, metadata = await execute_claude_code(message["content"], stream=True)
            agent_state.add_message("assistant", response_text)

            await websocket.send_json({
                "type": "message",
                "role": "assistant",
                "content": response_text,
                "execution_log": [entry.model_dump() for entry in execution_log],
                "metadata": metadata.model_dump()
            })
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_name": agent_state.agent_name,
        "claude_available": agent_state.claude_code_available,
        "message_count": len(agent_state.conversation_history)
    }


# ============================================================================
# Session Activity Endpoints (for real-time monitoring)
# ============================================================================

@app.get("/api/activity")
async def get_session_activity():
    """
    Get session activity summary for real-time monitoring.

    Returns the current session activity including:
    - status: "running" or "idle"
    - active_tool: currently executing tool (if any)
    - tool_counts: count of each tool used
    - timeline: list of tool executions (newest first)
    - totals: aggregate statistics
    """
    return agent_state.session_activity


@app.get("/api/activity/{tool_id}")
async def get_tool_call_detail(tool_id: str):
    """
    Get full details for a specific tool call.

    Returns the complete input and output for drill-down inspection.
    """
    # Find the timeline entry
    for entry in agent_state.session_activity["timeline"]:
        if entry["id"] == tool_id:
            # Get full output from tool_outputs if available
            full_output = agent_state.tool_outputs.get(tool_id, entry.get("output_summary", ""))

            return {
                "id": entry["id"],
                "tool": entry["tool"],
                "input": entry["input"],
                "output": full_output,
                "duration_ms": entry["duration_ms"],
                "started_at": entry["started_at"],
                "ended_at": entry["ended_at"],
                "success": entry["success"]
            }

    raise HTTPException(status_code=404, detail=f"Tool call {tool_id} not found")


@app.delete("/api/activity")
async def clear_session_activity():
    """
    Clear session activity (called when starting a new session).

    This only clears the activity tracking, not the conversation history.
    Use DELETE /api/chat/history to clear everything.
    """
    agent_state.session_activity = agent_state._create_empty_activity()
    agent_state.tool_outputs = {}
    return {
        "status": "cleared",
        "message": "Session activity cleared"
    }


# ============================================================================
# Credential Management (Internal - called by Trinity backend)
# ============================================================================

@app.post("/api/credentials/update")
async def update_credentials(request: CredentialUpdateRequest):
    """
    Update agent credentials by writing .env and regenerating .mcp.json.

    This endpoint is called by the Trinity backend when credentials are updated.
    It writes the new credentials to files that MCP servers read at startup/runtime.

    Flow:
    1. Write credentials to /home/developer/.env
    2. If mcp_config provided, write to /home/developer/.mcp.json
    3. If .mcp.json.template exists, generate .mcp.json from it using envsubst
    """
    home_dir = Path("/home/developer")
    env_file = home_dir / ".env"
    mcp_file = home_dir / ".mcp.json"
    mcp_template = home_dir / ".mcp.json.template"

    updated_files = []

    try:
        # 1. Write .env file
        env_lines = ["# Generated by Trinity - Agent credentials", ""]
        for var_name, value in request.credentials.items():
            # Escape special characters in values
            escaped_value = str(value).replace('"', '\\"')
            env_lines.append(f'{var_name}="{escaped_value}"')

        env_content = "\n".join(env_lines) + "\n"
        env_file.write_text(env_content)
        updated_files.append(str(env_file))
        logger.info(f"Updated .env with {len(request.credentials)} credentials")

        # 2. Handle .mcp.json generation
        if request.mcp_config:
            # If backend provides pre-generated .mcp.json, use it
            mcp_file.write_text(request.mcp_config)
            updated_files.append(str(mcp_file))
            logger.info("Updated .mcp.json from provided config")

        elif mcp_template.exists():
            # Generate .mcp.json from template using envsubst-style substitution
            template_content = mcp_template.read_text()

            # Perform variable substitution (${VAR_NAME} -> value)
            generated_content = template_content
            for var_name, value in request.credentials.items():
                placeholder = f"${{{var_name}}}"
                generated_content = generated_content.replace(placeholder, str(value))

            mcp_file.write_text(generated_content)
            updated_files.append(str(mcp_file))
            logger.info("Generated .mcp.json from template")

        # 3. Also export credentials to environment (for current process)
        # Note: This won't affect already-running subprocesses, but helps for new ones
        for var_name, value in request.credentials.items():
            os.environ[var_name] = str(value)

        return {
            "status": "success",
            "updated_files": updated_files,
            "credential_count": len(request.credentials),
            "note": "MCP servers may need to be restarted to pick up new credentials"
        }

    except Exception as e:
        logger.error(f"Failed to update credentials: {e}")
        raise HTTPException(status_code=500, detail=f"Credential update failed: {str(e)}")


# ============================================================================
# Git Sync Endpoints (Phase 7: GitHub Bidirectional Sync)
# ============================================================================

class GitSyncRequest(BaseModel):
    """Request for git sync operation"""
    message: Optional[str] = None  # Custom commit message
    paths: Optional[List[str]] = None  # Specific paths to sync (default: all)


class GitCommitInfo(BaseModel):
    """Git commit information"""
    sha: str
    short_sha: str
    message: str
    author: str
    date: str


@app.get("/api/git/status")
async def get_git_status():
    """
    Get git repository status including current branch, changes, and sync state.
    Only available for agents with git sync enabled.
    """
    home_dir = Path("/home/developer")
    git_dir = home_dir / ".git"

    if not git_dir.exists():
        return {
            "git_enabled": False,
            "message": "Git sync not enabled for this agent"
        }

    try:
        # Get current branch
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=10
        )
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

        # Get status (modified, untracked files)
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=10
        )
        changes = []
        if status_result.returncode == 0 and status_result.stdout.strip():
            for line in status_result.stdout.strip().split('\n'):
                if line:
                    status_code = line[:2]
                    filepath = line[3:]
                    changes.append({
                        "status": status_code.strip(),
                        "path": filepath
                    })

        # Get last commit
        log_result = subprocess.run(
            ["git", "log", "-1", "--format=%H|%h|%s|%an|%ai"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=10
        )
        last_commit = None
        if log_result.returncode == 0 and log_result.stdout.strip():
            parts = log_result.stdout.strip().split('|')
            if len(parts) >= 5:
                last_commit = {
                    "sha": parts[0],
                    "short_sha": parts[1],
                    "message": parts[2],
                    "author": parts[3],
                    "date": parts[4]
                }

        # Check if we're ahead/behind remote
        fetch_result = subprocess.run(
            ["git", "fetch", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=30
        )

        ahead_behind_result = subprocess.run(
            ["git", "rev-list", "--left-right", "--count", f"origin/{current_branch}...HEAD"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=10
        )
        ahead = 0
        behind = 0
        if ahead_behind_result.returncode == 0:
            parts = ahead_behind_result.stdout.strip().split()
            if len(parts) == 2:
                behind = int(parts[0])
                ahead = int(parts[1])

        # Get remote URL (without credentials)
        remote_result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=10
        )
        remote_url = ""
        if remote_result.returncode == 0:
            url = remote_result.stdout.strip()
            # Remove credentials from URL for display
            if '@github.com' in url:
                remote_url = "https://github.com/" + url.split('@github.com/')[1]
            else:
                remote_url = url

        return {
            "git_enabled": True,
            "branch": current_branch,
            "remote_url": remote_url,
            "last_commit": last_commit,
            "changes": changes,
            "changes_count": len(changes),
            "ahead": ahead,
            "behind": behind,
            "sync_status": "up_to_date" if ahead == 0 and len(changes) == 0 else "pending_sync"
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Git operation timed out")
    except Exception as e:
        logger.error(f"Git status error: {e}")
        raise HTTPException(status_code=500, detail=f"Git status error: {str(e)}")


@app.post("/api/git/sync")
async def sync_to_github(request: GitSyncRequest):
    """
    Sync local changes to GitHub by staging, committing, and pushing.

    Steps:
    1. Stage all changes (or specific paths if provided)
    2. Create a commit with the provided message (or auto-generated)
    3. Force push to the working branch

    Returns the commit SHA on success.
    """
    home_dir = Path("/home/developer")
    git_dir = home_dir / ".git"

    if not git_dir.exists():
        raise HTTPException(status_code=400, detail="Git sync not enabled for this agent")

    try:
        # 1. Stage changes
        if request.paths:
            # Stage specific paths
            for path in request.paths:
                add_result = subprocess.run(
                    ["git", "add", path],
                    capture_output=True,
                    text=True,
                    cwd=str(home_dir),
                    timeout=30
                )
                if add_result.returncode != 0:
                    logger.warning(f"Failed to add {path}: {add_result.stderr}")
        else:
            # Stage all changes
            add_result = subprocess.run(
                ["git", "add", "-A"],
                capture_output=True,
                text=True,
                cwd=str(home_dir),
                timeout=30
            )
            if add_result.returncode != 0:
                raise HTTPException(status_code=500, detail=f"Git add failed: {add_result.stderr}")

        # Check if there's anything to commit
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=10
        )

        staged_changes = [line for line in status_result.stdout.split('\n') if line and line[0] != ' ' and line[0] != '?']
        if not staged_changes:
            return {
                "success": True,
                "message": "No changes to sync",
                "commit_sha": None,
                "files_changed": 0
            }

        # 2. Create commit
        commit_message = request.message or f"Trinity sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        commit_result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=30
        )
        if commit_result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Git commit failed: {commit_result.stderr}")

        # Get the commit SHA
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=10
        )
        commit_sha = sha_result.stdout.strip() if sha_result.returncode == 0 else None

        # 3. Push to remote (force push to allow rebasing)
        push_result = subprocess.run(
            ["git", "push", "--force-with-lease"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=60
        )
        if push_result.returncode != 0:
            # If force-with-lease fails, try regular push
            push_result = subprocess.run(
                ["git", "push"],
                capture_output=True,
                text=True,
                cwd=str(home_dir),
                timeout=60
            )
            if push_result.returncode != 0:
                raise HTTPException(status_code=500, detail=f"Git push failed: {push_result.stderr}")

        # Get current branch for response
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=10
        )
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

        return {
            "success": True,
            "message": f"Synced to {current_branch}",
            "commit_sha": commit_sha,
            "files_changed": len(staged_changes),
            "branch": current_branch,
            "sync_time": datetime.now().isoformat()
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Git operation timed out")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Git sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Git sync error: {str(e)}")


@app.get("/api/git/log")
async def get_git_log(limit: int = 10):
    """
    Get recent git commits for this agent's branch.
    """
    home_dir = Path("/home/developer")
    git_dir = home_dir / ".git"

    if not git_dir.exists():
        raise HTTPException(status_code=400, detail="Git sync not enabled for this agent")

    try:
        log_result = subprocess.run(
            ["git", "log", f"-{limit}", "--format=%H|%h|%s|%an|%ai"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=30
        )

        if log_result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Git log failed: {log_result.stderr}")

        commits = []
        for line in log_result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        "sha": parts[0],
                        "short_sha": parts[1],
                        "message": parts[2],
                        "author": parts[3],
                        "date": parts[4]
                    })

        return {
            "commits": commits,
            "count": len(commits)
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Git operation timed out")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Git log error: {e}")
        raise HTTPException(status_code=500, detail=f"Git log error: {str(e)}")


@app.post("/api/git/pull")
async def pull_from_github():
    """
    Pull latest changes from the remote branch.
    Use with caution - may cause merge conflicts.
    """
    home_dir = Path("/home/developer")
    git_dir = home_dir / ".git"

    if not git_dir.exists():
        raise HTTPException(status_code=400, detail="Git sync not enabled for this agent")

    try:
        # Fetch first
        fetch_result = subprocess.run(
            ["git", "fetch", "origin"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=60
        )

        # Then pull with rebase to keep history clean
        pull_result = subprocess.run(
            ["git", "pull", "--rebase"],
            capture_output=True,
            text=True,
            cwd=str(home_dir),
            timeout=60
        )

        if pull_result.returncode != 0:
            # If rebase fails, abort it
            subprocess.run(["git", "rebase", "--abort"], cwd=str(home_dir), timeout=10)
            raise HTTPException(status_code=409, detail=f"Pull failed (possible conflict): {pull_result.stderr}")

        return {
            "success": True,
            "message": "Pulled latest changes",
            "output": pull_result.stdout
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Git operation timed out")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Git pull error: {e}")
        raise HTTPException(status_code=500, detail=f"Git pull error: {str(e)}")


@app.get("/api/credentials/status")
async def get_credentials_status():
    """
    Get current credential status - which files exist and when they were last modified.
    """
    home_dir = Path("/home/developer")
    files_status = {}

    credential_files = [
        ".env",
        ".mcp.json",
        ".mcp.json.template"
    ]

    for filename in credential_files:
        filepath = home_dir / filename
        if filepath.exists():
            stat = filepath.stat()
            files_status[filename] = {
                "exists": True,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        else:
            files_status[filename] = {"exists": False}

    # Count credentials in .env if it exists
    env_file = home_dir / ".env"
    credential_count = 0
    if env_file.exists():
        content = env_file.read_text()
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                credential_count += 1

    return {
        "agent_name": agent_state.agent_name,
        "files": files_status,
        "credential_count": credential_count
    }

# ============================================================================
# Startup
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("AGENT_SERVER_PORT", "8000"))

    logger.info(f"Starting Agent API Server on port {port}")
    logger.info(f"Agent Name: {agent_state.agent_name}")
    logger.info(f"Claude Code Available: {agent_state.claude_code_available}")
    logger.info("SECURITY: This server is internal-only, accessed via Trinity backend proxy")

    # Bind to 0.0.0.0 for Docker internal network communication
    # Port is NOT exposed externally - backend proxies requests via Docker network
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
