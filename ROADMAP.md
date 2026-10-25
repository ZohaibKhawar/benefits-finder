# Claimable (formerly Benefits Finder): roadmap

A free website for **students and newcomers anywhere in Canada** (ten provinces and three territories), in English and French. It asks
13 short questions and lists the credits and benefits they might qualify for, with a rough dollar amount,
what to do first, and the official link for each one.

Started and built 2026-10-18. Research is in [research/](research/).

**Status:** every phase is built and tested (231 tests). What's left needs you: choosing hosting and a
name, putting it online (`DEPLOY.md`), sending the outreach, and the open number checks
below and in research/05.

---

## What makes it different

Ontario and Canada already run free "Benefits Finder" quizzes (see
[research/04](research/04-existing-tools-legal-privacy.md)). They give a generic list with no amounts.
This app wins on:

1. **Questions that matter for students and newcomers** (full-time or part-time, residence or renting,
   permit type, months in Canada, student health plan, public school or career college).
2. **Dollar estimates** from the official formulas ("about $1,100 a year"), with the official calculator
   linked for the exact number.
3. **A step-by-step plan** in the right order (SIN, RC151, OHIP, file taxes by April 30, ...).
4. **"Not yet" results** ("You can get the Canada Child Benefit from August 2027").
5. **Plain English**, phone-first, no sign-up, nothing saved.

---

## Phase 0: Research (done 2026-10-18)

