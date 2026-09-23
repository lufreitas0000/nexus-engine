import os
import httpx
from arq.connections import RedisSettings

from common.logging import get_logger
from research_graph.adapters.external_apis import ArxivAdapter
from ingestion_engine.adapters.downloader import ArxivDownloader
from document_processor.adapters.processor import ArchiveProcessor
from document_converter.adapters.converter import LatexToMarkdownConverter

logger = get_logger(__name__)

async def process_query_task(ctx, query: str, max_results: int, output_dir: str):
    logger.info("worker_processing", query=query)
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
                dl_task = await downloader.download_paper(paper.arxiv_id, download_dir)

                if not dl_task.success or not dl_task.file_path:
                    logger.error("download_failed", arxiv_id=paper.arxiv_id, error=dl_task.error)
                    continue

                extract_dir = os.path.join(output_dir, "extracted", paper.arxiv_id)
                proc_doc = processor.process_archive(paper.arxiv_id, dl_task.file_path, extract_dir)

                if not proc_doc.success or not proc_doc.main_file_path:
                    logger.error("processing_failed", arxiv_id=paper.arxiv_id, error=proc_doc.error)
                    continue

                markdown_dir = os.path.join(output_dir, "markdown")
                conv_doc = converter.convert(paper, proc_doc.main_file_path, markdown_dir)

                if not conv_doc.success:
                    logger.error("conversion_failed", arxiv_id=paper.arxiv_id, error=conv_doc.error)
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
