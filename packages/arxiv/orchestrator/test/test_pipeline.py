import pytest
import os
import respx
import httpx
from unittest.mock import patch, MagicMock

from orchestrator.src.infra.worker import process_query_task

@pytest.fixture
def mock_arxiv_search_xml():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/1234.5678</id>
        <title>Quantum Computing</title>
        <summary>A study on quantum computing.</summary>
        <author><name>John Doe</name></author>
        <published>2023-01-01T00:00:00Z</published>
      </entry>
    </feed>
    """

@pytest.fixture
def mock_arxiv_pdf_content():
    return b"%PDF-1.4 mock content"

@pytest.mark.asyncio
@respx.mock
async def test_process_query_task_success(tmp_path, mock_arxiv_search_xml, mock_arxiv_pdf_content):
    # Setup tmp_path as output_dir
    output_dir = str(tmp_path)

    # Mock external API calls
    respx.get("https://export.arxiv.org/api/query?search_query=all%3Aquantum&max_results=1").mock(
        return_value=httpx.Response(200, text=mock_arxiv_search_xml)
    )

    # Mock the arXiv E-print download (which ArxivDownloader uses by default)
    # The URL pattern used in ArxivDownloader is typically https://export.arxiv.org/e-print/{arxiv_id}
    respx.get("https://export.arxiv.org/e-print/1234.5678").mock(
        return_value=httpx.Response(200, content=mock_arxiv_pdf_content)
    )
    respx.get("https://export.arxiv.org/pdf/1234.5678.pdf").mock(
        return_value=httpx.Response(200, content=mock_arxiv_pdf_content)
    )

    # Mock the Processor to succeed
    with patch("orchestrator.src.infra.worker.ArchiveProcessor.process_archive") as mock_process:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.main_file_path = os.path.join(output_dir, "extracted", "1234.5678", "main.tex")
        mock_process.return_value = mock_result

        # Mock the Converter to succeed
        with patch("orchestrator.src.infra.worker.LatexToMarkdownConverter.convert") as mock_convert:
            mock_convert_result = MagicMock()
            mock_convert_result.success = True
            mock_convert_result.markdown_path = os.path.join(output_dir, "markdown", "1234.5678.md")
            mock_convert.return_value = mock_convert_result

            # Execute worker task
            ctx = {} # Mock ARQ context
            await process_query_task(ctx, query="all:quantum", max_results=1, output_dir=output_dir)

            # Verify paths were created
            assert os.path.exists(os.path.join(output_dir, "downloads"))
            assert os.path.exists(os.path.join(output_dir, "errors"))

            # Verify there are no errors in error dir
            errors_dir = os.path.join(output_dir, "errors")
            assert len(os.listdir(errors_dir)) == 0

            mock_process.assert_called_once()
            mock_convert.assert_called_once()

@pytest.mark.asyncio
@respx.mock
async def test_process_query_task_download_error_retries_and_saves_state(tmp_path, mock_arxiv_search_xml):
    output_dir = str(tmp_path)

    # Mock search
    respx.get("https://export.arxiv.org/api/query?search_query=all%3Aquantum&max_results=1").mock(
        return_value=httpx.Response(200, text=mock_arxiv_search_xml)
    )

    # Mock download to ALWAYS fail with 500
    route = respx.get("https://export.arxiv.org/e-print/1234.5678").mock(
        return_value=httpx.Response(500)
    )

    ctx = {}

    # We patch asyncio.sleep to not actually wait during the test
    with patch("asyncio.sleep") as mock_sleep:
        await process_query_task(ctx, query="all:quantum", max_results=1, output_dir=output_dir)

        # ArxivDownloader internally does 3 attempts per call. We call it 3 times.
        assert route.call_count == 9
        # process_query_task calls sleep twice for its 3 retries. ArxivDownloader might also call it.
        # Let's just assert that it was called.
        assert mock_sleep.call_count > 0

    # Verify error state was saved
    error_file = os.path.join(output_dir, "errors", "1234.5678_download_error.json")
    assert os.path.exists(error_file)

@pytest.mark.asyncio
@respx.mock
async def test_process_query_task_processing_error_saves_state(tmp_path, mock_arxiv_search_xml, mock_arxiv_pdf_content):
    output_dir = str(tmp_path)

    respx.get("https://export.arxiv.org/api/query?search_query=all%3Aquantum&max_results=1").mock(
        return_value=httpx.Response(200, text=mock_arxiv_search_xml)
    )
    respx.get("https://export.arxiv.org/e-print/1234.5678").mock(
        return_value=httpx.Response(200, content=mock_arxiv_pdf_content)
    )
    respx.get("https://export.arxiv.org/pdf/1234.5678.pdf").mock(
        return_value=httpx.Response(200, content=mock_arxiv_pdf_content)
    )

    with patch("orchestrator.src.infra.worker.ArchiveProcessor.process_archive") as mock_process:
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Corrupted archive"
        mock_process.return_value = mock_result

        ctx = {}
        await process_query_task(ctx, query="all:quantum", max_results=1, output_dir=output_dir)

        # Verify error state was saved
        error_file = os.path.join(output_dir, "errors", "1234.5678_processing_error.json")
        assert os.path.exists(error_file)
