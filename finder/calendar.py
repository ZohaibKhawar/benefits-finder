"""A calendar file (.ics) with the dates that matter for this person. Nothing is stored or sent:
the browser downloads it and the person adds it to their own calendar."""

from datetime import date, datetime, timezone

from .engine import Report
from .i18n import Month, benefit_text, gettext


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _event(day: date, summary: str, description: str, url: str, uid: str, stamp: str) -> list[str]:
    return [
        "BEGIN:VEVENT",
        f"UID:{uid}@claimable",
        f"DTSTAMP:{stamp}",
        f"DTSTART;VALUE=DATE:{day:%Y%m%d}",
        f"SUMMARY:{_escape(summary)}",
        f"DESCRIPTION:{_escape(description)}",
        f"URL:{url}",
        "END:VEVENT",
    ]


def build_calendar(report: Report, lang: str, link_base: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    deadline = report.tax_deadline
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Claimable//EN", "CALSCALE:GREGORIAN"]

    lines += _event(deadline, gettext("Tax deadline: file your return", lang),
                    gettext("File even if you had no income. Most benefits only start after you file.", lang),
                    link_base, f"taxes-{deadline.year}", stamp)
    new_year = date(deadline.year, 7, 1)
    lines += _event(new_year, gettext("New benefit year: amounts change", lang),
                    gettext("Benefit amounts change every July. Check Claimable again.", lang),
                    link_base, f"july-{new_year.year}", stamp)
    for item in report.not_yet:
        opens = item.available_from.params.get("month") if item.available_from else None
        if isinstance(opens, Month):
            name = benefit_text(item.benefit, "name", lang)
            lines += _event(opens, gettext("You can now apply: {name}", lang).format(name=name),
                            benefit_text(item.benefit, "how_to_get", lang), item.url,
                            f"{item.id}-{opens:%Y%m}", stamp)
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
