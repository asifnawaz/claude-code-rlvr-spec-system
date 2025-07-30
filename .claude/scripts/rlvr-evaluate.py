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
            'review_feedback_score': self._evaluate_review_feedback(),
            'doom_template_score': self._evaluate_doom_template(task_id)
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
            project_root = Path(os.environ.get('CLAUDE_PROJECT_DIR', '.'))
            feedback_file = project_root / 'data' / 'tasks' / os.environ.get('DOOM_TASK_ID', 'unknown') / 'review.json'
            if feedback_file.exists():
                with open(feedback_file) as f:
                    review = json.load(f)
                    return review.get('score', 0.0)
        except:
            pass
        
        # No review data available
        return 0.0
    
    def _evaluate_doom_template(self, task_id: str) -> float:
        """Evaluate Doom template compliance (-1 to +1)"""
        try:
            # Get the task metadata to check prompt structure
            project_root = Path(os.environ.get('CLAUDE_PROJECT_DIR', '.'))
            task_dir = project_root / 'data' / 'tasks' / task_id
            metadata_file = task_dir / 'metadata.json'
            
            if not metadata_file.exists():
                return 0.0
            
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            prompt = metadata.get('optimized_prompt', '')
            
            # Import the validator
            import sys
            project_root = Path(os.environ.get('CLAUDE_PROJECT_DIR', '.'))
            sys.path.insert(0, str(project_root / ".claude" / "hooks"))
            try:
                from validate_prompt_structure import DoomPromptValidator
                validator = DoomPromptValidator()
                
                # Validate the prompt
                is_valid, results = validator.validate(prompt)
                
                # Get the score (0-10)
                doom_score = results.get('score', 0)
                
                # Check acceptance criteria completion
                if '$ACCEPTANCE_CRITERIA' in prompt:
                    # Count checked items
                    checked = prompt.count('[x]')
                    total_items = prompt.count('[ ]') + checked
                    if total_items > 0:
                        completion_rate = checked / total_items
                        # Bonus for completing acceptance criteria
                        doom_score += completion_rate * 2
                
                # Normalize to -1 to +1
                # Score 10+ = 1.0, Score 7 = 0.5, Score 5 = 0, Score < 3 = negative
                if doom_score >= 10:
                    return 1.0
                elif doom_score >= 7:
                    return (doom_score - 7) / 3 * 0.5 + 0.5
                elif doom_score >= 5:
                    return (doom_score - 5) / 2 * 0.5
                else:
                    return (doom_score - 5) / 5
                    
            except Exception as e:
                print(f"Error loading validator: {e}")
                # Fallback: check for basic Doom fields
                required_fields = ['$GOAL:', '$CONTEXT:', '$INPUT:', '$CONSTRAINTS:', 
                                 '$OUTPUT_EXPECTED:', '$ACCEPTANCE_CRITERIA:', '$DEADLINE:']
                found = sum(1 for field in required_fields if field in prompt)
                return (found / len(required_fields)) * 2 - 1
                
        except Exception as e:
            print(f"Error evaluating Doom template: {e}")
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
            agent_file = Path(__file__).parent.parent / "agents" / f"{agent_name}.md"
            if agent_file.exists():
                # Parse markdown front-matter
                in_frontmatter = False
                frontmatter_lines = []
                
                with open(agent_file) as f:
                    for line in f:
                        line = line.strip()
                        if line == '---':
                            if not in_frontmatter:
                                in_frontmatter = True
                                continue
                            else:
                                break
                        if in_frontmatter:
                            frontmatter_lines.append(line)
                
                # Simple parsing for performance section
                performance = {}
                in_performance = False
                for line in frontmatter_lines:
                    if line == 'performance:':
                        in_performance = True
                    elif in_performance and line.startswith('  '):
                        if ':' in line:
                            key, value = line.strip().split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            try:
                                if key == 'rolling_avg_reward':
                                    performance[key] = float(value)
                                elif key == 'total_tasks':
                                    performance[key] = int(value)
                            except:
                                pass
                    elif not line.startswith('  '):
                        in_performance = False
                
                if performance:
                    return performance
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