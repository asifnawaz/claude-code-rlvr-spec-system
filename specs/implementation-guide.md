# Kiro-RLVR Implementation Guide

## Getting Started

This guide provides step-by-step instructions for implementing the Kiro-RLVR Context Engineering Platform for Claude Code.

## Prerequisites

- Python 3.11+
- Claude Code CLI installed and configured
- Git version control
- Node.js 18+ (for JavaScript project examples)
- Docker or Distrobox (for sandboxing)

## Project Structure

```
kiro-rlvr/
├── .claude/
│   ├── agents/                  # Agent definitions
│   │   ├── agent-bugfix-junior.yml
│   │   ├── agent-feature-senior.yml
│   │   └── template.yml
│   ├── hooks/                   # Hook scripts
│   │   ├── TaskStart
│   │   ├── PostToolUse
│   │   ├── SubagentStop
│   │   └── TaskComplete
│   ├── scripts/                 # Core scripts
│   │   ├── rlvr-evaluate.py
│   │   ├── tier-updater.py
│   │   └── coordinator.py
│   ├── scoreboard/             # Performance data
│   │   ├── rlvr.jsonl
│   │   └── agent_tiers.json
│   ├── config/                 # Configuration files
│   │   ├── kiro-rlvr.toml
│   │   ├── evaluator-config.json
│   │   ├── sandbox-config.yml
│   │   └── hooks.yaml
│   └── tasks/                  # Task workspace
├── src/                        # Platform source code
│   ├── coordinator/
│   ├── evaluator/
│   ├── agents/
│   └── api/
├── tests/                      # Test suites
├── docs/                       # Documentation
└── examples/                   # Example projects
```

## Step 1: Initialize Project

```bash
# Create project directory
mkdir kiro-rlvr && cd kiro-rlvr

# Initialize git repository
git init

# Create directory structure
mkdir -p .claude/{agents,hooks,scripts,scoreboard,config,tasks}
mkdir -p src/{coordinator,evaluator,agents,api}
mkdir -p tests docs examples

# Initialize Python environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install typer pydantic pyyaml jsonlines httpx fastapi uvicorn
```

## Step 2: Create Core Configuration

### Main Configuration File

```toml
# .claude/config/kiro-rlvr.toml

[coordinator]
port = 8080
host = "127.0.0.1"
max_concurrent_agents = 10
task_timeout_default_ms = 300000
queue_max_size = 100

[evaluator]
[evaluator.weights]
test_coverage = 0.3
lint_score = 0.2
security_scan = 0.2
complexity = 0.1
ci_status = 0.1
review_feedback = 0.1

[evaluator.thresholds]
min_test_coverage = 0.8
max_complexity_increase = 0.1
critical_security_fail = 0

[scoreboard]
retention_days = 90
compact_on_startup = true
backup_enabled = true
backup_path = ".claude/backups/"

[tiers]
promotion_threshold = 4.0
demotion_threshold = 2.0
suspension_threshold = 0.0
evaluation_window = 10
grace_period_tasks = 3

[security]
sandbox_enabled = true
audit_log_enabled = true
audit_retention_days = 30
```

## Step 3: Implement Coordinator

