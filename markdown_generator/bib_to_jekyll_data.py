#!/usr/bin/env python3

from __future__ import annotations

import argparse
import codecs
import json
import re
import shutil
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import quote

import latexcodec  # noqa: F401  Registers LaTeX codecs.
from pybtex.database.input import bibtex


REPO_ROOT = Path(__file__).resolve().parents[1]
CAREER_ROOT = REPO_ROOT.parent / "Career"

DEFAULT_ARTICLES_BIB = CAREER_ROOT / "articles.bib"
DEFAULT_CONFERENCE_BIB = CAREER_ROOT / "conference.bib"
DEFAULT_PUBLICATIONS_OUTPUT = REPO_ROOT / "_data" / "generated_publications.json"
DEFAULT_TALKS_OUTPUT = REPO_ROOT / "_data" / "generated_talks.json"
LOCAL_ARTICLE_PDF_SOURCE = REPO_ROOT / "_data" / "_Article"
PUBLIC_ARTICLE_PDF_DIR = REPO_ROOT / "files" / "articles"
PUBLIC_ARTICLE_PDF_BASE = "/files/articles"

LOCAL_PDF_IGNORED_TOKENS = {
    "alexandre",
    "article",
    "m1h3",
    "m2h3",
    "paper",
    "pdf",
}

STATUS_SORT_KEYS = {
    "in prep.": 99991231,
    "submitted": 99991230,
}

MONTH_LOOKUP = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_match_token(value: str | None) -> str:
    if not value:
        return ""

    decoded = decode_latex(value)
    normalized = unicodedata.normalize("NFKD", decoded)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def decode_latex(value: str | None) -> str:
    if not value:
        return ""

    codec_name: Any = "ulatex"
    decoded = codecs.decode(value, codec_name)
    decoded = decoded.replace("\\", "")
    decoded = decoded.replace("{", "").replace("}", "")
    return normalize_whitespace(decoded.strip(" \t\n\r\"'"))


def parse_keywords(entry) -> set[str]:
    keywords = decode_latex(entry.fields.get("keywords", ""))
    if not keywords:
        return set()
    return {token.strip().lower() for token in keywords.split(",") if token.strip()}


def person_to_text(person) -> str:
    parts = []
    for name_group in (
        person.first_names,
        person.middle_names,
        person.prelast_names,
        person.last_names,
        person.lineage_names,
    ):
        if name_group:
            parts.extend(name_group)

    text = decode_latex(" ".join(parts))
    if text.lower() == "others":
        return "and others"
    return text


def build_authors(entry) -> str:
    authors = [person_to_text(person) for person in entry.persons.get("author", [])]
    return ", ".join(author for author in authors if author)


def build_author_match_tokens(entry) -> set[str]:
    tokens = set()
    for person in entry.persons.get("author", []):
        surname_parts = []
        if person.prelast_names:
            surname_parts.extend(person.prelast_names)
        if person.last_names:
            surname_parts.extend(person.last_names)

        token = normalize_match_token(" ".join(surname_parts))
        if token:
            tokens.add(token)

    return tokens


def build_doi(entry) -> str:
    doi = decode_latex(entry.fields.get("doi", ""))
    return doi


def build_doi_url(entry) -> str:
    doi = build_doi(entry)
    if doi:
        return f"https://doi.org/{doi}"

    return ""


def build_external_url(entry) -> str:
    return decode_latex(entry.fields.get("url", ""))


def build_paper_url(entry) -> str:
    doi_url = build_doi_url(entry)
    if doi_url:
        return doi_url

    url = build_external_url(entry)
    if url:
        return url

    return ""


def parse_month(month_value: str) -> int:
    if not month_value:
        return 1

    if month_value.isdigit():
        return max(1, min(12, int(month_value)))

    return MONTH_LOOKUP.get(month_value.lower(), 1)


def parse_date_fields(entry, bib_key: str = "") -> tuple[str, str, int]:
    year_label = decode_latex(entry.fields.get("year", ""))
    if not year_label and bib_key:
        match = re.search(r"(19|20)\d{2}", bib_key)
        if match:
            year_label = match.group(0)

    if year_label.isdigit():
        month = parse_month(decode_latex(entry.fields.get("month", "")))
        day_label = decode_latex(entry.fields.get("day", ""))
        day = int(day_label) if day_label.isdigit() else 1
        date_value = f"{int(year_label):04d}-{month:02d}-{day:02d}"
        sort_key = int(f"{int(year_label):04d}{month:02d}{day:02d}")
        return date_value, year_label, sort_key

    status_key = STATUS_SORT_KEYS.get(year_label.lower(), 0) if year_label else 0
    return "", year_label, status_key


