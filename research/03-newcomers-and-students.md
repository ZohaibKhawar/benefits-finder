# Rules that change by who you are (newcomers and students)

Researched 2026-10-18. This is the file the questionnaire logic is built from. The same benefit can be
"yes", "not yet" or "no" depending on immigration status, student status and time in Canada.

---

## 1. The two separate ideas the app must keep apart

1. **Immigration status** (citizen, PR, protected person, refugee claimant, study permit, work permit,
   visitor). Decides OSAP, OHIP, the CCB, settlement services.
2. **Residency for tax purposes** (resident, non-resident, deemed resident). Decided by **residential
   ties** (a home, spouse, or dependants in Canada; secondary ties like a bank account, driver's licence,
   provincial health card). Decides the CGEB (GST credit), Ontario Trillium Benefit, CDCP, CWB.
   - "For most newcomers, this starts the first day you live in Canada." (CRA, official)
   - Most international students who live here for their program **are residents for tax purposes**.
   - Non-resident = no significant ties and under 183 days in Canada in the year.
   - Unsure? Form **NR74** asks the CRA to decide.

The questionnaire should ask about status in plain words, then assume "resident for tax purposes" for
anyone who lives in Ontario, with a note and a link to NR74 if they're unsure.

## 2. Newcomer rules (official CRA, newcomers page)

- **You can apply for benefits before your first tax return.** One application per household.
- **CGEB (GST credit):**
  - No kids: online **web form RC151** (launched June 2025, no mail needed).
  - Kids under 19: mail **PDF RC151** with proof of birth, or use **RC66** if eligible for the CCB.
- **CCB:** form **RC66** + **RC66SCH** (status in Canada and income). One form also signs you up for the
  CGEB child amounts and the **Ontario Child Benefit**.
- **Temporary residents and the CCB:** eligible only from the **19th month** after arriving, with a valid
  permit in the 19th month. Permits marked "does not confer status" don't count. Before that, RC66 still
  registers the kids for the CGEB. (Official T4114 guide.) So a family on a study or work permit should
  apply for the CGEB now and set a reminder for month 19 for the CCB.
- **World income:** the forms ask for income earned **outside Canada for up to two years before** you
  became a resident (not taxed, only used to calculate benefits). Missed it? Send a Statement of Income in
  My Account.
- **First tax return:** due April 30 of the year after you arrive (e.g. arrived 2026 -> file by
  April 30, 2027). Filing is what keeps benefits going and unlocks the CDCP, OTB and CWB.
- **SIN:** needed for benefits, work, most bank accounts. Apply through Service Canada. Without one, the
  CRA can issue a temporary tax number.
- **CDCP:** needs a filed Canadian return first. Arrived 2026 -> likely after filing in early 2027.

## 3. Status-by-benefit table (Ontario, 2026)

Y = can qualify if other rules met. N = no. Later = after a waiting rule. ? = check.

| Benefit | Citizen / PR | Protected person | Refugee claimant | Study permit (intl student) | Work permit |
|---|---|---|---|---|---|
| CGEB (GST credit) | Y | Y | Y if tax resident | Y if tax resident (RC151) | Y if tax resident |
| Canada Child Benefit | Y | Y | N (until protected) | Later (month 19) | Later (month 19) |
| Ontario Child Benefit | with CCB | with CCB | N | with CCB | with CCB |
| Ontario Trillium (OEPTC/OSTC) | Y | Y | Y if tax resident | Y if tax resident | Y |
| Canada Workers Benefit | Y | Y | Y if tax resident all year | rarely (full-time student rule) | Y |
| CDCP (dental) | Y | Y | ? (IFHP covers dental) | rarely (student plan) | Y |
| OSAP / Canada Student Grant | Y | Y | N | **N** | N |
| OHIP | Y | Y | N (IFHP instead) | **N** (UHIP/college plan) | Y if full-time Ontario job 6+ months |
| OHIP+ (24 and under) | with OHIP | with OHIP | N | N | with OHIP |
| IFHP (federal health) | N | until OHIP | **Y** | N | N |
| Tuition tax credit | Y | Y | Y | Y (T2202) | Y |
| Settlement services (IRCC) | PR: Y (economic class only 6 yrs) | Y | ? | N | mostly N |
| OBPAP bridging bursary | Y | Y | some | N | some (PR approved) |
| Ontario Works | Y | Y | Y (confirm) | N | ? |

Notes:
- **Refugee claimants:** the Interim Federal Health Program (IFHP) covers doctor and hospital visits free;
  since **May 1, 2026** there are co-pays for extras ($4 per prescription, 30% of dental, vision,
  counselling, devices). Coverage is automatic. Bill C-12 (law March 26, 2026) changed some asylum rules;
  check effects before launch.
- **Settlement services change (April 1, 2026):** economic-class PRs can use IRCC-funded settlement
  services for **6 years** from becoming PR (or until citizenship); this drops to **5 years on April 1,
  2027**. People who landed before April 1, 2020 lost access. Refugees/protected persons still qualify.
- **International students** can't get OSAP, OHIP or (usually) the CWB, but **can** get the CGEB, the
  Ontario Trillium Benefit (if they rent off campus) and the tuition credit (carried forward until they
  owe tax). Many never file because "I have no income", and miss the CGEB entirely. This is a strong
  hook for the app.

## 4. Student rules that change results

