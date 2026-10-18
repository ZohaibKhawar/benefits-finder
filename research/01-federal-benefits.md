# Federal benefits and credits (apply in every province)

Researched 2026-10-18. Benefit year = July 2026 to June 2027, based on the **2025** tax return,
unless it says otherwise. "Official" = read on canada.ca. "Secondary" = news or tax-prep sites; check
on canada.ca before the app shows the number.

The single most important fact for the app: **almost everything below needs a filed Canadian tax
return**, even with zero income. "File your taxes" is the first item on every results page.

---

## 1. Canada Groceries and Essentials Benefit (CGEB), formerly the GST/HST credit

- **What changed:** The GST/HST credit was renamed the CGEB in July 2026. Same rules, same structure,
  but amounts went up **25% for five years (2026 to 2031)**. Official.
- **One-time top-up:** paid June 5, 2026, equal to 50% of the 2025-26 GST/HST credit. Already paid.
  Don't show it as something to apply for. Official (ESDC news, April 2026).
- **Max amounts, July 2026 to June 2027 (official):**
  - Single: up to **$679**
  - Married or common-law: up to **$890**
  - Each child under 19: up to **$234**
  - Previous year (2025-26) was $533 / $698 / $184.
- **Who is eligible (official):**
  - 19 or older. Under 19 only if you have or had a spouse or common-law partner, or are or were a
    parent living with your child. First payment comes on the next payment date after the 19th birthday.
  - Resident of Canada for tax purposes the month before the payment and at the start of the payment month.
- **Income limits, 2025 base year (official table).** Adjusted family net income (AFNI) must be under:

  | Family | No kids | 1 kid | 2 kids | 3 kids | 4+ kids |
  |---|---|---|---|---|---|
  | Single (or single parent) | $60,012 | $68,912 | $73,592 | $78,272 | $82,952 |
  | Married / common-law | $64,232 | $68,912 | $73,592 | $78,272 | $82,952 |

- **AFNI** = line 23600 (you + spouse) minus UCCB and RDSP income (lines 11700, 12500) plus amounts
  repaid (lines 21300, 23200). The same definition is used by CCB, CDCP and others, so the app can ask
  for "net income (line 23600)" once and reuse it.
- **How to get it:** file a tax return. **Newcomers** apply with form **RC151** (or through the CCB
  application RC66 if they have kids). Students who are residents for tax purposes, including many
  international students, can get it.
- **Paid:** quarterly (July, October, January, April). Next: January 2027.
- **Exact phase-in/phase-out formula (to confirm):** the old GST credit had a single supplement that
  phased in at 2% of net income above about $11,000, and the whole credit reduced by 5% of AFNI above
  about $45,000. The 2026-27 numbers are on the CRA "payments chart" page, which I could not read in
  this pass. For the MVP, show "up to $679" and the income cut-off instead of an exact estimate.
- Links:
  - https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-groceries-essentials-benefit.html
  - Who is eligible: .../canada-groceries-essentials-benefit/who-eligible.html
  - How much: .../canada-groceries-essentials-benefit/how-much.html
  - New residents: .../canada-groceries-essentials-benefit/get-benefit.html
  - Guide RC4210: https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/rc4210.html
  - Finance backgrounder: https://www.canada.ca/en/department-finance/news/2026/01/the-new-canada-groceries-and-essentials-benefit.html

## 2. Canada Workers Benefit (CWB), line 45300

- **What it is:** refundable tax credit for people who work and earn a low income. Two parts: basic
  amount and disability supplement. Claimed on **Schedule 6** with the tax return. Part can be paid in
  advance (Advance CWB, three payments a year).
- **2025 tax year amounts (claimed in spring 2026). Official via search summary of CRA page:**
  - Single: max **$1,633**, reduced above AFNI **$26,855**, zero above **$37,742**.
  - Family: max **$2,813**, reduced above **$30,639**, zero above **$49,393**.
  - Disability supplement (single): max **$843**, phases out above $37,740, ends above $43,360.
  - Different amounts in Quebec, Nunavut and Alberta (not relevant for Ontario).
- **Who is eligible:**
  - Resident of Canada all year, 19+ on December 31 (or lives with a spouse, common-law partner or child).
  - **Student rule (key for this app):** NOT eligible if enrolled **full-time** at a designated
    educational institution for **more than 13 weeks** in the year, **unless** they have an eligible
    dependant on December 31. So most full-time university/college students do NOT get CWB, but
    part-time students and recent grads who work can. The questionnaire must ask this.
  - Must have working income (about $3,000 minimum in past years; confirm current number).
  - Not in prison 90+ days, not a diplomat (old rules; confirm).
- Link: https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-workers-benefit.html

## 3. Canada Child Benefit (CCB)

