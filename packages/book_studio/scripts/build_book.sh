#!/bin/bash
# Must be run from the repository root
python3 scripts/inject_solutions.py --book baym_quantum_mechanics_1969
python3 scripts/inject_figures.py --book baym_quantum_mechanics_1969

cd books/baym_quantum_mechanics_1969/06_compiled/
python3 generate_main_tex.py
pdflatex -interaction=nonstopmode baym_qm_1969.tex >/dev/null
pdflatex -interaction=nonstopmode baym_qm_1969.tex >/dev/null
echo "Compilation finished!"