def infer_event_from_code(code: str, year_label: str) -> str:
    code_upper = code.upper()
    if code_upper.startswith("EGU"):
        return f"EGU General Assembly {year_label}" if year_label.isdigit() else "EGU General Assembly"
    if code_upper.startswith("EPSC-DPS"):
        return f"EPSC-DPS {year_label}" if year_label.isdigit() else "EPSC-DPS"
    return code


def split_event_and_location(raw_event: str, year_label: str) -> tuple[str, str]:
    if not raw_event:
        return "", ""

    if "," not in raw_event:
        return raw_event, ""

    first, rest = raw_event.split(",", 1)
    event = infer_event_from_code(first.strip(), year_label)
    if event.count('"') == 1:
        event = event.replace('"', "")
    location = normalize_whitespace(rest)
    return event, location


def derive_publication_category(entry, keywords: set[str]) -> str:
    entry_type = entry.type.lower()
    if entry_type in {"phdthesis", "masterthesis"}:
        return "theses"
    if "report" in keywords:
        return "reports"
    if entry_type == "inproceedings" or {"oral", "poster"} & keywords:
        return "conferences"
    return "manuscripts"


def choose_publication_venue(entry) -> str:
    for field_name in ("journal", "booktitle", "institution", "school"):
        value = decode_latex(entry.fields.get(field_name, ""))
        if value:
            return value
    return ""


def choose_excerpt(entry) -> str:
    for field_name in ("summary", "description"):
        value = decode_latex(entry.fields.get(field_name, ""))
        if value:
            return value
    return ""


def build_publication_state(keywords: set[str], year_label: str) -> str:
    if "submitted" in keywords or year_label.lower() == "submitted":
        return "submitted"
    return "published"


def build_citation(authors: str, title: str, venue: str, year_label: str) -> str:
    parts = []
    if authors:
        parts.append(authors.rstrip("."))
    if title:
        parts.append(title.rstrip("."))
    if venue:
        parts.append(venue.rstrip("."))
    if year_label:
        parts.append(year_label.rstrip("."))
    if not parts:
        return ""
    return ". ".join(parts) + "."


def build_publication_item(bib_key: str, entry) -> dict:
    keywords = parse_keywords(entry)
    title = decode_latex(entry.fields.get("title", ""))
    authors = build_authors(entry)
    venue = choose_publication_venue(entry)
    date_value, year_label, sort_key = parse_date_fields(entry, bib_key)
    publication_state = build_publication_state(keywords, year_label)
    doi = build_doi(entry)
    doi_url = build_doi_url(entry)
    external_url = build_external_url(entry)
    paper_url = build_paper_url(entry)

    return {
        "bibtex_key": bib_key,
        "collection": "publications",
        "category": derive_publication_category(entry, keywords),
        "title": title,
        "authors": authors,
        "venue": venue,
        "date": date_value,
        "year_label": year_label,
        "sort_key": sort_key,
        "publication_state": publication_state,
        "citation": build_citation(authors, title, venue, year_label),
        "doi": doi,
        "doi_url": doi_url,
        "external_url": external_url,
        "paperurl": paper_url,
        "link": paper_url,
        "excerpt": choose_excerpt(entry),
    }


def parse_local_pdf_metadata(pdf_path: Path) -> tuple[str, set[str]]:
    parts = [normalize_match_token(part) for part in pdf_path.stem.split("_") if part]
    if not parts:
        return "", set()

    year_label = parts[0] if re.fullmatch(r"(19|20)\d{2}", parts[0]) else ""
    match_tokens = {
        token
        for token in parts[1:]
        if token and token not in LOCAL_PDF_IGNORED_TOKENS
    }
    return year_label, match_tokens


def sync_local_article_pdfs() -> list[Path]:
    if not LOCAL_ARTICLE_PDF_SOURCE.exists():
        return []

    source_files = sorted(path for path in LOCAL_ARTICLE_PDF_SOURCE.glob("*.pdf") if path.is_file())
    PUBLIC_ARTICLE_PDF_DIR.mkdir(parents=True, exist_ok=True)

    source_names = {path.name for path in source_files}
    for existing_file in PUBLIC_ARTICLE_PDF_DIR.glob("*.pdf"):
        if existing_file.is_file() and existing_file.name not in source_names:
            existing_file.unlink()

    for source_file in source_files:
        shutil.copy2(source_file, PUBLIC_ARTICLE_PDF_DIR / source_file.name)

    return source_files


