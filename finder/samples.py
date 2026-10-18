"""Five made-up people from research/03, used by the tests and the demo."""

from datetime import date

from .answers import Answers

# Every expected number in the tests was worked out for this date.
TODAY = date(2026, 10, 18)

PEOPLE = {
    # 20, full-time university student, rents off campus in Toronto, part-time job, school health plan.
    "aisha": Answers(age=20, status="citizen", student="full_time", school_type="public",
                     housing="rent", monthly_rent=900, work_income=9000,
                     has_dental_plan=True, has_drug_plan=True),
    # 24, international master's student in Waterloo, lives in residence, TA income.
    "wei": Answers(age=24, status="study_permit", arrived="2025-09", student="full_time",
                   school_type="public", housing="residence", work_income=14000,
                   has_dental_plan=True, has_drug_plan=True),
    # New permanent residents in Mississauga with two kids (3 and 8), one income, no return filed yet.
    "carlos_and_maria": Answers(age=35, status="pr", arrived="2026-03", has_partner=True,
                                kids_under_6=1, kids_6_to_17=1, housing="rent", monthly_rent=1800,
                                work_income=38000, filed_taxes=False),
    # 29, part-time college student and single mom in Sudbury, hydro in her name.
    "priya": Answers(age=29, status="citizen", northern_ontario=True, student="part_time",
                     school_type="public", housing="rent", monthly_rent=1100, kids_6_to_17=1,
                     work_income=22000, hydro_in_name=True),
    # 22, refugee claimant in Ottawa, not working, rents a room.
    "daniel": Answers(age=22, status="refugee_claimant", arrived="2026-06", housing="rent",
                      monthly_rent=600, filed_taxes=False),
}
