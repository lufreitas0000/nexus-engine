from app_spatial_compiler.src.domain.models import SpatialNode, MarkdownAST
from app_spatial_compiler.src.domain.services.topology import GeometricParser

def test_baseline_clustering_reconstructs_1d_string(synthetic_paragraph_nodes: list[SpatialNode]) -> None:
    parser = GeometricParser(epsilon_font=2.0, space_threshold=1.5)
    
    ast = parser.compile_graph(synthetic_paragraph_nodes)
    
    assert isinstance(ast, MarkdownAST)
    assert ast.content == "Hi AI"
    assert ast.metadata["lines"] == "1"

def test_compile_graph_handles_empty_manifold() -> None:
    parser = GeometricParser()
    ast = parser.compile_graph([])
    
    assert ast.content == ""
    assert ast.metadata["status"] == "empty"
