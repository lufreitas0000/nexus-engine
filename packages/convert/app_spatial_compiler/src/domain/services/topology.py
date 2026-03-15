from collections.abc import Sequence
from app_spatial_compiler.src.domain.models import SpatialNode, MarkdownAST
from app_spatial_compiler.src.domain.geometry.tessellation import recursive_xy_cut

class GeometricParser:
    def __init__(self, epsilon_font: float = 2.0, space_threshold: float = 1.5, min_dx: float = 10.0, min_dy: float = 2.0):
        self.epsilon_font = epsilon_font
        self.space_threshold = space_threshold
        self.min_dx = min_dx
        self.min_dy = min_dy

    def compile_graph(self, nodes: Sequence[SpatialNode]) -> MarkdownAST:
        if not nodes:
            return MarkdownAST(content="", metadata={"status": "empty"})

        # 1. Global Topological Partial Ordering
        topologically_ordered_nodes = recursive_xy_cut(nodes, min_dx=self.min_dx, min_dy=self.min_dy)

        # 2. Baseline Clustering (O(N) sequential pass over the ordered tree)
        lines: list[list[SpatialNode]] = []
        current_line: list[SpatialNode] = [topologically_ordered_nodes[0]]

        for node in topologically_ordered_nodes[1:]:
            if abs(node.y0 - current_line[0].y0) <= self.epsilon_font:
                current_line.append(node)
            else:
                lines.append(current_line)
                current_line = [node]
        lines.append(current_line)

        # 3. Local Synthesis and String Buffer Allocation
        buffer = []
        for line in lines:
            # Sort local baseline strictly by x0
            line_sorted = sorted(line, key=lambda n: n.x0)
            line_str = ""
            for i, node in enumerate(line_sorted):
                if i > 0 and (node.x0 - line_sorted[i-1].x1) > self.space_threshold:
                    line_str += " "
                line_str += node.char
            buffer.append(line_str)

        return MarkdownAST(
            content="\n".join(buffer),
            metadata={"lines": str(len(lines))}
        )
