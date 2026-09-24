"""
Structural subtyping definitions.
Enforces Dependency Inversion for the spatial mapping and effectful fallbacks.
"""
from collections.abc import Sequence
from typing import Protocol

from .models import SpatialNode, MarkdownAST

class SpatialCompilerPort(Protocol):
    """Protocol for the deterministic geometric parser."""
    def compile_graph(self, nodes: Sequence[SpatialNode]) -> MarkdownAST: ...

class EquationFallbackPort(Protocol):
    """Protocol for delegating complex topological failures to an ML adapter."""
    def resolve_subgraph(self, bounds: tuple[float, float, float, float]) -> str: ...

from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass
