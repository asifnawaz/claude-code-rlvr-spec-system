# Kiro-RLVR Setup Guide

## Quick Start

1. **Copy the `.claude` directory to your project root**
   ```bash
   cp -r /path/to/kiro-spec-claude/.claude /your/project/
   ```

2. **Initialize the system**
   ```bash
   cd /your/project
   python .claude/scripts/kiro-cli.py init
   ```

3. **Create a task file**
   ```bash
   cp /path/to/kiro-spec-claude/task.yml .
   # Edit task.yml with your requirements
   ```

4. **Run Claude Code**
   ```bash
   # The PreCommand hook will automatically assign the task to the best agent
   claude-code "Fix the authentication issue"
   ```

## How It Works

1. **Task Submission**: When you run a command with a `task.yml` file present, the PreCommand hook intercepts it
2. **Agent Selection**: The system selects the best agent based on task type, tier, and performance
3. **Execution**: Claude Code runs with the selected agent's context and constraints
4. **Monitoring**: PostToolUse hook monitors tool usage and enforces policies
5. **Evaluation**: PostCommand hook evaluates the results and calculates rewards
6. **Tier Updates**: Agents are promoted/demoted based on rolling performance

## CLI Commands

```bash
# View agent status
python .claude/scripts/kiro-cli.py agents

# Check task status
python .claude/scripts/kiro-cli.py status

# View leaderboard
python .claude/scripts/kiro-cli.py leaderboard

# Check agent scores
python .claude/scripts/kiro-cli.py scores agent-bugfix-senior

# Follow live logs
python .claude/scripts/kiro-cli.py logs --tail

# Manually update tiers
python .claude/scripts/kiro-cli.py update-tiers
```

## Configuration

### Adjust Evaluation Weights
Edit `.claude/config/evaluator-config.json`:
```json
{
  "weights": {
    "test_coverage_delta": 0.3,
    "lint_score": 0.2,
    "security_scan_score": 0.2,
    "code_complexity_delta": 0.1,
    "ci_pipeline_status": 0.1,
    "review_feedback_score": 0.1
  }
}
```

### Adjust Tier Thresholds
Edit `.claude/config/settings.json`:
```json
{
  "tiers": {
    "promotion_threshold": 4.0,
    "demotion_threshold": 2.0,
    "suspension_threshold": 0.0
  }
}
```

### Add New Agents
1. Copy `.claude/agents/template.yml` to `.claude/agents/agent-[type]-[level].yml`
2. Edit the agent configuration
3. Set specializations and system prompt

## Monitoring

### Real-time Dashboard
```bash
# In one terminal
python .claude/scripts/kiro-cli.py logs --tail

# In another terminal
watch -n 5 'python .claude/scripts/kiro-cli.py leaderboard'
```

### Performance Analysis
```bash
# Export metrics
cat .claude/scoreboard/rlvr.jsonl | jq -s '.' > metrics.json

# Generate report
python -c "
import json
with open('metrics.json') as f:
    data = json.load(f)
    by_agent = {}
    for entry in data:
        agent = entry['agent_name']
        if agent not in by_agent:
            by_agent[agent] = []
        by_agent[agent].append(entry['reward'])
    
    for agent, rewards in by_agent.items():
        avg = sum(rewards) / len(rewards)
        print(f'{agent}: {avg:.2f} (n={len(rewards)})')
"
```

## Troubleshooting

### No suitable agent found
- Check that agents exist: `ls .claude/agents/`
- Verify agent specializations match task type
- Check no agents are suspended

### Hooks not executing
- Ensure hooks are executable: `chmod +x .claude/hooks/*`
- Check Claude Code recognizes hooks: `claude-code --list-hooks`
- Verify Python is available: `python3 --version`

### Low reward scores
- Review evaluation criteria in CLAUDE.md
- Check test coverage is improving
- Ensure lint and security checks pass
- Verify CI/CD pipeline is configured

### Agent not improving
- Check grace period (3 tasks minimum)
- Review recent task failures
- Adjust evaluation weights if needed
- Consider manual tier adjustment

## Advanced Usage

### Custom Evaluator
Create `.claude/scripts/custom_evaluators/my_evaluator.py`:
```python
def evaluate_my_metric(task_id):
    # Return score between -1 and 1
    return 0.5
```

Add to evaluator config:
```json
{
  "custom_evaluators": {
    "my_metric": {
      "enabled": true,
      "weight": 0.1,
      "script": "custom_evaluators/my_evaluator.py"
    }
  }
}
```

### Batch Task Processing
```bash
for task in task1.yml task2.yml task3.yml; do
    cp $task task.yml
    claude-code "Process task"
    mv .claude/tasks/*/output.json results/$task.json
done
```

## Integration

### CI/CD Integration
```yaml
# .github/workflows/kiro-tasks.yml
name: Process Kiro Tasks
on:
  issues:
    types: [labeled]

jobs:
  process:
    if: contains(github.event.label.name, 'kiro-task')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Claude Code
        run: |
          # Install Claude Code CLI
          # Copy .claude directory
      - name: Process Task
        run: |
          # Convert issue to task.yml
          # Run Claude Code
          # Comment results on issue
```

### Git Hooks
```bash
# .git/hooks/pre-commit
#!/bin/bash
# Run tier update before each commit
python .claude/scripts/tier-updater.py
git add .claude/agents/*.yml .claude/scoreboard/leaderboard.json
```