- [x] Federal benefits: [01-federal-benefits.md](research/01-federal-benefits.md)
- [x] Ontario benefits: [02-ontario-benefits.md](research/02-ontario-benefits.md)
- [x] Newcomer and student rules, 5 sample people: [03-newcomers-and-students.md](research/03-newcomers-and-students.md)
- [x] Competitors, legal, privacy, accessibility, update calendar: [04-existing-tools-legal-privacy.md](research/04-existing-tools-legal-privacy.md)
- [x] Confirm the main formulas on official pages (done 2026-10-18; what's left is at the bottom)

## Phase 1: Benefit data and rules engine (done 2026-10-18)

The core, no UI. Text and numbers live in data files; the logic for each benefit is one small
function. A new benefit year is a data edit; a new province is a new data file plus its rules.

- `data/federal.yaml`, `data/ontario.yaml`: 33 benefits and programs with plain-language summary,
  how to get it, official link, `last_checked`, `source` (official or secondary) and the numbers.
- `finder/answers.py`: what the person told us (age, status, arrival month, student, housing, rent,
  partner, kids, income, plans, disability...), with checks on bad input.
- `finder/rules.py`: one rule per benefit: **likely / maybe / not yet / no** with plain reasons.
  Covers the 13-week student rule, month 19 for the CCB on a permit, age 18/19 starts, student plans
  blocking dental and OHIP+, career college changes, refugee claimants on IFHP.
- `finder/estimates.py`: exact formulas for the grocery benefit (CGEB), CWB, CCB, Ontario Child
  Benefit, Ontario Sales Tax Credit, Energy and Property Tax Credit, Northern Energy Credit and the
  Ontario workers' tax credit.
- `finder/engine.py`: runs every rule, sorts, totals the "likely" money and builds the step-by-step
  plan (SIN, OHIP, RC151/RC66, file by April 30 with ON-BEN, OSAP, dental, calendar dates).
- `tests/`: **56 tests**, all passing. The CGEB formula hits every zero point in the CRA's official
  income table; CWB, CCB and the Trillium parts match CRA numbers; the five sample people match the
  hand-worked results.
- `check_links.py`: opens every official link (36 of 36 working on 2026-10-18) and flags any benefit
  not re-checked in 6 months.

Run it:

```bash
pip install -r requirements.txt
python -m pytest
python -m finder.demo
python check_links.py
```

What the five sample people get (likely money a year): Aisha $1,402, Wei $897,
Carlos and Maria $21,232, Priya $14,253, Daniel $1,330.

## Phase 2: Website (done 2026-10-18)

Flask + Jinja + plain CSS/JS, no database. Run `python app.py` and open http://127.0.0.1:5240.

- **Home:** what it does, an example money slip (a Toronto student: about $1,402 a year), what changed in 2026.
- **Questionnaire:** 13 screens, one question each, progress bar, Back/Next, Enter key, fields that only
  appear when they apply. Without JavaScript it's one long form that still works.
- **Results:** the money slip with the yearly total under a highlighter, "Do these first" plan, groups
  (money, studies, health, if money is tight, free help), "Not yet, but soon" with dates, and
  "Probably not for you, and why". Calendar download, print/PDF, change my answers.
- **Pages:** every benefit and its source, one page per benefit (for search engines), about, privacy, 404.
- **Privacy:** answers only travel by POST, are never stored or logged, results pages aren't cached.
- **Design:** paper, ink and one highlighter; Atkinson Hyperlegible (a font made for legibility);
  light and dark mode; works at 320px.

## Phase 3: Quality (done 2026-10-18)

- Contrast checked for every colour pair in light and dark mode (WCAG AA); one h1 per page; every field
  labelled; unique ids; visible keyboard focus; reduced motion respected (all in `tests/`).
- Checked in the browser at phone width in English and French: no sideways scrolling.
- Speed: every page renders in under 4 ms on the server and is at most about 5 KB compressed.
- Weekly link checker (`check_links.py`): 83 official links, all working (RAMQ blocks scripts, so it's
  flagged to check by hand).
- Not done: page-view counting. Skipped on purpose to keep "we track nothing" true; add a cookie-free
  counter later if you want numbers.

## Phase 4: Launch (prepared; needs you)

- Done: sitemap, robots.txt, canonical and English/French language tags, `wsgi.py`, `DEPLOY.md`
  (PythonAnywhere steps), `UPDATING.md` (what to update each January, budget season, April, June, August),
  a GitHub workflow that runs the tests and the link check, and outreach emails and a Reddit post
  (kept out of the repository).
- **Needs you:** where to host it (a free PythonAnywhere account only allows one web app, and CalcLearners
  uses it), a name and domain, creating the repository, and sending or posting anything.

## Phase 5: Make it better (done 2026-10-18, except other languages)

- **French:** everything, including all benefit descriptions, with the governments' own French program
  names, French number and date formats, and a test that fails if any sentence is untranslated.
- **City programs (Ontario):** Toronto Fair Pass and Welcome Policy, Ottawa EquiPass, Peel transit
  discount, Hamilton Fare Assist, Waterloo transit discount, London transit pass.
- **Reminders:** instead of emails (which would mean storing addresses), a calendar file with the tax
  deadline, the July benefit-year change and any "not yet" dates.
- **AI helper:** "Ask about your results" with Claude Haiku 5.5 (the cheapest model; well under a tenth
  of a cent per question). Off until `ANTHROPIC_API_KEY` is set; 8 questions per visitor per hour and a
  daily cap; only explains results, never decides who qualifies.
- **Not done:** Punjabi, Mandarin, Arabic and other newcomer languages. Machine-translating benefit
  rules into many languages without a native speaker checking them risks telling people wrong things.
  The site is ready for them: add `translations/<lang>.yaml` and the test lists what's missing.

## Phase 6: Other provinces (done 2026-10-18)

All ten provinces: BC, Alberta, Saskatchewan, Manitoba, Quebec, New Brunswick, Nova Scotia, PEI,
Newfoundland and Labrador, plus Ontario. Each has its child benefit or credits (with exact formulas where
the CRA publishes them), health card rules for newcomers and international students, student aid and
income assistance. Quebec has its own tax return, family allowance, solidarity credit and student aid.
Sources and open questions: [research/05-other-provinces.md](research/05-other-provinces.md).

## Phase 7: Territories (done 2026-10-20)

Yukon, the Northwest Territories and Nunavut: each territory's child benefit (the NWT one with its exact
formula), health card rules for newcomers and permit holders, student aid and income assistance. The NWT
and Nunavut run their own student aid, so the federal Canada Student Grant shows as "no" there, and their
programs ask for 12 months of residency first (shown as "not yet" with the date). The federal northern
residents deduction shows for everyone in the territories. Nunavut sets its own Canada Workers Benefit
amounts, so no estimate is shown (like Alberta and Quebec).

Also fixed: the "Every benefit and its source" page listed every federal program ten times with no
province names. It now shows the federal programs once, then each province and territory under its name.

## Phase 8: Scholarships and bursaries for Ontario students (done 2026-10-25)

A second finder at `/awards` (English and French) for anyone at, or applying to, an Ontario college or
university. Eight questions: school (all 24 public colleges and 23 universities), program and subject,
year, average on any scale (percent, 4.0, 4.33, York's 9, uOttawa's 10, the 12-point scale), status in
Canada, money, optional groups (First Nations, Métis, Inuit, Black, disability, first-generation, in care,
military family) and what they do (volunteering, leadership, research, a language course).

