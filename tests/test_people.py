"""The five sample people from research/03, worked out by hand."""

import pytest

from finder import find
from finder.samples import PEOPLE, TODAY


@pytest.fixture(scope="module")
def reports():
    return {name: find(answers, today=TODAY) for name, answers in PEOPLE.items()}


def status(report, benefit_id):
    item = report.get(benefit_id)
    return item.status if item else None


def estimate(report, benefit_id):
    return report.get(benefit_id).estimate


def test_aisha_domestic_student_renting(reports):
    r = reports["aisha"]
    assert estimate(r, "cgeb") == 445          # $9,000 is below where the single top-up starts
    assert estimate(r, "ostc") == 378
    assert estimate(r, "oeptc") == 579
    assert status(r, "cwb") == "no"             # full-time student
    assert status(r, "cdcp") == "no"            # student dental plan
    assert status(r, "ohip_plus") == "no"       # student drug plan pays first
    assert status(r, "osap") == "likely"
    assert status(r, "student_grant") == "maybe"
    assert status(r, "clb") == "maybe"          # 20, could still claim before 21
    assert status(r, "liwtc") == "no"           # owes no Ontario tax
    assert status(r, "ohip") is None            # born here
    assert r.total == 445 + 378 + 579


def test_wei_international_student_in_residence(reports):
    r = reports["wei"]
    assert estimate(r, "cgeb") == 494
    assert estimate(r, "oeptc") == 25
    assert status(r, "osap") == "no"
    assert status(r, "student_grant") == "no"
    assert status(r, "ohip") == "no"
    assert status(r, "tuition_credit") == "likely"
    assert status(r, "ccb") is None
    assert r.total == 494 + 378 + 25


def test_carlos_and_maria_new_permanent_residents(reports):
    r = reports["carlos_and_maria"]
    assert estimate(r, "ccb") == 8157 + 6883
    assert estimate(r, "ocb") == 2629
    assert estimate(r, "cgeb") == 890 + 2 * 234
    assert estimate(r, "ostc") == 1444
    assert estimate(r, "oeptc") == 761
    assert status(r, "cwb") == "maybe"          # not resident for the whole first year
    assert status(r, "cdcp") == "not_yet"       # no tax return yet
    assert status(r, "ohip") == "likely"
    assert status(r, "healthy_smiles") == "no"  # $38,000 is over the 2-child limit
    assert status(r, "settlement") == "likely"
    assert status(r, "liwtc") == "maybe"
    assert r.total == 15040 + 2629 + 1358 + 1444 + 761
    plan = " ".join(step.text for step in r.plan)
    assert "RC66" in plan and "OHIP" in plan and "Social Insurance Number" in plan
    assert "April 30, 2027" in plan
    assert "After you file, apply for the Canadian Dental Care Plan" in plan


def test_priya_single_mom_part_time_student_up_north(reports):
    r = reports["priya"]
    assert estimate(r, "ccb") == 6883
    assert estimate(r, "ocb") == 1760
    assert estimate(r, "cgeb") == 445 + 445 + 234
    assert estimate(r, "cwb") == 2813           # part-time student, so the student rule doesn't apply
    assert estimate(r, "noec") == 290
    assert estimate(r, "oeptc") == 627
    assert status(r, "cdcp") == "likely"
    assert status(r, "healthy_smiles") == "likely"
    assert status(r, "training_credit") == "likely"
    assert status(r, "oesp") == "maybe"
    assert r.total == 6883 + 2813 + 1760 + 1124 + 756 + 627 + 290


def test_daniel_refugee_claimant(reports):
    r = reports["daniel"]
    assert status(r, "ifhp") == "likely"
    assert status(r, "ohip") == "no"
    assert status(r, "cdcp") is None            # IFHP covers dental
    assert status(r, "ccb") is None
    assert status(r, "ontario_works") == "maybe"
    assert estimate(r, "cgeb") == 445
    assert "RC151" in " ".join(step.text for step in r.plan)
    assert r.total == 445 + 378 + 507
