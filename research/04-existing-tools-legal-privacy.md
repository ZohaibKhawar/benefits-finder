# Existing tools, the gap, legal, privacy and accessibility

Researched 2026-10-18.

---

## 1. Tools that already exist (the competition)

| Tool | Who runs it | What it does | What it doesn't do |
|---|---|---|---|
| **Benefits Finder (federal)** canada.ca/benefits-finder | Government of Canada | Filter list of **157 federal** benefits by type and audience (page dated April 2026). A redesign around "life events" is being tested. | Federal only in the list version; no dollar estimates; not student/newcomer specific. |
| **Benefits Finder questionnaire** benefitsfinder.services.gc.ca | Government of Canada | Questionnaire, may suggest federal + provincial programs, doesn't store data. | Generic; no amounts; no "do this first" plan. |
| **Ontario Benefits Finder** benefitsfinder.mof.gov.on.ca | Ontario Ministry of Finance | **21 questions** (newcomer?, age, income range, job status, kids, disability, student?, housing, veteran...). Filtered list of Ontario programs. Anonymous, nothing stored. | Ontario programs only; **no amounts**; income in wide $25k bands; no student detail (full-time vs part-time, residence vs renting, permit type). |
| **Benefits wayfinder** benefitswayfinder.org | Prosper Canada (charity), sponsored by TD | Bilingual. Starting points by life event, questionnaire, browse all, local help agencies. Launched Jan 2022; 4,419 frontline staff trained. | Built for caseworkers and low-income people in general; no amounts. |
| **211 Ontario** 211ontario.ca | United Way / 211 | Directory of local services by phone, chat, web. | Directory, not eligibility. |
| **CRA child and family benefits calculator** | CRA | Exact estimates of CCB, CGEB, OTB, OCB from income. | You must already know which benefits apply and your exact numbers; no student/newcomer guidance. |
| **OSAP Aid Estimator** | Ontario | OSAP estimate. | OSAP only. |
| **Tax software** (Wealthsimple Tax, TurboTax, UFile...) | Companies | Claims credits while you file. | Only at tax time; doesn't tell you about OSAP, OHIP, CDCP, RC151 before you file. |
| **Settlement.org / WelcomeAide / immigration blogs** | Non-profits, companies | Long articles for newcomers. | Not personalized; some have wrong numbers (several 2026 blogs disagree with the CRA). |

**The gap our app can fill:**

1. **Students and newcomers specifically.** None of the official tools ask the questions that actually
   flip the answer for these groups: full-time vs part-time, public vs career college, residence vs
   off-campus rent, study/work permit and months in Canada, student health plan, born 2004+.
2. **Dollar estimates** ("about $1,200 a year") using the official formulas, with the
   official calculator linked for the exact number. Official finders give a list, not money.
3. **An ordered action plan.** "1. Get a SIN. 2. Apply RC151 today. 3. Apply for OHIP at ServiceOntario.
   4. File a return by April 30 even with zero income. 5. Set a reminder for month 19 for the CCB."
4. **"Not yet" answers**, not just yes/no: "You'll qualify for the CCB in August 2027."
5. **What changed in 2026** in plain words: GST credit renamed and 25% bigger, OSAP mostly loans,
   CDCP open to all ages, IFHP co-pays, settlement services time limit.
6. **Plain language** (grade 6 to 8 reading level), mobile-first, fast, no sign-up.

Positioning line: "Find the money you're owed as a student or newcomer in Ontario, in 3 minutes, with
the official link for each one."

## 2. Why it matters (numbers for the About page or a pitch)

- Carleton researchers estimated about **$1.7 billion** in benefits lost by working-age non-filers in
  2015; about 12% of working-age Canadians didn't file.
- The PBO estimated automatic filing could return **$1.7 to $1.9 billion a year**.
- StatCan: non-permanent residents had a **40.2% non-filing rate** (2021), much higher than average.
- So the #1 message of the app is: **file a tax return, even with no income.**
- **Coming change:** the CRA starts **automatic tax filing for about 1 million low-income people for the
  2026 tax year** (returns in 2027), growing to about 5.5 million by 2028. Newcomers and students with
  T2202/foreign income likely won't be auto-filed at first. Keep the "file your taxes" step but mention it.

## 3. Legal: what the app must and must not do

**It's information, not advice.**
- Show on every results page: "This is an estimate to help you find programs. It isn't tax, legal or
  immigration advice. The government decides if you qualify. Check the official page before you apply."
- Never say "you will get $X". Say "you might qualify for up to $X".
- Don't give immigration advice (that's regulated: only licensed RCICs and lawyers can). Questions about
  status are only used to filter benefits.
- Don't fill in or submit government forms for people. Link to them.

**Don't look like the government.**
- No Canada wordmark, flag symbol, Arms of Canada, or Ontario trillium logo. The Open Government
  Licence excludes official symbols, and using them needs written permission.
- Footer: "Not affiliated with the Government of Canada or the Government of Ontario."
- Domain must not look like a .gc.ca or ontario.ca address.

