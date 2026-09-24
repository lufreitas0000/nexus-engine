import pytest
from orchestrator.src.services.router import route_task, LOCAL_VRAM_LIMIT_GB

def test_route_task_local(monkeypatch):
    monkeypatch.setattr("orchestrator.src.services.router.get_available_vram_gb", lambda: 6.0)
    queue = route_task({"task_id": "test"}, 4.0)
    assert queue == "local_queue"

def test_route_task_remote_exceeds_limit(monkeypatch):
    monkeypatch.setattr("orchestrator.src.services.router.get_available_vram_gb", lambda: 6.0)
    queue = route_task({"task_id": "test"}, 6.0) # > 5.0
    assert queue == "colab_queue"

def test_route_task_remote_no_vram(monkeypatch):
    monkeypatch.setattr("orchestrator.src.services.router.get_available_vram_gb", lambda: 2.0)
    queue = route_task({"task_id": "test"}, 4.0)
    assert queue == "colab_queue"
