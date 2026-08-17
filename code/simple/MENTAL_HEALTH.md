# Serious mental illness: specification and sources

Every parameter, what disciplines it, and what is still unjustified. Written
because the first implementation had five parameters set by guesswork — the same
failure R1 attacked κ_cons for.

---

## 1. What the state represents

**Serious mental illness (SMI), not "any mental illness."** This matters. AMI
covers roughly 23% of US adults and includes mild anxiety and depression; SMI is
about 5.5% and is defined by substantial functional impairment. It is SMI that
drives chronic homelessness and disability receipt, and AMI at 23% would put a
quarter of the population in a state that cuts productivity by half.

This follows İmrohoroğlu and Zhao (2022), on whose framework the paper builds.
Their structure is the reason to model it this way at all: in their model **labour
market shocks generate short homeless spells while health shocks generate chronic
homelessness**, and expanded means-tested disability income is the effective
policy for the chronic group. Homelessness driven purely by income risk is
transitory; the persistent tail needs a persistent state.

---

## 2. Parameters

| Parameter | Value | How it is set |
|---|---|---|
| `smi_prevalence` | 0.055 | **External.** SMI among US adults, NSDUH 2023 (5.5–5.6%, ≈14.6m people) |
| `mh_onset` | derived | **Not free.** `mh_recover · p/(1−p)`, so prevalence stays at its data value while persistence is calibrated |
| `mh_recover` | calibrated | Targets **SMI share of the homeless = 25%** |
| `kappa_ue_m` | calibrated | Targets **employment rate given SMI = 30%** |
| `prod_pen_m` | calibrated | Targets **homeless income / average = 19.1%** |
| `kappa_phi_m` | 2.50 | **External.** Standardised mortality ratios for SMI are roughly 2–3 |
| `disab_income` | 0.25 | **External, approximate.** Disability transfer for the non-employed with SMI |
| `rec_mult_m` | 0.50 | **Still unjustified** — see §4 |
| `mh_b_ratio` | 0.25 | **Still unjustified** — see §4 |

### The identifying moments

**SMI share of the homeless — 25%.** Gutwinski et al. (2021, *PLOS Medicine*)
pool 39 studies of homeless people in high-income countries (N = 8,049) and find
**12.4% schizophrenia-spectrum** and **12.6% major depression**, so about a
quarter carry a severe disorder, against 5.5% in the adult population — a
relative risk near **4.5**. This is what identifies persistence: only a
sufficiently sticky SMI state lets the SMI population accumulate in
homelessness at that ratio.

The same study reports **any current mental disorder at 76.2%**, alcohol use
disorder at **36.7%**, drug use disorder at **21.7%**. Two things follow. First,
the model's binary SMI state cannot and should not try to reach 76% — that
figure includes mild conditions the state does not represent. Second, the
paper's old "addiction rate of homeless = 37%" target sat almost exactly on the
*alcohol* figure, not the drug figure, and the paper models drug use.

**That has been settled: the figure is 21.7%, the drug use disorder number.**
The note carries it, in the calibration section under "Three targets that were
wrong and are now right", and the full model has it as
`sud_share_of_homeless = 0.217`. It is an untargeted validation moment, not a
target. Do not re-open it — this paragraph used to argue for a change that has
since been made.

**Employment rate given SMI — 30%.** Employment runs 22–40% for
high-disability diagnoses, and roughly a fifth of people with schizophrenia are
in work (12% full-time). For any mental illness the range is 48–73%, against
76–87% for those without. 30% is the midpoint of the high-disability range.

**Homeless income relative to average — 19.1%.** R1 comment 2(c)(i). The
productivity penalty is what generates *employed* households poor enough to be
priced out, which an unemployment effect alone cannot do.

---

## 3. What SMI affects, and how it interacts

| Channel | Direction |
|---|---|
| Productivity while employed | ×`prod_pen_m` |
| Job finding / separation | ×`kappa_ue_m` / ÷`kappa_ue_m` |
| Mortality | ×2.5 |
| SUD recovery hazard | ×`rec_mult_m` |
| Drug temptation (`b`) | lower ⇒ higher marginal utility of first units |
| Income when not employed | disability transfer |

**Interaction with drug use — yes, both margins.** Lower `b` raises *initiation*
(self-medication); a lower recovery hazard raises *persistence*. So SMI both
causes drug use and traps people in it. This is exactly R1 comment 1(a): "mental
health contributing to drug use and addiction as well as homelessness."

**Interaction with income — yes, three ways.** Directly through the productivity
penalty, indirectly through employment, and partially offset by the disability
transfer.

**Interaction with homelessness — indirect, through income.** SMI has no direct
effect on housing preferences or access.

**Adding disability income matters and was missing.** Roughly two-thirds of
people with schizophrenia receive federal disability insurance. Giving the
non-employed with SMI zero income overstated their homelessness badly. It is
also the policy margin İmrohoroğlu and Zhao find effective for the chronically
homeless, so without it the model cannot speak to that comparison at all.

