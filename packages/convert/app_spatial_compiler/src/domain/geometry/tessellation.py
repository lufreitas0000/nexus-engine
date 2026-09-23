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

    if not sorted_nodes:
        return None, -1.0, []

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

def get_spatial_blocks(nodes: Sequence[SpatialNode], min_dx: float = -1.0, min_dy: float = -1.0) -> list[list[SpatialNode]]:
    """
    Partitions a 2D Euclidean manifold into discrete blocks using recursive XY-cuts.
    If dx/dy thresholds are < 0, dynamically scales them to the median manifold size.
    """
    if not nodes:
        return []
    if len(nodes) <= 1:
        return [list(nodes)]

    # Dynamic scaling Phase 2
    if min_dx < 0 or min_dy < 0:
        w_vals = sorted(n.width for n in nodes if n.width > 0)
        h_vals = sorted(n.height for n in nodes if n.height > 0)
        if w_vals and h_vals:
            median_w = w_vals[len(w_vals)//2]
            median_h = h_vals[len(h_vals)//2]
            min_dx = min_dx if min_dx > 0 else median_w * 2.0
            min_dy = min_dy if min_dy > 0 else median_h * 0.5
        else:
            min_dx = 10.0
            min_dy = 2.0

    x_idx, x_gap, x_sorted = _find_maximal_cut(nodes, 'x')
    y_idx, y_gap, y_sorted = _find_maximal_cut(nodes, 'y')

    x_ratio = (x_gap / min_dx) if x_gap is not None and x_gap >= min_dx else -1.0
    y_ratio = (y_gap / min_dy) if y_gap is not None and y_gap >= min_dy else -1.0

    if x_ratio < 0 and y_ratio < 0:
        return [list(nodes)]

    if y_ratio >= x_ratio:
        return get_spatial_blocks(y_sorted[:y_idx], min_dx, min_dy) + \
               get_spatial_blocks(y_sorted[y_idx:], min_dx, min_dy)
    else:
        left_nodes = sorted(x_sorted[:x_idx], key=lambda n: n.y0)
        right_nodes = sorted(x_sorted[x_idx:], key=lambda n: n.y0)
        return get_spatial_blocks(left_nodes, min_dx, min_dy) + \
               get_spatial_blocks(right_nodes, min_dx, min_dy)

def recursive_xy_cut(nodes: Sequence[SpatialNode], min_dx: float = -1.0, min_dy: float = -1.0) -> list[SpatialNode]:
    # Dynamic thresholds fallback Phase 2
    if min_dx < 0 or min_dy < 0:
        w_vals = sorted(n.width for n in nodes if n.width > 0)
        h_vals = sorted(n.height for n in nodes if n.height > 0)
        if w_vals and h_vals:
            median_w = w_vals[len(w_vals)//2]
            median_h = h_vals[len(h_vals)//2]
            min_dx = min_dx if min_dx > 0 else median_w * 2.0
            min_dy = min_dy if min_dy > 0 else median_h * 0.5
        else:
            min_dx = 10.0
            min_dy = 2.0

    x_idx, x_gap, x_sorted = _find_maximal_cut(nodes, 'x')

    if x_gap is not None and x_gap >= min_dx:
        left_col = recursive_xy_cut(x_sorted[:x_idx], min_dx, min_dy)
        right_col = recursive_xy_cut(x_sorted[x_idx:], min_dx, min_dy)
        return left_col + right_col

    blocks = get_spatial_blocks(nodes, min_dx, min_dy)
    flattened = []
    for block in blocks:
        flattened.extend(sorted(block, key=lambda n: (n.y0, n.x0)))
    return flattened

def detect_graphical_voids(nodes: Sequence[SpatialNode], page_bounds: tuple[float, float, float, float]) -> list[tuple[float, float, float, float]]:
    if not nodes:
        return [page_bounds]
    sorted_y = sorted(nodes, key=lambda n: n.y0)
    voids = []
    if sorted_y[0].y0 - page_bounds[1] > 50.0:
        voids.append((page_bounds[0], page_bounds[1], page_bounds[2], sorted_y[0].y0))
    for i in range(len(sorted_y) - 1):
        gap = sorted_y[i+1].y0 - sorted_y[i].y1
        if gap > 100.0:
            voids.append((page_bounds[0], sorted_y[i].y1, page_bounds[2], sorted_y[i+1].y0))
    return voids
