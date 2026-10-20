"""Who qualifies for what. One function per benefit id in the data files.

Each rule returns a Result, or None when the benefit has nothing to do with this person
(the Canada Child Benefit for someone with no children, for example).

Statuses:
  likely   - meets every rule we can check
  maybe    - could qualify, depends on something we didn't ask (or can't know)
  not_yet  - will qualify later (after a birthday, a tax return, month 19 in Canada...)
  no       - a clear rule rules them out; the reason is shown so nobody wonders why

Every sentence is a Msg so it can be shown in English or French.
"""

from dataclasses import dataclass, field
from datetime import date

from . import estimates as est
from .answers import Answers, add_months
from .i18n import Money, Month, Msg


@dataclass
class Result:
    status: str
    reasons: list[Msg] = field(default_factory=list)
    estimate: int | None = None          # dollars a year, when we can work it out
    up_to: int | None = None             # "up to $X a year" when we can't
    counts_in_total: bool = True         # False for tax cuts, loans, coverage, savings
    available_from: Msg | None = None    # when a not_yet result opens up
    next_step: Msg | None = None         # replaces the general "how to get it" for this person


RULES = {}

# Provincial child benefits that arrive with the Canada Child Benefit (no separate calendar step).
PAID_WITH_CCB = {"ocb"}


def rule(*benefit_ids):
    def register(fn):
        for benefit_id in benefit_ids:
            RULES[benefit_id] = fn
        return fn
    return register


def plural_children(count: int) -> Msg:
    return Msg("1 child") if count == 1 else Msg("{count} children", count=count)


# ---------------------------------------------------------------- federal: money

@rule("cgeb")
def cgeb(a: Answers, p: dict, today: date):
    if not a.tax_resident:
        return Result("no", [Msg("You need to be a resident of Canada for tax purposes. Visitors usually aren't.")])
    amount = est.cgeb(p, has_partner=a.has_partner, kids=a.kids, income=a.income)
    if a.age < 19 and not a.family:
        return Result("not_yet", [Msg("Payments start after your 19th birthday. File a tax return now so they "
                                      "start on time.")],
                      estimate=amount, available_from=Msg("after you turn 19"))
    if amount == 0:
        return Result("no", [Msg("Your family income is above the limit for your family size.")])
    if a.income > 0:
        reason = Msg("Worked out from a family income of about {income}.", income=Money(a.income))
    else:
        reason = Msg("Even with no income you get the base amount, as long as you file a tax return.")
    result = Result("likely", [reason], estimate=amount)
    if a.is_newcomer(today) and not a.filed_taxes:
        if a.kids:
            result.next_step = Msg("Apply now with form RC66 (it covers your children too). You don't have to "
                                   "wait for your first tax return.")
        else:
            result.next_step = Msg("Apply now with the RC151 web form. You don't have to wait for your first "
                                   "tax return.")
    return result


@rule("cwb")
def cwb(a: Answers, p: dict, today: date):
    if a.work_income <= 0:
        return None
    if not a.tax_resident:
        return Result("no", [Msg("You need to be a resident of Canada for tax purposes all year.")])
    if a.student == "full_time" and not a.kids:
        return Result("no", [Msg("Full-time students who studied more than {weeks} weeks in the year can't get "
                                 "it, unless they have a child living with them.", weeks=p["student_weeks_limit"])])
    if a.age < 19 and not a.family:
        return Result("no", [Msg("You need to be 19 or older on December 31, or live with a partner or child.")])
    amount = est.cwb(p, family=a.family, work_income=a.work_income, income=a.income)
    if amount == 0:
        if a.work_income <= p["min_work_income"]:
            return Result("no", [Msg("You need more than {amount} of income from work.",
                                     amount=Money(p["min_work_income"]))])
        return Result("no", [Msg("Your income is above the limit.")])
    reasons = [Msg("Worked out from about {amount} of work income.", amount=Money(a.work_income))]
    if a.has_dtc:
        reasons.append(Msg("With the Disability Tax Credit you may also get up to {amount} more.",
                           amount=Money(p["disability_max"])))
    up_to = None
    if a.province in ("AB", "QC", "NU"):
        # Alberta, Quebec and Nunavut set their own amounts, so show the usual maximum instead of an estimate.
        reasons = [Msg("Amounts are different in Alberta, Quebec and Nunavut, so we can't estimate it here.")]
        up_to, amount = p["family_max" if a.family else "single_max"], None
    months = a.months_in_canada(today)
    if months is not None and months < 12:
        reasons.append(Msg("You must be a resident for the whole year, so your first full year in Canada counts."))
        return Result("maybe", reasons, estimate=amount, up_to=up_to)
    return Result("likely", reasons, estimate=amount, up_to=up_to)


