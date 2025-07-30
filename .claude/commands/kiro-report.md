---
description: Generate comprehensive task report
argument-hint: [--last N]
allowed-tools: Read, Bash(find:*, jq:*, wc:*)
---

## Context

Generate a comprehensive report of Kiro-RLVR task activities.

## Task

### Task Summary
!`find "${CLAUDE_PROJECT_DIR}/data/tasks" -name "metadata.json" 2>/dev/null | wc -l | xargs echo "Total Tasks:"`

### Recent Activity
!`tail -20 "${CLAUDE_PROJECT_DIR}/data/scoreboard/events.jsonl" 2>/dev/null | jq -r '"[\(.timestamp)] \(.event) - Task: \(.task_id // "N/A")"' || echo "No events recorded"`

### Agent Performance
!`for f in "${CLAUDE_PROJECT_DIR}/data/scoreboard"/*_performance.jsonl; do [ -f "$f" ] && echo "$(basename "$f" _performance.jsonl): $(tail -5 "$f" | jq -s 'add/length' 2>/dev/null || echo "N/A")"; done || echo "No performance data"`

### Quality Metrics
!`tail -10 "${CLAUDE_PROJECT_DIR}/data/scoreboard/rlvr.jsonl" 2>/dev/null | jq -s 'map(.reward) | add/length' | xargs echo "Average Recent Reward:" || echo "No evaluation data"`