# Doom-RLVR Technical Specification

## Overview

Doom-RLVR is a Context Engineering Platform for Claude Code that implements a multi-agent system with Reinforcement Learning and Variable Rewards (RLVR) to improve code quality and agent performance through automated evaluation and tier-based routing.

## System Components

### 1. Coordinator Service

**Purpose**: Central orchestrator that routes tasks to appropriate sub-agents based on tier and specialization.

**Responsibilities**:
- Parse incoming task metadata from `task.yml`
- Query agent registry for available agents
- Select optimal agent based on tier, tags, and historical performance
- Monitor task execution and trigger hooks
- Enforce token budget limits

**Key Interfaces**:
```yaml
# task.yml schema
task:
  id: string
  type: bugfix | feature | refactor | security
  tags: string[]
  priority: P0 | P1 | P2
  description: string
  constraints:
    max_tokens: number
    timeout_ms: number
```

### 2. Sub-Agent Pool

**Purpose**: Collection of specialized Claude Code agents with isolated contexts.

**Agent Structure**:
```yaml
# agent-{name}.yml
agent:
  name: string
  tier: junior | senior | principal | suspended
  specializations:
    - bugfix
    - feature
    - refactor
    - security
  performance:
    rolling_avg_reward: number
    total_tasks: number
    last_10_rewards: number[]
  context:
    system_prompt: string
    tools_allowed: string[]
    max_context_tokens: number
```

**Tiers**:
- **Junior**: r < 2.0, handles simple tasks
- **Senior**: 2.0 ≤ r < 4.0, standard development tasks
- **Principal**: r ≥ 4.0, complex features and architecture
- **Suspended**: r < 0 or manual override, not assignable

### 3. RLVR Evaluator

**Purpose**: Compute scalar rewards based on multiple quality signals.

**Evaluation Criteria**:
```python
# Reward components (weights configurable)
reward = weighted_sum([
    (0.3, test_coverage_delta),      # -1 to +1
    (0.2, lint_score),               # 0 to 1
    (0.2, security_scan_score),      # 0 to 1
    (0.1, code_complexity_delta),    # -1 to +1
    (0.1, ci_pipeline_status),       # 0 or 1
    (0.1, review_feedback_score)     # -1 to +1
])
```

**Hook Integration**:
```bash
# .claude/hooks/SubagentStop
#!/bin/bash
python3 .claude/scripts/rlvr-evaluate.py \
  --task-id "$TASK_ID" \
  --agent-name "$AGENT_NAME" \
  --output-dir "$PROJECT_ROOT/.claude/scoreboard"
```

### 4. Scoreboard Store

**Purpose**: Persistent storage for agent performance metrics.

**Data Schemas**:

```jsonl
# rlvr.jsonl
{"timestamp": "2025-08-12T10:30:00Z", "task_id": "bug-123", "agent": "agent-bugfix-senior", "reward": 3.7, "components": {...}}
```

```json
# agent_tiers.json
{
  "agents": {
    "agent-bugfix-senior": {
      "tier": "senior",
      "rolling_avg": 3.7,
      "last_updated": "2025-08-12T10:30:00Z"
    }
  }
}
```

### 5. Tier Update Service

**Purpose**: Nightly job that recalculates agent tiers based on performance.

**Algorithm**:
```python
def update_tiers():
    for agent in agents:
        recent_rewards = get_last_n_rewards(agent, n=10)
        rolling_avg = mean(recent_rewards)
        
        if rolling_avg >= 4.0:
            agent.tier = "principal"
        elif rolling_avg >= 2.0:
            agent.tier = "senior"
        elif rolling_avg >= 0:
            agent.tier = "junior"
        else:
            agent.tier = "suspended"
```

## API Specifications

### CLI Commands

```bash
# Task management
doom assign --task <id> [--force-agent <name>]
doom status [--format json|table]
doom logs --tail [--agent <name>]

# Agent management
doom agents list [--tier <tier>]
doom agents promote <name>
doom agents suspend <name> [--reason <text>]

# Scoreboard operations
doom scores --agent <name> [--last <n>]
doom leaderboard [--metric reward|tasks|success-rate]
```

