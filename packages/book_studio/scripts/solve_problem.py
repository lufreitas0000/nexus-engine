#!/usr/bin/env python3
"""
scripts/solve_problem.py

Multi-agent physics problem solver.

Usage:
    # Single problem by number
    python3 scripts/solve_problem.py --book baym_quantum_mechanics_1969 --chapter 1 --problem 4

    # All problems in a chapter (runs triage first, skips difficulty 5)
    python3 scripts/solve_problem.py --book baym_quantum_mechanics_1969 --chapter 1 --all

    # From a specific problems markdown file
    python3 scripts/solve_problem.py \
        --problems-file books/baym_quantum_mechanics_1969/03_verified_md/01_06_PROBLEMS.md \
        --problem 4

Produces:
    books/{book_id}/solutions/ch{NN}/ch{NN}_p{MM}.md
"""

import re
import sys
import json
import click
import datetime
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ── Problem Parsing ────────────────────────────────────────────────────────────

def extract_problems(md_text: str) -> dict[int, str]:
    """
    Parse a PROBLEMS.md file and return a dict of {problem_number: problem_text}.
    Handles numbered lists like '1. ...', '2. ...'.
    """
    # Split on top-level numbered items
    pattern = r'(?=^(\d+)\.\s)'
    parts = re.split(pattern, md_text, flags=re.MULTILINE)

    problems = {}
    i = 0
    while i < len(parts):
        if parts[i].isdigit():
            num = int(parts[i])
            text = parts[i + 1] if i + 1 < len(parts) else ''
            problems[num] = text.strip()
            i += 2
        else:
            i += 1
    return problems


def load_chapter_notes(book_root: Path, chapter: int) -> str:
    """Load all verified markdown files for a given chapter into one string."""
    md_dir = book_root / '03_verified_md'
    prefix = f'{chapter:02d}_'
    files = sorted(md_dir.glob(f'{prefix}*.md'))
    chunks = []
    for f in files:
        if 'PROBLEMS' not in f.name:
            chunks.append(f'### {f.stem}\n\n{f.read_text()}')
    return '\n\n---\n\n'.join(chunks)


# ── Solution File Writer ────────────────────────────────────────────────────────

def write_solution_template(
    output_path: Path,
    book_id: str,
    chapter: int,
    problem_num: int,
    problem_text: str,
    difficulty: str = 'medium',
) -> None:
    """Write a solution template file. Agents fill in the sections."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()

    content = f"""---
problem_id: {book_id}_ch{chapter:02d}_p{problem_num:02d}
source_book: {book_id}
chapter: {chapter}
problem_number: {problem_num}
difficulty: {difficulty}
status: pending
solver_confidence: ~
adversarial_verdict: ~
last_updated: {today}
---

# Problem {chapter}.{problem_num}

**Source**: Chapter {chapter}, Problem {problem_num}

## Problem Statement

{problem_text}

---

## Restatement

<!-- Context Agent + Solver Agent: Rewrite the problem in self-contained form. -->
<!-- No references to "above" or "part (a)". Include all definitions. -->

> *[To be filled by Solver Agent]*

---

## Prerequisites

<!-- Context Agent: Extract from chapter markdown notes -->
<!-- Format: concept name, one-sentence explanation, key equation -->

> *[To be filled by Context Agent]*

---

## Hints

<!-- Solver Agent: 3-5 graduated hints, from general to specific -->
<!-- Each hint should be a nudge, not a spoiler -->

> **Hint 1** — *[To be filled]*

> **Hint 2** — *[To be filled]*

> **Hint 3** — *[To be filled]*

---

## Solution

<!-- Solver Agent: Full derivation with named steps -->
<!-- Mark each step: <!-- CONFIDENT -->, <!-- UNCERTAIN -->, or <!-- SKIPPED --> -->

### Setup

*[To be filled]*

### Step 1

$$
% derivation here
$$

### Result

$$
\\boxed{{...}}
$$

---

## Discussion

<!-- Physical interpretation. Limiting cases. Connection to bigger picture. -->

