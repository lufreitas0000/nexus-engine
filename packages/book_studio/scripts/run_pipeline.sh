#!/usr/bin/env bash
set -uo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: ./scripts/run_pipeline.sh <path_to_pdf> [--skip-ocr]"
    exit 1
fi

LOG_FILE="docs/execution.log"
echo "[*] Initializing pipeline execution. Full logs routed to $LOG_FILE"

echo "[*] Starting local vLLM inference server on RTX 3050 (Isolated Env)..."
./infra/vllm_env/bin/vllm serve "datalab-to/surya-ocr-2" \
    --gpu-memory-utilization 0.90 \
    --max-model-len 4096 \
    > docs/vllm.log 2>&1 &
VLLM_PID=$!

trap "kill \$VLLM_PID 2>/dev/null" EXIT

echo "[*] Waiting for Vision-Language Model to load into VRAM..."
TIMEOUT=150
while ! curl -s http://127.0.0.1:8000/v1/models > /dev/null 2>&1; do
    sleep 5
    TIMEOUT=$((TIMEOUT-5))
    if [ $TIMEOUT -le 0 ]; then
        echo "ERROR: vLLM server failed to start. Check docs/vllm.log" | tee -a "$LOG_FILE"
        exit 1
    fi
done
echo "[*] VLM server healthy and bound to port 8000."

export SURYA_INFERENCE_URL="http://127.0.0.1:8000/v1"
export SURYA_INFERENCE_AUTOSTART="False"
export CUDA_VISIBLE_DEVICES="0"

poetry run python src/main.py run-pipeline "$@" 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 137 ]; then
    echo "CRITICAL ERROR: Process killed by OS (Exit Code 137). WSL OOM." | tee -a "$LOG_FILE"
elif [ $EXIT_CODE -ne 0 ]; then
    echo "ERROR: Pipeline failed with exit code $EXIT_CODE." | tee -a "$LOG_FILE"
else
    echo "[*] Pipeline completed successfully." | tee -a "$LOG_FILE"
fi

exit $EXIT_CODE
