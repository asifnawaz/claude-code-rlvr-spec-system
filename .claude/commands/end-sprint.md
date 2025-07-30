---
description: End current sprint and generate metrics report
allowed-tools: Read, Bash(jq:*, python3:*)
---

## Context

Ending the current sprint and calculating RLVR performance metrics.

## Current Sprint

!`cat "${CLAUDE_PROJECT_DIR}/data/sprints/current-sprint.json" 2>/dev/null | jq -r '"Sprint: \(.name)\nStarted: \(.start_date)"' || echo "No active sprint"`

## Sprint Metrics

### Task Completion
!`find "${CLAUDE_PROJECT_DIR}/data/tasks" -name "metadata.json" -newermt "$(cat "${CLAUDE_PROJECT_DIR}/data/sprints/current-sprint.json" 2>/dev/null | jq -r .start_date || echo "1970-01-01")" 2>/dev/null | wc -l | xargs echo "Total tasks:"`

### Agent Performance
!`tail -100 "${CLAUDE_PROJECT_DIR}/data/scoreboard/rlvr.jsonl" 2>/dev/null | jq -s 'group_by(.agent_name) | map({agent: .[0].agent_name, avg_reward: (map(.reward) | add/length), tasks: length}) | sort_by(.avg_reward) | reverse' || echo "[]"`

### Overall Sprint Score
!`tail -100 "${CLAUDE_PROJECT_DIR}/data/scoreboard/rlvr.jsonl" 2>/dev/null | jq -s 'map(.reward) | add/length' | xargs printf "Average reward: %.2f\n" || echo "No rewards recorded"`

### Kiro Template Compliance
!`tail -50 "${CLAUDE_PROJECT_DIR}/data/scoreboard/rlvr.jsonl" 2>/dev/null | jq -s 'map(.components.kiro_template_score // 0) | add/length' | xargs printf "Average Kiro score: %.2f\n" || echo "No Kiro scores"`

## Archive Sprint

!`mv "${CLAUDE_PROJECT_DIR}/data/sprints/current-sprint.json" "${CLAUDE_PROJECT_DIR}/data/sprints/sprint-$(date +%Y%m%d-%H%M%S).json" 2>/dev/null || echo "No sprint to archive"`

Sprint ended successfully!