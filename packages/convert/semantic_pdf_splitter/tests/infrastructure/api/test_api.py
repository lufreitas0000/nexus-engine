import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from semantic_pdf_splitter.infrastructure.api.app import create_app
from semantic_pdf_splitter.infrastructure.queue.celery_app import app as celery_app

@pytest.fixture(autouse=True)
def configure_celery():
    # Force Celery to execute synchronously for fast, deterministic unit testing
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True
    )

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_submit_job_invalid_path(client):
    response = client.post("/v1/documents/jobs", data={"document_path": "/fake/path/does/not/exist.pdf"})
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]

def test_submit_job_success(client, tmp_path):
    fake_pdf = tmp_path / "test.pdf"
    fake_pdf.write_text("dummy")

    with patch("semantic_pdf_splitter.infrastructure.api.app.process_document_async.delay") as mock_delay:
        mock_task = MagicMock()
        mock_task.id = "mock-uuid-123"
        mock_delay.return_value = mock_task

        response = client.post("/v1/documents/jobs", data={"document_path": str(fake_pdf)})

        assert response.status_code == 202
        data = response.json()
        assert data["job_id"] == "mock-uuid-123"
        assert data["status"] == "PENDING"

        mock_delay.assert_called_once()

def test_poll_job_success(client):
    # Mock AsyncResult
    with patch("semantic_pdf_splitter.infrastructure.api.app.AsyncResult") as mock_async_result:
        mock_task = MagicMock()
        mock_task.state = "SUCCESS"
        mock_task.result = {"status": "completed", "chunks": 5}
        mock_async_result.return_value = mock_task

        response = client.get("/v1/documents/jobs/mock-uuid-123")

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "mock-uuid-123"
        assert data["status"] == "SUCCESS"
        assert data["ready"] is True
        assert data["successful"] is True
        assert data["result"] == {"status": "completed", "chunks": 5}
        assert data["error"] is None

def test_poll_job_failure(client):
    with patch("semantic_pdf_splitter.infrastructure.api.app.AsyncResult") as mock_async_result:
        mock_task = MagicMock()
        mock_task.state = "FAILURE"
        mock_task.result = Exception("VRAM allocation failed")
        mock_async_result.return_value = mock_task

        response = client.get("/v1/documents/jobs/mock-uuid-123")

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "mock-uuid-123"
        assert data["status"] == "FAILURE"
        assert data["ready"] is True
        assert data["successful"] is False
        assert "VRAM allocation failed" in data["error"]

def test_poll_job_pending(client):
    with patch("semantic_pdf_splitter.infrastructure.api.app.AsyncResult") as mock_async_result:
        mock_task = MagicMock()
        mock_task.state = "PENDING"
        mock_task.result = None
        mock_async_result.return_value = mock_task

        response = client.get("/v1/documents/jobs/mock-uuid-123")

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "mock-uuid-123"
        assert data["status"] == "PENDING"
        assert data["ready"] is False
        assert data["successful"] is None
        assert data["result"] is None
