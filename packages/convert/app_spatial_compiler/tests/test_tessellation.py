import pytest
from app_spatial_compiler.src.domain.models import SpatialNode
from app_spatial_compiler.src.domain.geometry.tessellation import get_spatial_blocks, recursive_xy_cut

def test_recursive_xy_cut_separates_columns():
    nodes = [
        # Left Column
        SpatialNode(char="1", x0=10, y0=10, x1=20, y1=20),
        SpatialNode(char="2", x0=10, y0=30, x1=20, y1=40),
        # Right Column
        SpatialNode(char="3", x0=100, y0=10, x1=110, y1=20),
        SpatialNode(char="4", x0=100, y0=30, x1=110, y1=40),
    ]

    blocks = get_spatial_blocks(nodes, min_dx=50.0, min_dy=5.0)
    assert len(blocks) == 4  # Should split into 4 individual text blocks since dx/dy thresholds are met

    # Topological Reading Order: Left col first, then Right col
    flattened = recursive_xy_cut(nodes, min_dx=50.0, min_dy=5.0)
    chars = [n.char for n in flattened]
    assert chars == ["1", "2", "3", "4"]

def test_recursive_xy_cut_handles_empty():
    assert recursive_xy_cut([]) == []
