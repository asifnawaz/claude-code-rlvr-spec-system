---
description: View specific agent details
argument-hint: <agent-name>
allowed-tools: Read, Bash(cat:*, grep:*, jq:*)
---

## Context

Agent name provided: $ARGUMENTS

## Task

Show detailed information about a specific Kiro-RLVR agent including:

1. Agent configuration:
!`cat "${CLAUDE_PROJECT_DIR}/kiro/agents/${ARGUMENTS}.md" 2>/dev/null || echo "Agent '$ARGUMENTS' not found"`

2. Recent performance:
!`tail -5 "${CLAUDE_PROJECT_DIR}/data/scoreboard/${ARGUMENTS}_performance.jsonl" 2>/dev/null | jq -r '.reward' | paste -sd, - || echo "No performance data"`

3. Available agents (if not found):
!`ls "${CLAUDE_PROJECT_DIR}/kiro/agents/" | grep "^agent-" | sed 's/\.md$//'`