#!/usr/bin/env bash
set -uo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: ./scripts/run_pipeline.sh <path_to_pdf> [--skip-ocr]"
    exit 1
fi

LOG_FILE="docs/execution.log"
echo "[*] Initializing pipeline execution. Full logs routed to $LOG_FILE"

export VLLM_WSL2_ENABLE_PIN_MEMORY=1

# Run in offline mode to prevent HF Hub '429 Too Many Requests' from crashing vLLM during startup.
export HF_HUB_OFFLINE=1
export VLLM_USE_V1=0
export VLLM_USE_FLASHINFER_SAMPLER=0

echo "[*] Starting local vLLM inference server on RTX 3050 (Isolated Env)..."
# The --limit-mm-per-prompt parameter requires a strict JSON dictionary payload.
./infra/vllm_env/bin/vllm serve "datalab-to/surya-ocr-2" \
    --gpu-memory-utilization 0.35 \
    --max-model-len 4096 \
    --max-num-seqs 1 \
    --limit-mm-per-prompt '{"image": 1, "video": 0}' \
    --mm-processor-kwargs '{"max_pixels": 313600}' \
    --enforce-eager &
VLLM_PID=$!

# Use pkill -P to aggressively terminate all multiprocess workers (which hold PyTorch CUDA context) to free GPU memory
trap "pkill -9 -P \$VLLM_PID 2>/dev/null; kill -9 \$VLLM_PID 2>/dev/null" EXIT

echo "[*] Waiting for Vision-Language Model to load into VRAM..."
TIMEOUT=300
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

poetry run python -m book_studio.main run-pipeline "$@" 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=$?

if [ "$EXIT_CODE" = "137" ]; then
    echo "CRITICAL ERROR: Process killed by OS (Exit Code 137). WSL OOM." | tee -a "$LOG_FILE"
elif [ "$EXIT_CODE" != "0" ]; then
    echo "ERROR: Pipeline failed with exit code $EXIT_CODE." | tee -a "$LOG_FILE"
else
    echo "[*] Pipeline completed successfully." | tee -a "$LOG_FILE"
fi

exit $EXIT_CODE
