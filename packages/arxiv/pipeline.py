import asyncio
import httpx
import typer
import os
from typing import Annotated

from common.logging import setup_logging, get_logger
from research_graph.src.infra.external_apis import ArxivAdapter
from ingestion_engine.src.infra.downloader import ArxivDownloader
from document_processor.src.infra.processor import ArchiveProcessor
from document_converter.src.infra.converter import LatexToMarkdownConverter
from research_graph.src.domain.model import PaperMetadata
from orchestrator.src.infra.queue import BackgroundQueue

logger = get_logger(__name__)
setup_logging()

def create_pipeline() -> BackgroundQueue:
    """
    Initializes and returns the orchestrator BackgroundQueue instance.
    This encapsulates the pipeline logic making it agnostic of the primary adapter (e.g. FastAPI, TUI).
    """
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    queue = BackgroundQueue(redis_url=redis_url)
    return queue

app = typer.Typer(help="arXiv Scraper Pipeline")

async def _search(query: str, max_results: int):
    async with httpx.AsyncClient() as client:
        arxiv_adapter = ArxivAdapter(client)
        logger.info("searching_arxiv", query=query)
        papers = await arxiv_adapter.search_by_query(query, max_results)
        if not papers:
            typer.echo("No papers found.")
            return []

        for p in papers:
            typer.echo(f"Found: {p.arxiv_id} - {p.title}")
        return papers

@app.command(name="search")
def search_cmd(
    query: Annotated[str, typer.Argument(help="Search query for arXiv")],
    max_results: Annotated[int, typer.Option(help="Max number of papers to retrieve")] = 3,
):
    """Queries arXiv and lists results."""
    asyncio.run(_search(query, max_results))

async def _download(arxiv_id: str, output_dir: str):
    async with httpx.AsyncClient() as client:
        downloader = ArxivDownloader(client, rate_limit_delay=1.0)
        download_dir = os.path.join(output_dir, "downloads")
        logger.info("downloading_paper", arxiv_id=arxiv_id)
        dl_task = await downloader.download_paper(arxiv_id, download_dir)

        if not dl_task.success or not dl_task.file_path:
            typer.echo(f"[Error] Download failed: {dl_task.error}", err=True)
            return None

        typer.echo(f"[Success] Downloaded to {dl_task.file_path}")
        return dl_task.file_path

@app.command(name="download")
def download_cmd(
    arxiv_id: Annotated[str, typer.Argument(help="arXiv ID to download")],
    output_dir: Annotated[str, typer.Option(help="Output directory")] = "./output",
):
    """Downloads a specific paper by its arXiv ID."""
    asyncio.run(_download(arxiv_id, output_dir))

def _extract(arxiv_id: str, file_path: str, output_dir: str):
    processor = ArchiveProcessor()
    extract_dir = os.path.join(output_dir, "extracted", arxiv_id)
    logger.info("extracting_archive", arxiv_id=arxiv_id)
    proc_doc = processor.process_archive(arxiv_id, file_path, extract_dir)

    if not proc_doc.success or not proc_doc.main_file_path:
        typer.echo(f"[Error] Extraction failed: {proc_doc.error}", err=True)
        return None

    typer.echo(f"[Success] Extracted main file to {proc_doc.main_file_path}")
    return proc_doc.main_file_path

@app.command(name="extract")
def extract_cmd(
    arxiv_id: Annotated[str, typer.Argument(help="arXiv ID of the paper")],
    file_path: Annotated[str, typer.Argument(help="Path to the downloaded archive/file")],
    output_dir: Annotated[str, typer.Option(help="Output directory")] = "./output",
):
    """Unpacks a downloaded archive."""
    _extract(arxiv_id, file_path, output_dir)

def _convert(arxiv_id: str, main_file_path: str, output_dir: str):
    converter = LatexToMarkdownConverter()
    markdown_dir = os.path.join(output_dir, "markdown")
    logger.info("converting_to_markdown", arxiv_id=arxiv_id)

    # We need a dummy PaperMetadata object for the converter
    dummy_paper = PaperMetadata(
        arxiv_id=arxiv_id,
        title="Unknown Title",
        authors=[],
        published_date="Unknown",
        summary="",
        url=""
    )

    conv_doc = converter.convert(dummy_paper, main_file_path, markdown_dir)

    if not conv_doc.success:
        typer.echo(f"[Error] Failed to convert: {conv_doc.error}", err=True)
        return None

    typer.echo(f"[Success] Saved to {conv_doc.markdown_path}")
    return conv_doc.markdown_path

@app.command(name="convert")
def convert_cmd(
    arxiv_id: Annotated[str, typer.Argument(help="arXiv ID of the paper")],
    main_file_path: Annotated[str, typer.Argument(help="Path to the main extracted file")],
    output_dir: Annotated[str, typer.Option(help="Output directory")] = "./output",
):
    """Converts a processed/unpacked document to Markdown."""
    _convert(arxiv_id, main_file_path, output_dir)

async def _run_pipeline(query: str, max_results: int, output_dir: str):
    logger.info("pipeline_started", query=query, max_results=max_results)

    papers = await _search(query, max_results)
    if not papers:
        return

    for paper in papers:
        logger.info("processing_paper", arxiv_id=paper.arxiv_id, title=paper.title)

        dl_path = await _download(paper.arxiv_id, output_dir)
        if not dl_path:
            continue

        main_file_path = _extract(paper.arxiv_id, dl_path, output_dir)
        if not main_file_path:
            continue

        converter = LatexToMarkdownConverter()
        markdown_dir = os.path.join(output_dir, "markdown")
        logger.info("converting_to_markdown", arxiv_id=paper.arxiv_id)
        conv_doc = converter.convert(paper, main_file_path, markdown_dir)

        if not conv_doc.success:
            logger.error("conversion_failed", arxiv_id=paper.arxiv_id, error=conv_doc.error)
            typer.echo(f"  [Error] Failed to convert: {conv_doc.error}", err=True)
            continue

        logger.info("conversion_success", arxiv_id=paper.arxiv_id, path=conv_doc.markdown_path)
        typer.echo(f"  [Success] Saved to {conv_doc.markdown_path}")

@app.command(name="all")
def all_cmd(
    query: Annotated[str, typer.Argument(help="Search query for arXiv")],
    max_results: Annotated[int, typer.Option(help="Max number of papers to process")] = 3,
    output_dir: Annotated[str, typer.Option(help="Output directory")] = "./output",
):
    """The existing end-to-end pipeline running all steps sequentially."""
    asyncio.run(_run_pipeline(query, max_results, output_dir))

if __name__ == "__main__":
    app()