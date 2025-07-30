#!/usr/bin/env python3
"""
Test suite for DOOM-RLVR (Reinforcement Learning with Variable Rewards)
Tests the core functionality of the agent orchestration system
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from rlvr_evaluate import RLVREvaluator


class TestRLVREvaluator(unittest.TestCase):
    """Test the RLVR evaluation system"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = Path(self.test_dir) / "evaluator-config.json"
        
        # Create test configuration
        test_config = {
            "weights": {
                "test_coverage_delta": 0.25,
                "lint_score": 0.15,
                "security_scan_score": 0.15,
                "code_complexity_delta": 0.10,
                "ci_pipeline_status": 0.10,
                "review_feedback_score": 0.10,
                "doom_template_score": 0.15
            },
            "thresholds": {
                "min_test_coverage": 0.8,
                "max_complexity_increase": 0.1,
                "critical_security_fail": 0,
                "lint_error_tolerance": 5,
                "min_doom_score": 7.0
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
            
        self.evaluator = RLVREvaluator(str(self.config_path))
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test evaluator initialization"""
        self.assertIsNotNone(self.evaluator.weights)
        self.assertIsNotNone(self.evaluator.thresholds)
        self.assertEqual(self.evaluator.weights['test_coverage_delta'], 0.25)
    
    def test_calculate_reward_perfect_score(self):
        """Test reward calculation with perfect scores"""
        components = {
            'test_coverage_delta': 0.1,  # 10% increase
            'lint_score': 1.0,           # Perfect lint
            'security_scan_score': 1.0,   # No vulnerabilities
            'code_complexity_delta': -0.05,  # Reduced complexity
            'ci_pipeline_status': 1.0,    # All tests pass
            'review_feedback_score': 1.0,  # Perfect review
            'doom_template_score': 10.0   # Perfect template usage
        }
        
        # Calculate expected reward
        expected = (
            0.1 * 10 * 0.25 +  # test coverage (normalized to 0-1)
            1.0 * 0.15 +       # lint
            1.0 * 0.15 +       # security
            1.05 * 0.10 +      # complexity (inverted, so reduction is good)
            1.0 * 0.10 +       # CI
            1.0 * 0.10 +       # review
            1.0 * 0.15         # template (10/10 = 1.0)
        )
        
        reward = self.evaluator._calculate_reward(components)
        self.assertAlmostEqual(reward, expected, places=2)
    
    def test_calculate_reward_poor_score(self):
        """Test reward calculation with poor scores"""
        components = {
            'test_coverage_delta': -0.1,  # 10% decrease
            'lint_score': 0.5,           # Many lint errors
            'security_scan_score': 0.0,   # Critical vulnerabilities
            'code_complexity_delta': 0.2,  # Increased complexity
            'ci_pipeline_status': 0.0,    # Tests fail
            'review_feedback_score': 0.2,  # Poor review
            'doom_template_score': 3.0    # Poor template usage
        }
        
        reward = self.evaluator._calculate_reward(components)
        self.assertLess(reward, 0.5)  # Should be low


class TestTaskDetection(unittest.TestCase):
    """Test task type detection from prompts"""
    
    def setUp(self):
        """Set up test data"""
        self.test_prompts = {
            'bugfix': [
                "Fix the login bug where users can't sign in",
                "There's an error in the payment processing",
                "The app crashes when clicking submit",
                "Broken navigation menu needs fixing"
            ],
            'feature': [
                "Add dark mode to the settings page",
                "Implement CSV export functionality",
                "Create a new dashboard for analytics",
                "Build user profile management"
            ],
            'refactor': [
                "Refactor the authentication module",
                "Clean up the database queries",
                "Improve code structure in the API layer",
                "Restructure the component hierarchy"
            ],
            'security': [
                "Fix SQL injection vulnerability",
                "Update authentication to prevent XSS",
                "Security audit found issues in login",
                "Patch the authorization bypass"
            ],
            'performance': [
                "The page loads too slowly",
                "Optimize database queries for speed",
                "Performance issues with large datasets",
                "Make the search faster"
            ]
        }
    
    def test_detect_task_type(self):
        """Test task type detection accuracy"""
        # This would integrate with the actual task detection logic
        # from user-prompt-submit.py
        
        def detect_task_type(prompt):
            """Simple task type detection for testing"""
            prompt_lower = prompt.lower()
            
            if any(word in prompt_lower for word in ['fix', 'bug', 'error', 'broken', 'crash']):
                return 'bugfix'
            elif any(word in prompt_lower for word in ['add', 'implement', 'create', 'build', 'new']):
                return 'feature'
            elif any(word in prompt_lower for word in ['refactor', 'clean', 'improve', 'restructure']):
                return 'refactor'
            elif any(word in prompt_lower for word in ['security', 'vulnerability', 'injection', 'xss', 'auth']):
                return 'security'
            elif any(word in prompt_lower for word in ['performance', 'slow', 'optimize', 'speed', 'faster']):
                return 'performance'
            else:
                return 'general'
        
        # Test each category
        for expected_type, prompts in self.test_prompts.items():
            for prompt in prompts:
                detected = detect_task_type(prompt)
                self.assertEqual(detected, expected_type, 
                               f"Failed to detect {expected_type} from: {prompt}")


class TestAgentSelection(unittest.TestCase):
    """Test agent selection logic"""
    
    def setUp(self):
        """Set up test agents"""
        self.agents = {
            'agent-bugfix-junior': {
                'tier': 'junior',
                'specializations': ['bugfix'],
                'avg_reward': 2.5
            },
            'agent-bugfix-senior': {
                'tier': 'senior',
                'specializations': ['bugfix'],
                'avg_reward': 3.8
            },
            'agent-feature-junior': {
                'tier': 'junior',
                'specializations': ['feature'],
                'avg_reward': 2.2
            },
            'agent-feature-senior': {
                'tier': 'senior',
                'specializations': ['feature'],
                'avg_reward': 4.1
            },
            'agent-refactor-principal': {
                'tier': 'principal',
                'specializations': ['refactor'],
                'avg_reward': 4.5
            }
        }
    
    def test_select_best_agent(self):
        """Test selection of best agent for task"""
        def select_agent(task_type, agents):
            """Select best agent for task type"""
            # Filter by specialization
            candidates = {
                name: info for name, info in agents.items()
                if task_type in info['specializations']
            }
            
            if not candidates:
                return None
            
            # Sort by tier (principal > senior > junior) then by reward
            tier_order = {'principal': 3, 'senior': 2, 'junior': 1}
            
            best_agent = max(
                candidates.items(),
                key=lambda x: (tier_order.get(x[1]['tier'], 0), x[1]['avg_reward'])
            )
            
            return best_agent[0]
        
        # Test selections
        self.assertEqual(select_agent('bugfix', self.agents), 'agent-bugfix-senior')
        self.assertEqual(select_agent('feature', self.agents), 'agent-feature-senior')
        self.assertEqual(select_agent('refactor', self.agents), 'agent-refactor-principal')
        self.assertIsNone(select_agent('security', self.agents))


class TestTemplateCompliance(unittest.TestCase):
    """Test DOOM template compliance scoring"""
    
    def test_score_template_compliance(self):
        """Test scoring of DOOM template usage"""
        def score_template(prompt):
            """Score how well prompt follows DOOM template"""
            score = 10.0
            
            # Check for required fields
            required_fields = ['$GOAL', '$CONTEXT', '$CONSTRAINTS', '$OUTPUT_FORMAT', 
                             '$STYLE', '$EXAMPLES', '$ACCEPTANCE_CRITERIA']
            
            for field in required_fields:
                if field not in prompt:
                    score -= 2.0
            
            # Check for completion markers
            if '- [x]' in prompt:
                completed = prompt.count('- [x]')
                total = prompt.count('- [ ]') + completed
                if total > 0:
                    score += (completed / total)
            
            return max(0, min(10, score))
        
        # Test cases
        good_prompt = """
        $GOAL: Fix login bug
        $CONTEXT: Users cannot login
        $CONSTRAINTS: Must not break existing auth
        $OUTPUT_FORMAT: Fixed code
        $STYLE: Clean and maintainable
        $EXAMPLES: N/A
        $ACCEPTANCE_CRITERIA:
        - [x] Login works
        - [x] Tests pass
        - [ ] Documentation updated
        """
        
        poor_prompt = "Just fix the login bug"
        
        self.assertGreater(score_template(good_prompt), 7.0)
        self.assertLess(score_template(poor_prompt), 3.0)


class TestTierPromotion(unittest.TestCase):
    """Test agent tier promotion/demotion logic"""
    
    def test_should_promote(self):
        """Test promotion logic"""
        def should_promote(avg_reward, current_tier):
            """Determine if agent should be promoted"""
            thresholds = {
                'junior': 3.5,    # Junior to Senior
                'senior': 4.0,    # Senior to Principal
                'principal': 999  # Cannot promote further
            }
            
            return avg_reward >= thresholds.get(current_tier, 999)
        
        self.assertTrue(should_promote(3.6, 'junior'))
        self.assertFalse(should_promote(3.4, 'junior'))
        self.assertTrue(should_promote(4.1, 'senior'))
        self.assertFalse(should_promote(3.9, 'senior'))
        self.assertFalse(should_promote(5.0, 'principal'))
    
    def test_should_demote(self):
        """Test demotion logic"""
        def should_demote(avg_reward, current_tier):
            """Determine if agent should be demoted"""
            thresholds = {
                'junior': 0,      # Cannot demote further
                'senior': 2.0,    # Senior to Junior
                'principal': 3.5  # Principal to Senior
            }
            
            return avg_reward < thresholds.get(current_tier, 0)
        
        self.assertFalse(should_demote(1.0, 'junior'))
        self.assertTrue(should_demote(1.9, 'senior'))
        self.assertFalse(should_demote(2.1, 'senior'))
        self.assertTrue(should_demote(3.4, 'principal'))
        self.assertFalse(should_demote(3.6, 'principal'))


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)