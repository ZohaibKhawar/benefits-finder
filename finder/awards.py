"""Scholarships and bursaries for students at Ontario colleges and universities.

A second, shorter questionnaire: school, program, year, average, status, money, and a few optional
questions about who they are. It lists their school's own awards (with the automatic entrance
scholarship at their average, where the school publishes one) and the outside awards they fit,
each linking to the official page. Nothing is saved, the same as the main questionnaire.

Statuses:
  fits   - meets every rule we asked about (many awards are still competitive)
  check  - could fit; depends on something we didn't ask (shown with what to check)
  no     - a rule we asked about rules them out; the reason is shown
Awards for a group the student isn't in, or a level or field they aren't studying, aren't shown at all.
"""

import json
from dataclasses import asdict, dataclass, field, fields
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

import yaml

from .form import STATUS_CHOICES, FormError, _number
from .i18n import EntryText, Msg, Percent

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

LEVELS = ("college", "bachelor", "masters", "phd")
YEARS = ("hs_senior", "first", "second", "third", "fourth_plus")
FIELDS = ("stem", "health", "business", "arts", "social", "trades", "creative", "undecided")
NEEDS = ("osap", "tight", "no")
IDENTITIES = ("first_nations", "metis", "inuit", "black", "disability", "first_gen", "care", "military_family")
ACTIVITIES = ("volunteer", "leadership", "research", "language")
STATUSES = ("citizen", "pr", "protected", "refugee_claimant", "study_permit", "work_permit")
DOMESTIC = ("citizen", "pr", "protected")
NO_SCHOOL = ("other", "undecided")
GROUPS = (("government", "From governments"), ("foundation", "From foundations and organizations"),
          ("search", "Places to search for more"))

# Grade points -> the lowest percentage that earns them, for the scales Ontario schools use.
# We take the bottom of each letter grade, so a converted average never looks better than it is.
SCALES = {
    "percent": None,
    "4": [(4.0, 85), (3.7, 80), (3.3, 77), (3.0, 73), (2.7, 70), (2.3, 67), (2.0, 63), (1.7, 60),
          (1.3, 57), (1.0, 53), (0.7, 50), (0, 0)],
    "4.33": [(4.33, 90), (4.0, 85), (3.67, 80), (3.33, 77), (3.0, 73), (2.67, 70), (2.33, 67), (2.0, 63),
             (1.67, 60), (1.33, 57), (1.0, 53), (0.67, 50), (0, 0)],
    "9": [(9, 90), (8, 80), (7, 75), (6, 70), (5, 65), (4, 60), (3, 55), (2, 50), (1, 40), (0, 0)],
    "10": [(10, 90), (9, 85), (8, 80), (7, 75), (6, 70), (5, 65), (4, 60), (3, 55), (2, 50), (1, 40), (0, 0)],
    "12": [(12, 90), (11, 85), (10, 80), (9, 77), (8, 73), (7, 70), (6, 67), (5, 63), (4, 60), (3, 57),
           (2, 53), (1, 50), (0, 0)],
}

STATUS_REASONS = {
    frozenset(DOMESTIC): "It's for Canadian citizens, permanent residents and protected persons.",
    frozenset(("citizen", "pr")): "It's for Canadian citizens and permanent residents.",
    frozenset(("citizen",)): "It's for Canadian citizens.",
}


def to_percent(grade: float, scale: str) -> float:
    """An average on any scale as a percentage (the bottom of its letter grade)."""
    table = SCALES[scale]
    if table is None:
        return float(grade)
    for points, percent in table:
        if grade >= points - 1e-9:
            return float(percent)
    return 0.0


# ---------------------------------------------------------------- data

def _read(name: str) -> dict:
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache
def schools() -> dict:
    """Every school by id, universities first, in file order."""
    found = {}
    for school in _read("ontario_schools.yaml")["schools"]:
        for key in ("id", "name", "kind", "domain", "url", "last_checked"):
            if key not in school:
                raise ValueError(f"school {school.get('id', '?')} is missing {key}")
        if school["kind"] not in ("university", "college"):
            raise ValueError(f"school {school['id']} has unknown kind {school['kind']}")
        if school["id"] in found or school["id"] in NO_SCHOOL:
            raise ValueError(f"duplicate school id {school['id']}")
        found[school["id"]] = school
    return found


@lru_cache
def _awards_file() -> dict:
    return _read("student_awards.yaml")