def child_benefit_gate(a: Answers, today: date):
    """Shared rules for the Canada Child Benefit and the provincial child benefits paid with it.

    Returns None when the family can get it now, or a (status, reasons, available_from) tuple.
    """
    if a.status == "visitor":
        return "no", [Msg("Visitors can't get it.")], None
    if a.status == "refugee_claimant":
        return "no", [Msg("Refugee claimants can't get it until the claim is accepted. Apply as soon as you "
                          "become a protected person.")], None
    months = a.months_in_canada(today)
    if a.temporary and months is not None and months < 18:
        opens = add_months(a.arrived, 18)
        return ("not_yet",
                [Msg("People on a study or work permit can get it from their 19th month in Canada, with a valid "
                     "permit that month. Apply then with form RC66.")],
                Month(opens.year, opens.month, 1))
    return None


@rule("ccb")
def ccb(a: Answers, p: dict, today: date):
    if not a.kids:
        return None
    amount = est.ccb(p, under_6=a.kids_under_6, age_6_to_17=a.kids_6_to_17, income=a.income)
    gate = child_benefit_gate(a, today)
    if gate:
        status, reasons, opens = gate
        return Result(status, reasons, estimate=amount if status == "not_yet" else None,
                      available_from=Msg("{month}", month=opens) if opens else None)
    if amount == 0:
        return Result("no", [Msg("Your family income is above the limit for your number of children.")])
    result = Result("likely", [Msg("For {children}, with a family income of about {income}.",
                                   children=plural_children(a.kids), income=Money(a.income))], estimate=amount)
    if a.is_newcomer(today):
        result.next_step = Msg("Apply with form RC66 (and RC66SCH). It also signs you up for the provincial "
                               "child benefit.")
    return result


@rule("cdcp")
def cdcp(a: Answers, p: dict, today: date):
    if a.status == "refugee_claimant":
        return None              # the Interim Federal Health Program covers their dental care
    if not a.tax_resident:
        return Result("no", [Msg("You need to be a resident of Canada for tax purposes.")], counts_in_total=False)
    if a.has_dental_plan:
        return Result("no", [Msg("You have dental coverage through school, work or family, and that rules it out. "
                                 "Opting out of a plan doesn't make you eligible.")], counts_in_total=False)
    if a.income >= p["income_limit"]:
        return Result("no", [Msg("Family income must be under {amount}.", amount=Money(p["income_limit"]))],
                      counts_in_total=False)
    if not a.filed_taxes:
        return Result("not_yet", [Msg("You can apply after you file your first Canadian tax return.")],
                      counts_in_total=False, available_from=Msg("after you file your tax return"))
    if a.income < p["free_under"]:
        reason = Msg("No dental plan and income under {amount}: care is free.", amount=Money(p["free_under"]))
    else:
        reason = Msg("No dental plan and income under {amount}: care is covered with a co-pay (you pay 40% or 60%).",
                     amount=Money(p["income_limit"]))
    return Result("likely", [reason], counts_in_total=False)


@rule("dtc")
def dtc(a: Answers, p: dict, today: date):
    if not a.disability or a.has_dtc:
        return None
    return Result("maybe", [Msg("If your condition seriously limits everyday activities (walking, seeing, thinking, "
                                "and others) and will last a year or more, you may qualify. It unlocks other "
                                "benefits.")], counts_in_total=False)


