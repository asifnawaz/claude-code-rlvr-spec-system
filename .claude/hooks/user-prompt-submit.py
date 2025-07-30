#!/usr/bin/env python3
"""
UserPromptSubmit Hook - Autonomous Agent Handling System
Automatically detects task type, optimizes prompt, and routes to best agent
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Read hook data from stdin
try:
    hook_data = json.load(sys.stdin)
except:
    sys.exit(0)

project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '.')

# Import path configuration
sys.path.insert(0, str(Path(__file__).parent))
from doom_paths import get_paths, get_agents_dir, get_tasks_dir, get_scoreboard_dir, get_prompts_dir

# Get configured paths
paths = get_paths()
AGENTS_DIR = get_agents_dir()
TASKS_DIR = get_tasks_dir()
SCOREBOARD_DIR = get_scoreboard_dir()
PROMPTS_DIR = get_prompts_dir()

# Get original user prompt
original_prompt = hook_data.get('userPrompt', '')

# Skip if no prompt or if already processed
if not original_prompt or '[Doom-RLVR Agent Assignment]' in original_prompt:
    sys.exit(0)

def detect_task_type(prompt):
    """Automatically detect task type from user prompt"""
    prompt_lower = prompt.lower()
    
    # First check if this is a question or informational request
    question_indicators = ['what is', 'what are', 'how does', 'how do', 'why is', 'why does', 
                          'where is', 'where are', 'who is', 'explain', 'describe', 'tell me',
                          'can you explain', 'help me understand', '?']
    
    is_question = any(indicator in prompt_lower for indicator in question_indicators)
    
    # If it's clearly a question, return None to skip agent routing
    if is_question and not any(action in prompt_lower for action in ['fix', 'implement', 'create', 'add']):
        return None
    
    # Keywords for each task type
    task_indicators = {
        'bugfix': ['fix', 'bug', 'error', 'issue', 'broken', 'crash', 'fail', 'debug', 'repair'],
        'feature': ['add', 'implement', 'create', 'new feature', 'build', 'develop', 'enhance'],
        'refactor': ['refactor', 'clean', 'improve', 'optimize', 'restructure', 'reorganize'],
        'security': ['security', 'vulnerability', 'exploit', 'injection', 'auth', 'permission', 'secure'],
        'testing': ['test', 'coverage', 'unit test', 'integration', 'testing', 'spec'],
        'performance': ['performance', 'speed', 'optimize', 'slow', 'efficiency', 'latency']
    }
    
    # Score each task type
    scores = {}
    for task_type, keywords in task_indicators.items():
        score = sum(1 for keyword in keywords if keyword in prompt_lower)
        if score > 0:
            scores[task_type] = score
    
    # Return highest scoring type, or None if no clear task
    if scores:
        return max(scores, key=scores.get)
    return None

def detect_priority(prompt):
    """Detect task priority from prompt"""
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['urgent', 'critical', 'asap', 'immediately', 'emergency']):
        return 'P0'
    elif any(word in prompt_lower for word in ['important', 'priority', 'soon']):
        return 'P1'
    elif any(word in prompt_lower for word in ['minor', 'low priority', 'when possible']):
        return 'P3'
    return 'P2'

def optimize_prompt(prompt, task_type):
    """Optimize and enhance the user prompt with Doom template"""
    
    # Import the validator
    sys.path.insert(0, str(paths['hooks_dir']))
    try:
        from validate_prompt_structure import DoomPromptValidator
        validator = DoomPromptValidator()
        
        # Check if prompt already follows Doom format
        is_valid, results = validator.validate(prompt)
        if is_valid and results['score'] >= 8:
            # Already well-structured
            return prompt
    except:
        # Fallback if validator not available
        pass
    
    # Create Doom-compliant prompt based on task type
    doom_templates = {
        'bugfix': """# Doom Prompt
