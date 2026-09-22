import asyncio
import httpx
import argparse
import os

from research_graph.adapters.external_apis import ArxivAdapter
from ingestion_engine.adapters.downloader import ArxivDownloader
from document_processor.adapters.processor import ArchiveProcessor
from document_converter.adapters.converter import LatexToMarkdownConverter

async def run_pipeline(query: str, max_results: int, output_dir: str):
    print(f"Starting pipeline for query: '{query}'")

    # Instantiate modules
    async with httpx.AsyncClient() as client:
        arxiv_adapter = ArxivAdapter(client)
        downloader = ArxivDownloader(client, rate_limit_delay=1.0)
        processor = ArchiveProcessor()
        converter = LatexToMarkdownConverter()

        # 1. Search
        print(f"Searching arXiv for top {max_results} results...")
        papers = await arxiv_adapter.search_by_query(query, max_results)

        if not papers:
            print("No papers found.")
            return

        print(f"Found {len(papers)} papers. Starting download and conversion...")

        # We process them sequentially in this simple CLI, but downloader has a semaphore
        for paper in papers:
            print(f"\nProcessing: {paper.arxiv_id} - {paper.title}")

            # 2. Download
            download_dir = os.path.join(output_dir, "downloads")
            print("  Downloading...")
            dl_task = await downloader.download_paper(paper.arxiv_id, download_dir)

            if not dl_task.success or not dl_task.file_path:
                print(f"  [Error] Failed to download: {dl_task.error}")
                continue

            # 3. Process/Extract
            extract_dir = os.path.join(output_dir, "extracted", paper.arxiv_id)
            print("  Extracting...")
            proc_doc = processor.process_archive(paper.arxiv_id, dl_task.file_path, extract_dir)

            if not proc_doc.success or not proc_doc.main_file_path:
                print(f"  [Error] Failed to process archive: {proc_doc.error}")
                continue

            # 4. Convert
            markdown_dir = os.path.join(output_dir, "markdown")
            print("  Converting to Markdown...")
            conv_doc = converter.convert(paper.arxiv_id, proc_doc.main_file_path, markdown_dir)

            if not conv_doc.success:
                print(f"  [Error] Failed to convert: {conv_doc.error}")
                continue

            print(f"  [Success] Saved to {conv_doc.markdown_path}")

def main():
    parser = argparse.ArgumentParser(description="arXiv Scraper Pipeline")
    parser.add_argument("query", type=str, help="Search query for arXiv")
    parser.add_argument("--max_results", type=int, default=3, help="Max number of papers to process")
    parser.add_argument("--output_dir", type=str, default="./output", help="Output directory")

    args = parser.parse_args()

    asyncio.run(run_pipeline(args.query, args.max_results, args.output_dir))

if __name__ == "__main__":
    main()