*[To be filled by Solver Agent]*

---

## Adversarial Review

<!-- Adversarial Logic Agent findings -->

| Step | Error Type | Description | Severity |
|------|-----------|-------------|----------|
| *[To be filled]* | | | |

**Verdict**: *[PASS / PASS_WITH_WARNINGS / FAIL]*

---

## Related Resources

<!-- Web Searcher Agent: approach comparison, reference URLs -->

- **Typical method used**: *[To be filled]*
- **Alternative approaches**: *[To be filled]*
- **References**: *[To be filled]*

---

## Notes

*[Any unsolved parts, open questions, or partial solutions go here]*
"""
    output_path.write_text(content, encoding='utf-8')


# ── CLI ────────────────────────────────────────────────────────────────────────

@click.command()
@click.option('--book', default=None, help='Book ID (e.g. baym_quantum_mechanics_1969)')
@click.option('--chapter', default=None, type=int, help='Chapter number')
@click.option('--problem', default=None, type=int, help='Problem number')
@click.option('--problems-file', default=None, type=click.Path(), help='Path to PROBLEMS.md')
@click.option('--all', 'solve_all', is_flag=True, help='Generate templates for all problems in chapter')
@click.option('--difficulty', default='medium',
              type=click.Choice(['easy', 'medium', 'hard', 'research']),
              help='Difficulty override')
def main(book, chapter, problem, problems_file, solve_all, difficulty):
    """Generate solution template(s) for physics problems."""

    # Locate book root
    if book:
        book_root = Path(f'books/{book}')
    elif problems_file:
        book_root = Path(problems_file).parents[2]  # books/{id}/03_verified_md/
        book = book_root.name
    else:
        click.echo("Error: provide --book or --problems-file", err=True)
        sys.exit(1)

    if not book_root.exists():
        click.echo(f"Error: Book directory not found: {book_root}", err=True)
        sys.exit(1)

    # Locate the problems file
    if problems_file:
        prob_file = Path(problems_file)
    elif chapter:
        md_dir = book_root / '03_verified_md'
        candidates = sorted(md_dir.glob(f'{chapter:02d}_*PROBLEMS*.md'))
        if not candidates:
            click.echo(f"No PROBLEMS.md found for chapter {chapter} in {md_dir}", err=True)
            sys.exit(1)
        prob_file = candidates[0]
    else:
        click.echo("Error: provide --chapter or --problems-file", err=True)
        sys.exit(1)

    click.echo(f"📖 Book: {book}")
    click.echo(f"📄 Problems file: {prob_file}")

    md_text = prob_file.read_text(encoding='utf-8')
    problems = extract_problems(md_text)
    click.echo(f"   Found {len(problems)} problems")

    # Determine chapter number from filename
    if chapter is None:
        stem = prob_file.stem
        chapter_match = re.match(r'^(\d+)', stem)
        chapter = int(chapter_match.group(1)) if chapter_match else 0

    solutions_dir = book_root / 'solutions' / f'ch{chapter:02d}'

    # Generate template(s)
    if solve_all:
        targets = list(problems.keys())
    elif problem:
        targets = [problem]
    else:
        click.echo("Error: provide --problem N or --all", err=True)
        sys.exit(1)

    for pnum in targets:
        if pnum not in problems:
            click.echo(f"  [!] Problem {pnum} not found in {prob_file.name}")
            continue

        out_path = solutions_dir / f'ch{chapter:02d}_p{pnum:02d}.md'

        if out_path.exists():
            click.echo(f"  [skip] {out_path.name} already exists — use --overwrite to regenerate")
            continue

        write_solution_template(out_path, book, chapter, pnum, problems[pnum], difficulty)
        click.echo(f"  [✓] Created: {out_path}")

    click.echo(f"\nNext step:")
    click.echo(f"  Invoke the problem_solver skill agents to fill in the solutions:")
    click.echo(f"  See: skills/06_problem_solver/SKILL.md")
    click.echo(f"  Solutions directory: {solutions_dir}/")


if __name__ == '__main__':
    main()

