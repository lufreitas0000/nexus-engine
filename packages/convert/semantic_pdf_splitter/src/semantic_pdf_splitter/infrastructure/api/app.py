import os
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Form, status
from celery.result import AsyncResult

from semantic_pdf_splitter.infrastructure.api.models import JobSubmissionResponse, JobStatusResponse
from semantic_pdf_splitter.infrastructure.queue.tasks import process_document_async
from semantic_pdf_splitter.infrastructure.queue.celery_app import app as celery_app

def create_app() -> FastAPI:
    app = FastAPI(title="Semantic PDF Splitter API", version="0.1.0")

    @app.get("/healthz")
    def health_check():
        return {"status": "ok"}

    @app.post("/v1/documents/jobs", response_model=JobSubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
    def submit_job(document_path: str = Form(...)):
        path = Path(document_path)
        if not path.exists():
            raise HTTPException(status_code=400, detail="Document path does not exist on the local disk")

        job_id = str(uuid.uuid4())
        # Dispatch Celery background task
        task = process_document_async.delay(document_path=str(path), job_id=job_id)

        return JobSubmissionResponse(job_id=task.id, status="PENDING")

    @app.get("/v1/documents/jobs/{job_id}", response_model=JobStatusResponse)
    def get_job_status(job_id: str):
        task_result = AsyncResult(job_id, app=celery_app)
        state = task_result.state

        response = JobStatusResponse(
            job_id=job_id,
            status=state,
            ready=False
        )

        if state == "SUCCESS":
            response.ready = True
            response.successful = True
            response.result = task_result.result
        elif state == "FAILURE":
            response.ready = True
            response.successful = False
            response.error = str(task_result.result)

        return response

    return app
