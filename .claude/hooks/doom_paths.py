#!/usr/bin/env python3
"""
Centralized path configuration for Doom-RLVR system.
This module provides consistent paths across all hooks and scripts.
"""

import os
import json
from pathlib import Path

def get_project_root():
    """Get the project root directory"""
    return Path(os.environ.get('CLAUDE_PROJECT_DIR', '.')).resolve()

def get_paths():
    """Get all Doom-RLVR paths"""
    project_root = get_project_root()
    
    # Try to load paths from config
    config_file = project_root / ".claude" / "config" / "paths.json"
    if config_file.exists():
        with open(config_file) as f:
            paths_config = json.load(f)
    else:
        # Fallback to default paths
        paths_config = {
            "agents_dir": ".claude/agents",
            "scripts_dir": ".claude/scripts",
            "config_dir": ".claude/config",
            "prompts_dir": ".claude/prompts",
            "tasks_dir": ".claude/tasks",
            "scoreboard_dir": ".claude/scoreboard",
            "feedback_dir": ".claude/feedback"
        }
    
    # Convert to absolute paths
    paths = {}
    for key, rel_path in paths_config.items():
        paths[key] = project_root / rel_path
        # Ensure data directories exist
        if key.endswith('_dir') and 'data/' in rel_path:
            paths[key].mkdir(parents=True, exist_ok=True)
    
    # Add Claude-specific paths
    paths['claude_dir'] = project_root / ".claude"
    paths['hooks_dir'] = paths['claude_dir'] / "hooks"
    paths['commands_dir'] = paths['claude_dir'] / "commands"
    
    return paths

# Convenience functions for commonly used paths
def get_agents_dir():
    return get_paths()['agents_dir']

def get_scripts_dir():
    return get_paths()['scripts_dir']

def get_scoreboard_dir():
    return get_paths()['scoreboard_dir']

def get_tasks_dir():
    return get_paths()['tasks_dir']

def get_feedback_dir():
    return get_paths()['feedback_dir']

def get_prompts_dir():
    return get_paths()['prompts_dir']

def get_config_dir():
    return get_paths()['config_dir']