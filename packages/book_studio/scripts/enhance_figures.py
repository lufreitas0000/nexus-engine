#!/usr/bin/env python3
"""
scripts/enhance_figures.py

Orchestrates the Figure Enhancement pipeline (Stage 4.5).
Currently a stub that lists figures to be manually dispatched to agents,
but can be extended to call the Gemini API automatically in the future.
"""

import os
import glob
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="List and orchestrate figure enhancement.")
    parser.add_argument('--book', required=True, help="Book ID (e.g. baym_quantum_mechanics_1969)")
    args = parser.parse_args()

    book_dir = Path(f"books/{args.book}")
    raw_dir = book_dir / "05_figures" / "raw"
    enhanced_dir = book_dir / "05_figures" / "enhanced"
    scripts_dir = Path("scripts/figures") / args.book

    enhanced_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(raw_dir.glob("*.png"))

    print(f"Found {len(images)} raw figures in {raw_dir}")
    print(f"Enhanced dir: {enhanced_dir}")
    print(f"Scripts dir: {scripts_dir}\n")

    print("Next steps:")
    print("1. Use `view_file` to inspect the PNGs.")
    print("2. If it's a text artifact (OCR mistake), delete it.")
    print("3. If it's a diagram/plot, invoke `figure_tikz_specialist` or `figure_python_specialist`")
    print("   passing the absolute path to the image.")

if __name__ == "__main__":
    main()

