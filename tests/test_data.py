"""The data files must be complete, and every benefit must have a rule (and the other way round)."""

from datetime import date

from finder.data import all_benefits, load
from finder.rules import RULES

BENEFITS, LINKS = load("ON")


def test_every_benefit_has_a_rule_and_every_rule_has_data():
    used = {benefit.get("rule", benefit_id) for benefit_id, benefit in all_benefits().items()}
    assert used == set(RULES)


def test_links_are_https():
    for benefit in BENEFITS.values():
        assert benefit["url"].startswith("https://"), benefit["id"]
        if "extra_url" in benefit:
            assert benefit["extra_url"].startswith("https://"), benefit["id"]
    for name, url in LINKS.items():
        if name != "plan":
            assert url.startswith("https://"), name


def test_nothing_is_more_than_a_year_old():
    # Fails on purpose once a benefit hasn't been re-checked for a year.
    for benefit in BENEFITS.values():
        assert (date.today() - benefit["last_checked"]).days < 365, benefit["id"]


def test_ended_programs_are_not_listed():
    names = " ".join(b["name"].lower() for b in BENEFITS.values())
    assert "carbon rebate" not in names
    assert "climate action" not in names


def test_summaries_are_short_enough_to_read_on_a_phone():
    for benefit in BENEFITS.values():
        assert len(benefit["summary"]) <= 320, benefit["id"]
