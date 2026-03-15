from collections.abc import Sequence
from app_spatial_compiler.src.domain.models import SpatialNode
from app_spatial_compiler.src.domain.geometry.spatial_tree import SpatialKDTree

class MathTopologyResolver:
    """
    Applies deterministic graph grammars to continuous 2D manifolds 
    to extract 1D LaTeX mathematical syntax.
    """
    def resolve_manifold(self, nodes: Sequence[SpatialNode]) -> str:
        if not nodes:
            return ""

        # 1. Fraction Topology Resolution
        # Detect horizontal vectors where width strictly exceeds height
        fraction_lines = [n for n in nodes if n.char == "-" and (n.x1 - n.x0) > (n.y1 - n.y0) * 1.5]
        
        if fraction_lines:
            frac_line = fraction_lines[0]
            # Partition the Euclidean subspace strictly by the vector's orthogonal bounds
            numerator = [n for n in nodes if n.y1 <= frac_line.y0 and n is not frac_line]
            denominator = [n for n in nodes if n.y0 >= frac_line.y1 and n is not frac_line]
            
            if numerator and denominator:
                num_str = self.resolve_manifold(numerator)
                den_str = self.resolve_manifold(denominator)
                return f"\\frac{{{num_str}}}{{{den_str}}}"

        # 2. Sequential Baseline and Sub/Superscript Resolution
        tree = SpatialKDTree(list(nodes))
        sorted_nodes = sorted(nodes, key=lambda n: n.x0)
        
        buffer = ""
        processed: set[int] = set()
        
        for node in sorted_nodes:
            if id(node) in processed:
                continue
                
            buffer += node.char
            processed.add(id(node))
            
            # O(log N) adjacency query for topological attachments
            neighbors = tree.query_knn(node, k=1)
            if not neighbors:
                continue
                
            nn = neighbors[0]
            if id(nn) in processed:
                continue
                
            # Topological Invariant: Superscript elevation
            # The neighbor must be shifted right and its bottom edge must exceed the base node's top edge
            is_superscript = (nn.x0 > node.x0) and (nn.y1 <= node.y0 + 2.0)
            
            if is_superscript:
                buffer += f"^{{{nn.char}}}"
                processed.add(id(nn))
                
        return buffer
