#!/bin/bash

# TDD Cycle Script for the Agent
# Runs linting and tests using the project's existing Makefile infrastructure

set -e

echo "=== Running TDD Cycle ==="

echo "[1/2] Running strict static analysis (lint)..."
make lint

echo "[2/2] Running synthetic manifold assertions (tests)..."
make test

echo "=== TDD Cycle Completed Successfully ==="
