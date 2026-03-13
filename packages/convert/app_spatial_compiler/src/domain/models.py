"""
Immutable memory structures for the Spatial Compiler domain.
Defines the mapping between continuous geometric bounds and discrete Unicode nodes.
"""

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class SpatialNode:
    """
    A discrete Unicode character mapped to a Euclidean bounding box.
    Memory is slotted to ensure contiguous allocation for O(N log N) projection sorts.
    """
    char: str
    x0: float
    y0: float
    x1: float
    y1: float

@dataclass(frozen=True, slots=True)
class MarkdownAST:
    """
    The final 1D discrete representation of the spatially compiled graph.
    """
    content: str
    metadata: dict[str, str]
