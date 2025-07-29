#!/bin/bash
# View specific agent details

set -euo pipefail

# Check if agent name provided
if [ $# -eq 0 ]; then
    echo "Usage: /kiro-agent <agent-name>"
    echo ""
    echo "View detailed information about a specific agent."
    echo ""
    echo "Available agents:"
    ls "$CLAUDE_PROJECT_DIR/.claude/agents/" | grep "^agent-" | sed 's/\.yml$//'
    exit 1
fi

AGENT_NAME="$1"
AGENT_FILE="$CLAUDE_PROJECT_DIR/.claude/agents/${AGENT_NAME}.yml"

# Check if agent exists
if [ ! -f "$AGENT_FILE" ]; then
    echo "Error: Agent '$AGENT_NAME' not found"
    echo ""
    echo "Available agents:"
    ls "$CLAUDE_PROJECT_DIR/.claude/agents/" | grep "^agent-" | sed 's/\.yml$//'
    exit 1
fi

# Display agent details
echo "=== Agent Details: $AGENT_NAME ==="
echo ""

# Parse YAML file (simple approach)
echo "Configuration:"
cat "$AGENT_FILE" | grep -E "^(name|tier|specializations|tools_allowed|max_context_tokens):" | sed 's/^/  /'

echo ""
echo "Performance:"

# Check performance file
PERF_FILE="$CLAUDE_PROJECT_DIR/.claude/scoreboard/${AGENT_NAME}_performance.jsonl"
if [ -f "$PERF_FILE" ]; then
    # Get last 5 performance entries
    RECENT_REWARDS=$(tail -5 "$PERF_FILE" | jq -r '.reward' 2>/dev/null | paste -sd, -)
    if [ -n "$RECENT_REWARDS" ]; then
        echo "  Recent rewards: $RECENT_REWARDS"
        # Calculate average
        AVG=$(tail -5 "$PERF_FILE" | jq -r '.reward' 2>/dev/null | awk '{sum+=$1} END {if(NR>0) printf "%.2f", sum/NR}')
        echo "  Recent average: $AVG"
    else
        echo "  No recent performance data"
    fi
else
    echo "  No performance data available"
fi

echo ""
echo "Recent Tasks:"

# Find recent tasks for this agent
EVENTS_FILE="$CLAUDE_PROJECT_DIR/.claude/scoreboard/events.jsonl"
if [ -f "$EVENTS_FILE" ]; then
    grep "\"agent_name\": \"$AGENT_NAME\"" "$EVENTS_FILE" | tail -5 | while read -r line; do
        TASK_ID=$(echo "$line" | jq -r '.task_id' 2>/dev/null || echo "unknown")
        EVENT=$(echo "$line" | jq -r '.event' 2>/dev/null || echo "unknown")
        TIMESTAMP=$(echo "$line" | jq -r '.timestamp' 2>/dev/null || echo "unknown")
        echo "  - $TASK_ID ($EVENT) at $TIMESTAMP"
    done
else
    echo "  No task history available"
fi

echo ""
echo "System Prompt:"
echo ""

# Extract system prompt
awk '/^system_prompt:/ {p=1; next} p && /^[a-zA-Z_]+:/ {p=0} p {print}' "$AGENT_FILE"