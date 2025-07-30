---
description: Start a new sprint with RLVR metrics
argument-hint: <sprint-name> [duration-days]
allowed-tools: Read, Write, Bash(date:*, jq:*)
---

## Context

Starting a new sprint for Kiro-RLVR tracked development.

## Task

!`mkdir -p "${CLAUDE_PROJECT_DIR}/data/sprints"`

Create sprint metadata:

!`cat > "${CLAUDE_PROJECT_DIR}/data/sprints/current-sprint.json" << EOF
{
  "name": "$ARGUMENTS",
  "start_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "duration_days": ${2:-14},
  "status": "active",
  "metrics": {
    "planned_tasks": 0,
    "completed_tasks": 0,
    "total_reward": 0,
    "avg_reward": 0
  },
  "goals": [
    "Achieve mean reward ≥ +4",
    "Complete all P0/P1 tasks",
    "Maintain test coverage above 80%"
  ]
}
EOF`

## Sprint Planning

Based on RLVR metrics, prioritize:

!`python3 "${CLAUDE_PROJECT_DIR}/.claude/scripts/kiro_cli_simple.py" analyze-backlog 2>/dev/null || echo "No backlog analysis available"`

Top agents for this sprint:
!`tail -20 "${CLAUDE_PROJECT_DIR}/data/scoreboard/rlvr.jsonl" 2>/dev/null | jq -r '.agent_name' | sort | uniq -c | sort -nr | head -5 || echo "No agent metrics yet"`

Sprint "$ARGUMENTS" started successfully!