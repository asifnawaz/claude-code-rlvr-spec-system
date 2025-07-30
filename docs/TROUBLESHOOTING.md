# Doom-RLVR Troubleshooting Guide

## Common Issues and Solutions

### 1. "No agent selected" or System doesn't detect task

**Symptoms:**
- Your prompt is processed without agent assignment
- No task type detection occurs

**Solutions:**
- Check if hooks are running: Look for `[Doom-RLVR Agent Assignment]` in output
- Verify agents exist: `ls .claude/agents/agent-*.yml`
- Add more keywords to your prompt (e.g., "fix", "add", "implement")
- Check hook permissions: `chmod +x .claude/hooks/*`

### 2. Commands not found

**Symptoms:**
- `/doom-status: command not found`
- Commands don't work

**Solutions:**
- Ensure you're using Claude Code (not regular terminal)
- Check settings.json exists: `cat .claude/settings.json`
- Verify command scripts are executable: `chmod +x .claude/commands/*.sh`
- Run from project root where .claude exists

### 3. Hook errors

**Symptoms:**
- Error messages about Python modules
- Hooks fail to execute

**Solutions:**
- Check Python 3 is available: `python3 --version`
- Ensure no external dependencies in code (only standard library)
- Check error log: `cat .claude/scoreboard/errors.log`
- Verify hook syntax: `python3 .claude/hooks/UserPromptSubmit < /dev/null`

### 4. No evaluation occurs

**Symptoms:**
- Tasks complete but no reward shown
- Stop hook doesn't provide feedback

**Solutions:**
- Check Stop hook is executable: `ls -la .claude/hooks/Stop`
- Verify task metadata exists: `ls .claude/tasks/`
- Check RLVR evaluator: `python3 .claude/scripts/rlvr-evaluate.py --help`
- Look for errors: `tail .claude/scoreboard/errors.log`

### 5. Agent performance not updating

**Symptoms:**
- Leaderboard shows no data
- Agent performance static

**Solutions:**
- Check performance files: `ls .claude/scoreboard/*_performance.jsonl`
- Verify evaluations are running: `tail .claude/scoreboard/rlvr.jsonl`
- Ensure Stop hook completes: Check for evaluation output

### 6. Task detection incorrect

**Symptoms:**
- Wrong task type detected
- Wrong agent selected

**Solutions:**
- Use clearer keywords in prompt
- Create manual task.yml for specific control:
  ```yaml
  type: bugfix
  priority: P1
  agent_name: agent-bugfix-senior
  description: Your task description
  ```
- Modify detection keywords in UserPromptSubmit hook

### 7. "Permission denied" errors

**Symptoms:**
- Hooks fail with permission errors
- Can't execute commands

**Solutions:**
```bash
# Fix all permissions at once
chmod +x .claude/hooks/*
chmod +x .claude/commands/*.sh
chmod +x .claude/scripts/*.sh
```

### 8. State not persisting

**Symptoms:**
- Tasks disappear between sessions
- Performance data lost

**Solutions:**
- Check directories exist: `ls -la .claude/{tasks,scoreboard,feedback}/`
- Ensure write permissions: `touch .claude/scoreboard/test.tmp && rm .claude/scoreboard/test.tmp`
- Verify files aren't in .gitignore if using git

### 9. Hooks not triggering

**Symptoms:**
- No autonomous behavior
- Prompts processed normally without enhancement

**Solutions:**
- Verify Claude Code recognizes hooks: Should see hook output
- Check settings.json structure is valid JSON
- Ensure project directory is set: `echo $CLAUDE_PROJECT_DIR`
- Try manual test: `echo '{"userPrompt":"test"}' | python3 .claude/hooks/UserPromptSubmit`

### 10. Poor task performance

**Symptoms:**
- Low rewards consistently
- Negative feedback

**Solutions:**
- Review feedback: `tail .claude/feedback/*_feedback.jsonl | jq .`
- Check evaluation criteria in Stop hook
- Ensure test coverage tools available
- Verify lint/security scan commands work

## Debug Mode

To enable detailed debugging:

1. Add debug prints to hooks:
```python
import sys
print(f"DEBUG: Hook starting", file=sys.stderr)
```

2. Check all logs:
```bash
# System events
tail -f .claude/scoreboard/events.jsonl

# Errors
tail -f .claude/scoreboard/errors.log

# Task metadata
find .claude/tasks -name metadata.json -exec cat {} \;
```

3. Test individual components:
```bash
# Test task detection
echo '{"userPrompt":"fix the bug"}' | python3 .claude/hooks/UserPromptSubmit

# Test evaluation
python3 .claude/scripts/rlvr-evaluate.py test-task agent-test completed
```

## Getting Help

If issues persist:

1. Run initialization check:
   ```bash
   bash .claude/scripts/init.sh
   ```

2. Collect diagnostic info:
   ```bash
   find .claude -type f -name "*.jsonl" -exec wc -l {} \;
   ls -la .claude/hooks/
   python3 --version
   ```

3. Check documentation:
   - SETUP-GUIDE.md
   - AUTONOMOUS-SYSTEM.md
   - CLAUDE-CODE-FIXES.md

Remember: The system is designed to work with Python standard library only. Any external dependencies will cause failures.