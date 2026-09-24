import os
import httpx
import asyncio
import json
from arq.connections import RedisSettings

from common.logging import get_logger
from research_graph.src.infra.external_apis import ArxivAdapter
from ingestion_engine.src.infra.downloader import ArxivDownloader
from document_processor.src.infra.processor import ArchiveProcessor
from document_converter.src.infra.converter import LatexToMarkdownConverter
from research_graph.src.domain.model import PaperMetadata
from ingestion_engine.src.domain.model import IngestionTask, TaskType
import redis.asyncio as redis_async
from orchestrator.src.services.router import get_available_vram_gb, LOCAL_VRAM_LIMIT_GB
from research_graph.src.infra.external_apis import (
    ColabComputeAdapter,
    RemoteComputeUnavailableError
)

logger = get_logger(__name__)

async def publish_state(ctx: dict, task_id: str, origin: str, stage: str, status: str):
    try:
        client = ctx.get("redis_client")
        if client:
            message = json.dumps({"task_id": task_id, "origin": origin, "stage": stage, "status": status})
            await client.publish("pipeline_state", message)
    except Exception as e:
        logger.error("redis_publish_error", error=str(e))

async def process_paper_pipeline(ctx: dict, paper: PaperMetadata, task_id: str, output_dir: str, downloader: ArxivDownloader, processor: ArchiveProcessor, converter: LatexToMarkdownConverter):
    error_dir = os.path.join(output_dir, "errors")
    os.makedirs(error_dir, exist_ok=True)

    def save_error(arxiv_id: str, step: str, error_msg: str):
        error_path = os.path.join(error_dir, f"{arxiv_id}_{step}_error.json")
        try:
            with open(error_path, "w") as f:
                json.dump({"arxiv_id": arxiv_id, "step": step, "error": error_msg}, f, indent=2)
            logger.info("error_state_saved", arxiv_id=arxiv_id, step=step, path=error_path)
        except Exception as e:
            logger.error("failed_to_save_error_state", arxiv_id=arxiv_id, error=str(e))

    await publish_state(ctx, task_id, paper.arxiv_id, "Ingestion", "In Progress")

    download_dir = os.path.join(output_dir, "downloads")
    max_retries = 3
    dl_task = None
    for attempt in range(max_retries):
        dl_task = await downloader.download_paper(paper.arxiv_id, download_dir)
        if dl_task.success and dl_task.file_path:
            break

        logger.warning("download_failed_attempt", arxiv_id=paper.arxiv_id, attempt=attempt+1, error=dl_task.error)
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)

    if not dl_task or not dl_task.success or not dl_task.file_path:
        error_msg = (dl_task.error if dl_task and dl_task.error else "Unknown download error")
        logger.error("download_failed_permanently", arxiv_id=paper.arxiv_id, error=error_msg)
        save_error(paper.arxiv_id, "download", error_msg)
        await publish_state(ctx, task_id, paper.arxiv_id, "Ingestion", "Failed")
        return

    await publish_state(ctx, task_id, paper.arxiv_id, "Extraction", "In Progress")
    extract_dir = os.path.join(output_dir, "extracted", paper.arxiv_id)
    proc_doc = processor.process_archive(paper.arxiv_id, dl_task.file_path, extract_dir)

    if not proc_doc.success or not proc_doc.main_file_path:
        error_msg = proc_doc.error or "Unknown processing error"
        logger.error("processing_failed", arxiv_id=paper.arxiv_id, error=error_msg)
        save_error(paper.arxiv_id, "processing", error_msg)
        await publish_state(ctx, task_id, paper.arxiv_id, "Extraction", "Failed")
        return

    await publish_state(ctx, task_id, paper.arxiv_id, "Conversion", "In Progress")
    markdown_dir = os.path.join(output_dir, "markdown")
    conv_doc = converter.convert(paper, proc_doc.main_file_path, markdown_dir)

    if not conv_doc.success:
        error_msg = conv_doc.error or "Unknown conversion error"
        logger.error("conversion_failed", arxiv_id=paper.arxiv_id, error=error_msg)
        save_error(paper.arxiv_id, "conversion", error_msg)
        await publish_state(ctx, task_id, paper.arxiv_id, "Conversion", "Failed")
        return

    logger.info("conversion_success", arxiv_id=paper.arxiv_id, path=conv_doc.markdown_path)
    await publish_state(ctx, task_id, paper.arxiv_id, "Conversion", "Completed")

