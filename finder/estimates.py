"""Dollar estimates from the official formulas. Each function returns whole dollars per year.

The numbers come from the data files (params), so a new benefit year is a data change only.
"""


def _over(income: float, threshold: float) -> float:
    return max(0.0, income - threshold)


def cgeb(p: dict, *, has_partner: bool, kids: int, income: float) -> int:
    """Canada Groceries and Essentials Benefit (formerly the GST/HST credit).

    Single parents get the adult amount for their first child plus the full single top-up.
    Single people with no children get the top-up only as their income passes a starting point.
    """
    if has_partner:
        amount = 2 * p["adult"] + kids * p["child"]
    elif kids:
        amount = 2 * p["adult"] + p["single_supplement"] + (kids - 1) * p["child"]
    else:
        top_up = min(p["single_supplement"], p["supplement_rate"] * _over(income, p["supplement_start"]))
        amount = p["adult"] + top_up
    amount -= p["reduction_rate"] * _over(income, p["reduction_start"])
    return max(0, round(amount))


def cwb(p: dict, *, family: bool, work_income: float, income: float) -> int:
    """Canada Workers Benefit, basic amount (the disability supplement is shown separately)."""
    most = p["family_max"] if family else p["single_max"]
    start = p["family_reduction_start"] if family else p["single_reduction_start"]
    amount = min(most, p["phase_in_rate"] * _over(work_income, p["min_work_income"]))
    amount -= p["reduction_rate"] * _over(income, start)
    return max(0, round(amount))


def ccb(p: dict, *, under_6: int, age_6_to_17: int, income: float) -> int:
    """Canada Child Benefit for all children together."""
    count = under_6 + age_6_to_17
    if count == 0:
        return 0
    full = under_6 * p["under_6"] + age_6_to_17 * p["age_6_to_17"]
    i = min(count, 4) - 1
    if income <= p["first_threshold"]:
        reduction = 0
    elif income <= p["second_threshold"]:
        reduction = p["rate_1"][i] * (income - p["first_threshold"])
    else:
        reduction = p["base_2"][i] + p["rate_2"][i] * (income - p["second_threshold"])
    return max(0, round(full - reduction))


def ocb(p: dict, *, kids: int, income: float) -> int:
    """Ontario Child Benefit."""
    amount = kids * p["per_child"] - p["reduction_rate"] * _over(income, p["threshold"])
    return max(0, round(amount))


def ostc(p: dict, *, has_partner: bool, kids: int, income: float) -> int:
    """Ontario Sales Tax Credit."""
    people = 1 + has_partner + kids
    single = not has_partner and kids == 0
    threshold = p["single_threshold"] if single else p["family_threshold"]
    amount = people * p["per_person"] - p["reduction_rate"] * _over(income, threshold)
    return max(0, round(amount))


def oeptc(p: dict, *, annual_rent: float = 0, property_tax: float = 0, residence: bool = False,
          income: float, family: bool) -> int:
    """Ontario Energy and Property Tax Credit, for people under 65 (CRA 2026 calculation sheet)."""
    residence_amount = p["residence_amount"] if residence else 0
    occupancy = p["rent_share"] * annual_rent + property_tax + residence_amount
    energy = min(occupancy - residence_amount, p["energy_max"])
    property_part = min(min(p["property_rate"] * occupancy, p["property_cap"]) + p["property_add"], occupancy)
    threshold = p["family_threshold"] if family else p["single_threshold"]
    amount = energy + property_part - p["reduction_rate"] * _over(income, threshold)
    return max(0, round(amount))


def noec(p: dict, *, family: bool, income: float) -> int:
    """Northern Ontario Energy Credit."""
    most = p["family_max"] if family else p["single_max"]
    threshold = p["family_threshold"] if family else p["single_threshold"]
    return max(0, round(most - p["reduction_rate"] * _over(income, threshold)))


def liwtc(p: dict, *, has_partner: bool, work_income: float, income: float) -> int:
    """Ontario Low-Income Workers Tax Credit (a cut to Ontario tax owed, not a payment)."""
    threshold = p["family_threshold"] if has_partner else p["individual_threshold"]
    amount = min(p["max"], p["rate"] * work_income) - p["reduction_rate"] * _over(income, threshold)
    return max(0, round(amount))


# ---------------------------------------------------------------- other provinces
# Each takes the benefit's params and returns whole dollars a year, or None when the official
# page gives no formula for this income (the page then shows "up to" instead).

