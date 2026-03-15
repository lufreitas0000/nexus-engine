import heapq
from collections.abc import Sequence
from typing import Optional
from app_spatial_compiler.src.domain.models import SpatialNode

class KDTreeNode:
    __slots__ = ('node', 'centroid', 'left', 'right')
    
    def __init__(self, node: SpatialNode, centroid: tuple[float, float], left: Optional['KDTreeNode'], right: Optional['KDTreeNode']):
        self.node = node
        self.centroid = centroid
        self.left = left
        self.right = right

class SpatialKDTree:
    """
    A 2D spatial partition tree mapping the continuous Euclidean manifold 
    to discrete topological bounds, enabling O(log N) adjacency queries.
    """
    def __init__(self, nodes: Sequence[SpatialNode]):
        self._root = self._build_tree(list(nodes), depth=0)

    def _centroid(self, node: SpatialNode) -> tuple[float, float]:
        """Maps the rectangular bounds to a singular continuous coordinate."""
        return ((node.x0 + node.x1) / 2.0, (node.y0 + node.y1) / 2.0)

    def _build_tree(self, nodes: list[SpatialNode], depth: int) -> Optional[KDTreeNode]:
        if not nodes:
            return None
        
        axis = depth % 2
        # Deterministic sorting over the continuous orthogonal hyperplane
        nodes.sort(key=lambda n: self._centroid(n)[axis])
        
        median_idx = len(nodes) // 2
        median_node = nodes[median_idx]
        
        return KDTreeNode(
            node=median_node,
            centroid=self._centroid(median_node),
            left=self._build_tree(nodes[:median_idx], depth + 1),
            right=self._build_tree(nodes[median_idx + 1:], depth + 1)
        )

    def query_knn(self, target: SpatialNode, k: int) -> list[SpatialNode]:
        """
        Executes an O(log N) topological search to extract the K-nearest 
        mathematical components, rigorously excluding the target origin.
        """
        target_centroid = self._centroid(target)
        heap: list[tuple[float, int, SpatialNode]] = []
        
        def _search(current: Optional[KDTreeNode], depth: int) -> None:
            if current is None:
                return
            
            dx = current.centroid[0] - target_centroid[0]
            dy = current.centroid[1] - target_centroid[1]
            dist_sq = dx * dx + dy * dy
            
            # Mathematical exclusion: Do not map the target to its own adjacency graph
            if current.node is not target:
                if len(heap) < k:
                    heapq.heappush(heap, (-dist_sq, id(current.node), current.node))
                elif dist_sq < -heap[0][0]:
                    heapq.heappushpop(heap, (-dist_sq, id(current.node), current.node))
                    
            axis = depth % 2
            diff = target_centroid[axis] - current.centroid[axis]
            
            first_branch, second_branch = (current.left, current.right) if diff < 0 else (current.right, current.left)
            
            _search(first_branch, depth + 1)
            
            # Bounding box orthogonal intersection test to determine if the hyperplane must be crossed
            if len(heap) < k or (diff * diff) < -heap[0][0]:
                _search(second_branch, depth + 1)
                
        _search(self._root, depth=0)
        
        # Unwind the priority queue, reversing the max-heap scalar
        return [item[2] for item in sorted(heap, key=lambda x: -x[0])]
