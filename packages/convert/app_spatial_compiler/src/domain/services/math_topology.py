import statistics
from collections.abc import Sequence
from pylatexenc.latexencode import unicode_to_latex
from app_spatial_compiler.src.domain.models import SpatialNode
from app_spatial_compiler.src.domain.geometry.spatial_tree import SpatialKDTree

class MathTopologyResolver:
    def _get_ref_height(self, nodes: Sequence[SpatialNode]) -> float:
        if not nodes: return 12.0
        vals = [n.font_size if n.font_size else n.height for n in nodes]
        return float(statistics.median(vals))

    def _to_latex(self, char: str) -> str:
        return unicode_to_latex(char)

    def resolve_manifold(self, nodes: Sequence[SpatialNode]) -> str:
        if not nodes: return ""
        ref_h = self._get_ref_height(nodes)
        
        # 1. Fraction Resolution
        fraction_lines = [n for n in nodes if n.char == "-" and n.width > ref_h * 0.4]
        if fraction_lines:
            frac = fraction_lines[0]
            num = [n for n in nodes if n.y1 <= frac.y0 and n is not frac]
            den = [n for n in nodes if n.y0 >= frac.y1 and n is not frac]
            if num and den:
                return f"\\frac{{{self.resolve_manifold(num)}}}{{{self.resolve_manifold(den)}}}"

        # 2. Sequential Graph Grammar
        tree = SpatialKDTree(list(nodes))
        sorted_nodes = sorted(nodes, key=lambda n: n.x0)
        buffer = ""
        processed: set[int] = set()

        for node in sorted_nodes:
            if id(node) in processed: continue
            
            # Adjacency query
            neighbors = tree.query_knn(node, k=5)
            buffer += self._to_latex(node.char)
            processed.add(id(node))

            # Right-side Multi-Index (Sub/Super)
            right_super = []
            right_sub = []
            for n in neighbors:
                if id(n) in processed: continue
                # Tighten contiguity for superscripts
                if (n.x0 - node.x1) > ref_h * 0.4: continue
                
                # Use centroid-based elevation for more robust sub/super detection
                if n.centroid[1] < node.y0 + (ref_h * 0.2):
                    right_super.append(n)
                elif n.centroid[1] > node.y1 - (ref_h * 0.2):
                    right_sub.append(n)

            if right_super:
                buffer += f"^{{{''.join(self._to_latex(n.char) for n in sorted(right_super, key=lambda n: n.x0))}}}"
                for n in right_super: processed.add(id(n))
            if right_sub:
                buffer += f"_{{{''.join(self._to_latex(n.char) for n in sorted(right_sub, key=lambda n: n.x0))}}}"
                for n in right_sub: processed.add(id(n))
                
        return buffer
