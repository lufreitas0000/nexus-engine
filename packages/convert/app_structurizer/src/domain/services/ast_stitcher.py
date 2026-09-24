import re
from app_structurizer.src.domain.models import MarkdownAST


class AstStitcher:
    """
    Domain service to mathematically strip raster artifacts from the AST,
    preserving captions and structural nodes, and injecting semantic ALT texts
    from the Vision Encoder.
    """

    # Regex to capture Markdown image syntax: ![caption](url/path/base64)
    # Group 1 captures the caption.
    # Group 2 captures the URL/path, which we might need to match with xref semantics.
    IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    def stitch_ast(
        self, ast: MarkdownAST, image_semantics: dict[str, str]
    ) -> MarkdownAST:
        """
        Executes the mapping function over the AST string buffer, replacing
        image tags with their extracted ALT texts.
        """

        def replacement(match):
            caption = match.group(1)
            url = match.group(2)

            # Identify the xref if present in the url (e.g. if the structurizer saved it as xref_123.png)
            # Or if image_semantics dictionary maps exactly based on some matching logic.
            # Usually, the AST extracted by marker or spatial might not have the exact xref.
            # But based on the Phase 4/5 spec: "takes a raw Markdown string with image placeholders
            # and a dictionary of extracted ALT texts... mathematically replaces the placeholders"

            # Let's extract an identifier. If it matches a key in image_semantics, use it.
            # For this implementation, we will check if any key in image_semantics is in the URL.
            semantic_text = None
            for key, val in image_semantics.items():
                if key in url:
                    semantic_text = val
                    break

            if semantic_text:
                return (
                    f"[ALT Text] {caption} - {semantic_text}"
                    if caption
                    else f"[ALT Text] {semantic_text}"
                )
            else:
                return f"[ALT Text] {caption}" if caption else "[ALT Text]"

        filtered_content = self.IMAGE_PATTERN.sub(replacement, ast.content)

        return MarkdownAST(content=filtered_content, metadata=ast.metadata)