@lru_cache
def awards() -> dict:
    found = {}
    for award in _awards_file()["awards"]:
        for key in ("id", "name", "provider", "group", "summary", "url", "last_checked"):
            if key not in award:
                raise ValueError(f"award {award.get('id', '?')} is missing {key}")
        if award["group"] not in dict(GROUPS):
            raise ValueError(f"award {award['id']} has unknown group {award['group']}")
        if award["group"] != "search" and not all(award.get(key) for key in ("amount", "how", "when")):
            raise ValueError(f"award {award['id']} needs an amount, how and when")
        if award.get("rules", {}).get("looks_for") and not award.get("looks_for_note"):
            raise ValueError(f"award {award['id']} needs a looks_for_note")
        if award["id"] in found:
            raise ValueError(f"duplicate award id {award['id']}")
        found[award["id"]] = award
    return found


def trusted_domains() -> dict:
    return _awards_file()["trusted_domains"]


def on_domain(url: str, domain: str) -> bool:
    host = (urlsplit(url).hostname or "").lower()
    return host == domain or host.endswith("." + domain)


def school_choices() -> list:
    """(group label, [(id, name)]) for the school menu."""
    by_kind = {"university": [], "college": []}
    for school in schools().values():
        by_kind[school["kind"]].append((school["id"], school["name"]))
    return [("Universities", sorted(by_kind["university"], key=lambda c: c[1])),
            ("Colleges", sorted(by_kind["college"], key=lambda c: c[1])),
            ("Something else", [("other", "Another school, or it isn't listed"),
                                ("undecided", "I haven't picked a school yet")])]


# ---------------------------------------------------------------- the student

@dataclass
class Student:
    school: str = "other"
    level: str = "bachelor"
    year: str = "first"
    field: str = "undecided"
    grade: float | None = None          # what they typed, on their scale; None if they don't know
    scale: str = "percent"
    status: str = "citizen"
    need: str = "osap"
    identities: tuple = ()
    activities: tuple = ()

    def __post_init__(self):
        if self.school not in schools() and self.school not in NO_SCHOOL:
            raise ValueError("unknown school")
        for name, allowed in (("level", LEVELS), ("year", YEARS), ("field", FIELDS), ("status", STATUSES),
                              ("need", NEEDS), ("scale", tuple(SCALES))):
            if getattr(self, name) not in allowed:
                raise ValueError(f"{name} must be one of {allowed}")
        self.identities = tuple(sorted(set(self.identities)))
        self.activities = tuple(sorted(set(self.activities)))
        if not set(self.identities) <= set(IDENTITIES) or not set(self.activities) <= set(ACTIVITIES):
            raise ValueError("unknown identity or activity")
        if self.grade is not None:
            if isinstance(self.grade, bool) or not isinstance(self.grade, (int, float)):
                raise ValueError("grade must be a number")
            top = 100 if self.scale == "percent" else SCALES[self.scale][0][0]
            if not 0 <= self.grade <= top:
                raise ValueError("grade out of range")

    @property
    def average(self) -> float | None:
        return None if self.grade is None else to_percent(self.grade, self.scale)

    @property
    def domestic(self) -> bool:
        return self.status in DOMESTIC

    @property
    def stages(self) -> set:
        """The levels an award's rules can name: bachelor_final is a bachelor's student in fourth year or later."""
        found = {self.level}
        if self.level == "bachelor" and self.year == "fourth_plus":
            found.add("bachelor_final")
        return found

    @property
    def school_entry(self) -> dict | None:
        return schools().get(self.school)


