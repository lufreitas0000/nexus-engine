#!/bin/bash

# delegate_task.sh
#
# A mock/interface script demonstrating how an Orchestrator agent can delegate
# specific tasks to a lighter model (e.g., Gemini Flash) using an agent CLI.
# This assumes an agent CLI like 'agy' (Antigravity) or similar is installed.

set -e

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 \"<task_description>\" [--file <target_file>]"
    echo "Example: $0 \"Fix linting errors in router module\""
    exit 1
fi

TASK_DESCRIPTION=$1
shift

TARGET_FILE=""
if [ "$1" == "--file" ]; then
    TARGET_FILE=$2
    shift 2
fi

# We explicitly select a lightweight, fast model for sub-tasks to save costs/tokens
MODEL="gemini-1.5-flash"

echo "========================================="
echo "Delegating task to Light Model ($MODEL)..."
echo "Task: $TASK_DESCRIPTION"
if [ -n "$TARGET_FILE" ]; then
    echo "Target File: $TARGET_FILE"
fi
echo "========================================="

# Construct the CLI command (Mock implementation)
# In a real scenario, this would call the actual agentic CLI, for example:
# agy run --model $MODEL --prompt "$TASK_DESCRIPTION" ${TARGET_FILE:+--context "$TARGET_FILE"}

echo "[EXEC] Running command: agy run --model $MODEL --prompt \"$TASK_DESCRIPTION\""

# Mock success output for demonstration
echo "[INFO] Task completed successfully by delegated model."
exit 0
