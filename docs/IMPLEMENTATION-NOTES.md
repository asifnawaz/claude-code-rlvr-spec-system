# Doom-RLVR Implementation Notes

## Compliance with Claude Code

This implementation follows Claude Code's official guidelines with some creative extensions:

### ✅ Official Claude Code Features Used

1. **Hooks** (settings.json)
   - UserPromptSubmit - Intercepts user prompts
   - PreToolUse - Validates tool usage
   - PostToolUse - Tracks tool usage
   - Stop - Runs after task completion

2. **Custom Commands** (.claude/commands/*.md)
   - Markdown files with YAML frontmatter
   - Uses official format with allowed-tools
   - Leverages bash execution with !`command`

3. **Environment Variables** (settings.json "env")
   - DOOM_ENABLED
   - DOOM_VERSION

4. **CLAUDE.md**
   - Project context for Claude Code

### 🔧 Creative Extensions

1. **Agent System**
   - The `agents/` directory contains YAML files that define agent "personas"
   - These are NOT official Claude Code agents (which don't exist)
   - Instead, they're configuration files read by our hooks
   - The UserPromptSubmit hook reads these to modify prompts

2. **Simulated Multi-Agent Behavior**
   - We simulate different agents through prompt engineering
   - Each "agent" is just a different system prompt template
   - The hooks inject these prompts based on task type

3. **RLVR Evaluation**
   - Implemented entirely in Python hooks
   - Uses file-based storage for persistence
   - No external services or databases

### 📁 Directory Structure

```
.claude/
├── settings.json          # Official Claude Code config
├── CLAUDE.md             # Official context file
├── commands/             # Official custom commands (*.md)
├── hooks/                # Official hook scripts
├── agents/               # Our extension - agent configs
├── scripts/              # Helper Python scripts
├── prompts/              # Prompt templates
├── tasks/                # Task metadata storage
├── scoreboard/           # Performance tracking
└── feedback/             # Improvement suggestions
```

### 🚨 Important Notes

1. **No Real Sub-Agents**: Claude Code doesn't support spawning sub-agents. Our "agents" are simulated through prompt modification.

2. **No Persistent Services**: Everything runs as hooks - no background processes.

3. **File-Based State**: All state is stored in files since environment variables don't persist between hook executions.

4. **Python Standard Library Only**: No external dependencies to ensure compatibility.

### 🔄 How It Works

1. User types a natural language prompt
2. UserPromptSubmit hook:
   - Detects task type
   - Reads appropriate agent config from `agents/`
   - Modifies the prompt with agent's system prompt
   - Adds optimization templates
3. Claude Code processes the enhanced prompt
4. Stop hook evaluates the result using RLVR
5. Performance data is saved for future agent selection

This approach maximizes what's possible within Claude Code's constraints while providing an intelligent, autonomous experience.