AWARD_QUESTIONS = [
    {"id": "school", "title": "Which school do you go to, or plan to go to?", "fields": [
        {"name": "school", "kind": "select", "label": "School", "groups": "schools", "default": "",
         "required": True},
    ]},
    {"id": "program", "title": "What are you studying?", "fields": [
        {"name": "level", "kind": "radio", "label": "Program", "default": "bachelor", "choices": [
            ("college", "College certificate or diploma", "Including graduate certificates and apprenticeships in school"),
            ("bachelor", "Bachelor's degree", "At a university or a college"),
            ("masters", "Master's degree", None),
            ("phd", "PhD", None),
        ]},
        {"name": "field", "kind": "radio", "label": "Subject", "default": "undecided", "choices": [
            ("stem", "Science, technology, engineering or math", None),
            ("health", "Nursing or another health program", None),
            ("business", "Business", None),
            ("arts", "Arts and humanities", "Languages, history, philosophy"),
            ("social", "Social sciences, education or law", None),
            ("trades", "Skilled trades", "Electrician, plumber, welder, mechanic"),
            ("creative", "Art, design or media", None),
            ("undecided", "Not decided, or something else", None),
        ]},
    ]},
    {"id": "year", "title": "What year are you in?", "fields": [
        {"name": "year", "kind": "radio", "default": "first", "choices": [
            ("hs_senior", "I'm applying now, to start next year", "In Grade 12, or going back to school"),
            ("first", "First year", None),
            ("second", "Second year", None),
            ("third", "Third year", None),
            ("fourth_plus", "Fourth year or later", None),
        ]},
    ]},
    {"id": "average", "title": "What's your average?",
     "help": "In Grade 12 or starting first year? Use your top 6 Grade 12 marks. Otherwise, use your average at school. Leave it blank if you don't know.",
     "fields": [
        {"name": "grade", "kind": "number", "label": "Your average"},
        {"name": "scale", "kind": "radio", "label": "Out of", "default": "percent", "choices": [
            ("percent", "Percent (out of 100)", None),
            ("4", "4.0", None),
            ("4.33", "4.33", None),
            ("9", "9", "York"),
            ("10", "10", "uOttawa"),
            ("12", "12", "Carleton, McMaster, Laurier"),
        ]},
    ]},
    {"id": "status", "title": "What's your status in Canada?", "fields": [
        {"name": "status", "kind": "radio", "default": "citizen",
         "choices": [choice for choice in STATUS_CHOICES if choice[0] != "visitor"]},
    ]},
    {"id": "need", "title": "Do you need help paying for school?", "fields": [
        {"name": "need", "kind": "radio", "default": "osap", "choices": [
            ("osap", "Yes, and I get OSAP or I'm applying", None),
            ("tight", "Yes, but I don't have OSAP", None),
            ("no", "No, I can manage", None),
        ]},
    ]},
    {"id": "about", "title": "Do any of these describe you?",
     "help": "Optional. Some awards are only for certain groups. We use this only to build your list, and we don't keep it.",
     "fields": [
        {"name": "first_nations", "kind": "check", "label": "First Nations"},
        {"name": "metis", "kind": "check", "label": "Métis"},
        {"name": "inuit", "kind": "check", "label": "Inuit"},
        {"name": "black", "kind": "check", "label": "Black"},
        {"name": "disability", "kind": "check", "label": "I have a disability",
         "help": "Permanent, or persistent or prolonged"},
        {"name": "first_gen", "kind": "check", "label": "My parents never went to college or university",
         "help": "Anywhere in the world"},
        {"name": "care", "kind": "check", "label": "I'm in, or was in, the care of a Children's Aid Society",
         "help": "Including extended society care (formerly Crown wards)"},
        {"name": "military_family", "kind": "check",
         "label": "My parent or partner serves, or served, in the Canadian Armed Forces"},
    ]},
    {"id": "activities", "title": "What else do you do?", "help": "Pick any that fit, or none.", "fields": [
        {"name": "volunteer", "kind": "check", "label": "I volunteer or help my community, without pay"},
        {"name": "leadership", "kind": "check", "label": "I lead something: a club, team, group or project"},
        {"name": "research", "kind": "check", "label": "I'd like a paid research job with a professor"},
        {"name": "language", "kind": "check", "label": "I'd like to learn French or English in a summer course"},
    ]},
]


def student_from_form(form) -> Student:
    """Turn the submitted questionnaire into a Student. Raises FormError with the field to fix."""
    get = form.get
    school = get("school") or ""
    if school not in schools() and school not in NO_SCHOOL:
        raise FormError("school", "Pick your school, or one of the choices at the end of the list.")
    scale = get("scale") or "percent"
    if scale not in SCALES:
        raise FormError("scale", "Check this answer.")
    grade = None
    if (get("grade") or "").strip():
        top = 100 if scale == "percent" else SCALES[scale][0][0]
        grade = _number(get("grade"), "grade", 0, 1000)
        if grade > top:
            raise FormError("grade", "That's higher than the scale goes. Check the scale you picked.")
    try:
        return Student(
            school=school,
            level=get("level") or "bachelor",
            year=get("year") or "first",
            field=get("field") or "undecided",
            grade=grade,
            scale=scale,
            status=get("status") or "citizen",
            need=get("need") or "osap",
            identities=tuple(name for name in IDENTITIES if get(name)),
            activities=tuple(name for name in ACTIVITIES if get(name)),
        )
    except ValueError:
        raise FormError("school", "Check this answer.") from None


