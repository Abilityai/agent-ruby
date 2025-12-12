#!/bin/bash
# Agent initialization script for local development
# Generates .mcp.json files from templates using credentials from .env

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Ruby Agent Initialization ==="
echo ""

# Check for .env
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo ""
        echo "ERROR: Please edit .env and add your credentials before running init.sh again"
        echo "       Required credentials are listed in .env.example"
        exit 1
    else
        echo "ERROR: No .env.example found"
        exit 1
    fi
fi

# Source credentials
echo "Loading credentials from .env..."
set -a
source .env
set +a

# Verify required credentials are set
MISSING=""
for var in TWITTER_API_KEY HEYGEN_API_KEY CLOUDINARY_API_KEY GEMINI_API_KEY BLOTATO_API_KEY GOFILE_API_TOKEN; do
    if [ -z "${!var}" ]; then
        MISSING="$MISSING $var"
    fi
done

if [ -n "$MISSING" ]; then
    echo ""
    echo "WARNING: The following credentials are not set:$MISSING"
    echo "         Some features may not work without them."
    echo ""
fi

# Generate .mcp.json from template
if [ -f .mcp.json.template ]; then
    echo "Generating .mcp.json..."
    envsubst < .mcp.json.template > .mcp.json
    echo "  ✓ Created .mcp.json"
else
    echo "WARNING: No .mcp.json.template found"
fi

# Generate .claude/agents/.mcp.json from template
if [ -f .claude/agents/.mcp.json.template ]; then
    echo "Generating .claude/agents/.mcp.json..."
    envsubst < .claude/agents/.mcp.json.template > .claude/agents/.mcp.json
    echo "  ✓ Created .claude/agents/.mcp.json"
fi

echo ""
echo "=== Initialization Complete ==="
echo ""
echo "Agent initialized successfully!"
echo "Run 'claude' to start the agent"
echo ""
echo "Note: .mcp.json and .env are gitignored and will not be committed."