```python
# src/coordinator/coordinator.py

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import typer
from pydantic import BaseModel
import yaml
import jsonlines

app = typer.Typer()

class Task(BaseModel):
    id: str
    type: str
    status: str = "pending"
    priority: str = "P1"
    tags: List[str] = []
    description: str
    assigned_agent: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    constraints: Dict = {}

class Agent(BaseModel):
    name: str
    tier: str
    specializations: List[str]
    performance: Dict
    config: Dict

class Coordinator:
    def __init__(self, config_path: str = ".claude/config/kiro-rlvr.toml"):
        self.config = self._load_config(config_path)
        self.agents = self._load_agents()
        self.task_queue: List[Task] = []
        self.active_tasks: Dict[str, Task] = {}
    
    def _load_config(self, path: str) -> Dict:
        import tomli
        with open(path, "rb") as f:
            return tomli.load(f)
    
    def _load_agents(self) -> List[Agent]:
        agents = []
        agent_dir = Path(".claude/agents")
        
        for agent_file in agent_dir.glob("agent-*.yml"):
            with open(agent_file) as f:
                agent_data = yaml.safe_load(f)
                agents.append(Agent(**agent_data["agent"]))
        
        return agents
    
    def select_agent(self, task: Task) -> Optional[Agent]:
        """Select best agent for task based on tier and specialization"""
        
        # Filter agents by specialization
        candidates = [
            agent for agent in self.agents
            if task.type in agent.specializations
            and agent.tier != "suspended"
        ]
        
        if not candidates:
            return None
        
        # Sort by tier (principal > senior > junior) and performance
        tier_order = {"principal": 3, "senior": 2, "junior": 1}
        candidates.sort(
            key=lambda a: (
                tier_order.get(a.tier, 0),
                a.performance.get("rolling_avg_reward", 0)
            ),
            reverse=True
        )
        
        return candidates[0]
    
    async def assign_task(self, task: Task) -> Optional[str]:
        """Assign task to agent and execute"""
        
        agent = self.select_agent(task)
        if not agent:
            print(f"No suitable agent found for task {task.id}")
            return None
        
        task.assigned_agent = agent.name
        task.status = "assigned"
        self.active_tasks[task.id] = task
        
        # Trigger TaskStart hook
        await self._run_hook("TaskStart", {
            "TASK_ID": task.id,
            "TASK_TYPE": task.type,
            "AGENT_NAME": agent.name,
            "AGENT_TIER": agent.tier
        })
        
        # Execute via Claude Code
        result = await self._execute_with_agent(task, agent)
        
        # Trigger SubagentStop hook
        await self._run_hook("SubagentStop", {
            "TASK_ID": task.id,
            "AGENT_NAME": agent.name,
            "TASK_STATUS": result["status"]
        })
        
        return result.get("pr_url")
    
    async def _execute_with_agent(self, task: Task, agent: Agent) -> Dict:
        """Execute task using Claude Code with specific agent context"""
        
        # Create agent-specific context file
        context_path = Path(f".claude/tasks/{task.id}/context.md")
        context_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(context_path, "w") as f:
            f.write(f"# Task: {task.id}\n\n")
            f.write(f"## Agent: {agent.name} ({agent.tier})\n\n")
            f.write(f"## Instructions\n\n{agent.config['system_prompt']}\n\n")
            f.write(f"## Task Description\n\n{task.description}\n")
        
        # Execute via Claude Code CLI
        import subprocess
        result = subprocess.run([
            "claude", "code",
            "--context", str(context_path),
            "--max-tokens", str(task.constraints.get("max_tokens", 100000)),
            "--tools", ",".join(agent.config["tools_allowed"]),
            "--output", f".claude/tasks/{task.id}/output.md"
        ], capture_output=True, text=True)
        
        return {
            "status": "completed" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
    
    async def _run_hook(self, hook_name: str, env: Dict[str, str]) -> None:
        """Execute hook script with environment variables"""
        
        hook_path = Path(f".claude/hooks/{hook_name}")
        if not hook_path.exists():
            return
        
        import subprocess
        subprocess.run(
            [str(hook_path)],
            env={**os.environ, **env},
            timeout=30
        )

@app.command()
def serve(
    config: str = typer.Option(".claude/config/kiro-rlvr.toml", help="Config file path"),
    port: int = typer.Option(8080, help="API port")
):
    """Start the coordinator service"""
    
    coordinator = Coordinator(config)
    
    # Start FastAPI server
    from fastapi import FastAPI
    import uvicorn
    
    api = FastAPI(title="Kiro-RLVR Coordinator")
    
    @api.post("/tasks")
    async def create_task(task: Task):
        result = await coordinator.assign_task(task)
        return {"task_id": task.id, "pr_url": result}
    
    @api.get("/agents")
    def list_agents():
        return coordinator.agents
    
    uvicorn.run(api, host="127.0.0.1", port=port)

if __name__ == "__main__":
    app()
```

## Step 4: Create Agent Templates

### Junior Agent Example

```yaml
# .claude/agents/agent-bugfix-junior.yml
agent:
  name: agent-bugfix-junior
  tier: junior
  specializations:
    - bugfix
    - testing
  performance:
    rolling_avg_reward: 2.5
    total_tasks: 45
    last_10_rewards: [2.1, 2.3, 2.8, 2.5, 2.9, 2.4, 2.6, 2.7, 2.3, 2.5]
  config:
    system_prompt: |
      You are a junior-level Claude Code agent specialized in bug fixes.
      Focus on:
      - Finding and fixing the reported bug
      - Adding tests to prevent regression
      - Following existing code patterns
      - Asking for clarification when needed
      
      Be careful and methodical. Double-check your changes.
    tools_allowed:
      - Read
      - Edit
      - Grep
      - Test
    max_context_tokens: 50000
```

### Senior Agent Example

```yaml
# .claude/agents/agent-feature-senior.yml
agent:
  name: agent-feature-senior
  tier: senior
  specializations:
    - feature
    - refactor
    - bugfix
  performance:
    rolling_avg_reward: 3.8
    total_tasks: 120
    last_10_rewards: [3.5, 4.0, 3.9, 3.7, 4.1, 3.8, 3.6, 4.0, 3.8, 3.9]
  config:
    system_prompt: |
      You are a senior-level Claude Code agent specialized in feature development.
      Your approach should:
      - Design clean, maintainable solutions
      - Consider edge cases and error handling
      - Write comprehensive tests
      - Document complex logic
      - Optimize for performance and readability
      
      You have autonomy to make architectural decisions within reason.
    tools_allowed:
      - Read
      - Edit
      - MultiEdit
      - Grep
      - Test
      - Bash
      - WebSearch
    max_context_tokens: 75000
```

