# Kiro-RLVR Claude Code Configuration

## Overview

This project implements a multi-agent orchestration system with Reinforcement Learning and Variable Rewards (RLVR) for Claude Code. Agents are tiered (junior/senior/principal) and automatically promoted/demoted based on performance.

## Agent System

### Available Agents

- **agent-bugfix-junior**: Entry-level bug fixing (reward threshold: 2.0+)
- **agent-bugfix-senior**: Experienced bug fixing (reward threshold: 3.5+)
- **agent-feature-junior**: Basic feature development
- **agent-feature-senior**: Complex feature implementation
- **agent-refactor-principal**: Architecture-level refactoring (reward threshold: 4.0+)
- **agent-security-senior**: Security vulnerability fixes

### Agent Selection

Agents are selected based on:
1. Task type matching agent specializations
2. Highest tier available (principal > senior > junior)
3. Performance score (rolling average reward)

## Task Types

- `bugfix`: Fix bugs, add regression tests
- `feature`: Implement new functionality
- `refactor`: Improve code structure
- `security`: Address security vulnerabilities
- `performance`: Optimize performance
- `testing`: Add or improve tests

## Hooks

### Configured Hooks

1. **PreCommand** - Validate and route tasks to appropriate agents
2. **PostToolUse** - Monitor tool usage and collect metrics
3. **PostCommand** - Evaluate results and calculate rewards

## RLVR Evaluation

Rewards are calculated based on:
- Test coverage delta (30%)
- Lint score (20%)
- Security scan (20%)
- Code complexity (10%)
- CI status (10%)
- Review feedback (10%)

## Usage

### Submit a Task

```bash
# Create a task file
cat > task.yml << EOF
type: bugfix
priority: P1
description: |
  Fix authentication bypass in login endpoint.
  Users can skip 2FA by manipulating cookies.
tags:
  - security
  - authentication
EOF

# The PreCommand hook will automatically assign to best agent
```

### Check Agent Performance

```bash
# View leaderboard
cat .claude/scoreboard/leaderboard.json

# Check specific agent
grep "agent-bugfix-senior" .claude/scoreboard/rlvr.jsonl | tail -5
```

### Manual Agent Selection

```bash
# Force specific agent
export KIRO_AGENT="agent-feature-senior"
# Run your command
```

## Configuration

Key settings in `.claude/config/settings.json`:
- `coordinator.max_concurrent_agents`: Maximum parallel agents
- `evaluator.weights`: Reward component weights
- `tiers.promotion_threshold`: Score needed for promotion
- `security.sandbox_enabled`: Enable/disable sandboxing

## Monitoring

Logs are written to:
- `.claude/scoreboard/rlvr.jsonl` - Reward history
- `.claude/scoreboard/agent_tiers.json` - Current agent tiers
- `.claude/tasks/*/output.json` - Task execution details

## Best Practices

1. **Let the system choose agents** - Manual selection should be rare
2. **Provide clear task descriptions** - Better context = better results
3. **Review failed tasks** - Help improve agent training
4. **Monitor tier changes** - Ensure healthy promotion/demotion

## Troubleshooting

### No suitable agent found
- Check task type matches agent specializations
- Verify agents aren't suspended
- Review `.claude/agents/*.yml` files

### Low reward scores
- Check test coverage requirements
- Ensure CI/CD pipeline is configured
- Verify security scanning tools are installed

### Agent suspended
- Review recent task failures in scoreboard
- Check suspension reason in agent file
- Manually unsuspend if needed

## Advanced Features

### Custom Evaluation Components

Add to `.claude/scripts/custom_evaluators.py`:
```python
def evaluate_documentation(task_id):
    # Return score 0-1
    pass
```

### Agent Templates

Create new agents by copying `.claude/agents/template.yml`

### Hook Extensions

Add custom hooks in `.claude/hooks/custom/`