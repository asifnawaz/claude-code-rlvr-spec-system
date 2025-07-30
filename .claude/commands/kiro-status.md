---
description: Check Kiro-RLVR task and agent status
argument-hint: [task-id]
allowed-tools: Read, Bash(python3:*)
---

## Context

Current directory: !`pwd`
Kiro-RLVR Status Check

## Task

!`python3 "${CLAUDE_PROJECT_DIR}/.claude/scripts/kiro_cli_simple.py" status $ARGUMENTS`

Show the current status of Kiro-RLVR tasks and agents. If a task ID is provided as an argument, show details for that specific task.