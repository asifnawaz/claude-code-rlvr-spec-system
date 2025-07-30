#!/usr/bin/env python3
"""
Test the Stop hook externally
Simulates task completion and evaluation
"""

import json
import subprocess
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

def setup_test_task(task_id, agent_name, task_type="bugfix"):
    """Create a test task structure"""
    project_root = Path(__file__).parent.parent.parent
    tasks_dir = project_root / '.claude' / 'tasks'
    task_dir = tasks_dir / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    
    # Create task metadata
    metadata = {
        'task_id': task_id,
        'agent_name': agent_name,
        'task_type': task_type,
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'in_progress',
        'optimized_prompt': """$GOAL: Fix login bug
$CONTEXT: Users cannot login
$CONSTRAINTS: Must not break existing auth
$OUTPUT_FORMAT: Fixed code
$STYLE: Clean code
$EXAMPLES: N/A
$ACCEPTANCE_CRITERIA:
- [x] Login works
- [x] Tests pass
- [ ] Documentation updated"""
    }
    
    with open(task_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return task_dir


def test_stop_hook(task_id, agent_name):
    """Test the Stop hook"""
    
    # Set up environment
    project_root = Path(__file__).parent.parent.parent
    env = os.environ.copy()
    env['CLAUDE_PROJECT_DIR'] = str(project_root)
    env['DOOM_ENABLED'] = 'true'
    env['DOOM_TASK_ID'] = task_id
    env['DOOM_AGENT'] = agent_name
    
    # Hook input data
    hook_data = {
        "event": "stop",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Run the hook
    hook_path = project_root / '.claude' / 'hooks' / 'stop.py'
    
    try:
        result = subprocess.run(
            ['python3', str(hook_path)],
            input=json.dumps(hook_data),
            capture_output=True,
            text=True,
            env=env,
            cwd=str(project_root),
            timeout=30
        )
        
        # Check if evaluation was created
        scoreboard_file = project_root / '.claude' / 'scoreboard' / 'rlvr.jsonl'
        evaluation_found = False
        reward = None
        
        if scoreboard_file.exists():
            with open(scoreboard_file) as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get('task_id') == task_id:
                            evaluation_found = True
                            reward = entry.get('reward', 0)
                            break
                    except:
                        pass
        
        return {
            "success": result.returncode == 0,
            "evaluation_found": evaluation_found,
            "reward": reward,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Hook timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """Run stop hook tests"""
    print("🧪 Testing Stop Hook (Evaluation)\n")
    
    # Test scenarios
    test_cases = [
        {
            "task_id": "test-task-001",
            "agent_name": "agent-bugfix-senior",
            "task_type": "bugfix",
            "description": "Senior agent bug fix"
        },
        {
            "task_id": "test-task-002",
            "agent_name": "agent-feature-junior",
            "task_type": "feature",
            "description": "Junior agent feature"
        },
        {
            "task_id": "test-task-003",
            "agent_name": "agent-refactor-principal",
            "task_type": "refactor",
            "description": "Principal agent refactor"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"Test: {test['description']}")
        
        # Setup test task
        task_dir = setup_test_task(
            test['task_id'],
            test['agent_name'],
            test['task_type']
        )
        
        # Run stop hook
        result = test_stop_hook(test['task_id'], test['agent_name'])
        
        if result['success'] and result['evaluation_found']:
            print(f"✅ Passed - Reward: {result['reward']:.2f}")
            passed += 1
        else:
            print(f"❌ Failed - {result.get('error', 'No evaluation found')}")
            if result.get('error'):
                print(f"   Error: {result['error']}")
            failed += 1
        
        # Cleanup
        try:
            shutil.rmtree(task_dir)
        except:
            pass
        
        print()
    
    print(f"\n📊 Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())