# Doom-RLVR Quick Start Guide

## 🎯 Start Using Doom-RLVR in 30 Seconds

### Step 1: Enter Your Project Directory
```bash
cd /path/to/your/project
```

### Step 2: Copy Doom-RLVR
```bash
# If you have the repo cloned:
cp -r /path/to/doom-spec-claude/.claude .

# Or clone it first:
git clone https://github.com/asifnawaz/claude-code-rlvr-spec-system /tmp/doom-spec-claude
cp -r /tmp/doom-spec-claude/.claude .
```

### Step 3: Start Using Natural Language
That's it! Just type what you need:

```bash
# Examples:
"Fix the authentication bug"
"Add a search feature to the user dashboard"
"Optimize the database queries in the reports module"
```

## 🚀 What Happens Next?

When you type a request, Doom-RLVR automatically:

1. **Analyzes** your request
2. **Detects** the task type (bug, feature, etc.)
3. **Generates** Doom template with $GOAL, $CONTEXT, etc.
4. **Selects** the best agent from .md profiles
5. **Validates** tool usage for security
6. **Executes** with quality constraints
7. **Evaluates** results including template compliance
8. **Provides** improvement feedback

## 📊 Monitor Progress

```bash
# Check recent tasks
/doom-status

# View agent performance
/doom-leaderboard

# Start a sprint
/start-sprint "Sprint 1" 14

# Check sprint progress
/burndown
```

## 💡 Examples

### Bug Fix
```
Input: "Users can't upload profile pictures larger than 2MB"
→ Detected: Bugfix task
→ Generated: Doom template with $GOAL, $CONTEXT, etc.
→ Selected: agent-bugfix-senior (from .md profile)
→ Validated: Tool usage checked by pre-check.py
→ Score: Template compliance adds 15% to RLVR
```

### New Feature
```
Input: "Add two-factor authentication"
→ Detected: Feature + Security task
→ Generated: Doom template with security constraints
→ Selected: agent-security-senior (specialized in auth)
→ Added: $ACCEPTANCE_CRITERIA with security checklist
→ Tracked: Sprint velocity and burndown
```

### Performance
```
Input: "The search is too slow"
→ Detected: Performance task
→ Selected: agent-feature-senior
→ Added: Performance optimization template
```

## 🎨 No Configuration Needed

- ✅ Works immediately after copying
- ✅ No API keys required
- ✅ No setup commands
- ✅ No dependencies to install
- ✅ Natural language only

## 📚 Learn More

- Full setup options: [SETUP-GUIDE.md](SETUP-GUIDE.md)
- How it works: [AUTONOMOUS-SYSTEM.md](AUTONOMOUS-SYSTEM.md)
- Customization: [SETUP-GUIDE.md#configuration](SETUP-GUIDE.md#configuration)

## 🔧 Troubleshooting

### "No agent selected"
- The `.claude` directory might not be in the right place
- Check: `ls .claude/agents/` should show .md files (not .yml)

### "Command not found"
- Make sure you're using Claude Code
- The commands only work within Claude Code

### Need Help?
Just ask! The system is designed to be self-explanatory.