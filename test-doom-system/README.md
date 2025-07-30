# DOOM-RLVR External Test Suite

This directory contains external tests that simulate real-world usage of the DOOM-RLVR system from outside the `.claude/` directory.

## Purpose

These tests verify that:
1. Hooks execute correctly when triggered by Claude Code
2. Scripts can be called from external contexts
3. The system works end-to-end in realistic scenarios
4. Environment variables and paths are correctly configured

## Test Structure

```
test-doom-system/
├── README.md
├── test-hooks/           # Hook execution tests
├── test-scenarios/       # Real-world task scenarios
├── test-cli/            # CLI command tests
├── test-integration/    # Full system integration tests
└── run-all-tests.sh     # Main test runner
```

## Running Tests

### Run all external tests:
```bash
cd test-doom-system
./run-all-tests.sh
```

### Run specific test category:
```bash
./test-hooks/run-hook-tests.sh
./test-scenarios/run-scenario-tests.sh
./test-cli/run-cli-tests.sh
```

## Test Categories

### 1. Hook Tests (`test-hooks/`)
- Simulates Claude Code triggering hooks
- Tests hook data flow
- Verifies error handling

### 2. Scenario Tests (`test-scenarios/`)
- Real-world task examples
- End-to-end workflow validation
- Performance testing

### 3. CLI Tests (`test-cli/`)
- Command-line interface testing
- Argument parsing
- Output validation

### 4. Integration Tests (`test-integration/`)
- Complete system workflows
- Multi-component interactions
- Edge case handling