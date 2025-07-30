---
description: Show sprint burndown chart using RLVR metrics
allowed-tools: Read, Bash(jq:*, python3:*)
---

## Context

Displaying sprint burndown and progress metrics.

## Current Sprint Status

!`cat "${CLAUDE_PROJECT_DIR}/data/sprints/current-sprint.json" 2>/dev/null | jq -r '"Sprint: \(.name)\nDay: " + (((now - (.start_date | strptime("%Y-%m-%dT%H:%M:%SZ") | mktime)) / 86400) | floor | tostring) + " of \(.duration_days)"' || echo "No active sprint"`

## Task Burndown

### Pending Tasks by Priority
!`python3 << 'EOF'
import json
import os
from pathlib import Path
from collections import defaultdict

tasks_dir = Path(os.environ.get('CLAUDE_PROJECT_DIR', '.')) / 'data' / 'tasks'
priority_counts = defaultdict(int)
status_counts = defaultdict(int)

for task_file in tasks_dir.glob('*/metadata.json'):
    try:
        with open(task_file) as f:
            task = json.load(f)
            priority = task.get('priority', 'P2')
            status = task.get('status', 'pending')
            if status != 'completed':
                priority_counts[priority] += 1
            status_counts[status] += 1
    except:
        pass

print("Remaining tasks by priority:")
for priority in ['P0', 'P1', 'P2', 'P3']:
    count = priority_counts.get(priority, 0)
    bar = '█' * min(count, 20)
    print(f"{priority}: {bar} {count}")

print("\nTasks by status:")
for status, count in sorted(status_counts.items()):
    print(f"  {status}: {count}")
EOF
`

## Daily Progress

### Tasks Completed Per Day
!`find "${CLAUDE_PROJECT_DIR}/data/tasks" -name "metadata.json" -mtime -7 2>/dev/null | xargs grep -l '"status": "completed"' | xargs ls -la | awk '{print $6}' | sort | uniq -c || echo "No completed tasks in last 7 days"`

### Average Reward Trend
!`tail -50 "${CLAUDE_PROJECT_DIR}/data/scoreboard/rlvr.jsonl" 2>/dev/null | jq -s 'group_by(.timestamp[0:10]) | map({date: .[0].timestamp[0:10], avg_reward: (map(.reward) | add/length)}) | .[-5:]' || echo "[]"`

## Velocity Metrics

### Agent Utilization
!`tail -30 "${CLAUDE_PROJECT_DIR}/data/scoreboard/events.jsonl" 2>/dev/null | grep "agent_selected" | jq -r .agent_name | sort | uniq -c | sort -nr || echo "No agent activity"`

### Completion Rate
!`python3 << 'EOF'
import json
from pathlib import Path
import os
from datetime import datetime, timedelta

events_file = Path(os.environ.get('CLAUDE_PROJECT_DIR', '.')) / 'data' / 'scoreboard' / 'events.jsonl'
if events_file.exists():
    week_ago = datetime.now() - timedelta(days=7)
    started = completed = 0
    
    with open(events_file) as f:
        for line in f:
            try:
                event = json.loads(line)
                if datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')) > week_ago:
                    if event['event'] == 'task_started':
                        started += 1
                    elif event['event'] == 'task_completed':
                        completed += 1
            except:
                pass
    
    if started > 0:
        rate = (completed / started) * 100
        print(f"Completion rate (7 days): {rate:.1f}% ({completed}/{started})")
    else:
        print("No tasks started in last 7 days")
else:
    print("No event data available")
EOF
`