def student_to_json(student: Student) -> str:
    return json.dumps(asdict(student), separators=(",", ":"))


def student_from_json(text: str) -> Student:
    """A Student sent back by the browser: anything tampered with is a ValueError."""
    data = json.loads(text or "{}")
    if not isinstance(data, dict):
        raise ValueError("bad answers")
    known = {f.name for f in fields(Student)}
    try:
        return Student(**{key: value for key, value in data.items() if key in known})
    except (TypeError, AttributeError) as error:
        raise ValueError("bad answers") from error


def student_form_values(student: Student) -> dict:
    """Field values to pre-fill 'Change my answers'."""
    s = student
    values = {"school": s.school, "level": s.level, "year": s.year, "field": s.field,
              "grade": "" if s.grade is None else f"{s.grade:g}", "scale": s.scale, "status": s.status,
              "need": s.need}
    values.update({name: name in s.identities for name in IDENTITIES})
    values.update({name: name in s.activities for name in ACTIVITIES})
    return values


# ---------------------------------------------------------------- matching

@dataclass
class Match:
    award: dict
    status: str
    reasons: list = field(default_factory=list)

    @property
    def id(self):
        return self.award["id"]


def status_reason(allowed) -> Msg:
    text = STATUS_REASONS.get(frozenset(allowed))
    if text:
        return Msg(text)
    if "study_permit" in allowed:
        return Msg("It isn't open to refugee claimants.")
    return Msg("Your status in Canada doesn't fit its rules.")


def allowed_statuses(rule) -> tuple:
    if rule is None:
        return STATUSES
    return DOMESTIC if rule == "domestic" else tuple(rule)


def match(student: Student, award: dict) -> Match | None:
    """Does this award fit? None when it's clearly meant for someone else."""
    rules = award.get("rules", {})
    if rules.get("identities") and not set(rules["identities"]) & set(student.identities):
        return None
    if rules.get("activities") and not set(rules["activities"]) & set(student.activities):
        return None
    if rules.get("levels") and not set(rules["levels"]) & student.stages:
        return None
    if rules.get("years") and student.year not in rules["years"]:
        return None
    if rules.get("fields") and student.field not in rules["fields"]:
        return None
    statuses = allowed_statuses(rules.get("statuses"))
    if award["group"] == "search":
        return Match(award, "fits") if student.status in statuses else None

    if student.status not in statuses:
        return Match(award, "no", [status_reason(statuses)])
    if rules.get("need") and student.need == "no":
        return Match(award, "no", [Msg("It's only for students who need money for school.")])
    checks = []
    minimum = rules.get("min_average")
    if minimum:
        if student.average is None:
            checks.append(Msg("You need an average of at least {needed}.", needed=Percent(minimum)))
        elif student.average < minimum:
            return Match(award, "no", [Msg("It needs an average of at least {needed}. We read yours as about "
                                           "{yours}.", needed=Percent(minimum), yours=Percent(student.average))])
    if rules.get("in_school") and student.year == "hs_senior":
        checks.append(Msg("You can apply once you've started at your school."))
    looks_for = rules.get("looks_for")
    if looks_for and not set(looks_for) & set(student.activities):
        checks.append(EntryText("awards", award, "looks_for_note"))
    if award.get("check"):
        checks.append(EntryText("awards", award, "check"))
    return Match(award, "check" if checks else "fits", checks)


# ---------------------------------------------------------------- entrance scholarships

@dataclass
class Entrance:
    school: dict
    status: str      # amount, qualifies (no published amount), below, unknown_average, no_amount, not_eligible, decided
    tier: dict | None = None
    reasons: list = field(default_factory=list)

    @property
    def rules(self) -> dict:
        return self.school["entrance"]

    @property
    def tiers(self) -> list:
        return self.rules.get("tiers", [])

    @property
    def lowest(self) -> float | None:
        if self.tiers:
            return self.tiers[-1]["min"]
        return self.rules.get("min")


