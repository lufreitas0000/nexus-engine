from collections.abc import Sequence
from semantic_pdf_splitter.spatial.domain.models import SpatialNode

class MarkdownSynthesizer:
    def __init__(self, median_width: float, median_height: float):
        self.median_width = median_width
        self.median_height = median_height

    def synthesize_text(self, block: Sequence[SpatialNode]) -> str:
        sorted_block = sorted(block, key=lambda n: (n.y0, n.x0))
        text = ""
        last_y = -1.0
        last_x = -1.0

        for i, node in enumerate(sorted_block):
            # Line break heuristic
            if last_y > 0 and (node.y0 - last_y) > self.median_height * 0.5:
                text += "\n"
                last_x = -1.0

            # Space insertion heuristic
            if last_x > 0 and (node.x0 - last_x) > self.median_width * 0.8:
                # specifically for lists: don't double space if previous char was a space
                if not text.endswith(" "):
                    text += " "

            text += node.char
            last_y = node.y0
            last_x = node.x1

        return text.strip()

class StructuralDispatcher:
    def __init__(self, synthesizer: MarkdownSynthesizer):
        self.synthesizer = synthesizer

    def generate_ast(self, blocks: list[list[SpatialNode]]) -> str:
        md_blocks = []
        for block in blocks:
            if not block:
                continue

            text = self.synthesizer.synthesize_text(block)
            if not text:
                continue

            avg_font = sum(n.font_size for n in block if n.font_size) / max(len(block), 1)
            is_header = avg_font > self.synthesizer.median_height * 1.3

            if is_header and "\n" not in text:
                md_blocks.append(f"# {text}")
            else:
                # Detect bullet lists via heuristic
                if text.startswith("- ") or text.startswith("• "):
                    # ensure proper md formatting for multi-line list items
                    md_blocks.append(text)
                else:
                    md_blocks.append(text.replace("\n", " ")) # naive unwrap for standard text

        return "\n\n".join(md_blocks)
