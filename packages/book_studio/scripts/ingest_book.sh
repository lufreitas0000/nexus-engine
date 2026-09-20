#!/usr/bin/env bash
# scripts/ingest_book.sh
# One-command launcher for ingesting a new book through all pipeline stages.
#
# Usage:
#   bash scripts/ingest_book.sh baym_quantum_mechanics_1969
#   bash scripts/ingest_book.sh baym_quantum_mechanics_1969 --skip-ocr
#   bash scripts/ingest_book.sh baym_quantum_mechanics_1969 --stage 2
#
# The book must have a directory under books/ with a book.yaml file.

set -e

BOOK_ID="${1:-}"
EXTRA_ARGS="${@:2}"

if [ -z "$BOOK_ID" ]; then
  echo "Usage: bash scripts/ingest_book.sh <book_id> [--skip-ocr] [--stage N]"
  echo ""
  echo "Available books:"
  ls books/
  exit 1
fi

BOOK_YAML="books/$BOOK_ID/book.yaml"
if [ ! -f "$BOOK_YAML" ]; then
  echo "Error: $BOOK_YAML not found."
  echo "Create it first using books/TEMPLATE/book.yaml as a guide."
  exit 1
fi

echo "=================================================="
echo " PDF Ingestion Pipeline"
echo " Book: $BOOK_ID"
echo " book.yaml: $BOOK_YAML"
echo "=================================================="

# Activate Python environment
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
elif [ -f "env/bin/activate" ]; then
  source env/bin/activate
fi

# Run pipeline via main.py
python3 src/main.py run-pipeline "$BOOK_YAML" $EXTRA_ARGS

echo ""
echo "Pipeline done. To compile the book:"
echo "  python3 src/main.py compile $BOOK_YAML"