| Question | Why it matters |
|---|---|
| Full-time or part-time? | CWB excludes full-time students enrolled 13+ weeks (unless they have a dependant). OSAP living costs only for full-time. Part-time Canada Student Grant is different. |
| Public school or private career college? | From Aug 1, 2026: career college students get no provincial OSAP grant and mostly no federal full-time grant. |
| Live in residence, rent off campus, or with parents? | OEPTC: residence counts as only $25; off-campus rent counts (20% of rent). Living with parents rent-free = no OEPTC. |
| Age (under 19, 19 to 24, 25+) | CGEB starts at 19. OHIP+ ends at 25. Canada Training Credit starts at 25. CLB can be claimed until 21. |
| Under 21 and family was low income? | Canada Learning Bond: up to $2,000 never claimed. |
| Have a student health/dental plan? | Blocks the CDCP; OHIP+ bills it first. |
| Have kids? | CCB, OCB, CGEB child amounts, OSAP child care, Canada Student Grant for dependants, CWB student exception, CARE credit. |
| Have a disability? | DTC, Canada Student Grant for Students with Disabilities, BSWD, CDB, CWB supplement, longer OSAP limit. |
| Paid tuition this year? | Tuition credit (T2202). Unused amounts carry forward forever; or transfer up to $5,000 to a parent. |
| Moved 40 km+ for school or a summer job? | Moving expenses deduction. |
| Studying nursing / paramedic / med lab in the north, east or southwest? | Ontario Learn and Stay Grant (full tuition). |
| Internationally trained, in a bridge program? | OBPAP up to $5,000. |
| Laid off and want to retrain? | Better Jobs Ontario up to $28,000 / $35,000. |
| Hydro bill in your name? | OESP monthly credit. |
| Repaying student loans? | Repayment Assistance Plan (zero payment under about $3,788/month income, single). |

## 5. Five sample people (use as test cases in the app)

1. **Aisha, 20, domestic full-time university student, rents off campus in Toronto ($900/month),
   earned $9,000 at a part-time job, no kids.**
   CGEB yes (up to $679; the single top-up part phases in with income, so at $9,000 it's closer to the
   $445 base, confirm on the CRA payments chart), OSTC yes ($378), OEPTC yes (rent $10,800 -> occupancy cost $2,160 -> part of
   the credit), CWB **no** (full-time student), OSAP yes (apply; federal grant up to $4,200, Ontario part
   now mostly loans), tuition credit yes (carry forward), OHIP+ only if no student drug plan, LIWTC no
   effect (owes no Ontario tax). CLB if born 2004+ and low-income family: check.
2. **Wei, 24, international master's student in Waterloo, study permit, lives in residence, TA income
   $14,000.** CGEB yes via RC151 (if tax resident), OEPTC tiny ($25 residence rule), OSTC yes, OSAP no,
   OHIP no (UHIP), tuition credit yes, CWB no (full-time student), CDCP likely no (student plan).
3. **Carlos and Maria, new PRs arrived March 2026 in Mississauga, two kids (3 and 8), Carlos working
   $38,000.** RC66 now (CCB both kids, CGEB, OCB), OHIP now (no wait), settlement services yes (6 years),
   first return due April 30, 2027, then OTB, CWB (family), CDCP after filing, Healthy Smiles for kids
   now if income under $31,265, $10-a-day child care for the 3-year-old, OBPAP if doing a bridge program.
4. **Priya, 29, part-time college student and single mom in Sudbury, earns $22,000.** CCB, OCB, CGEB,
   OEPTC + **NOEC** (Northern Ontario), OSTC, CWB yes (part-time, or full-time with a dependant), OSAP
   part-time + child care, Canada Student Grant for dependants, CARE credit, CDCP (if no plan),
   Healthy Smiles for the child, OESP if hydro in her name.
5. **Daniel, 22, refugee claimant in Ottawa, no permit yet, not working.** IFHP (automatic), Ontario
   Works (check), CGEB if tax resident (file a return even with zero income), free tax clinic,
   settlement agency, legal aid (Legal Aid Ontario). No OSAP, no OHIP, no CCB until protected.

## Sources

- [CRA: Newcomers to Canada](https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/individuals-leaving-entering-canada-non-residents/newcomers-canada-immigrants.html)
- [CRA: International students studying in Canada](https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/individuals-leaving-entering-canada-non-residents/international-students-studying-canada.html)
- [CRA T4114: Canada Child Benefit guide](https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/t4114/canada-child-benefit.html)
- [CRA tax tip: new online form for newcomers (2025)](https://www.canada.ca/en/revenue-agency/news/newsroom/tax-tips/tax-tips-2025/apply-benefit-credit-payments-using-new-online-form.html)
- [Ontario: Apply for OHIP](https://www.ontario.ca/page/apply-ohip-and-get-health-card)
- [Ontario: Learn about OSAP](https://www.ontario.ca/page/learn-about-osap)
- [ISANS: settlement eligibility changes April 1, 2026](https://isans.ca/settlement-program-eligibility-changes/)
- [CLEO: changes to IFHP](https://cleoconnect.ca/resource/yourlegalrights/changes-to-the-interim-federal-health-program-ifhp/)
- [BNN Bloomberg: IFHP co-pays](https://www.bnnbloomberg.ca/business/economics/2026/01/30/ottawa-will-soon-require-asylum-seekers-and-refugees-to-co-pay-for-health-care/)
- [StatCan: non-filers and the CWB](https://www150.statcan.gc.ca/n1/pub/75f0002m/75f0002m2025004-eng.htm)
