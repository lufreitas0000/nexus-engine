import os
import re
import subprocess
from pathlib import Path

import json
from nexus_schema import Document, Section, Paragraph, Metadata

from typing import Dict, List, Any
from document_converter.src.domain.model import ConvertedDocument
from research_graph.src.domain.model import PaperMetadata
from document_converter.src.infra.image_optimizer import ImageOptimizer

class LatexParser:
    def __init__(self):
        self.macros: Dict[str, Dict[str, Any]] = {}
        self.packages: List[str] = []

    def parse(self, content: str) -> str:
        # Remove comments but keep \%
        content = re.sub(r'(?<!\\)%.*$', '', content, flags=re.MULTILINE)

        # Extract packages
        packages = re.findall(r'\\usepackage(?:\[.*?\])?{([^}]+)}', content)
        for pkg_group in packages:
            for pkg in pkg_group.split(','):
                self.packages.append(pkg.strip())

        # Extract and apply newcommands
        def extract_newcommand(m):
            name = m.group(1) or m.group(2)
            args = int(m.group(3)) if m.group(3) else 0
            definition = m.group(4)
            self.macros[name] = {'args': args, 'def': definition}
            return ''

        # A somewhat naive regex, but better than before.
        # Match till the matching brace by assuming no nested braces in the definition (or up to 1 level).
        # Actually a common hack is to use a non-greedy match, but as we saw, it matches \end{...} or \begin{...} partially.
        # Let's match any character except `{` and `}`, or a matched pair of `{}`.
        regex_newcommand = r'\\newcommand(?:{\\([a-zA-Z]+)}|\\([a-zA-Z]+))(?:\[(\d+)\])?{((?:[^{}]|{[^{}]*})*)}'

        content = re.sub(regex_newcommand, extract_newcommand, content)

        # Apply macros (simplistic replacement)
        for name, macro in self.macros.items():
            if macro['args'] == 0:
                # Use regex with negative lookahead to avoid matching prefixes
                def zero_arg_replacer(m: Any, defn: str = str(macro['def'])) -> str:
                    return defn
                content = re.sub(rf'\\{name}(?![a-zA-Z])', zero_arg_replacer, content)
            else:
                pattern = f'\\\\{name}'
                for _ in range(macro['args']):
                    # Match grouped arguments more safely by using greedy matching up to a matching brace
                    # For a single argument, we match `{` followed by any number of characters, ending with `}`.
                    # Since nested macros like `\vect{v}` will produce inner braces, simple `[^}]+` matches `\vect{v` and stops at the `}` of `\vect`.
                    # To allow one level of nesting (e.g. `\norm{\vect{v}}`), we can match:
                    # `{(?:[^{}]|{[^{}]*})*}`
                    # The outer braces are explicitly matched, and the capturing group captures the inside.
                    pattern += r'{((?:[^{}]|{[^{}]*})*)}'

                def macro_replacer(m):
                    res = macro['def']
                    for i in range(1, macro['args'] + 1):
                        res = res.replace(f'#{i}', m.group(i))
                    return res

                content = re.sub(pattern, macro_replacer, content)

        return content


class PackageTranslator:
    def __init__(self, packages: List[str]):
        self.packages = packages

    def translate(self, content: str) -> str:
        if 'hyperref' in self.packages:
            # \href{url}{text} -> [text](url)
            content = re.sub(r'\\href{([^}]+)}{([^}]+)}', r'[\2](\1)', content)
            # \url{url} -> <url>
            content = re.sub(r'\\url{([^}]+)}', r'<\1>', content)
        return content


class MarkdownFormatter:
    def __init__(self, image_optimizer: ImageOptimizer, arxiv_id: str, source_dir: str, output_dir: str):
        self.image_optimizer = image_optimizer
        self.arxiv_id = arxiv_id
        self.source_dir = source_dir
        self.output_dir = output_dir

    def format(self, content: str) -> str:
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
                resolved_path = self.image_optimizer.resolve_image_path(self.source_dir, image_ref)

                if resolved_path:
                    figures_dir_name = f"{self.arxiv_id}_figures"
                    figures_output_dir = os.path.join(self.output_dir, figures_dir_name)
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


class LatexToMarkdownConverter:
    def __init__(self):
        self.image_optimizer = ImageOptimizer()

    def convert(self, paper: PaperMetadata, main_file_path: str, output_dir: str) -> ConvertedDocument:
        try:
            if not os.path.exists(main_file_path):
                raise FileNotFoundError(f"File not found: {main_file_path}")

            os.makedirs(output_dir, exist_ok=True)
            output_path = Path(output_dir) / f"{paper.arxiv_id}.json"

            frontmatter = self._generate_frontmatter(paper)

            if main_file_path.endswith(".pdf"):
                # Use convert as a black-box service for PDF processing
                try:
                    convert_dir = str(Path(__file__).resolve().parent.parent.parent / "convert" / "app_structurizer")
                    subprocess.run(
                        ["python", "-m", "src.cli", "extract", os.path.abspath(main_file_path), "--output-dir", os.path.abspath(output_dir), "--use-fake"],
                        cwd=convert_dir,
                        check=True,
                        capture_output=True,
                        text=True,
                        env=dict(os.environ, PYTHONPATH=convert_dir)
                    )

                    if output_path.exists():
                        # Spliter creates the file. We need to prepend the frontmatter.
                        with open(output_path, "r", encoding="utf-8", errors="ignore") as f:
                            content_str = f.read()
                        
                        from nexus_schema import markdown_to_document
                        # Convert markdown_content to AST
                        doc = markdown_to_document(content_str)
                        doc.metadata.title = paper.title
                        doc.metadata.author = ", ".join(paper.authors)
                        with open(output_path, "w", encoding="utf-8") as f:
                            json.dump(doc.model_dump(), f, ensure_ascii=False, indent=2)
                    else:
                        raise Exception("Spliter did not produce expected markdown file.")

                except subprocess.CalledProcessError as e:
                    raise Exception(f"Spliter fallback failed: {e.stderr}")

                return ConvertedDocument(arxiv_id=paper.arxiv_id, ast_path=str(output_path), success=True)

            with open(main_file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            source_dir = str(Path(main_file_path).parent)
            markdown_content = self._parse_latex(content, source_dir, output_dir, paper.arxiv_id)


            from nexus_schema import markdown_to_document
            # Convert markdown_content to AST
            doc = markdown_to_document(markdown_content)
            doc.metadata.title = paper.title
            doc.metadata.author = ", ".join(paper.authors)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(doc.model_dump(), f, ensure_ascii=False, indent=2)


            return ConvertedDocument(arxiv_id=paper.arxiv_id, ast_path=str(output_path), success=True)

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
        parser = LatexParser()
        parsed_content = parser.parse(content)

        translator = PackageTranslator(parser.packages)
        translated_content = translator.translate(parsed_content)

        formatter = MarkdownFormatter(
            image_optimizer=self.image_optimizer,
            arxiv_id=arxiv_id,
            source_dir=source_dir,
            output_dir=output_dir
        )
        final_content = formatter.format(translated_content)

        return final_content
