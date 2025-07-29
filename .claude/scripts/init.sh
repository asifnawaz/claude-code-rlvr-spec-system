#!/bin/bash
# Initialize Kiro-RLVR system

set -euo pipefail

echo "=== Kiro-RLVR System Initialization ==="
echo ""

# Get project directory
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
CLAUDE_DIR="$PROJECT_DIR/.claude"

# Check if .claude directory exists
if [ ! -d "$CLAUDE_DIR" ]; then
    echo "Error: .claude directory not found in $PROJECT_DIR"
    echo "Please run this from your project root where .claude is located"
    exit 1
fi

echo "Initializing in: $PROJECT_DIR"
echo ""

# Create required directories
echo "Creating directories..."
mkdir -p "$CLAUDE_DIR"/{tasks,feedback,scoreboard}
echo "✓ Directories created"

# Make hooks executable
echo "Setting hook permissions..."
chmod +x "$CLAUDE_DIR/hooks"/*
echo "✓ Hooks are executable"

# Make command scripts executable
echo "Setting command permissions..."
chmod +x "$CLAUDE_DIR/commands"/*.sh
echo "✓ Commands are executable"

# Initialize scoreboard files if they don't exist
echo "Initializing scoreboard..."
touch "$CLAUDE_DIR/scoreboard"/{events.jsonl,rlvr.jsonl,tool_usage.jsonl}
echo "✓ Scoreboard initialized"

# Check Python version
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✓ Python $PYTHON_VERSION found"
else
    echo "✗ Python 3 not found - required for Kiro-RLVR"
    exit 1
fi

# Verify all components
echo ""
echo "Verifying components..."

# Check hooks
for hook in UserPromptSubmit PreToolUse PostToolUse Stop; do
    if [ -f "$CLAUDE_DIR/hooks/$hook" ] && [ -x "$CLAUDE_DIR/hooks/$hook" ]; then
        echo "✓ Hook: $hook"
    else
        echo "✗ Hook missing or not executable: $hook"
    fi
done

# Check key scripts
for script in kiro_cli_simple.py rlvr_evaluate.py; do
    if [ -f "$CLAUDE_DIR/scripts/$script" ]; then
        echo "✓ Script: $script"
    else
        echo "✗ Script missing: $script"
    fi
done

# Check agents
AGENT_COUNT=$(ls "$CLAUDE_DIR/agents"/agent-*.yml 2>/dev/null | wc -l)
echo "✓ Agents found: $AGENT_COUNT"

# Check settings
if [ -f "$CLAUDE_DIR/settings.json" ]; then
    echo "✓ Settings configured"
else
    echo "✗ Settings missing"
fi

echo ""
echo "=== Initialization Complete ==="
echo ""
echo "Kiro-RLVR is ready to use!"
echo ""
echo "Quick start:"
echo "  Just type your request naturally, for example:"
echo "  \"Fix the login bug where users can't sign in\""
echo ""
echo "Available commands:"
echo "  /kiro-status      - View recent tasks"
echo "  /kiro-leaderboard - See agent performance"
echo "  /kiro-agent       - View agent details"
echo "  /kiro-report      - Generate task report"
echo ""
echo "For more information, see:"
echo "  - SETUP-GUIDE.md"
echo "  - AUTONOMOUS-SYSTEM.md"
echo "  - .claude/CLAUDE.md"