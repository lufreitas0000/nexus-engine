---
name: notation_upgrade
description: >
  Standardizes mathematical notation across all Markdown and LaTeX files to
  a modern, unambiguous, physics notation. Uses config/notation.json as the
  canonical reference. Operates on a book's verified_md or final_tex directory.
---

# Skill: Notation Upgrade Agent

## Purpose

Physics textbooks written before the 1990s often use outdated notation:
- Bare `H` for the Hamiltonian (ambiguous with classical H)
- Wave functions written as `psi(x)` instead of `⟨x|ψ⟩`
- Matrices written in components without tensor notation
- Mixed use of `i` and `j` for imaginary unit
- Inconsistent placement of operator hats

This skill standardizes notation **consistently within each book** while staying close to the original where modern physicists would still recognize it.

---

## Canonical Notation Reference

Consult `config/notation.json` for the full table. Key rules:

### Operators
| Legacy | Modern | Notes |
|--------|--------|-------|
| `H` (Hamiltonian) | `\hat{H}` | Always hat for operators |
| `p` (momentum op.) | `\hat{p}` | Distinguish from classical |
| `L`, `S`, `J` | `\hat{L}`, `\hat{S}`, `\hat{J}` | Angular momentum |
| `a`, `a†` | `\hat{a}`, `\hat{a}^\dagger` | Ladder operators |
| `N` (number op.) | `\hat{N}` | |

### States and Amplitudes
| Legacy | Modern | Notes |
|--------|--------|-------|
| `<φ\|ψ>` | `\braket{\phi}{\psi}` | Use macro |
| `\|n\>` | `\ket{n}` | Use macro |
| `<n\|` | `\bra{n}` | Use macro |
| `<A>` | `\ev{\hat{A}}{\psi}` | Expectation value |

### Differentials and Constants
| Legacy | Modern | Notes |
|--------|--------|-------|
| `dx` | `\dd x` | Upright d for measure |
| `d^3r` | `\dd^3 r` | |
| `e^{iθ}` | `\ee^{\ii\theta}` | Upright e, i only if consistent |
| `ℏ` | `\hbar` | Already standard |

### Common Physics Notation
| Quantity | Notation | Notes |
|---------|---------|-------|
| Commutator | `\comm{\hat{A}}{\hat{B}}` | |
| Anti-commutator | `\acomm{\hat{A}}{\hat{B}}` | |
| Hermitian conjugate | `\hat{A}^\dagger` | Not `\hat{A}^+` |
| Trace | `\tr(\hat{\rho})` | Not `Tr` or `tr` |
| Tensor product | `\otimes` | |
| Direct sum | `\oplus` | |

---

## Step 1: Scope Analysis

**Agent**: Notation Analyzer (use `flash`)

For each chapter/file:
1. Read the file
2. Identify the top-5 notation inconsistencies by frequency
3. Output a JSON report: `{file: ..., issues: [{pattern, count, suggested_fix}]}`

---

## Step 2: Apply Corrections

**Agent**: Notation Upgrader (use `flash`, text-only — no PDF needed)

### Agent Prompt Template

```
You are a physics notation standardizer. Your task is to upgrade the mathematical
notation in the following LaTeX file to modern conventions.

NOTATION RULES (from config/notation.json):
- All quantum mechanical operators must have \hat{}: \hat{H}, \hat{p}, \hat{L}
- Use \ket{}, \bra{}, \braket{} macros (defined in the preamble)
- Use \comm{A}{B} for commutators [A,B]
- Use \mathrm{d} for differentials (or \dd if defined)
- Use \dagger for Hermitian conjugate (not +)
- Do NOT change: equation numbers, section titles, proper names, citations

IMPORTANT CONSTRAINTS:
- Preserve all existing \label{} and \eqref{} references exactly
- Do not paraphrase physics content — only notation symbols
- Be conservative: when ambiguous (e.g., H could be a field), leave unchanged
- Add % NOTATION: comment on changed lines for traceability

Input file: {file_path}
Output: overwrite the same file with corrections applied.
```

---

## Step 3: Verification

After applying corrections, run:
```bash
pdflatex -interaction=nonstopmode books/{book_id}/06_compiled/{book_id}.tex
```

Any compilation error reveals a notation change that broke a macro. Fix before proceeding.

---

## Context-Dependence Warning

> [!CAUTION]
> Notation upgrades are **context-dependent**. The symbol `H` in a condensed matter book might be the **magnetic field intensity** (not the Hamiltonian). Always check the surrounding paragraph before applying mechanical substitutions.

The `notation.json` file has a `context_hints` field for each symbol to guide agents:
```json
{
  "symbol": "H",
  "legacy": "H",
  "modern": "\\hat{H}",
  "context_hints": ["Hamiltonian operator", "energy eigenvalue equation"],
  "false_positives": ["magnetic field H", "Hilbert space H", "enthalpy"]
}
```

---

## Integration with `config/notation.json`

The notation table is stored in `config/notation.json` and is the **single source of truth** for all books. When ingesting a new book that uses unconventional notation (e.g., Fazekas uses `c_{k\sigma}^+` instead of `c_{k\sigma}^\dagger`), add an entry to `notation.json` and note it in `book.yaml` under `notation_overrides`.

