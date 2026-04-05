#!/usr/bin/env python3
"""Leaflet cluster map of talk locations from generated Jekyll data."""

import json
from html import escape
from pathlib import Path

import getorg
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut

TIMEOUT = 5
BASE_DIR = Path(__file__).resolve().parent
TALKS_DATA = BASE_DIR / "_data" / "generated_talks.json"


def load_talks(data_path):
    with data_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_description(talk):
    title = escape((talk.get("title") or "").strip())
    venue = escape((talk.get("venue") or "").strip())
    location = escape((talk.get("location") or "").strip())
    link = (talk.get("link") or "").strip()

    if link:
        title_html = f'<a href="{escape(link, quote=True)}">{title}</a>'
    else:
        title_html = title

    details = "; ".join(part for part in [venue, location] if part)
    if details:
        return f"{title_html}<br />{details}"
    return title_html


def main():
    talks = load_talks(TALKS_DATA)
    geocoder = Nominatim(user_agent="academicpages.github.io")
    location_dict = {}

    for talk in talks:
        location = (talk.get("location") or "").strip()
        if not location:
            continue

        description = build_description(talk)

        try:
            location_dict[description] = geocoder.geocode(location, timeout=TIMEOUT)
            print(description, location_dict[description])
        except ValueError as ex:
            print(f"Error: geocode failed on input {location} with message {ex}")
        except GeocoderTimedOut as ex:
            print(f"Error: geocode timed out on input {location} with message {ex}")
        except Exception as ex:
            print(
                f"An unhandled exception occurred while processing input {location} with message {ex}"
            )

    getorg.orgmap.create_map_obj()
    getorg.orgmap.output_html_cluster_map(
        location_dict,
        folder_name="talkmap",
        hashed_usernames=False,
    )


if __name__ == "__main__":
    main()
