#!/usr/bin/env python3
"""
Stop Hook - Evaluates task completion and provides feedback for improvement
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Read hook data from stdin
try:
    hook_data = json.load(sys.stdin)
except:
    hook_data = {}

project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '.')

# Import path configuration
sys.path.insert(0, str(Path(__file__).parent))
from doom_paths import get_paths, get_scripts_dir, get_scoreboard_dir, get_tasks_dir, get_feedback_dir

# Get configured paths
paths = get_paths()
SCRIPTS_DIR = get_scripts_dir()
SCOREBOARD_DIR = get_scoreboard_dir()
TASKS_DIR = get_tasks_dir()
FEEDBACK_DIR = get_feedback_dir()

# Import the evaluator directly from kebab-case file
sys.path.insert(0, str(paths['claude_dir'] / "scripts"))
import importlib.util
spec = importlib.util.spec_from_file_location("rlvr_evaluate", 
                                              paths['claude_dir'] / "scripts" / "rlvr-evaluate.py")
rlvr_evaluate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rlvr_evaluate)
RLVREvaluator = rlvr_evaluate.RLVREvaluator

# Find the most recent task
def get_current_task():
    """Find the most recent task based on metadata files"""
    latest_task = None
    latest_time = None
    
    if TASKS_DIR.exists():
        for task_dir in TASKS_DIR.iterdir():
            if task_dir.is_dir():
                metadata_file = task_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                        task_time = datetime.fromisoformat(metadata['timestamp'])
                        if latest_time is None or task_time > latest_time:
                            latest_time = task_time
                            latest_task = metadata
                    except:
                        continue
    
    return latest_task

# Get current task
current_task = get_current_task()
if not current_task:
    sys.exit(0)

task_id = current_task['task_id']
agent_name = current_task['agent_name']

def get_task_status():
    """Determine task completion status"""
    # Simple heuristic - if we got here, task completed
    return 'completed'

def trigger_evaluation():
    """Run RLVR evaluation"""
    task_status = get_task_status()
    
    # Run evaluator
    evaluator = RLVREvaluator()
    result = evaluator.evaluate(task_id, agent_name, task_status)
    
    # Save evaluation result
    eval_file = SCOREBOARD_DIR / "rlvr.jsonl"
    with open(eval_file, 'a') as f:
        f.write(json.dumps(result) + '\n')
    
    # Update task metadata
    task_dir = TASKS_DIR / task_id
    if task_dir.exists():
        metadata_file = task_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            metadata['completed_at'] = datetime.utcnow().isoformat()
            metadata['status'] = task_status
            metadata['reward'] = result['reward']
            metadata['evaluation'] = result
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
    
    return result

def generate_feedback(evaluation, task_metadata):
    """Generate improvement feedback based on evaluation"""
    reward = evaluation['reward']
    components = evaluation['components']
    
    feedback = {
        'task_id': task_metadata['task_id'],
        'agent': task_metadata['agent_name'],
        'reward': reward,
        'timestamp': datetime.utcnow().isoformat(),
        'improvements': []
    }
    
    # Analyze each component and suggest improvements
    if components.get('test_coverage_delta', 0) < 0:
        feedback['improvements'].append({
            'area': 'test_coverage',
            'issue': 'Test coverage decreased',
            'suggestion': 'Always add tests for new code and never remove existing tests'
        })
    
    if components.get('lint_score', 1) < 0.8:
        feedback['improvements'].append({
            'area': 'code_quality',
            'issue': 'Lint errors detected',
            'suggestion': 'Run linter before completing tasks and fix all warnings'
        })
    
    if components.get('security_scan_score', 1) < 1.0:
        feedback['improvements'].append({
            'area': 'security',
            'issue': 'Security vulnerabilities found',
            'suggestion': 'Review security best practices and scan for vulnerabilities'
        })
    
    if components.get('code_complexity_delta', 0) > 0.1:
        feedback['improvements'].append({
            'area': 'complexity',
            'issue': 'Code complexity increased significantly',
            'suggestion': 'Refactor complex code into smaller, more manageable functions'
        })
    
    # Store feedback for future learning
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    feedback_file = FEEDBACK_DIR / f"{task_metadata['task_type']}_feedback.jsonl"
    with open(feedback_file, 'a') as f:
        f.write(json.dumps(feedback) + '\n')
    
    return feedback

def update_agent_performance(agent_name, reward):
    """Update agent's rolling performance metrics"""
    agent_file = paths['agents_dir'] / f"{agent_name}.yml"
    if not agent_file.exists():
        return
    
    # Simple update - just append to performance log
    perf_file = SCOREBOARD_DIR / f"{agent_name}_performance.jsonl"
    perf_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'reward': reward,
        'task_id': task_id
    }
    with open(perf_file, 'a') as f:
        f.write(json.dumps(perf_entry) + '\n')

def update_prompt_optimization_data(task_metadata, reward):
    """Store data about prompt optimization effectiveness"""
    if task_metadata.get('optimized'):
        opt_data = {
            'task_type': task_metadata['task_type'],
            'priority': task_metadata['priority'],
            'reward': reward,
            'optimized': True,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        opt_file = SCOREBOARD_DIR / "optimization_effectiveness.jsonl"
        with open(opt_file, 'a') as f:
            f.write(json.dumps(opt_data) + '\n')

# Main execution
try:
    # Run evaluation
    evaluation = trigger_evaluation()
    reward = evaluation['reward']
    
    # Update agent performance
    update_agent_performance(agent_name, reward)
    
    # Generate feedback for continuous improvement
    feedback = generate_feedback(evaluation, current_task)
    
    # Track optimization effectiveness
    update_prompt_optimization_data(current_task, reward)
    
    # Log completion
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event': 'task_completed',
        'task_id': task_id,
        'agent_name': agent_name,
        'reward': reward,
        'feedback_generated': len(feedback['improvements']) > 0
    }
    
    with open(SCOREBOARD_DIR / "events.jsonl", 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    # Print summary (visible in Claude Code output)
    print(f"\n{'='*60}")
    print(f"Task Evaluation Complete")
    print(f"Task ID: {task_id}")
    print(f"Agent: {agent_name}")
    print(f"Reward: {reward:.2f}")
    
    if feedback['improvements']:
        print(f"\nAreas for Improvement:")
        for imp in feedback['improvements']:
            print(f"- {imp['area']}: {imp['suggestion']}")
    else:
        print(f"\nExcellent work! No major improvements needed.")
    
    print(f"{'='*60}\n")
    
except Exception as e:
    # Log error but don't fail
    error_log = SCOREBOARD_DIR / "errors.log"
    with open(error_log, 'a') as f:
        f.write(f"{datetime.utcnow().isoformat()} - Stop hook error: {e}\n")