"""The questionnaire: what we ask, in what order, and how a submitted form becomes Answers.

Each question is one screen. `show_if` hides a screen (or a field inside one) unless an earlier
answer matches; quiz.js does the hiding, and without JavaScript everything shows as one long form.
"""

import json
from dataclasses import asdict, fields
from datetime import date

from .answers import Answers, _parse_month

PROVINCE_CHOICES = [
    ("ON", "Ontario", None),
    ("BC", "British Columbia", None),
    ("AB", "Alberta", None),
    ("SK", "Saskatchewan", None),
    ("MB", "Manitoba", None),
    ("QC", "Quebec", None),
    ("NB", "New Brunswick", None),
    ("NS", "Nova Scotia", None),
    ("PE", "Prince Edward Island", None),
    ("NL", "Newfoundland and Labrador", None),
    ("YT", "Yukon", None),
    ("NT", "Northwest Territories", None),
    ("NU", "Nunavut", None),
]

CITY_CHOICES = [
    ("toronto", "Toronto", None),
    ("ottawa", "Ottawa", None),
    ("peel", "Mississauga or Brampton", None),
    ("hamilton", "Hamilton", None),
    ("waterloo", "Waterloo Region", "Kitchener, Waterloo, Cambridge"),
    ("london", "London", None),
    ("north", "Northern Ontario", "Sudbury, Thunder Bay, Sault Ste. Marie, North Bay, Timmins and other towns up north"),
    ("other", "Somewhere else in Ontario", None),
]

STATUS_CHOICES = [
    ("citizen", "Canadian citizen", None),
    ("pr", "Permanent resident", None),
    ("protected", "Protected person", "Your refugee claim was accepted"),
    ("refugee_claimant", "Refugee claimant", "You're waiting for a decision"),
    ("study_permit", "Study permit", "International student"),
    ("work_permit", "Work permit", "Including a post-graduation work permit"),
    ("visitor", "Visitor", None),
]

