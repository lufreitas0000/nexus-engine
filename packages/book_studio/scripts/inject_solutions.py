#!/usr/bin/env python3
"""
scripts/inject_solutions.py

Collects all solved problems from books/{book_id}/solutions/chNN/,
converts the markdown to LaTeX, and writes them to
books/{book_id}/04_final_tex/NN_99_SOLUTIONS.tex so they appear
at the end of each chapter.
"""

import re
import os
from pathlib import Path
import argparse
import yaml

def clean_latex(md_text):
    """Very basic MD to LaTeX converter for solutions."""
    # Remove YAML front matter
    text = re.sub(r'^---[\s\S]*?^---\n', '', md_text, flags=re.MULTILINE)
    # Convert headings
    text = re.sub(r'^## (.*)', r'\\subsection*{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*)', r'\\section*{\1}', text, flags=re.MULTILINE)
    # Convert bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    # Convert blockquotes
    text = re.sub(r'^> (.*)', r'\\begin{quote}\1\\end{quote}', text, flags=re.MULTILINE)
    return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--book', required=True)
    args = parser.parse_args()

    solutions_dir = Path(f"books/{args.book}/solutions")
    tex_dir = Path(f"books/{args.book}/04_final_tex")

    if not solutions_dir.exists():
        print("No solutions found.")
        return

    # Process chapter by chapter
    for ch_dir in sorted(solutions_dir.glob("ch*")):
        ch_num = ch_dir.name.replace('ch', '')

        solved_contents = []
        for prob_file in sorted(ch_dir.glob("*.md")):
            content = prob_file.read_text(encoding='utf-8')
            if 'status: solved' in content:
                latex_content = clean_latex(content)
                solved_contents.append(latex_content)

        if solved_contents:
            output_tex = tex_dir / f"{ch_num}_99_SOLUTIONS.tex"
            with open(output_tex, 'w', encoding='utf-8') as f:
                f.write(f"\\section*{{Appendix: Chapter {int(ch_num)} Solutions}}\n")
                f.write("\\addcontentsline{toc}{section}{Solutions}\n\n")
                f.write("\n\\vspace{1cm}\n\\hrule\n\\vspace{1cm}\n".join(solved_contents))
            print(f"Generated {output_tex} with {len(solved_contents)} solutions.")

if __name__ == "__main__":
    main()

