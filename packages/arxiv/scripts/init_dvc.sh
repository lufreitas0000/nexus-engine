#!/usr/bin/env bash
if [ ! -d ".dvc" ]; then
    dvc init
fi
mkdir -p ingestion_engine/artifacts
dvc add ingestion_engine/artifacts
git add ingestion_engine/artifacts.dvc .gitignore
git commit -m "chore: track ingestion artifacts via DVC"
