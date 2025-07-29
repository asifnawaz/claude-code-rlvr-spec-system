# Kiro-RLVR System Files

This directory contains the Kiro-RLVR multi-agent orchestration system for Claude Code.

## Directory Structure

```
.claude/
├── agents/          # Agent definitions (YAML files)
├── config/          # System configuration
├── hooks/           # Claude Code hooks (PreCommand, PostToolUse, PostCommand)
├── prompts/         # Agent instruction templates
├── scoreboard/      # Performance metrics and logs
├── scripts/         # Core Python scripts
└── tasks/           # Task execution workspace
```

## Key Components

### Hooks
- **PreCommand**: Routes tasks to appropriate agents
- **PostToolUse**: Monitors tool usage and enforces policies  
- **PostCommand**: Evaluates results and calculates rewards

### Scripts
- **rlvr_evaluate.py**: Calculates multi-component reward scores
- **tier_updater.py**: Updates agent tiers based on performance
- **kiro_cli.py**: Command-line interface for system management

### Agents
- Multiple specialized agents with different tiers (junior/senior/principal)
- Each agent has specific specializations and performance history
- Agents are automatically promoted/demoted based on performance

## Usage

1. Create a `task.yml` file in your project root
2. Run any Claude Code command - the task will be routed automatically
3. Check results with: `python .claude/scripts/kiro_cli.py status`

## Configuration

Edit `.claude/config/settings.json` to adjust:
- Evaluation weights
- Tier thresholds  
- Security policies
- Resource limits

## Monitoring

View system activity:
```bash
# Check agent standings
python .claude/scripts/kiro_cli.py leaderboard

# View recent tasks
python .claude/scripts/kiro_cli.py status

# Follow live events
python .claude/scripts/kiro_cli.py logs --tail
```