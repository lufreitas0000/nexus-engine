import statistics
import re
from collections.abc import Sequence
from app_spatial_compiler.src.domain.models import SpatialNode, BlockType

class BlockClassifier:
    """
    Classifies 2D manifolds into semantic types using typographic 
    ratios and character invariants.
    """
    def classify(self, nodes: Sequence[SpatialNode], page_median_h: float) -> tuple[BlockType, int]:
        if not nodes:
            return BlockType.TEXT, 0
            
        # 1. Math Detection
        text_content = "".join(n.char for n in nodes)
        math_signals = r"[\^_{}=]|\\(frac|int|mu|nu|alpha|beta|Sigma|partial|mathbb)"
        if re.search(math_signals, text_content):
            return BlockType.MATH, 0
            
        # 2. Header Detection (H1 vs H2)
        block_median_h = statistics.median(n.font_size if n.font_size else n.height for n in nodes)
        if block_median_h > page_median_h * 1.5:
            return BlockType.HEADER, 1
        if block_median_h > page_median_h * 1.2:
            return BlockType.HEADER, 2
            
        # 3. Itemize Detection
        sorted_nodes = sorted(nodes, key=lambda n: n.x0)
        if sorted_nodes[0].char in ["•", "·", "*", "-"]:
            return BlockType.ITEMIZE, 0
            
        return BlockType.TEXT, 0
