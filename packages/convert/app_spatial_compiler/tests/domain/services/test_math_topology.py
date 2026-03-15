from app_spatial_compiler.src.domain.models import SpatialNode
from app_spatial_compiler.src.domain.services.math_topology import MathTopologyResolver

def test_resolver_reduces_superscript_manifold(synthetic_superscript_nodes: list[SpatialNode]) -> None:
    """
    Asserts that the graph grammar detects a geometric elevation 
    (y-axis shift) relative to a baseline node and reduces it to a LaTeX superscript.
    """
    resolver = MathTopologyResolver()
    
    # Morphism application
    result = resolver.resolve_manifold(synthetic_superscript_nodes)
    
    # Topological Assertion
    assert result == "x^{2}"

def test_resolver_reduces_fraction_manifold(synthetic_fraction_nodes: list[SpatialNode]) -> None:
    """
    Asserts that the graph grammar detects a horizontal vector (fraction line) 
    intersecting the y-axis of surrounding nodes, partitioning them into a 
    numerator (above y0) and denominator (below y1).
    """
    resolver = MathTopologyResolver()
    
    # Morphism application
    result = resolver.resolve_manifold(synthetic_fraction_nodes)
    
    # Topological Assertion
    assert result == "\\frac{1}{2}"
