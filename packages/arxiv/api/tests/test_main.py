import pytest
import os
from fastapi.testclient import TestClient

from api.main import app, queue

client = TestClient(app)

def test_submit_research():
    with client:
        response = client.post("/api/research", json={"query": "quantum computing", "max_results": 2})
        assert response.status_code == 200
        assert response.json() == {"message": "Query submitted", "query": "quantum computing", "max_results": 2}

def test_get_notes_not_found():
    response = client.get("/api/notes/9999.9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Notes not found or not processed yet."

def test_get_notes_success(tmp_path):
    # Mock a processed markdown file
    arxiv_id = "1234.5678"
    md_dir = os.path.join(tmp_path, "markdown")
    os.makedirs(md_dir, exist_ok=True)

    md_path = os.path.join(md_dir, f"{arxiv_id}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Fake Note\nThis is a fake note.")

    # Temporarily override queue output_dir to tmp_path
    old_output_dir = queue.output_dir
    queue.output_dir = str(tmp_path)

    try:
        response = client.get(f"/api/notes/{arxiv_id}")
        assert response.status_code == 200
        assert response.json()["arxiv_id"] == arxiv_id
        assert "# Fake Note" in response.json()["content"]
    finally:
        queue.output_dir = old_output_dir
