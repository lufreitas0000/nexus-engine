#!/bin/sh
# Usage: ./skills/adversarial_check.sh
# Detects silent test deletions, type-check escapes, and workspace mutations.
set -eu

echo "=== [Adversarial Gate 1] Checking for Type Escapes in Diff ==="
if git diff HEAD | grep -E "^\+.*(# type: ignore|Any\b)" ; then
    echo "[WARN] New '# type: ignore' or 'Any' detected in diff. Verify strict necessity."
fi

echo "=== [Adversarial Gate 2] Checking for Deleted Test Assertions ==="
REMOVED_ASSERTS=$(git diff HEAD -- "**/tests/**" | grep -cE "^\-[[:space:]]*assert " || true)
ADDED_ASSERTS=$(git diff HEAD -- "**/tests/**" | grep -cE "^\+[[:space:]]*assert " || true)
echo "Assertions removed: ${REMOVED_ASSERTS} | Assertions added: ${ADDED_ASSERTS}"
if [ "$REMOVED_ASSERTS" -gt "$ADDED_ASSERTS" ]; then
    echo "[FAIL] Net reduction in test assertions detected (${REMOVED_ASSERTS} removed vs ${ADDED_ASSERTS} added). Inspect diff for test weakening."
    exit 1
fi

echo "=== [Adversarial Gate 3] Checking for Leftover Duplicate Directories ==="
FOUND_LEGACY=$(find packages -maxdepth 3 -type d \( -name "test" -o -name "adapters" -o -name "ports" -o -name "application" -o -name "infrastructure" \) || true)
if [ -n "$FOUND_LEGACY" ]; then
    echo "[WARN] Legacy non-standardized directories still present:"
    echo "$FOUND_LEGACY"
fi

echo "[OK] Adversarial static checks complete."
