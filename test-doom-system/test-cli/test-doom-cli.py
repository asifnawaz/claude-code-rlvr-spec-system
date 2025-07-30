#!/usr/bin/env python3
"""
Test DOOM CLI commands
Verifies command-line interface functionality
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime

class DoomCLITester:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.cli_simple = self.project_root / '.claude' / 'scripts' / 'doom-cli-simple.py'
        self.env = os.environ.copy()
        self.env['CLAUDE_PROJECT_DIR'] = str(self.project_root)
    
    def run_command(self, args):
        """Run doom-cli-simple.py with given arguments"""
        cmd = ['python3', str(self.cli_simple)] + args
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=self.env,
            cwd=str(self.project_root)
        )
        
        return result
    
    def test_status_command(self):
        """Test the status command"""
        print("\n🔍 Testing 'status' command")
        
        result = self.run_command(['status'])
        
        if result.returncode == 0:
            print("✅ Status command executed successfully")
            
            # Check if output contains expected sections
            output = result.stdout
            if "Recent Tasks" in output or "No recent tasks" in output:
                print("   - Task list displayed correctly")
                return True
            else:
                print("❌ Unexpected output format")
                print(f"Output: {output[:200]}...")
                return False
        else:
            print(f"❌ Command failed: {result.stderr}")
            return False
    
    def test_agents_command(self):
        """Test the agents command"""
        print("\n👥 Testing 'agents' command")
        
        result = self.run_command(['agents'])
        
        if result.returncode == 0:
            print("✅ Agents command executed successfully")
            
            # Check for agent listings
            output = result.stdout
            expected_agents = [
                'agent-bugfix-junior',
                'agent-bugfix-senior',
                'agent-feature-junior',
                'agent-feature-senior'
            ]
            
            found_count = sum(1 for agent in expected_agents if agent in output)
            
            if found_count >= 2:  # At least some agents found
                print(f"   - Found {found_count} expected agents")
                return True
            else:
                print("❌ Agent list incomplete")
                return False
        else:
            print(f"❌ Command failed: {result.stderr}")
            return False
    
    def test_leaderboard_command(self):
        """Test the leaderboard command"""
        print("\n🏆 Testing 'leaderboard' command")
        
        # First, ensure we have some data
        self.create_sample_leaderboard()
        
        result = self.run_command(['leaderboard'])
        
        if result.returncode == 0:
            print("✅ Leaderboard command executed successfully")
            
            output = result.stdout
            if "Leaderboard" in output or "Agent Performance" in output:
                print("   - Leaderboard displayed")
                return True
            elif "No leaderboard data" in output:
                print("   - No data message shown (expected)")
                return True
            else:
                print("❌ Unexpected output")
                return False
        else:
            print(f"❌ Command failed: {result.stderr}")
            return False
    
    def test_invalid_command(self):
        """Test handling of invalid commands"""
        print("\n❓ Testing invalid command handling")
        
        result = self.run_command(['invalid-command'])
        
        if result.returncode != 0:
            print("✅ Invalid command rejected correctly")
            
            if "Usage:" in result.stdout or "Usage:" in result.stderr:
                print("   - Usage message displayed")
                return True
            else:
                print("⚠️  No usage message shown")
                return True  # Still acceptable
        else:
            print("❌ Invalid command accepted (should fail)")
            return False
    
    def test_status_with_task_id(self):
        """Test status command with specific task ID"""
        print("\n🔍 Testing 'status <task-id>' command")
        
        # Create a test task
        task_id = "test-task-123"
        self.create_test_task(task_id)
        
        result = self.run_command(['status', task_id])
        
        if result.returncode == 0:
            output = result.stdout
            if task_id in output:
                print(f"✅ Task {task_id} details displayed")
                return True
            else:
                print("❌ Task details not shown")
                return False
        else:
            # Task not found is also valid
            if "not found" in result.stdout.lower():
                print("✅ Task not found message displayed")
                return True
            else:
                print(f"❌ Unexpected error: {result.stderr}")
                return False
    
    def create_sample_leaderboard(self):
        """Create sample leaderboard data"""
        leaderboard_dir = self.project_root / '.claude' / 'scoreboard'
        leaderboard_dir.mkdir(parents=True, exist_ok=True)
        
        leaderboard_data = {
            "updated_at": datetime.utcnow().isoformat(),
            "agents": [
                {
                    "name": "agent-bugfix-senior",
                    "tier": "senior",
                    "rolling_avg_reward": 3.8,
                    "total_tasks": 25
                },
                {
                    "name": "agent-feature-senior",
                    "tier": "senior",
                    "rolling_avg_reward": 4.1,
                    "total_tasks": 18
                }
            ]
        }
        
        with open(leaderboard_dir / 'leaderboard.json', 'w') as f:
            json.dump(leaderboard_data, f)
    
    def create_test_task(self, task_id):
        """Create a test task"""
        tasks_dir = self.project_root / '.claude' / 'tasks'
        task_dir = tasks_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            'task_id': task_id,
            'agent_name': 'agent-bugfix-senior',
            'task_type': 'bugfix',
            'status': 'completed',
            'reward': 3.5,
            'created_at': datetime.utcnow().isoformat()
        }
        
        with open(task_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f)


def main():
    """Run all CLI tests"""
    print("🧪 Testing DOOM CLI Commands\n")
    
    tester = DoomCLITester()
    
    tests = [
        ("Status Command", tester.test_status_command),
        ("Agents Command", tester.test_agents_command),
        ("Leaderboard Command", tester.test_leaderboard_command),
        ("Invalid Command", tester.test_invalid_command),
        ("Status with Task ID", tester.test_status_with_task_id),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            failed += 1
    
    print(f"\n📊 CLI Test Results: {passed} passed, {failed} failed")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())