import time
import multiprocessing
from typing import Any
from app_structurizer.src.concurrency.manager import ConcurrencyManager

def dummy_process(path: str, semaphore: Any) -> str:
    """Dummy processing function for tests."""
    # Simulate work
    time.sleep(0.1)

    # Simulate VRAM access
    with semaphore:
        time.sleep(0.2)

    return f"Processed: {path}"

def test_parallel_execution_returns_results():
    with ConcurrencyManager(max_workers=2, vram_lock_count=1) as manager:
        paths = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

        results = manager.process_pdfs_in_parallel(paths, dummy_process)

        assert len(results) == 3
        for path in paths:
            assert f"Processed: {path}" in results


def dummy_process_semaphore(path: str, semaphore: Any) -> dict:
    """Dummy processing function for semaphore test."""
    acquired = semaphore.acquire(blocking=False)
    if acquired:
        try:
            # Hold the lock for a bit to simulate work and allow other processes to try acquiring
            time.sleep(0.5)
            return {"path": path, "acquired": True}
        finally:
            semaphore.release()
    else:
        return {"path": path, "acquired": False}


def test_semaphore_limits_concurrency():
    # Only allow 1 concurrent VRAM access
    with ConcurrencyManager(max_workers=4, vram_lock_count=1) as manager:
        paths = ["doc1.pdf", "doc2.pdf", "doc3.pdf", "doc4.pdf"]

        # Run in parallel. If semaphore works, some might not acquire it immediately if we use non-blocking.
        # Actually, a better test is to measure time, but that can be flaky.
        # We'll use the non-blocking acquire to see if they overlap.
        # With 4 workers and 1 lock, they should all try to acquire almost simultaneously.
        # At least one should fail to acquire if they are truly concurrent.

        results = manager.process_pdfs_in_parallel(paths, dummy_process_semaphore)

        acquired_count = sum(1 for r in results if r["acquired"])
        # If they ran sequentially, acquired_count would be 4.
        # Since they run in parallel and hold the lock for 0.5s,
        # some will fail to acquire the lock since blocking=False.
        assert acquired_count < 4
        assert acquired_count >= 1 # At least one should acquire it
