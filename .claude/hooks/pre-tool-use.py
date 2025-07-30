#!/usr/bin/env python3
"""
PreToolUse Hook - Runs before tool execution
Validates tool usage and applies agent-specific constraints
"""

import os
import sys
import json
from pathlib import Path

# Read hook data from stdin
try:
    hook_data = json.load(sys.stdin)
except:
    # If no JSON data, exit silently
    sys.exit(0)

# Extract relevant information
tool_name = hook_data.get('tool', {}).get('name', '')
tool_params = hook_data.get('tool', {}).get('params', {})
session_id = hook_data.get('sessionId', '')
project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '.')

# Get current agent context
agent_name = os.environ.get('DOOM_AGENT_NAME', '')
agent_tier = os.environ.get('DOOM_AGENT_TIER', '')
task_id = os.environ.get('DOOM_TASK_ID', '')

# Load agent constraints if available
agent_file = Path(project_dir) / '.claude' / 'agents' / f'{agent_name}.yml'
if agent_file.exists() and agent_name:
    try:
        # Parse YAML manually without external dependency
        with open(agent_file) as f:
            content = f.read()
            # Simple YAML parsing for tools_allowed list
            agent_data = {}
            if 'tools_allowed:' in content:
                tools_section = content.split('tools_allowed:')[1].split('\n')
                tools_allowed = []
                for line in tools_section:
                    line = line.strip()
                    if line.startswith('- '):
                        tools_allowed.append(line[2:].strip())
                    elif line and not line.startswith(' '):
                        break
                agent_data['tools_allowed'] = tools_allowed
        
        # Check tool allowlist
        tools_allowed = agent_data.get('tools_allowed', [])
        if tools_allowed and tool_name not in tools_allowed:
            # Block tool usage
            response = {
                "decision": "block",
                "reason": f"Tool '{tool_name}' not allowed for {agent_tier} agent {agent_name}. Allowed tools: {', '.join(tools_allowed)}",
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Agent {agent_name} is restricted to: {', '.join(tools_allowed)}"
            }
            print(json.dumps(response))
            sys.exit(0)
    except Exception as e:
        # Log error but continue
        pass

# Apply resource limits - check file change tracking
if tool_name in ['Edit', 'MultiEdit', 'Write']:
    try:
        # Use data directory instead of .claude for consistency
        tracker_file = Path(project_dir) / 'data' / 'tasks' / task_id / 'files_changed.txt'
        if tracker_file.exists():
            with open(tracker_file) as f:
                files_changed = len(f.read().strip().split('\n'))
            
            # Default limit for agents
            max_files = 100
            if agent_tier == 'junior':
                max_files = 10
            elif agent_tier == 'senior':
                max_files = 50
            
            if files_changed >= max_files:
                response = {
                    "decision": "block",
                    "reason": f"File change limit reached ({max_files} files). This is a {agent_tier} agent constraint.",
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Resource limit: {agent_tier} agents limited to {max_files} file changes"
                }
                print(json.dumps(response))
                sys.exit(0)
    except Exception:
        # Continue if tracking fails
        pass

# Security checks for Bash/Shell commands
if tool_name == 'Bash':
    command = tool_params.get('command', '')
    
    # Comprehensive forbidden patterns
    forbidden_patterns = [
        "rm -rf /",
        "rm -rf /*",
        "sudo",
        "chmod 777 /",
        "eval",
        "exec",
        "> /dev/sda",
        "mkfs",
        "dd if=/dev/zero of=/",
        ":(){ :|:& };:",  # Fork bomb
    ]
    
    # Check for suspicious URLs
    suspicious_domains = ["evil", "malware", "hack", "exploit"]
    
    for forbidden in forbidden_patterns:
        if forbidden in command:
            response = {
                "decision": "block",
                "reason": f"Security: Command contains forbidden pattern '{forbidden}'",
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Security policy violation: dangerous command pattern detected"
            }
            print(json.dumps(response))
            sys.exit(0)
    
    # Check for suspicious network activity
    if any(domain in command.lower() for domain in suspicious_domains):
        response = {
            "decision": "block",
            "reason": "Security: Suspicious network activity detected",
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Security policy: suspicious domain access attempted"
        }
        print(json.dumps(response))
        sys.exit(0)

# Log tool usage for metrics
try:
    # Use data directory for consistency
    log_dir = Path(project_dir) / 'data' / 'scoreboard'
    if log_dir.exists():
        log_entry = {
            "timestamp": hook_data.get('timestamp', ''),
            "event": "pre_tool_use",
            "tool": tool_name,
            "agent": agent_name,
            "task_id": task_id,
            "session_id": session_id,
            "approved": True
        }
        
        with open(log_dir / 'tool_usage.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
except Exception:
    # Don't fail hook if logging fails
    pass

# Approve tool usage by default
response = {
    "decision": "approve",
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow"
}
print(json.dumps(response))