### Hook Events

```typescript
interface HookEvent {
  type: 'TaskStart' | 'PostToolUse' | 'SubagentStop' | 'TaskComplete'
  timestamp: string
  task_id: string
  agent_name: string
  payload: Record<string, any>
}
```

### REST API (Future)

```yaml
openapi: 3.0.0
paths:
  /api/v1/tasks:
    post:
      summary: Submit new task
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Task'
  
  /api/v1/agents/{name}/metrics:
    get:
      summary: Get agent performance metrics
      parameters:
        - name: name
          in: path
          required: true
```

## Data Models

### Task Model
```typescript
interface Task {
  id: string
  type: 'bugfix' | 'feature' | 'refactor' | 'security'
  status: 'pending' | 'assigned' | 'in_progress' | 'completed' | 'failed'
  assigned_agent?: string
  created_at: Date
  completed_at?: Date
  metadata: {
    tags: string[]
    priority: 'P0' | 'P1' | 'P2'
    description: string
    constraints: {
      max_tokens: number
      timeout_ms: number
    }
  }
  outcome?: {
    pr_url?: string
    error_message?: string
    tokens_used: number
    duration_ms: number
  }
}
```

### Agent Model
```typescript
interface Agent {
  name: string
  tier: 'junior' | 'senior' | 'principal' | 'suspended'
  created_at: Date
  specializations: string[]
  performance: {
    rolling_avg_reward: number
    total_tasks: number
    success_rate: number
    last_10_rewards: number[]
    tier_history: Array<{
      tier: string
      timestamp: Date
      reason: string
    }>
  }
  config: {
    system_prompt: string
    tools_allowed: string[]
    max_context_tokens: number
    custom_hooks?: string[]
  }
}
```

### Reward Model
```typescript
interface Reward {
  timestamp: Date
  task_id: string
  agent_name: string
  reward: number  // -5 to +5
  components: {
    test_coverage_delta: number
    lint_score: number
    security_scan_score: number
    code_complexity_delta: number
    ci_pipeline_status: number
    review_feedback_score: number
  }
  metadata: {
    evaluator_version: string
    hook_duration_ms: number
  }
}
```

## Security Specifications

### Sandboxing
- Hooks execute in isolated environment using `distrobox`
- Network access restricted to whitelisted domains:
  - `api.github.com`
  - `*.githubusercontent.com`
  - CI/CD endpoints

### Access Control
```yaml
# .claude/permissions.yml
hooks:
  allowed_commands:
    - git
    - npm
    - python3
    - rg
    - jq
  forbidden_paths:
    - /etc
    - /root
    - ~/.ssh
  environment_vars:
    - GITHUB_TOKEN: read-only
    - CI_API_KEY: encrypted
```

### Audit Logging
```json
{
  "event": "agent_execution",
  "timestamp": "2025-08-12T10:30:00Z",
  "agent": "agent-bugfix-senior",
  "task_id": "bug-123",
  "actions": [
    {"tool": "Edit", "file": "src/main.py", "status": "success"},
    {"tool": "Bash", "command": "pytest", "status": "success"}
  ],
  "security_flags": []
}
```

## Performance Requirements

### Latency Targets
- Task routing: < 200ms
- Hook execution: < 5s
- Reward calculation: < 1s
- Tier update (per agent): < 100ms

### Resource Limits
```yaml
coordinator:
  memory: 512MB
  cpu: 0.5 cores

per_agent:
  memory: 2GB
  cpu: 1 core
  max_context_tokens: 100000

evaluator:
  memory: 256MB
  cpu: 0.25 cores
  parallel_evaluations: 4
```

## Configuration Files

### Project Configuration
```toml
# .claude/doom-rlvr.toml
[coordinator]
port = 8080
max_concurrent_agents = 10
task_timeout_default_ms = 300000

[evaluator]
weights = {
  test_coverage = 0.3,
  lint_score = 0.2,
  security_scan = 0.2,
  complexity = 0.1,
  ci_status = 0.1,
  review_feedback = 0.1
}

[scoreboard]
retention_days = 90
compact_on_startup = true

[tiers]
promotion_threshold = 4.0
demotion_threshold = 2.0
suspension_threshold = 0.0
evaluation_window = 10  # last N tasks
```

