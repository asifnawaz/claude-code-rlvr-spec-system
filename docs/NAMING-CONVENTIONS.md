# Doom-RLVR Naming Conventions

## Problem Statement

Currently, we have inconsistent naming across different component types:
- Hooks: Mixed CamelCase (no extension) and kebab-case (.py)
- Scripts: snake_case with .py
- Commands: kebab-case with .md
- Agents: kebab-case with .md

This creates confusion and makes the codebase harder to navigate.

## Proposed Standard

### Universal Rules
1. **Use kebab-case** for all filenames (most readable, URL-safe)
2. **Include appropriate extensions** where possible
3. **Be descriptive** but concise

### Component-Specific Conventions

#### 1. Hooks
Claude Code hooks have special requirements, so we'll use a hybrid approach:
- **Main hooks** (no extension, for Claude Code compatibility):
  - `UserPromptSubmit` → Keep as-is (Claude Code requirement)
  - `PreToolUse` → Keep as-is (Claude Code requirement)
  - `PostToolUse` → Keep as-is (Claude Code requirement)  
  - `Stop` → Keep as-is (Claude Code requirement)
- **Supporting scripts** (.py extension):
  - `pre-check.py` ✓ (already correct)
  - `validate-prompt-structure.py` ✓ (already correct)
  - Any new validation scripts should use kebab-case with .py

#### 2. Scripts (.py or .sh)
Keep descriptive names but convert to kebab-case:
- `doom-cli.py` (was: doom-cli.py)
- `doom-cli-simple.py` (was: doom-cli-simple.py)
- `rlvr-evaluate.py` (was: rlvr-evaluate.py)
- `tier-updater.py` (was: tier-updater.py)
- `manual-assign.py` (was: manual-assign.py)
- `init.sh` ✓ (already correct)

#### 3. Commands (.md)
Already following the convention - no changes needed:
- `doom-status.md` ✓
- `doom-leaderboard.md` ✓
- `doom-report.md` ✓
- `doom-agent.md` ✓
- `start-sprint.md` ✓
- `end-sprint.md` ✓
- `burndown.md` ✓

#### 4. Agents (.md)
Already following the convention - no changes needed:
- `agent-bugfix-junior.md` ✓
- `agent-bugfix-senior.md` ✓
- `agent-feature-junior.md` ✓
- `agent-feature-senior.md` ✓
- `agent-refactor-principal.md` ✓
- `agent-security-senior.md` ✓

## Benefits

1. **Consistency**: Single naming pattern across all components
2. **Clarity**: File extensions make file types obvious
3. **Tooling**: IDEs and editors can properly syntax highlight
4. **URL-safe**: kebab-case works well in URLs and commands
5. **Readability**: kebab-case is easier to read than snake_case or CamelCase

## Migration Plan

1. Create this naming convention document ✓
2. Rename all hooks to follow the pattern
3. Update all Python imports and references
4. Update hook loading logic in scripts
5. Update documentation
6. Test everything works

## Implementation Impact

### Code Changes Required

1. **Hook Loading** (`UserPromptSubmit`, etc.):
   - Update hook name references to new names
   - Ensure Claude Code recognizes .py extension

2. **Script Imports** (`doom-cli.py`, `rlvr-evaluate.py`):
   - Update import statements to use new module names
   - Update any dynamic loading code

3. **Documentation**:
   - Update all references in README.md, SETUP-GUIDE.md, etc.
   - Update code examples

### Backwards Compatibility

For a smooth transition, we could:
1. Keep old names as symlinks temporarily
2. Add deprecation warnings
3. Remove old names in next major version

## Decision

We'll implement a pragmatic approach:

1. **Hooks**: Keep Claude Code required names (no extension)
2. **Scripts**: Use kebab-case for files, provide compatibility wrappers for imports
3. **Commands & Agents**: Already using kebab-case with .md

## Implementation Status

✅ **Completed**:
- Renamed script files to kebab-case
- Created compatibility wrappers for Python imports
- Updated references in documentation and code

⏳ **Pending**:
- Testing all functionality with new names
- Consider deprecating compatibility wrappers in future

This approach gives us:
- Clean, consistent file names
- Backward compatibility for imports
- Clear naming standards going forward