from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from nexus_schema import Document, Section, Paragraph, Metadata

class Block(BaseModel):
    id: str
    block_type: str
    content: Optional[str] = ""
    polygon: Optional[List[List[float]]] = None

class Page(BaseModel):
    page_number: Optional[int] = None
    blocks: List[Block] = Field(default_factory=list)

class ExtractionResult(BaseModel):
    metadata: Dict[str, Any] = Field(default_factory=dict)
    pages: List[Page] = Field(default_factory=list)

    def to_nexus_document(self) -> Document:
        """Converts extraction result into a canonical nexus_schema Document."""
        sections = []
        for page in self.pages:
            content_paragraphs = [
                Paragraph(text=b.content or "") for b in page.blocks if b.content
            ]
            title = f"Page {page.page_number}" if page.page_number is not None else None
            sections.append(Section(title=title, content=content_paragraphs))
        return Document(
            metadata=Metadata(
                title=self.metadata.get("title"),
                author=self.metadata.get("author"),
                extra={k: v for k, v in self.metadata.items() if k not in ("title", "author")}
            ),
            sections=sections
        )

    @classmethod
    def from_nexus_document(cls, doc: Document) -> "ExtractionResult":
        """Reconstructs ExtractionResult from a canonical nexus_schema Document."""
        pages = []
        for i, sec in enumerate(doc.sections, 1):
            blocks = []
            for j, p in enumerate(sec.content, 1):
                b_type = "SectionHeader" if j == 1 and p.text.startswith("Chapter") else "Text"
                blocks.append(Block(id=str(j), block_type=b_type, content=p.text))
            pages.append(Page(page_number=i, blocks=blocks))
        meta = {**doc.metadata.extra}
        if doc.metadata.title:
            meta["title"] = doc.metadata.title
        if doc.metadata.author:
            meta["author"] = doc.metadata.author
        return cls(metadata=meta, pages=pages)