- **Official, July 2026 to June 2027:**
  - Under 6: **$8,157/year ($679.75/month)** per child
  - 6 to 17: **$6,883/year ($573.58/month)** per child
  - Full amount if AFNI under **$38,237**.
  - Reduction between $38,237 and $82,847: 7% (1 child), 13.5% (2), 19% (3), 23% (4+) of income over $38,237.
  - Above $82,847: $3,123 / $6,022 / $8,476 / $10,260 plus 3.2% / 5.7% / 8% / 9.5% of income over $82,847.
  - Child Disability Benefit: up to **$3,480/year ($290/month)** per child eligible for the DTC.
- This is exact enough to build a real estimator.
- **Who:** primary caregiver of a child under 18 who lives with them, resident for tax purposes, and
  the parent or spouse is a citizen, PR, protected person, or **temporary resident who has lived in
  Canada for the previous 18 months and has a valid permit in the 19th month** (other than permits that
  say "does not confer status"), or an Indigenous person under the Indian Act. (Long-standing rule;
  confirm wording on canada.ca.)
- **Newcomers apply with RC66** (+ RC66SCH status and income schedule). Also gets them the CGEB and
  the **Ontario Child Benefit** automatically.
- Link: https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-child-benefit-overview.html
- Calculation page: https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-child-benefit-overview/canada-child-benefit-we-calculate-your-ccb.html

## 4. Canadian Dental Care Plan (CDCP)

- **Official (page updated 2026-09-22). All four required:**
  1. No access to private dental insurance (through work, a family member's work, a pension, a
     **professional or student organization**, or bought privately). Tip: T4 box 45 = "1" means no access.
     **Student association dental plans count as access**, so many college/university students are out
     unless they opted out of their student plan (confirm whether opting out before applying is allowed).
  2. You (and spouse) filed a tax return for the previous year.
  3. Adjusted family net income **under $90,000**.
  4. Resident of Canada for tax purposes.
- Public dental coverage (Ontario Works, ODSP, Healthy Smiles) doesn't disqualify you.
- Open to all ages now (since 2025).
- **Co-pays (secondary):** under $70,000 = no co-pay; $70,000 to $79,999 = 40%; $80,000 to $89,999 = 60%.
- **Newcomers:** need at least one filed Canadian return first. Someone who arrived in 2026 may have
  to wait until they file their 2026 return in early 2027 (secondary).
- Links: https://www.canada.ca/en/services/benefits/dental/dental-care-plan.html
  , qualify: .../dental-care-plan/qualify.html , apply: .../dental-care-plan/apply.html

## 5. Canada Disability Benefit (CDB)

- Started July 2025. **$204.20/month max** for July 2026 to June 2027 ($2,450/year), indexed 2.1%.
  (Secondary; $200/month the year before.)
- Ages 18 to 64, must have the **Disability Tax Credit (DTC)** approved, must file taxes.
- Reduced by 20 cents per dollar of income over $23,000 (single) or $32,500 (couple); part of working
  income exempt (official regulations summary).
- One-time **$150** supplemental payment from September 2026 to help with the cost of getting the DTC form
  filled in. Automatic.
- In Ontario, ODSP does not claw back the CDB (Ontario announced it would exempt it; confirm).
- Link: https://www.canada.ca/en/services/benefits/disability/canada-disability-benefit.html

## 6. Disability Tax Credit (DTC)

- Non-refundable credit, but it is the **gateway** to CDB, Child Disability Benefit, CWB disability
  supplement, RDSP grants and bonds, and the Canada Student Grant for students with disabilities.
- Needs form **T2201** certified by a medical practitioner.
- Link: https://www.canada.ca/en/revenue-agency/services/tax/individuals/segments/tax-credits-deductions-persons-disabilities/disability-tax-credit.html

## 7. Federal student aid (paid through OSAP in Ontario)

- **Canada Student Grant for Full-Time Students:** up to **$4,200/year ($525 per month of study)**
  through the end of 2026-27 (official page; amount noted as "pending government approval").
  - Family of one: full grant below **$38,474** gross family income; none at or above **$69,987**.
  - **New from August 1, 2026:** most students at **for-profit private career colleges** can no longer
    get the full-time grant (exemptions exist). The app must ask "public or private school?".
- Part-time students: up to **$2,520/year**.
- Students with disabilities: **$2,800/year** (plus equipment/services grant up to $20,000).
- Full-time students with dependants: up to **$280 per dependant per month**.
- **Canada Student Loans are interest-free** permanently (federal part, since April 2023).
- **Repayment Assistance Plan (RAP):** no payment if income is under the threshold; about **$3,788/month
  for a family of one** from April 1, 2026 (official page; one secondary site said $3,866, confirm).
  Reapply every 6 months.
