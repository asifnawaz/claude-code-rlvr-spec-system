# Doom-RLVR Autonomous Agent Handling System

## Overview

The Doom-RLVR system now operates **completely autonomously**. Users simply provide their natural language prompts, and the system automatically:

1. **Detects task type** from the prompt content
2. **Determines priority** based on urgency indicators
3. **Optimizes the prompt** for better results
4. **Selects the best agent** based on specialization and performance
5. **Enhances the request** with agent-specific context
6. **Evaluates results** and provides feedback

## How It Works

### 1. Automatic Task Detection

The system analyzes keywords in the user's prompt to determine task type:

- **Bugfix**: "fix", "bug", "error", "broken", "crash"
- **Feature**: "add", "implement", "create", "build"
- **Refactor**: "refactor", "clean", "improve", "restructure"
- **Security**: "security", "vulnerability", "auth", "exploit"
- **Testing**: "test", "coverage", "unit test"
- **Performance**: "performance", "speed", "optimize", "slow"

### 2. Priority Detection

Priority is automatically determined from urgency indicators:

- **P0 (Critical)**: "urgent", "critical", "asap", "emergency"
- **P1 (High)**: "important", "priority", "soon"
- **P2 (Medium)**: Default for most tasks
- **P3 (Low)**: "minor", "low priority", "when possible"

### 3. Prompt Optimization

Each task type has an optimization template that:
- Asks clarifying questions
- Provides structure
- Ensures important details aren't missed

Example for bugfix:
```
Please provide the following details:
1. What is the expected behavior?
2. What is the actual behavior?
3. Steps to reproduce
4. Any error messages?
5. Affected files/components (if known)
```

### 4. Agent Selection Algorithm

The system scores each agent based on:
- **Specialization match** (+10 points)
- **Tier level** (Principal: +3, Senior: +2, Junior: +1)
- **Critical task boost** (+5 for P0 tasks to Principal agents)
- **Performance history** (rolling average reward)

### 5. Continuous Improvement

The Stop hook provides:
- Performance evaluation
- Specific feedback on improvements needed
- Tracking of optimization effectiveness
- Agent performance updates

## Usage Examples

### Simple Usage

Just type your request naturally:

```bash
# Bug fix request
"Fix the login page - users can't sign in with Google"

# Feature request
"Add dark mode toggle to the settings page"

# Security issue
"There's a SQL injection vulnerability in the search function"

# Performance issue
"The dashboard is loading very slowly with large datasets"
```

### What Happens Automatically

1. **Task Analysis**:
   - Detected type: bugfix
   - Priority: P2 (medium)
   - Selected agent: agent-bugfix-senior

2. **Prompt Enhancement**:
   - Original prompt is preserved
   - Optimization template added
   - Agent instructions injected
   - Evaluation criteria included

3. **Execution**:
   - Agent operates with proper constraints
   - Tools are validated against permissions
   - Performance is tracked

4. **Evaluation**:
   - Code quality checked
   - Test coverage analyzed
   - Security scanned
   - Feedback generated

## Benefits

### For Users
- No need to create task.yml files
- Natural language interface
- Automatic optimization
- Best agent selection

### For Quality
- Consistent task handling
- Proper context for each task type
- Performance-based agent selection
- Continuous improvement through feedback

### For Teams
- Standardized approach
- Performance tracking
- Knowledge accumulation
- Quality metrics

## Configuration

### Customizing Task Detection

Edit keywords in `UserPromptSubmit` hook:
```python
task_indicators = {
    'bugfix': ['fix', 'bug', 'error', ...],
    'feature': ['add', 'implement', ...],
    # Add your own patterns
}
```

### Adjusting Optimization Templates

Edit `optimization-templates.json`:
```json
{
  "bugfix": {
    "template": "Your custom template...",
    "keywords": ["fix", "bug", ...],
    "priority_boost": 0.2
  }
}
```

### Agent Specialization

Agents automatically specialize based on:
- Task type frequency
- Performance scores
- Tier progression

## Monitoring

### Check Recent Tasks
```bash
/doom-status
```

### View Agent Performance
```bash
/doom-leaderboard
```

### Analyze Feedback
```bash
cat .claude/feedback/*_feedback.jsonl | jq .
```

### Track Optimization Effectiveness
```bash
cat .claude/scoreboard/optimization_effectiveness.jsonl | jq .
```

## Advanced Features

### Learning from Feedback

The system tracks:
- Which optimizations lead to better rewards
- Common issues by task type
- Agent performance patterns

### Adaptive Agent Selection

Over time, the system learns:
- Which agents excel at specific task types
- When to promote/demote agents
- Optimal agent-task matching

### Prompt Evolution

Future enhancements could include:
- Learning better optimization templates
- Customizing prompts per agent
- Adapting to project-specific patterns

## Troubleshooting

### No Agent Selected
- Check if agents exist in `.claude/agents/`
- Verify agents aren't suspended
- Review task type detection

### Poor Performance
- Check feedback in evaluation output
- Review agent specializations
- Analyze optimization effectiveness

### Task Not Detected
- Add keywords to task indicators
- Check prompt clarity
- Manual override still available via task.yml

## Summary

The autonomous system eliminates manual configuration while maintaining the benefits of the RLVR evaluation system. Users get an intelligent assistant that improves over time, while the system ensures consistent quality through automated evaluation and feedback.