QUESTIONS = [
    {"id": "where", "title": "Where do you live?", "fields": [
        {"name": "province", "kind": "radio", "choices": PROVINCE_CHOICES, "default": "ON"},
        {"name": "city", "kind": "radio", "label": "Which part of Ontario?", "choices": CITY_CHOICES,
         "show_if": {"province": ["ON"]}},
    ]},
    {"id": "age", "title": "How old are you?", "fields": [
        {"name": "age", "kind": "number", "min": 0, "max": 120, "required": True, "suffix": "years old"},
    ]},
    {"id": "status", "title": "What's your status in Canada?", "fields": [
        {"name": "status", "kind": "radio", "choices": STATUS_CHOICES, "default": "citizen"},
    ]},
    {"id": "arrived", "title": "When did you move to Canada?", "fields": [
        {"name": "arrived_when", "kind": "radio", "default": "long_ago", "choices": [
            ("long_ago", "I was born here, or came more than 2 years ago", None),
            ("recent", "In the last 2 years", None),
        ]},
        {"name": "arrived_month", "kind": "month", "label": "Which month did you arrive?",
         "help": "Your first day living in Canada, as year and month (like 2025-03).", "show_if": {"arrived_when": ["recent"]}},
    ]},
    {"id": "student", "title": "Are you a student?", "fields": [
        {"name": "student", "kind": "radio", "default": "no", "choices": [
            ("no", "No", None),
            ("full_time", "Yes, full-time", None),
            ("part_time", "Yes, part-time", None),
        ]},
        {"name": "school_type", "kind": "radio", "label": "What kind of school?",
         "show_if": {"student": ["full_time", "part_time"]}, "default": "public", "choices": [
            ("public", "University or public college", None),
            ("career_college", "Private career college", None),
            ("high_school", "High school", None),
        ]},
        {"name": "health_program", "kind": "check", "label": "I study nursing, paramedic or medical lab",
         "show_if": {"student": ["full_time", "part_time"]}},
    ]},
    {"id": "housing", "title": "Where do you live right now?", "fields": [
        {"name": "housing", "kind": "radio", "default": "rent", "choices": [
            ("rent", "I rent", "An apartment, a room, a basement"),
            ("residence", "Student residence", None),
            ("own", "I own my home", None),
            ("family_no_rent", "With family, and I don't pay rent", None),
            ("other", "Somewhere else", "A shelter, or no fixed address"),
        ]},
        {"name": "monthly_rent", "kind": "money", "label": "Your share of the rent each month",
         "show_if": {"housing": ["rent"]}},
        {"name": "hydro_in_name", "kind": "check", "label": "The hydro (electricity) bill is in my name",
         "show_if": {"housing": ["rent", "own"]}},
    ]},
    {"id": "partner", "title": "Do you have a spouse or common-law partner?", "fields": [
        {"name": "has_partner", "kind": "radio", "default": "no", "help": "Common-law means you've lived "
         "together for at least 12 months, or you have a child together.",
         "choices": [("no", "No", None), ("yes", "Yes", None)]},
    ]},
    {"id": "kids", "title": "Do you have children under 18 living with you?", "fields": [
        {"name": "kids_under_6", "kind": "count", "label": "Under 6"},
        {"name": "kids_6_to_17", "kind": "count", "label": "6 to 17"},
    ]},
    {"id": "income", "title": "About how much money came in last year?",
     "help": "Add your partner's too. Rough numbers are fine. Enter 0 if you had none.", "fields": [
        {"name": "work_income", "kind": "money", "label": "From work", "help": "Before tax: jobs, tips, self-employment"},
        {"name": "other_income", "kind": "money", "label": "From anything else",
         "help": "EI, pensions, support payments, taxable scholarships"},
    ]},
    {"id": "plans", "title": "Do you have health coverage through school, work or family?", "fields": [
        {"name": "has_dental_plan", "kind": "check", "label": "Dental coverage",
         "help": "Most college and university students have a student plan."},
        {"name": "has_drug_plan", "kind": "check", "label": "Prescription drug coverage"},
    ]},
    {"id": "disability", "title": "Do you have a disability or a long-term health condition?", "fields": [
        {"name": "disability", "kind": "radio", "default": "no", "choices": [
            ("no", "No", None),
            ("yes", "Yes", None),
            ("yes_dtc", "Yes, and I'm approved for the Disability Tax Credit", None),
        ]},
    ]},
    {"id": "taxes", "title": "Did you file a Canadian tax return last year?", "fields": [
        {"name": "filed_taxes", "kind": "radio", "default": "yes", "choices": [
            ("yes", "Yes", None), ("no", "No", None), ("not_sure", "Not sure", None),
        ]},
    ]},
    {"id": "extras", "title": "Do any of these apply to you?", "help": "Pick all that fit, or none.", "fields": [
        {"name": "repaying_student_loans", "kind": "check", "label": "I'm paying back student loans"},
        {"name": "out_of_work", "kind": "check", "label": "I was laid off, or I've been out of work for 3 months or more"},
        {"name": "bridge_program", "kind": "check", "label": "I'm in a bridging program for people trained in another country"},
        {"name": "on_ow_or_odsp", "kind": "check",
         "label": "I get income assistance or disability assistance from my province",
         "help": "For example Ontario Works or ODSP"},
    ]},
]


class FormError(ValueError):
    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field = field
        self.message = message


def _number(text, field: str, lowest=0, highest=10_000_000) -> float:
    text = (text or "").strip().replace(",", "").replace("$", "").replace(" ", "")
    if not text:
        return 0
    try:
        value = float(text)
    except ValueError:
        raise FormError(field, "Enter a number, like 12000.") from None
    if not lowest <= value <= highest:
        raise FormError(field, "That number looks too big or too small.")
    return value


