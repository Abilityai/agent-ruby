---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*)
description: Create a meaningful git commit to checkpoint current agent state
argument-hint: [optional commit message]
---

# Commit Agent State

Create a meaningful git commit to checkpoint the current agent state. This should be run once per session at natural breakpoints or session end.

## Context

- Current git status: !`git status`
- Staged changes: !`git diff --cached --stat`
- Unstaged changes: !`git diff --stat`
- Recent commits (for style reference): !`git log --oneline -5`

## Instructions

1. **Review changes** - Analyze what files have been modified
2. **Stage appropriate files** - Only commit files that should be tracked:
   - `memory/` - Agent's persistent state
   - `.claude/memory/` - Claude-specific memory
   - `outputs/` - Generated content
   - `CLAUDE.md` - Agent instruction updates
   - `template.yaml` - Configuration changes
3. **DO NOT commit** - Never stage these files:
   - `.mcp.json` - Contains credentials
   - `.env` - Contains credentials
   - `*.log` - Temporary logs
   - Any files with API keys or secrets
4. **Create commit** - Write a descriptive commit message:
   - Summarize the session's work (what was accomplished)
   - Use conventional commit format if appropriate
   - Keep under 72 characters for the subject line

## Commit Message Format

If the user provided a message via $ARGUMENTS, use that.
Otherwise, analyze the changes and create a descriptive message like:
- "Update schedule.json with 5 new LinkedIn posts"
- "Add memory context from content planning session"
- "Update CLAUDE.md with new workflow documentation"

## Execution

```bash
# Stage changes (excluding sensitive files)
git add memory/ .claude/memory/ outputs/ CLAUDE.md template.yaml 2>/dev/null || true

# Commit with appropriate message
git commit -m "message here"
```

After committing, show the user:
- The commit hash
- Summary of what was committed
- Any files that were intentionally skipped
