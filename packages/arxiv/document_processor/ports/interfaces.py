from typing import Protocol
from document_processor.domain.model import ProcessedDocument

class DocumentProcessor(Protocol):
    def process_archive(self, arxiv_id: str, archive_path: str, extract_dir: str) -> ProcessedDocument:
        """Processes the downloaded archive and finds the main document file."""
        ...
