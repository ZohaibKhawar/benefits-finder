"""Accessibility basics that can be checked without a browser: contrast of every colour pair we use,
one h1 per page, labelled form fields, unique ids, and a page language."""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

from app import app

CSS = (Path(__file__).resolve().parent.parent / "static" / "style.css").read_text(encoding="utf-8")


def tokens(block: str) -> dict:
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9A-Fa-f]{6})", block))


LIGHT = tokens(CSS.split("@media (prefers-color-scheme: dark)")[0])
DARK = {**LIGHT, **tokens(CSS.split("@media (prefers-color-scheme: dark)")[1].split("}\n}")[0])}


def luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


# (text colour, background, minimum ratio): 4.5 for text, 3 for focus rings and big numbers
PAIRS = [
    ("ink", "paper", 4.5), ("ink-2", "paper", 4.5), ("ink", "paper-2", 4.5), ("ink-2", "paper-2", 4.5),
    ("likely", "likely-bg", 4.5), ("notyet", "notyet-bg", 4.5), ("no", "paper", 4.5),
    ("error", "paper", 4.5), ("highlight-ink", "highlight", 4.5), ("paper", "ink", 4.5),
    ("focus", "paper", 3.0), ("ink-2", "rule", 3.0),
]


@pytest.mark.parametrize("theme", [LIGHT, DARK], ids=["light", "dark"])
@pytest.mark.parametrize("fg, bg, minimum", PAIRS)
def test_colour_contrast(theme, fg, bg, minimum):
    assert contrast(theme[fg], theme[bg]) >= minimum, f"{fg} on {bg}"


class PageCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.labels_for, self.fields, self.h1, self.lang = [], set(), [], 0, None
        self.label_depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "h1":
            self.h1 += 1
        if tag == "label":
            self.label_depth += 1
            if "for" in a:
                self.labels_for.add(a["for"])
        if tag in ("input", "textarea", "select") and a.get("type") != "hidden":
            self.fields.append((a.get("id"), self.label_depth > 0))

    def handle_endtag(self, tag):
        if tag == "label":
            self.label_depth -= 1


STUDENT = {"school": "york", "level": "bachelor", "field": "stem", "year": "hs_senior", "grade": "87",
           "status": "citizen", "need": "osap", "first_gen": "1"}

AISHA = {"province": "ON", "city": "toronto", "age": "20", "student": "full_time", "school_type": "public",
         "housing": "rent", "monthly_rent": "900", "work_income": "9000"}


@pytest.mark.parametrize("method, path", [("get", "/"), ("get", "/start"), ("post", "/results"),
                                          ("get", "/benefits"), ("get", "/benefits/cgeb"), ("get", "/about"),
                                          ("get", "/privacy"), ("get", "/fr/start"), ("get", "/awards"),
                                          ("post", "/awards/results"), ("get", "/awards/sources")])
def test_page_structure(method, path):
    client = app.test_client()
    data = STUDENT if path.startswith("/awards") else AISHA
    response = client.post(path, data=data) if method == "post" else client.get(path)
    check = PageCheck()
    check.feed(response.get_data(as_text=True))
    assert check.lang in ("en", "fr")
    assert check.h1 == 1, "exactly one h1"
    assert len(check.ids) == len(set(check.ids)), "duplicate ids"
    for field_id, wrapped in check.fields:
        assert wrapped or field_id in check.labels_for, f"unlabelled field {field_id}"
