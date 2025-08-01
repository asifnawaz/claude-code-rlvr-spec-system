#!/usr/bin/env python3
"""
PostToolUse Hook - Monitors tool usage and enforces policies
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Import path configuration
sys.path.insert(0, str(Path(__file__).parent))
from doom_paths import get_scoreboard_dir, get_tasks_dir

SCOREBOARD_DIR = get_scoreboard_dir()
TASKS_DIR = get_tasks_dir()

# Policy configuration
FORBIDDEN_COMMANDS = [
    "rm -rf /",
    "curl evil.com",
    "eval",
    "sudo rm",
    "dd if=/dev/zero",
    ":(){ :|:& };:"  # Fork bomb
]

SENSITIVE_PATTERNS = [
    "password=",
    "api_key=",
    "secret=",
    "token=",
    "private_key"
]

def check_command_safety(command):
    """Check if a command is safe to execute"""
    for forbidden in FORBIDDEN_COMMANDS:
        if forbidden in command:
            return False, f"Forbidden command pattern: {forbidden}"
    
    for pattern in SENSITIVE_PATTERNS:
        if pattern.lower() in command.lower():
            return False, f"Potential sensitive data exposure: {pattern}"
    
    return True, None

def record_tool_usage(tool_data):
    """Record tool usage metrics"""
    task_id = os.environ.get('DOOM_TASK_ID', 'unknown')
    agent_name = os.environ.get('DOOM_AGENT_NAME', 'unknown')
    
    # Create metrics entry
    metrics = {
        'timestamp': datetime.utcnow().isoformat(),
        'task_id': task_id,
        'agent_name': agent_name,
        'tool_name': tool_data.get('tool_name', 'unknown'),
        'tool_status': tool_data.get('status', 'unknown'),
        'duration_ms': tool_data.get('duration_ms', 0),
        'metadata': tool_data.get('metadata', {})
    }
    
    # Save to task-specific metrics
    task_dir = TASKS_DIR / task_id
    if task_dir.exists():
        metrics_file = task_dir / "tool_metrics.jsonl"
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
    
    # Update global metrics
    global_metrics_file = SCOREBOARD_DIR / "tool_usage.jsonl"
    with open(global_metrics_file, 'a') as f:
        f.write(json.dumps(metrics) + '\n')

def enforce_resource_limits(tool_data):
    """Check if resource limits are being respected"""
    tool_name = tool_data.get('tool_name', '')
    
    # Check token usage for LLM tools
    if tool_name in ['Generate', 'Edit', 'Refactor']:
        tokens_used = tool_data.get('metadata', {}).get('tokens_used', 0)
        max_tokens = int(os.environ.get('DOOM_MAX_TOKENS', '100000'))
        
        if tokens_used > max_tokens:
            return False, f"Token limit exceeded: {tokens_used} > {max_tokens}"
    
    # Check file size limits
    if tool_name in ['Write', 'Create']:
        file_size = tool_data.get('metadata', {}).get('file_size', 0)
        max_file_size = 10 * 1024 * 1024  # 10MB
        
        if file_size > max_file_size:
            return False, f"File size limit exceeded: {file_size} bytes"
    
    return True, None

def main():
    """Main hook entry point"""
    # Read tool data from stdin
    try:
        tool_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # No tool data provided
        return
    
    tool_name = tool_data.get('tool_name', 'unknown')
    
    # Special handling for Bash/Shell commands
    if tool_name in ['Bash', 'Shell', 'Execute']:
        command = tool_data.get('metadata', {}).get('command', '')
        safe, reason = check_command_safety(command)
        
        if not safe:
            print(f"ERROR: Command blocked - {reason}", file=sys.stderr)
            sys.exit(1)
    
    # Check resource limits
    within_limits, reason = enforce_resource_limits(tool_data)
    if not within_limits:
        print(f"ERROR: Resource limit exceeded - {reason}", file=sys.stderr)
        sys.exit(1)
    
    # Record metrics
    record_tool_usage(tool_data)
    
    # Warnings for certain patterns
    if tool_name == 'Delete' and tool_data.get('metadata', {}).get('path', '').endswith('.test.js'):
        print("WARNING: Deleting test files - this may reduce code coverage")
    
    if tool_name == 'Edit' and tool_data.get('status') == 'failed':
        print(f"WARNING: Edit tool failed - agent may need to re-read the file")
    
    # Success case - tool usage is allowed
    task_id = os.environ.get('DOOM_TASK_ID', 'unknown')
    print(f"Tool {tool_name} executed successfully for task {task_id}")

if __name__ == "__main__":
    main()