@rule("cdb")
def cdb(a: Answers, p: dict, today: date):
    if not a.disability:
        return None
    if not 18 <= a.age <= 64:
        return Result("no", [Msg("It's for people aged 18 to 64.")], counts_in_total=False)
    if not a.has_dtc:
        return Result("not_yet", [Msg("You need the Disability Tax Credit first.")], up_to=p["max_per_year"],
                      counts_in_total=False, available_from=Msg("after the Disability Tax Credit is approved"))
    return Result("likely", [Msg("You have the Disability Tax Credit. The amount goes down as income goes up.")],
                  up_to=p["max_per_year"], counts_in_total=False)


@rule("ifhp")
def ifhp(a: Answers, p: dict, today: date):
    if a.status == "refugee_claimant":
        return Result("likely", [Msg("Refugee claimants are covered automatically.")], counts_in_total=False)
    months = a.months_in_canada(today)
    if a.status == "protected" and months is not None and months < 6:
        return Result("maybe", [Msg("It covers you until your provincial health coverage starts.")],
                      counts_in_total=False)
    return None


@rule("northern_residents")
def northern_residents(a: Answers, p: dict, today: date):
    if a.province not in ("YT", "NT", "NU"):
        return None
    months = a.months_in_canada(today)
    if months is not None and months < p["months_needed"]:
        opens = add_months(a.arrived, p["months_needed"])
        return Result("not_yet", [Msg("You need to have lived in the North for 6 months in a row.")],
                      counts_in_total=False, available_from=Msg("{month}", month=Month(opens.year, opens.month, 1)))
    return Result("likely", [Msg("Everyone living in the territories can claim it. It lowers the tax you owe.")],
                  counts_in_total=False)


# ---------------------------------------------------------------- federal: studies

def student_aid_status_reason(a: Answers) -> Msg:
    if a.status == "study_permit":
        return Msg("International students can't get government student aid or Canada Student Grants.")
    return Msg("Only Canadian citizens, permanent residents and protected persons can get it.")


@rule("student_grant")
def student_grant(a: Answers, p: dict, today: date):
    if not a.post_secondary:
        return None
    if not a.can_get_osap:
        return Result("no", [student_aid_status_reason(a)], counts_in_total=False)
    most = p["full_time_max"] if a.student == "full_time" else p["part_time_max"]
    reasons = [Msg("It depends on your income (or your parents' income if you're a dependent student) and your "
                   "costs.")]
    if a.disability:
        most += p["disability"]
        reasons.append(Msg("Students with a disability can get {amount} more.", amount=Money(p["disability"])))
    if a.kids and a.student == "full_time":
        most += a.kids * p["per_dependant_per_month"] * 8
        reasons.append(Msg("Plus up to {amount} a month for each child.", amount=Money(p["per_dependant_per_month"])))
    if a.school_type == "career_college" and a.student == "full_time":
        reasons.insert(0, Msg("Since August 1, 2026 most students at for-profit career colleges can't get the "
                              "full-time grant (some exceptions apply)."))
    if a.province == "QC":
        reasons.insert(0, Msg("Quebec runs its own student aid (AFE), so the federal grant isn't paid there."))
        return Result("no", reasons[:1], counts_in_total=False)
    if a.province in ("NT", "NU"):
        return Result("no", [Msg("The Northwest Territories and Nunavut run their own student aid, so the federal "
                                 "grant isn't paid there.")], counts_in_total=False)
    return Result("maybe", reasons, up_to=most, counts_in_total=False)


@rule("tuition_credit")
def tuition_credit(a: Answers, p: dict, today: date):
    if not a.post_secondary:
        return None
    if a.income < 16000:
        reason = Msg("You probably owe no tax yet, so the credit is saved for later years, or up to $5,000 can go "
                     "to a parent or grandparent.")
    else:
        reason = Msg("It lowers the tax you owe this year.")
    return Result("likely", [reason], counts_in_total=False)


@rule("training_credit")
def training_credit(a: Answers, p: dict, today: date):
    if not a.post_secondary or not 25 <= a.age <= 64 or a.work_income < p["min_work_income"]:
        return None
    return Result("likely", [Msg("You're 25 to 64, you work, and you pay tuition.")], counts_in_total=False)


