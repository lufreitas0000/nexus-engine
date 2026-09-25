#!/bin/sh
# Usage: ./skills/run_tdd_cycle.sh [package_path_or_test_Target]
# Token-efficient test, lint, and typecheck runner.
set -eu

TARGET="${1:-packages/}"

echo "=== [1/3] Ruff Lint Check ==="
uv run ruff check "$TARGET" --quiet

echo "=== [2/3] Mypy Type Check ==="
uv run mypy "$TARGET" --no-error-summary --hide-error-context

echo "=== [3/3] Pytest Suite (Compact Output) ==="
uv run pytest "$TARGET" -q --tb=short --maxfail=3