## Step 5: Implement Hook Scripts

### TaskStart Hook

```bash
#!/bin/bash
# .claude/hooks/TaskStart

set -euo pipefail

echo "[TaskStart] Initializing task $TASK_ID for agent $AGENT_NAME"

# Create task workspace
TASK_DIR="$PROJECT_ROOT/.claude/tasks/$TASK_ID"
mkdir -p "$TASK_DIR"/{logs,artifacts,metrics}

# Record task metadata
cat > "$TASK_DIR/metadata.json" <<EOF
{
  "task_id": "$TASK_ID",
  "task_type": "$TASK_TYPE",
  "agent_name": "$AGENT_NAME",
  "agent_tier": "$AGENT_TIER",
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_root": "$PROJECT_ROOT"
}
EOF

# Validate repository state
cd "$PROJECT_ROOT"
if ! git diff --quiet; then
    echo "WARNING: Uncommitted changes detected"
    git stash push -m "Auto-stash for task $TASK_ID"
fi

# Initialize monitoring
if [ -n "${MONITORING_WEBHOOK:-}" ]; then
    curl -s -X POST "$MONITORING_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{
            \"event\": \"task_start\",
            \"task_id\": \"$TASK_ID\",
            \"agent\": \"$AGENT_NAME\",
            \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
        }" || true
fi

echo "[TaskStart] Task initialization complete"
```

## Step 6: Example Task Submission

```python
# examples/submit_task.py

import httpx
import asyncio
from datetime import datetime

async def submit_bugfix_task():
    """Example: Submit a bug fix task to Kiro-RLVR"""
    
    task = {
        "id": f"bug-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "type": "bugfix",
        "priority": "P1",
        "tags": ["authentication", "security"],
        "description": """
        Fix authentication bypass vulnerability in login endpoint.
        
        Issue: Users can bypass 2FA by manipulating the session cookie.
        
        Requirements:
        1. Validate session integrity on each request
        2. Add tests for session tampering scenarios
        3. Update security documentation
        
        Files likely affected:
        - src/auth/middleware.js
        - src/auth/session.js
        - tests/auth/security.test.js
        """,
        "constraints": {
            "max_tokens": 50000,
            "timeout_ms": 600000,
            "required_checks": ["security_scan", "auth_tests"]
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8080/tasks",
            json=task
        )
        
        result = response.json()
        print(f"Task submitted: {result['task_id']}")
        if result.get('pr_url'):
            print(f"PR created: {result['pr_url']}")

if __name__ == "__main__":
    asyncio.run(submit_bugfix_task())
```

## Step 7: Deploy and Run

### Local Development

```bash
# 1. Start the coordinator
cd kiro-rlvr
source venv/bin/activate
python src/coordinator/coordinator.py serve

# 2. In another terminal, submit a task
python examples/submit_task.py

# 3. Monitor progress
kiro logs --tail --task bug-20250729-143022

# 4. Check leaderboard
kiro leaderboard --metric reward
```

### Production Deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  coordinator:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./.claude:/app/.claude
      - ./src:/app/src
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    command: python src/coordinator/coordinator.py serve

  tier-updater:
    build: .
    volumes:
      - ./.claude:/app/.claude
    command: |
      sh -c 'while true; do
        python .claude/scripts/tier-updater.py
        sleep 86400
      done'

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Monitoring Setup

```python
# src/monitoring/metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
task_counter = Counter(
    'kiro_tasks_total',
    'Total number of tasks processed',
    ['status', 'type', 'agent_tier']
)

task_duration = Histogram(
    'kiro_task_duration_seconds',
    'Task execution duration',
    ['type', 'agent_tier']
)

agent_reward_gauge = Gauge(
    'kiro_agent_reward',
    'Current agent reward score',
    ['agent_name']
)

# Usage in coordinator
def record_task_metrics(task, agent, duration, status):
    task_counter.labels(
        status=status,
        type=task.type,
        agent_tier=agent.tier
    ).inc()
    
    task_duration.labels(
        type=task.type,
        agent_tier=agent.tier
    ).observe(duration)
```

## Step 8: Testing

### Unit Tests

