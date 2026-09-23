from collections.abc import Sequence
from semantic_pdf_splitter.spatial.domain.models import SpatialNode, MarkdownAST
from semantic_pdf_splitter.spatial.domain.ports import SpatialCompilerPort

class CompileDocumentUseCase:
    """
    Orchestrates the transformation of a 2D Euclidean manifold into a 
    1D syntactic tree by delegating pure mathematical operations to the Domain boundary.
    """
    def __init__(self, spatial_compiler: SpatialCompilerPort):
        self._spatial_compiler = spatial_compiler

    def execute(self, nodes: Sequence[SpatialNode]) -> MarkdownAST:
        """
        Routes the continuous topological data to the injected deterministic compiler.
        """
        return self._spatial_compiler.compile_graph(nodes)
