---
name: problem_solver
description: >
  Multi-agent pipeline that produces structured, hint-driven solution documents
  for physics/math problems from ingested textbooks. Outputs a markdown file
  with: prerequisites, ordered hints, algebraic derivation, and adversarial
  verification. Designed for Baym QM and Fazekas condensed matter problems.
---

# Skill: Physics Problem Solver

## Overview

This skill coordinates 4 specialized agents to produce a pedagogically structured
solution for any problem from our ingested textbooks.

```
Problem text (from PROBLEMS.md)
           │
    ┌──────▼───────┐
    │ Context Agent │  reads related MD notes, extracts prerequisites
    └──────┬───────┘
           │ prerequisites JSON
    ┌──────▼───────┐
    │ Solver Agent  │  writes restatement → hints → derivation
    └──────┬───────┘
           │ draft solution
    ┌──────▼──────────┐      ┌────────────────────┐
    │ Adversarial     │◄────►│ Web Searcher Agent  │
    │ Logic Agent     │      │ (approach only)     │
    └──────┬──────────┘      └────────────────────┘
           │ verified solution
    ┌──────▼────────┐
    │  Output MD    │  saved to books/{book_id}/solutions/{ch}/
    └───────────────┘
```

---

## Agent 1: Context Agent (flash)

**Role**: Mine the book's verified Markdown notes for prerequisites.

### Prompt Template
```
You are a physics knowledge extractor. Given a problem statement and the
relevant chapter markdown notes, extract:

1. prerequisites: List of concepts/equations needed to understand the problem.
   For each, provide:
   - concept name
   - one-sentence explanation
   - the key equation (LaTeX) if applicable
   - which section/file it comes from

2. notation_used: Dict of symbols appearing in the problem and their meanings.

3. related_sections: List of section names most relevant to this problem.

Output as JSON.

Book notes directory: books/{book_id}/03_verified_md/
Focus on chapter: {chapter_files}
Problem: {problem_text}
```

---

## Agent 2: Solver Agent (pro)

**Role**: Write the complete structured solution.

### Output Format

The Solver Agent writes the solution in this exact structure:

```markdown
## Problem Restatement
[Self-contained rewrite of the problem. No pronouns like "Problem 3 above".
 Include all needed definitions.]

## Prerequisites
[From Context Agent output — formatted as a readable list with equations]

## Hints
> **Hint 1** — [Direction: "Consider the completeness relation..."]
> **Hint 2** — [Narrower: "Express the transformation matrix as..."]
> **Hint 3** — [Specific: "Apply unitarity condition UU† = I..."]

## Solution

### Setup
[Physical/mathematical setup, define symbols]

### Step 1: [Title]
[Prose + equation block]
$$
...derivation...
$$

### Step N: [Title]
...

### Result
$$
\boxed{final answer}
$$

## Discussion
[Physical interpretation of the result. What does it mean?
 Limiting cases. Connection to bigger picture.]
```

### Directives for Solver Agent
- **Never skip steps** — every algebraic move must be justified in one sentence
- **Use canonical notation** — consult `config/notation.json`
- **Mark confidence**: add `<!-- CONFIDENT -->`, `<!-- UNCERTAIN -->`, or `<!-- SKIPPED -->`
  after each step
- For problems that are **too hard to solve completely**: solve what you can,
  write partial steps, mark `status: partial` in the YAML front matter,
  and write a `## Why This Is Hard` section explaining what methods are missing
  (e.g., "requires advanced contour integration", "needs numerical solution")

---

## Agent 3: Adversarial Logic Agent (pro)

**Role**: Challenge every step of the solver's derivation.

### Prompt Template
```
You are an adversarial physics reviewer. You are given a draft solution.
Your task is to find errors. Check:

1. SIGN ERRORS: Is every sign correct? Check esp. in commutators,
   Hermitian conjugates, cross products.
2. DROPPED CONSTANTS: Are ℏ, factors of 2, π consistently tracked?
3. NORMALIZATION: Are states and operators properly normalized?
4. BOUNDARY CONDITIONS: Are appropriate limits/BCs applied?
5. APPROXIMATIONS: Are any approximations made without justification?
6. DIMENSIONAL ANALYSIS: Does every equation have consistent dimensions?
7. LOGIC GAPS: Is every step justified?

For each issue found, output:
{
  "step": "Step N title",
  "error_type": "sign_error | dropped_constant | ...",
  "description": "...",
  "correction": "...",
  "severity": "critical | minor | suggestion"
}

If no errors, output: {"errors": [], "verdict": "PASS"}
```

---

## Agent 4: Web Searcher Agent (flash + web search)

**Role**: Find similar problems online and compare approach (NOT the answer).

### Prompt Template
```
Search for this physics problem or a similar one:
{problem_summary}

Focus on:
1. What approach/method is typically used?
2. Are there multiple valid methods? Which is preferred for a graduate course?
3. Common pitfalls mentioned in online discussions?

Do NOT copy any solution text. Report only:
- Method names used (e.g., "Gram-Schmidt orthogonalization", "insertion of completeness")
- Whether the typical approach matches what our Solver Agent used
- Any important alternative methods worth mentioning

Source URLs for reference.
```

---

## Output File Format

```markdown
---
problem_id: {book_id}_ch{NN}_p{MM}
source_book: {book_id}
chapter: {N}
problem_number: {M}
difficulty: easy | medium | hard | research
status: solved | partial | unsolved
solver_confidence: high | medium | low
adversarial_verdict: PASS | PASS_WITH_WARNINGS | FAIL
last_updated: YYYY-MM-DD
---

# Problem {ch}.{n}: {Short Title}

**Source**: {Book Title}, Chapter {N}, Problem {M}

## Problem Statement
{Original verbatim statement}

## Restatement
{Self-contained rewrite}

## Prerequisites
...

## Hints
...

## Solution
...

## Adversarial Review
{Summary of Adversarial Agent findings}

## Related Resources
{Web Searcher findings — approach comparison, reference URLs}

## Notes
{Any unsolved parts, open questions, alternative approaches}
```

---

## Invocation

### From command line:
```bash
python3 scripts/solve_problem.py \
  --book baym_quantum_mechanics_1969 \
  --chapter 1 \
  --problem 4
```

### Agent orchestration:
```bash
python3 scripts/solve_problem.py \
  --book baym_quantum_mechanics_1969 \
  --problems-file books/baym_quantum_mechanics_1969/03_verified_md/01_06_PROBLEMS.md \
  --all
```

### Output location:
```
books/{book_id}/solutions/ch{NN}/
├── ch{NN}_p{MM}.md
└── ch{NN}_all.md    # combined chapter problems
```

---

## Quota & Efficiency Notes

- Context Agent (flash): ~500 tokens per problem — very cheap
- Solver Agent (pro): ~3000–8000 tokens per problem — bulk of cost
- Adversarial Agent (pro): ~2000–4000 tokens — run after solver
- Web Searcher (flash): ~500 tokens — optional, skip for simple problems

**Batch strategy**: Run Context Agent for all problems in a chapter first (flash),
then run Solver + Adversarial per problem (pro). Cap at 5 problems per session
to stay under quota.

**Difficulty triage**: Before running Solver (pro), have a flash agent score
difficulty 1-5. Skip to `status: unsolved` for difficulty 5 unless requested.