### Agent Template
```yaml
# .claude/agents/template.yml
agent:
  name: "agent-{{type}}-{{tier}}"
  tier: "{{tier}}"
  specializations:
    - "{{type}}"
  performance:
    rolling_avg_reward: 0
    total_tasks: 0
    last_10_rewards: []
  context:
    system_prompt: |
      You are a {{tier}}-level Claude Code agent specialized in {{type}} tasks.
      Focus on code quality, test coverage, and security best practices.
      {{custom_instructions}}
    tools_allowed:
      - Read
      - Edit
      - Bash
      - Grep
      - WebSearch
    max_context_tokens: 50000
```

## Implementation Phases

### Phase 1: MVP (Aug 12, 2025)
- Basic coordinator with manual agent selection
- Simple task routing based on tags
- Manual reward entry via CLI
- Basic scoreboard (JSONL file)

### Phase 2: RLVR Integration (Sep 02, 2025)
- Automated hook-based evaluation
- Multi-component reward calculation
- Real-time leaderboard updates
- Agent performance tracking

### Phase 3: Tier Automation (Sep 30, 2025)
- Automated tier promotion/demotion
- Rolling average calculations
- Suspension mechanism
- Performance history tracking

### Phase 4: Cross-Project Registry (Oct 28, 2025)
- Shared agent reputation system
- Export/import agent profiles
- Global leaderboard
- Best practices repository

## Monitoring & Observability

### Metrics
```prometheus
# Task metrics
doom_tasks_total{status="completed|failed|timeout"}
doom_task_duration_seconds{agent="name", percentile="p50|p90|p99"}

# Agent metrics
doom_agent_reward{agent="name", component="test|lint|security"}
doom_agent_tier{agent="name", tier="junior|senior|principal"}

# System metrics
doom_coordinator_queue_length
doom_evaluator_duration_seconds
doom_hooks_failed_total{hook="name"}
```

### Dashboards
- Task completion rates by agent tier
- Reward distribution histograms
- Agent promotion/demotion events
- Token usage by agent and task type

## Error Handling

### Failure Modes
1. **Agent Timeout**: Task reassigned to higher-tier agent
2. **Hook Failure**: Logged, task continues with default reward
3. **Token Limit**: Task split or escalated to Principal agent
4. **Evaluation Error**: Fallback to previous reward value

### Recovery Strategies
```python
class TaskRecovery:
    def on_agent_failure(task, agent, error):
        if error.type == "timeout":
            return reassign_to_tier(task, agent.tier + 1)
        elif error.type == "token_limit":
            return split_task(task) or escalate_to_principal(task)
        else:
            return mark_failed(task, error)
```

## Testing Strategy

### Unit Tests
- Coordinator routing logic
- Reward calculation components
- Tier update algorithms
- Hook sandboxing

### Integration Tests
- End-to-end task flow
- Multi-agent coordination
- Hook execution pipeline
- Scoreboard persistence

### Performance Tests
- 50 concurrent agents
- 1000 tasks/hour throughput
- Sub-second routing latency
- Memory usage under load

## Deployment Guide

### Prerequisites
```bash
# System requirements
- Python 3.11+
- Claude Code CLI installed
- Git for version control
- Optional: Docker for sandboxing

# Environment setup
export ANTHROPIC_API_KEY="sk-..."
export GITHUB_TOKEN="ghp-..."
```

### Installation
```bash
# Clone repository
git clone https://github.com/org/doom-rlvr
cd doom-rlvr

# Install dependencies
pip install -r requirements.txt

# Initialize project structure
./scripts/init-doom-rlvr.sh

# Configure agents
cp .claude/agents/template.yml .claude/agents/agent-bugfix-junior.yml
# Edit agent configuration...

# Start coordinator
doom serve --config .claude/doom-rlvr.toml
```

### Verification
```bash
# Check system status
doom status

# Submit test task
doom assign --task test-001 --type bugfix

# View results
doom scores --agent agent-bugfix-junior --last 1
```