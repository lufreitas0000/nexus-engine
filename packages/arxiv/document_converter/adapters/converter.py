import os
import re
from pathlib import Path

from document_converter.domain.model import ConvertedDocument

class LatexToMarkdownConverter:
    def convert(self, arxiv_id: str, main_file_path: str, output_dir: str) -> ConvertedDocument:
        try:
            if not os.path.exists(main_file_path):
                raise FileNotFoundError(f"File not found: {main_file_path}")

            os.makedirs(output_dir, exist_ok=True)
            output_path = Path(output_dir) / f"{arxiv_id}.md"

            if main_file_path.endswith(".pdf"):
                # Basic handling if we only got a PDF: just note it
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(f"# Document {arxiv_id}\n\n[Only PDF source was available. Conversion not supported natively.]")
                return ConvertedDocument(arxiv_id=arxiv_id, markdown_path=str(output_path), success=True)

            with open(main_file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            markdown_content = self._parse_latex(content)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            return ConvertedDocument(arxiv_id=arxiv_id, markdown_path=str(output_path), success=True)

        except Exception as e:
            return ConvertedDocument(arxiv_id=arxiv_id, success=False, error=str(e))

    def _parse_latex(self, content: str) -> str:
        """A very simplistic LaTeX to Markdown regex parser."""

        # Remove comments but keep \%
        content = re.sub(r'(?<!\\)%.*$', '', content, flags=re.MULTILINE)

        # Sections
        content = re.sub(r'\\section\*?{([^}]+)}', r'# \1', content)
        content = re.sub(r'\\subsection\*?{([^}]+)}', r'## \1', content)
        content = re.sub(r'\\subsubsection\*?{([^}]+)}', r'### \1', content)

        # Math blocks
        content = re.sub(r'\\begin{equation\*?}(.*?)\\end{equation\*?}', r'$$\1$$', content, flags=re.DOTALL)
        content = re.sub(r'\\begin{align\*?}(.*?)\\end{align\*?}', r'$$\1$$', content, flags=re.DOTALL)

        # Bold and italic
        content = re.sub(r'\\textbf{([^}]+)}', r'**\1**', content)
        content = re.sub(r'\\textit{([^}]+)}', r'*\1*', content)
        content = re.sub(r'\\emph{([^}]+)}', r'*\1*', content)

        # Figures (Simplistic extraction of caption)
        def replace_figure(match):
            fig_content = match.group(1)
            caption_match = re.search(r'\\caption{([^}]+)}', fig_content)
            caption = caption_match.group(1) if caption_match else "Figure"
            return f"\n\n![{caption}](extracted_figure_placeholder)\n\n"

        content = re.sub(r'\\begin{figure\*?}\[.*?\](.*?)\\end{figure\*?}', replace_figure, content, flags=re.DOTALL)
        content = re.sub(r'\\begin{figure\*?}(.*?)\\end{figure\*?}', replace_figure, content, flags=re.DOTALL)

        return content