**Reusing government text.**
- Most canada.ca content is under the **Open Government Licence – Canada**: free reuse (even
  commercial) with attribution: "Contains information licensed under the Open Government Licence – Canada."
- Ontario has its own **Open Government Licence – Ontario** (same idea; confirm terms).
- Better: write our own plain-language summaries and **link** to the official pages. Linking needs no
  permission.

## 4. Privacy (PIPEDA)

- PIPEDA covers personal information collected in commercial activity. If the app is free with no ads
  it may fall outside, but design as if it applies.
- **Best design: collect nothing.** Run the questionnaire in the browser or keep answers only in the
  request; no accounts in the MVP; never ask for a name, SIN, address, email or exact birthdate (ask
  age range or birth year only).
- Income: ask a number, but don't store it. Show "We don't save your answers" (Ontario's finder does
  the same; users expect it).
- Analytics: count page views and which benefits show up, with no IPs or answer-level data
  (e.g. self-hosted, cookie-free analytics). No cookie banner needed if no tracking cookies.
- If accounts or email reminders come later (e.g. "remind me in month 19 for the CCB"), add a privacy
  policy listing what is collected, why, how long it's kept, and how to delete it (OPC consent guidance).
- Bill C-27 (to replace PIPEDA) died in early 2025; PIPEDA still applies (confirm nothing new was passed).

## 5. Accessibility (AODA / WCAG)

- AODA's website rule (WCAG 2.0 AA) legally applies to Ontario public sector and private organizations
  with 50+ employees, so a solo project isn't required to meet it. **Do it anyway**: the audience includes
  people with disabilities, low vision, older phones, and English learners.
- Target **WCAG 2.1 AA**: labels on every input, keyboard-only use, visible focus, 4.5:1 contrast, no
  color-only meaning, errors in text, works at 320px wide, page language set, plain language.
- **French:** not legally required for a private site, but Ontario has 600k+ francophones and many
  newcomers come from French-speaking countries. Plan it for phase 3 (all text in translation files
  from day one so it's cheap later).

## 6. Data freshness: the real risk

Benefit numbers change on fixed dates. Wrong numbers are the fastest way to lose trust (several 2026
blogs already disagree with the CRA). The app needs an update calendar:

| When | What changes |
|---|---|
| **January** | New tax year: CWB, LIWTC, tuition and other tax credit amounts (indexed). Ontario Works/ODSP sometimes. |
| **Late Feb / March** | Federal budget, Ontario budget (new programs, cuts like OSAP 2026). |
| **April 1** | IRCC settlement rules, RAP thresholds, some Ontario programs. |
| **June** | CRA publishes July amounts for CGEB, CCB, OTB, OCB. |
| **July** | New benefit year starts (CGEB, CCB, OTB, OCB, CDB, ODSP, Healthy Smiles limits). |
| **August 1** | New OSAP / student aid year. |

Each benefit in the data file gets `last_checked` and `source_url`; a weekly job checks every link for
404s and flags anything not checked in 6+ months.

## Sources

- [Federal Benefits Finder](https://www.canada.ca/en/services/benefits/finder.html)
- [Benefits Finder questionnaire](https://benefitsfinder.services.gc.ca)
- [Ontario Benefits Finder](https://benefitsfinder.mof.gov.on.ca/Questionnaire?lang=en)
- [Prosper Canada: Benefits wayfinder](https://prospercanada.org/News-Media/News/The-Benefits-wayfinder-Simplifying-benefits-access.aspx)
- [benefitswayfinder.org about](https://benefitswayfinder.org/about)
- [Tamarack: wayfinder launch](https://www.tamarackcommunity.ca/latest/prosper-canada-launches-benefits-wayfinder-to-support-access-to-government-benefits)
- [Carleton: the mystery of unclaimed tax benefits](https://carleton.ca/sppa/2021/the-mystery-of-unclaimed-tax-benefits/)
- [StatCan: income research paper 2025004](https://www150.statcan.gc.ca/n1/pub/75f0002m/75f0002m2025004-eng.htm)
- [CTV: PBO on automatic filing](https://prd.ctvnews.ca/canada/article/a-new-tax-filing-system-could-give-canadians-more-than-1-billion-in-unclaimed-benefits-pbo)
- [Global News: automatic tax filing](https://globalnews.ca/news/11473231/automatic-tax-filing-low-income-canadians-budget)
- [IRPP on automatic filing](https://irpp.org/?p=21322)
- [Finance Canada terms and conditions (OGL)](https://www.canada.ca/en/department-finance/corporate/terms-conditions.html)
- [eCampusOntario: government websites and copyright](https://ecampusontario.pressbooks.pub/authoringguide/chapter/government-websites-and-publications/)
- [OPC: privacy guide for businesses](https://www.priv.gc.ca/media/4895/bus_notes_eng.pdf)
- [Accessibility.Works: AODA website requirements](https://www.accessibility.works/aoda-website-accessibility-requirements/)