@rule("rap")
def rap(a: Answers, p: dict, today: date):
    if not a.repaying_student_loans:
        return None
    limit = p["zero_payment_monthly_single"] * 12
    if a.income < limit and not a.family:
        return Result("likely", [Msg("Single people earning under about {amount} a year can pay $0.",
                                     amount=Money(limit))], counts_in_total=False)
    return Result("maybe", [Msg("The $0 payment limit depends on your income and family size.")],
                  counts_in_total=False)


@rule("clb")
def clb(a: Answers, p: dict, today: date):
    reasons = []
    up_to = 0
    status = None
    if 18 <= a.age <= 20 and a.status in ("citizen", "pr", "protected"):
        reasons.append(Msg("If your family had a low income while you were growing up, money may be waiting for "
                           "you. You can claim it yourself until you turn 21."))
        up_to += p["max"]
        status = "maybe"
    if a.kids and a.income <= p["family_income_limit"]:
        reasons.append(Msg("Your children may get {first} now and $100 a year after, up to {most} each.",
                           first=Money(p["first_year"]), most=Money(p["max"])))
        up_to += a.kids * p["max"]
        status = "likely"
    if not status:
        return None
    return Result(status, reasons, up_to=up_to, counts_in_total=False)


# ---------------------------------------------------------------- federal: help

@rule("settlement")
def settlement(a: Answers, p: dict, today: date):
    months = a.months_in_canada(today)
    if a.status in ("protected", "refugee_claimant"):
        return Result("likely", [Msg("Refugees and protected persons can use them.")], counts_in_total=False)
    if a.status == "pr":
        if months is None or months <= 72:
            return Result("likely", [Msg("Permanent residents can use them (economic-class: for 6 years).")],
                          counts_in_total=False)
        return Result("maybe", [Msg("Economic-class permanent residents can use them for 6 years after landing.")],
                      counts_in_total=False)
    if a.temporary:
        return Result("maybe", [Msg("Federal services are mostly for permanent residents, but some provinces fund "
                                    "agencies that help people on study and work permits.")], counts_in_total=False)
    if a.status == "citizen" and months is not None and months <= 72:
        return Result("maybe", [Msg("New citizens can use provincially funded settlement agencies.")],
                      counts_in_total=False)
    return None


@rule("tax_clinic")
def tax_clinic(a: Answers, p: dict, today: date):
    people = 1 + a.has_partner + a.kids
    limit = p["single_limit"] if people == 1 else p["couple_limit"] + p["per_extra_person"] * (people - 2)
    if a.income > limit:
        return None
    return Result("likely", [Msg("Your income is under about {amount} for a household of {people}.",
                                 amount=Money(limit), people=people)], counts_in_total=False)


# ---------------------------------------------------------------- Ontario: money

def age_ok(a: Answers, age: int) -> bool:
    return a.age >= age or a.family


@rule("oeptc")
def oeptc(a: Answers, p: dict, today: date):
    if not age_ok(a, 18):
        return Result("not_yet", [Msg("You need to be 18 or older (or have a partner or child).")],
                      available_from=Msg("after you turn 18"))
    if a.housing in ("family_no_rent", "other"):
        return Result("no", [Msg("You need to pay rent or property tax, or live in a student residence.")])
    most = p["max_65_plus"] if a.age >= 65 else p["max_under_65"]
    if a.housing == "own" or a.age >= 65 or (a.housing == "rent" and a.monthly_rent <= 0):
        return Result("likely", [Msg("The amount depends on the rent or property tax you paid.")], up_to=most)
    amount = est.oeptc(p, annual_rent=a.monthly_rent * 12, residence=a.housing == "residence",
                       income=a.income, family=a.family)
    if amount == 0:
        return Result("no", [Msg("Your income is above the limit for the rent you pay.")])
    if a.housing == "residence":
        reason = Msg("A student residence counts for only $25. Renting off campus counts for much more.")
    else:
        reason = Msg("Worked out from {rent} a month in rent (20% of rent counts).", rent=Money(a.monthly_rent))
    return Result("likely", [reason], estimate=amount)


@rule("noec")
def noec(a: Answers, p: dict, today: date):
    if not a.northern_ontario:
        return None
    if a.housing not in ("rent", "own"):
        return Result("no", [Msg("You need to pay rent or property tax in Northern Ontario.")])
    if not age_ok(a, 18):
        return Result("not_yet", [Msg("You need to be 18 or older.")], available_from=Msg("after you turn 18"))
    amount = est.noec(p, family=a.family, income=a.income)
    if amount == 0:
        return Result("no", [Msg("Your income is above the limit.")])
    return Result("likely", [Msg("You live in Northern Ontario and pay rent or property tax.")], estimate=amount)


