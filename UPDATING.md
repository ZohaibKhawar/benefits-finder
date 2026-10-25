# Keeping the numbers right

Benefit amounts change on fixed dates. Wrong numbers lose trust fast, so check these on schedule.
Every number lives in `data/*.yaml`; update it there, change `last_checked`, then run:

```
python -m pytest
python check_links.py
python -m finder.i18n_keys fr
```

The tests check the formulas against the official income limits. If a test fails after you change a
number, the official limit in the test changed too: update both from the same official page.

## January (new tax year)

- [ ] Canada Workers Benefit amounts and thresholds (`federal.yaml` → `cwb`). CRA "How much you can get".
- [ ] Northern residents deduction daily amounts (`northern_residents`), CRA line 25500.
- [ ] Canada Training Credit income limits (`training_credit`).
- [ ] Ontario Low-Income Workers Tax Credit (`liwtc`), BC renter's credit (`bc_renter_credit`),
      Manitoba renters credit (`mb_renter_credit`).
- [ ] Quebec family allowance amounts (`qc_family_allowance`), indexed every January.
- [ ] Tax deadline wording: nothing to change, it's worked out from the date.

## February to March (budgets)

- [ ] Federal budget and each provincial budget: new programs, ended programs, cuts (like OSAP in 2026).
- [ ] Add or remove entries; never list ended programs (the tests block "carbon rebate").

## April 1

- [ ] IRCC settlement-service eligibility (5-year limit from April 2027).
- [ ] Repayment Assistance Plan threshold (`rap`).

## June (CRA publishes July amounts)

- [ ] Canada Groceries and Essentials Benefit (`cgeb`): adult, child, single top-up, thresholds.
- [ ] Canada Child Benefit (`ccb`) and every provincial and territorial child benefit (the NWT table is in
      the GNWT Finance handout).
- [ ] Ontario Trillium parts (`oeptc` from the new CRA calculation sheet, `ostc`, `noec`).
- [ ] Every provincial credit paid with the grocery benefit (SK, NS, NB, PE, NL).
- [ ] Quebec solidarity tax credit (`qc_solidarity`).
- [ ] Canada Disability Benefit (`cdb`).
- [ ] The slip note "Estimates for July 2026 to June 2027" in `templates/_slip.html` and its French
      line in `translations/fr.yaml`.

## August 1

- [ ] Student aid year: OSAP and the other provinces, Canada Student Grant amounts, the Yukon Grant weekly
      rate, NWT SFA and Nunavut FANS amounts.

## September to October (scholarships)

- [ ] University entrance scholarship tables for next year's students (`data/ontario_schools.yaml`):
      schools post them in the fall. Change `last_checked` for each school you open.
- [ ] Dates in `data/student_awards.yaml`: Loran (closes mid-October), Schulich Leader and Builders,
      Terry Fox (Nov 1 to Dec 1), CGRS Master's (Dec 1), Indspire, BBPA, nurses (Jan to March), Rhodes.
- [ ] Any award that ended: remove it, and add its name to `test_ended_programs_are_not_listed`.
- [ ] A new outside award goes in only if its site is run by a government, a school, or a long-running
      charity or foundation. Add the domain to `trusted_domains` with who runs it.

## Every week

- [ ] `python check_links.py`. Fix any link marked BAD. RAMQ blocks scripts; open it in a browser.
