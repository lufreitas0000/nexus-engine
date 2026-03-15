from collections.abc import Sequence
from app_spatial_compiler.src.domain.models import SpatialNode, MarkdownAST

class GeometricParser:
    def __init__(self, epsilon_font: float = 2.0, space_threshold: float = 1.5):
        self.epsilon_font = epsilon_font
        self.space_threshold = space_threshold

    def compile_graph(self, nodes: Sequence[SpatialNode]) -> MarkdownAST:
        if not nodes:
            return MarkdownAST(content="", metadata={"status": "empty"})

        sorted_nodes = sorted(nodes, key=lambda n: (n.y0, n.x0))
        lines: list[list[SpatialNode]] = []
        current_line: list[SpatialNode] = [sorted_nodes[0]]

        for node in sorted_nodes[1:]:
            if abs(node.y0 - current_line[0].y0) <= self.epsilon_font:
                current_line.append(node)
            else:
                lines.append(current_line)
                current_line = [node]
        lines.append(current_line)

        buffer = []
        for line in lines:
            line_str = ""
            for i, node in enumerate(line):
                if i > 0 and (node.x0 - line[i-1].x1) > self.space_threshold:
                    line_str += " "
                line_str += node.char
            buffer.append(line_str)

        return MarkdownAST(
            content="\n".join(buffer),
            metadata={"lines": str(len(lines))}
        )