- **Your school:** its own awards page, and the automatic entrance scholarship at your average (or how far
  below the cut-off you are) for the 18 universities that publish one.
- **Grade 12 students:** every university's automatic entrance scholarship at your average, biggest first.
- **25 outside awards and search lists:** Ontario's first-generation, Indigenous, youth-in-care and
  disability bursaries, OGS, the federal master's scholarship and research awards, Explore, Indspire,
  MNO, Loran, Schulich Leader and Builders, Terry Fox, BBPA, nurses, Rhodes. "You can apply", "Check
  first" (with what to check) or "Not for you" (with why).
- **Trusted links only:** each link's site is on a list with who runs it (shown at `/awards/sources`),
  and a test fails on anything else, including lookalike domains. A box warns about scholarship scams.
- Ended programs left out: TD Scholarships for Community Leadership, the federal apprenticeship grants.
- Sources: [research/06](research/06-student-awards.md). 59 new tests.

---

## Launch list: about 25 benefits for Ontario v1

**Federal:** Canada Groceries and Essentials Benefit (GST credit), Canada Workers Benefit, Canada Child
Benefit (+ Child Disability Benefit), Canadian Dental Care Plan, Canada Disability Benefit, Disability
Tax Credit, Canada Student Grant (full-time / part-time / disabilities / dependants), Canada Student
Loans + Repayment Assistance Plan, Tuition tax credit, Moving expenses for students, Canada Training
Credit, Canada Learning Bond, FHSA (info only), IFHP (refugee claimants).

**Ontario:** Ontario Trillium Benefit (OEPTC, NOEC, OSTC), Ontario Child Benefit, Low-Income Workers
Tax Credit, CARE credit, OSAP, Ontario Learn and Stay Grant, OHIP, OHIP+, Healthy Smiles Ontario,
Ontario Works, ODSP, OESP, Canada-Ontario Housing Benefit, OBPAP, Better Jobs Ontario.

**Free help:** CVITP free tax clinics, 211 Ontario, settlement agencies (IRCC-funded), school financial
aid offices, Legal Aid Ontario.

**Do not list (ended):** Canada Carbon Rebate (ended April 2025), Ontario tuition credit (ended 2017),
CERB/CRB, "GST/HST credit" under its old name (show it as "Canada Groceries and Essentials Benefit
(formerly GST/HST credit)").

---

## Still to confirm before the numbers go live

**Settled on 2026-10-18 (official pages):**
- CGEB formula: base $445, single top-up $234 building at 2% above $11,564, 5% reduction above
  $46,432. It lands exactly on every income limit in the CRA's table.
- Ontario Energy and Property Tax Credit: CRA 2026 calculation sheet (energy part up to $290;
  property part = 10% of occupancy cost up to $944, plus $73; 2% reduction above $29,047 single or
  $36,309 family; residence = $25).
- CWB 2025 numbers fit a 27% phase-in above $3,000 and a 15% reduction exactly.
- Opting out of a student dental plan does **not** make someone eligible for the CDCP (CDCP page).
- Canada Learning Bond: automatic RESP for eligible children born 2024+ from April 2028.

**Still open:**
1. CWB 2026 tax-year amounts (CRA usually publishes them in November).
2. Northern Ontario Energy Credit reduction (1% above $50,833 / $65,356 is from a tax site).
3. Ontario Child Benefit reduction rate (8% is from older years).
4. OSAP: official grant/loan split (25%?), Ontario residency definition, whether current students
   are grandfathered, Ontario loan interest rate.
5. CDCP co-pay bands for 2026.
6. CARE credit numbers, OESP income table, Toronto Fair Pass discount.
7. Ontario Works rules for full-time students and refugee claimants.
8. Bill C-12 (2026) effects on refugee claimants' benefits.
9. RAP threshold ($3,788 vs $3,866 for a family of one).
10. Whether the CRA's automatic filing (2026 tax year) is confirmed and who it covers.
11. Senior (65+) Trillium formula (the app shows "up to $1,488" for now).

## Decisions to make together

- **Name and domain.** Name chosen 2026-10-19: *Claimable* ("Benefits Finder" is the Government of
  Canada's own tool name). Before buying a domain, search the name in the CIPO trademarks database.
  Must not look like a government site.
- **Ask exact income or ranges?** Exact gives real estimates; ranges feel safer. Suggest: number field
  with "I don't know" -> ranges.
- **Where the logic runs.** Server (Flask, simpler to test) or browser (nothing ever leaves the phone).
  Suggest: Flask for v1, answers never stored or logged.
