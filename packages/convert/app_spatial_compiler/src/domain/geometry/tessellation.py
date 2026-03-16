from collections.abc import Sequence
from typing import Callable
from app_spatial_compiler.src.domain.models import SpatialNode

def _find_maximal_cut(nodes: Sequence[SpatialNode], axis: str) -> tuple[int | None, float, list[SpatialNode]]:
    get_min: Callable[[SpatialNode], float]
    get_max: Callable[[SpatialNode], float]

    if axis == 'x':
        sorted_nodes = sorted(nodes, key=lambda n: n.x0)
        get_min = lambda n: n.x0
        get_max = lambda n: n.x1
    else:
        sorted_nodes = sorted(nodes, key=lambda n: n.y0)
        get_min = lambda n: n.y0
        get_max = lambda n: n.y1

    best_gap = -1.0
    cut_idx = None
    max_ext = get_max(sorted_nodes[0])

    for i in range(1, len(sorted_nodes)):
        current_min = get_min(sorted_nodes[i])
        gap = current_min - max_ext
        
        if gap > best_gap:
            best_gap = gap
            cut_idx = i
            
        max_ext = max(max_ext, get_max(sorted_nodes[i]))

    return cut_idx, best_gap, sorted_nodes

def recursive_xy_cut(nodes: Sequence[SpatialNode], min_dx: float = 10.0, min_dy: float = 2.0) -> list[SpatialNode]:
    if len(nodes) <= 1:
        return list(nodes)

    x_idx, x_gap, x_sorted = _find_maximal_cut(nodes, 'x')
    y_idx, y_gap, y_sorted = _find_maximal_cut(nodes, 'y')

    x_ratio = (x_gap / min_dx) if x_gap is not None and x_gap >= min_dx else -1.0
    y_ratio = (y_gap / min_dy) if y_gap is not None and y_gap >= min_dy else -1.0

    if x_ratio < 0 and y_ratio < 0:
        return sorted(nodes, key=lambda n: (n.y0, n.x0))

    if x_ratio >= y_ratio:
        return recursive_xy_cut(x_sorted[:x_idx], min_dx, min_dy) + recursive_xy_cut(x_sorted[x_idx:], min_dx, min_dy)
    else:
        return recursive_xy_cut(y_sorted[:y_idx], min_dx, min_dy) + recursive_xy_cut(y_sorted[y_idx:], min_dx, min_dy)

def detect_graphical_voids(nodes: Sequence[SpatialNode], page_bounds: tuple[float, float, float, float]) -> list[tuple[float, float, float, float]]:
    """
    Identifies macroscopic empty regions in the manifold.
    Uses a simplified maximal empty rectangle approach relative to the page bounds.
    """
    if not nodes:
        return [page_bounds]
        
    # Heuristic: Find the largest gap between consecutive macroscopic blocks
    sorted_y = sorted(nodes, key=lambda n: n.y0)
    voids = []
    
    # Check gap between top margin and first node
    if sorted_y[0].y0 - page_bounds[1] > 50.0:
        voids.append((page_bounds[0], page_bounds[1], page_bounds[2], sorted_y[0].y0))
        
    # Check internal gaps (e.g., between a paragraph and its caption)
    for i in range(len(sorted_y) - 1):
        gap = sorted_y[i+1].y0 - sorted_y[i].y1
        if gap > 100.0: # Threshold for a figure void
            voids.append((page_bounds[0], sorted_y[i].y1, page_bounds[2], sorted_y[i+1].y0))
            
    return voids
