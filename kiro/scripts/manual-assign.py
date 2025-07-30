#!/usr/bin/env python3
"""
Manual task assignment script for Kiro-RLVR
Allows overriding automatic agent selection
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime

def manual_assign():
    """Manually assign task to specific agent"""
    
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '.')
    CLAUDE_DIR = Path(project_dir) / ".claude"
    AGENTS_DIR = CLAUDE_DIR / "agents"
    TASKS_DIR = CLAUDE_DIR / "tasks"
    SCOREBOARD_DIR = CLAUDE_DIR / "scoreboard"
    
    # Check for task.yml
    task_file = Path(project_dir) / "task.yml"
    if not task_file.exists():
        print("Error: task.yml not found", file=sys.stderr)
        sys.exit(1)
    
    with open(task_file) as f:
        task_data = yaml.safe_load(f)
    
    # Get manual assignment parameters
    agent_name = os.environ.get('KIRO_MANUAL_AGENT', '')
    force = os.environ.get('KIRO_FORCE_ASSIGNMENT', 'false').lower() == 'true'
    
    if agent_name:
        # Verify agent exists
        agent_file = AGENTS_DIR / f"{agent_name}.yml"
        if not agent_file.exists():
            # Try with agent- prefix
            agent_file = AGENTS_DIR / f"agent-{agent_name}.yml"
            agent_name = f"agent-{agent_name}"
        
        if not agent_file.exists():
            print(f"Error: Agent {agent_name} not found", file=sys.stderr)
            print("\nAvailable agents:")
            for f in sorted(AGENTS_DIR.glob("agent-*.yml")):
                print(f"  - {f.stem}")
            sys.exit(1)
        
        with open(agent_file) as f:
            agent_data = yaml.safe_load(f)
        
        # Check if agent is suitable
        task_type = task_data.get('type', 'general')
        if not force and task_type not in agent_data.get('specializations', []):
            print(f"Warning: Agent {agent_name} does not specialize in {task_type} tasks", file=sys.stderr)
            print(f"Agent specializations: {', '.join(agent_data.get('specializations', []))}")
            print("Use --force to assign anyway")
            sys.exit(1)
        
        if agent_data.get('tier') == 'suspended' and not force:
            print(f"Error: Agent {agent_name} is suspended", file=sys.stderr)
            print("Use --force to assign anyway")
            sys.exit(1)
    else:
        # Auto-select agent
        from .kiro_cli import load_agents, select_best_agent
        agents = []
        for agent_file in AGENTS_DIR.glob("agent-*.yml"):
            with open(agent_file) as f:
                agents.append(yaml.safe_load(f))
        
        if not agents:
            print("Error: No agents available", file=sys.stderr)
            sys.exit(1)
        
        task_type = task_data.get('type', 'general')
        
        # Filter and sort agents
        candidates = [a for a in agents if task_type in a.get('specializations', [])]
        if not candidates:
            candidates = agents
        
        tier_priority = {'principal': 3, 'senior': 2, 'junior': 1}
        candidates.sort(
            key=lambda a: (
                tier_priority.get(a.get('tier', 'junior'), 1),
                a.get('performance', {}).get('rolling_avg_reward', 0)
            ),
            reverse=True
        )
        
        agent_data = candidates[0]
        agent_name = agent_data['name']
    
    # Create task assignment
    task_id = f"{task_data.get('type', 'task')}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    task_dir = TASKS_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    
    # Create context
    context = f"""[Kiro-RLVR Task Assignment]

Task ID: {task_id}
Assigned Agent: {agent_name} ({agent_data['tier']} tier)
Assignment Method: {'Manual (forced)' if force else 'Manual' if os.environ.get('KIRO_MANUAL_AGENT') else 'Automatic'}

{agent_data.get('system_prompt', '')}

Task Type: {task_data.get('type', 'general')}
Priority: {task_data.get('priority', 'P2')}

Description:
{task_data.get('description', 'No description provided')}

Constraints:
- Max tokens: {task_data.get('constraints', {}).get('max_tokens', 100000)}
- Timeout: {task_data.get('constraints', {}).get('timeout_ms', 300000)}ms
"""
    
    # Save context
    with open(task_dir / "context.md", 'w') as f:
        f.write(context)
    
    # Save metadata
    metadata = {
        'task_id': task_id,
        'task_type': task_data.get('type', 'general'),
        'agent_name': agent_name,
        'agent_tier': agent_data['tier'],
        'created_at': datetime.utcnow().isoformat(),
        'status': 'assigned',
        'assignment_method': 'manual' if os.environ.get('KIRO_MANUAL_AGENT') else 'automatic',
        'forced': force
    }
    
    with open(task_dir / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Log assignment
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event': 'task_assigned',
        'task_id': task_id,
        'task_type': task_data.get('type', 'general'),
        'agent_name': agent_name,
        'agent_tier': agent_data['tier'],
        'method': 'manual' if os.environ.get('KIRO_MANUAL_AGENT') else 'automatic'
    }
    
    with open(SCOREBOARD_DIR / "events.jsonl", 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    # Set environment for hooks
    print(f"export KIRO_TASK_ID='{task_id}'")
    print(f"export KIRO_AGENT_NAME='{agent_name}'")
    print(f"export KIRO_AGENT_TIER='{agent_data['tier']}'")
    print(f"export KIRO_CONTEXT_FILE='{task_dir / 'context.md'}'")
    
    print(f"\nTask {task_id} assigned to {agent_name} ({agent_data['tier']} tier)")
    print(f"Context saved to: {task_dir / 'context.md'}")

if __name__ == "__main__":
    manual_assign()