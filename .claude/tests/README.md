# DOOM-RLVR Test Suite

This directory contains the test suite for the DOOM-RLVR (Reinforcement Learning with Variable Rewards) system.

## Test Structure

- `test_doom_rlvr.py` - Unit tests for core RLVR functionality
  - RLVR Evaluator tests
  - Task detection tests
  - Agent selection tests
  - Template compliance tests
  - Tier promotion/demotion tests

- `test_integration.py` - Integration tests
  - End-to-end task flow tests
  - Hook integration tests
  - Error handling tests
  - Performance and scale tests

- `run_tests.py` - Test runner script

## Running Tests

### Run all tests:
```bash
python3 .claude/tests/run_tests.py
```

### Run with coverage report:
```bash
python3 .claude/tests/run_tests.py --coverage
```

### Run specific test file:
```bash
python3 -m unittest .claude/tests/test_doom_rlvr.py -v
```

### Run specific test class:
```bash
python3 -m unittest .claude.tests.test_doom_rlvr.TestRLVREvaluator -v
```

### Run specific test method:
```bash
python3 -m unittest .claude.tests.test_doom_rlvr.TestRLVREvaluator.test_initialization -v
```

## Test Categories

### 1. Unit Tests (`test_doom_rlvr.py`)

#### RLVR Evaluator Tests
- Configuration loading
- Reward calculation with various component scores
- Individual component evaluation methods

#### Task Detection Tests
- Automatic task type detection from natural language
- Priority level detection
- Edge case handling

#### Agent Selection Tests
- Best agent selection based on specialization
- Tier-based selection (principal > senior > junior)
- Performance-based selection

#### Template Compliance Tests
- DOOM template field validation
- Acceptance criteria completion tracking
- Score calculation

#### Tier Management Tests
- Promotion threshold validation
- Demotion threshold validation
- Suspension logic

### 2. Integration Tests (`test_integration.py`)

#### End-to-End Flow Tests
- Complete task lifecycle from submission to evaluation
- Task metadata creation and storage
- Evaluation result persistence

#### Hook Integration Tests
- Data flow between hooks
- Hook execution order
- Error propagation

#### Error Handling Tests
- Missing agent fallback
- Invalid task format handling
- Evaluation failure recovery
- Graceful degradation

#### Performance Tests
- Concurrent task handling
- Large scoreboard processing
- Scalability validation

## Test Data

Tests use temporary directories and mock data to ensure isolation. No external dependencies or network calls are made during testing.

## Coverage Goals

Target coverage: 80%+ for core functionality
- RLVR evaluation logic: 90%+
- Task detection: 85%+
- Agent selection: 85%+
- Error handling: 80%+

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all existing tests pass
3. Add integration tests for new hooks
4. Update this README with new test descriptions

## Debugging Tests

To debug failing tests:
1. Run with verbose output: `-v` or `-vv`
2. Use print statements in test methods
3. Check temporary test directories in `/tmp/`
4. Review mock call assertions

## CI/CD Integration

These tests are designed to run in CI/CD pipelines:
- No external dependencies required
- No network calls
- Deterministic results
- Fast execution (< 30 seconds total)