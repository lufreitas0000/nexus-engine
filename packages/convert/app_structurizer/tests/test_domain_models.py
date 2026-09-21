from pathlib import Path
import pytest
from src.domain.models import RawDocument, MarkdownAST

def test_raw_document_initialization_success(tmp_path: Path):
    file_path = tmp_path / "test.pdf"
    file_path.write_bytes(b"dummy_data")

    doc = RawDocument(file_path=file_path, file_size_bytes=10)

    assert doc.file_path == file_path
    assert doc.file_size_bytes == 10

def test_raw_document_file_not_found_raises_error():
    fake_path = Path("/tmp/does_not_exist.pdf")

    with pytest.raises(FileNotFoundError):
        RawDocument(file_path=fake_path, file_size_bytes=0)

def test_markdown_ast_immutability():
    ast = MarkdownAST(content="# Test", metadata={"key": "value"})

    assert ast.content == "# Test"
    assert ast.metadata == {"key": "value"}
