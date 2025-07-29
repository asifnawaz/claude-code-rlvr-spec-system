# Claude Code Compatibility Fixes

## Issues Fixed

### 1. ✅ Removed External Dependencies
- **Problem**: Used `import yaml` and `from rich.console import Console`
- **Fix**: Created simple YAML parser without external dependencies
- **Files affected**: 
  - `UserPromptSubmit` hook - now uses custom YAML parser
  - Created `kiro_cli_simple.py` without Rich library

### 2. ✅ Removed Incorrect Sub-Agent Launcher
- **Problem**: `launch_subagent.py` tried to use non-existent `claude-code --mode subagent`
- **Fix**: Deleted the file - Claude Code doesn't support launching sub-agents

### 3. ✅ Simplified CLI Tools
- **Problem**: Complex CLI with external dependencies
- **Fix**: Created `kiro_cli_simple.py` with basic Python only

### 4. ⚠️ Environment Variable Limitations
- **Problem**: Hooks tried to set environment variables for other hooks
- **Reality**: Each hook runs in isolation - variables don't persist
- **Workaround**: Store state in files under `.claude/tasks/`

### 5. ✅ Updated Command Scripts
- **Problem**: Commands referenced the complex CLI
- **Fix**: Updated to use simple CLI version

## Remaining Limitations

### 1. No Real Sub-Agents
- Claude Code runs as a single instance
- We simulate agents through prompt modification

### 2. No Background Services
- Can't run coordinator or cron jobs
- Everything happens in hooks during execution

### 3. State Management
- Must use files for persistence between hook calls
- No shared memory or environment variables

### 4. Dependencies
- Limited to Python standard library
- No pip install capability

## How It Works Now

1. **Task Routing**: 
   - `UserPromptSubmit` hook reads `task.yml`
   - Selects agent based on simple logic
   - Modifies prompt to include agent context

2. **Constraints**:
   - `PreToolUse` hook checks allowed tools
   - Returns deny decision if tool not allowed

3. **Evaluation**:
   - `Stop` hook runs simplified evaluation
   - Writes scores to JSONL files

4. **Commands**:
   - Simple Python scripts for status/leaderboard
   - No fancy formatting, just basic output

## Usage

The system now works with only Python standard library:

```bash
# Create task
cat > task.yml << EOF
type: bugfix
description: Fix the authentication bug
EOF

# Run Claude Code - automatically routes to best agent
# Check status
/kiro-status

# View leaderboard  
/kiro-leaderboard
```

## What's Not Possible

1. **True multi-agent execution** - Single Claude instance only
2. **Background processing** - No services or cron
3. **Network restrictions** - Claude manages its own network
4. **Package installation** - Can't add Python packages
5. **Cross-project sharing** - No central registry

The implementation now works within Claude Code's actual constraints while maintaining the core RLVR concept through creative use of hooks and prompt engineering.