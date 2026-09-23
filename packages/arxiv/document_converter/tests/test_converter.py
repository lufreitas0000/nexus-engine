import pytest
import os
import tempfile

from document_converter.adapters.converter import LatexToMarkdownConverter
from research_graph.domain.model import PaperMetadata

def test_latex_conversion():
    converter = LatexToMarkdownConverter()
    arxiv_id = "1234"
    paper = PaperMetadata(
        arxiv_id=arxiv_id,
        title="Test Paper",
        abstract="Test Abstract",
        published_date="20240101",
        authors=["Alice", "Bob"]
    )

    latex_content = r"""
\section{Introduction}
This is a test.
\textbf{Bold text} and \textit{italic text}.

\begin{equation}
E = mc^2
\end{equation}

\begin{figure}
\includegraphics{test.png}
\caption{A test figure}
\end{figure}
"""

    from PIL import Image
    with tempfile.TemporaryDirectory() as tempdir:
        tex_path = os.path.join(tempdir, "main.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_content)

        # Create a dummy image file
        img_path = os.path.join(tempdir, "test.png")
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save(img_path)

        output_dir = os.path.join(tempdir, "output")

        result = converter.convert(paper, tex_path, output_dir)

        assert result.success is True
        assert result.markdown_path is not None
        assert os.path.exists(result.markdown_path)

        with open(result.markdown_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        assert "# Introduction" in md_content
        assert "**Bold text**" in md_content
        assert "*italic text*" in md_content
        assert "$$\nE = mc^2\n$$" in md_content

        # Check that the placeholder was replaced with the actual image path
        assert "![A test figure](1234_figures/test.jpg)" in md_content

        # Verify the image was actually created in the output directory
        output_image_path = os.path.join(output_dir, "1234_figures", "test.jpg")
        assert os.path.exists(output_image_path)