```python
# tests/test_coordinator.py

import pytest
from src.coordinator.coordinator import Coordinator, Task, Agent

@pytest.fixture
def coordinator():
    return Coordinator("tests/fixtures/test-config.toml")

def test_agent_selection(coordinator):
    """Test agent selection logic"""
    
    task = Task(
        id="test-001",
        type="bugfix",
        description="Fix test bug"
    )
    
    # Add test agents
    coordinator.agents = [
        Agent(
            name="junior-1",
            tier="junior",
            specializations=["bugfix"],
            performance={"rolling_avg_reward": 2.0},
            config={}
        ),
        Agent(
            name="senior-1",
            tier="senior",
            specializations=["bugfix"],
            performance={"rolling_avg_reward": 3.5},
            config={}
        )
    ]
    
    selected = coordinator.select_agent(task)
    assert selected.name == "senior-1"  # Should select higher tier

def test_reward_calculation():
    """Test RLVR reward calculation"""
    from src.evaluator.rlvr_evaluate import calculate_reward
    
    components = {
        "test_coverage_delta": 0.5,
        "lint_score": 0.8,
        "security_scan_score": 1.0,
        "code_complexity_delta": -0.2,
        "ci_pipeline_status": 1.0,
        "review_feedback_score": 0.0
    }
    
    reward = calculate_reward(components, "completed")
    assert 2.0 <= reward <= 3.0
```

### Integration Tests

```bash
#!/bin/bash
# tests/integration/test_full_flow.sh

# Start services
docker-compose up -d

# Wait for services
sleep 5

# Submit test task
TASK_ID=$(python examples/submit_task.py | grep "Task submitted" | cut -d: -f2 | tr -d ' ')

# Wait for completion
timeout 300 bash -c "while ! kiro status --task $TASK_ID | grep -q 'completed'; do sleep 5; done"

# Verify results
kiro status --task $TASK_ID
kiro scores --agent $(kiro status --task $TASK_ID | jq -r .assigned_agent)

# Cleanup
docker-compose down
```

## Best Practices

### 1. Agent Prompt Engineering

```yaml
# Best practices for agent prompts
system_prompt: |
  You are a {{tier}}-level agent specialized in {{specialization}}.
  
  Core Principles:
  1. Code Quality > Speed
  2. Test Everything
  3. Security First
  4. Follow Project Conventions
  
  Specific Guidelines:
  - Read existing code before making changes
  - Run tests before submitting
  - Check for security vulnerabilities
  - Document complex logic
  
  Constraints:
  - Max file size: 10KB
  - Max files changed: 20
  - Required test coverage: 80%
```

### 2. Reward Tuning

```python
# Iterative reward weight optimization
def optimize_weights(historical_data):
    """Find optimal weights based on outcome correlation"""
    
    from sklearn.linear_model import LinearRegression
    
    # Extract features and outcomes
    X = []  # Component scores
    y = []  # Human satisfaction scores
    
    for task in historical_data:
        X.append([
            task["components"]["test_coverage_delta"],
            task["components"]["lint_score"],
            # ... other components
        ])
        y.append(task["human_satisfaction_score"])
    
    # Fit model
    model = LinearRegression()
    model.fit(X, y)
    
    # Normalized weights
    weights = model.coef_ / model.coef_.sum()
    
    return {
        "test_coverage": weights[0],
        "lint_score": weights[1],
        # ... etc
    }
```

### 3. Security Hardening

```yaml
# Enhanced sandbox configuration
sandbox:
  engine: distrobox
  image: alpine:3.18
  
  capabilities:
    drop:
      - ALL
    add:
      - DAC_OVERRIDE  # File access
  
  seccomp:
    profile: strict
    
  rlimits:
    RLIMIT_CPU: 300      # 5 minutes CPU time
    RLIMIT_FSIZE: 10485760  # 10MB file size
    RLIMIT_NPROC: 50     # Max 50 processes
    
  mount:
    - type: bind
      source: $PROJECT_ROOT
      target: /workspace
      options: ["rw", "nosuid", "nodev"]
```

## Troubleshooting

### Common Issues

1. **Agent Selection Failures**
   ```bash
   # Check available agents
   kiro agents list
   
   # Verify agent specializations match task type
   kiro agents show <agent-name>
   ```

2. **Hook Execution Errors**
   ```bash
   # Test hook manually
   TASK_ID=test-001 AGENT_NAME=test .claude/hooks/TaskStart
   
   # Check hook logs
   kiro logs --hook TaskStart --tail
   ```

3. **Reward Calculation Issues**
   ```bash
   # Validate evaluator config
   python -m src.evaluator.rlvr_evaluate --validate
   
   # Test with sample data
   python -m src.evaluator.rlvr_evaluate --test
   ```

## Next Steps

1. **Extend Evaluator**: Add custom evaluation components for your domain
2. **Create Specialized Agents**: Build agents for specific frameworks or languages
3. **Integrate with CI/CD**: Connect to your existing development pipeline
4. **Scale Horizontally**: Deploy multiple coordinators with shared state
5. **Add Visualization**: Build dashboards for real-time monitoring

For more examples and advanced configurations, see the `/examples` directory.