#!/usr/bin/env python3
"""Generate markdown reference lists from a bib.tex file.

Creates four files in the _pages/includes directory:
 - accepted_article.md      (@article with journal)
 - inprocess_article.md     (@article without journal)
 - tech_report.md           (@techreport)
 - com.md                   (@inproceedings where Gauvain is first author)

Usage:
  python generate_md_from_bibtex.py [path/to/bib.tex] [output_dir]

Requires: bibtexparser (pip install bibtexparser)
"""
from __future__ import annotations
import os
import sys
from typing import Dict, List

try:
    import bibtexparser
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.customization import convert_to_unicode
except Exception:
    print("Missing dependency: please install bibtexparser (pip install bibtexparser)")
    sys.exit(1)


DEFAULT_BIB = "bib.tex"
DEFAULT_OUT = "_pages/includes"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def format_authors(author_field: str) -> str:
    # bib authors separated by ' and '
    parts = [a.strip() for a in author_field.split(" and ") if a.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return ", ".join(parts[:-1]) + ", and " + parts[-1]


def make_bibtex_from_entry(entry: Dict) -> str:
    w = BibTexWriter()
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = [entry]
    return bibtexparser.dumps(db, writer=w)


def format_citation(entry: Dict) -> str:
    etype = entry.get("ENTRYTYPE", "")
    authors = format_authors(entry.get("author", ""))
    year = entry.get("year", "n.d.")
    title = entry.get("title", "").strip()

    if etype == "article":
        journal = entry.get("journal", "").strip()
        volume = entry.get("volume")
        number = entry.get("number")
        pages = entry.get("pages")
        parts = []
        if authors:
            parts.append(f"{authors} ({year})")
        else:
            parts.append(f"({year})")
        if title:
            parts.append(f"{title}.")
        if journal:
            venue = journal
            if volume:
                venue += f", {volume}"
            if number:
                venue += f"({number})"
            if pages:
                venue += f": {pages}"
            parts.append(venue + ".")
        else:
            if pages:
                parts.append(f"pp. {pages}.")
        return " ".join([p for p in parts if p])

    if etype == "inproceedings":
        book = entry.get("booktitle", entry.get("booktitle", "")).strip()
        pages = entry.get("pages")
        parts = [f"{authors} ({year})" if authors else f"({year})"]
        if title:
            parts.append(f"{title}.")
        if book:
            parts.append(f"In {book}.")
        if pages:
            parts.append(f"pp. {pages}.")
        return " ".join(parts)

    if etype == "techreport":
        institution = entry.get("institution", entry.get("institution", "")).strip()
        parts = [f"{authors} ({year})" if authors else f"({year})"]
        if title:
            parts.append(f"{title}.")
        if institution:
            parts.append(institution + ".")
        return " ".join(parts)

    # fallback
    parts = [f"{authors} ({year})" if authors else f"({year})"]
    if title:
        parts.append(f"{title}.")
    return " ".join(parts)


def entry_is_gauvain_first(entry: Dict) -> bool:
    author_field = entry.get("author", "")
    if not author_field:
        return False
    first = author_field.split(" and ")[0].lower()
    return "gauvain" in first


def write_markdown(entries: List[Dict], outfile: str, title: str) -> None:
    ensure_dir(os.path.dirname(outfile) or ".")
    header = "<!-- Auto-generated from bib.tex -->\n<!-- Do not edit manually -->\n\n"
    header += f"## {title}\n\n"
    lines: List[str] = [header]

    for i, e in enumerate(entries, start=1):
        citation = format_citation(e)
        lines.append(f"{i}. {citation}")
        lines.append("")
        lines.append("<details>")
        lines.append("<summary>BibTeX</summary>\n")
        lines.append("```bibtex")
        lines.append(make_bibtex_from_entry(e).strip())
        lines.append("```")
        lines.append("</details>\n")

    with open(outfile, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main(argv: List[str]) -> int:
    from os.path import dirname
    file= os.path.abspath(__file__)
    dir = dirname((file))
    bibpath = os.path.join(dir, DEFAULT_BIB)
    outdir = os.path.join(dir, DEFAULT_OUT)

    if not os.path.exists(bibpath):
        print(f"bib file not found: {bibpath}")
        return 2

    ensure_dir(outdir)

    with open(bibpath, encoding="utf-8") as fh:
        bibdb = bibtexparser.load(fh)

    # ensure unicode
    bibdb = convert_to_unicode(bibdb)

    accepted = []
    inprocess = []
    techreport = []
    comms = []

    for entry in bibdb.entries:
        etype = entry.get("ENTRYTYPE", "").lower()
        if etype == "article":
            if entry.get("journal"):
                accepted.append(entry)
            else:
                inprocess.append(entry)
        elif etype == "techreport":
            techreport.append(entry)
        elif etype == "inproceedings":
            if entry_is_gauvain_first(entry):
                comms.append(entry)

    write_markdown(accepted, os.path.join(outdir, "accepted_article.md"), "Accepted articles")
    write_markdown(inprocess, os.path.join(outdir, "inprocess_article.md"), "In-process articles")
    write_markdown(techreport, os.path.join(outdir, "tech_report.md"), "Technical reports")
    write_markdown(comms, os.path.join(outdir, "com.md"), "Communications (Gauvain first author)")

    print(f"Wrote: accepted={len(accepted)}, inprocess={len(inprocess)}, techreport={len(techreport)}, comms={len(comms)} to {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
