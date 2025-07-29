#!/bin/bash
# Generate comprehensive task report

set -euo pipefail

# Display help
if [ "$1" == "--help" ] 2>/dev/null; then
    echo "Usage: /kiro-report [--json] [--last N]"
    echo ""
    echo "Generate a comprehensive report of task activities."
    echo ""
    echo "Options:"
    echo "  --json    Output in JSON format"
    echo "  --last N  Show only last N tasks (default: all)"
    echo "  --help    Show this help message"
    exit 0
fi

# Parse arguments
FORMAT="text"
LAST_N=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            FORMAT="json"
            shift
            ;;
        --last)
            LAST_N="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

SCOREBOARD_DIR="$CLAUDE_PROJECT_DIR/.claude/scoreboard"
TASKS_DIR="$CLAUDE_PROJECT_DIR/.claude/tasks"

echo "=== Kiro-RLVR Task Report ==="
echo "Generated: $(date)"
echo ""

# Task Summary
echo "## Task Summary"
echo ""

# Count tasks by status
if [ -d "$TASKS_DIR" ]; then
    TOTAL_TASKS=$(find "$TASKS_DIR" -name "metadata.json" | wc -l)
    echo "Total Tasks: $TOTAL_TASKS"
    
    # Count by type
    echo ""
    echo "By Type:"
    find "$TASKS_DIR" -name "metadata.json" -exec jq -r '.task_type' {} \; 2>/dev/null | sort | uniq -c | while read count type; do
        echo "  - $type: $count"
    done
    
    # Count by priority
    echo ""
    echo "By Priority:"
    find "$TASKS_DIR" -name "metadata.json" -exec jq -r '.priority' {} \; 2>/dev/null | sort | uniq -c | while read count priority; do
        echo "  - $priority: $count"
    done
else
    echo "No tasks found"
fi

# Agent Performance
echo ""
echo "## Agent Performance"
echo ""

# Calculate agent statistics
for agent_file in "$SCOREBOARD_DIR"/*_performance.jsonl; do
    if [ -f "$agent_file" ]; then
        agent_name=$(basename "$agent_file" _performance.jsonl)
        
        # Get performance stats
        if [ -s "$agent_file" ]; then
            task_count=$(wc -l < "$agent_file")
            avg_reward=$(jq -s 'add/length | .*100 | round/100' < "$agent_file" 2>/dev/null || echo "N/A")
            last_reward=$(tail -1 "$agent_file" | jq -r '.reward' 2>/dev/null || echo "N/A")
            
            echo "$agent_name:"
            echo "  Tasks completed: $task_count"
            echo "  Average reward: $avg_reward"
            echo "  Last reward: $last_reward"
            echo ""
        fi
    fi
done

# Recent Activity
echo "## Recent Activity"
echo ""

if [ -f "$SCOREBOARD_DIR/events.jsonl" ]; then
    if [ -n "$LAST_N" ]; then
        EVENTS=$(tail -"$LAST_N" "$SCOREBOARD_DIR/events.jsonl")
    else
        EVENTS=$(tail -20 "$SCOREBOARD_DIR/events.jsonl")
    fi
    
    echo "Recent Events:"
    echo "$EVENTS" | while read -r line; do
        if [ -n "$line" ]; then
            timestamp=$(echo "$line" | jq -r '.timestamp' 2>/dev/null || echo "unknown")
            event=$(echo "$line" | jq -r '.event' 2>/dev/null || echo "unknown")
            task_id=$(echo "$line" | jq -r '.task_id' 2>/dev/null || echo "")
            agent=$(echo "$line" | jq -r '.agent_name' 2>/dev/null || echo "")
            
            echo "  - $timestamp: $event"
            [ -n "$task_id" ] && echo "    Task: $task_id"
            [ -n "$agent" ] && echo "    Agent: $agent"
        fi
    done
else
    echo "No events recorded"
fi

# Quality Metrics
echo ""
echo "## Quality Metrics"
echo ""

if [ -f "$SCOREBOARD_DIR/rlvr.jsonl" ]; then
    # Calculate average component scores
    echo "Average Component Scores:"
    
    components=("test_coverage_delta" "lint_score" "security_scan_score" "code_complexity_delta" "ci_status" "review_readiness")
    
    for component in "${components[@]}"; do
        avg=$(jq -s "map(.components.$component // 0) | add/length | .*100 | round/100" < "$SCOREBOARD_DIR/rlvr.jsonl" 2>/dev/null || echo "N/A")
        echo "  - ${component//_/ }: $avg"
    done
else
    echo "No evaluation data available"
fi

# Improvement Areas
echo ""
echo "## Improvement Areas"
echo ""

if [ -d "$CLAUDE_PROJECT_DIR/.claude/feedback" ]; then
    # Aggregate feedback
    echo "Common feedback themes:"
    
    find "$CLAUDE_PROJECT_DIR/.claude/feedback" -name "*_feedback.jsonl" -exec cat {} \; 2>/dev/null | \
        jq -r '.improvements[].area' 2>/dev/null | \
        sort | uniq -c | sort -rn | head -5 | while read count area; do
        echo "  - $area: $count occurrences"
    done
else
    echo "No feedback data available"
fi

# Prompt Optimization Effectiveness
echo ""
echo "## Prompt Optimization"
echo ""

if [ -f "$SCOREBOARD_DIR/optimization_effectiveness.jsonl" ]; then
    opt_count=$(wc -l < "$SCOREBOARD_DIR/optimization_effectiveness.jsonl")
    avg_reward=$(jq -s 'map(select(.optimized == true) | .reward) | add/length | .*100 | round/100' < "$SCOREBOARD_DIR/optimization_effectiveness.jsonl" 2>/dev/null || echo "N/A")
    
    echo "Optimized tasks: $opt_count"
    echo "Average reward for optimized tasks: $avg_reward"
else
    echo "No optimization data available"
fi

echo ""
echo "=== End of Report ==="