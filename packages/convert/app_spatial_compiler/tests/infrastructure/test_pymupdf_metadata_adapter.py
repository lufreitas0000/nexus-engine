import json
import pytest
import fitz  # type: ignore
from app_spatial_compiler.src.domain.models import DocumentStructure, BookmarkNode
from app_spatial_compiler.src.infrastructure.adapters.pymupdf_extractor import (
    PyMuPDFMetadataAdapter,
)


@pytest.fixture
def sample_pdf_with_toc() -> bytes:
    """Generate a synthetic PDF with a Table of Contents in memory."""
    doc = fitz.open()
    doc.new_page()
    doc.new_page()

    # TOC format for fitz.set_toc: [level, title, page, dest_dict]
    toc = [[1, "Chapter 1", 1], [2, "Section 1.1", 1], [1, "Chapter 2", 2]]
    doc.set_toc(toc)

    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def test_extract_structure_from_bytes(sample_pdf_with_toc: bytes):
    """Test that the adapter can extract TOC bookmarks from an in-memory PDF."""
    adapter = PyMuPDFMetadataAdapter()
    structure = adapter.extract_structure(sample_pdf_with_toc)

    assert isinstance(structure, DocumentStructure)
    assert len(structure.bookmarks) == 3

    b1, b2, b3 = structure.bookmarks

    assert b1.level == 1
    assert b1.title == "Chapter 1"
    assert b1.page == 1

    assert b2.level == 2
    assert b2.title == "Section 1.1"
    assert b2.page == 1

    assert b3.level == 1
    assert b3.title == "Chapter 2"
    assert b3.page == 2


def test_to_markdown_json(sample_pdf_with_toc: bytes):
    """Test that the intermediate structure correctly compiles to JSON."""
    adapter = PyMuPDFMetadataAdapter()
    structure = adapter.extract_structure(sample_pdf_with_toc)

    json_str = adapter.to_markdown_json(structure)
    data = json.loads(json_str)

    assert "bookmarks" in data
    assert len(data["bookmarks"]) == 3

    assert data["bookmarks"][0]["title"] == "Chapter 1"
    assert data["bookmarks"][0]["level"] == 1

    assert data["bookmarks"][1]["title"] == "Section 1.1"
    assert data["bookmarks"][1]["level"] == 2


def test_extract_structure_empty_or_invalid():
    """Test fallback when given empty bytes or invalid PDF."""
    adapter = PyMuPDFMetadataAdapter()
    structure = adapter.extract_structure(b"invalid pdf data")

    assert isinstance(structure, DocumentStructure)
    assert len(structure.bookmarks) == 0
