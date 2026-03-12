import pytest
import fitz  # type: ignore
from pathlib import Path
from src.domain.models import RawDocument, MarkdownAST
from src.domain.ports import VisionExtractor

FIXTURE_DIR = Path(__file__).parent / "fixtures"

class FakeVisionExtractor:
    def extract_ast(self, document: RawDocument) -> MarkdownAST:
        return MarkdownAST(
            content=f"# Simulated Chapter for {document.file_path.name}\n\nMocked extraction.",
            metadata={"confidence": "0.99", "model": "FakeAdapter_v1"}
        )

@pytest.fixture(scope="session")
def fake_extractor() -> VisionExtractor:
    return FakeVisionExtractor()

@pytest.fixture(scope="session")
def degraded_raster_book_path() -> Path:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIXTURE_DIR / "old_scanned_book.pdf"
    if out_path.exists(): return out_path

    final_doc = fitz.open()
    temp_doc = fitz.open()
    
    for i in range(50):
        temp_page = temp_doc.new_page()
        temp_page.insert_text(fitz.Point(50, 50), f"Chapter {i}", fontsize=24)
        temp_page.insert_text(fitz.Point(50, 100), "Degraded raster text payload.", fontsize=12)
        
        pix = temp_page.get_pixmap(dpi=72)
        img_bytes = pix.tobytes("jpeg", jpg_quality=10) 
        
        final_page = final_doc.new_page(width=pix.width, height=pix.height)
        final_page.insert_image(final_page.rect, stream=img_bytes)
        
    final_doc.save(str(out_path))
    temp_doc.close()
    final_doc.close()
    return out_path

@pytest.fixture(scope="session")
def clean_vector_book_path() -> Path:
    """Synthesizes a modern, purely vector-based PDF (no rasters/images)."""
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIXTURE_DIR / "modern_vector_book.pdf"
    if out_path.exists(): return out_path

    doc = fitz.open()
    for i in range(5):
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), f"Modern Chapter {i}", fontsize=20)
        page.insert_text(fitz.Point(50, 90), "This text exists as pure math vectors.", fontsize=10)
    doc.save(str(out_path))
    doc.close()
    return out_path

@pytest.fixture
def raw_document(degraded_raster_book_path: Path) -> RawDocument:
    return RawDocument(file_path=degraded_raster_book_path, file_size_bytes=degraded_raster_book_path.stat().st_size)
