"""Print the results for the five sample people: python -m finder.demo [name]"""

import sys

from .engine import find
from .samples import PEOPLE, TODAY

LABELS = {"likely": "LIKELY", "maybe": "MAYBE", "not_yet": "NOT YET", "no": "NO"}


def show(name: str) -> None:
    report = find(PEOPLE[name], today=TODAY)
    print(f"\n=== {name} ===  about ${report.total:,} a year in likely money")
    for title, items in report.groups:
        print(f"\n  {title}")
        for item in items:
            amount = (f"about ${item.estimate:,}/yr" if item.estimate
                      else f"up to ${item.up_to:,}" if item.up_to else "")
            print(f"    [{LABELS[item.status]:7}] {item.name} {amount}")
            for reason in item.reasons:
                print(f"              - {reason}")
    if report.not_yet:
        print("\n  Not yet")
        for item in report.not_yet:
            print(f"    {item.name}: {item.available_from}")
    if report.ruled_out:
        print("\n  Probably not for you")
        for item in report.ruled_out:
            print(f"    {item.name}: {item.reasons[0]}")
    print("\n  Plan")
    for number, step in enumerate(report.plan, 1):
        print(f"    {number}. {step.text}")


if __name__ == "__main__":
    for person in sys.argv[1:] or PEOPLE:
        show(person)
