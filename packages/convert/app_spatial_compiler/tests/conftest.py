"""
Test-Driven Development (TDD) Axiom.
Defines synthetic geometric manifolds in continuous RAM to bypass disk I/O.
"""
import pytest
from app_spatial_compiler.src.domain.models import SpatialNode
from app_spatial_compiler.src.domain.ports import EquationFallbackPort

class FakeEquationFallbackAdapter:
    """
    Deterministic test double for complex LaTeX topological fallback.
    Intercepts bounding box bounds and returns a mathematically pure constant.
    """
    def resolve_subgraph(self, bounds: tuple[float, float, float, float]) -> str:
        return "\\int E \\cdot da"

@pytest.fixture
def fallback_adapter() -> EquationFallbackPort:
    return FakeEquationFallbackAdapter()

@pytest.fixture
def synthetic_superscript_nodes() -> list[SpatialNode]:
    """
    Synthesizes the geometric relationship for x^{2}.
    Node 'x' defines the baseline. Node '2' is shifted right and elevated.
    """
    return [
        SpatialNode(char="x", x0=10.0, y0=20.0, x1=15.0, y1=25.0),
        SpatialNode(char="2", x0=16.0, y0=15.0, x1=19.0, y1=19.0)
    ]

@pytest.fixture
def synthetic_fraction_nodes() -> list[SpatialNode]:
    """
    Synthesizes the geometric relationship for \\frac{1}{2}.
    Detects the horizontal fraction vector (node '-') intersecting the Y-axis.
    """
    return [
        SpatialNode(char="1", x0=12.0, y0=10.0, x1=14.0, y1=14.0),
        SpatialNode(char="-", x0=10.0, y0=15.0, x1=16.0, y1=16.0),
        SpatialNode(char="2", x0=12.0, y0=17.0, x1=14.0, y1=21.0)
    ]

@pytest.fixture
def synthetic_paragraph_nodes() -> list[SpatialNode]:
    """
    Synthesizes a standard 1D sequence mapping to two words on a single line.
    """
    return [
        SpatialNode(char="H", x0=10.0, y0=10.0, x1=12.0, y1=15.0),
        SpatialNode(char="i", x0=12.1, y0=10.0, x1=13.0, y1=15.0),
        # Space displacement implied by delta x0
        SpatialNode(char="A", x0=16.0, y0=10.0, x1=18.0, y1=15.0),
        SpatialNode(char="I", x0=18.1, y0=10.0, x1=19.0, y1=15.0)
    ]
