#!/usr/bin/env python3
"""
Compatibility wrapper for rlvr-evaluate.py
This file allows imports using the old underscore naming convention.
"""

import sys
from pathlib import Path

# Add the scripts directory to the path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# Import from the kebab-case file
import importlib.util
spec = importlib.util.spec_from_file_location("rlvr_evaluate_module", 
                                              scripts_dir.parent.parent / "kiro" / "scripts" / "rlvr-evaluate.py")
rlvr_evaluate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rlvr_evaluate_module)

# Export all symbols from the module
for name in dir(rlvr_evaluate_module):
    if not name.startswith('_'):
        globals()[name] = getattr(rlvr_evaluate_module, name)