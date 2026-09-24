from typing import Protocol
from document_converter.domain.model import ConvertedDocument

class DocumentConverter(Protocol):
    def convert(self, arxiv_id: str, main_file_path: str, output_dir: str) -> ConvertedDocument:
        """Converts the main document file into Markdown."""
        ...