@rule("ostc")
def ostc(a: Answers, p: dict, today: date):
    if not a.tax_resident:
        return Result("no", [Msg("You need to be a resident for tax purposes.")])
    amount = est.ostc(p, has_partner=a.has_partner, kids=a.kids, income=a.income)
    if not age_ok(a, 19):
        return Result("not_yet", [Msg("You need to be 19 or older (or have a partner or child).")],
                      estimate=amount, available_from=Msg("after you turn 19"))
    if amount == 0:
        return Result("no", [Msg("Your family income is above the limit.")])
    return Result("likely", [Msg("Worked out from a family income of about {income}.", income=Money(a.income))],
                  estimate=amount)


def paid_with_ccb(a: Answers, amount: int, today: date):
    """Provincial child benefits ride on the Canada Child Benefit application."""
    gate = child_benefit_gate(a, today)
    if gate:
        status, reasons, opens = gate
        return Result(status, reasons, estimate=amount if status == "not_yet" else None,
                      available_from=Msg("{month}", month=opens) if opens else None)
    if amount == 0:
        return Result("no", [Msg("Your family income is above the limit.")])
    return Result("likely", [Msg("Paid with the Canada Child Benefit.")], estimate=amount)


@rule("ocb")
def ocb(a: Answers, p: dict, today: date):
    if not a.kids:
        return None
    return paid_with_ccb(a, est.ocb(p, kids=a.kids, income=a.income), today)


@rule("liwtc")
def liwtc(a: Answers, p: dict, today: date):
    if a.work_income <= 0:
        return None
    amount = est.liwtc(p, has_partner=a.has_partner, work_income=a.work_income, income=a.income)
    if amount == 0:
        return Result("no", [Msg("Your income is above the limit.")], counts_in_total=False)
    if a.income < p["no_ontario_tax_below"]:
        return Result("no", [Msg("At your income you probably owe no provincial tax, so this wouldn't add "
                                 "anything.")], counts_in_total=False)
    if a.has_partner:
        # Each working partner claims their own, and the limit depends on how the income is split.
        return Result("maybe", [Msg("Each working partner can cut their provincial tax by up to {amount}, "
                                    "depending on how your income is split.", amount=Money(p["max"]))],
                      up_to=p["max"], counts_in_total=False)
    return Result("likely", [Msg("Cuts your provincial tax by up to {amount}. Tax software claims it for you.",
                                 amount=Money(amount))], up_to=amount, counts_in_total=False)


@rule("care_credit")
def care_credit(a: Answers, p: dict, today: date):
    if not a.kids:
        return None
    if a.income > p["income_limit"]:
        return Result("no", [Msg("Family income must be under about {amount}.", amount=Money(p["income_limit"]))],
                      counts_in_total=False)
    return Result("maybe", [Msg("Only if you pay for child care. Keep every receipt.")], counts_in_total=False)


# ---------------------------------------------------------------- Ontario: studies

@rule("osap")
def osap(a: Answers, p: dict, today: date):
    if not a.post_secondary:
        return None
    if not a.can_get_osap:
        return Result("no", [student_aid_status_reason(a)], counts_in_total=False)
    reasons = [Msg("Since August 1, 2026 most of Ontario's part is a loan; the federal grant is still free money.")]
    if a.school_type == "career_college":
        reasons = [Msg("At a career college, everything Ontario gives is a loan.")]
    return Result("likely", reasons, counts_in_total=False)


@rule("learn_and_stay")
def learn_and_stay(a: Answers, p: dict, today: date):
    if not (a.post_secondary and a.health_program):
        return None
    if not a.can_get_osap:
        return Result("no", [student_aid_status_reason(a)], counts_in_total=False)
    return Result("maybe", [Msg("Only for some schools in Northern, Eastern and Southwestern Ontario.")],
                  counts_in_total=False)


