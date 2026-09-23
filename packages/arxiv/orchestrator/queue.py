import asyncio
import httpx
import os

from common.logging import get_logger
from research_graph.adapters.external_apis import ArxivAdapter
from ingestion_engine.adapters.downloader import ArxivDownloader
from document_processor.adapters.processor import ArchiveProcessor
from document_converter.adapters.converter import LatexToMarkdownConverter

logger = get_logger(__name__)

class BackgroundQueue:
    def __init__(self, output_dir: str = "./output"):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.output_dir = output_dir
        self.worker_task = None

    async def add_query(self, query: str, max_results: int = 3):
        await self.queue.put((query, max_results))
        logger.info("added_to_queue", query=query, max_results=max_results)

    async def start_worker(self):
        self.worker_task = asyncio.create_task(self._worker())
        logger.info("worker_started")

    async def stop_worker(self):
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                logger.info("worker_stopped")

    async def _worker(self):
        while True:
            query, max_results = await self.queue.get()
            logger.info("worker_processing", query=query)
            try:
                await self._process_query(query, max_results)
            except Exception as e:
                logger.error("worker_error", query=query, error=str(e))
            finally:
                self.queue.task_done()

    async def _process_query(self, query: str, max_results: int):
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

                download_dir = os.path.join(self.output_dir, "downloads")
                dl_task = await downloader.download_paper(paper.arxiv_id, download_dir)

                if not dl_task.success or not dl_task.file_path:
                    logger.error("download_failed", arxiv_id=paper.arxiv_id, error=dl_task.error)
                    continue

                extract_dir = os.path.join(self.output_dir, "extracted", paper.arxiv_id)
                proc_doc = processor.process_archive(paper.arxiv_id, dl_task.file_path, extract_dir)

                if not proc_doc.success or not proc_doc.main_file_path:
                    logger.error("processing_failed", arxiv_id=paper.arxiv_id, error=proc_doc.error)
                    continue

                markdown_dir = os.path.join(self.output_dir, "markdown")
                conv_doc = converter.convert(paper, proc_doc.main_file_path, markdown_dir)

                if not conv_doc.success:
                    logger.error("conversion_failed", arxiv_id=paper.arxiv_id, error=conv_doc.error)
                    continue

                logger.info("conversion_success", arxiv_id=paper.arxiv_id, path=conv_doc.markdown_path)
