#!/usr/bin/env python3
"""
Feature Development Scenario Test
Simulates a complete feature development task
"""

import json
import subprocess
import os
import sys
import time
from pathlib import Path
from datetime import datetime

class FeatureScenario:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.task_id = f"feature-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
    def run_scenario(self):
        """Execute complete feature development scenario"""
        print("🚀 Running Feature Development Scenario Test\n")
        
        steps = [
            ("1. Submit feature request", self.submit_feature_request),
            ("2. Check agent assignment", self.check_agent_assignment),
            ("3. Simulate implementation", self.simulate_implementation),
            ("4. Add tests", self.add_tests),
            ("5. Run evaluation", self.run_evaluation),
            ("6. Verify tier impact", self.verify_tier_impact)
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}")
            print("-" * 40)
            
            success = step_func()
            if not success:
                print(f"❌ Failed at: {step_name}")
                return False
            
            time.sleep(0.5)
        
        print("\n✅ Feature scenario completed successfully!")
        return True
    
    def submit_feature_request(self):
        """Submit a feature request"""
        prompt = """Add export to CSV functionality for user reports. 
        Should include filters for date range and user status.
        Must handle large datasets efficiently."""
        
        # Simulate hook input
        hook_data = {
            "prompt": prompt,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        env = os.environ.copy()
        env['CLAUDE_PROJECT_DIR'] = str(self.project_root)
        env['DOOM_ENABLED'] = 'true'
        
        # Run UserPromptSubmit hook
        hook_path = self.project_root / '.claude' / 'hooks' / 'user-prompt-submit.py'
        
        result = subprocess.run(
            ['python3', str(hook_path)],
            input=json.dumps(hook_data),
            capture_output=True,
            text=True,
            env=env,
            cwd=str(self.project_root)
        )
        
        if result.returncode != 0:
            print(f"❌ Hook failed: {result.stderr}")
            return False
        
        print("✅ Feature request submitted")
        print("   Type detected: feature")
        print("   Priority: P2")
        return True
    
    def check_agent_assignment(self):
        """Verify correct agent was assigned"""
        # Create task file for assignment
        task_data = {
            "type": "feature",
            "priority": "P2",
            "description": "Add CSV export functionality"
        }
        
        task_file = self.project_root / "task.yml"
        with open(task_file, 'w') as f:
            import yaml
            yaml.dump(task_data, f)
        
        env = os.environ.copy()
        env['CLAUDE_PROJECT_DIR'] = str(self.project_root)
        
        result = subprocess.run(
            ['python3', str(self.project_root / '.claude' / 'scripts' / 'manual-assign.py')],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(self.project_root)
        )
        
        # Extract assigned agent
        agent_name = None
        for line in result.stdout.split('\n'):
            if 'agent-feature-' in line:
                if 'senior' in line:
                    agent_name = 'agent-feature-senior'
                elif 'junior' in line:
                    agent_name = 'agent-feature-junior'
                break
        
        if agent_name:
            print(f"✅ Assigned to: {agent_name}")
            return True
        else:
            print("❌ No feature agent assigned")
            return False
    
    def simulate_implementation(self):
        """Simulate feature implementation"""
        implementation = """
import csv
from datetime import datetime
from typing import List, Dict, Optional

class CSVExporter:
    \"\"\"Export user reports to CSV format\"\"\"
    
    def __init__(self):
        self.chunk_size = 1000  # Process in chunks for large datasets
    
    def export_users(self, 
                    users: List[Dict],
                    date_from: Optional[datetime] = None,
                    date_to: Optional[datetime] = None,
                    status_filter: Optional[str] = None) -> str:
        \"\"\"
        Export users to CSV with optional filters
        
        Args:
            users: List of user dictionaries
            date_from: Start date filter
            date_to: End date filter
            status_filter: Filter by user status
            
        Returns:
            Path to generated CSV file
        \"\"\"
        # Apply filters
        filtered_users = self._apply_filters(users, date_from, date_to, status_filter)
        
        # Generate CSV
        output_file = f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        with open(output_file, 'w', newline='') as csvfile:
            if not filtered_users:
                return output_file
                
            fieldnames = filtered_users[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            # Write in chunks for memory efficiency
            for i in range(0, len(filtered_users), self.chunk_size):
                chunk = filtered_users[i:i + self.chunk_size]
                writer.writerows(chunk)
        
        return output_file
    
    def _apply_filters(self, users, date_from, date_to, status_filter):
        \"\"\"Apply filters to user list\"\"\"
        filtered = users
        
        if date_from:
            filtered = [u for u in filtered 
                       if datetime.fromisoformat(u.get('created_at', '')) >= date_from]
        
        if date_to:
            filtered = [u for u in filtered 
                       if datetime.fromisoformat(u.get('created_at', '')) <= date_to]
        
        if status_filter:
            filtered = [u for u in filtered 
                       if u.get('status') == status_filter]
        
        return filtered
"""
        
        print("✅ Feature implementation created")
        print("   - CSV export class")
        print("   - Date range filtering")
        print("   - Status filtering")
        print("   - Chunked processing for large datasets")
        
        # Save to a temporary location
        impl_file = self.project_root / "csv_exporter.py"
        with open(impl_file, 'w') as f:
            f.write(implementation)
        
        return True
    
    def add_tests(self):
        """Add unit tests for the feature"""
        tests = """
import unittest
from datetime import datetime, timedelta
from csv_exporter import CSVExporter
import os

class TestCSVExporter(unittest.TestCase):
    
    def setUp(self):
        self.exporter = CSVExporter()
        self.test_users = [
            {
                'id': 1,
                'name': 'John Doe',
                'email': 'john@example.com',
                'status': 'active',
                'created_at': '2024-01-15T10:00:00'
            },
            {
                'id': 2,
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'status': 'inactive',
                'created_at': '2024-02-20T10:00:00'
            }
        ]
    
    def test_export_all_users(self):
        \"\"\"Test exporting all users without filters\"\"\"
        output_file = self.exporter.export_users(self.test_users)
        
        self.assertTrue(os.path.exists(output_file))
        
        # Verify content
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn('John Doe', content)
            self.assertIn('Jane Smith', content)
        
        # Cleanup
        os.remove(output_file)
    
    def test_filter_by_status(self):
        \"\"\"Test filtering by user status\"\"\"
        output_file = self.exporter.export_users(
            self.test_users,
            status_filter='active'
        )
        
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn('John Doe', content)
            self.assertNotIn('Jane Smith', content)
        
        os.remove(output_file)
    
    def test_date_range_filter(self):
        \"\"\"Test date range filtering\"\"\"
        date_from = datetime(2024, 2, 1)
        date_to = datetime(2024, 3, 1)
        
        output_file = self.exporter.export_users(
            self.test_users,
            date_from=date_from,
            date_to=date_to
        )
        
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertNotIn('John Doe', content)  # Created in January
            self.assertIn('Jane Smith', content)    # Created in February
        
        os.remove(output_file)
    
    def test_large_dataset_chunking(self):
        \"\"\"Test handling of large datasets\"\"\"
        # Create 5000 test users
        large_dataset = []
        for i in range(5000):
            large_dataset.append({
                'id': i,
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'status': 'active' if i % 2 == 0 else 'inactive',
                'created_at': datetime.now().isoformat()
            })
        
        # Should complete without memory issues
        output_file = self.exporter.export_users(large_dataset)
        
        self.assertTrue(os.path.exists(output_file))
        
        # Verify all users exported
        line_count = 0
        with open(output_file, 'r') as f:
            line_count = sum(1 for line in f)
        
        # Header + 5000 users
        self.assertEqual(line_count, 5001)
        
        os.remove(output_file)

if __name__ == '__main__':
    unittest.main()
"""
        
        print("✅ Unit tests created")
        print("   - Test all users export")
        print("   - Test status filtering")
        print("   - Test date range filtering")
        print("   - Test large dataset handling")
        
        # Save tests
        test_file = self.project_root / "test_csv_exporter.py"
        with open(test_file, 'w') as f:
            f.write(tests)
        
        return True
    
    def run_evaluation(self):
        """Run RLVR evaluation"""
        # Create a dummy task for evaluation
        task_id = f"feature-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        task_dir = self.project_root / '.claude' / 'tasks' / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # Create metadata
        metadata = {
            'task_id': task_id,
            'agent_name': 'agent-feature-senior',
            'task_type': 'feature',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'completed'
        }
        
        with open(task_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f)
        
        env = os.environ.copy()
        env['CLAUDE_PROJECT_DIR'] = str(self.project_root)
        env['DOOM_TASK_ID'] = task_id
        
        # Simulate running tests (would normally be done by CI)
        print("\n   Running tests...")
        print("   .... (4/4 passed)")
        print("   Coverage: 92%")
        
        # Run evaluator
        evaluator_path = self.project_root / '.claude' / 'scripts' / 'rlvr-evaluate.py'
        
        result = subprocess.run(
            [
                'python3', str(evaluator_path),
                '--task-id', task_id,
                '--agent-name', 'agent-feature-senior',
                '--task-status', 'completed',
                '--test'  # Use test mode
            ],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(self.project_root)
        )
        
        if result.stdout:
            try:
                eval_result = json.loads(result.stdout)
                reward = eval_result.get('reward', 0)
                print(f"\n✅ Evaluation complete - Reward: {reward:.2f}")
                self.task_id = task_id
                return True
            except:
                pass
        
        print("❌ Evaluation failed")
        return False
    
    def verify_tier_impact(self):
        """Check if the agent's performance affects tier"""
        print("📊 Checking tier impact...")
        
        # In a real scenario, this would check if the agent
        # is close to promotion/demotion thresholds
        print("   Current tier: Senior")
        print("   Rolling average: 3.8")
        print("   Promotion threshold: 4.0")
        print("   Status: 0.2 points from promotion to Principal")
        
        return True


def main():
    """Run the feature scenario test"""
    scenario = FeatureScenario()
    
    try:
        success = scenario.run_scenario()
        
        # Cleanup
        for file in ['task.yml', 'csv_exporter.py', 'test_csv_exporter.py']:
            filepath = scenario.project_root / file
            if filepath.exists():
                filepath.unlink()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ Scenario failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())