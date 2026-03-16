import statistics
import re
from collections.abc import Sequence
from app_spatial_compiler.src.domain.models import SpatialNode, BlockType

class BlockClassifier:
    """
    Classifies 2D manifolds into semantic types using typographic 
    ratios and character invariants.
    """
    
    def classify(self, nodes: Sequence[SpatialNode], page_median_h: float) -> BlockType:
        if not nodes:
            return BlockType.TEXT
            
        # 1. Math Detection: Check for operators or LaTeX signals
        # We look for explicit symbols or LaTeX reduction markers
        text_content = "".join(n.char for n in nodes)
        math_signals = r"[\^_{}=]|\\(frac|int|mu|nu|alpha|beta|Sigma|partial)"
        if re.search(math_signals, text_content):
            return BlockType.MATH
            
        # 2. Header Detection: Height relative to page median
        # If the median height of this block is significantly larger than the page
        block_median_h = statistics.median(n.font_size if n.font_size else n.height for n in nodes)
        if block_median_h > page_median_h * 1.25:
            return BlockType.HEADER
            
        # 3. Itemize Detection: Leading bullets or high indentation
        # Typically academic lists start with specific Unicode characters
        sorted_nodes = sorted(nodes, key=lambda n: n.x0)
        if sorted_nodes[0].char in ["•", "·", "*", "-"]:
            return BlockType.ITEMIZE
            
        return BlockType.TEXT
