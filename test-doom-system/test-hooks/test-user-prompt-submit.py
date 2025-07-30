#!/usr/bin/env python3
"""
Test the UserPromptSubmit hook externally
Simulates how Claude Code would trigger this hook
"""

import json
import subprocess
import os
import sys
from pathlib import Path

# Test scenarios
TEST_PROMPTS = [
    {
        "input": "Fix the login bug where users can't authenticate",
        "expected_type": "bugfix",
        "expected_priority": "P2"  # Default priority
    },
    {
        "input": "Add dark mode toggle to settings page",
        "expected_type": "feature",
        "expected_priority": "P2"
    },
    {
        "input": "URGENT: Security vulnerability in API endpoint",
        "expected_type": "security",
        "expected_priority": "P0"
    },
    {
        "input": "Refactor the database connection layer",
        "expected_type": "refactor",
        "expected_priority": "P2"
    },
    {
        "input": "The search is too slow, needs optimization",
        "expected_type": "performance",
        "expected_priority": "P2"  # Default priority
    }
]

def test_user_prompt_submit(prompt_text):
    """Test the UserPromptSubmit hook with given prompt"""
    
    # Prepare hook input data
    hook_data = {
        "userPrompt": prompt_text,  # Changed from "prompt" to "userPrompt"
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    # Set up environment
    project_root = Path(__file__).parent.parent.parent
    env = os.environ.copy()
    env['CLAUDE_PROJECT_DIR'] = str(project_root)
    env['DOOM_ENABLED'] = 'true'
    
    # Run the hook
    hook_path = project_root / '.claude' / 'hooks' / 'user-prompt-submit.py'
    
    try:
        result = subprocess.run(
            ['python3', str(hook_path)],
            input=json.dumps(hook_data),
            capture_output=True,
            text=True,
            env=env,
            cwd=str(project_root)
        )
        
        # Check if hook executed successfully
        if result.returncode != 0:
            print(f"❌ Hook failed with code {result.returncode}")
            print(f"STDERR: {result.stderr}")
            return {"success": False, "error": f"Exit code {result.returncode}"}
            
        # Parse JSON output from hook
        try:
            response = json.loads(result.stdout)
            enhanced_prompt = response.get('userPrompt', '')
            
            # Extract task metadata from enhanced prompt
            detected_type = None
            detected_priority = None
            
            # Look for the metadata section in the enhanced prompt
            lines = enhanced_prompt.split('\n')
            for line in lines:
                if "Task Type:" in line:
                    detected_type = line.split(":")[-1].strip()
                elif "Priority:" in line and "Priority Level:" not in line:
                    detected_priority = line.split(":")[-1].strip()
                elif "Detected Type:" in line:
                    detected_type = line.split(":")[-1].strip()
                elif "Priority Level:" in line:
                    detected_priority = line.split(":")[-1].strip()
            
            return {
                "success": True,
                "detected_type": detected_type,
                "detected_priority": detected_priority,
                "output": result.stdout,
                "response": response
            }
        except json.JSONDecodeError:
            print(f"Failed to parse JSON output: {result.stdout[:500]}")
            print(f"STDERR: {result.stderr}")
            return {
                "success": False,
                "error": "Invalid JSON output",
                "output": result.stdout,
                "stderr": result.stderr
            }
        
    except Exception as e:
        print(f"❌ Error running hook: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Run all test scenarios"""
    print("🧪 Testing UserPromptSubmit Hook\n")
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(TEST_PROMPTS, 1):
        print(f"Test {i}: {test['input'][:50]}...")
        
        result = test_user_prompt_submit(test['input'])
        
        if not result.get("success"):
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            failed += 1
            continue
        
        # Verify detection
        type_match = result.get("detected_type") == test["expected_type"]
        priority_match = result.get("detected_priority") == test["expected_priority"]
        
        if type_match and priority_match:
            print(f"✅ Passed - Type: {result['detected_type']}, Priority: {result['detected_priority']}")
            passed += 1
        else:
            print(f"❌ Failed - Expected: {test['expected_type']}/{test['expected_priority']}, ")
            print(f"   Got: {result['detected_type']}/{result['detected_priority']}")
            failed += 1
        
        print()
    
    # Summary
    print(f"\n📊 Results: {passed} passed, {failed} failed out of {len(TEST_PROMPTS)} tests")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())