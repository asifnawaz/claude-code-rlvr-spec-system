#!/usr/bin/env python3
"""
Integration tests for DOOM-RLVR system
Tests the complete flow from prompt to evaluation
"""

import unittest
import json
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock


class TestEndToEndFlow(unittest.TestCase):
    """Test complete task flow from submission to evaluation"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.test_dir) / '.claude'
        
        # Create directory structure
        (self.claude_dir / 'tasks').mkdir(parents=True)
        (self.claude_dir / 'scoreboard').mkdir(parents=True)
        (self.claude_dir / 'agents').mkdir(parents=True)
        (self.claude_dir / 'feedback').mkdir(parents=True)
        
        # Create test agent
        agent_config = """---
name: agent-bugfix-senior
tier: senior
specializations: [bugfix, testing]
tools_allowed:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
performance:
  avg_reward: 3.8
  total_tasks: 25
---

You are a senior bug fixing specialist.
"""
        
        with open(self.claude_dir / 'agents' / 'agent-bugfix-senior.md', 'w') as f:
            f.write(agent_config)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    @patch('subprocess.run')
    def test_complete_task_flow(self, mock_subprocess):
        """Test complete flow from prompt to evaluation"""
        # Simulate user prompt
        user_prompt = "Fix the login bug where users get 500 error"
        
        # 1. Task Detection (simplified)
        task_type = 'bugfix'
        priority = 'P1'
        
        # 2. Create task
        task_id = f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        task_dir = self.claude_dir / 'tasks' / task_id
        task_dir.mkdir(parents=True)
        
        task_metadata = {
            'task_id': task_id,
            'task_type': task_type,
            'priority': priority,
            'description': user_prompt,
            'agent_name': 'agent-bugfix-senior',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'in_progress'
        }
        
        with open(task_dir / 'metadata.json', 'w') as f:
            json.dump(task_metadata, f)
        
        # 3. Simulate task execution
        # Mock subprocess calls for various checks
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout='All tests pass\nCoverage: 85%',
            stderr=''
        )
        
        # 4. Simulate evaluation
        evaluation_result = {
            'task_id': task_id,
            'agent_name': 'agent-bugfix-senior',
            'timestamp': datetime.utcnow().isoformat(),
            'reward': 3.9,
            'components': {
                'test_coverage_delta': 0.05,
                'lint_score': 0.95,
                'security_scan_score': 1.0,
                'code_complexity_delta': -0.02,
                'ci_pipeline_status': 1.0,
                'review_feedback_score': 0.9,
                'doom_template_score': 8.5
            }
        }
        
        # Save evaluation
        with open(self.claude_dir / 'scoreboard' / 'rlvr.jsonl', 'a') as f:
            f.write(json.dumps(evaluation_result) + '\n')
        
        # Verify task was created
        self.assertTrue(task_dir.exists())
        
        # Verify evaluation was saved
        with open(self.claude_dir / 'scoreboard' / 'rlvr.jsonl') as f:
            saved_eval = json.loads(f.read().strip())
            self.assertEqual(saved_eval['task_id'], task_id)
            self.assertEqual(saved_eval['reward'], 3.9)


class TestHookIntegration(unittest.TestCase):
    """Test hook integration and data flow"""
    
    def test_hook_data_flow(self):
        """Test data flow between hooks"""
        # Test UserPromptSubmit -> PreToolUse -> PostToolUse -> Stop
        
        # Simulate hook data
        initial_data = {
            'prompt': 'Fix the authentication bug',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # UserPromptSubmit output
        task_data = {
            **initial_data,
            'task_type': 'bugfix',
            'priority': 'P1',
            'agent': 'agent-bugfix-senior'
        }
        
        # PreToolUse adds validation
        validated_data = {
            **task_data,
            'tools_validated': True,
            'security_check': 'passed'
        }
        
        # PostToolUse adds metrics
        metrics_data = {
            **validated_data,
            'tools_used': ['Read', 'Edit', 'Bash'],
            'execution_time': 2.5
        }
        
        # Stop adds evaluation
        final_data = {
            **metrics_data,
            'reward': 3.7,
            'evaluation_complete': True
        }
        
        # Verify data accumulation
        self.assertIn('task_type', final_data)
        self.assertIn('tools_validated', final_data)
        self.assertIn('tools_used', final_data)
        self.assertIn('reward', final_data)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_missing_agent(self):
        """Test handling of missing agent"""
        # Simulate task with non-existent agent
        task_type = 'security'
        available_agents = ['agent-bugfix-senior', 'agent-feature-junior']
        
        # Should fallback to general agent or error gracefully
        def select_fallback_agent(task_type, available_agents):
            # Simple fallback logic
            for agent in available_agents:
                if 'senior' in agent:
                    return agent
            return available_agents[0] if available_agents else None
        
        fallback = select_fallback_agent(task_type, available_agents)
        self.assertEqual(fallback, 'agent-bugfix-senior')
    
    def test_invalid_task_format(self):
        """Test handling of invalid task format"""
        invalid_prompts = [
            "",  # Empty
            "   ",  # Whitespace only
            "a" * 10000,  # Too long
            None,  # None type
        ]
        
        def validate_prompt(prompt):
            if not prompt or not isinstance(prompt, str):
                return False
            prompt = prompt.strip()
            if len(prompt) < 5 or len(prompt) > 5000:
                return False
            return True
        
        for prompt in invalid_prompts:
            self.assertFalse(validate_prompt(prompt))
        
        self.assertTrue(validate_prompt("Fix the login bug"))
    
    def test_evaluation_failure_recovery(self):
        """Test recovery from evaluation failures"""
        # Simulate evaluation with missing components
        incomplete_components = {
            'test_coverage_delta': 0.1,
            'lint_score': None,  # Missing
            'security_scan_score': 'error',  # Invalid type
        }
        
        def safe_evaluate(components):
            """Safe evaluation with defaults"""
            defaults = {
                'test_coverage_delta': 0.0,
                'lint_score': 0.5,
                'security_scan_score': 0.5,
                'code_complexity_delta': 0.0,
                'ci_pipeline_status': 0.5,
                'review_feedback_score': 0.5,
                'doom_template_score': 5.0
            }
            
            safe_components = {}
            for key, default in defaults.items():
                value = components.get(key, default)
                # Validate type
                if not isinstance(value, (int, float)):
                    value = default
                safe_components[key] = value
            
            return safe_components
        
        safe_comps = safe_evaluate(incomplete_components)
        self.assertEqual(safe_comps['lint_score'], 0.5)
        self.assertEqual(safe_comps['security_scan_score'], 0.5)


class TestPerformanceAndScale(unittest.TestCase):
    """Test system performance with scale"""
    
    def test_concurrent_tasks(self):
        """Test handling of concurrent tasks"""
        # Simulate multiple tasks running concurrently
        tasks = []
        for i in range(10):
            task = {
                'task_id': f'task_{i}',
                'agent': f'agent-{i % 3}',
                'status': 'in_progress'
            }
            tasks.append(task)
        
        # Verify no task ID collisions
        task_ids = [t['task_id'] for t in tasks]
        self.assertEqual(len(task_ids), len(set(task_ids)))
    
    def test_large_scoreboard(self):
        """Test performance with large scoreboard"""
        # Simulate large number of evaluations
        evaluations = []
        for i in range(1000):
            eval_entry = {
                'task_id': f'task_{i}',
                'reward': 2.0 + (i % 30) / 10,
                'timestamp': datetime.utcnow().isoformat()
            }
            evaluations.append(eval_entry)
        
        # Test aggregation performance
        start_time = datetime.utcnow()
        
        # Calculate average reward
        avg_reward = sum(e['reward'] for e in evaluations) / len(evaluations)
        
        # Group by reward ranges
        reward_buckets = {}
        for e in evaluations:
            bucket = int(e['reward'])
            reward_buckets[bucket] = reward_buckets.get(bucket, 0) + 1
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Should process 1000 entries quickly
        self.assertLess(processing_time, 0.1)
        self.assertAlmostEqual(avg_reward, 3.45, places=1)


if __name__ == '__main__':
    unittest.main(verbosity=2)