from dataclasses import dataclass
from typing import Optional
from enum import Enum, auto

class BlockType(Enum):
    """
    Categorization of Euclidean manifolds based on typographic intent.
    Used to select the appropriate 1D synthesis morphism.
    """
    TEXT = auto()      # Standard body paragraphs
    MATH = auto()      # Display or inline LaTeX manifolds
    HEADER = auto()    # Structural headings (# , ##)
    ITEMIZE = auto()   # Bulleted or numbered lists
    FIGURE = auto()    # Visual voids delegated to VLM
    TABLE = auto()     # Grid-aligned tabular data

@dataclass(frozen=True, slots=True)
class SpatialNode:
    char: str
    x0: float
    y0: float
    x1: float
    y1: float
    font_size: Optional[float] = None

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def centroid(self) -> tuple[float, float]:
        return ((self.x0 + self.x1) / 2.0, (self.y0 + self.y1) / 2.0)

@dataclass(frozen=True, slots=True)
class MarkdownAST:
    content: str
    metadata: dict[str, str]