---

## 4. What is still not justified

Be explicit about this rather than let it pass into a draft.

**`rec_mult_m = 0.50`** — that SMI halves the SUD recovery hazard. Direction is
certain, magnitude is invented. Needs either a treatment-outcomes source on
co-occurring disorders or internal calibration against a comorbidity moment.

**`mh_b_ratio = 0.25`** — the self-medication channel. Should be calibrated to
the **co-occurring SUD rate among adults with SMI**, which is the natural moment
and exists in the SAMHSA NSDUH detailed tables (co-occurring SMI and SUD). I
could not retrieve the exact figure — samhsa.gov and nimh.nih.gov are blocked
from this environment. **This is the one number worth pulling manually.**

**`disab_income = 0.25`** — order of magnitude only. Should come from average
SSI/SSDI benefits relative to mean income.

**SMI is exogenous.** It does not respond to drug use, homelessness, or income.
The epidemiological evidence on reverse causation from homelessness to mental
illness is substantial, so this is a genuine restriction and should be stated as
one rather than left implicit.

**No SMI-specific treatment margin.** Treatment in the model raises the SUD
recovery hazard only; there is no mental-health treatment. Given that "Treatment
First" programmes in practice treat both, this is a real gap.

---

## 4a. The bug that adding the state introduced, and how it hid

Worth recording separately, because it was invisible in every output and it
corrupted exactly the moments the SMI parameters are calibrated to.

The joint state folds employment, SMI and the SUD into one index,
`index = 3*number_of_smi_states*d + 3*m + e`. Tests that used to ask "is this
household employed?" were written for the six state grid, where the employed
states are `{1, 4}`, as

    index == 1  .OR.  (sud_of(index) == 1 .AND. emp_of(index) == 1)

At one SMI state that is exactly `{1, 4}` and correct. At two states the employed
states are `{1, 4, 7, 10}` and the test returns `{1, 7, 10}`. The state it misses
is index 4: **employed, carrying SMI, no SUD** — which is most of the employed
SMI population, since most people with SMI do not have a co-occurring drug
disorder.

That household was handed **zero labour income** by `calculate_income` and
counted as not working everywhere else. So the employment rate given SMI, the
homeless income share, and the SMI share of the homeless — the three moments that
identify `mh_recover`, `kappa_ue_m` and `prod_pen_m` — were all being measured
against a population a quarter of whose employed members had been zeroed out.
Eighteen tests were wrong in this way and the model ran and printed numbers
throughout.

**Why the existing check did not catch it.** `verify_index_map` compares the
accessor forms against the old threshold forms, and it skips when
`number_of_smi_states /= 1`, on the correct reasoning that the old forms are
wrong at two states by construction. The composite tests were never rewritten,
so the one configuration where they were wrong was the one configuration the
check declined to look at.

The fix is that every such test now goes through `emp_of` alone, and
`verify_index_map` has a second block that runs at **every** grid size and checks
**cardinalities** rather than membership: any predicate that partitions on
employment must split the grid into three equal blocks whatever the SMI grid
size, so a test that forgets a state lands a block short. That check fails on the
old forms at two states, which is the test that was missing.

---

## 5. What was wrong before

For the record, since these numbers appeared in earlier output:

| | Before | Now |
|---|---|---|
| Ergodic share | 9.1% (between SMI and AMI, matching neither) | 5.5%, NSDUH |
| Mortality multiplier | 1.30, invented | 2.50, SMR range |
| Employment multiplier | 0.65, invented | calibrated to a 30% employment rate |
| Income when not employed | zero | disability transfer |
| Homeless SMI share | not measured | targeted at 25%, Gutwinski et al. |
| Persistence | fixed at 10%/yr, invented | calibrated, prevalence held fixed |

---

## Sources

- [Gutwinski et al. (2021), *PLOS Medicine* — prevalence of mental disorders among homeless people in high-income countries](https://journals.plos.org/plosmedicine/article?id=10.1371%2Fjournal.pmed.1003750) ([PubMed](https://pubmed.ncbi.nlm.nih.gov/34424908/), [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8423293/))
- [İmrohoroğlu and Zhao (2022), "Homelessness" — SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4308222)
- [NIMH — Mental Illness statistics (SMI prevalence)](https://www.nimh.nih.gov/health/statistics/mental-illness)
- [SAMHSA — 2023 NSDUH Annual National Report](https://www.samhsa.gov/data/sites/default/files/reports/rpt47095/National%20Report/National%20Report/2023-nsduh-annual-national.htm)
- [Employment Barriers for Persons With Psychiatric Disabilities, *Psychiatric Services* (2006)](https://psychiatryonline.org/doi/10.1176/ps.2006.57.10.1391)
- [Employment Status of People With Mental Illness, *Psychiatric Services* (2014)](https://psychiatryonline.org/doi/10.1176/appi.ps.201300335)

Figures above are from search-result summaries; the primary-source domains are
blocked from this environment, so verify the exact numbers against the papers
before they go into the draft.
