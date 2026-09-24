import torch

LOCAL_VRAM_LIMIT_GB = 5.0

def get_available_vram_gb() -> float:
    if not torch.cuda.is_available():
        return 0.0
    free_memory, _ = torch.cuda.mem_get_info(0)
    return free_memory / (1024 ** 3)

def route_task(task_payload: dict, required_vram_gb: float) -> str:
    available_vram = get_available_vram_gb()

    if required_vram_gb <= LOCAL_VRAM_LIMIT_GB and required_vram_gb <= available_vram:
        return "local_queue"
    else:
        return "colab_queue"
