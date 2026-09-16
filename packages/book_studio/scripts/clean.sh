#!/usr/bin/env bash
set -euo pipefail

echo "[*] Cleaning Python cache directories..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +

echo "[*] Cleaning LaTeX temporary compilation artifacts..."
find . -type f -name "texput.*" -delete
find . -type f -name "*.aux" -delete
find . -type f -name "*.log" -delete

echo "[*] Workspace clean."
