# PRD vs Claude Code Implementation Compatibility

## Overview

This document explains which PRD requirements can be implemented with Claude Code's actual capabilities and which cannot.

## ✅ Implemented Features

### 1. Agent Routing (FR-1)
- **PRD**: Route tasks to specialized sub-agents
- **Implementation**: UserPromptSubmit hook modifies prompts with agent context
- **Limitation**: Not true sub-agents, but simulated through prompt engineering

### 2. RLVR Evaluation (FR-2)
- **PRD**: Run evaluation on SubagentStop
- **Implementation**: Evaluation runs in Stop hook when Claude finishes
- **Note**: SubagentStop hook doesn't exist in Claude Code

### 3. Performance Tracking (FR-3)
- **PRD**: Nightly tier recalculation
- **Implementation**: Manual command `/doom-update-tiers` or Python script
- **Limitation**: No cron capability in Claude Code

### 4. Agent Suspension (FR-4)
- **PRD**: Suspended agents not selectable
- **Implementation**: ✓ Fully implemented in agent selection logic

### 5. CLI Status (FR-5)
- **PRD**: `doom status` returns leaderboard JSON
- **Implementation**: ✓ Implemented as `/doom-status` command

## ❌ Cannot Implement

### 1. True Sub-Agents
- **PRD**: Isolated sub-agent contexts
- **Reality**: Claude Code runs as single instance, no process isolation

### 2. Coordinator Service
- **PRD**: Background service managing agents
- **Reality**: Hooks only run during Claude Code execution

### 3. Sandboxing
- **PRD**: Distrobox + network restrictions
- **Reality**: Claude Code manages its own sandboxing

### 4. Concurrent Agents
- **PRD**: Support 50+ concurrent agents
- **Reality**: Single-threaded execution

### 5. Cross-Project Registry
- **PRD**: Share agents across projects
- **Reality**: No built-in mechanism for this

## 🔄 Adapted Features

### 1. Task Assignment
- **PRD**: `doom assign --task bug-123`
- **Adapted**: Place `task.yml` in project root, Claude auto-routes

### 2. Evaluation Timing
- **PRD**: Evaluate on SubagentStop
- **Adapted**: Evaluate on Stop (when Claude finishes)

### 3. Tier Updates
- **PRD**: Nightly cron job
- **Adapted**: Manual command or post-task trigger

### 4. Logging
- **PRD**: Structured logs to `logs/<date>.ndjson`
- **Adapted**: JSONL files in `.claude/scoreboard/`

## Architecture Differences

### PRD Architecture:
```
Coordinator Service → Sub-Agent Pool → RLVR Evaluator
     ↓                      ↓                ↓
  (persistent)          (isolated)       (async)
```

### Claude Code Reality:
```
UserPromptSubmit → Claude (with context) → Stop Hook
       ↓                    ↓                  ↓
  (modifies prompt)    (single instance)   (evaluate)
```

## Working Within Constraints

Despite limitations, the implementation achieves core PRD goals:

1. **Task Routing** - Via prompt modification
2. **Performance Evaluation** - Via Stop hook
3. **Agent Tiers** - Via local YAML files
4. **Quality Improvement** - Via RLVR scoring

The system works by:
- Injecting agent personas into prompts
- Tracking performance locally
- Adjusting agent selection based on scores
- Providing manual tools for operations that can't be automated

## Recommendations

For full PRD compliance, you would need:
1. External coordinator service (e.g., Python daemon)
2. GitHub Actions for CI integration
3. Cron jobs on the host system
4. External database for cross-project sharing

The current implementation maximizes what's possible within Claude Code's architecture while maintaining the core RLVR concept.