def _per_child(amounts: list, kids: int) -> float:
    """Amounts listed for the 1st, 2nd, 3rd... child; later children get the last amount."""
    return sum(amounts[min(i, len(amounts) - 1)] for i in range(kids))


def bc_family_benefit(p: dict, *, kids: int, income: float, single_parent: bool) -> int:
    most = _per_child(p["per_child"], kids) + (p["single_parent"] if single_parent else 0)
    least = _per_child(p["minimum"], kids)
    if income <= p["second_threshold"]:
        amount = max(least, most - p["rate"] * _over(income, p["first_threshold"]))
    else:
        amount = least - p["rate"] * _over(income, p["second_threshold"])
    return max(0, round(amount))


def alberta_child_family(p: dict, *, kids: int, income: float, work_income: float) -> int:
    base = _per_child(p["base"], kids)
    span = p["working_threshold"] - p["base_threshold"]
    base *= max(0.0, 1 - _over(income, p["base_threshold"]) / span)
    working = min(_per_child(p["working"], kids),
                  p["working_phase_in"] * _over(work_income, p["working_start"]))
    working -= p["working_rate"] * _over(income, p["working_threshold"])
    return max(0, round(base + max(0.0, working)))


def flat_per_child(p: dict, *, kids: int, income: float):
    """Full amount per child under a threshold; the official page gives no formula above it."""
    if income > p["full_below"]:
        return None
    return round(_per_child(p["per_child"], kids))


def nwt_child(p: dict, *, under_6: int, age_6_to_17: int, income: float) -> int:
    """GNWT's table gives the total for 1 to 4 children of each age; each child after that adds a set
    amount. Full under one income, then a straight line down to $0."""
    def total(table, extra, count):
        return table[min(count, 4) - 1] + extra * max(0, count - 4) if count else 0
    full = (total(p["under_6"], p["under_6_extra"], under_6)
            + total(p["age_6_to_17"], p["age_6_to_17_extra"], age_6_to_17))
    share = 1 - _over(income, p["full_below"]) / (p["zero_at"] - p["full_below"])
    return max(0, round(full * share))


def pei_child(p: dict, *, kids: int, income: float):
    if income < p["lower"]:
        return round(kids * p["low_income"])
    if income <= p["upper"]:
        return round(kids * p["middle_income"])
    return None


def adults_and_children(p: dict, *, has_partner: bool, kids: int, income: float, living_alone: bool = False) -> int:
    """Credits built from an adult amount, a partner (or first child of a single parent) amount
    and a per-child amount, reduced by a rate above a threshold (SK, NS, NB style)."""
    amount = p["adult"]
    if has_partner:
        amount += p["partner"] + p["child"] * min(kids, p.get("max_children", 99))
    elif kids:
        amount += p.get("first_child_single_parent", p["child"]) + p["child"] * min(kids - 1, p.get("max_children", 99) - 1)
    amount -= p["rate"] * _over(income, p["threshold"])
    return max(0, round(amount))


def pei_essentials(p: dict, *, family: bool, income: float) -> int:
    top = p["family"] if family else p["single"]
    end = p["family_end"] if family else p["single_end"]
    if income <= p["start"]:
        return top
    if income >= end:
        return p["minimum"]
    share = (income - p["start"]) / (end - p["start"])
    return round(top - share * (top - p["minimum"]))


def renters_credit(p: dict, *, income: float) -> int:
    return max(0, round(p["max"] - p.get("rate", 0) * _over(income, p.get("threshold", 0))))


def quebec_solidarity(p: dict, *, has_partner: bool, kids: int, income: float, has_home: bool) -> int:
    adults = 1 + has_partner
    qst = adults * p["qst_adult"] + (p["qst_alone"] if not has_partner and not kids else 0)
    housing = 0
    if has_home:
        housing = (p["housing_couple"] if has_partner else p["housing_single"]) + kids * p["housing_child"]
    rate = p["rate_two_parts"] if housing else p["rate_one_part"]
    return max(0, round(qst + housing - rate * _over(income, p["threshold"])))


FORMULAS = {
    "bc_family_benefit": bc_family_benefit,
    "alberta_child_family": alberta_child_family,
    "flat_per_child": flat_per_child,
    "pei_child": pei_child,
    "nwt_child": nwt_child,
    "adults_and_children": adults_and_children,
    "pei_essentials": pei_essentials,
    "renters_credit": renters_credit,
    "quebec_solidarity": quebec_solidarity,
}
