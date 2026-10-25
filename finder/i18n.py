"""Translations.

English text is the key (like gettext): templates call _("Start"), rules build Msg("...{amount}...").
translations/<lang>.yaml maps the English text to the translated text. Anything missing falls back
to English, and a test lists what's missing.
"""

from datetime import date
from functools import lru_cache
from pathlib import Path

import yaml

LANGUAGES = ("en", "fr")
TRANSLATIONS_DIR = Path(__file__).resolve().parent.parent / "translations"

MONTHS = {
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
           "octobre", "novembre", "décembre"],
}


class Money(float):
    """A dollar amount inside a message; formatted for the reader's language."""


class Month(date):
    """A month inside a message, e.g. March 2027 / mars 2027."""


class BenefitName(str):
    """A benefit id inside a message; shown as that benefit's name in the reader's language."""


class Percent(float):
    """An average inside a message: 88% / 88 %."""


@lru_cache
def catalog(lang: str) -> dict:
    if lang == "en":
        return {}
    path = TRANSLATIONS_DIR / f"{lang}.yaml"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def gettext(text: str, lang: str) -> str:
    if lang == "en" or not text:
        return text
    return catalog(lang).get("text", {}).get(text, text)


def money(amount: float, lang: str = "en") -> str:
    whole = f"{round(amount):,}"
    if lang == "fr":
        return whole.replace(",", " ") + " $"
    return f"${whole}"


def percent(value: float, lang: str = "en") -> str:
    number = f"{value:g}"
    return f"{number.replace('.', ',')} %" if lang == "fr" else f"{number}%"


def month(day: date, lang: str = "en") -> str:
    if lang in MONTHS:
        return f"{MONTHS[lang][day.month - 1]} {day.year}"
    return day.strftime("%B %Y")


def entry_text(section: str, entry: dict, field: str, lang: str):
    """A field of a data-file entry in the reader's language. Sections: benefits, awards, schools."""
    if lang != "en":
        translated = catalog(lang).get(section, {}).get(entry["id"], {}).get(field)
        if translated:
            return translated
    value = entry
    for key in field.split("."):          # "entrance.note" reaches into a nested entry
        value = value.get(key) if isinstance(value, dict) else None
    return value


def benefit_text(benefit: dict, field: str, lang: str):
    """A field of a benefit (name, summary, how_to_get, also_called) in the reader's language."""
    return entry_text("benefits", benefit, field, lang)


def _benefit_name(benefit_id: str, lang: str) -> str:
    from .data import all_benefits      # late import: data imports nothing from here
    benefit = all_benefits().get(benefit_id, {"id": benefit_id, "name": benefit_id})
    return benefit_text(benefit, "name", lang)


def _format(value, lang: str) -> str:
    if isinstance(value, Msg):
        return value.render(lang)
    if isinstance(value, Money):
        return money(value, lang)
    if isinstance(value, Month):
        return month(value, lang)
    if isinstance(value, BenefitName):
        return _benefit_name(value, lang)
    if isinstance(value, Percent):
        return percent(value, lang)
    if isinstance(value, int):
        return f"{value:,}" if lang == "en" else f"{value:,}".replace(",", " ")
    return str(value)


class Msg(str):
    """A sentence with blanks, kept so it can be shown in any language.

    It behaves like its English text (so str(msg) and "x" in msg work), and
    msg.render("fr") gives the French.
    """

    def __new__(cls, template: str, **params):
        text = template.format(**{key: _format(value, "en") for key, value in params.items()})
        obj = super().__new__(cls, text)
        obj.template = template
        obj.params = params
        return obj

    def render(self, lang: str) -> str:
        if lang == "en":
            return str(self)
        template = gettext(self.template, lang)
        return template.format(**{key: _format(value, lang) for key, value in self.params.items()})


class EntryText(Msg):
    """A text field of a data-file entry used as a message (an award's 'check', say)."""

    def __new__(cls, section: str, entry: dict, field: str):
        obj = super().__new__(cls, entry_text(section, entry, field, "en"))
        obj.section, obj.entry, obj.field = section, entry, field
        return obj

    def render(self, lang: str) -> str:
        return entry_text(self.section, self.entry, self.field, lang)


def render(value, lang: str):
    """Show a Msg (or plain text) in the reader's language."""
    if isinstance(value, Msg):
        return value.render(lang)
    return value
