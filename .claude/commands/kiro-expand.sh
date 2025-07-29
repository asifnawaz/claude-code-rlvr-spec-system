#!/bin/bash
# Expand a task into subtasks

set -euo pipefail

# Display help if no arguments
if [ $# -eq 0 ] || [ "$1" == "--help" ]; then
    echo "Usage: /kiro-expand <task-description>"
    echo ""
    echo "Expand a task into detailed subtasks for implementation."
    echo ""
    echo "This command will:"
    echo "  1. Analyze the task complexity"
    echo "  2. Generate appropriate subtasks"
    echo "  3. Create a structured plan"
    echo ""
    echo "Example:"
    echo "  /kiro-expand \"Add user authentication with JWT\""
    exit 0
fi

# Combine all arguments as task description
TASK_DESC="$*"

echo "=== Task Expansion ==="
echo ""
echo "Task: $TASK_DESC"
echo ""

# Create temporary task file for expansion
TEMP_TASK="/tmp/kiro_expand_$$.json"

# Generate task expansion using Python
python3 <<EOF
import json
import re
from datetime import datetime

task_desc = """$TASK_DESC"""

# Detect task type
task_type = "feature"  # default
keywords = {
    'bugfix': ['fix', 'bug', 'error', 'broken'],
    'feature': ['add', 'implement', 'create', 'build'],
    'refactor': ['refactor', 'clean', 'improve'],
    'security': ['security', 'vulnerability', 'auth'],
    'testing': ['test', 'coverage'],
    'performance': ['performance', 'optimize', 'speed']
}

task_lower = task_desc.lower()
for t_type, kwords in keywords.items():
    if any(kw in task_lower for kw in kwords):
        task_type = t_type
        break

# Generate subtasks based on task type
subtasks = []

if task_type == "bugfix":
    subtasks = [
        "Reproduce the issue and document steps",
        "Identify root cause through debugging",
        "Implement fix with minimal changes",
        "Add regression tests",
        "Verify fix doesn't break existing functionality"
    ]
elif task_type == "feature":
    subtasks = [
        "Design API/interface for the feature",
        "Implement core functionality",
        "Add comprehensive tests",
        "Update documentation",
        "Add examples or demo code"
    ]
elif task_type == "refactor":
    subtasks = [
        "Analyze current code structure",
        "Identify refactoring opportunities",
        "Implement changes incrementally",
        "Ensure all tests pass",
        "Update affected documentation"
    ]
elif task_type == "security":
    subtasks = [
        "Identify security vulnerability details",
        "Assess impact and severity",
        "Implement secure solution",
        "Add security-specific tests",
        "Document security considerations"
    ]
elif task_type == "testing":
    subtasks = [
        "Identify areas lacking test coverage",
        "Write unit tests for core functions",
        "Add integration tests",
        "Implement edge case tests",
        "Set up continuous testing"
    ]
elif task_type == "performance":
    subtasks = [
        "Profile current performance",
        "Identify bottlenecks",
        "Implement optimizations",
        "Benchmark improvements",
        "Document performance gains"
    ]

# Create task structure
task_data = {
    "task_id": f"expanded-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    "type": task_type,
    "description": task_desc,
    "subtasks": [
        {
            "id": f"subtask-{i+1}",
            "description": subtask,
            "status": "pending"
        }
        for i, subtask in enumerate(subtasks)
    ],
    "created_at": datetime.utcnow().isoformat()
}

# Output expansion
print(f"Detected Type: {task_type}")
print("")
print("Subtasks Generated:")
for i, subtask in enumerate(subtasks, 1):
    print(f"  {i}. {subtask}")

# Save to temp file
with open("$TEMP_TASK", "w") as f:
    json.dump(task_data, f, indent=2)
EOF

echo ""
echo "=== Implementation Plan ==="
echo ""

# Show implementation order
echo "Recommended execution order:"
echo "1. Start with understanding/analysis tasks"
echo "2. Implement core functionality"
echo "3. Add tests and validation"
echo "4. Document changes"
echo "5. Review and refine"

echo ""
echo "To create this as a tracked task, save the expansion to a task.yml file."

# Clean up
rm -f "$TEMP_TASK"