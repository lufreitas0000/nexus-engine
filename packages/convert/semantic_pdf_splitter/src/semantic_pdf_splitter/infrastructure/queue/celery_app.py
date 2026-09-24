import os
from celery import Celery

# Default to local redis instance via environment variables
broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

app = Celery("semantic_pdf_splitter", broker=broker_url, backend=result_backend)

app.conf.update(
    # Production Safety: Late acks and disable prefetching to prevent VRAM hoarding
    task_acks_late=True,
    worker_prefetch_multiplier=1,

    # Timeouts to kill stalled GPU workers
    task_time_limit=3600,
    task_soft_time_limit=3300,

    # Register tasks modules
    imports=("semantic_pdf_splitter.infrastructure.queue.tasks",)
)
