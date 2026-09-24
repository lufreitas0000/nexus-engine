from typing import Protocol
from ingestion_engine.src.domain.model import DownloadTask

class IngestionDownloader(Protocol):
    async def download_paper(self, arxiv_id: str, download_dir: str) -> DownloadTask:
        """Downloads the paper source files and returns a DownloadTask indicating status."""
        ...
