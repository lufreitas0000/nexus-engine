# 2. Server definition and worker script (server.py)
import gc
import os
import re
import subprocess
import time
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import uvicorn

app = FastAPI(title="Colab Compute Server")


class ComputeRequest(BaseModel):
    task_id: str
    task_type: str
    payload: Dict[str, Any]


class ComputeResponse(BaseModel):
    task_id: str
    status: str
    result: Dict[str, Any]
    error: str | None = None


@app.post("/api/v1/compute", response_model=ComputeResponse)
async def process_task(request: ComputeRequest) -> ComputeResponse:
    try:
        # Task routing based on payload specification
        if request.task_type == "embedding_extraction":
            # Placeholder for heavy batch embedding model
            result_data = {
                "embeddings": [[0.0] * 768],
                "processed_items": len(request.payload.get("texts", [])),
            }
        elif request.task_type == "llm_inference":
            # Placeholder for heavy unquantized or 8B+ LLM inference
            result_data = {
                "generated_text": "Model output payload",
                "tokens_generated": 128,
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported task_type: {request.task_type}",
            )

        return ComputeResponse(
            task_id=request.task_id, status="completed", result=result_data
        )

    except Exception as exc:
        return ComputeResponse(
            task_id=request.task_id,
            status="failed",
            result={},
            error=str(exc),
        )

    finally:
        # Memory reclamation to prevent VRAM fragmentation
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        gc.collect()


# 3. Tunnel lifecycle manager and execution
def launch_service(port: int = 8000) -> None:
    # Terminate any conflicting background instances
    os.system("pkill -f cloudflared")

    # Start Cloudflare Tunnel
    tunnel_proc = subprocess.Popen(
        [
            "cloudflared",
            "tunnel",
            "--url",
            f"http://127.0.0.1:{port}",
            "--metrics",
            "127.0.0.1:45678",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    tunnel_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    # Parse public URL from process stream
    start_time = time.time()
    while time.time() - start_time < 30:
        line = tunnel_proc.stdout.readline()
        if not line:
            continue
        match = url_pattern.search(line)
        if match:
            tunnel_url = match.group(0)
            break

    if not tunnel_url:
        tunnel_proc.terminate()
        raise RuntimeError("Failed to establish Cloudflare tunnel within 30s.")

    print(f"\n[INFO] Remote Server Public URL: {tunnel_url}")
    print(f"[INFO] Set in local .env: COLAB_TUNNEL_URL={tunnel_url}\n")

    # Run FastAPI server on main thread
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    launch_service(port=8000)
