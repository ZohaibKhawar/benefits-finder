"""What the person told us in the questionnaire, plus a few values worked out from it."""

import math
from dataclasses import dataclass
from datetime import date

STATUSES = ("citizen", "pr", "protected", "refugee_claimant", "study_permit", "work_permit", "visitor")
STUDENT = ("no", "full_time", "part_time")
SCHOOL_TYPES = (None, "public", "career_college", "high_school")
HOUSING = ("rent", "residence", "own", "family_no_rent", "other")

# Statuses that can get OSAP, the Canada Student Grant and most Ontario programs.
STATUS_CAN_GET_OSAP = ("citizen", "pr", "protected")


PROVINCES = ("ON", "BC", "AB", "SK", "MB", "QC", "NB", "NS", "PE", "NL", "YT", "NT", "NU")

# Ontario areas the questionnaire offers; the north gets the Northern Ontario Energy Credit.
ONTARIO_CITIES = ("toronto", "ottawa", "peel", "hamilton", "waterloo", "london", "north", "other")


@dataclass
class Answers:
    age: int
    status: str = "citizen"
    arrived: str | None = None          # "YYYY-MM" if they moved to Canada; None if born here
    province: str = "ON"
    city: str | None = None             # one of ONTARIO_CITIES in Ontario
    northern_ontario: bool = False
    student: str = "no"
    school_type: str | None = None
    health_program: bool = False        # nursing, paramedic or medical lab
    bridge_program: bool = False        # bridge training for people trained in another country
    housing: str = "rent"
    monthly_rent: float = 0             # their own share
    has_partner: bool = False
    kids_under_6: int = 0
    kids_6_to_17: int = 0
    work_income: float = 0              # last year, theirs plus their partner's
    other_income: float = 0             # last year, theirs plus their partner's
    has_dental_plan: bool = False       # through school, work or family
    has_drug_plan: bool = False
    disability: bool = False
    has_dtc: bool = False               # approved for the Disability Tax Credit
    filed_taxes: bool = True            # filed a Canadian return for last year
    repaying_student_loans: bool = False
    out_of_work: bool = False           # laid off, or out of work 12+ weeks
    hydro_in_name: bool = False
    on_ow_or_odsp: bool = False

    def __post_init__(self):
        if self.province not in PROVINCES:
            raise ValueError(f"province must be one of {PROVINCES}")
        if self.province == "ON" and self.city is not None and self.city not in ONTARIO_CITIES:
            raise ValueError(f"city must be one of {ONTARIO_CITIES}")
        if self.city == "north":
            self.northern_ontario = True
        if self.status not in STATUSES:
            raise ValueError(f"status must be one of {STATUSES}")
        if self.student not in STUDENT:
            raise ValueError(f"student must be one of {STUDENT}")
        if self.school_type not in SCHOOL_TYPES:
            raise ValueError(f"school_type must be one of {SCHOOL_TYPES}")
        if self.housing not in HOUSING:
            raise ValueError(f"housing must be one of {HOUSING}")
        if not 0 <= self.age <= 120:
            raise ValueError("age must be between 0 and 120")
        for name in ("monthly_rent", "work_income", "other_income", "kids_under_6", "kids_6_to_17"):
            if not 0 <= getattr(self, name) < math.inf:     # also rejects NaN
                raise ValueError(f"{name} must be a number, 0 or more")
        if self.arrived is not None:
            _parse_month(self.arrived)

    @property
    def kids(self) -> int:
        return self.kids_under_6 + self.kids_6_to_17

    @property
    def income(self) -> float:
        """Family net income, used as a stand-in for the CRA's adjusted family net income."""
        return self.work_income + self.other_income

    @property
    def family(self) -> bool:
        return self.has_partner or self.kids > 0

    @property
    def tax_resident(self) -> bool:
        # Anyone who lives here with a home, partner or kids is usually a resident for tax
        # purposes, including international students. Visitors usually aren't.
        return self.status != "visitor"

    @property
    def temporary(self) -> bool:
        return self.status in ("study_permit", "work_permit")

    @property
    def can_get_osap(self) -> bool:
        return self.status in STATUS_CAN_GET_OSAP

    @property
    def post_secondary(self) -> bool:
        return self.student != "no" and self.school_type != "high_school"

    def months_in_canada(self, today: date) -> int | None:
        if self.arrived is None:
            return None
        year, month = _parse_month(self.arrived)
        return max(0, (today.year - year) * 12 + today.month - month)

    def is_newcomer(self, today: date) -> bool:
        """Arrived in the last two years."""
        months = self.months_in_canada(today)
        return months is not None and months < 24


def _parse_month(text: str) -> tuple[int, int]:
    try:
        year, month = (int(part) for part in text.split("-"))
    except ValueError:
        raise ValueError("arrived must look like 2026-03") from None
    if not (1 <= month <= 12 and 1900 <= year <= 2100):
        raise ValueError("arrived must look like 2026-03")
    return year, month


def add_months(text: str, months: int) -> date:
    year, month = _parse_month(text)
    total = year * 12 + (month - 1) + months
    return date(total // 12, total % 12 + 1, 1)
