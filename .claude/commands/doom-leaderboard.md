---
description: View agent performance leaderboard
allowed-tools: Read, Bash(python3:*)
---

## Context

Show performance rankings for all Doom-RLVR agents.

## Task

!`python3 "${CLAUDE_PROJECT_DIR}/.claude/scripts/doom-cli-simple.py" leaderboard`

Display the agent leaderboard showing:
- Agent names and tiers
- Average rewards
- Task counts
- Recent performance trends