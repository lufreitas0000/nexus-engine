from collections.abc import Sequence
from app_spatial_compiler.src.domain.models import SpatialNode
from app_spatial_compiler.src.domain.geometry.spatial_tree import SpatialKDTree

class MathTopologyResolver:
    """
    Applies multi-directional graph grammars to resolve tensors, 
    prescripts, and complex fractions.
    """
    def resolve_manifold(self, nodes: Sequence[SpatialNode]) -> str:
        if not nodes:
            return ""

        # 1. Fraction Resolution
        fraction_lines = [n for n in nodes if n.char == "-" and (n.x1 - n.x0) > (n.y1 - n.y0) * 1.5]
        if fraction_lines:
            frac_line = fraction_lines[0]
            numerator = [n for n in nodes if n.y1 <= frac_line.y0 and n is not frac_line]
            denominator = [n for n in nodes if n.y0 >= frac_line.y1 and n is not frac_line]
            if numerator and denominator:
                return f"\\frac{{{self.resolve_manifold(numerator)}}}{{{self.resolve_manifold(denominator)}}}"

        # 2. Sequential Baseline with Multi-Index Support
        tree = SpatialKDTree(list(nodes))
        sorted_nodes = sorted(nodes, key=lambda n: n.x0)
        buffer = ""
        processed: set[int] = set()

        for node in sorted_nodes:
            if id(node) in processed: continue
            
            # Identify Prescripts (Left-side attachments)
            # Before adding the base node, check if any UNPROCESSED neighbors are to its left
            neighbors = tree.query_knn(node, k=5)
            h_base = node.y1 - node.y0
            
            left_super = [nn for nn in neighbors if id(nn) not in processed and nn.x1 <= node.x0 and nn.y1 <= node.y0 + (h_base * 0.2)]
            left_sub = [nn for nn in neighbors if id(nn) not in processed and nn.x1 <= node.x0 and nn.y0 >= node.y1 - (h_base * 0.2)]
            
            if left_super:
                buffer += f"^{{{''.join(n.char for n in sorted(left_super, key=lambda n: n.x0))}}}"
                for n in left_super: processed.add(id(n))
            if left_sub:
                buffer += f"_{{{''.join(n.char for n in sorted(left_sub, key=lambda n: n.x0))}}}"
                for n in left_sub: processed.add(id(n))

            buffer += node.char
            processed.add(id(node))

            # Identify Right-side Multi-Indices (Levi-Civita, Christoffel)
            right_super = []
            right_sub = []
            
            for nn in neighbors:
                if id(nn) in processed: continue
                h_nn = nn.y1 - nn.y0
                
                # Invariant: Sub/superscripts are smaller and shifted right
                is_smaller = h_nn < h_base * 0.95
                is_right = nn.x0 >= node.x1 - 2.0
                
                if is_smaller and is_right:
                    if nn.y1 <= node.y0 + (h_base * 0.5): # Superscript elevation
                        right_super.append(nn)
                    elif nn.y0 >= node.y1 - (h_base * 0.5): # Subscript depression
                        right_sub.append(nn)

            if right_super:
                buffer += f"^{{{''.join(n.char for n in sorted(right_super, key=lambda n: n.x0))}}}"
                for n in right_super: processed.add(id(n))
            if right_sub:
                buffer += f"_{{{''.join(n.char for n in sorted(right_sub, key=lambda n: n.x0))}}}"
                for n in right_sub: processed.add(id(n))
                
        return buffer
