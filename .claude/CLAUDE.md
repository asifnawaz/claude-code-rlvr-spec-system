# Doom-RLVR Context for Claude Code

## System Overview

Doom-RLVR is an autonomous agent handling system that automatically:
- Detects task types from natural language prompts
- Structures prompts using the Doom template ($GOAL, $CONTEXT, etc.)
- Routes tasks to specialized agents (defined as .md files)
- Validates tool usage with security checks (pre-check.py)
- Evaluates performance using RLVR including template compliance
- Tracks sprint progress and team velocity
- Improves continuously through reinforcement learning

## How to Use

Just type your request naturally. The system handles everything else:

```bash
# Examples:
"Fix the login bug where users can't sign in"
"Add dark mode to the settings page"
"The API is returning 500 errors"
"Improve the performance of the search function"
```

## Available Commands

### Task Management
- `/doom-status` - View recent tasks and their status
- `/doom-leaderboard` - See agent performance rankings with RLVR scores
- `/doom-agent <name>` - View specific agent details from .md files
- `/doom-report` - Generate comprehensive task report

### Sprint Management (NEW)
- `/start-sprint "Name" [days]` - Start a new sprint with RLVR tracking
- `/burndown` - View sprint progress, velocity, and task burndown
- `/end-sprint` - Complete sprint and generate metrics report

Note: These are custom slash commands defined as markdown files in `.claude/commands/`

## Task Types

The system automatically detects:
- **bugfix**: Keywords like "fix", "bug", "error", "broken"
- **feature**: Keywords like "add", "implement", "create", "build"
- **refactor**: Keywords like "refactor", "clean", "improve", "restructure"
- **security**: Keywords like "security", "vulnerability", "auth"
- **testing**: Keywords like "test", "coverage", "unit test"
- **performance**: Keywords like "performance", "speed", "optimize", "slow"

## Agents

Current specialized agents (defined as .md files with YAML front-matter):
- `agent-bugfix-junior` - Entry-level bug fixing
- `agent-bugfix-senior` - Advanced bug fixing
- `agent-feature-junior` - Basic feature development
- `agent-feature-senior` - Complex feature development
- `agent-refactor-principal` - Architecture and refactoring
- `agent-security-senior` - Security specialist

Each agent has:
- YAML configuration in front-matter (tier, specializations, tools_allowed)
- Markdown body with instructions and Doom template guidance

## Priority Levels

Automatically detected from keywords:
- **P0 (Critical)**: "urgent", "critical", "asap", "emergency"
- **P1 (High)**: "important", "priority", "soon"
- **P2 (Medium)**: Default for most tasks
- **P3 (Low)**: "minor", "low priority", "when possible"

## RLVR Evaluation Metrics

Tasks are evaluated on:
1. **Test Coverage** (25%): Must increase or maintain
2. **Code Quality** (15%): Lint checks must pass
3. **Security** (15%): No new vulnerabilities
4. **Complexity** (10%): Should not increase significantly
5. **CI/CD** (10%): All pipelines must pass
6. **Review Quality** (10%): Clean, reviewable code
7. **Doom Template Compliance** (15%): Proper use of $GOAL, $CONTEXT, etc.

The Doom template score includes:
- Presence of all required fields (-2 points per missing)
- Completion of acceptance criteria (+1 per checked item)
- Overall structure and clarity

## Manual Task Creation (Optional)

For specific control, create `task.yml`:

```yaml
type: feature
priority: P1
description: Add user authentication
agent_name: agent-feature-senior  # Optional - force specific agent
```

## File Locations

- **Agents**: `.claude/agents/`
- **Task History**: `.claude/tasks/`
- **Performance Data**: `.claude/scoreboard/`
- **Feedback**: `.claude/feedback/`
- **Hooks**: `.claude/hooks/`

## Important Notes

1. **Autonomous by Default**: Just describe what you need
2. **No External Dependencies**: Uses only Python standard library
3. **File-based State**: All state stored in `.claude/` directory
4. **Continuous Learning**: System improves over time
5. **Natural Language**: No special syntax required

## Debugging

Check logs if needed:
- `.claude/scoreboard/events.jsonl` - All system events
- `.claude/scoreboard/rlvr.jsonl` - Evaluation results
- `.claude/scoreboard/errors.log` - Error messages

## Best Practices

1. **Be Specific**: Clear descriptions help task detection
2. **Trust the System**: Let it optimize and route automatically
3. **Review Feedback**: Check evaluation results for insights
4. **Monitor Performance**: Use `/doom-leaderboard` periodically

## Quick Examples

### Bug Fix
```
"The login form doesn't validate email addresses correctly"
→ Automatically routed to bugfix specialist with debugging template
```

### Feature Request
```
"Add CSV export functionality to the reports page"
→ Routed to feature developer with implementation checklist
```

### Performance Issue
```
"The dashboard takes 10 seconds to load"
→ Routed to performance specialist with profiling template
```

## System Architecture

```
User Input → UserPromptSubmit Hook → Task Detection → Agent Selection
    ↓                                      ↓              ↓
Natural Text                         Type & Priority   Best Match
                                                           ↓
                                                    Enhanced Prompt
                                                           ↓
Stop Hook ← Task Execution ← Tool Validation ← PreToolUse Hook
    ↓              ↑
Evaluation    Claude Code
    ↓
Feedback & Learning
```

Remember: The system is designed to work autonomously. Just describe what you need!