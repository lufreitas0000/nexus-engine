import json
import pytest
from pathlib import Path
from pypdf import PdfWriter
from book_studio.tools.extractor import MarkerExtractor
from book_studio.core.schemas import ExtractionResult

def test_marker_extractor_success(mocker, tmp_path):
    # Setup mock file paths
    pdf_path = tmp_path / "test_book.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    output_dir = tmp_path / "output"
    
    mock_payload = {
        "metadata": {"languages": ["eng"]},
        "children": [
            {
                "id": "/page/1",
                "children": [
                    {
                        "id": "1",
                        "block_type": "Text",
                        "html": "Quantum Mechanics",
                        "polygon": None,
                    }
                ],
            }
        ],
    }

    # Mock subprocess.run to simulate successful CLI execution without invoking PyTorch
    def fake_subprocess_run(cmd, *args, **kwargs):
        chunk_pdf = Path(cmd[1])
        out_dir = Path(cmd[cmd.index("--output_dir") + 1])
        chunk_stem = chunk_pdf.stem
        chunk_dir = out_dir / chunk_stem
        chunk_dir.mkdir(parents=True, exist_ok=True)
        (chunk_dir / f"{chunk_stem}.json").write_text(json.dumps(mock_payload))
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        return mock_result

    mock_run = mocker.patch("subprocess.run", side_effect=fake_subprocess_run)

    # Execute
    extractor = MarkerExtractor()
    result = extractor.extract(pdf_path, output_dir)

    # Assertions
    assert isinstance(result, ExtractionResult)
    assert len(result.pages) == 1
    assert result.pages[0].blocks[0].content == "Quantum Mechanics"
    mock_run.assert_called_once()
