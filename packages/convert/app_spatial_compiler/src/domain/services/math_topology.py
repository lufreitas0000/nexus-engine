from collections.abc import Sequence
from app_spatial_compiler.src.domain.models import SpatialNode
from app_spatial_compiler.src.domain.geometry.spatial_tree import SpatialKDTree

SYMBOL_MAP = {
    "μ": "\\mu", "ν": "\\nu", "α": "\\alpha", "β": "\\beta", "γ": "\\gamma",
    "δ": "\\delta", "ε": "\\epsilon", "π": "\\pi", "Σ": "\\Sigma", "Δ": "\\Delta"
}

class MathTopologyResolver:
    """
    Resolves 2D manifolds into 1D LaTeX syntax with symbol mapping 
    and proximity-aware topological attachments.
    """
    def _to_latex(self, char: str) -> str:
        return SYMBOL_MAP.get(char, char)

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

        # 2. Baseline and Multi-Index Resolution
        tree = SpatialKDTree(list(nodes))
        sorted_nodes = sorted(nodes, key=lambda n: n.x0)
        buffer = ""
        processed: set[int] = set()

        for node in sorted_nodes:
            if id(node) in processed:
                continue
            
            h_base = node.y1 - node.y0
            w_base = node.x1 - node.x0
            neighbors = tree.query_knn(node, k=5)

            # Prescript Detection (Left-side)
            left_super = [nn for nn in neighbors if id(nn) not in processed and nn.x1 <= node.x0 and (node.x0 - nn.x1) < w_base and nn.y1 <= node.y0 + (h_base * 0.3)]
            left_sub = [nn for nn in neighbors if id(nn) not in processed and nn.x1 <= node.x0 and (node.x0 - nn.x1) < w_base and nn.y0 >= node.y1 - (h_base * 0.3)]
            
            if left_super:
                buffer += f"^{{{''.join(self._to_latex(n.char) for n in sorted(left_super, key=lambda n: n.x0))}}}"
                for n in left_super: processed.add(id(n))
            if left_sub:
                buffer += f"_{{{''.join(self._to_latex(n.char) for n in sorted(left_sub, key=lambda n: n.x0))}}}"
                for n in left_sub: processed.add(id(n))

            buffer += self._to_latex(node.char)
            processed.add(id(node))

            # Right-side Multi-Index Detection
            right_super = []
            right_sub = []
            
            for nn in neighbors:
                if id(nn) in processed: continue
                # Proximity Invariant: Attachments must be locally contiguous
                # We limit the horizontal search to 50% of the base width or a small constant
                if (nn.x0 - node.x1) > max(w_base * 0.5, 5.0): continue
                
                if nn.y1 <= node.y0 + (h_base * 0.4):
                    right_super.append(nn)
                elif nn.y0 >= node.y1 - (h_base * 0.4):
                    right_sub.append(nn)

            if right_super:
                buffer += f"^{{{''.join(self._to_latex(n.char) for n in sorted(right_super, key=lambda n: n.x0))}}}"
                for n in right_super: processed.add(id(n))
            if right_sub:
                buffer += f"_{{{''.join(self._to_latex(n.char) for n in sorted(right_sub, key=lambda n: n.x0))}}}"
                for n in right_sub: processed.add(id(n))
                
        return buffer
