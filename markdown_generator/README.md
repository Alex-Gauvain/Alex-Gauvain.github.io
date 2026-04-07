# Markdown Generator

This directory contains various ways of creating Markdown for your site. In general, filenames that end with `.ipynb` or `.py` are similar, but may contain different documentation or are intended to be run from with GitHub when deploying your site.

## Python Scripts

The .py files are Python scripts that that can be run from the command line (ex., `python3 publications.py publications.csv`) with the objective of also ensuring that they have reduced requirements for packages, which may allow them to run when deploying your site from within GitHub.

The `bib_to_jekyll_data.py` script reads BibTeX sources and generates `_data/generated_publications.json` and `_data/generated_talks.json` directly for Jekyll list pages. This avoids maintaining one Markdown file per publication or talk.

Local PDF links are configured explicitly in `_data/local_pdf_mappings.json`.

Talks and posters are generated only from conference entries where Alexandre Gauvain is the first author.

- `publications`: maps a `bibtex_key` to a PDF filename. Preferred location is `_data/_Article/`, from which the file is copied to `/files/articles/` during the build. A mapped file already present in `/files/articles/` is also accepted and preserved.
- `talks`: maps a `bibtex_key` to a PDF filename stored directly in `/files/talks/`.

Example:

```json
{
	"publications": {
		"lemesnil2024characterizing": "2024_Gauvain_LeMesnil.pdf"
	},
	"talks": {
		"gauvainVulnerabilityCoastalAreas2021": "EGU21.pdf"
	}
}
```

Example:

```bash
python3 bib_to_jekyll_data.py \
	--articles-bib ../../Career/articles.bib \
	--conference-bib ../../Career/conference.bib \
	--pdf-mappings ../_data/local_pdf_mappings.json
```

The script requires `pybtex` and `latexcodec` in the active Python environment.

## Jupyter Notebooks

These .ipynb files document the older workflow that generated one Markdown file per talk or publication. They are kept as reference material, but the active workflow for this repository is `bib_to_jekyll_data.py`, which writes directly to Jekyll `_data` files.
*** Add File: /home/agauvain/Git/Alex-Gauvain.github.io/scripts/build_from_bib.sh
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
