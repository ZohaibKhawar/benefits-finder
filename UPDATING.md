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
- [ ] Canada Child Benefit (`ccb`) and every provincial child benefit.
- [ ] Ontario Trillium parts (`oeptc` from the new CRA calculation sheet, `ostc`, `noec`).
- [ ] Every provincial credit paid with the grocery benefit (SK, NS, NB, PE, NL).
- [ ] Quebec solidarity tax credit (`qc_solidarity`).
- [ ] Canada Disability Benefit (`cdb`).
- [ ] The slip note "Estimates for July 2026 to June 2027" in `templates/_slip.html` and its French
      line in `translations/fr.yaml`.

## August 1

- [ ] Student aid year: OSAP and the other provinces, Canada Student Grant amounts.

## Every week

- [ ] `python check_links.py`. Fix any link marked BAD. RAMQ blocks scripts; open it in a browser.
