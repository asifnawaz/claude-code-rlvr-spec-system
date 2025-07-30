# Doom-RLVR Directory Restructure Plan

## What Claude Code Needs in `.claude/`

### Essential for Claude Code:
1. **Hooks** - Core functionality
   - `hooks/UserPromptSubmit`
   - `hooks/PreToolUse`
   - `hooks/PostToolUse`
   - `hooks/Stop`
   - `hooks/pre-check.py`
   - `hooks/validate-prompt-structure.py`

2. **Commands** - Claude slash commands
   - `commands/*.md`

3. **Settings** - Claude configuration
   - `settings.json`
   - `settings.local.json`

4. **Claude-specific docs**
   - `CLAUDE.md` (context for Claude)

### Should Move Outside `.claude/`:

1. **Scripts** (utility/support scripts)
   - `scripts/doom-cli.py`
   - `scripts/doom-cli-simple.py`
   - `scripts/rlvr-evaluate.py`
   - `scripts/tier-updater.py`
   - `scripts/manual-assign.py`
   - `scripts/rename-to-kebab-case.py`
   - `scripts/init.sh`
   - Compatibility wrappers

2. **Agents** (configuration files)
   - `agents/*.md`

3. **Configuration** (non-Claude configs)
   - `config/evaluator-config.json`
   - `prompts/optimization-templates.json`
   - `prompts/agent-instructions.md`

4. **Data/Storage** (runtime data)
   - `tasks/`
   - `scoreboard/`
   - `feedback/`

5. **Documentation** (project docs)
   - `README.md`
   - `IMPLEMENTATION-NOTES.md`
   - `TROUBLESHOOTING.md`
   - `NAMING-CONVENTIONS.md`
   - `NAMING-STANDARDS-SUMMARY.md`
   - `hooks.md`

## Proposed New Structure

```
doom-spec-claude/
├── .claude/                    # Only Claude Code essentials
│   ├── hooks/                  # Core hooks
│   ├── commands/               # Slash commands
│   ├── settings.json          # Claude settings
│   └── CLAUDE.md              # Claude context
│
├── doom/                      # Main Doom-RLVR implementation
│   ├── agents/                # Agent configurations
│   ├── scripts/               # Utility scripts
│   ├── config/                # Doom configurations
│   └── prompts/               # Prompt templates
│
├── data/                      # Runtime data (gitignored)
│   ├── tasks/
│   ├── scoreboard/
│   └── feedback/
│
└── docs/                      # Documentation
    ├── IMPLEMENTATION-NOTES.md
    ├── TROUBLESHOOTING.md
    └── architecture/
```

## Benefits

1. **Cleaner `.claude/` folder** - Only Claude-specific files
2. **Better organization** - Logical grouping of components
3. **Easier maintenance** - Clear separation of concerns
4. **Simpler distribution** - Users only copy what they need