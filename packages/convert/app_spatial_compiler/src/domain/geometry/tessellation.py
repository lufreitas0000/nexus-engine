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
