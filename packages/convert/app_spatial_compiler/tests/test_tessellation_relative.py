import pytest
from app_spatial_compiler.src.domain.models import SpatialNode
from app_spatial_compiler.src.domain.geometry.tessellation import get_spatial_blocks, recursive_xy_cut

def test_recursive_xy_cut_relative_scaling():
    # Phase 2 implementation requirement: relative coordinate scales
    nodes_small = [
        SpatialNode(char="A", x0=10, y0=10, x1=12, y1=14),
        SpatialNode(char="B", x0=10, y0=20, x1=12, y1=24), # Gap dy=6
    ]

    # 2x scaled exact layout
    nodes_large = [
        SpatialNode(char="A", x0=20, y0=20, x1=24, y1=28),
        SpatialNode(char="B", x0=20, y0=40, x1=24, y1=48), # Gap dy=12
    ]

    # Static thresholds fail the larger scaling if not tuned
    b_small = get_spatial_blocks(nodes_small, min_dx=10, min_dy=5)
    b_large_static = get_spatial_blocks(nodes_large, min_dx=20, min_dy=5) # should easily split

    assert len(b_small) == 2
    assert len(b_large_static) == 2
