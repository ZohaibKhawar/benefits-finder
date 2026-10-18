"""Runs every rule for a person and builds the results page: groups, a total and a step-by-step plan."""

from dataclasses import dataclass, field
from datetime import date

from .answers import Answers
from .data import load
from .i18n import BenefitName, Msg
from .rules import PAID_WITH_CCB, RULES, Result

GROUPS = (
    ("money", "Money you might get"),
    ("study", "For your studies"),
    ("health", "Health and dental"),
    ("support", "If money is tight"),
    ("help", "Free help"),
)
STATUS_ORDER = {"likely": 0, "maybe": 1, "not_yet": 2, "no": 3}


@dataclass
class Item:
    """One benefit for one person: the data-file entry plus what the rule decided."""
    benefit: dict
    result: Result

    def __getattr__(self, name):
        # Lets templates write item.name, item.url, item.status ... without caring where it lives.
        result = self.__dict__["result"]
        if hasattr(result, name):
            return getattr(result, name)
        return self.__dict__["benefit"].get(name)

    @property
    def next_step(self):
        """This person's own next step if the rule gave one, otherwise the general one (None)."""
        return self.result.next_step


@dataclass
class Step:
    text: Msg
    url: str | None = None


@dataclass
class Report:
    items: list[Item]
    plan: list[Step]
    tax_deadline: date
    province: str = "ON"
    by_id: dict = field(init=False)

    def __post_init__(self):
        self.by_id = {item.id: item for item in self.items}

    def get(self, benefit_id: str) -> Item | None:
        return self.by_id.get(benefit_id)

    @property
    def total(self) -> int:
        """Money a year from the benefits we're fairly sure about and could put a number on."""
        return sum(item.estimate or 0 for item in self.counted)

    @property
    def counted(self) -> list[Item]:
        return [item for item in self.items
                if item.status == "likely" and item.counts_in_total and item.estimate]

    def group(self, category: str) -> list[Item]:
        return [item for item in self.items if item.category == category and item.status in ("likely", "maybe")]

    @property
    def groups(self) -> list[tuple[str, list[Item]]]:
        return [(title, self.group(category)) for category, title in GROUPS if self.group(category)]

    @property
    def not_yet(self) -> list[Item]:
        return [item for item in self.items if item.status == "not_yet"]

    @property
    def ruled_out(self) -> list[Item]:
        return [item for item in self.items if item.status == "no"]


def next_tax_deadline(today: date) -> date:
    deadline = date(today.year, 4, 30)
    return deadline if today <= deadline else date(today.year + 1, 4, 30)


def find(answers: Answers, today: date | None = None) -> Report:
    today = today or date.today()
    benefits, links = load(answers.province)
    items = []
    for benefit_id, benefit in benefits.items():
        rule = RULES.get(benefit.get("rule", benefit_id))
        if rule is None:
            raise LookupError(f"No rule written for {benefit_id}")
        result = rule(answers, benefit.get("params", {}), today)
        if result is not None:
            items.append(Item(benefit, result))
    items.sort(key=lambda item: (STATUS_ORDER[item.status], -(item.estimate or item.up_to or 0)))
    report = Report(items, [], next_tax_deadline(today), answers.province)
    report.plan = build_plan(answers, report, links, today)
    return report


def build_plan(a: Answers, report: Report, links: dict, today: date) -> list[Step]:
    """The few things to do, in the order that unlocks the most."""
    def has(benefit_id, *statuses):
        item = report.get(benefit_id)
        return item is not None and item.status in (statuses or ("likely",))

    steps = []
    local = links.get("plan", {})
    months = a.months_in_canada(today)
    if months is not None and months < 12:
        steps.append(Step(Msg("Get a Social Insurance Number (SIN) from Service Canada if you don't have one. "
                              "You need it for every benefit."), links.get("sin")))
    health = local.get("health_card_id")
    if health and has(health):
        steps.append(Step(Msg("Apply for {name}. Bring your immigration papers and proof of address.",
                              name=BenefitName(health)), report.get(health).url))
    if a.is_newcomer(today) and not a.filed_taxes and a.tax_resident:
        if has("ccb"):
            steps.append(Step(Msg("Apply for the Canada Child Benefit with form RC66. The same form signs you up "
                                  "for the grocery benefit and the provincial child benefit."), links.get("rc66")))
        else:
            steps.append(Step(Msg("Apply for the Canada Groceries and Essentials Benefit with the RC151 web form. "
                                  "You don't have to wait for your first tax return."), links.get("rc151")))

    tax_year = report.tax_deadline.year - 1
    parts = [Msg("File your {year} tax return by April 30, {deadline}, even if you had no income. Most of these "
                 "benefits only start after you file.", year=str(tax_year), deadline=str(report.tax_deadline.year))]
    rent_form = local.get("rent_form_benefit")
    if rent_form and has(rent_form, "likely", "maybe"):
        parts.append(Msg(local.get("rent_form_text", "")))
    if local.get("tax_text"):
        parts.append(Msg(local["tax_text"]))
    if has("tax_clinic"):
        parts.append(Msg("A free tax clinic can do it for you."))
    if not a.filed_taxes and not a.is_newcomer(today):
        parts.append(Msg("Missed a year? You can still file late, and benefits for past years are often paid back."))
    steps.append(Step(Msg(" ".join("{p%d}" % i for i in range(len(parts))),
                          **{f"p{i}": part for i, part in enumerate(parts)}), links.get("file_taxes")))

    aid = local.get("student_aid_id")
    if aid and has(aid):
        steps.append(Step(Msg("Apply for {name}.", name=BenefitName(aid)), report.get(aid).url))
    if has("cdcp"):
        steps.append(Step(Msg("Apply for the Canadian Dental Care Plan."), report.get("cdcp").url))
    elif has("cdcp", "not_yet"):
        steps.append(Step(Msg("After you file, apply for the Canadian Dental Care Plan."), report.get("cdcp").url))
    if has("dtc", "maybe"):
        steps.append(Step(Msg("Ask your doctor about the Disability Tax Credit (form T2201). It unlocks other help."),
                          report.get("dtc").url))
    for item in report.not_yet:
        if (item.available_from and item.id != "cdcp" and item.id not in PAID_WITH_CCB
                and item.benefit.get("rule") != "provincial_child_benefit"):
            steps.append(Step(Msg("Mark your calendar: {name}, {when}.", name=BenefitName(item.id),
                                  when=item.available_from), item.url))
    return steps
