#!/bin/bash

# Adversarial Check Script for the Agent
# Runs extremely strict static analysis to identify potential flaws

set -e

echo "=== Running Adversarial Static Analysis Check ==="

# We leverage mypy with highly strict configurations to catch subtle type inconsistencies
# Since the Makefile already defines a lint target, we can extend it or run mypy directly on the whole project

echo "Running strict mypy over the current environment..."
python3 -m mypy --strict app_spatial_compiler/src app_spatial_compiler/tests tests/ cli.py || {
    echo "Adversarial check found potential issues via mypy --strict."
    exit 1
}

echo "=== Adversarial Check Completed Successfully ==="
