import os
import pytest
from pathlib import Path
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from resolver import get_workspace_path

def test_get_workspace_path_success(monkeypatch):
    monkeypatch.setenv("NEXUS_WORKSPACE", "/tmp/my-workspace")
    path = get_workspace_path()
    assert path == Path("/tmp/my-workspace").resolve()

def test_get_workspace_path_missing(monkeypatch):
    monkeypatch.delenv("NEXUS_WORKSPACE", raising=False)
    with pytest.raises(RuntimeError, match="missing or empty"):
        get_workspace_path()

def test_get_workspace_path_empty(monkeypatch):
    monkeypatch.setenv("NEXUS_WORKSPACE", "   ")
    with pytest.raises(RuntimeError, match="missing or empty"):
        get_workspace_path()
