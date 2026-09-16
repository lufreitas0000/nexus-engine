#!/usr/bin/env bash
set -uo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: ./scripts/run_pipeline.sh <path_to_pdf> [--skip-ocr]"
    exit 1
fi

LOG_FILE="docs/execution.log"
echo "[*] Initializing pipeline execution. Full logs routed to $LOG_FILE"

# Execute Python state-machine, redirecting stdout and stderr to tee
# This ensures that even if the terminal drops, the exact crash reason is written to disk.
poetry run python src/main.py run-pipeline "$@" 2>&1 | tee "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 137 ]; then
    echo "CRITICAL ERROR: Process was killed by the OS (Exit Code 137). This is a guaranteed Out-Of-Memory (OOM) kill from the WSL kernel." | tee -a "$LOG_FILE"
elif [ $EXIT_CODE -ne 0 ]; then
    echo "ERROR: Pipeline failed with exit code $EXIT_CODE." | tee -a "$LOG_FILE"
else
    echo "[*] Pipeline completed successfully." | tee -a "$LOG_FILE"
fi

exit $EXIT_CODE
