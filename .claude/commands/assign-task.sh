#!/bin/bash
# Custom command to manually assign a task to a specific agent

set -euo pipefail

# Check if task.yml exists
if [ ! -f "task.yml" ]; then
    echo "Error: task.yml not found in current directory"
    exit 1
fi

# Parse arguments
AGENT_NAME=""
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --agent)
            AGENT_NAME="$2"
            shift 2
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help)
            echo "Usage: /assign-task [--agent AGENT_NAME] [--force]"
            echo ""
            echo "Assign the current task to a specific agent or let the system choose."
            echo ""
            echo "Options:"
            echo "  --agent NAME    Specify the agent to assign the task to"
            echo "  --force         Force assignment even if agent is not optimal"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set environment variables for manual assignment
if [ -n "$AGENT_NAME" ]; then
    export KIRO_MANUAL_AGENT="$AGENT_NAME"
    export KIRO_FORCE_ASSIGNMENT="$FORCE"
fi

# Trigger task assignment
echo "Assigning task..."
python3 "$CLAUDE_PROJECT_DIR/.claude/scripts/manual_assign.py"