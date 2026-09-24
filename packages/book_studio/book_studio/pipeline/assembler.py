import re
import yaml
from pathlib import Path
from typing import List, Dict, Any
from nexus_schema import Document, Section, Paragraph, Metadata
from book_studio.core.schemas import ExtractionResult, Block, Page

class SemanticChunker:
    """Deterministically identifies headings and groups stitched blocks into atomic chapters/sections."""

    def __init__(self):
        # Matches "Chapter 1: Title", "1 Title", "Chapter 1 - Title"
        self.chap_regex = re.compile(r"^(?:Chapter\s+)?(\d+)\s*[:.-]?\s+(.+)$", re.IGNORECASE)
        # Matches "1.2 The Schrodinger Equation"
        self.sec_regex = re.compile(r"^(\d+)\.(\d+)\s+(.+)$")

        self.current_chapter = 0
        self.current_section = 0

    def _slugify(self, text: str) -> str:
        """Converts strings to standardized file names (e.g., 'The Schrodinger Equation' -> 'The_Schrodinger_Equation')."""
        clean_text = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip()
        return re.sub(r'[-\s]+', '_', clean_text)

    def verify_and_chunk(self, stitched_data: ExtractionResult) -> List[Dict[str, Any]]:
        chunks = []
        current_chunk = None

        for page in stitched_data.pages:
            for block in page.blocks:
                content = block.content.strip()
                if not content:
                    continue

                # Strip HTML tags for regex matching
                clean_text = re.sub(r'<[^>]+>', '', content).strip()

                is_header = block.block_type == "SectionHeader"
                chap_match = self.chap_regex.match(clean_text)
                sec_match = self.sec_regex.match(clean_text)

                # It's a new atomic chunk if it matches Chapter/Section regex OR is any SectionHeader
                if (is_header or chap_match or sec_match) and len(clean_text) < 150:
                    if current_chunk:
                        chunks.append(current_chunk)

                    if chap_match:
                        self.current_chapter = int(chap_match.group(1))
                        self.current_section = 0
                        title = chap_match.group(2)
                    elif sec_match:
                        self.current_chapter = int(sec_match.group(1))
                        self.current_section = int(sec_match.group(2))
                        title = sec_match.group(3)
                    else:
                        self.current_section += 1
                        title = clean_text

                    filename = f"{self.current_chapter:02d}_{self.current_section:02d}_{self._slugify(title)}"

                    current_chunk = {
                        "chapter": self.current_chapter,
                        "section": self.current_section,
                        "title": title,
                        "filename": filename,
                        "start_page": page.page_number,
                        "blocks": []
                    }
                else:
                    if current_chunk is None:
                        current_chunk = {
                            "chapter": 0,
                            "section": 0,
                            "title": "Frontmatter",
                            "filename": "00_00_Frontmatter",
                            "start_page": page.page_number,
                            "blocks": []
                        }
                    current_chunk["blocks"].append(content)

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

class Assembler:
    """Consumes semantic chunks and writes dual Markdown and LaTeX files."""

    def __init__(self, output_md: Path, output_tex: Path):
        self.output_md = output_md
        self.output_tex = output_tex
        self.output_md.mkdir(parents=True, exist_ok=True)
        self.output_tex.mkdir(parents=True, exist_ok=True)
        self.chunker = SemanticChunker()

    def assemble(self, stitched_data: ExtractionResult) -> None:
        chunks = self.chunker.verify_and_chunk(stitched_data)

        for chunk in chunks:
            self._write_markdown(chunk)
            self._write_tex(chunk)

    def _write_markdown(self, chunk: Dict[str, Any]) -> None:
        frontmatter = {
            "title": chunk["title"],
            "tags": ["physics", "quantum_mechanics", "raw_ingestion"],
            "page": chunk["start_page"],
            "status": "unverified",
            "alias": [],
            "chapter": chunk["chapter"],
            "section": chunk["section"]
        }

        yaml_header = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True)

        md_content = f"---\n{yaml_header}---\n\n"
        md_content += f"# {chunk['title']}\n\n"
        md_content += "\n\n".join(chunk["blocks"])

        md_file = self.output_md / f"{chunk['filename']}.md"
        md_file.write_text(md_content, encoding="utf-8")

    def _write_tex(self, chunk: Dict[str, Any]) -> None:
        # Frontmatter skipped for LaTeX; basic sectional mapping used instead
        tex_content = f"\\section{{{chunk['title']}}}\n\n" if chunk["section"] > 0 else f"\\chapter{{{chunk['title']}}}\n\n"
        tex_content += "\n\n".join(chunk["blocks"])

        tex_file = self.output_tex / f"{chunk['filename']}.tex"
        tex_file.write_text(tex_content, encoding="utf-8")

    def to_nexus_document(self, stitched_data: ExtractionResult) -> Document:
        """Converts assembled chunks into a canonical nexus_schema Document."""
        chunks = self.chunker.verify_and_chunk(stitched_data)
        sections = []
        for chunk in chunks:
            sections.append(
                Section(
                    title=chunk["title"],
                    content=[Paragraph(text=b) for b in chunk["blocks"] if b]
                )
            )
        return Document(
            metadata=Metadata(
                title=stitched_data.metadata.get("title"),
                author=stitched_data.metadata.get("author"),
                extra={"total_chunks": len(chunks), **stitched_data.metadata}
            ),
            sections=sections
        )
