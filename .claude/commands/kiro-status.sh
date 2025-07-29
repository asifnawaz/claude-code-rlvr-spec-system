#!/bin/bash
# Custom command to check Kiro-RLVR system status

set -euo pipefail

# Parse arguments
FORMAT="table"
TASK_ID=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            FORMAT="json"
            shift
            ;;
        --task)
            TASK_ID="$2"
            shift 2
            ;;
        --help)
            echo "Usage: /kiro-status [--json] [--task TASK_ID]"
            echo ""
            echo "Check the status of Kiro-RLVR tasks and agents."
            echo ""
            echo "Options:"
            echo "  --json          Output in JSON format"
            echo "  --task ID       Show details for specific task"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run the CLI status command
if [ -n "$TASK_ID" ]; then
    python3 "$CLAUDE_PROJECT_DIR/.claude/scripts/kiro_cli_simple.py" status "$TASK_ID"
else
    python3 "$CLAUDE_PROJECT_DIR/.claude/scripts/kiro_cli_simple.py" status
fi