$GOAL: Fix the reported bug
$CONTEXT: {prompt}
$INPUT: Error logs, affected code files, reproduction steps
$CONSTRAINTS: Maintain backward compatibility, minimize changes outside bug scope
$OUTPUT_EXPECTED: Fixed code with regression tests
$ACCEPTANCE_CRITERIA:
  - [ ] Bug is reproducible before fix
  - [ ] Bug is resolved after fix
  - [ ] All existing tests pass
  - [ ] New regression test added
  - [ ] Code changes are minimal
$DEADLINE: ASAP for production bugs""",
        
        'feature': """# Doom Prompt
$GOAL: Implement new feature
$CONTEXT: {prompt}
$INPUT: Requirements, design specs, API contracts
$CONSTRAINTS: Follow existing patterns, maintain performance, ensure security
$OUTPUT_EXPECTED: Feature implementation with tests and documentation
$ACCEPTANCE_CRITERIA:
  - [ ] Feature works as specified
  - [ ] Unit tests cover new code
  - [ ] Integration tests pass
  - [ ] API documented
  - [ ] UI/UX follows design
  - [ ] Performance benchmarks met
$DEADLINE: Based on sprint planning""",
        
        'refactor': """# Doom Prompt
$GOAL: Refactor code for improved quality
$CONTEXT: {prompt}
$INPUT: Current codebase, performance metrics, code analysis
$CONSTRAINTS: No breaking changes, maintain API contracts, preserve functionality
$OUTPUT_EXPECTED: Refactored code with same functionality but better structure
$ACCEPTANCE_CRITERIA:
  - [ ] All tests pass before and after
  - [ ] Code complexity reduced
  - [ ] Performance maintained or improved
  - [ ] Documentation updated
  - [ ] No breaking changes
$DEADLINE: Low priority unless blocking""",
        
        'security': """# Doom Prompt
$GOAL: Address security vulnerability
$CONTEXT: {prompt}
$INPUT: Security scan results, vulnerability reports, OWASP guidelines
$CONSTRAINTS: No data loss, maintain user experience, comply with standards
$OUTPUT_EXPECTED: Secure implementation with security tests
$ACCEPTANCE_CRITERIA:
  - [ ] Vulnerability fixed
  - [ ] Security tests added
  - [ ] No new vulnerabilities introduced
  - [ ] OWASP guidelines followed
  - [ ] Security documentation updated
$DEADLINE: Critical - immediate attention""",
        
        'testing': """# Doom Prompt
$GOAL: Improve test coverage
$CONTEXT: {prompt}
$INPUT: Current test suite, coverage reports, code to test
$CONSTRAINTS: Tests must be maintainable, fast, and reliable
$OUTPUT_EXPECTED: Comprehensive test suite
$ACCEPTANCE_CRITERIA:
  - [ ] Unit tests for all functions
  - [ ] Integration tests for workflows
  - [ ] Edge cases covered
  - [ ] Tests are fast and reliable
  - [ ] Coverage target met
$DEADLINE: Before feature release""",
        
        'performance': """# Doom Prompt
$GOAL: Optimize performance
$CONTEXT: {prompt}
$INPUT: Performance profiles, bottleneck analysis, benchmarks
$CONSTRAINTS: Maintain functionality, avoid premature optimization
$OUTPUT_EXPECTED: Optimized code with performance benchmarks
$ACCEPTANCE_CRITERIA:
  - [ ] Performance baseline measured
  - [ ] Bottlenecks identified
  - [ ] Optimizations implemented
  - [ ] Performance improved by target %
  - [ ] No functionality regression
$DEADLINE: Based on user impact"""
    }
    
    template = doom_templates.get(task_type, """# Doom Prompt
$GOAL: Complete the requested task
$CONTEXT: {prompt}
$INPUT: Relevant files and documentation
$CONSTRAINTS: Follow best practices
$OUTPUT_EXPECTED: Completed task with tests
$ACCEPTANCE_CRITERIA:
  - [ ] Task completed as requested
  - [ ] Tests added/updated
  - [ ] Documentation updated
