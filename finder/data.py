"""Loads the benefit data files and checks they are complete."""

from functools import lru_cache
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROVINCE_FILES = {
    "ON": "ontario.yaml",
    "BC": "british_columbia.yaml",
    "AB": "alberta.yaml",
    "SK": "saskatchewan.yaml",
    "MB": "manitoba.yaml",
    "QC": "quebec.yaml",
    "NB": "new_brunswick.yaml",
    "NS": "nova_scotia.yaml",
    "PE": "prince_edward_island.yaml",
    "NL": "newfoundland_labrador.yaml",
}

REQUIRED = ("id", "name", "level", "category", "summary", "how_to_get", "url",
            "needs_tax_return", "last_checked", "source")
CATEGORIES = ("money", "study", "health", "support", "help")
SOURCES = ("official", "secondary")


def _read(name: str) -> dict:
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache
def load(province: str = "ON") -> tuple[dict, dict]:
    """Return (benefits by id, in file order) and (named links, plus the province's plan settings)."""
    if province not in PROVINCE_FILES:
        raise ValueError(f"No data for province {province!r} yet")
    federal = _read("federal.yaml")
    local = _read(PROVINCE_FILES[province])
    benefits = {}
    for entry in federal["benefits"] + local["benefits"]:
        missing = [key for key in REQUIRED if key not in entry]
        if missing:
            raise ValueError(f"{entry.get('id', '?')} is missing {missing}")
        if entry["id"] in benefits:
            raise ValueError(f"Duplicate benefit id {entry['id']}")
        if entry["category"] not in CATEGORIES:
            raise ValueError(f"{entry['id']} has unknown category {entry['category']}")
        if entry["source"] not in SOURCES:
            raise ValueError(f"{entry['id']} has unknown source {entry['source']}")
        benefits[entry["id"]] = entry
    links = {**federal.get("links", {}), **local.get("links", {})}
    links["plan"] = local.get("plan", {})
    return benefits, links


@lru_cache
def all_benefits() -> dict:
    """Every benefit in every province file, by id (for names and the sources page)."""
    merged = {}
    for province in PROVINCE_FILES:
        merged.update(load(province)[0])
    return merged
