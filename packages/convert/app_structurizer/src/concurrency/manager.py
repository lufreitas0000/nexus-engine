import concurrent.futures
import multiprocessing
from typing import List, Callable, Any, Iterable

class ConcurrencyManager:
    def __init__(self, max_workers: int = 4, vram_lock_count: int = 1):
        """
        Initializes the concurrency manager.

        Args:
            max_workers: Maximum number of processes in the process pool.
            vram_lock_count: Number of concurrent tasks allowed to access VRAM.
        """
        self.max_workers = max_workers
        # Use a Manager to create a semaphore that can be safely shared across processes
        self.manager = multiprocessing.Manager()
        self.vram_semaphore = self.manager.Semaphore(vram_lock_count)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def shutdown(self):
        """Shuts down the multiprocessing Manager to free resources."""
        self.manager.shutdown()

    def process_pdfs_in_parallel(self, pdf_paths: List[str], process_func: Callable[[str, Any], Any]) -> List[Any]:
        """
        Processes a list of PDF file paths in parallel using a process pool.

        Args:
            pdf_paths: A list of file paths to process.
            process_func: A function that takes a file path and a semaphore, and returns a result.
                          The function is responsible for acquiring/releasing the semaphore
                          when executing VRAM-intensive operations.

        Returns:
            A list of results corresponding to the input pdf_paths.
        """
        results = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # We pass both the item and the shared semaphore to the processing function.
            # We map the inputs and zip them with the semaphore.
            futures = [
                executor.submit(process_func, path, self.vram_semaphore)
                for path in pdf_paths
            ]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        return results
