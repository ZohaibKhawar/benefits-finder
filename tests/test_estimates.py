"""The formulas must land exactly on the numbers the CRA publishes."""

import pytest

from finder import estimates as est
from finder.data import load

BENEFITS, _ = load("ON")


def params(benefit_id):
    return BENEFITS[benefit_id]["params"]


# ------------------------------------------------ Canada Groceries and Essentials Benefit

# CRA "who is eligible" table, 2025 base year: income at which the benefit reaches zero.
CGEB_ZERO_POINTS = [
    # (has_partner, kids, official income limit)
    (False, 0, 60012),
    (False, 1, 68912),
    (False, 2, 73592),
    (False, 3, 78272),
    (False, 4, 82952),
    (True, 0, 64232),
    (True, 1, 68912),
    (True, 2, 73592),
    (True, 3, 78272),
    (True, 4, 82952),
]


@pytest.mark.parametrize("has_partner, kids, limit", CGEB_ZERO_POINTS)
def test_cgeb_reaches_zero_at_the_official_limit(has_partner, kids, limit):
    p = params("cgeb")
    assert est.cgeb(p, has_partner=has_partner, kids=kids, income=limit) == 0
    assert est.cgeb(p, has_partner=has_partner, kids=kids, income=limit - 100) > 0


def test_cgeb_official_maximums():
    p = params("cgeb")
    assert est.cgeb(p, has_partner=False, kids=0, income=30000) == 679
    assert est.cgeb(p, has_partner=True, kids=0, income=30000) == 890
    assert est.cgeb(p, has_partner=True, kids=1, income=30000) - 890 == 234


def test_cgeb_single_top_up_builds_with_income():
    p = params("cgeb")
    assert est.cgeb(p, has_partner=False, kids=0, income=0) == 445
    assert est.cgeb(p, has_partner=False, kids=0, income=15000) == 514
    assert est.cgeb(p, has_partner=False, kids=0, income=50000) == 501


# ------------------------------------------------ Canada Workers Benefit (2025 tax year)

def test_cwb_single():
    p = params("cwb")
    assert est.cwb(p, family=False, work_income=20000, income=20000) == 1633
    assert est.cwb(p, family=False, work_income=37742, income=37742) == 0
    assert est.cwb(p, family=False, work_income=3000, income=3000) == 0
    assert est.cwb(p, family=False, work_income=5000, income=5000) == 540   # 27% of $2,000


def test_cwb_family():
    p = params("cwb")
    assert est.cwb(p, family=True, work_income=25000, income=25000) == 2813
    assert est.cwb(p, family=True, work_income=49393, income=49393) == 0


# ------------------------------------------------ Canada Child Benefit (July 2026 to June 2027)

def test_ccb_full_amounts_below_first_threshold():
    p = params("ccb")
    assert est.ccb(p, under_6=1, age_6_to_17=0, income=38237) == 8157
    assert est.ccb(p, under_6=0, age_6_to_17=1, income=10000) == 6883


def test_ccb_second_threshold_matches_both_formulas():
    p = params("ccb")
    # At the second threshold both reduction formulas must give the same answer.
    for kids in range(1, 5):
        just_below = est.ccb(p, under_6=kids, age_6_to_17=0, income=82847)
        just_above = est.ccb(p, under_6=kids, age_6_to_17=0, income=82848)
        assert abs(just_below - just_above) <= 1


def test_ccb_one_child_at_second_threshold():
    p = params("ccb")
    assert est.ccb(p, under_6=1, age_6_to_17=0, income=82847) == 8157 - 3123


# ------------------------------------------------ Ontario Trillium Benefit parts

def test_oeptc_maximum_needs_big_occupancy_cost():
    p = params("oeptc")
    # Occupancy cost of $9,440 (rent of $47,200) reaches both caps: $290 + $944 + $73.
    assert est.oeptc(p, annual_rent=47200, income=0, family=False) == 1307


def test_oeptc_student_residence_is_25():
    p = params("oeptc")
    assert est.oeptc(p, residence=True, income=10000, family=False) == 25


def test_oeptc_renter_example():
    p = params("oeptc")
    # $900/month: occupancy $2,160 -> energy $290 + property ($216 + $73) = $579.
    assert est.oeptc(p, annual_rent=10800, income=20000, family=False) == 579
    # 2% reduction above $29,047 for a single person.
    assert est.oeptc(p, annual_rent=10800, income=39047, family=False) == 379


def test_ostc():
    p = params("ostc")
    assert est.ostc(p, has_partner=False, kids=0, income=29047) == 378
    assert est.ostc(p, has_partner=False, kids=0, income=38497) == 0
    assert est.ostc(p, has_partner=True, kids=2, income=36309) == 4 * 378


def test_ocb():
    p = params("ocb")
    assert est.ocb(p, kids=1, income=26865) == 1760
    assert est.ocb(p, kids=2, income=0) == 3520


def test_noec():
    p = params("noec")
    assert est.noec(p, family=False, income=20000) == 189
    assert est.noec(p, family=True, income=20000) == 290


def test_liwtc():
    p = params("liwtc")
    assert est.liwtc(p, has_partner=False, work_income=10000, income=10000) == 505
    assert est.liwtc(p, has_partner=False, work_income=25000, income=25000) == 850
    assert est.liwtc(p, has_partner=False, work_income=38500, income=38500) == 0
