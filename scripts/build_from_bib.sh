#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -x "$BASE_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$BASE_DIR/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "Error: Python interpreter not found. Create .venv or install python3." >&2
  exit 1
fi

cd "$BASE_DIR"

echo "Generating Jekyll data from BibTeX..."
"$PYTHON_BIN" markdown_generator/bib_to_jekyll_data.py \
  --articles-bib ../Career/articles.bib \
  --conference-bib ../Career/conference.bib

echo "Cleaning previous site output..."
bundle exec jekyll clean

echo "Building site..."
bundle exec jekyll build

echo "Site rebuilt successfully from BibTeX sources."