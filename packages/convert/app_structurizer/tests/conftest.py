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
        """Simulates the tensor to Markdown mapping."""
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
    """
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIXTURE_DIR / "old_scanned_book.pdf"

    if out_path.exists():
        return out_path

    final_doc = fitz.open()
    temp_doc = fitz.open()

    for i in range(50):
        temp_page = temp_doc.new_page()
        text = f"Chapter {i}\n\nThis simulates an old, degraded page {i} from a classic textbook."

        # FIX: Rely on the guaranteed built-in default font buffer (Helvetica)
        temp_page.insert_text(fitz.Point(50, 50), text, fontsize=12)

        # Rasterize and compress
        pix = temp_page.get_pixmap(dpi=72)
        img_bytes = pix.tobytes("jpeg", jpg_quality=10)

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
