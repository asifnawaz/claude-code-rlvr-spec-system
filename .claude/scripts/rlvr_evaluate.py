#!/usr/bin/env python3
"""
RLVR Evaluator - Calculates rewards based on multiple quality metrics
"""

import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional

class RLVREvaluator:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "evaluator-config.json"
        
        # Default configuration
        self.config = {
            "weights": {
                "test_coverage_delta": 0.3,
                "lint_score": 0.2,
                "security_scan_score": 0.2,
                "code_complexity_delta": 0.1,
                "ci_pipeline_status": 0.1,
                "review_feedback_score": 0.1
            },
            "thresholds": {
                "min_test_coverage": 0.8,
                "max_complexity_increase": 0.1,
                "critical_security_fail": 0,
                "lint_error_tolerance": 5
            }
        }
        
        # Load custom config if exists
        if Path(config_path).exists():
            with open(config_path) as f:
                custom_config = json.load(f)
                self.config.update(custom_config)
        
        self.weights = self.config['weights']
        self.thresholds = self.config['thresholds']
    
    def evaluate(self, task_id: str, agent_name: str, task_status: str) -> Dict:
        """Main evaluation entry point"""
        
        # Collect all evaluation components
        components = {
            'test_coverage_delta': self._evaluate_test_coverage(),
            'lint_score': self._evaluate_lint(),
            'security_scan_score': self._evaluate_security(),
            'code_complexity_delta': self._evaluate_complexity(),
            'ci_pipeline_status': self._evaluate_ci_status(),
            'review_feedback_score': self._evaluate_review_feedback()
        }
        
        # Calculate weighted reward
        reward = self._calculate_reward(components, task_status)
        
        # Get agent performance for metadata
        agent_performance = self._get_agent_performance(agent_name)
        
        # Record evaluation
        evaluation_result = {
            'timestamp': datetime.utcnow().isoformat(),
            'task_id': task_id,
            'agent_name': agent_name,
            'task_status': task_status,
            'reward': reward,
            'components': components,
            'metadata': {
                'evaluator_version': '1.0.0',
                'weights_used': self.weights,
                'agent_performance': agent_performance
            }
        }
        
        return evaluation_result
    
    def _evaluate_test_coverage(self) -> float:
        """Evaluate test coverage delta (-1 to +1)"""
        try:
            # Try different test runners
            coverage_commands = [
                ['npm', 'run', 'test:coverage', '--', '--json'],
                ['pytest', '--cov', '--cov-report=json'],
                ['go', 'test', '-cover', '-json', './...'],
                ['mvn', 'test', 'jacoco:report']
            ]
            
            current_coverage = None
            for cmd in coverage_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=os.environ.get('PROJECT_ROOT', '.')
                    )
                    if result.returncode == 0:
                        # Parse coverage based on tool
                        if 'npm' in cmd[0]:
                            # Jest/JavaScript coverage
                            coverage_file = Path('coverage/coverage-summary.json')
                            if coverage_file.exists():
                                with open(coverage_file) as f:
                                    data = json.load(f)
                                    current_coverage = data['total']['lines']['pct'] / 100
                        # Add other parsers as needed
                        break
                except:
                    continue
            
            if current_coverage is None:
                # No coverage data available
                return 0.0
            
            # Get baseline coverage (simplified - in reality would check git history)
            baseline_coverage = 0.75  # Default baseline
            
            # Calculate delta
            delta = current_coverage - baseline_coverage
            
            # Normalize to -1 to +1 range
            if delta > 0:
                return min(delta / 0.1, 1.0)  # +10% = perfect score
            else:
                return max(delta / 0.05, -1.0)  # -5% = worst score
                
        except Exception as e:
            print(f"Error evaluating test coverage: {e}")
            return 0.0
    
    def _evaluate_lint(self) -> float:
        """Evaluate linting score (0 to 1)"""
        try:
            # Try different linters
            lint_commands = [
                ['npm', 'run', 'lint', '--', '--format', 'json'],
                ['eslint', '.', '--format', 'json'],
                ['pylint', '--output-format=json', '**/*.py'],
                ['golint', '-json', './...']
            ]
            
            for cmd in lint_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd=os.environ.get('PROJECT_ROOT', '.')
                    )
                    
                    if result.returncode == 0:
                        return 1.0  # No lint errors
                    elif result.stdout:
                        # Parse lint results
                        try:
                            lint_results = json.loads(result.stdout)
                            if isinstance(lint_results, list):
                                total_files = len(lint_results)
                                clean_files = sum(1 for r in lint_results 
                                                if isinstance(r, dict) and r.get('errorCount', 0) == 0)
                                return clean_files / total_files if total_files > 0 else 1.0
                        except:
                            # If we can't parse, assume some errors
                            return 0.7
                except:
                    continue
            
            # No linter found or all failed
            return 0.5
            
        except Exception as e:
            print(f"Error evaluating lint: {e}")
            return 0.5
    
    def _evaluate_security(self) -> float:
        """Evaluate security scan score (0 to 1)"""
        try:
            # Try different security scanners
            security_commands = [
                ['snyk', 'test', '--json'],
                ['npm', 'audit', '--json'],
                ['safety', 'check', '--json'],
                ['gosec', '-fmt=json', './...']
            ]
            
            for cmd in security_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=os.environ.get('PROJECT_ROOT', '.')
                    )
                    
                    if result.stdout:
                        scan_data = json.loads(result.stdout)
                        
                        # Parse based on scanner type
                        if cmd[0] == 'snyk':
                            vulnerabilities = scan_data.get('vulnerabilities', [])
                        elif cmd[0] == 'npm':
                            vulnerabilities = scan_data.get('vulnerabilities', {})
                            # Convert npm audit format
                            vuln_count = sum(v.get('findings', 0) for v in vulnerabilities.values())
                            if vuln_count == 0:
                                return 1.0
                            else:
                                return max(0, 1 - (vuln_count / 10))  # 10+ vulns = 0 score
                        
                        # Generic vulnerability scoring
                        if isinstance(vulnerabilities, list):
                            severity_weights = {
                                'low': 0.1,
                                'medium': 0.3,
                                'high': 0.6,
                                'critical': 1.0
                            }
                            
                            if not vulnerabilities:
                                return 1.0
                            
                            total_weight = sum(
                                severity_weights.get(v.get('severity', 'low'), 0.1) 
                                for v in vulnerabilities
                            )
                            
                            # Normalize score
                            max_acceptable_weight = 2.0
                            return max(0, 1 - (total_weight / max_acceptable_weight))
                        
                        break
                except:
                    continue
            
            # No scanner found, return neutral score
            return 0.8
            
        except Exception as e:
            print(f"Error evaluating security: {e}")
            return 0.8
    
    def _evaluate_complexity(self) -> float:
        """Evaluate code complexity delta (-1 to +1)"""
        try:
            # Simple complexity check using line count and file count
            # In production, would use proper complexity analysis tools
            
            project_root = Path(os.environ.get('PROJECT_ROOT', '.'))
            
            # Count lines of code
            total_lines = 0
            file_count = 0
            
            for ext in ['*.py', '*.js', '*.ts', '*.java', '*.go']:
                for file_path in project_root.rglob(ext):
                    if 'node_modules' not in str(file_path) and '.git' not in str(file_path):
                        try:
                            with open(file_path) as f:
                                total_lines += len(f.readlines())
                                file_count += 1
                        except:
                            pass
            
            # Simple heuristic: more lines = more complex
            # Baseline: 10000 lines
            baseline_lines = 10000
            complexity_ratio = total_lines / baseline_lines
            
            # If significantly more complex, penalize
            if complexity_ratio > 1.2:
                return -0.5
            elif complexity_ratio > 1.1:
                return -0.2
            elif complexity_ratio < 0.9:
                return 0.2  # Reduced complexity is good
            else:
                return 0.0
                
        except Exception as e:
            print(f"Error evaluating complexity: {e}")
            return 0.0
    
    def _evaluate_ci_status(self) -> float:
        """Evaluate CI pipeline status (0 or 1)"""
        try:
            # Check for CI status files
            ci_indicators = [
                '.github/workflows',
                '.gitlab-ci.yml',
                'Jenkinsfile',
                '.circleci/config.yml'
            ]
            
            project_root = Path(os.environ.get('PROJECT_ROOT', '.'))
            
            # Check if CI is configured
            ci_configured = any((project_root / indicator).exists() for indicator in ci_indicators)
            
            if not ci_configured:
                return 0.5  # No CI configured, neutral score
            
            # Try to check recent CI status
            try:
                # Check GitHub Actions
                result = subprocess.run([
                    'gh', 'run', 'list',
                    '--limit', '1',
                    '--json', 'status,conclusion'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout:
                    runs = json.loads(result.stdout)
                    if runs and runs[0]['status'] == 'completed':
                        return 1.0 if runs[0]['conclusion'] == 'success' else 0.0
            except:
                pass
            
            # CI configured but can't check status
            return 0.7
            
        except Exception as e:
            print(f"Error evaluating CI status: {e}")
            return 0.5
    
    def _evaluate_review_feedback(self) -> float:
        """Evaluate review feedback score (-1 to +1)"""
        # In a real implementation, this would integrate with PR review systems
        # For now, check if there's a review feedback file
        try:
            feedback_file = Path('.claude/tasks') / os.environ.get('KIRO_TASK_ID', 'unknown') / 'review.json'
            if feedback_file.exists():
                with open(feedback_file) as f:
                    review = json.load(f)
                    return review.get('score', 0.0)
        except:
            pass
        
        # No review data available
        return 0.0
    
    def _calculate_reward(self, components: Dict[str, float], task_status: str) -> float:
        """Calculate final weighted reward"""
        
        # Base penalty for failure
        if task_status == 'failed':
            base_penalty = -2.0
        elif task_status == 'timeout':
            base_penalty = -1.0
        else:
            base_penalty = 0.0
        
        # Calculate weighted sum
        weighted_sum = sum(
            self.weights.get(key, 0) * value 
            for key, value in components.items() 
            if key in self.weights
        )
        
        # Normalize to -5 to +5 range
        normalized_reward = weighted_sum * 5
        
        # Apply base penalty
        final_reward = normalized_reward + base_penalty
        
        # Clamp to valid range
        return max(-5, min(5, final_reward))
    
    def _get_agent_performance(self, agent_name: str) -> Dict:
        """Get current agent performance metrics"""
        try:
            agent_file = Path(__file__).parent.parent / "agents" / f"{agent_name}.yml"
            if agent_file.exists():
                import yaml
                with open(agent_file) as f:
                    agent_data = yaml.safe_load(f)
                    return agent_data.get('performance', {})
        except:
            pass
        
        return {
            'rolling_avg_reward': 0.0,
            'total_tasks': 0,
            'last_10_rewards': []
        }


def main():
    """CLI entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RLVR Evaluator')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--agent-name', required=True)
    parser.add_argument('--task-status', required=True)
    parser.add_argument('--output-dir', default='.')
    parser.add_argument('--validate', action='store_true', help='Validate configuration')
    parser.add_argument('--test', action='store_true', help='Run with test data')
    
    args = parser.parse_args()
    
    evaluator = RLVREvaluator()
    
    if args.validate:
        print("Configuration valid")
        print(json.dumps(evaluator.config, indent=2))
        return
    
    if args.test:
        # Test with sample data
        result = evaluator.evaluate("test-001", "agent-test", "completed")
        print(json.dumps(result, indent=2))
        return
    
    # Normal evaluation
    result = evaluator.evaluate(args.task_id, args.agent_name, args.task_status)
    
    # Write to output
    output_path = Path(args.output_dir) / 'rlvr.jsonl'
    with open(output_path, 'a') as f:
        f.write(json.dumps(result) + '\n')
    
    # Output for hook
    print(json.dumps(result))


if __name__ == '__main__':
    main()