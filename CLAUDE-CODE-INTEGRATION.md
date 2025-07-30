# Claude Code Integration Guide for Doom-RLVR

## Overview

The Doom-RLVR system is fully integrated with Claude Code's hooks, commands, and sub-agents API. This guide explains how the integration works and how to use it effectively.

## Claude Code Hooks API

### Hook Types Used

1. **UserPromptSubmit**: Intercepts user prompts to inject agent context
2. **PreToolUse**: Validates tool usage against agent constraints  
3. **PostToolUse**: Tracks metrics and resource usage
4. **Stop**: Evaluates task completion and calculates rewards

### Hook Configuration

The hooks are configured in `.claude/settings.json`:

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

### Hook Data Format

Hooks receive JSON data via stdin:

```json
{
  "sessionId": "session-123",
  "timestamp": "2024-01-01T12:00:00Z",
  "userPrompt": "Fix the bug",
  "tool": {
    "name": "Edit",
    "params": {
      "file_path": "/src/main.py"
    }
  }
}
```

Hooks can return control decisions:

```json
{
  "decision": "allow",  // or "deny"
  "permissionDecisionReason": "Tool not allowed for junior agents",
  "userPrompt": "Modified prompt with agent context"
}
```

## Custom Commands

Doom-RLVR provides custom slash commands:

### /assign-task
Manually assign a task to a specific agent:
```bash
/assign-task --agent agent-bugfix-senior --force
```

### /doom-status
Check task and agent status:
```bash
/doom-status --json
/doom-status --task bugfix-20240101-120000
```

### /doom-leaderboard
View agent performance rankings:
```bash
/doom-leaderboard --metric reward --limit 10
```

### /doom-evaluate
Manually trigger evaluation:
```bash
/doom-evaluate
```

## Sub-Agents Integration

The system supports Claude Code's sub-agent architecture:

### Agent Definitions

Each agent is defined in `.claude/agents/agent-*.yml`:

```yaml
name: agent-bugfix-senior
tier: senior
specializations:
  - bugfix
  - refactor
system_prompt: |
  You are a senior-level agent specialized in bug fixes...
tools_allowed:
  - Read
  - Edit
  - MultiEdit
  - Grep
  - Bash
max_context_tokens: 75000
```

### Sub-Agent Launching

The `launch_subagent.py` script demonstrates how to launch sub-agents:

```python
result = launch_subagent(
    agent_name="agent-feature-senior",
    task_data={"type": "feature", "description": "..."},
    context="Additional context"
)
```

## Environment Variables

The system uses environment variables for state management:

- `CLAUDE_PROJECT_DIR`: Set by Claude Code, points to project root
- `DOOM_TASK_ID`: Current task identifier  
- `DOOM_AGENT_NAME`: Assigned agent name
- `DOOM_AGENT_TIER`: Agent tier level

## Security and Constraints

### Tool Access Control

PreToolUse hook enforces tool restrictions:

```python
# Junior agents can't use certain tools
tools_allowed = agent_data.get('tools_allowed', [])
if tool_name not in tools_allowed:
    return {"decision": "deny", "reason": "Tool not allowed"}
```

### Resource Limits

Agents have tier-based resource limits:

```yaml
resource_limits:
  max_files_changed: 10  # Junior
  max_files_changed: 30  # Senior  
  max_files_changed: 100 # Principal
```

### Command Security

Dangerous commands are blocked:

```python
FORBIDDEN_COMMANDS = [
    "rm -rf /",
    "sudo",
    "eval",
    "exec"
]
```

## Performance Tracking

### Metrics Collection

PostToolUse hook records:
- Tool usage frequency
- Execution duration
- Error rates
- Resource consumption

### RLVR Evaluation

Stop hook triggers evaluation based on:
- Test coverage changes
- Lint scores
- Security scan results
- Code complexity
- CI/CD status

### Automatic Tier Updates

Agents are promoted/demoted based on rolling average rewards:
- Principal: ≥ 4.0
- Senior: 2.0 - 3.9
- Junior: 0.0 - 1.9
- Suspended: < 0.0

## Best Practices

1. **Let hooks handle routing**: Don't manually set agent context
2. **Use task.yml**: Define clear task requirements
3. **Monitor performance**: Check leaderboard regularly
4. **Review logs**: Use `/doom-status` to track progress
5. **Trust evaluations**: Let RLVR guide agent improvements

## Troubleshooting

### Hooks not firing
- Check `.claude/settings.json` exists
- Verify hook scripts are executable
- Check `CLAUDE_PROJECT_DIR` is set

### Agent not selected
- Ensure `task.yml` exists in project root
- Verify agents have matching specializations
- Check no agents are suspended

### Low rewards
- Review evaluation criteria
- Check test coverage is improving
- Ensure CI/CD is configured
- Verify security tools are installed

## Future Enhancements

1. **WebSocket integration** for real-time monitoring
2. **Multi-project agent sharing** via registry
3. **Custom evaluation plugins** for domain-specific metrics
4. **Agent collaboration** for complex tasks
5. **Learning from feedback** to improve prompts