@rule("obpap")
def obpap(a: Answers, p: dict, today: date):
    if not a.bridge_program:
        return None
    if a.status in ("citizen", "pr", "protected"):
        return Result("likely", [Msg("You're in a bridge training program.")], up_to=5000, counts_in_total=False)
    if a.status in ("work_permit", "refugee_claimant"):
        return Result("maybe", [Msg("Some refugee claimants and work permit holders approved for permanent "
                                    "residence qualify.")], up_to=5000, counts_in_total=False)
    return Result("no", [Msg("It's for permanent residents, citizens and some others; not study permit holders.")],
                  counts_in_total=False)


@rule("better_jobs")
def better_jobs(a: Answers, p: dict, today: date):
    if not a.out_of_work:
        return None
    if not a.can_get_osap:
        return Result("no", [Msg("It's for citizens, permanent residents and protected persons.")],
                      counts_in_total=False)
    return Result("maybe", [Msg("You were laid off or have been out of work for a while.")], up_to=28000,
                  counts_in_total=False)


@rule("aid_office")
def aid_office(a: Answers, p: dict, today: date):
    if not a.post_secondary:
        return None
    return Result("likely", [Msg("Every school has its own bursaries and emergency money.")], counts_in_total=False)


# ---------------------------------------------------------------- Ontario: health

@rule("ohip")
def ohip(a: Answers, p: dict, today: date):
    if a.status in ("citizen", "pr", "protected"):
        if a.arrived is None:
            return None          # born here or here for years: they already have it
        return Result("likely", [Msg("There is no waiting period. Apply as soon as you arrive.")],
                      counts_in_total=False)
    if a.status == "work_permit":
        return Result("maybe", [Msg("Only if you work full-time for an Ontario employer for at least 6 months. "
                                    "Your partner and children may be covered too.")], counts_in_total=False)
    if a.status == "study_permit":
        return Result("no", [Msg("International students aren't covered. Use UHIP or your college's health plan. "
                                 "With a work permit and 6 months of full-time work you may qualify later.")],
                      counts_in_total=False)
    if a.status == "refugee_claimant":
        return Result("no", [Msg("You're covered by the Interim Federal Health Program until your claim is "
                                 "accepted.")], counts_in_total=False)
    return Result("no", [Msg("Visitors aren't covered. Buy travel health insurance.")], counts_in_total=False)


@rule("ohip_plus")
def ohip_plus(a: Answers, p: dict, today: date):
    if a.age > 24 or a.status not in ("citizen", "pr", "protected", "work_permit"):
        return None
    if a.has_drug_plan:
        return Result("no", [Msg("You have a drug plan through school, work or family, and that plan pays first.")],
                      counts_in_total=False)
    status = "maybe" if a.status == "work_permit" else "likely"
    return Result(status, [Msg("You're 24 or under with no private drug plan.")], counts_in_total=False)


@rule("healthy_smiles")
def healthy_smiles(a: Answers, p: dict, today: date):
    if not a.kids:
        return None
    if a.on_ow_or_odsp:
        return Result("likely", [Msg("Children on Ontario Works or ODSP are signed up automatically.")],
                      counts_in_total=False)
    limit = p["one_child"] + p["per_extra_child"] * (min(a.kids, p["max_children_counted"]) - 1)
    if a.income > limit:
        return Result("no", [Msg("Family net income must be {amount} or less for {children}.",
                                 amount=Money(limit), children=plural_children(a.kids))], counts_in_total=False)
    return Result("likely", [Msg("Your family income is under {amount}.", amount=Money(limit))],
                  counts_in_total=False)


# ---------------------------------------------------------------- Ontario: when money is tight

@rule("ontario_works", "income_assistance")
def ontario_works(a: Answers, p: dict, today: date):
    if a.on_ow_or_odsp or a.status in ("study_permit", "visitor", "work_permit") or a.student == "full_time":
        return None
    if a.income >= 15000:
        return None
    return Result("maybe", [Msg("If you can't cover food and rent right now.")], counts_in_total=False)


@rule("odsp")
def odsp(a: Answers, p: dict, today: date):
    if not a.disability or a.on_ow_or_odsp or a.status in ("study_permit", "visitor"):
        return None
    if a.income >= 25000:
        return None
    return Result("maybe", [Msg("You have a disability and a low income.")], counts_in_total=False)


