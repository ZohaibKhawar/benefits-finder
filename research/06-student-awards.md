# Scholarships and bursaries for Ontario students (Phase 8)

Researched 2026-10-25, every fact read on the official page itself (not search summaries). Data is in
`data/ontario_schools.yaml` and `data/student_awards.yaml`; matching is in `finder/awards.py`.

## Rule for links

Only governments, the schools themselves, and long-running charities and foundations. Every award link's
host has to be on `trusted_domains` in `student_awards.yaml` (with who runs it), and every school link has
to be on that school's own domain; `tests/test_awards.py` fails otherwise, including on lookalike hosts.
Left out on purpose: aggregator and "scholarship search" sites (ScholarshipsCanada is linked by
ontario.ca but blocks scripts and is ad-funded), contest-style "win $1,000" sites, and anything that
asks for a fee or a SIN to apply.

## Ended or closed, never list

- **TD Scholarships for Community Leadership**: ended. TD's page: no new applications for 2026 and beyond.
- **Apprenticeship Incentive Grant and Apprenticeship Completion Grant**: closed March 31, 2025 (canada.ca).
- **NEADS National Student Awards**: merged into a new program whose grant funding had run out for Fall 2026.

## Universities: automatic entrance scholarships (students straight from high school)

Admission average is the top 6 Grade 12 U/M courses unless noted. "First year / total".

| School | Tiers | Source |
|---|---|---|
| Algoma | 95: $4,000/$16,000 · 90: $3,000/$12,000 · 85: $2,500/$10,000 · 80: $1,500/$6,000 | algomau.ca entrance-scholarships |
| Brock (2026 domestic) | 95: $5,500/$7,000 · 90: $3,500/$5,000 · 85: $1,500/$3,000 ($500 renewals at 80%) | brocku.ca/safa/2026-future-students |
| Carleton | 95: $3,000/yr · 90: $2,000/yr · 85: $1,000/yr, 4 years, renew at 10.0 GPA; based on grades sent with the application | carleton.ca/awards entrance-scholarships |
| Guelph (citizens, PR) | 95: $2,000 · 90: $1,000, first year only | uoguelph.ca scholarships-bursaries |
| Lakehead | 95: $4,000/yr (free tuition at 95% final) · 90: $2,500/yr · 85: $1,250/yr · 80: $750/yr | lakeheadu.ca studentcentral |
| Nipissing | guaranteed at 80% by June 30, amounts not shown on the page we could read | nipissingu.ca (blocks scripts; read with WebFetch) |
| OCAD U (Ontario high school, citizens/PR/protected) | 95: $3,000 · 90: $2,000 · 85: $1,000 | admissions.ocadu.ca funding-options |
| Ontario Tech | 85%+, out of high school under 18 months; amounts not on the official FAQ | registrar.ontariotechu.ca FAQ |
| uOttawa | 95: $3,000 · 90: $2,000 · 85: $1,000 (page updated Sept 24, 2026) | uottawa.ca scholarships-awards-overview |
| Queen's | grade-based admission scholarships from 90%; amounts vary | queensu.ca automatic-awards |
| TMU (2027-28, Canadian high school) | 95: $3,000/yr · 90: $1,500/yr · 86: $750/yr, 4 years | torontomu.ca/admissions/scholarships-awards |
| Trent | 95: free first-year tuition ($6,241) + $4,000 x 3 = $18,118 · 90: $3,000 x 4 · 85: $2,000 x 4 · 80: $1,500 x 4 | trentu.ca entrance-scholarships |
| U of T | about 900 awards of $10,000 to the top averages (Scholars Program), domestic and international | future.utoronto.ca |
| Waterloo | 95: $2,000 + up to $3,000 later · 90: $2,000 · 85: $1,000, one-time | uwaterloo.ca/future-students/financing/scholarships |
| Western | 92: $2,500 + $1,000 abroad · 90: $1,500 + $1,000 abroad; top 250 get $6,000 + $2,000 | registrar.uwo.ca admission scholarship program |
| Laurier (Sept 2027+, domestic) | 95: $4,000 · 90: $3,000 · 85: $2,500 (BBA from 90%); international $5,000/$6,000 | wlu.ca entrance-scholarships |
| Windsor | 95: $2,000 x 8 terms · 90: $1,250 x 8 · 85: $1,000 once; renew at 85% | uwindsor.ca/studentawards/entering-students |
| York | 95: $3,500 · 90: $2,000 · 85: $1,500 · 80: $1,000, renewable at 8.0 GPA ($4,000-$14,000) | futurestudents.yorku.ca/scholarships-incoming-students |
| UOF (citizens, PR, OSSD) | $12,000 over four years for every bachelor's except the B.A./B.Éd. ($18,000) | uof.ca bourses-et-aide-financiere |

