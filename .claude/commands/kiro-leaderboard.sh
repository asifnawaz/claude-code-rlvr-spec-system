#!/bin/bash
# Custom command to view agent leaderboard

set -euo pipefail

# Parse arguments
METRIC="reward"
LIMIT=10

while [[ $# -gt 0 ]]; do
    case $1 in
        --metric)
            METRIC="$2"
            shift 2
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: /kiro-leaderboard [--metric METRIC] [--limit N]"
            echo ""
            echo "Display the agent performance leaderboard."
            echo ""
            echo "Options:"
            echo "  --metric TYPE   Sort by: reward (default), tasks, or tier"
            echo "  --limit N       Number of agents to show (default: 10)"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run the CLI leaderboard command
python3 "$CLAUDE_PROJECT_DIR/.claude/scripts/kiro_cli_simple.py" leaderboard