# app_structurizer/src/domain/models.py
"""
Immutable representations of the document states.
Mapped directly to contiguous memory blocks.
"""

from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class RawDocument:
    """
    Represents the continuous space of the unparsed PDF.
    This is essentially a pointer to a sequence of bytes (raster or vector) on disk.
    """
    file_path: Path
    file_size_bytes: int

    def __post_init__(self) -> None:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Binary tensor not found at {self.file_path}")

@dataclass(frozen=True)
class MarkdownAST:
    """
    The discrete topological representation of the document.
    A raw string buffer formatted in Markdown, acting as the Abstract Syntax Tree.
    """
    content: str
    metadata: dict[str, str]