$DEADLINE: As appropriate""")
    
    return template.format(prompt=prompt)

def parse_markdown_frontmatter(file_path):
    """Parse YAML front-matter from markdown file"""
    data = {}
    in_frontmatter = False
    frontmatter_lines = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.rstrip()
            
            # Check for front-matter boundaries
            if line == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    # End of front-matter
                    break
            
            if in_frontmatter:
                frontmatter_lines.append(line)
    
    # Parse the front-matter
    current_key = None
    for line in frontmatter_lines:
        if not line or line.startswith('#'):
            continue
            
        # Handle list items
        if line.startswith('  - '):
            if current_key and current_key in data:
                if not isinstance(data[current_key], list):
                    data[current_key] = []
                data[current_key].append(line[4:].strip())
        # Handle key-value pairs
        elif ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            current_key = key
            data[key] = value
        # Handle nested data (simple approach)
        elif line.startswith('  ') and ':' in line:
            # Skip nested data for now
            continue
    
    return data

def load_agents():
    """Load available agents from markdown files"""
    agents = []
    for agent_file in AGENTS_DIR.glob("agent-*.md"):
        try:
            agent_data = parse_markdown_frontmatter(agent_file)
            agent_data['name'] = agent_file.stem
            
            # Ensure specializations is a list
            if 'specializations' in agent_data and isinstance(agent_data['specializations'], list):
                agent_data['specializations_list'] = agent_data['specializations']
            
            if agent_data.get('tier') != 'suspended':
                agents.append(agent_data)
        except Exception as e:
            # Log error but continue
            print(f"Error loading agent {agent_file}: {e}", file=sys.stderr)
            continue
    return agents

def select_best_agent(task_type, priority, agents):
    """Select the best agent for the task"""
    tier_priority = {'principal': 3, 'senior': 2, 'junior': 1}
    best_agent = None
    best_score = -1
    
    for agent in agents:
        score = 0
        
        # Check specialization match
        specs = agent.get('specializations_list', [])
        if task_type in specs:
            score += 10
        elif 'general' in specs:
            score += 1
            
        # Add tier score
        tier = agent.get('tier', 'junior')
        score += tier_priority.get(tier, 1)
        
        # Boost principal agents for critical tasks
        if priority == 'P0' and tier == 'principal':
            score += 5
            
        # Consider performance
        perf_score = float(agent.get('rolling_avg_reward', '0') or '0')
        score += perf_score
        
        if score > best_score:
            best_score = score
            best_agent = agent
    
    return best_agent

# Detect task type and priority
task_type = detect_task_type(original_prompt)

# If not a task (just a question), skip agent routing
if task_type is None:
    # Add CLAUDE.md context reminder
    claude_md_reminder = ""
    claude_md_path = Path(project_dir) / '.claude' / 'CLAUDE.md'
    if claude_md_path.exists():
        claude_md_reminder = """
[DOOM-RLVR Project Context]
• This project uses autonomous agent routing based on task type detection
• Agents are evaluated using RLVR metrics (test coverage, lint, security, complexity)
• Commands: /doom-status, /doom-leaderboard, /doom-agent, /doom-report
• Tasks are automatically structured using the Doom template format
• All hooks and evaluation are handled automatically - just describe what you need
• Important: Refer to .claude/CLAUDE.md for full system documentation
"""
    
    response = {
        "userPrompt": claude_md_reminder + "\n" + original_prompt if claude_md_reminder else original_prompt
    }
    print(json.dumps(response))
    sys.exit(0)

priority = detect_priority(original_prompt)

# Load and select agent
agents = load_agents()
if not agents:
    # No agents available, proceed with original prompt
    sys.exit(0)

selected_agent = select_best_agent(task_type, priority, agents)
if not selected_agent:
    # Use first available agent
    selected_agent = agents[0]

# Create task ID
task_id = f"{task_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

# Optimize the prompt
optimized_prompt = optimize_prompt(original_prompt, task_type)

# Load agent's system prompt from file if available
agent_prompt = ""
agent_prompt_file = AGENTS_DIR / f"{selected_agent['name']}.yml"
if agent_prompt_file.exists():
    with open(agent_prompt_file, 'r') as f:
        in_prompt_section = False
        for line in f:
            if 'system_prompt:' in line:
                in_prompt_section = True
                continue
            elif in_prompt_section:
                if line.strip() and not line.startswith(' '):
                    break
                agent_prompt += line[2:] if line.startswith('  ') else line

# Create comprehensive agent context
agent_context = f"""[Doom-RLVR Agent Assignment]

