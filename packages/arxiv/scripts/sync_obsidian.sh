#!/usr/bin/env bash
# Synchronizes the generated graph exports with the remote digital garden.

VAULT_DIR="${1:-./vault}"
TIMESTAMP=$(date +"%Y-%m-%dT%H:%M:%S")

if [ ! -d "$VAULT_DIR/.git" ]; then
    echo "[ERROR] Target directory is not a Git repository."
    exit 1
fi

cd "$VAULT_DIR" || exit 1

# Check for modifications
if [[ -z $(git status -s) ]]; then
    echo "[INFO] No new literature notes to synchronize."
    exit 0
fi

echo "[INFO] Synchronizing digital garden..."
git add .
git commit -m "Auto-ingest: literature and graph state update at $TIMESTAMP"
git push origin main

echo "[INFO] Obsidian synchronization complete."