def attach_local_pdf_urls(publication_records: list[tuple[dict, Any]]) -> None:
    source_pdf_files = sync_local_article_pdfs()
    if not source_pdf_files:
        return

    publication_metadata = []
    for item, entry in publication_records:
        publication_metadata.append(
            {
                "item": item,
                "category": item["category"],
                "year_label": item["year_label"],
                "author_tokens": build_author_match_tokens(entry),
            }
        )

    for pdf_path in source_pdf_files:
        year_label, match_tokens = parse_local_pdf_metadata(pdf_path)
        if not year_label:
            print(f"Skipping local PDF without parsable year: {pdf_path.name}")
            continue

        candidates = [
            metadata
            for metadata in publication_metadata
            if metadata["category"] != "conferences"
            and metadata["year_label"] == year_label
            and match_tokens.issubset(metadata["author_tokens"])
        ]

        if len(candidates) != 1:
            print(
                "Could not uniquely match local PDF "
                f"{pdf_path.name} to a publication entry (found {len(candidates)} candidate(s))."
            )
            continue

        candidates[0]["item"]["local_pdf_url"] = f"{PUBLIC_ARTICLE_PDF_BASE}/{quote(pdf_path.name)}"


def build_talk_item(bib_key: str, entry) -> dict:
    keywords = parse_keywords(entry)
    title = decode_latex(entry.fields.get("title", ""))
    authors = build_authors(entry)
    date_value, year_label, sort_key = parse_date_fields(entry, bib_key)
    doi = build_doi(entry)
    doi_url = build_doi_url(entry)
    external_url = build_external_url(entry)
    paper_url = build_paper_url(entry)

    raw_event = decode_latex(entry.fields.get("booktitle", ""))
    if not raw_event:
        raw_event = decode_latex(entry.fields.get("number", ""))
    if not raw_event:
        raw_event = decode_latex(entry.fields.get("institution", ""))

    venue, location = split_event_and_location(raw_event, year_label)
    venue = venue.replace('"', "")

    if "poster" in keywords:
        talk_type = "Poster"
        section = "posters"
    elif "oral" in keywords:
        talk_type = "Oral presentation"
        section = "talks"
    else:
        talk_type = "Conference contribution"
        section = "talks"

    return {
        "bibtex_key": bib_key,
        "collection": "talks",
        "section": section,
        "title": title,
        "authors": authors,
        "type": talk_type,
        "venue": venue,
        "location": location,
        "date": date_value,
        "year_label": year_label,
        "sort_key": sort_key,
        "doi": doi,
        "doi_url": doi_url,
        "external_url": external_url,
        "paperurl": paper_url,
        "link": paper_url,
        "excerpt": "",
    }


def parse_bib_file(path: Path):
    parser = bibtex.Parser()
    return parser.parse_file(str(path))


def write_json(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(items, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def build_publications(articles_bib: Path, conference_bib: Path) -> list[dict]:
    publication_records = []
    for source in (articles_bib, conference_bib):
        bib_data = parse_bib_file(source)
        for bib_key, entry in bib_data.entries.items():
            publication_records.append((build_publication_item(bib_key, entry), entry))

    attach_local_pdf_urls(publication_records)
    return [item for item, _ in publication_records]


def build_talks(conference_bib: Path) -> list[dict]:
    bib_data = parse_bib_file(conference_bib)
    return [build_talk_item(bib_key, entry) for bib_key, entry in bib_data.entries.items()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Jekyll _data files for publications and talks from BibTeX sources.",
    )
    parser.add_argument("--articles-bib", type=Path, default=DEFAULT_ARTICLES_BIB)
    parser.add_argument("--conference-bib", type=Path, default=DEFAULT_CONFERENCE_BIB)
    parser.add_argument("--publications-output", type=Path, default=DEFAULT_PUBLICATIONS_OUTPUT)
    parser.add_argument("--talks-output", type=Path, default=DEFAULT_TALKS_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    missing_files = [path for path in (args.articles_bib, args.conference_bib) if not path.exists()]
    if missing_files:
        missing_list = ", ".join(str(path) for path in missing_files)
        raise SystemExit(f"Missing BibTeX source file(s): {missing_list}")

    publications = build_publications(args.articles_bib, args.conference_bib)
    talks = build_talks(args.conference_bib)

    write_json(args.publications_output, publications)
    write_json(args.talks_output, talks)

    print(f"Wrote {len(publications)} publication entries to {args.publications_output}")
    print(f"Wrote {len(talks)} talk entries to {args.talks_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())