def entrance(school: dict | None, student: Student) -> Entrance | None:
    """The automatic entrance scholarship at this school for this student, if it applies to them."""
    if not school or "entrance" not in school or student.level != "bachelor":
        return None
    if student.year not in ("hs_senior", "first"):
        return None
    result = Entrance(school, "no_amount")
    statuses = allowed_statuses(school["entrance"].get("statuses", "domestic"))
    if student.status not in statuses:
        result.status = "not_eligible"
        result.reasons = [Msg("This one is for Canadian students. International students have their own "
                              "awards; check the school's page.")]
        return result
    if student.year == "first":
        result.status = "decided"
        result.reasons = [Msg("These are decided when you're admitted. If you got one, it's in your offer "
                              "or your student account.")]
        return result
    if not result.tiers:
        minimum = result.lowest
        if minimum and student.average is not None:
            result.status = "below" if student.average < minimum else "qualifies"
        return result
    if student.average is None:
        result.status = "unknown_average"
        return result
    for tier in result.tiers:
        if student.average >= tier["min"]:
            result.status, result.tier = "amount", tier
            return result
    result.status = "below"
    return result


def entrance_table(student: Student) -> list:
    """Every university's automatic entrance scholarship at this student's average, biggest first."""
    if student.year != "hs_senior" or student.level != "bachelor" or student.average is None:
        return []
    rows = []
    for school in schools().values():
        offer = entrance(school, student)
        if offer and offer.status in ("amount", "qualifies"):
            rows.append(offer)
    return sorted(rows, key=lambda o: (o.tier is None, -((o.tier or {}).get("first_year") or 0),
                                       -((o.tier or {}).get("total") or 0), o.school["name"]))


# ---------------------------------------------------------------- the results page

@dataclass
class Step:
    text: Msg
    url: str | None = None


@dataclass
class AwardReport:
    student: Student
    school: dict | None
    entrance: Entrance | None
    table: list
    matches: list
    plan: list

    def group(self, name: str) -> list:
        return [m for m in self.matches if m.award["group"] == name and m.status in ("fits", "check")]

    @property
    def groups(self) -> list:
        return [(title, self.group(name)) for name, title in GROUPS if self.group(name)]

    @property
    def ruled_out(self) -> list:
        return [m for m in self.matches if m.status == "no"]

    @property
    def count(self) -> int:
        return sum(1 for m in self.matches if m.status in ("fits", "check") and m.award["group"] != "search")


STATUS_ORDER = {"fits": 0, "check": 1, "no": 2}

OSAP_URL = "https://www.ontario.ca/page/osap-ontario-student-assistance-program"


def find_awards(student: Student) -> AwardReport:
    matches = [m for m in (match(student, award) for award in awards().values()) if m]
    matches.sort(key=lambda m: STATUS_ORDER[m.status])
    school = student.school_entry
    report = AwardReport(student, school, entrance(school, student), entrance_table(student), matches, [])
    report.plan = build_plan(report)
    return report


def build_plan(report: AwardReport) -> list:
    s = report.student
    steps = []
    if s.domestic and s.need != "no":
        if s.year == "hs_senior":
            steps.append(Step(Msg("Apply for OSAP as soon as it opens for next year. Many bursaries, including "
                                  "your school's, use it to see what you need."), OSAP_URL))
        else:
            steps.append(Step(Msg("Apply for OSAP every year, even if you're not sure you'll get much. Many "
                                  "bursaries, including your school's, use it to see what you need."), OSAP_URL))
    if report.school:
        if s.year == "hs_senior":
            steps.append(Step(Msg("Look at {school}'s awards page now. Some entrance awards need their own "
                                  "application, often with an early deadline.", school=Msg(report.school["name"])),
                              report.school["url"]))
        else:
            steps.append(Step(Msg("Fill in {school}'s awards application. One form usually puts you in the "
                                  "running for many scholarships and bursaries.", school=Msg(report.school["name"])),
                              report.school["url"]))
    elif s.school == "other":
        steps.append(Step(Msg("Ask your school's financial aid office for its awards application. One form usually "
                              "puts you in the running for many scholarships and bursaries.")))
    if any(m.status in ("fits", "check") and m.award["group"] != "search" for m in report.matches):
        steps.append(Step(Msg("Apply for the awards below that fit you, and put their deadlines in your calendar.")))
    if not s.domestic:
        steps.append(Step(Msg("Ask your school's international student office about awards for students on a "
                              "permit. Many government awards are only for citizens and permanent residents.")))
    return steps
