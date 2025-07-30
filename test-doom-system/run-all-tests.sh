#!/bin/bash
# Run all DOOM-RLVR external tests

echo "🧪 DOOM-RLVR External Test Suite"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall results
TOTAL_PASSED=0
TOTAL_FAILED=0

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to run a test category
run_test_category() {
    local category=$1
    local test_script=$2
    
    echo -e "\n${YELLOW}Running $category Tests${NC}"
    echo "----------------------------------------"
    
    if [ -f "$test_script" ]; then
        python3 "$test_script"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ $category tests passed${NC}"
            ((TOTAL_PASSED++))
        else
            echo -e "${RED}❌ $category tests failed${NC}"
            ((TOTAL_FAILED++))
        fi
    else
        echo -e "${RED}❌ Test script not found: $test_script${NC}"
        ((TOTAL_FAILED++))
    fi
}

# Run each test category
echo "Starting test execution..."

# Hook Tests
run_test_category "UserPromptSubmit Hook" "test-hooks/test-user-prompt-submit.py"
run_test_category "Stop Hook" "test-hooks/test-stop-hook.py"

# Scenario Tests
run_test_category "Bugfix Scenario" "test-scenarios/bugfix-scenario.py"
run_test_category "Feature Scenario" "test-scenarios/feature-scenario.py"

# CLI Tests
run_test_category "CLI Commands" "test-cli/test-doom-cli.py"

# Summary
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}Test Summary${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "Total test categories: $((TOTAL_PASSED + TOTAL_FAILED))"
echo -e "${GREEN}Passed: $TOTAL_PASSED${NC}"
echo -e "${RED}Failed: $TOTAL_FAILED${NC}"

if [ $TOTAL_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed${NC}"
    exit 1
fi