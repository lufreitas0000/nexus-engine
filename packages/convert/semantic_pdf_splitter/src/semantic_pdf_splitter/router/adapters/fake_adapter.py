from semantic_pdf_splitter.router.domain.ports import VisionExtractor
from semantic_pdf_splitter.router.domain.models import RawDocument, MarkdownAST

class FakeVisionExtractor(VisionExtractor):
    def extract_ast(self, document: RawDocument) -> MarkdownAST:
        return MarkdownAST(
            content=f"# Mocked extraction for {document.file_path.name}",
            metadata={"adapter": "FakeVisionExtractor"}
        )
