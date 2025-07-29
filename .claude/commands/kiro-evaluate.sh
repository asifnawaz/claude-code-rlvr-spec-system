#!/bin/bash
# Custom command to manually trigger evaluation for current task

set -euo pipefail

# Check if we have a current task
if [ -z "${KIRO_TASK_ID:-}" ]; then
    echo "Error: No active Kiro task. Create a task.yml and start a task first."
    exit 1
fi

echo "Evaluating task: $KIRO_TASK_ID"
echo "Agent: ${KIRO_AGENT_NAME:-unknown}"
echo ""

# Run the evaluator
python3 "$CLAUDE_PROJECT_DIR/.claude/scripts/rlvr_evaluate.py" \
    --task-id "$KIRO_TASK_ID" \
    --agent-name "${KIRO_AGENT_NAME:-unknown}" \
    --task-status "in_progress" \
    --output-dir "$CLAUDE_PROJECT_DIR/.claude/scoreboard"

# Show the result
echo ""
echo "Evaluation complete. Recent scores:"
python3 "$CLAUDE_PROJECT_DIR/.claude/scripts/kiro_cli.py" scores "${KIRO_AGENT_NAME:-unknown}" --last 5