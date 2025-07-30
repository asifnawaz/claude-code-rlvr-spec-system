#!/usr/bin/env python3
"""
Kiro Prompt Template Validator
Ensures prompts follow the structured Kiro format
"""

import re
from typing import Dict, List, Tuple

class KiroPromptValidator:
    """Validates and scores Kiro prompt structure compliance"""
    
    REQUIRED_FIELDS = [
        '$GOAL',
        '$CONTEXT',
        '$INPUT',
        '$CONSTRAINTS',
        '$OUTPUT_EXPECTED',
        '$ACCEPTANCE_CRITERIA',
        '$DEADLINE'
    ]
    
    def __init__(self):
        self.validation_results = {}
        self.score = 0
        self.max_score = 10
    
    def validate(self, prompt: str) -> Tuple[bool, Dict[str, any]]:
        """
        Validate a prompt against Kiro template
        Returns: (is_valid, results_dict)
        """
        self.validation_results = {
            'missing_fields': [],
            'present_fields': [],
            'score': 0,
            'feedback': [],
            'is_valid': False
        }
        
        # Check for each required field
        for field in self.REQUIRED_FIELDS:
            pattern = re.escape(field) + r':\s*(.+?)(?=\$|$)'
            match = re.search(pattern, prompt, re.MULTILINE | re.DOTALL)
            
            if match:
                content = match.group(1).strip()
                if content:
                    self.validation_results['present_fields'].append(field)
                else:
                    self.validation_results['missing_fields'].append(field)
                    self.validation_results['feedback'].append(f"{field} is present but empty")
            else:
                self.validation_results['missing_fields'].append(field)
                self.validation_results['feedback'].append(f"{field} is missing from prompt")
        
        # Calculate score
        self.calculate_score()
        
        # Determine if valid
        self.validation_results['is_valid'] = len(self.validation_results['missing_fields']) == 0
        
        return self.validation_results['is_valid'], self.validation_results
    
    def calculate_score(self):
        """Calculate compliance score"""
        # Base score from field presence
        present_count = len(self.validation_results['present_fields'])
        total_fields = len(self.REQUIRED_FIELDS)
        
        # Each field is worth up to 1 point
        field_score = (present_count / total_fields) * 7
        
        # Bonus points for specific criteria
        bonus_score = 0
        
        # Check if acceptance criteria has checklist items
        if '$ACCEPTANCE_CRITERIA' in self.validation_results['present_fields']:
            bonus_score += 1
        
        # Check if deadline follows ISO format
        if '$DEADLINE' in self.validation_results['present_fields']:
            bonus_score += 1
        
        # Check if goal is concise (single line)
        if '$GOAL' in self.validation_results['present_fields']:
            bonus_score += 1
        
        self.score = round(field_score + bonus_score, 2)
        self.validation_results['score'] = self.score
        
        # Add feedback based on score
        if self.score >= 9:
            self.validation_results['feedback'].append("Excellent Kiro prompt compliance!")
        elif self.score >= 7:
            self.validation_results['feedback'].append("Good prompt structure, minor improvements possible")
        elif self.score >= 5:
            self.validation_results['feedback'].append("Prompt needs improvement to meet Kiro standards")
        else:
            self.validation_results['feedback'].append("Poor prompt structure - please follow Kiro template")
    
    def format_template(self) -> str:
        """Return the Kiro prompt template"""
        return """# Kiro Prompt Template
$GOAL: <single objective sentence>
$CONTEXT: <brief background>
$INPUT: <relevant artifacts / code refs>
$CONSTRAINTS: <edge cases, security limits>
$OUTPUT_EXPECTED: <deliverable definition>
$ACCEPTANCE_CRITERIA: <checklist>
$DEADLINE: <ISO 8601>"""

    def enhance_prompt(self, original_prompt: str) -> str:
        """Enhance a non-compliant prompt with Kiro structure"""
        if self.validation_results['is_valid']:
            return original_prompt
        
        enhanced = "# Kiro Prompt\n"
        
        # Try to extract information from original prompt
        lines = original_prompt.strip().split('\n')
        first_line = lines[0] if lines else "Task to complete"
        rest = '\n'.join(lines[1:]) if len(lines) > 1 else ""
        
        # Build structured prompt
        enhanced += f"$GOAL: {first_line}\n"
        enhanced += f"$CONTEXT: {rest if rest else 'Please provide context'}\n"
        enhanced += "$INPUT: <Please specify relevant files/data>\n"
        enhanced += "$CONSTRAINTS: <Please specify any limitations>\n"
        enhanced += "$OUTPUT_EXPECTED: <Please define expected deliverables>\n"
        enhanced += "$ACCEPTANCE_CRITERIA:\n"
        enhanced += "  - [ ] Requirement 1\n"
        enhanced += "  - [ ] Requirement 2\n"
        enhanced += "$DEADLINE: <Please specify deadline>\n"
        
        return enhanced


def main():
    """CLI interface for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: validate-prompt-structure.py <prompt_file>")
        print("\nKiro Prompt Template:")
        validator = KiroPromptValidator()
        print(validator.format_template())
        sys.exit(1)
    
    # Read prompt from file
    with open(sys.argv[1], 'r') as f:
        prompt = f.read()
    
    # Validate
    validator = KiroPromptValidator()
    is_valid, results = validator.validate(prompt)
    
    # Output results
    print(f"Valid: {is_valid}")
    print(f"Score: {results['score']}/10")
    print(f"Present fields: {', '.join(results['present_fields'])}")
    if results['missing_fields']:
        print(f"Missing fields: {', '.join(results['missing_fields'])}")
    print("\nFeedback:")
    for feedback in results['feedback']:
        print(f"  - {feedback}")
    
    # Show enhanced version if not valid
    if not is_valid:
        print("\nEnhanced prompt:")
        print(validator.enhance_prompt(prompt))


if __name__ == '__main__':
    main()