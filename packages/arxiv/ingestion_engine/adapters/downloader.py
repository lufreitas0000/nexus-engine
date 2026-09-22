import asyncio
import os
import httpx
from typing import Optional
from pathlib import Path

from common.logging import get_logger
from ingestion_engine.domain.model import DownloadTask

logger = get_logger(__name__)

class ArxivDownloader:
    def __init__(self, client: httpx.AsyncClient, rate_limit_delay: float = 3.0):
        self.client = client
        self.rate_limit_delay = rate_limit_delay
        self.semaphore = asyncio.Semaphore(1)  # Strictly one at a time for arXiv

    async def download_paper(self, arxiv_id: str, download_dir: str) -> DownloadTask:
        async with self.semaphore:
            # Enforce delay between requests
            logger.info("enforcing_rate_limit", arxiv_id=arxiv_id, delay=self.rate_limit_delay)
            await asyncio.sleep(self.rate_limit_delay)

            try:
                # Prioritize e-print (LaTeX source tarball)
                url = f"https://export.arxiv.org/e-print/{arxiv_id}"
                response = await self._fetch_with_retries(url)

                # Check if it returned a valid file (sometimes it redirects to PDF if source not available)
                content_type = response.headers.get("content-type", "")

                ext = ".tar.gz" if "application/x-eprint-tar" in content_type or "application/gzip" in content_type else ".pdf"

                # Fallback to pdf endpoint if e-print is explicitly PDF or not what we expect
                if ext == ".pdf" and "application/pdf" not in content_type:
                    url = f"https://export.arxiv.org/pdf/{arxiv_id}.pdf"
                    response = await self._fetch_with_retries(url)

                file_path = Path(download_dir) / f"{arxiv_id}{ext}"
                os.makedirs(download_dir, exist_ok=True)

                with open(file_path, "wb") as f:
                    f.write(response.content)

                logger.info("download_success", arxiv_id=arxiv_id, file_path=str(file_path))
                return DownloadTask(arxiv_id=arxiv_id, download_dir=download_dir, file_path=str(file_path), success=True)

            except Exception as e:
                logger.error("download_error", arxiv_id=arxiv_id, error=str(e))
                return DownloadTask(arxiv_id=arxiv_id, download_dir=download_dir, success=False, error=str(e))

    async def _fetch_with_retries(self, url: str, max_retries: int = 3) -> httpx.Response:
        for attempt in range(max_retries):
            response = await self.client.get(url, follow_redirects=True)
            if response.status_code in [429, 500, 502, 503, 504]:
                wait_time = 2 ** attempt
                logger.warning("retry_request", url=url, attempt=attempt, wait_time=wait_time, status_code=response.status_code)
                await asyncio.sleep(wait_time)
                continue
            response.raise_for_status()
            return response

        logger.error("max_retries_exceeded", url=url, max_retries=max_retries)
        raise Exception(f"Failed to fetch {url} after {max_retries} attempts.")
