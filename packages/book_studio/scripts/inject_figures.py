#!/usr/bin/env python3
"""
scripts/inject_figures.py

Finds generated .pdf figures in books/{book_id}/05_figures/enhanced/ and injects them
into the corresponding .tex files in 04_final_tex/ by searching for "Fig. X-Y" references.
"""

import re
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--book', required=True)
    args = parser.parse_args()

    enhanced_dir = Path(f"books/{args.book}/05_figures/enhanced")
    tex_dir = Path(f"books/{args.book}/04_final_tex")

    if not enhanced_dir.exists():
        print("No enhanced figures found.")
        return

    # Find all available figure pdfs: e.g. fig_4_15.pdf
    figs = list(enhanced_dir.glob("*.pdf"))
    if not figs:
        print("No PDF figures to inject.")
        return

    # Map e.g. "4-15" to the figure path
    fig_map = {}
    for f in figs:
        # Expecting name like fig_4_15.pdf
        m = re.search(r'fig_(\d+)_(\d+)', f.name)
        if m:
            fig_str = f"{m.group(1)}-{m.group(2)}"
            fig_map[fig_str] = f.name

    print(f"Found {len(fig_map)} figures to inject: {list(fig_map.keys())}")

    # Process all tex files
    for tex_file in sorted(tex_dir.glob("*.tex")):
        content = tex_file.read_text(encoding='utf-8')
        modified = False

        for fig_ref, pdf_name in fig_map.items():
            # Check if this tex file references the figure (e.g. "Fig. 4-15" or "Figure 4-15")
            # We want to inject it once, after the paragraph where it is first mentioned.
            # Avoid injecting multiple times
            if f"% INJECTED {fig_ref}" in content:
                continue

            # Look for the reference
            pattern = re.compile(r'(.*?(?:Fig\.|Figure)\s*' + re.escape(fig_ref) + r'.*?)\n\n', re.DOTALL)
            match = pattern.search(content)

            if match:
                print(f"Injecting Figure {fig_ref} into {tex_file.name}")
                injection = f"\n\n% INJECTED {fig_ref}\n"
                injection += "\\begin{figure}[htbp]\n"
                injection += "  \\centering\n"
                # Path relative to the main .tex file in 06_compiled
                injection += f"  \\includegraphics{{../05_figures/enhanced/{pdf_name}}}\n"
                injection += f"  \\caption{{Graphical representation (Fig. {fig_ref}).}}\n"
                injection += f"  \\label{{fig:{fig_ref}}}\n"
                injection += "\\end{figure}\n\n"

                # Insert the figure block right after the matching paragraph
                content = content[:match.end()] + injection + content[match.end():]
                modified = True

        if modified:
            tex_file.write_text(content, encoding='utf-8')

    print("Figure injection complete.")

if __name__ == "__main__":
    main()

