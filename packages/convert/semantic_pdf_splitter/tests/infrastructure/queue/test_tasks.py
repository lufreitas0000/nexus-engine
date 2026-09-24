import pytest
from unittest.mock import patch

from semantic_pdf_splitter.infrastructure.queue.celery_app import app
from semantic_pdf_splitter.infrastructure.queue.tasks import process_document_async

# Configure celery to execute synchronously for testing
app.conf.update(task_always_eager=True)

def test_task_dispatch_success():
    with patch("semantic_pdf_splitter.infrastructure.queue.tasks.process_document") as mock_pipeline:
        mock_pipeline.return_value = "/mock/output/path.md"

        # Invoke delay asynchronously (executed eagerly by celery config)
        result = process_document_async.delay("test_path.pdf", "job-123")

        # Verify the returned object wrapper provides the expected dictionary
        assert result.result == {
            "job_id": "job-123",
            "status": "completed",
            "output_path": "/mock/output/path.md"
        }

        # Verify the underlying sync pipeline was invoked with the exact params
        mock_pipeline.assert_called_once_with("test_path.pdf")

def test_task_retry_state():
    with patch("semantic_pdf_splitter.infrastructure.queue.tasks.process_document") as mock_pipeline:
        # Mock pipeline to always raise an exception
        mock_pipeline.side_effect = RuntimeError("Simulated pipeline crash")

        # In task_always_eager=True mode, celery's @retry mechanic
        # handles the exception and returns an AsyncResult representing failure.
        # It gets invoked synchronously up to max_retries times.
        result = process_document_async.delay("test_path.pdf", "job-123")

        # Verify the exception was propagated into the result object
        assert isinstance(result.result, RuntimeError)

        # In eager mode, max_retries=3 means it gets called 1 (initial) + 3 (retries) = 4 times.
        assert mock_pipeline.call_count == 4