- You apply for the federal grant **through OSAP**, not separately.
- Links:
  - https://www.canada.ca/en/services/benefits/education/student-aid/grants-loans/full-time.html
  - https://www.canada.ca/en/employment-social-development/services/student-financial-aid/student-loan/student-loans/student-loans-repayment-assistance-plan.html

## 8. Student tax credits and deductions (federal)

- **Tuition tax credit:** 15% of eligible tuition (over $100 per institution), line 32300, Schedule 11,
  from form **T2202** (the school issues it). Unused amounts carry forward forever. Up to **$5,000** of the
  current year's tuition can be transferred to a spouse, parent or grandparent. **Ontario has no
  provincial tuition credit since 2017**; only legacy carry-forwards remain. International students
  with tuition at a Canadian school can claim it too.
- **Interest paid on student loans:** credit for interest on government student loans (line 31900).
  Rarely matters now since federal loans are interest-free, but the Ontario part of OSAP still charges interest
  (prime + 1%, confirm).
- **Moving expenses (line 21900):** students can deduct moving costs to go to school full-time if
  they moved at least 40 km closer, but only against scholarship/research grant income included in
  income; or against job income when moving for work or a summer job.
- **Scholarships and bursaries** are usually tax-free for full-time students (scholarship exemption).
- **Canada Training Credit:** builds **$250/year**, lifetime max **$5,000**, ages 25 to 64, needs
  working income of about $12,000+ and net income under about $177,000 (2025 numbers, secondary).
  Refundable, claimed for tuition. Shown on the Notice of Assessment.
- Links:
  - https://www.canada.ca/en/revenue-agency/services/tax/individuals/segments/students.html
  - https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-32300-your-tuition-education-textbook-amounts.html

## 9. Savings programs worth flagging

- **Canada Learning Bond (CLB):** for kids born 2004 or later in low-income families. $500 first year
  plus $100 each later eligible year to age 15, max **$2,000**, no contribution needed. Needs an RESP
  and a SIN. Can apply until **age 21** (adult can apply themselves at 18 to 20). Income limit 2025-26:
  $57,375 for 1 to 3 kids (secondary). **Big one for students 18 to 20 from low-income families who
  never got it.**
- **First Home Savings Account (FHSA):** $8,000/year, $40,000 lifetime, tax-deductible in, tax-free out
  for a first home. Newcomers and students qualify once 18 and a resident.
- **RDSP grants and bonds:** for people with the DTC, up to $3,500/year grant and $1,000/year bond.
- Link CLB: https://www.canada.ca/en/employment-social-development/services/learning-bond.html

## 10. Things that ENDED (the app must not list them)

- **Canada Carbon Rebate / Climate Action Incentive:** final payment April 2025. Ended.
- **GST/HST credit name:** renamed to CGEB July 2026 (same program).
- **Ontario tuition and education credits:** ended 2017.
- **Canada Emergency benefits (CERB, CRB etc.):** ended; only repayments remain.

## Sources used in this file

- [CGEB overview](https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-groceries-essentials-benefit.html)
- [CGEB who is eligible](https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-groceries-essentials-benefit/who-eligible.html)
- [CGEB how much](https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-groceries-essentials-benefit/how-much.html)
- [ESDC news on the June 5 top-up](https://www.canada.ca/en/employment-social-development/news/2026/04/secretary-of-state-mclean-highlights-canada-groceries-and-essentials-benefit-top-up-coming-june-5.html)
- [Money.ca on the rename](https://money.ca/managing-money/taxes/canada-groceries-essentials-benefit-gst-hst-credit-renamed-2026)
- [CWB line 45300](https://www.canada.ca/canada-workers-benefit)
- [CCB calculation](https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-child-benefit-overview/canada-child-benefit-we-calculate-your-ccb.html)
- [CDCP qualify](https://www.canada.ca/en/services/benefits/dental/dental-care-plan/qualify.html)
- [CDB regulations summary](https://www.canada.ca/content/dam/esdc-edsc/documents/programs/disability-benefit/summary-regulations/summary-of-the-canada-disability-benefit-regulations-en.pdf)
- [Canada Student Grant full-time](https://www.canada.ca/en/services/benefits/education/student-aid/grants-loans/full-time.html)
- [Repayment Assistance Plan](https://www.canada.ca/en/employment-social-development/services/student-financial-aid/student-loan/student-loans/student-loans-repayment-assistance-plan.html)
- [TaxTips tuition transfer](https://www.taxtips.ca/filing/students/transfercarryforward.htm)
- [TaxTips Canada Training Credit](https://www.taxtips.ca/filing/canada-training-credit.htm)
- [Fidelity on the Canada Learning Bond](https://www.fidelity.ca/en/insights/articles/can-learning-bond-explained/)
- [Canada Education Savings Act s.6](https://laws-lois.justice.gc.ca/eng/acts/C-3.6/section-6.html)
