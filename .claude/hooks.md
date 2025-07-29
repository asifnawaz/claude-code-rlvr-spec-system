# Kiro-RLVR Hooks Documentation

## Overview

The Kiro-RLVR system uses Claude Code's hook system to intercept and modify behavior at key points in the execution lifecycle.

## Hook Implementation

### UserPromptSubmit Hook

**Trigger**: When the user submits a prompt
**Purpose**: Route tasks to appropriate agents based on task.yml

This hook:
1. Checks for presence of `task.yml` in project root
2. Loads agent configurations and selects best match
3. Modifies the user prompt to include agent context
4. Sets environment variables for other hooks

### PreToolUse Hook

**Trigger**: Before any tool is executed
**Purpose**: Enforce agent-specific constraints and security policies

This hook:
1. Validates tool usage against agent's allowed tools list
2. Enforces resource limits (file changes, etc.)
3. Blocks dangerous commands for security
4. Logs tool usage for metrics

### PostToolUse Hook

**Trigger**: After a tool completes successfully
**Purpose**: Track metrics and monitor performance

This hook:
1. Records tool execution metrics
2. Updates resource usage counters
3. Warns about potentially problematic actions

### Stop Hook

**Trigger**: When Claude finishes generating response
**Purpose**: Evaluate task completion and update agent performance

This hook:
1. Runs RLVR evaluation to calculate reward
2. Updates agent performance metrics
3. Checks for tier promotions/demotions
4. Logs completion event

## Hook Data Flow

```
UserPromptSubmit (task.yml detected)
    ↓
Sets KIRO_TASK_ID, KIRO_AGENT_NAME environment variables
    ↓
PreToolUse (validates each tool call)
    ↓
PostToolUse (records metrics)
    ↓
Stop (evaluates and rewards)
```

## Environment Variables

The hooks communicate through environment variables:

- `KIRO_TASK_ID`: Current task identifier
- `KIRO_AGENT_NAME`: Assigned agent name
- `KIRO_AGENT_TIER`: Agent tier (junior/senior/principal)
- `CLAUDE_PROJECT_DIR`: Project root directory (set by Claude Code)

## Configuration

Hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "command": "python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/UserPromptSubmit"
      }
    ],
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/PreToolUse"
          }
        ]
      }
    ]
  }
}
```

## Security

Hooks implement several security measures:

1. **Command Filtering**: Dangerous commands are blocked
2. **Resource Limits**: File and token usage is limited per agent tier
3. **Audit Logging**: All actions are logged for review
4. **Sandboxing**: Hooks run with limited permissions

## Custom Extensions

To add custom hook behavior:

1. Create a new script in `.claude/hooks/custom/`
2. Add to the hook chain in settings.json
3. Access hook data via stdin (JSON format)
4. Return control decisions via stdout (JSON format)

Example custom hook:
```python
#!/usr/bin/env python3
import json
import sys

# Read hook data
data = json.load(sys.stdin)

# Custom logic here

# Return decision (for PreToolUse)
result = {"decision": "allow"}
print(json.dumps(result))
```