You are now operating as: {selected_agent['name']} ({selected_agent.get('tier', 'junior')} tier)
Task ID: {task_id}
Task Type: {task_type}
Priority: {priority}

=== AGENT PROFILE ===
{agent_prompt.strip()}

=== TASK ANALYSIS ===
Detected Type: {task_type}
Priority Level: {priority}
Optimization Applied: Yes

=== OPTIMIZED REQUEST ===
{optimized_prompt}

=== EVALUATION CRITERIA ===
Your performance will be evaluated on:
1. Test Coverage: Increase test coverage, never decrease it (30%)
2. Code Quality: Pass all lint checks, follow style guides (20%)
3. Security: No new vulnerabilities, fix existing ones (20%)
4. Complexity: Reduce complexity where possible (10%)
5. CI/CD: All pipelines must pass (10%)
6. Review: Clean, reviewable code with good practices (10%)

=== CONSTRAINTS ===
- You have access to these tools: {selected_agent.get('tools_allowed', 'all standard tools')}
- Maximum context tokens: {selected_agent.get('max_context_tokens', '75000')}
- Follow all project conventions and patterns
- Ensure backward compatibility unless explicitly asked to break it

=== APPROACH ===
Based on your tier ({selected_agent.get('tier', 'junior')}), you should:
""" + (
    "- Take initiative and make architectural decisions\n- Optimize for long-term maintainability\n- Set best practices for the team"
    if selected_agent.get('tier') == 'principal' else
    "- Implement robust solutions with good test coverage\n- Consider edge cases and error handling\n- Refactor code when it improves quality"
    if selected_agent.get('tier') == 'senior' else
    "- Follow instructions carefully\n- Ask for clarification when unsure\n- Focus on correctness over optimization"
) + f"""

Now, let's work on this {task_type} task with {priority} priority.
"""

# Save task metadata
metadata = {
    'task_id': task_id,
    'task_type': task_type,
    'priority': priority,
    'agent_name': selected_agent['name'],
    'agent_tier': selected_agent.get('tier', 'junior'),
    'timestamp': datetime.utcnow().isoformat(),
    'original_prompt': original_prompt,
    'optimized': True,
    'auto_detected': True
}

# Create task directory and save metadata
task_dir = TASKS_DIR / task_id
task_dir.mkdir(parents=True, exist_ok=True)
with open(task_dir / "metadata.json", 'w') as f:
    json.dump(metadata, f, indent=2)

# Log the assignment
log_entry = {
    'timestamp': datetime.utcnow().isoformat(),
    'event': 'autonomous_task_assigned',
    'task_id': task_id,
    'task_type': task_type,
    'priority': priority,
    'agent_name': selected_agent['name'],
    'agent_tier': selected_agent.get('tier', 'junior'),
    'prompt_optimized': True
}

log_file = SCOREBOARD_DIR / "events.jsonl"
log_file.parent.mkdir(parents=True, exist_ok=True)
with open(log_file, 'a') as f:
    f.write(json.dumps(log_entry) + '\n')

# Return the enhanced prompt with agent context
response = {
    "userPrompt": agent_context + "\n\n" + original_prompt
}

print(json.dumps(response))