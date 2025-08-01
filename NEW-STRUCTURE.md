# Doom-RLVR New Directory Structure

## Overview

We've reorganized the Doom-RLVR project to keep the `.claude` directory minimal and Claude Code-specific. All other components have been moved to more logical locations.

## New Structure

```
doom-spec-claude/
├── .claude/                    # ONLY Claude Code essentials
│   ├── hooks/                  # Core hooks (required by Claude Code)
│   │   ├── UserPromptSubmit    # Main hook (no extension)
│   │   ├── PreToolUse          # Main hook (no extension)
│   │   ├── PostToolUse         # Main hook (no extension)
│   │   ├── Stop                # Main hook (no extension)
│   │   ├── pre-check.py        # Security validation
│   │   ├── validate-prompt-structure.py  # Doom template validator
│   │   └── doom_paths.py       # Path configuration helper
│   ├── commands/               # Claude slash commands
│   │   ├── doom-status.md
│   │   ├── doom-leaderboard.md
│   │   ├── start-sprint.md
│   │   └── ...
│   ├── scripts/                # Compatibility wrappers only
│   │   ├── rlvr_evaluate.py    # Import wrapper
│   │   ├── doom_cli.py         # Import wrapper
│   │   └── ...
│   ├── settings.json           # Claude settings
│   ├── settings.local.json     # Local overrides
│   └── CLAUDE.md               # Claude context
│
├── doom/                       # Main Doom-RLVR implementation
│   ├── agents/                 # Agent configurations (.md files)
│   │   ├── agent-bugfix-junior.md
│   │   ├── agent-bugfix-senior.md
│   │   └── ...
│   ├── scripts/                # Main implementation scripts
│   │   ├── doom-cli.py
│   │   ├── doom-cli-simple.py
│   │   ├── rlvr-evaluate.py
│   │   └── ...
│   ├── config/                 # Doom configurations
│   │   ├── paths.json          # Path mappings
│   │   └── evaluator-config.json
│   └── prompts/                # Prompt templates
│       ├── optimization-templates.json
│       └── agent-instructions.md
│
├── data/                       # Runtime data (gitignored)
│   ├── tasks/                  # Task metadata
│   ├── scoreboard/             # Performance metrics
│   │   ├── rlvr.jsonl
│   │   ├── events.jsonl
│   │   └── ...
│   ├── feedback/               # Improvement suggestions
│   └── sprints/                # Sprint tracking
│
└── docs/                       # Documentation
    ├── README.md
    ├── IMPLEMENTATION-NOTES.md
    ├── TROUBLESHOOTING.md
    └── ...
```

## Key Changes

### 1. Minimal `.claude/` Directory
- Only contains files that Claude Code directly requires
- Hooks remain with their specific naming requirements
- Commands stay here as they're Claude-specific
- Added `doom_paths.py` for centralized path management

### 2. New `doom/` Directory
- Contains all the main implementation
- Agents moved here as `.md` files
- Scripts use kebab-case naming
- Configuration files organized here

### 3. `data/` Directory
- All runtime data moved here
- Automatically created by the path helper
- Should be gitignored (contains user data)

### 4. `docs/` Directory
- All documentation moved here
- Better organization for project docs

## Migration Notes

### For Users
When setting up Doom-RLVR in a new project:
```bash
# Copy only the .claude directory
cp -r /path/to/doom-spec-claude/.claude /your/project/

# Copy the doom implementation
cp -r /path/to/doom-spec-claude/doom /your/project/

# Data directories will be created automatically
```

### Path Configuration
All paths are centrally managed through:
- `/doom/config/paths.json` - Path mappings
- `/.claude/hooks/doom_paths.py` - Path helper module

### Compatibility
- Import wrappers in `.claude/scripts/` maintain backward compatibility
- All commands updated to use new paths
- Hooks updated to use the path helper

## Benefits

1. **Cleaner Organization** - Clear separation of concerns
2. **Easier Distribution** - Users know exactly what to copy
3. **Better Maintenance** - Logical grouping of components
4. **Flexible Deployment** - Can customize paths via config

## Testing

To verify everything works:
```bash
# Test a command
/doom-status

# Test agent selection (create a test task)
echo "Fix the login bug" > test-prompt.txt

# Check data directories
ls data/
```