def answers_from_form(form) -> Answers:
    """Turn a submitted questionnaire into Answers. Raises FormError with the field to fix."""
    get = form.get
    age_text = (get("age") or "").strip()
    if not age_text:
        raise FormError("age", "Enter your age.")
    age = int(_number(age_text, "age", 0, 120))

    arrived = None
    if get("arrived_when") == "recent":
        arrived = (get("arrived_month") or "").strip() or None
        if arrived is None:
            raise FormError("arrived_month", "Pick the month you arrived, or choose the other answer.")
        try:
            when = _parse_month(arrived)
        except ValueError:
            raise FormError("arrived_month", "Enter the month like 2025-03.") from None
        if when > (date.today().year, date.today().month):
            raise FormError("arrived_month", "That month hasn't happened yet. Enter the month you arrived.")

    student = get("student") or "no"
    housing = get("housing") or "rent"
    province = get("province") or "ON"
    disability = get("disability") or "no"
    try:
        return Answers(
            age=age,
            status=get("status") or "citizen",
            arrived=arrived,
            province=province,
            city=(get("city") or None) if province == "ON" else None,
            student=student,
            school_type=(get("school_type") or "public") if student != "no" else None,
            health_program=student != "no" and bool(get("health_program")),
            bridge_program=bool(get("bridge_program")),
            housing=housing,
            monthly_rent=_number(get("monthly_rent"), "monthly_rent", 0, 50_000) if housing == "rent" else 0,
            has_partner=get("has_partner") == "yes",
            kids_under_6=int(_number(get("kids_under_6"), "kids_under_6", 0, 20)),
            kids_6_to_17=int(_number(get("kids_6_to_17"), "kids_6_to_17", 0, 20)),
            work_income=_number(get("work_income"), "work_income"),
            other_income=_number(get("other_income"), "other_income"),
            has_dental_plan=bool(get("has_dental_plan")),
            has_drug_plan=bool(get("has_drug_plan")),
            disability=disability in ("yes", "yes_dtc"),
            has_dtc=disability == "yes_dtc",
            filed_taxes=get("filed_taxes", "yes") == "yes",
            repaying_student_loans=bool(get("repaying_student_loans")),
            out_of_work=bool(get("out_of_work")),
            hydro_in_name=housing in ("rent", "own") and bool(get("hydro_in_name")),
            on_ow_or_odsp=bool(get("on_ow_or_odsp")),
        )
    except ValueError as error:
        if isinstance(error, FormError):
            raise
        field = "arrived_month" if "arrived" in str(error) else "age"
        raise FormError(field, "Check this answer.") from None


def answers_to_json(answers: Answers) -> str:
    """For the hidden field that lets the results page re-send answers (calendar, edit) by POST."""
    return json.dumps(asdict(answers), separators=(",", ":"))


def answers_from_json(text: str) -> Answers:
    """Answers sent back by the browser: anything tampered with or out of date is a ValueError."""
    data = json.loads(text or "{}")
    if not isinstance(data, dict):
        raise ValueError("bad answers")
    known = {f.name for f in fields(Answers)}
    try:
        return Answers(**{key: value for key, value in data.items() if key in known})
    except (TypeError, AttributeError) as error:   # wrong types, or no age at all
        raise ValueError("bad answers") from error


def form_values(answers: Answers) -> dict:
    """The questionnaire's field values for these answers (to pre-fill 'Change my answers')."""
    a = answers
    return {
        "province": a.province, "city": a.city or "", "age": str(a.age), "status": a.status,
        "arrived_when": "recent" if a.arrived else "long_ago", "arrived_month": a.arrived or "",
        "student": a.student, "school_type": a.school_type or "public",
        "health_program": a.health_program, "housing": a.housing,
        "monthly_rent": f"{a.monthly_rent:g}" if a.monthly_rent else "",
        "hydro_in_name": a.hydro_in_name, "has_partner": "yes" if a.has_partner else "no",
        "kids_under_6": str(a.kids_under_6) if a.kids_under_6 else "",
        "kids_6_to_17": str(a.kids_6_to_17) if a.kids_6_to_17 else "",
        "work_income": f"{a.work_income:g}", "other_income": f"{a.other_income:g}",
        "has_dental_plan": a.has_dental_plan, "has_drug_plan": a.has_drug_plan,
        "disability": "yes_dtc" if a.has_dtc else "yes" if a.disability else "no",
        "filed_taxes": "yes" if a.filed_taxes else "no",
        "repaying_student_loans": a.repaying_student_loans, "out_of_work": a.out_of_work,
        "bridge_program": a.bridge_program, "on_ow_or_odsp": a.on_ow_or_odsp,
    }
