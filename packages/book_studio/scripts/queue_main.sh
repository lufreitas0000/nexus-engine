#!/bin/bash
# Ensures we launch the big pipeline detached
nohup ./scripts/run_pipeline.sh data/01_raw/gordon_baym_qm.pdf > docs/execution_gordon.log 2>&1 &
echo "[*] Main pipeline queued in background. PID: $!"
