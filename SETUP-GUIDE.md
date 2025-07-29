# Kiro-RLVR Setup Guide for Claude Code

## 🚀 Quick Start

### Prerequisites
- Claude Code installed and configured
- Python 3.8+ (comes with Claude Code)
- A project directory where you want to use Kiro-RLVR

### 1. Clone or Copy Kiro-RLVR

```bash
# Option A: Clone the repository
git clone https://github.com/your-username/kiro-spec-claude.git
cd kiro-spec-claude

# Option B: Copy the .claude directory to your project
cp -r /path/to/kiro-spec-claude/.claude /your/project/
```

### 2. Verify Installation

Check that all components are in place:

```bash
# Check hooks
ls .claude/hooks/
# Should show: UserPromptSubmit, PreToolUse, PostToolUse, Stop

# Check agents
ls .claude/agents/
# Should show: agent-bugfix-junior.yml, agent-bugfix-senior.yml, etc.

# Check scripts
ls .claude/scripts/
# Should show: kiro_cli_simple.py, rlvr_evaluate.py, etc.
```

### 3. Initialize Claude Code Settings

The settings.json should already be configured, but verify:

```bash
cat .claude/settings.json
```

## 🎯 Getting Started with Claude Code

### Basic Usage - Autonomous Mode

Just type your request naturally:

```bash
# Example 1: Bug fix
"Fix the login page - users can't sign in with Google"

# Example 2: New feature
"Add a dark mode toggle to the settings page"

# Example 3: Performance issue
"The dashboard is loading slowly with large datasets"
```

The system will automatically:
1. Detect the task type (bugfix/feature/performance)
2. Determine priority
3. Optimize your prompt
4. Select the best agent
5. Execute with proper constraints
6. Evaluate results

### Manual Task Creation (Optional)

For more control, create a task.yml:

```bash
cat > task.yml << EOF
type: feature
priority: P1
description: Add user authentication with JWT
requirements:
  - Implement login/logout endpoints
  - Add JWT token generation
  - Create middleware for protected routes
EOF
```

### Check Status

```bash
# View recent tasks
/kiro-status

# View agent performance
/kiro-leaderboard

# View specific agent details
/kiro-agent agent-bugfix-senior
```

## 📁 Directory Structure

```
.claude/
├── hooks/
│   ├── UserPromptSubmit    # Autonomous task detection & routing
│   ├── PreToolUse          # Tool permission enforcement
│   ├── PostToolUse         # Tool usage tracking
│   └── Stop                # Task evaluation & feedback
├── agents/
│   ├── agent-bugfix-junior.yml
│   ├── agent-bugfix-senior.yml
│   ├── agent-feature-junior.yml
│   ├── agent-feature-senior.yml
│   ├── agent-refactor-principal.yml
│   └── agent-security-senior.yml
├── scripts/
│   ├── kiro_cli_simple.py  # Main CLI tool
│   └── rlvr_evaluate.py    # Evaluation engine
├── prompts/
│   └── optimization-templates.json
├── tasks/                  # Task metadata storage
├── scoreboard/            # Performance metrics
└── feedback/              # Improvement suggestions
```

## 🔧 Configuration

### Customize Task Detection

Edit `.claude/hooks/UserPromptSubmit` to add custom keywords:

```python
task_indicators = {
    'bugfix': ['fix', 'bug', 'error', 'broken'],
    'feature': ['add', 'implement', 'create'],
    'custom_type': ['your', 'keywords', 'here']  # Add your own
}
```

### Adjust Optimization Templates

Edit `.claude/prompts/optimization-templates.json`:

```json
{
  "custom_type": {
    "template": "Your custom optimization template...",
    "keywords": ["your", "keywords"],
    "priority_boost": 0.0
  }
}
```

### Modify Agent Behavior

Edit agent files in `.claude/agents/`:

```yaml
name: agent-custom
tier: senior
specializations: custom - optimization - performance
tools_allowed: all
max_context_tokens: 100000
system_prompt: |
  You are a custom specialist agent...
```

## 🎮 Advanced Usage

### Force Specific Agent

Create a task.yml with agent specification:

