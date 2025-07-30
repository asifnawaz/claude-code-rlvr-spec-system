#!/usr/bin/env python3
"""
Bugfix Scenario Test
Simulates a complete bugfix task from submission to evaluation
"""

import json
import subprocess
import os
import sys
import time
from pathlib import Path
from datetime import datetime

class BugfixScenario:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.task_id = f"bugfix-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
    def run_scenario(self):
        """Execute complete bugfix scenario"""
        print("🐛 Running Bugfix Scenario Test\n")
        
        steps = [
            ("1. Submit bug report", self.submit_bug_report),
            ("2. Verify task creation", self.verify_task_creation),
            ("3. Simulate code changes", self.simulate_code_changes),
            ("4. Run evaluation", self.run_evaluation),
            ("5. Check results", self.check_results)
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}")
            print("-" * 40)
            
            success = step_func()
            if not success:
                print(f"❌ Failed at: {step_name}")
                return False
            
            time.sleep(0.5)  # Small delay between steps
        
        print("\n✅ Bugfix scenario completed successfully!")
        return True
    
    def submit_bug_report(self):
        """Submit a bug report through the system"""
        prompt = "Fix critical bug: Login fails with 'undefined is not a function' error when users click submit button"
        
        # Create task.yml
        task_data = {
            "type": "bugfix",
            "priority": "P0",
            "description": prompt,
            "tags": ["authentication", "critical", "user-facing"]
        }
        
        task_file = self.project_root / "task.yml"
        with open(task_file, 'w') as f:
            import yaml
            yaml.dump(task_data, f)
        
        print(f"📝 Created task.yml with bug report")
        print(f"   Type: {task_data['type']}")
        print(f"   Priority: {task_data['priority']}")
        
        return True
    
    def verify_task_creation(self):
        """Verify task was created and assigned"""
        # Simulate running manual-assign.py
        env = os.environ.copy()
        env['CLAUDE_PROJECT_DIR'] = str(self.project_root)
        env['DOOM_ENABLED'] = 'true'
        
        result = subprocess.run(
            ['python3', str(self.project_root / '.claude' / 'scripts' / 'manual-assign.py')],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(self.project_root)
        )
        
        if result.returncode != 0:
            print(f"❌ Task assignment failed: {result.stderr}")
            return False
        
        # Extract task ID from output
        for line in result.stdout.split('\n'):
            if line.startswith('export DOOM_TASK_ID='):
                self.task_id = line.split("'")[1]
                break
        
        print(f"✅ Task assigned: {self.task_id}")
        return True
    
    def simulate_code_changes(self):
        """Simulate code changes for the bugfix"""
        # Create a mock fix
        fix_content = """
// Fixed login bug
function handleLogin(event) {
    event.preventDefault();
    
    // Fix: Check if form data exists before processing
    const formData = event.target?.elements;
    if (!formData) {
        console.error('Form data not found');
        return;
    }
    
    const username = formData.username?.value || '';
    const password = formData.password?.value || '';
    
    // Rest of login logic...
    authenticateUser(username, password);
}

// Added unit test
describe('handleLogin', () => {
    it('should handle missing form data gracefully', () => {
        const mockEvent = { target: null, preventDefault: jest.fn() };
        expect(() => handleLogin(mockEvent)).not.toThrow();
    });
});
"""
        
        # Save to task directory
        task_dir = self.project_root / '.claude' / 'tasks' / self.task_id
        if task_dir.exists():
            with open(task_dir / 'fix.js', 'w') as f:
                f.write(fix_content)
            
            print("✅ Simulated code fix applied")
            print("   - Added null checks")
            print("   - Added unit test")
            return True
        else:
            print(f"❌ Task directory not found: {task_dir}")
            return False
    
    def run_evaluation(self):
        """Run RLVR evaluation"""
        env = os.environ.copy()
        env['CLAUDE_PROJECT_DIR'] = str(self.project_root)
        env['DOOM_TASK_ID'] = self.task_id
        env['DOOM_AGENT'] = 'agent-bugfix-senior'
        
        evaluator_path = self.project_root / '.claude' / 'scripts' / 'rlvr-evaluate.py'
        
        result = subprocess.run(
            [
                'python3', str(evaluator_path),
                '--task-id', self.task_id,
                '--agent-name', 'agent-bugfix-senior',
                '--task-status', 'completed',
                '--output-dir', str(self.project_root / '.claude' / 'scoreboard')
            ],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(self.project_root)
        )
        
        if result.returncode != 0:
            print(f"❌ Evaluation failed: {result.stderr}")
            return False
        
        print("✅ RLVR evaluation completed")
        return True
    
    def check_results(self):
        """Check evaluation results"""
        scoreboard_file = self.project_root / '.claude' / 'scoreboard' / 'rlvr.jsonl'
        
        if not scoreboard_file.exists():
            print("❌ Scoreboard file not found")
            return False
        
        # Find our evaluation
        with open(scoreboard_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get('task_id') == self.task_id:
                        reward = entry.get('reward', 0)
                        components = entry.get('components', {})
                        
                        print(f"📊 Evaluation Results:")
                        print(f"   Total Reward: {reward:.2f}")
                        print(f"   Components:")
                        for comp, score in components.items():
                            print(f"     - {comp}: {score:.2f}")
                        
                        # Check if reward is reasonable
                        if reward > 0:
                            print(f"\n✅ Positive reward indicates successful bugfix")
                            return True
                        else:
                            print(f"\n⚠️  Low reward: {reward:.2f}")
                            return False
                except:
                    continue
        
        print("❌ Evaluation not found in scoreboard")
        return False


def main():
    """Run the bugfix scenario test"""
    scenario = BugfixScenario()
    
    try:
        success = scenario.run_scenario()
        
        # Cleanup
        task_file = scenario.project_root / "task.yml"
        if task_file.exists():
            task_file.unlink()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ Scenario failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())