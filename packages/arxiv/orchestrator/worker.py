import os
import httpx
import asyncio
import json
from arq.connections import RedisSettings

from common.logging import get_logger
from research_graph.adapters.external_apis import ArxivAdapter
from ingestion_engine.adapters.downloader import ArxivDownloader
from document_processor.adapters.processor import ArchiveProcessor
from document_converter.adapters.converter import LatexToMarkdownConverter

logger = get_logger(__name__)

async def process_query_task(ctx, query: str, max_results: int, output_dir: str):
    logger.info("worker_processing", query=query)

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

    try:
        async with httpx.AsyncClient() as client:
            arxiv_adapter = ArxivAdapter(client)
            downloader = ArxivDownloader(client, rate_limit_delay=1.0)
            processor = ArchiveProcessor()
            converter = LatexToMarkdownConverter()

            logger.info("searching_arxiv", query=query)
            papers = await arxiv_adapter.search_by_query(query, max_results)

            if not papers:
                logger.info("no_papers_found", query=query)
                return

            for paper in papers:
                logger.info("processing_paper", arxiv_id=paper.arxiv_id, title=paper.title)

                download_dir = os.path.join(output_dir, "downloads")

                # Retry loop for downloading
                max_retries = 3
                dl_task = None
                for attempt in range(max_retries):
                    dl_task = await downloader.download_paper(paper.arxiv_id, download_dir)
                    if dl_task.success and dl_task.file_path:
                        break

                    logger.warning("download_failed_attempt", arxiv_id=paper.arxiv_id, attempt=attempt+1, error=dl_task.error)
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt) # Exponential backoff: 1s, 2s

                if not dl_task or not dl_task.success or not dl_task.file_path:
                    error_msg = (dl_task.error if dl_task and dl_task.error else "Unknown download error")
                    logger.error("download_failed_permanently", arxiv_id=paper.arxiv_id, error=error_msg)
                    save_error(paper.arxiv_id, "download", error_msg)
                    continue

                extract_dir = os.path.join(output_dir, "extracted", paper.arxiv_id)
                proc_doc = processor.process_archive(paper.arxiv_id, dl_task.file_path, extract_dir)

                if not proc_doc.success or not proc_doc.main_file_path:
                    error_msg = proc_doc.error or "Unknown processing error"
                    logger.error("processing_failed", arxiv_id=paper.arxiv_id, error=error_msg)
                    save_error(paper.arxiv_id, "processing", error_msg)
                    continue

                markdown_dir = os.path.join(output_dir, "markdown")
                conv_doc = converter.convert(paper, proc_doc.main_file_path, markdown_dir)

                if not conv_doc.success:
                    error_msg = conv_doc.error or "Unknown conversion error"
                    logger.error("conversion_failed", arxiv_id=paper.arxiv_id, error=error_msg)
                    save_error(paper.arxiv_id, "conversion", error_msg)
                    continue

                logger.info("conversion_success", arxiv_id=paper.arxiv_id, path=conv_doc.markdown_path)
    except Exception as e:
        logger.error("worker_error", query=query, error=str(e))
        raise e

# Setup Redis settings based on environment variable (defaults to localhost)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_settings = RedisSettings.from_dsn(redis_url)

class WorkerSettings:
    functions = [process_query_task]
    redis_settings = redis_settings
