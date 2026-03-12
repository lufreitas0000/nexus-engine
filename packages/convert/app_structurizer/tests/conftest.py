"""
Centralized Test Configuration and Dependency Injection (Fixtures).
Allocates deterministic state objects for the structurizer bounded context.
"""

import pytest
import fitz  # type: ignore
from pathlib import Path
from typing import Dict

from src.domain.models import RawDocument, MarkdownAST
from src.domain.ports import VisionExtractor

FIXTURE_DIR = Path(__file__).parent / "fixtures"

class FakeVisionExtractor:
    """
    A deterministic Test Double (Fake) satisfying the VisionExtractor Protocol.
    Bypasses PyTorch/GPU requirements to return a hardcoded AST instantly.
    """
    def extract_ast(self, document: RawDocument) -> MarkdownAST:
        """Simulates the $H \times W \times C$ tensor to Markdown mapping."""
        return MarkdownAST(
            content="# Simulated Chapter\n\nThis is a mocked extraction.",
            metadata={"confidence": "0.99", "model": "FakeAdapter_v1"}
        )

@pytest.fixture(scope="session")
def fake_extractor() -> VisionExtractor:
    """Injects the Fake adapter into the test suite."""
    return FakeVisionExtractor()

@pytest.fixture(scope="session")
def degraded_raster_book_path() -> Path:
    """
    Synthesizes a 50-page PDF simulating a poorly scanned, compressed old textbook.
    Renders text to a memory buffer, applies lossy JPEG quantization, and 
    embeds the pixel matrix back into a new PDF.
    
    Returns:
        Path: Absolute filesystem path to the generated artifact.
    """
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIXTURE_DIR / "old_scanned_book.pdf"
    
    # Do not regenerate if it already exists in the session to save CPU cycles
    if out_path.exists():
        return out_path

    final_doc = fitz.open()
    temp_doc = fitz.open()
    
    for i in range(50):
        # 1. Allocate temporary vector page
        temp_page = temp_doc.new_page()
        text = f"Chapter {i}\n\nThis simulates an old, degraded page {i} from a classic textbook."
        # Use a built-in serif font (Times-Roman) to approximate classic academic texts
        temp_page.insert_text(fitz.Point(50, 50), text, fontname="ti-ro", fontsize=12)
        
        # 2. Rasterize to a C-level uncompressed pixel matrix (Pixmap) at low DPI
        pix = temp_page.get_pixmap(dpi=72)
        
        # 3. Apply heavy lossy compression (simulating bad scanner)
        img_bytes = pix.tobytes("jpeg", jpg_quality=10) 
        
        # 4. Allocate final page and embed the image byte-stream
        final_page = final_doc.new_page(width=pix.width, height=pix.height)
        final_page.insert_image(final_page.rect, stream=img_bytes)
        
    final_doc.save(str(out_path))
    temp_doc.close()
    final_doc.close()
    
    return out_path

@pytest.fixture
def raw_document(degraded_raster_book_path: Path) -> RawDocument:
    """Injects a validated domain model pointing to the synthetic fixture."""
    return RawDocument(
        file_path=degraded_raster_book_path,
        file_size_bytes=degraded_raster_book_path.stat().st_size
    )