No published automatic table: Laurentian (page blocks scripts; secondary sources conflict), McMaster
(top 10% of each faculty, cut-offs change yearly), Hearst, NOSM U. Colleges: every college's own awards
page; none has a single published table by average (some degree programs do).

## Outside awards

| Award | Key facts | Source |
|---|---|---|
| Ontario First Generation Bursary | $1,000-$3,500; parents never in post-secondary anywhere; first-entry program; OSAP citizenship/residency; need; no OSAP application needed | osap.gov.on.ca PRDR019247 |
| Indigenous Student Bursary | typically $1,000-$3,500, up to $6,500 with remote travel; self-identified; need | osap.gov.on.ca POCONT1_109272 |
| First Nations Resource Development Scholarship | full program cost + $2,500 (2026-27); approved resource programs; FN community in Ontario | osap.gov.on.ca POCONT1_110873 |
| Post-Secondary Student Support Program | First Nations registered under the Indian Act, through the band | sac-isc.gc.ca |
| Inuit Post-Secondary Education Strategy | land-claim beneficiaries, through Inuit organizations / ITK | sac-isc.gc.ca |
| MNO Métis Student Bursary Program | 43 institutions; verified MNO citizen; citizen/PR; 12 months in Ontario; need | metisnation.org |
| Living and Learning Grant | up to $2,000 a semester; former youth in care 18-26; automatic with full-time OSAP | ontario.ca (OSAP under-represented learners; youth in child welfare) |
| Application Fee Reimbursement | fees for up to 5 university + 5 college choices; extended society care, any age | ontario.ca |
| BSWD + CSG-DSE | up to $2,000 (Ontario) and $20,000 (Canada) for disability services and equipment | osap.gov.on.ca POCONT1_109289 |
| Ontario Graduate Scholarship | $5,000 a term, up to $15,000 a year, through the school's grad office | ontario.ca student-loans-grants-scholarships-and-bursaries |
| CGRS Master's | $27,000 for 12 months; citizen/PR/protected; Dec 1 before 8 p.m. ET | nserc-crsng.canada.ca |
| USRA | $6,000 + school top-up, 14-16 weeks; citizen/PR/protected; B- normally; SSHRC and CIHR USRAs currently only for Black student researchers | nserc-crsng.canada.ca (French page) |
| Explore | $4,000 (16+), 31-33 days spring/summer; citizen/PR; student in the past year | canada.ca |
| Indspire Building Brighter Futures | deadlines Aug 1, Nov 1, Feb 1; one application | indspire.ca |
| Loran Award | ~$150,000 over 4 years; 88% (Grade 10-12 weighted); citizen/PR; closed Oct 15, 2026 for 2027 | loranscholar.ca |
| Schulich Leader | $120,000 engineering / $100,000 science, tech, math; Canadian citizen; school nominee by Jan 27, 2027, application by Feb 17, 2027 | schulichleaders.com/faq |
| Schulich Builders | $20,000 (1-year certificate) / $40,000 (2-year diploma); citizens; nominations by March 31, 2027; 8 colleges | schulichbuilders.com |
| Terry Fox Humanitarian Award | $7,000 a year, up to $28,000; citizen/PR; opens Nov 1, closes Dec 1 | terryfoxawards.ca |
| BBPA National Scholarship Program | $1,000-$7,000 a year; Black students 17-30; citizen/PR/protected or permit | bbpa.org/how-to-apply (window posted was 2024) |
| Canadian Nurses Foundation | $750-$10,000; citizen/PR; opens Jan 1, closes mid-March | cnf-fiic.ca |
| Rhodes (Canada) | citizen/PR; 18-23 on Oct 1; GPA 3.7/4.0 benchmark; certification Sept 28, 2026 | rhodeshouse.ox.ac.uk |
| Search lists | ISC Indigenous Bursaries Search Tool; DND/CAF Ombudsman list for military families; EduCanada for international students | sac-isc.gc.ca, canada.ca, educanada.ca |

## Grade scales

Converted to the bottom of each letter grade so nobody is told they qualify when they don't:
4.0 (A 85, A- 80, B+ 77...), 4.33 (A+ 90, A 85, A- 80...), York 9-point (A+ 90, A 80, B+ 75...),
uOttawa 10-point (A+ 90, A 85, A- 80, B+ 75...), 12-point at Carleton, McMaster and Laurier (A+ 90, A 85,
A- 80, B+ 77...). The results page says what we read the grade as.

## Still to confirm

1. Laurentian's entrance table (official page blocks scripts; open it in a browser).
2. Nipissing's and Ontario Tech's amounts by average.
3. BBPA's 2027 application window.
4. Whether OGS still takes some international students at every school (each school's rules).
