import pytest
import httpx
import respx
import tempfile
import os
from ingestion_engine.src.infra.downloader import ArxivDownloader

@pytest.mark.asyncio
async def test_downloader_success():
    arxiv_id = "1234.5678"
    url = f"https://export.arxiv.org/e-print/{arxiv_id}"

    with tempfile.TemporaryDirectory() as tempdir:
        async with httpx.AsyncClient() as client:
            downloader = ArxivDownloader(client, rate_limit_delay=0)

            with respx.mock:
                respx.get(url).respond(status_code=200, content=b"fake tar gz content", headers={"content-type": "application/gzip"})

                task = await downloader.download_paper(arxiv_id, tempdir)

                assert task.success is True
                assert task.file_path is not None
                assert task.file_path.endswith(".tar.gz")
                assert os.path.exists(task.file_path)

                with open(task.file_path, "rb") as f:
                    assert f.read() == b"fake tar gz content"

@pytest.mark.asyncio
async def test_downloader_retry_and_fail():
    arxiv_id = "1234.5678"
    url = f"https://export.arxiv.org/e-print/{arxiv_id}"

    with tempfile.TemporaryDirectory() as tempdir:
        async with httpx.AsyncClient() as client:
            downloader = ArxivDownloader(client, rate_limit_delay=0)

            with respx.mock:
                # Mock a 503 response
                respx.get(url).respond(status_code=503)

                task = await downloader.download_paper(arxiv_id, tempdir)

                assert task.success is False
                assert task.error is not None
                assert "Failed to fetch" in task.error
