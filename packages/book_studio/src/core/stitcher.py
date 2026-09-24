import re
from typing import List
from src.core.schemas import ExtractionResult, Block, Page

class CrossPageStitcher:
    """Deterministically stitches broken paragraphs and math environments across pages."""
    
    def __init__(self):
        # Matches words ending with a hyphen followed immediately by EOF/newline
        self.hyphen_regex = re.compile(r'(\w+)-\s*$')
        
    def stitch(self, raw_result: ExtractionResult) -> ExtractionResult:
        stitched_pages = []
        carry_over_block = None

        for page in raw_result.pages:
            new_blocks = []
            
            for block in page.blocks:
                if not block.content:
                    continue
                
                # If we have a block waiting to be stitched from the previous page
                if carry_over_block:
                    merged_content = self._merge_contents(carry_over_block.content, block.content)
                    # Update the carry_over block with merged content and add to current page
                    carry_over_block.content = merged_content
                    new_blocks.append(carry_over_block)
                    carry_over_block = None
                else:
                    new_blocks.append(block)
            
            # Check if the last block of the current page needs to be carried over to the next
            if new_blocks and self._requires_stitching(new_blocks[-1].content):
                carry_over_block = new_blocks.pop()
                
            stitched_pages.append(Page(page_number=page.page_number, blocks=new_blocks))

        # If the very last page ends in a carry_over block (edge case), append it
        if carry_over_block and stitched_pages:
            stitched_pages[-1].blocks.append(carry_over_block)

        return ExtractionResult(metadata=raw_result.metadata, pages=stitched_pages)

    def _requires_stitching(self, content: str) -> bool:
        """Determines if the text chunk is incomplete and requires the next block."""
        content = content.strip()
        if not content:
            return False
            
        # 1. Hyphenated word at the boundary
        if self.hyphen_regex.search(content):
            return True
            
        # 2. Mid-sentence break (ends with alphanumeric or comma, not punctuation)
        if content[-1].isalnum() or content[-1] == ',':
            return True
            
        # 3. Unclosed LaTeX math environments
        # Simple count check for unclosed \begin{...} without \end{...}
        begin_count = len(re.findall(r'\\begin\{[^}]+\}', content))
        end_count = len(re.findall(r'\\end\{[^}]+\}', content))
        if begin_count > end_count:
            return True
            
        # Simple count check for unclosed inline math ($)
        # Note: This is a heuristic. A robust LaTeX parser is needed for nested logic,
        # but for raw OCR extraction, counting isolated $ symbols suffices.
        dollar_count = content.count('$') - content.count(r'\$')
        if dollar_count % 2 != 0:
            return True

        return False

    def _merge_contents(self, tail: str, head: str) -> str:
        """Merges two strings based on their boundary conditions."""
        tail = tail.rstrip()
        head = head.lstrip()
        
        # Resolve hyphenation
        if self.hyphen_regex.search(tail):
            # Remove the hyphen and concatenate directly
            tail_clean = self.hyphen_regex.sub(r'\1', tail)
            return f"{tail_clean}{head}"
            
        # Default sentence or math continuation (add a space)
        return f"{tail} {head}"