@rule("oesp")
def oesp(a: Answers, p: dict, today: date):
    if not a.hydro_in_name or a.income >= 60000:
        return None
    return Result("maybe", [Msg("The hydro bill is in your name; the limit depends on how many people live with "
                                "you.")], counts_in_total=False)


@rule("cohb")
def cohb(a: Answers, p: dict, today: date):
    if a.housing != "rent" or a.income >= 40000 or a.status == "visitor":
        return None
    return Result("maybe", [Msg("You rent and have a lower income. Wait lists are long, so join early.")],
                  counts_in_total=False)


@rule("help_211")
def help_211(a: Answers, p: dict, today: date):
    return Result("likely", [Msg("Anyone in Canada can use it.")], counts_in_total=False)


# ---------------------------------------------------------------- city programs

CITY_NAMES = {"toronto": "Toronto", "ottawa": "Ottawa", "peel": "Peel Region", "hamilton": "Hamilton",
              "waterloo": "Waterloo Region", "london": "London"}


@rule("city_program")
def city_program(a: Answers, p: dict, today: date):
    """Shared by every city discount: right city, right age, and income under the city's screen."""
    if a.city != p["city"] or a.status == "visitor":
        return None
    if a.age < p.get("min_age", 0) or a.age > p.get("max_age", 120):
        return None
    people = 1 + a.has_partner + a.kids
    limit = p["one_person_limit"] * people ** 0.5
    if a.income > limit:
        return None
    return Result("maybe", [Msg("For lower-income residents. The limit for one person is about {amount} a year, "
                                "and higher for bigger households.", amount=Money(p["one_person_limit"]))],
                  counts_in_total=False)


# ---------------------------------------------------------------- other provinces (shared rules)
# Each province file points its benefits at one of these with `rule:`, and picks a formula
# from estimates.FORMULAS with `formula:` in its params.

def formula_estimate(a: Answers, p: dict, income: float | None = None):
    income = a.income if income is None else income
    name = p["formula"]
    fn = est.FORMULAS[name]
    if name == "bc_family_benefit":
        return fn(p, kids=a.kids, income=income, single_parent=a.kids > 0 and not a.has_partner)
    if name == "alberta_child_family":
        return fn(p, kids=a.kids, income=income, work_income=a.work_income)
    if name == "nwt_child":
        return fn(p, under_6=a.kids_under_6, age_6_to_17=a.kids_6_to_17, income=income)
    if name in ("flat_per_child", "pei_child"):
        return fn(p, kids=a.kids, income=income)
    if name == "adults_and_children":
        return fn(p, has_partner=a.has_partner, kids=a.kids, income=income)
    if name == "pei_essentials":
        return fn(p, family=a.family, income=income)
    if name == "renters_credit":
        return fn(p, income=income)
    if name == "quebec_solidarity":
        return fn(p, has_partner=a.has_partner, kids=a.kids, income=income, has_home=a.housing in ("rent", "own"))
    raise LookupError(name)


@rule("provincial_child_benefit")
def provincial_child_benefit(a: Answers, p: dict, today: date):
    if not a.kids:
        return None
    if "formula" in p:
        amount = formula_estimate(a, p)
        most = formula_estimate(a, p, income=0)
    else:
        amount = None
        most = a.kids * p["up_to_per_child"] + (p.get("single_parent", 0) if not a.has_partner else 0)
    if amount is not None:
        return paid_with_ccb(a, amount, today)
    gate = child_benefit_gate(a, today)
    if gate:
        status, reasons, opens = gate
        return Result(status, reasons, up_to=most, counts_in_total=False,
                      available_from=Msg("{month}", month=opens) if opens else None)
    return Result("likely" if "formula" not in p else "maybe",
                  [Msg(p.get("note", "The exact amount depends on your family income."))],
                  up_to=most, counts_in_total=False)


