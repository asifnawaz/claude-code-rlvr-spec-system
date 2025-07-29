# Kiro-RLVR Quick Start Guide

## 🎯 Start Using Kiro-RLVR in 30 Seconds

### Step 1: Enter Your Project Directory
```bash
cd /path/to/your/project
```

### Step 2: Copy Kiro-RLVR
```bash
# If you have the repo cloned:
cp -r /path/to/kiro-spec-claude/.claude .

# Or clone it first:
git clone https://github.com/your-org/kiro-spec-claude /tmp/kiro-spec-claude
cp -r /tmp/kiro-spec-claude/.claude .
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

When you type a request, Kiro-RLVR automatically:

1. **Analyzes** your request
2. **Detects** the task type (bug, feature, etc.)
3. **Optimizes** your prompt with helpful context
4. **Selects** the best specialized agent
5. **Executes** with quality constraints
6. **Evaluates** the results
7. **Provides** improvement feedback

## 📊 Monitor Progress

```bash
# Check recent tasks
/kiro-status

# View agent performance
/kiro-leaderboard
```

## 💡 Examples

### Bug Fix
```
Input: "Users can't upload profile pictures larger than 2MB"
→ Detected: Bugfix task
→ Selected: agent-bugfix-senior
→ Added: Bug analysis template
```

### New Feature
```
Input: "Add two-factor authentication"
→ Detected: Feature + Security task
→ Selected: agent-security-senior
→ Added: Security implementation checklist
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
- Check: `ls .claude/agents/` should show agent files

### "Command not found"
- Make sure you're using Claude Code
- The commands only work within Claude Code

### Need Help?
Just ask! The system is designed to be self-explanatory.