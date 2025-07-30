# Doom-RLVR Naming Standards Summary

## Final Naming Convention

### 1. Hooks (Claude Code Requirements)
- **Main hooks**: CamelCase, no extension
  - `UserPromptSubmit`
  - `PreToolUse`
  - `PostToolUse`
  - `Stop`
- **Supporting scripts**: kebab-case with .py
  - `pre-check.py`
  - `validate-prompt-structure.py`

### 2. Scripts (.py/.sh)
- **File names**: kebab-case
  - `doom-cli.py`
  - `doom-cli-simple.py`
  - `rlvr-evaluate.py`
  - `tier-updater.py`
  - `manual-assign.py`
  - `init.sh`
- **Imports**: Use compatibility wrappers (underscore names)
  ```python
  from rlvr_evaluate import RLVREvaluator  # Works!
  ```

### 3. Commands (.md)
- **All use kebab-case**:
  - `doom-status.md`
  - `doom-leaderboard.md`
  - `start-sprint.md`
  - `end-sprint.md`
  - `burndown.md`

### 4. Agents (.md)
- **All use kebab-case**:
  - `agent-bugfix-junior.md`
  - `agent-bugfix-senior.md`
  - `agent-feature-junior.md`
  - `agent-feature-senior.md`
  - `agent-refactor-principal.md`
  - `agent-security-senior.md`

## Benefits Achieved

✅ **Consistency**: kebab-case for all file names (except Claude hooks)
✅ **Compatibility**: Old imports still work via wrappers
✅ **Clarity**: Extensions clearly indicate file types
✅ **Standards**: Following industry best practices

## Migration Complete

All files have been renamed and compatibility maintained. No breaking changes!