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
DEFAULT_LOCAL_PDF_MAPPINGS = REPO_ROOT / "_data" / "local_pdf_mappings.json"
LOCAL_ARTICLE_PDF_SOURCE = REPO_ROOT / "_data" / "_Article"
PUBLIC_ARTICLE_PDF_DIR = REPO_ROOT / "files" / "articles"
PUBLIC_ARTICLE_PDF_BASE = "/files/articles"
LOCAL_TALK_PDF_DIR = REPO_ROOT / "files" / "talks"
PUBLIC_TALK_PDF_BASE = "/files/talks"
PROFILE_OWNER_SURNAME = "gauvain"

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


def normalize_person_token(value: str | None) -> str:
    if not value:
        return ""

    normalized = unicodedata.normalize("NFKD", decode_latex(value))
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


def is_profile_owner_first_author(entry) -> bool:
    authors = entry.persons.get("author", [])
    if not authors:
        return False

    first_author = authors[0]
    surname_parts = []
    if first_author.prelast_names:
        surname_parts.extend(first_author.prelast_names)
    if first_author.last_names:
        surname_parts.extend(first_author.last_names)

    return normalize_person_token(" ".join(surname_parts)) == PROFILE_OWNER_SURNAME


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


def sync_local_article_pdfs(preserved_public_names: set[str] | None = None) -> list[Path]:
    preserved_public_names = preserved_public_names or set()
    PUBLIC_ARTICLE_PDF_DIR.mkdir(parents=True, exist_ok=True)

    if LOCAL_ARTICLE_PDF_SOURCE.exists():
        source_files = sorted(path for path in LOCAL_ARTICLE_PDF_SOURCE.glob("*.pdf") if path.is_file())
    else:
        source_files = []

    source_names = {path.name for path in source_files}
    for existing_file in PUBLIC_ARTICLE_PDF_DIR.glob("*.pdf"):
        if (
            existing_file.is_file()
            and existing_file.name not in source_names
            and existing_file.name not in preserved_public_names
        ):
            existing_file.unlink()

    for source_file in source_files:
        shutil.copy2(source_file, PUBLIC_ARTICLE_PDF_DIR / source_file.name)

    return source_files


def load_local_pdf_mappings(path: Path) -> dict[str, dict[str, str]]:
    empty_mapping = {"publications": {}, "talks": {}}
    if not path.exists():
        return empty_mapping

    with path.open("r", encoding="utf-8") as stream:
        raw_mappings = json.load(stream)

    if not isinstance(raw_mappings, dict):
        raise SystemExit(f"Invalid local PDF mapping file: expected an object in {path}")

    parsed_mappings: dict[str, dict[str, str]] = {}
    for section in ("publications", "talks"):
        section_mapping = raw_mappings.get(section, {})
        if section_mapping is None:
            section_mapping = {}
        if not isinstance(section_mapping, dict):
            raise SystemExit(f"Invalid local PDF mapping section '{section}' in {path}")

        parsed_mappings[section] = {
            str(bibtex_key): str(pdf_name).strip()
            for bibtex_key, pdf_name in section_mapping.items()
            if str(pdf_name).strip()
        }

    return parsed_mappings


def apply_local_pdf_mapping(
    items: list[dict[str, Any]],
    pdf_mapping: dict[str, str],
    pdf_dir: Path,
    public_pdf_base: str,
    entry_label: str,
) -> None:
    if not pdf_mapping:
        return

    items_by_key = {item["bibtex_key"]: item for item in items}

    for bibtex_key, pdf_name in pdf_mapping.items():
        item = items_by_key.get(bibtex_key)
        if item is None:
            print(f"Skipping unknown {entry_label} bibtex_key in local PDF mapping: {bibtex_key}")
            continue

        pdf_path = pdf_dir / pdf_name
        if not pdf_path.exists():
            print(f"Skipping missing mapped PDF for {entry_label} {bibtex_key}: {pdf_path}")
            continue

        item["local_pdf_url"] = f"{public_pdf_base}/{quote(pdf_name)}"


def apply_publication_pdf_mapping(
    publication_items: list[dict[str, Any]],
    pdf_mapping: dict[str, str],
) -> None:
    sync_local_article_pdfs(set(pdf_mapping.values()))
    apply_local_pdf_mapping(
        publication_items,
        pdf_mapping,
        PUBLIC_ARTICLE_PDF_DIR,
        PUBLIC_ARTICLE_PDF_BASE,
        "publication",
    )


def apply_talk_pdf_mapping(
    talk_items: list[dict[str, Any]],
    pdf_mapping: dict[str, str],
) -> None:
    apply_local_pdf_mapping(
        talk_items,
        pdf_mapping,
        LOCAL_TALK_PDF_DIR,
        PUBLIC_TALK_PDF_BASE,
        "talk",
    )


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


def build_publications(articles_bib: Path, conference_bib: Path, pdf_mapping: dict[str, str]) -> list[dict]:
    publication_records = []
    for source in (articles_bib, conference_bib):
        bib_data = parse_bib_file(source)
        for bib_key, entry in bib_data.entries.items():
            publication_records.append((build_publication_item(bib_key, entry), entry))

    publication_items = [item for item, _ in publication_records]
    apply_publication_pdf_mapping(publication_items, pdf_mapping)
    return publication_items


def build_talks(conference_bib: Path, pdf_mapping: dict[str, str]) -> list[dict]:
    bib_data = parse_bib_file(conference_bib)
    talk_items = [
        build_talk_item(bib_key, entry)
        for bib_key, entry in bib_data.entries.items()
        if is_profile_owner_first_author(entry)
    ]
    apply_talk_pdf_mapping(talk_items, pdf_mapping)
    return talk_items


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Jekyll _data files for publications and talks from BibTeX sources.",
    )
    parser.add_argument("--articles-bib", type=Path, default=DEFAULT_ARTICLES_BIB)
    parser.add_argument("--conference-bib", type=Path, default=DEFAULT_CONFERENCE_BIB)
    parser.add_argument("--publications-output", type=Path, default=DEFAULT_PUBLICATIONS_OUTPUT)
    parser.add_argument("--talks-output", type=Path, default=DEFAULT_TALKS_OUTPUT)
    parser.add_argument("--pdf-mappings", type=Path, default=DEFAULT_LOCAL_PDF_MAPPINGS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    missing_files = [path for path in (args.articles_bib, args.conference_bib) if not path.exists()]
    if missing_files:
        missing_list = ", ".join(str(path) for path in missing_files)
        raise SystemExit(f"Missing BibTeX source file(s): {missing_list}")

    pdf_mappings = load_local_pdf_mappings(args.pdf_mappings)

    publications = build_publications(args.articles_bib, args.conference_bib, pdf_mappings["publications"])
    talks = build_talks(args.conference_bib, pdf_mappings["talks"])

    write_json(args.publications_output, publications)
    write_json(args.talks_output, talks)

    print(f"Wrote {len(publications)} publication entries to {args.publications_output}")
    print(f"Wrote {len(talks)} talk entries to {args.talks_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())