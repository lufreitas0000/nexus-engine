# app_spatial_compiler/src/domain/models.py
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True, slots=True)
class SpatialNode:
    """
    A discrete Unicode node mapped to Euclidean bounds.
    Slotted for memory contiguity and performance.
    """
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
