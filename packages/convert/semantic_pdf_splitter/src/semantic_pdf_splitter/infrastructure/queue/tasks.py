import logging
from celery.exceptions import SoftTimeLimitExceeded

from semantic_pdf_splitter.infrastructure.queue.celery_app import app

logger = logging.getLogger(__name__)

from typing import Any
from pathlib import Path
from app_orchestrator.pipeline import PipelineOrchestrator

def process_document(doc_path: str) -> str:
    from semantic_pdf_splitter.router.adapters.fake_adapter import FakeVisionExtractor
    from semantic_pdf_splitter.router.cli import FakeSpatialCompiler, FakeVisionEncoder

    from semantic_pdf_splitter.router.domain.models import RawDocument

    def wrapped_extractor(path: Path) -> Any:
        doc = RawDocument(file_path=path, file_size_bytes=100)
        return FakeVisionExtractor().extract_ast(doc)

    orchestrator = PipelineOrchestrator(
        extractor_fn=wrapped_extractor,
        spatial_fn=FakeSpatialCompiler().compile_graph,
        vision_fn=FakeVisionEncoder().encode_tensor
    )
    # Instantiate the synchronous orchestrator pipeline and execute it
    result_ast = orchestrator.process(Path(doc_path))

    # In reality we would save the AST to disk and return path
    return f"{doc_path}_processed.md"

@app.task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600
)
def process_document_async(self, document_path: str, job_id: str) -> dict:
    """
    Asynchronous task wrapper that instantiates the synchronous orchestrator pipeline.
    Ensures safe decoupling for VRAM-intensive VLM workers.
    """
    logger.info(f"Starting job {job_id} for document {document_path}")

    try:
        # Call the actual synchronous pipeline
        output_file = process_document(document_path)

        return {
            "job_id": job_id,
            "status": "completed",
            "output_path": output_file
        }
    except SoftTimeLimitExceeded as e:
        logger.error(f"Job {job_id} hit soft time limit: {e}")
        # Let it bubble up, Celery handles this explicitly
        raise
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        # Ensure it bubbles up to trigger the `autoretry_for` logic
        raise
