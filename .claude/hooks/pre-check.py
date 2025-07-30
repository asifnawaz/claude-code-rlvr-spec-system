#!/usr/bin/env python3
"""
Pre-Check Hook - Optional safeguard to validate tool calls before execution
Implements security checks and compliance validation
"""

import sys
import json
import os
import re
from pathlib import Path

# Read hook data from stdin
try:
    hook_data = json.load(sys.stdin)
except:
    sys.exit(0)

# Extract tool information
tool_name = hook_data.get('tool', '')
tool_args = hook_data.get('args', {})

# Get project and task context
project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '.')
task_id = os.environ.get('KIRO_TASK_ID', '')
agent_name = os.environ.get('KIRO_AGENT', '')

class ToolValidator:
    """Validates tool calls based on security and compliance rules"""
    
    def __init__(self):
        self.blocked_patterns = {
            'Bash': [
                r'rm\s+-rf\s+/',  # Dangerous recursive deletion
                r'curl.*\|\s*sh',  # Curl piped to shell
                r'wget.*\|\s*bash',  # Wget piped to bash
                r'eval\s*\(',  # Eval usage
                r'exec\s*\(',  # Exec usage
                r'>\s*/dev/sd[a-z]',  # Writing to raw devices
                r'dd\s+if=.*of=/dev/',  # DD to devices
                r'chmod\s+777',  # World-writable permissions
                r'.*password.*=',  # Password in command
                r'.*api[_-]?key.*=',  # API key in command
            ],
            'Write': [
                r'\.env$',  # Direct .env file writes
                r'\.git/config$',  # Git config modification
                r'/etc/',  # System config files
                r'~/.ssh/',  # SSH directory
            ],
            'WebFetch': [
                r'https?://localhost',  # Localhost access
                r'https?://127\.0\.0\.1',  # Loopback access
                r'https?://192\.168\.',  # Private network
                r'https?://10\.',  # Private network
                r'file://',  # File protocol
            ]
        }
        
        self.sensitive_paths = [
            '.env',
            '.git/config',
            'secrets/',
            'credentials/',
            '.ssh/',
            'private/',
        ]
        
        self.allowed_domains = [
            'github.com',
            'githubusercontent.com',
            'npmjs.org',
            'pypi.org',
            'docs.python.org',
            'developer.mozilla.org',
            'stackoverflow.com',
        ]
    
    def validate(self, tool_name: str, args: dict) -> tuple[bool, str]:
        """
        Validate a tool call
        Returns: (is_allowed, reason)
        """
        
        # Check agent permissions first
        if not self._check_agent_permissions(tool_name):
            return False, f"Agent {agent_name} not allowed to use {tool_name}"
        
        # Tool-specific validation
        if tool_name == 'Bash':
            return self._validate_bash(args)
        elif tool_name == 'Write':
            return self._validate_write(args)
        elif tool_name == 'Edit':
            return self._validate_edit(args)
        elif tool_name == 'WebFetch':
            return self._validate_webfetch(args)
        elif tool_name == 'WebSearch':
            return self._validate_websearch(args)
        
        # Default allow for other tools
        return True, "Allowed"
    
    def _check_agent_permissions(self, tool_name: str) -> bool:
        """Check if current agent is allowed to use this tool"""
        if not agent_name:
            return True  # No agent context, allow
        
        # Load agent configuration
        agent_file = Path(project_dir) / '.claude' / 'agents' / f'{agent_name}.md'
        if not agent_file.exists():
            return True  # Agent not found, allow by default
        
        # Parse allowed tools from front-matter
        allowed_tools = []
        in_frontmatter = False
        in_tools = False
        
        with open(agent_file) as f:
            for line in f:
                line = line.strip()
                if line == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        break
                
                if in_frontmatter:
                    if line == 'tools_allowed:':
                        in_tools = True
                    elif in_tools and line.startswith('  - '):
                        allowed_tools.append(line[4:].strip())
                    elif not line.startswith('  '):
                        in_tools = False
        
        # Check if tool is in allowed list
        return tool_name in allowed_tools or not allowed_tools
    
    def _validate_bash(self, args: dict) -> tuple[bool, str]:
        """Validate Bash command"""
        command = args.get('command', '')
        
        # Check blocked patterns
        for pattern in self.blocked_patterns['Bash']:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Blocked pattern detected: {pattern}"
        
        # Check for sensitive file access
        for path in self.sensitive_paths:
            if path in command:
                return False, f"Access to sensitive path blocked: {path}"
        
        # Lint check (basic)
        if 'set -euo pipefail' not in command and len(command) > 50:
            # Suggest safer execution
            print(f"Warning: Consider adding 'set -euo pipefail' for safer execution", file=sys.stderr)
        
        return True, "Bash command allowed"
    
    def _validate_write(self, args: dict) -> tuple[bool, str]:
        """Validate Write operation"""
        file_path = args.get('file_path', '')
        
        # Check blocked patterns
        for pattern in self.blocked_patterns['Write']:
            if re.search(pattern, file_path):
                return False, f"Write to blocked path: {pattern}"
        
        # Check sensitive paths
        for path in self.sensitive_paths:
            if path in file_path:
                return False, f"Write to sensitive path blocked: {path}"
        
        # Check file size (prevent huge writes)
        content = args.get('content', '')
        if len(content) > 1_000_000:  # 1MB limit
            return False, "File content too large (>1MB)"
        
        return True, "Write allowed"
    
    def _validate_edit(self, args: dict) -> tuple[bool, str]:
        """Validate Edit operation"""
        # Similar to Write validation
        return self._validate_write(args)
    
    def _validate_webfetch(self, args: dict) -> tuple[bool, str]:
        """Validate WebFetch operation"""
        url = args.get('url', '')
        
        # Check blocked patterns
        for pattern in self.blocked_patterns['WebFetch']:
            if re.match(pattern, url):
                return False, f"Blocked URL pattern: {pattern}"
        
        # Extract domain
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check if domain is in allowed list (optional strict mode)
        # For now, just block obviously bad domains
        blocked_domains = ['malware.com', 'phishing.net']  # Example
        if any(bad in domain for bad in blocked_domains):
            return False, f"Blocked domain: {domain}"
        
        return True, "WebFetch allowed"
    
    def _validate_websearch(self, args: dict) -> tuple[bool, str]:
        """Validate WebSearch operation"""
        query = args.get('query', '')
        
        # Check for sensitive information in search
        sensitive_patterns = [
            r'password\s*[:=]',
            r'api[_-]?key\s*[:=]',
            r'secret\s*[:=]',
            r'token\s*[:=]',
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False, f"Sensitive information in search query"
        
        return True, "WebSearch allowed"

# Main execution
validator = ToolValidator()
is_allowed, reason = validator.validate(tool_name, tool_args)

if not is_allowed:
    # Block the tool execution
    error_response = {
        "error": f"Tool call blocked by pre-check: {reason}",
        "tool": tool_name,
        "suggestion": "Please modify your request to comply with security policies"
    }
    
    # Log the blocked attempt
    log_entry = {
        "timestamp": json.dumps({"timestamp": "now"}),  # Placeholder
        "event": "tool_blocked",
        "tool": tool_name,
        "reason": reason,
        "task_id": task_id,
        "agent": agent_name
    }
    
    log_file = Path(project_dir) / '.claude' / 'scoreboard' / 'security.jsonl'
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except:
        pass
    
    # Output error and exit with non-zero to block execution
    print(json.dumps(error_response))
    sys.exit(1)

# Tool is allowed, exit normally
sys.exit(0)