@rule("provincial_credit")
def provincial_credit(a: Answers, p: dict, today: date):
    if p.get("needs_work") and a.work_income <= 0:
        return None
    if not a.tax_resident or (p.get("no_refugee_claimants") and a.status == "refugee_claimant"):
        return Result("no", [Msg("You need to be a resident for tax purposes.")])
    min_age = p.get("min_age", 19)
    if a.age < min_age and not a.family:
        return Result("not_yet", [Msg("You need to be {age} or older (or have a partner or child).", age=min_age)],
                      available_from=Msg("after you turn {age}", age=min_age))
    months = a.months_in_canada(today)
    if p.get("temporary_months") and a.temporary and months is not None and months < p["temporary_months"]:
        opens = add_months(a.arrived, p["temporary_months"])
        return Result("not_yet", [Msg("People on a study or work permit qualify after {months} months in Canada.",
                                      months=p["temporary_months"])],
                      available_from=Msg("{month}", month=Month(opens.year, opens.month, 1)))
    if "formula" not in p:
        return Result("maybe", [Msg(p.get("note", "The exact amount depends on your income."))],
                      up_to=p.get("up_to"), counts_in_total=False)
    amount = formula_estimate(a, p)
    if amount is None:
        return Result("maybe", [Msg("The exact amount depends on your family income.")],
                      up_to=formula_estimate(a, p, income=0), counts_in_total=False)
    if amount == 0:
        return Result("no", [Msg("Your family income is above the limit.")])
    return Result("likely", [Msg("Worked out from a family income of about {income}.", income=Money(a.income))],
                  estimate=amount)


@rule("renter_credit")
def renter_credit(a: Answers, p: dict, today: date):
    if a.housing != "rent":
        return None
    if not a.tax_resident:
        return Result("no", [Msg("You need to be a resident for tax purposes.")])
    min_age = p.get("min_age", 19)
    if a.age < min_age and not a.family:
        return Result("not_yet", [Msg("You need to be {age} or older (or have a partner or child).", age=min_age)],
                      available_from=Msg("after you turn {age}", age=min_age))
    amount = formula_estimate(a, p)
    if amount == 0:
        return Result("no", [Msg("Your family income is above the limit.")])
    return Result("likely", [Msg("You rent your home.")], estimate=amount)


@rule("health_card")
def health_card(a: Answers, p: dict, today: date):
    if a.status in ("citizen", "pr", "protected"):
        if a.arrived is None:
            return None          # born here or here for years: they already have it
        return Result("likely", [Msg(p["wait"])], counts_in_total=False)
    if a.status == "work_permit":
        return Result("maybe", [Msg("Usually only if your work permit is long enough (often 6 to 12 months or "
                                    "more). Check the rules for your permit.")], counts_in_total=False)
    if a.status == "study_permit":
        status = "maybe" if p.get("study_permit") == "maybe" else "no"
        return Result(status, [Msg(p["study_note"])], counts_in_total=False)
    if a.status == "refugee_claimant":
        return Result("no", [Msg("You're covered by the Interim Federal Health Program until your claim is "
                                 "accepted.")], counts_in_total=False)
    return Result("no", [Msg("Visitors aren't covered. Buy travel health insurance.")], counts_in_total=False)


@rule("provincial_student_aid")
def provincial_student_aid(a: Answers, p: dict, today: date):
    if not a.post_secondary:
        return None
    if not a.can_get_osap:
        return Result("no", [student_aid_status_reason(a)], counts_in_total=False)
    note = Msg(p.get("note", "It's based on need: grants you don't pay back, plus loans."))
    months, needed = a.months_in_canada(today), p.get("residency_months")
    if needed and months is not None and months < needed:
        opens = add_months(a.arrived, needed)
        return Result("not_yet", [note], counts_in_total=False,
                      available_from=Msg("{month}", month=Month(opens.year, opens.month, 1)))
    return Result("likely", [note], counts_in_total=False)


@rule("rent_help")
def rent_help(a: Answers, p: dict, today: date):
    if a.housing != "rent" or a.status not in p.get("statuses", ("citizen", "pr", "protected")):
        return None
    people = 1 + a.has_partner + a.kids
    if a.income > p["one_person_limit"] * people ** 0.5:
        return None
    return Result("maybe", [Msg("You rent and have a lower income. The limit for one person is about {amount} "
                                "a year.", amount=Money(p["one_person_limit"]))], counts_in_total=False)
