"""Other provinces: the formulas match the CRA's provincial pages, and every province runs end to end."""

from datetime import date

import pytest

from finder import Answers, find
from finder import estimates as est
from finder.answers import PROVINCES
from finder.data import load

TODAY = date(2026, 10, 18)


def params(province, benefit_id):
    return load(province)[0][benefit_id]["params"]


def test_bc_family_benefit():
    p = params("BC", "bc_family_benefit")
    assert est.bc_family_benefit(p, kids=1, income=0, single_parent=True) == 1750 + 500
    assert est.bc_family_benefit(p, kids=1, income=30176, single_parent=False) == 1750
    assert est.bc_family_benefit(p, kids=1, income=90000, single_parent=False) == 775     # the floor
    assert est.bc_family_benefit(p, kids=1, income=96562 + 775 / 0.04, single_parent=False) == 0
    assert est.bc_family_benefit(p, kids=3, income=0, single_parent=False) == 1750 + 1100 + 900


def test_bc_renter_credit():
    p = params("BC", "bc_renter_credit")
    assert est.renters_credit(p, income=64764) == 400
    assert est.renters_credit(p, income=84764) == 0


def test_alberta_child_and_family_benefit():
    p = params("AB", "ab_child_family_benefit")
    assert est.alberta_child_family(p, kids=1, income=0, work_income=0) == 1529
    assert est.alberta_child_family(p, kids=2, income=20000, work_income=20000) == 1529 + 764 + 782 + 712
    assert est.alberta_child_family(p, kids=1, income=5000, work_income=5000) == 1529 + 336     # 15% of $2,240
    assert est.alberta_child_family(p, kids=1, income=47115, work_income=0) == 0


def test_saskatchewan_low_income_credit_matches_the_official_range():
    p = params("SK", "sk_low_income_credit")
    assert est.adults_and_children(p, has_partner=True, kids=2, income=39345) == 1282
    assert est.adults_and_children(p, has_partner=True, kids=3, income=0) == 1282      # two children at most
    assert est.adults_and_children(p, has_partner=True, kids=2, income=81668) == 0


def test_nova_scotia():
    p = params("NS", "ns_affordable_living")
    assert est.adults_and_children(p, has_partner=False, kids=0, income=30000) == 255
    assert est.adults_and_children(p, has_partner=True, kids=2, income=0) == 255 + 120
    assert est.adults_and_children(p, has_partner=False, kids=0, income=35100) == 0
    child = params("NS", "ns_child_benefit")
    assert est.flat_per_child(child, kids=2, income=20000) == 3050
    assert est.flat_per_child(child, kids=2, income=30000) is None      # partial range: no formula given


def test_new_brunswick_hst_credit():
    p = params("NB", "nb_hst_credit")
    assert est.adults_and_children(p, has_partner=False, kids=0, income=35000) == 300
    assert est.adults_and_children(p, has_partner=True, kids=2, income=0) == 800
    assert est.adults_and_children(p, has_partner=False, kids=1, income=0) == 600       # single parent's first child


def test_pei():
    p = params("PE", "pe_essentials")
    assert est.pei_essentials(p, family=False, income=50000) == 310
    assert est.pei_essentials(p, family=False, income=101750) == 242        # halfway between $310 and $175 ($242.50)
    assert est.pei_essentials(p, family=True, income=200000) == 175         # everyone gets at least $175
    child = params("PE", "pe_child_benefit")
    assert est.pei_child(child, kids=1, income=40000) == 410
    assert est.pei_child(child, kids=1, income=60000) == 290


def test_quebec_solidarity():
    p = params("QC", "qc_solidarity")
    assert est.quebec_solidarity(p, has_partner=False, kids=0, income=20000, has_home=True) == 363 + 172 + 746
    assert est.quebec_solidarity(p, has_partner=False, kids=0, income=20000, has_home=False) == 363 + 172
    assert est.quebec_solidarity(p, has_partner=True, kids=1, income=43195, has_home=True) == 726 + 906 + 158


@pytest.mark.parametrize("province", PROVINCES)
def test_every_province_runs_for_a_newcomer_family(province):
    family = Answers(age=34, status="pr", arrived="2026-02", province=province, has_partner=True,
                     kids_under_6=1, monthly_rent=1500, work_income=30000, filed_taxes=False,
                     student="part_time", school_type="public")
    report = find(family, today=TODAY)
    health_id = load(province)[1]["plan"]["health_card_id"]
    assert report.get(health_id).status == "likely"
    assert report.get(load(province)[1]["plan"]["student_aid_id"]).status == "likely"
    assert report.total > 0
    assert any("tax return" in step.text for step in report.plan)


def test_quebec_has_no_federal_student_grant_and_two_tax_returns():
    student = Answers(age=20, province="QC", student="full_time", school_type="public", monthly_rent=700)
    report = find(student, today=TODAY)
    assert report.get("student_grant").status == "no"
    assert report.get("qc_afe").status == "likely"
    assert any("TP-1" in step.text for step in report.plan)


def test_quebec_solidarity_waits_18_months_on_a_permit():
    student = Answers(age=23, province="QC", status="study_permit", arrived="2026-01", student="full_time",
                      school_type="public", monthly_rent=800)
    item = find(student, today=TODAY).get("qc_solidarity")
    assert item.status == "not_yet"
    assert item.available_from == "July 2027"


def test_manitoba_doesnt_cover_international_students():
    student = Answers(age=21, province="MB", status="study_permit", arrived="2025-09", student="full_time",
                      school_type="public", housing="residence")
    assert find(student, today=TODAY).get("mb_health").status == "no"


def test_alberta_and_quebec_workers_benefit_shows_no_estimate():
    for province in ("AB", "QC"):
        item = find(Answers(age=30, province=province, work_income=15000), today=TODAY).get("cwb")
        assert item.estimate is None and item.up_to == 1633


def test_ontario_only_programs_stay_in_ontario():
    report = find(Answers(age=22, province="BC", student="full_time", school_type="public"), today=TODAY)
    assert report.get("osap") is None and report.get("ohip") is None
    assert report.get("bc_student_aid").status == "likely"