```yaml
type: feature
agent_name: agent-feature-senior
description: Your task description
```

### Batch Operations

```bash
# Expand all pending tasks
/kiro-expand-all

# Check dependencies
/kiro-check-deps

# Generate task reports
/kiro-report
```

### Performance Tuning

Monitor and adjust based on feedback:

```bash
# View optimization effectiveness
cat .claude/scoreboard/optimization_effectiveness.jsonl | tail -5

# Check agent performance trends
cat .claude/scoreboard/agent-*_performance.jsonl | tail -5

# Review feedback
cat .claude/feedback/*_feedback.jsonl | tail -5
```

## 🛠️ Troubleshooting

### No Agent Selected

```bash
# Check agents exist
ls .claude/agents/

# Verify no suspended agents
grep "tier: suspended" .claude/agents/*.yml

# Check task detection
# Add debug print in UserPromptSubmit hook
```

### Poor Performance

```bash
# Review recent evaluations
cat .claude/scoreboard/rlvr.jsonl | tail -10 | jq .

# Check feedback
cat .claude/feedback/*_feedback.jsonl | tail -10 | jq .

# Adjust agent tiers if needed
```

### Hook Not Running

```bash
# Verify hook permissions
ls -la .claude/hooks/

# Make executable if needed
chmod +x .claude/hooks/*

# Check Claude Code recognizes hooks
# Should see hooks in Claude Code output
```

## 🚦 Best Practices

### 1. Natural Language Prompts
- Be specific about what you want
- Include context when helpful
- Mention priority if urgent

### 2. Let the System Work
- Don't override agent selection unless necessary
- Trust the optimization process
- Review feedback for improvements

### 3. Monitor Performance
- Check leaderboard weekly
- Review feedback patterns
- Adjust templates based on results

### 4. Iterate and Improve
- Add custom task types as needed
- Refine optimization templates
- Promote/demote agents based on performance

## 📊 Example Workflow

```bash
# 1. Start with a natural request
"The user profile page crashes when uploading large images"

# 2. System automatically:
# - Detects: bugfix task
# - Priority: P2 (medium)
# - Selects: agent-bugfix-senior
# - Optimizes prompt with bugfix template

# 3. Agent works on the task
# - Analyzes the issue
# - Implements fix
# - Adds tests
# - Verifies solution

# 4. Evaluation runs automatically
# - Code quality: ✓
# - Tests added: ✓
# - Security: ✓
# - Reward: 0.85

# 5. Check results
/kiro-status
# Shows completed task with high reward

/kiro-leaderboard
# Shows agent-bugfix-senior performance improved
```

## 🔗 Integration with Existing Projects

### Adding to Existing Project

```bash
cd /your/existing/project

# Copy only the .claude directory
cp -r /path/to/kiro-spec-claude/.claude .

# Verify Claude Code picks it up
ls .claude/hooks/
```

### Gradual Adoption

1. Start with autonomous mode
2. Monitor which agents perform best
3. Customize templates for your project
4. Add project-specific task types
5. Refine based on feedback

## 📚 Next Steps

1. **Read the Documentation**
   - `AUTONOMOUS-SYSTEM.md` - Detailed system overview
   - `prd.md` - Original design requirements
   - `CLAUDE-CODE-FIXES.md` - Implementation notes

2. **Try Different Task Types**
   - Submit various requests
   - Observe agent selection
   - Review evaluations

3. **Customize for Your Needs**
   - Add domain-specific task types
   - Create specialized agents
   - Tune optimization templates

## 💡 Tips

- **Be Patient**: Agents improve over time through the RLVR system
- **Review Feedback**: The Stop hook provides valuable improvement suggestions
- **Trust the Process**: The autonomous system gets better with usage
- **Stay Natural**: Write prompts as you normally would - the system handles the rest

## 🆘 Getting Help

If you encounter issues:

1. Check the logs: `.claude/scoreboard/errors.log`
2. Review recent events: `.claude/scoreboard/events.jsonl`
3. Verify file permissions
4. Ensure Python 3.8+ is available

Remember: The system is designed to be autonomous. Just describe what you need, and Kiro-RLVR handles the rest!