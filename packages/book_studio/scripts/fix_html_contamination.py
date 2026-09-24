#!/usr/bin/env python3
"""
scripts/fix_html_contamination.py
Strips raw HTML tags from .tex files and replaces HTML entities with proper LaTeX.
Handles frontmatter cleanup and broken TOC files.
"""
import re
import sys
from pathlib import Path

HTML_ENTITY_MAP = {
    '&amp;': r'\&',
    '&lt;': '<',
    '&gt;': '>',
    '&nbsp;': '~',
    '&mdash;': '---',
    '&ndash;': '--',
    '&ldquo;': "``",
    '&rdquo;': "''",
    '&lsquo;': "`",
    '&rsquo;': "'",
}

def parse_html_table_to_latex(html: str) -> str:
    """Convert an HTML table (TOC) to a LaTeX longtable."""
    rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
    latex_rows = []
    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
        cells = [strip_html_tags(c).strip() for c in cells]
        if len(cells) == 2:
            # TOC entry: section title + page number
            title, page = cells
            if page and re.match(r'[\d\w®^!*]+', page):
                latex_rows.append(f"\\contentsline{{section}}{{{title}}}{{{page}}}{{}}%")
        elif len(cells) == 1:
            latex_rows.append(f"\\contentsline{{chapter}}{{{cells[0]}}}{{}}{{}}")
    return '\n'.join(latex_rows)


def strip_html_tags(text: str) -> str:
    """Remove all HTML tags from text."""
    # Remove href links, keep text
    text = re.sub(r'<a [^>]+>(.*?)</a>', r'\1', text, flags=re.DOTALL)
    # Remove block elements, replacing with newlines
    text = re.sub(r'<(p|div|h[1-6]|tr|thead|tbody|table)[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</(p|div|h[1-6]|tr|thead|tbody|table)>', '\n', text, flags=re.IGNORECASE)
    # Remove inline formatting
    text = re.sub(r'<(b|i|em|strong|span|th|td)[^>]*>(.*?)</\1>', r'\2', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove all remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    # Replace HTML entities
    for entity, latex in HTML_ENTITY_MAP.items():
        text = text.replace(entity, latex)
    # Fix bare & that would break latex (not already escaped)
    text = re.sub(r'(?<!\\)&', r'\\&', text)
    # Collapse excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def fix_tex_file(path: Path) -> bool:
    """Fix HTML contamination in a single .tex file. Returns True if modified."""
    original = path.read_text(encoding='utf-8', errors='replace')

    if '<' not in original and '&amp;' not in original:
        return False  # No HTML, skip

    # Handle TOC table files — convert to LaTeX comment block
    if '<table>' in original or '<thead>' in original:
        section_match = re.match(r'(\\section\*?\{[^}]+\})', original)
        section_line = section_match.group(1) if section_match else ''

        # Extract all tables
        tables = re.findall(r'<table>.*?</table>', original, re.DOTALL)
        latex_toc = []
        for table in tables:
            latex_toc.append(parse_html_table_to_latex(table))

        result = (
            f"{section_line}\n\n"
            "% \\tableofcontents  % (Rendered by LaTeX automatically from main document)\n"
            "% Original OCR table-of-contents entries for reference:\n"
        )
        for entry in '\n'.join(latex_toc).split('\n'):
            if entry.strip():
                result += f"% {entry}\n"

        path.write_text(result, encoding='utf-8')
        return True

    # Handle other HTML-contaminated files
    cleaned = strip_html_tags(original)

    if cleaned != original:
        path.write_text(cleaned, encoding='utf-8')
        return True

    return False


def fix_publisher_page(path: Path) -> bool:
    """Specifically handle the Taylor & Francis publisher page."""
    text = path.read_text(encoding='utf-8', errors='replace')
    if 'Taylor' not in text and '<h2>' not in text:
        return False

    new_content = (
        "\\section*{Publisher Information}\n\n"
        "\\begin{center}\n"
        "{\\large\\textbf{Taylor \\& Francis}}\\\\\n"
        "Taylor \\& Francis Group\\\\\n"
        "\\url{http://taylorandfrancis.com}\n"
        "\\end{center}\n"
    )
    path.write_text(new_content, encoding='utf-8')
    return True


def main(tex_dir: Path):
    files = sorted(tex_dir.glob('*.tex'))
    modified = 0
    for f in files:
        # Special handling for the publisher page
        if 'CONTENTS_xi' in f.name or ('Taylor' in f.read_text(encoding='utf-8', errors='replace')[:200]):
            if fix_publisher_page(f):
                print(f"  [PUBLISHER] Fixed: {f.name}")
                modified += 1
                continue

        if fix_tex_file(f):
            print(f"  [HTML->LaTeX] Fixed: {f.name}")
            modified += 1

    print(f"\nDone. Modified {modified}/{len(files)} files.")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = Path('books/baym_quantum_mechanics_1969/04_final_tex')
    main(target)

