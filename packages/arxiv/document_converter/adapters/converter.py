import os
import re
import subprocess
from pathlib import Path

from document_converter.domain.model import ConvertedDocument
from research_graph.domain.model import PaperMetadata
from document_converter.adapters.image_optimizer import ImageOptimizer

class LatexToMarkdownConverter:
    def __init__(self):
        self.image_optimizer = ImageOptimizer()

    def convert(self, paper: PaperMetadata, main_file_path: str, output_dir: str) -> ConvertedDocument:
        try:
            if not os.path.exists(main_file_path):
                raise FileNotFoundError(f"File not found: {main_file_path}")

            os.makedirs(output_dir, exist_ok=True)
            output_path = Path(output_dir) / f"{paper.arxiv_id}.md"

            frontmatter = self._generate_frontmatter(paper)

            if main_file_path.endswith(".pdf"):
                # Use spliter as a black-box service for PDF processing
                try:
                    spliter_dir = str(Path(__file__).resolve().parent.parent.parent.parent / "spliter" / "app_structurizer")
                    subprocess.run(
                        ["python", "-m", "src.cli", "extract", os.path.abspath(main_file_path), "--output-dir", os.path.abspath(output_dir), "--use-fake"],
                        cwd=spliter_dir,
                        check=True,
                        capture_output=True,
                        text=True,
                        env=dict(os.environ, PYTHONPATH=spliter_dir)
                    )

                    if output_path.exists():
                        # Spliter creates the file. We need to prepend the frontmatter.
                        with open(output_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(frontmatter + content)
                    else:
                        raise Exception("Spliter did not produce expected markdown file.")

                except subprocess.CalledProcessError as e:
                    raise Exception(f"Spliter fallback failed: {e.stderr}")

                return ConvertedDocument(arxiv_id=paper.arxiv_id, markdown_path=str(output_path), success=True)

            with open(main_file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            source_dir = str(Path(main_file_path).parent)
            markdown_content = self._parse_latex(content, source_dir, output_dir, paper.arxiv_id)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(frontmatter + markdown_content)

            return ConvertedDocument(arxiv_id=paper.arxiv_id, markdown_path=str(output_path), success=True)

        except Exception as e:
            return ConvertedDocument(arxiv_id=paper.arxiv_id if hasattr(paper, 'arxiv_id') else str(paper), success=False, error=str(e))

    def _generate_frontmatter(self, paper: PaperMetadata) -> str:
        authors_list = "\n".join([f"  - {author}" for author in paper.authors])

        return f"""---
title: "{paper.title.replace('"', '\\"')}"
arxiv_id: "{paper.arxiv_id}"
published_date: "{paper.published_date}"
authors:
{authors_list}
---

"""

    def _parse_latex(self, content: str, source_dir: str, output_dir: str, arxiv_id: str) -> str:
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

        # Figures (Simplistic extraction of caption and image path)
        def replace_figure(match):
            fig_content = match.group(1)
            caption_match = re.search(r'\\caption{([^}]+)}', fig_content)
            caption = caption_match.group(1) if caption_match else "Figure"

            image_path_match = re.search(r'\\includegraphics(?:\[.*?\])?{([^}]+)}', fig_content)
            image_md_path = "extracted_figure_placeholder"

            if image_path_match:
                image_ref = image_path_match.group(1)
                resolved_path = self.image_optimizer.resolve_image_path(source_dir, image_ref)

                if resolved_path:
                    figures_dir_name = f"{arxiv_id}_figures"
                    figures_output_dir = os.path.join(output_dir, figures_dir_name)
                    output_filename = f"{Path(image_ref).stem}.jpg"

                    optimized_filename = self.image_optimizer.optimize(
                        str(resolved_path),
                        figures_output_dir,
                        output_filename
                    )

                    if optimized_filename:
                        # Path relative to output_dir
                        image_md_path = f"{figures_dir_name}/{optimized_filename}"

            return f"\n\n![{caption}]({image_md_path})\n\n"

        content = re.sub(r'\\begin{figure\*?}\[.*?\](.*?)\\end{figure\*?}', replace_figure, content, flags=re.DOTALL)
        content = re.sub(r'\\begin{figure\*?}(.*?)\\end{figure\*?}', replace_figure, content, flags=re.DOTALL)

        return content
