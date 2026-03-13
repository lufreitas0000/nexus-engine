"""
Structural Subtyping (Protocols) for the App Structurizer bounded context.
Enforces Dependency Inversion for all external computational modules.
"""

from typing import Protocol
from src.domain.models import RawDocument, MarkdownAST

class SpatialNode:
    """Represents a discrete C-level text node with its spatial bounds."""
    def __init__(self, char: str, x0: float, y0: float, x1: float, y1: float):
        self.char = char
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

class VisionExtractor(Protocol):
    """
    Solves the R^{H x W x C} -> MarkdownAST mapping.
    Handles full-page OCR for Q < 1.0 topologies.
    """
    def extract_ast(self, document: RawDocument) -> MarkdownAST: ...

class SpatialCompiler(Protocol):
    """
    Solves the discrete Graph -> MarkdownAST mapping.
    Handles formatting, LaTeX formulation, and layout for Q = 1.0 topologies.
    """
    def compile_graph(self, nodes: list[SpatialNode]) -> MarkdownAST: ...

class VisionEncoder(Protocol):
    """
    Solves the Image Sub-tensor -> Semantic String mapping.
    Generates ALT text.
    """
    def encode_tensor(self, image_bytes: bytes) -> str: ...
