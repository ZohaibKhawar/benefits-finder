"""Edge cases: birthdays, the 13-week student rule, month 19 in Canada, limits and bad input."""

from datetime import date

import pytest

from finder import Answers, find
from finder.engine import next_tax_deadline

TODAY = date(2026, 10, 18)


def status(answers, benefit_id):
    item = find(answers, today=TODAY).get(benefit_id)
    return item.status if item else None


def test_grocery_benefit_starts_at_19():
    assert status(Answers(age=18), "cgeb") == "not_yet"
    assert status(Answers(age=19), "cgeb") == "likely"
    assert status(Answers(age=18, has_partner=True), "cgeb") == "likely"


def test_visitors_get_no_tax_benefits():
    visitor = Answers(age=30, status="visitor", arrived="2026-08")
    assert status(visitor, "cgeb") == "no"
    assert status(visitor, "ohip") == "no"


def test_workers_benefit_student_rule():
    worker = dict(age=21, work_income=15000)
    assert status(Answers(**worker, student="full_time", school_type="public"), "cwb") == "no"
    assert status(Answers(**worker, student="part_time", school_type="public"), "cwb") == "likely"
    assert status(Answers(**worker, student="full_time", school_type="public", kids_under_6=1), "cwb") == "likely"
    assert status(Answers(age=21), "cwb") is None   # no work income: not shown at all


def test_child_benefit_waits_for_month_19_on_a_permit():
    family = dict(age=30, kids_under_6=1, status="work_permit")
    report = find(Answers(**family, arrived="2025-09"), today=TODAY)
    assert report.get("ccb").status == "not_yet"
    assert report.get("ccb").available_from == "March 2027"
    assert report.get("ocb").status == "not_yet"
    assert any("March 2027" in step.text for step in report.plan)
    assert status(Answers(**family, arrived="2025-01"), "ccb") == "likely"


def test_child_benefit_for_refugee_claimants_waits_for_protection():
    assert status(Answers(age=30, kids_under_6=1, status="refugee_claimant", arrived="2026-01"), "ccb") == "no"
    assert status(Answers(age=30, kids_under_6=1, status="protected", arrived="2026-01"), "ccb") == "likely"


def test_osap_needs_citizen_pr_or_protected():
    student = dict(age=19, student="full_time", school_type="public")
    assert status(Answers(**student), "osap") == "likely"
    assert status(Answers(**student, status="study_permit", arrived="2025-09"), "osap") == "no"
    assert status(Answers(age=19, student="full_time", school_type="high_school"), "osap") is None


def test_career_college_note():
    report = find(Answers(age=19, student="full_time", school_type="career_college"), today=TODAY)
    assert "career college" in report.get("osap").reasons[0]
    assert "career colleges" in report.get("student_grant").reasons[0]


def test_dental_plan_rules():
    assert status(Answers(age=30), "cdcp") == "likely"
    assert status(Answers(age=30, has_dental_plan=True), "cdcp") == "no"
    assert status(Answers(age=30, work_income=90000), "cdcp") == "no"
    assert status(Answers(age=30, filed_taxes=False), "cdcp") == "not_yet"


def test_trillium_needs_rent_or_property_tax():
    assert status(Answers(age=20, housing="family_no_rent"), "oeptc") == "no"
    assert status(Answers(age=17, housing="rent", monthly_rent=500), "oeptc") == "not_yet"
    assert status(Answers(age=40, housing="own"), "oeptc") == "likely"
    assert find(Answers(age=40, housing="own"), today=TODAY).get("oeptc").up_to == 1307


def test_northern_credit_only_up_north():
    assert status(Answers(age=30, monthly_rent=800), "noec") is None
    assert status(Answers(age=30, monthly_rent=800, northern_ontario=True), "noec") == "likely"


def test_ohip_plus_age_and_private_plan():
    assert status(Answers(age=24, arrived="2026-01", status="pr"), "ohip_plus") == "likely"
    assert status(Answers(age=25), "ohip_plus") is None
    assert status(Answers(age=20, has_drug_plan=True), "ohip_plus") == "no"


def test_disability_path():
    report = find(Answers(age=30, disability=True), today=TODAY)
    assert report.get("dtc").status == "maybe"
    assert report.get("cdb").status == "not_yet"
    report = find(Answers(age=30, disability=True, has_dtc=True), today=TODAY)
    assert report.get("dtc") is None
    assert report.get("cdb").status == "likely"


def test_everyone_gets_211_and_a_tax_filing_step():
    report = find(Answers(age=45, work_income=200000), today=TODAY)
    assert report.get("help_211").status == "likely"
    assert any("tax return" in step.text for step in report.plan)


def test_tax_deadline_rolls_over_after_april_30():
    assert next_tax_deadline(date(2027, 3, 1)) == date(2027, 4, 30)
    assert next_tax_deadline(date(2027, 4, 30)) == date(2027, 4, 30)
    assert next_tax_deadline(date(2027, 5, 1)) == date(2028, 4, 30)


def test_results_are_sorted_likely_first():
    report = find(Answers(age=20, student="full_time", school_type="public", work_income=9000,
                          has_dental_plan=True), today=TODAY)
    order = {"likely": 0, "maybe": 1, "not_yet": 2, "no": 3}
    ranks = [order[item.status] for item in report.items]
    assert ranks == sorted(ranks)


@pytest.mark.parametrize("bad", [
    dict(age=20, status="tourist"),
    dict(age=20, student="sometimes"),
    dict(age=20, housing="boat"),
    dict(age=-1),
    dict(age=20, work_income=-5),
    dict(age=20, arrived="last year"),
    dict(age=20, arrived="2026-13"),
])
def test_bad_answers_are_rejected(bad):
    with pytest.raises(ValueError):
        Answers(**bad)
