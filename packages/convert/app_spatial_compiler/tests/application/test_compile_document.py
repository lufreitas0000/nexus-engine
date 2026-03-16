from collections.abc import Sequence
from app_spatial_compiler.src.domain.models import SpatialNode, MarkdownAST
from app_spatial_compiler.src.domain.ports import SpatialCompilerPort
from app_spatial_compiler.src.application.use_cases.compile_document import CompileDocumentUseCase

class FakeSpatialCompiler(SpatialCompilerPort):
    """
    Deterministic test double to isolate Use Case orchestration
    from the O(N log N) geometric transformations.
    """
    def compile_graph(self, nodes: Sequence[SpatialNode]) -> MarkdownAST:
        return MarkdownAST(content="orchestrated_output", metadata={"nodes_processed": str(len(nodes))})

def test_use_case_delegates_to_spatial_port() -> None:
    """
    Asserts the Dependency Inversion boundary. The Use Case must route
    the Euclidean manifold to the injected compiler port without mutating the state.
    """
    synthetic_nodes = [
        SpatialNode(char="T", x0=0.0, y0=0.0, x1=1.0, y1=1.0),
        SpatialNode(char="D", x0=1.0, y0=0.0, x1=2.0, y1=1.0),
        SpatialNode(char="D", x0=2.0, y0=0.0, x1=3.0, y1=1.0)
    ]
    
    port = FakeSpatialCompiler()
    use_case = CompileDocumentUseCase(spatial_compiler=port)
    
    ast = use_case.execute(synthetic_nodes)
    
    assert isinstance(ast, MarkdownAST)
    assert ast.content == "orchestrated_output"
    assert ast.metadata["nodes_processed"] == "3"