async def process_ingestion_task(ctx, task_dict: dict, max_results: int, output_dir: str):
    # Reconstruct DTO
    task = IngestionTask(
        task_id=task_dict["task_id"],
        task_type=TaskType(task_dict["task_type"]),
        payload=task_dict["payload"],
        max_results=task_dict.get("max_results", max_results)
    )

    task_id = task.task_id
    task_type = task.task_type.value
    payload = task.payload

    logger.info("worker_processing", task_id=task_id, task_type=task_type, payload=payload)

    try:
        async with httpx.AsyncClient() as client:
            arxiv_adapter = ArxivAdapter(client)
            downloader = ArxivDownloader(client, rate_limit_delay=1.0)
            processor = ArchiveProcessor()
            converter = LatexToMarkdownConverter()

            if task_type == "SEARCH_QUERY":
                logger.info("searching_arxiv", query=payload)
                papers = await arxiv_adapter.search_by_query(payload, max_results)

                if not papers:
                    logger.info("no_papers_found", query=payload)
                    return

                for paper in papers:
                    await process_paper_pipeline(ctx, paper, task_id, output_dir, downloader, processor, converter)

            elif task_type == "ARXIV_IDENTIFIER":
                # Fallback to search to get metadata first
                papers = await arxiv_adapter.search_by_query(payload, 1)
                if not papers:
                    logger.error("arxiv_metadata_not_found", arxiv_id=payload)
                    await publish_state(ctx, task_id, payload, "Ingestion", "Failed")
                    return
                await process_paper_pipeline(ctx, papers[0], task_id, output_dir, downloader, processor, converter)

            elif task_type == "LOCAL_PATH":
                # For local path, we skip download and mock metadata
                paper = PaperMetadata(
                    arxiv_id=os.path.basename(payload),
                    title="Local File",
                    authors=[],
                    published_date="Unknown",
                    summary="",
                    url=""
                )
                await publish_state(ctx, task_id, paper.arxiv_id, "Ingestion", "Completed") # skipped download

                await publish_state(ctx, task_id, paper.arxiv_id, "Extraction", "In Progress")
                extract_dir = os.path.join(output_dir, "extracted", paper.arxiv_id)
                proc_doc = processor.process_archive(paper.arxiv_id, payload, extract_dir)

                if not proc_doc.success or not proc_doc.main_file_path:
                    error_msg = proc_doc.error or "Unknown processing error"
                    logger.error("processing_failed", arxiv_id=paper.arxiv_id, error=error_msg)
                    await publish_state(ctx, task_id, paper.arxiv_id, "Extraction", "Failed")
                    return

                await publish_state(ctx, task_id, paper.arxiv_id, "Conversion", "In Progress")
                markdown_dir = os.path.join(output_dir, "markdown")
                conv_doc = converter.convert(paper, proc_doc.main_file_path, markdown_dir)

                if not conv_doc.success:
                    error_msg = conv_doc.error or "Unknown conversion error"
                    logger.error("conversion_failed", arxiv_id=paper.arxiv_id, error=error_msg)
                    await publish_state(ctx, task_id, paper.arxiv_id, "Conversion", "Failed")
                    return
                await publish_state(ctx, task_id, paper.arxiv_id, "Conversion", "Completed")
            else:
                logger.error("unknown_task_type", task_type=task_type)

    except Exception as e:
        logger.error("worker_error", task_id=task_id, error=str(e))
        await publish_state(ctx, task_id, "Unknown", "Pipeline", "Failed")
        raise e

async def process_remote_task(ctx, task_payload: dict, required_vram_gb: float):
    """ARQ task to execute payloads on the remote Colab instance."""

    # Retrieve the Redis connection and tunnel URL from the worker context
    redis = ctx['redis']
    tunnel_url = ctx.get('tunnel_url', "")
    adapter = ColabComputeAdapter(tunnel_url=tunnel_url)

    task_id = task_payload.get("task_id", "unknown_task")

    try:
        # Attempt to execute on the remote Colab server
        result = await adapter.execute_remote_task("api/v1/compute", task_payload)
        return result

    except (RemoteComputeUnavailableError, httpx.TimeoutException, httpx.ConnectError) as exc:
        # Remote execution definitively failed (either 502/503 or max retries exceeded)
        logger.warning("remote_execution_failed", task_id=task_id, error=str(exc))

        # 1. Fallback Routing Evaluation
        available_vram = get_available_vram_gb()

        if required_vram_gb <= LOCAL_VRAM_LIMIT_GB and required_vram_gb <= available_vram:
            logger.info("fallback_routing_local", task_id=task_id)
            # Re-queue into the local pipeline directly.
            # Note: Because `process_local_task` wasn't originally registered,
            # we re-queue to process_ingestion_task with defaults to prevent ARQ errors
            await redis.enqueue_job("process_ingestion_task", task_payload, 3, "./output")
        else:
            # 2. Dead-Letter Queue (DLQ) Isolation
            logger.error("fallback_dlq_isolation", task_id=task_id)
            dlq_payload = {
                "task_payload": task_payload,
                "error": str(exc),
                "required_vram_gb": required_vram_gb,
                "status": "FAILED_REMOTE_TIMEOUT"
            }
            # Push to the Redis list acting as our DLQ
            redis_client = ctx.get("redis_client")
            if redis_client:
                await redis_client.lpush("pipeline_dlq", json.dumps(dlq_payload))

                # Publish state update to the Textual TUI via Redis Pub/Sub
                await redis_client.publish("pipeline_state", json.dumps({
                    "task_id": task_id,
                    "status": "FAILED_REMOTE_TIMEOUT",
                    "stage": "DLQ_FALLBACK"
                }))

# Kept for backwards compatibility with test files
async def process_query_task(ctx, query: str, max_results: int, output_dir: str):
    import uuid
    from ingestion_engine.src.domain.model import IngestionTask, TaskType
    from dataclasses import asdict

    task_id = str(uuid.uuid4())
    task = IngestionTask(task_id=task_id, task_type=TaskType.SEARCH_QUERY, payload=query, max_results=max_results)
    task_dict = asdict(task)
    task_dict["task_type"] = task.task_type.value

    await process_ingestion_task(ctx, task_dict, max_results, output_dir)

async def startup(ctx):
    import os
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ctx["redis_client"] = redis_async.from_url(redis_url)
    ctx['tunnel_url'] = os.getenv("COLAB_TUNNEL_URL", "")

async def shutdown(ctx):
    client = ctx.get("redis_client")
    if client:
        await client.aclose()

# Setup Redis settings based on environment variable (defaults to localhost)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_settings = RedisSettings.from_dsn(redis_url)

from orchestrator.src.infra.scheduler import run_daily_literature_review
from arq import cron

class WorkerSettings:
    functions = [process_query_task, process_ingestion_task, process_remote_task]
    redis_settings = redis_settings
    on_startup = startup
    on_shutdown = shutdown
    cron_jobs = [
        cron(run_daily_literature_review, hour=2, minute=0)
    ]
