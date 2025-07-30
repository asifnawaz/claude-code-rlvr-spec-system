#!/usr/bin/env python3
"""
Script to rename Python files from snake_case to kebab-case
and update all references in the codebase.
"""

import os
import re
import shutil
from pathlib import Path

# Mapping of old names to new names
RENAME_MAP = {
    'kiro_cli.py': 'kiro-cli.py',
    'kiro_cli_simple.py': 'kiro-cli-simple.py',
    'rlvr_evaluate.py': 'rlvr-evaluate.py',
    'tier_updater.py': 'tier-updater.py',
    'manual_assign.py': 'manual-assign.py',
}

# Files that might contain references to update
SEARCH_PATTERNS = [
    '**/*.py',
    '**/*.md',
    '**/*.json',
    '**/UserPromptSubmit',
    '**/PreToolUse',
    '**/PostToolUse',
    '**/Stop',
]

def get_module_name(filename):
    """Convert filename to module name for imports"""
    return filename.replace('.py', '').replace('-', '_')

def update_references(file_path, updates):
    """Update references in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_name, new_name in updates.items():
            # Update direct file references
            content = content.replace(old_name, new_name)
            
            # Update module imports (from kiro_cli import ...)
            old_module = get_module_name(old_name)
            new_module = get_module_name(new_name)
            
            # Various import patterns
            patterns = [
                (f'from {old_module} import', f'from {new_module} import'),
                (f'import {old_module}', f'import {new_module}'),
                (f'{old_module}.', f'{new_module}.'),
            ]
            
            for old_pattern, new_pattern in patterns:
                content = content.replace(old_pattern, new_pattern)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False
    
    return False

def main():
    """Main execution"""
    project_root = Path(__file__).resolve().parent.parent.parent
    scripts_dir = project_root / '.claude' / 'scripts'
    
    print("Kiro-RLVR Naming Convention Migration")
    print("=" * 40)
    
    # Step 1: Rename files
    print("\n1. Renaming script files:")
    renamed_files = {}
    
    for old_name, new_name in RENAME_MAP.items():
        old_path = scripts_dir / old_name
        new_path = scripts_dir / new_name
        
        if old_path.exists():
            if new_path.exists():
                print(f"  ⚠️  {new_name} already exists, skipping")
                continue
                
            try:
                shutil.move(str(old_path), str(new_path))
                print(f"  ✓ {old_name} → {new_name}")
                renamed_files[old_name] = new_name
            except Exception as e:
                print(f"  ✗ Failed to rename {old_name}: {e}")
        else:
            print(f"  - {old_name} not found, skipping")
    
    # Step 2: Update references
    print("\n2. Updating references in codebase:")
    updated_files = []
    
    for pattern in SEARCH_PATTERNS:
        for file_path in project_root.glob(pattern):
            # Skip this script and backup files
            if file_path.name == 'rename-to-kebab-case.py' or file_path.suffix == '.bak':
                continue
                
            if file_path.is_file() and update_references(file_path, renamed_files):
                updated_files.append(file_path)
                print(f"  ✓ Updated {file_path.relative_to(project_root)}")
    
    # Step 3: Summary
    print("\n3. Summary:")
    print(f"  - Renamed {len(renamed_files)} files")
    print(f"  - Updated {len(updated_files)} files with references")
    
    # Step 4: Next steps
    print("\n4. Next steps:")
    print("  - Test that all hooks and scripts still work")
    print("  - Update any documentation not caught by the script")
    print("  - Consider updating import statements to use the new module names")
    
    # Create a rollback script
    if renamed_files:
        rollback_content = "#!/bin/bash\n# Rollback script\n"
        for old_name, new_name in renamed_files.items():
            rollback_content += f"mv .claude/scripts/{new_name} .claude/scripts/{old_name}\n"
        
        rollback_path = project_root / '.claude' / 'scripts' / 'rollback-rename.sh'
        with open(rollback_path, 'w') as f:
            f.write(rollback_content)
        os.chmod(rollback_path, 0o755)
        print(f"\n  ℹ️  Rollback script created at: {rollback_path.relative_to(project_root)}")

if __name__ == "__main__":
    main()