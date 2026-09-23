import pytest
import os
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from api.main import app, queue

client = TestClient(app)

@patch("api.main.queue.pool")
@patch("api.main.queue.start_worker", new_callable=AsyncMock)
@patch("api.main.queue.stop_worker", new_callable=AsyncMock)
def test_submit_research(mock_stop, mock_start, mock_pool):
    mock_pool.enqueue_job = AsyncMock()
    # since we mock start_worker/stop_worker, we don't connect to real redis in lifespan
    with client:
        response = client.post("/api/research", json={"query": "quantum computing", "max_results": 2})
        assert response.status_code == 200
        assert response.json() == {"message": "Query submitted", "query": "quantum computing", "max_results": 2}
        mock_pool.enqueue_job.assert_called_once()

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
