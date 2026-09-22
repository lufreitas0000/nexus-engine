import asyncio
import httpx
import argparse
import os

from common.logging import setup_logging, get_logger
from research_graph.adapters.external_apis import ArxivAdapter
from ingestion_engine.adapters.downloader import ArxivDownloader
from document_processor.adapters.processor import ArchiveProcessor
from document_converter.adapters.converter import LatexToMarkdownConverter

logger = get_logger(__name__)

async def run_pipeline(query: str, max_results: int, output_dir: str):
    setup_logging()
    logger.info("pipeline_started", query=query, max_results=max_results)

    # Instantiate modules
    async with httpx.AsyncClient() as client:
        arxiv_adapter = ArxivAdapter(client)
        downloader = ArxivDownloader(client, rate_limit_delay=1.0)
        processor = ArchiveProcessor()
        converter = LatexToMarkdownConverter()

        # 1. Search
        logger.info("searching_arxiv", query=query)
        papers = await arxiv_adapter.search_by_query(query, max_results)

        if not papers:
            logger.info("no_papers_found")
            return

        logger.info("papers_found", count=len(papers))

        # We process them sequentially in this simple CLI, but downloader has a semaphore
        for paper in papers:
            logger.info("processing_paper", arxiv_id=paper.arxiv_id, title=paper.title)

            # 2. Download
            download_dir = os.path.join(output_dir, "downloads")
            logger.info("downloading_paper", arxiv_id=paper.arxiv_id)
            dl_task = await downloader.download_paper(paper.arxiv_id, download_dir)

            if not dl_task.success or not dl_task.file_path:
                logger.error("download_failed", arxiv_id=paper.arxiv_id, error=dl_task.error)
                continue

            # 3. Process/Extract
            extract_dir = os.path.join(output_dir, "extracted", paper.arxiv_id)
            logger.info("extracting_archive", arxiv_id=paper.arxiv_id)
            proc_doc = processor.process_archive(paper.arxiv_id, dl_task.file_path, extract_dir)

            if not proc_doc.success or not proc_doc.main_file_path:
                logger.error("processing_failed", arxiv_id=paper.arxiv_id, error=proc_doc.error)
                continue

            # 4. Convert
            markdown_dir = os.path.join(output_dir, "markdown")
            logger.info("converting_to_markdown", arxiv_id=paper.arxiv_id)
            conv_doc = converter.convert(paper.arxiv_id, proc_doc.main_file_path, markdown_dir)

            if not conv_doc.success:
                logger.error("conversion_failed", arxiv_id=paper.arxiv_id, error=conv_doc.error)
                continue

            logger.info("conversion_success", arxiv_id=paper.arxiv_id, path=conv_doc.markdown_path)

def main():
    parser = argparse.ArgumentParser(description="arXiv Scraper Pipeline")
    parser.add_argument("query", type=str, help="Search query for arXiv")
    parser.add_argument("--max_results", type=int, default=3, help="Max number of papers to process")
    parser.add_argument("--output_dir", type=str, default="./output", help="Output directory")

    args = parser.parse_args()

    asyncio.run(run_pipeline(args.query, args.max_results, args.output_dir))

if __name__ == "__main__":
    main()
