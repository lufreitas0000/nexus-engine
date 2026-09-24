import time
import torch
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def profile_execution(operation_name: str):
    """Context manager to profile execution time and CUDA VRAM allocation."""
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        start_vram = torch.cuda.memory_allocated() / (1024 ** 2)

    start_time = time.perf_counter()

    yield

    elapsed_time = time.perf_counter() - start_time

    if torch.cuda.is_available():
        peak_vram = torch.cuda.max_memory_allocated() / (1024 ** 2)
        end_vram = torch.cuda.memory_allocated() / (1024 ** 2)
        logger.info(
            f"[{operation_name}] Time: {elapsed_time:.4f}s | "
            f"VRAM Delta: {end_vram - start_vram:.2f}MB | "
            f"VRAM Peak: {peak_vram:.2f}MB"
        )
    else:
        logger.info(f"[{operation_name}] Time: {elapsed_time:.4f}s | CPU Only")
