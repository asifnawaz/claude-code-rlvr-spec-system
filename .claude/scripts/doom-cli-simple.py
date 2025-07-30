#!/usr/bin/env python3
"""
Simplified Doom CLI without external dependencies
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

CLAUDE_DIR = Path(__file__).parent.parent
AGENTS_DIR = CLAUDE_DIR / "agents"
SCOREBOARD_DIR = CLAUDE_DIR / "scoreboard"
TASKS_DIR = CLAUDE_DIR / "tasks"

def parse_simple_yaml(file_path):
    """Parse simple YAML without external dependencies"""
    data = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
    return data

def cmd_status(task_id=None):
    """Show task status"""
    if task_id:
        task_dir = TASKS_DIR / task_id
        if task_dir.exists():
            metadata_file = task_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                print(f"Task: {task_id}")
                print(f"Agent: {metadata.get('agent_name', 'unknown')}")
                print(f"Created: {metadata.get('timestamp', 'unknown')}")
        else:
            print(f"Task {task_id} not found")
    else:
        # Show recent tasks
        print("Recent tasks:")
        count = 0
        for task_dir in sorted(TASKS_DIR.iterdir(), reverse=True):
            if task_dir.is_dir() and count < 10:
                metadata_file = task_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    print(f"  {task_dir.name} - {metadata.get('agent_name', 'unknown')}")
                    count += 1

def cmd_agents():
    """List agents"""
    print("Available agents:")
    for agent_file in sorted(AGENTS_DIR.glob("agent-*.yml")):
        try:
            data = parse_simple_yaml(agent_file)
            print(f"  {agent_file.stem} - {data.get('tier', 'unknown')} tier")
        except:
            continue

def cmd_leaderboard():
    """Show leaderboard"""
    leaderboard_file = SCOREBOARD_DIR / "leaderboard.json"
    if leaderboard_file.exists():
        with open(leaderboard_file) as f:
            data = json.load(f)
        print("Agent Leaderboard:")
        for i, agent in enumerate(data.get('agents', [])[:10]):
            print(f"  {i+1}. {agent['name']} - Reward: {agent.get('rolling_avg_reward', 0):.2f}")
    else:
        print("No leaderboard data available")

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: doom-cli-simple.py [status|agents|leaderboard] [args...]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_status(task_id)
    elif command == "agents":
        cmd_agents()
    elif command == "leaderboard":
        cmd_leaderboard()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()