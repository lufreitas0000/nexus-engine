"""
Validation suite for the Application Service orchestration layer.
"""

from pathlib import Path
from src.services.extraction import extract_document_to_markdown
from src.domain.ports import VisionExtractor

def test_extract_document_to_markdown_io_piping(
    fake_extractor: VisionExtractor,
    degraded_raster_book_path: Path,
    tmp_path: Path
) -> None:
    """
    Validates that the service deterministically pipes the file buffer through 
    the domain port and successfully flushes the UTF-8 string to disk.
    
    Note: `tmp_path` is a native pytest fixture that allocates a temporary 
    directory in the OS temp folder, ensuring isolation between test runs.
    """
    out_path = extract_document_to_markdown(
        file_path=degraded_raster_book_path,
        extractor=fake_extractor,
        output_dir=tmp_path
    )
    
    assert out_path.exists(), "The output Markdown file was not created on disk."
    assert out_path.suffix == ".md", "The output file lacks the correct topological extension."
    
    content = out_path.read_text(encoding="utf-8")
    assert content.startswith("# Simulated Chapter"), "The AST content was corrupted during I/O flush."
