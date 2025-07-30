#!/usr/bin/env python3
"""
Test runner for DOOM-RLVR system
Runs all tests and generates coverage report
"""

import sys
import unittest
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_all_tests():
    """Discover and run all tests"""
    # Get the directory containing this script
    test_dir = Path(__file__).parent
    
    # Discover all test files
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on success
    return 0 if result.wasSuccessful() else 1


def run_with_coverage():
    """Run tests with coverage reporting"""
    try:
        import coverage
    except ImportError:
        print("Coverage module not installed. Running tests without coverage.")
        print("Install with: pip install coverage")
        return run_all_tests()
    
    # Initialize coverage
    cov = coverage.Coverage(source=['.'])
    cov.start()
    
    # Run tests
    exit_code = run_all_tests()
    
    # Stop coverage and generate report
    cov.stop()
    cov.save()
    
    print("\n" + "="*70)
    print("Coverage Report:")
    print("="*70)
    cov.report()
    
    # Generate HTML report
    html_dir = Path(__file__).parent / 'coverage_html'
    cov.html_report(directory=str(html_dir))
    print(f"\nDetailed HTML coverage report generated in: {html_dir}")
    
    return exit_code


if __name__ == '__main__':
    # Check for coverage flag
    if '--coverage' in sys.argv:
        exit_code = run_with_coverage()
    else:
        exit_code = run_all_tests()
    
    sys.exit(exit_code)