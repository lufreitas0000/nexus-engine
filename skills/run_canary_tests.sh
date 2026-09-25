#!/bin/sh
# Usage: ./skills/run_canary_tests.sh [package_name]
# Runs unmocked real-life micro-scenarios.
set -eu

PKG="${1:-}"
if [ -n "$PKG" ]; then
    CANARY_PATH="packages/${PKG}/tests/canary"
else
    CANARY_PATH="tests/canary"
fi

if [ ! -d "$CANARY_PATH" ]; then
    echo "[FAIL] Canary test directory ${CANARY_PATH} is missing. Create real-life micro-tests first."
    exit 1
fi

echo "=== Running Real-Life Canary Suite: ${CANARY_PATH} ==="
uv run pytest "$CANARY_PATH" -q --tb=short -o addopts=""
