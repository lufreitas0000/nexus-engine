import pytest
from pathlib import Path
import threading
import time

def test_workspace_concurrent_writes(tmp_path):
    # Simulate multiple workers trying to write to the same workspace file
    # This ensures that our IO boundaries and filelocks are solid.
    
    target_file = tmp_path / "concurrent_doc.json"
    
    def worker_write(worker_id: int):
        # We would use filelock here
        from filelock import FileLock
        lock = FileLock(str(target_file) + ".lock")
        
        with lock:
            if not target_file.exists():
                data = []
            else:
                import json
                with open(target_file, "r") as f:
                    data = json.load(f)
                    
            data.append(worker_id)
            time.sleep(0.01) # artificially induce race condition window
            
            import json
            with open(target_file, "w") as f:
                json.dump(data, f)
                
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker_write, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    import json
    with open(target_file, "r") as f:
        data = json.load(f)
        
    assert len(data) == 10
    assert set(data) == set(range(10))
