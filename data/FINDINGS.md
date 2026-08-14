# What the data files say, and what has to change because of them

Six files arrived on 14 Aug 2026. This is what is in them, what it implies for
the calibration, and which decisions are still open. Nothing here is wired into
`calibrate.f90` yet — the changes are batched deliberately, because each new
target costs a full calibration restart.

Sources, all in `data/` or reproducible from the scripts there:

| file | source | script |
|---|---|---|
| `us_life_table.csv` | SSA period life table `oact/STATS/table4c6` | `make_life_table.py --ssa-xlsx` |
| `us_housing_dist.csv` | ACS B25042, Tenure by Bedrooms, 2023 | `make_housing_dist.py` |
| — | NBER w32582, Abramson & Van Nieuwerburgh (2024) | read directly |
| — | HUD Picture of Subsidized Households, 2023 | read directly |
| — | HUD PIT counts by state, 2007–2024 | read directly |
| — | NSDUH 2023 detailed tables | `nq.py` in scratchpad |

---

## 1. The homelessness rate target is too high — DECISION NEEDED

The homeless state is literal homelessness (shelters and the street, not
doubling up). HUD's point-in-time count is *the* measure of that.

| year | PIT count | % of population | chronic | unsheltered |
|---|---:|---:|---:|---:|
| 2024 | 771,480 | **0.229%** | 0.050% | 35.5% |
| 2023 | 653,104 | 0.195% | 0.046% | 39.3% |
| 2022 | 582,462 | 0.175% | 0.042% | 40.1% |
| 2020 | 580,466 | 0.175% | 0.036% | 38.9% |
| 2019 | 567,715 | 0.173% | 0.032% | 37.2% |
| 2016 | 549,928 | 0.170% | 0.027% | 32.1% |

**The current target of 0.30% is above every year on record**, including 2024's
all-time high. 2021 is depressed by pandemic counting disruption and should be
ignored.

Options:
- **0.229%** — 2024, the most recent, and the year the other files describe.
- **~0.19%** — a pre-2022 average, arguably the steady state the model represents.
- Keep 0.30% and document it as something other than PIT literal homelessness,
  which contradicts the concept decision.

There is a real conceptual wrinkle either way. The model period is a year and
the homeless state persists for a full period, so a household in `h_1` is
homeless for a year. Most actual spells are far shorter. The PIT stock is the
closer analogue of the two, but the model cannot represent a three-month spell
at all, and that is worth a sentence in the paper rather than a silent choice.

### Abramson and Van Nieuwerburgh's 0.6% is not this number

They put the literally homeless at 0.6% of the population, which is **2.6× the
2024 PIT count**. Almost certainly an annual-flow rather than point-in-time
measure. This does *not* disturb `chi_H`: their \$2,500 is a per-household-month
rate, so \$30,000 per homeless-household-year holds regardless of how many
households there are. But a referee comparing total fiscal outlays will find
ours roughly half theirs, and the reason is the rate concept, not the cost.

---

## 2. The SUD definition is not written down — and it matters

NSDUH 2023, aged 26+ (the model's population), past-year disorder:

| measure | rate |
|---|---:|
| Substance use disorder, all (incl. alcohol) | 16.6% |
| Drug use disorder (incl. marijuana) | 8.6% |
| Marijuana use disorder | 5.5% |
| Prescription psychotherapeutics | 2.9% |
| Methamphetamine | 0.8% |
| Cocaine | 0.5% |
| Heroin | 0.3% |

**PROVENANCE CONFIRMED.** The target is **moderate/severe drug use disorder at
ages 26+**, reproduced exactly from `NSDUH_2024.dta` using `svyrdudany` (1 mild,
2 moderate, 3 severe, 4 none) weighted by `analwt2_c` over `age3 >= 7`:

| concept | rate |
|---|---:|
| any drug use disorder (severity 1–3) | 8.90% |
| **moderate/severe (severity 2–3)** | **3.68%** |

My earlier guess that it was "drugs excluding marijuana" was wrong — it is a
severity restriction, not a substance restriction. The definition still needs
writing down: the gap between 3.68% and NSDUH's headline 16.6% is large enough
that a referee assuming the published figure will think the model is off by a
factor of four.

---

## 3. RESOLVED: the SUD to employment channel was 2.25 times too strong

The full NSDUH 2024 public use file settles it. Ages 26+, unemployment over the
labour force, weighted by `analwt2_c`, using `svyrdudany` for severity and
`irwrkstat` for employment:

| group | unemployment rate |
|---|---:|
| everyone | 6.65% |
| no drug use disorder | 6.04% |
| any drug use disorder | 12.72% |
| **moderate or severe drug UD** | **16.25%** |

**The model targeted 26.90%, which had no provenance.** Against an overall rate
of 4.9% that implies a relative risk of 5.49; the data says 2.44. Target
corrected to 16.25%.

Two checks that the number is right. The table based estimate in the previous
version of this section, backed out of tables 5.4A and 5.4B by Bayes, gave
12.52% for any drug use disorder against 12.72% in the microdata, so that method
was sound. And the ordering is monotone in severity, 6.04 to 12.72 to 16.25,
which is what it should be.

**Why this matters beyond one moment.** R1's rival hypothesis is that the SUD to
employment channel does the work rather than mortality. The model was biased
toward that reading on both sides at once: this channel 2.25 times too strong,
and the mortality channel running at roughly a fifth of its measured strength
before the life table and the age varying multipliers went in. Correcting both
moves against R1, and now from measurement rather than assertion.

Also measured from the same file, ages 26+:

| moment | data | model target |
|---|---:|---:|
| SUD income / average, moderate or severe | 71.1% | 68.7% |
| labour force participation, moderate or severe | 65.8% | untargeted |
| labour force participation, no disorder | 61.5% | untargeted |

The income ratio nearly hits its target unprompted, which is a genuine check on
`prod_pen_d`. Participation is slightly HIGHER among those with a disorder,
which is worth knowing: the SUD penalty runs through unemployment conditional on
participating, not through dropping out.

Unemployment given moderate or severe drug UD also falls with age, 21.6% at 26
to 29, 15.5% at 35 to 49, 10.7% at 50 to 64, which is the same shape as the
mortality multipliers.

---

## 3b. TEDS-A 2022, the treatment admission joint distribution

999,619 admissions aged 25+. Selected on entering publicly funded treatment, so
useful for ratios rather than levels.

| | |
|---|---:|
| homeless at admission | 14.5% |
| co-occurring psychiatric problem | 43.1% of those answering |
| unemployed | 30.8% |
| **among the homeless: unemployed** | **50.2%** |
| among the homeless: not in the labour force | 41.1% |
| among the homeless: working at all | 6.6% |

The last line is the useful one. Among people entering treatment who are
homeless, 6.6% work at all. That is a direct check on the model's homelessness
to employment penalty, and it is far more severe than the SUD penalty alone.

---

## 4. `kappa_r` validates almost exactly — no change

HUD Picture of Subsidized Households, 2023, US total:

- Average family expenditure: \$452/month
- Household income: \$18,483/year = \$1,540/month
- **Tenant contribution: 29.35%**, against the model's `kappa_r = 0.30`.

That is a direct hit on a parameter that was set by statute rather than fitted,
and it is worth reporting as validation.

Also from the same file, all usable as untargeted validation:

| statistic | value | bears on |
|---|---:|---|
| HUD expenditure | \$1,135/month | voucher size |
| Wages are the major income source | 24% | voucher-holder employment |
| Other sources (SS/SSI/DI) major | 67% | `di_coverage` |
| Head or spouse has a disability | 39% | `di_coverage` |
| Unit size 0–1 / 2 / 3+ bedrooms | 46 / 29 / 25% | housing choice given voucher |
| Same, all US households (B25042) | 13 / 24 / 63% | — |

Voucher holders are dramatically concentrated in small units, and only a quarter
of them have wages as their main income. Both are strong untargeted checks on
whether the model puts the right households into vouchers.

### A tension worth resolving: `prob_V`

Average months on the waiting list: **25**. Average months since moving in: 123.

`prob_V = 0.06` is an annual lottery hazard, implying an expected wait of 16.7
years, or 200 months — eight times the observed figure. The 25 months is
selected (it is measured among those who received a unit) and stock-sampled, so
it is a lower bound on the true wait. But a factor of eight is not explained by
selection alone, and `prob_V` is currently identified only by the recipients-to-
eligible stock ratio, which a long tenure can reproduce at almost any hazard.
The waiting time is the moment that separates them.

---

## 5. Housing grid — done

ACS B25042, occupied units, 2023, N = 131,332,360: **13.21 / 24.12 / 62.67%**
across {0,1}, {2}, {3+} bedrooms. Now targeted by `h_small` and `h_spread`;
the two housing-cost moments are demoted to untargeted validation.

All households, not renters: the model has no homeownership, housing is a pure
flow at `p_r h`, so an owner's analogue is imputed rent. The choice is worth
2.4× on the small bin (renters alone give 32.35%).

---

## 6. Survival — done

SSA period life table, ages 26–85, sexes combined by survivor weight. The
placeholder understated mortality badly: q at 85 was 0.045 against an actual
0.081. Closes R3 M1b.

---

## 10. The homelessness mortality penalty was five times too small

Baggett et al. (2013, JAMA Intern Med), Boston Health Care for the Homeless,
race-adjusted all-cause mortality rate ratios against the Massachusetts general
population:

| age | men | women |
|---|---:|---:|
| 25-44 | **8.6** (7.4-9.9) | **9.6** (7.4-12.4) |
| 45-64 | 4.5 (4.1-4.9) | ~4.5 (3.6-5.6) |
| 65-84 | 1.1 (0.9-1.4) | ~1.1 (0.7-1.8) |

`kappa_phi_h` was **1.6, flat across all ages**. That was wrong twice: five
times too small at prime ages, and the wrong shape. A constant multiplier large
enough to match the young implies a 41% annual death rate for a homeless
80-year-old.

Their ratio is the TOTAL for homeless adults, most of whom also have SUD, and
the model already carries a separate `kappa_phi_d = 6.9`. Using 9.1 directly
would stack the two and count SUD mortality twice, giving 59x. Netting out the
SUD composition,

    RR_total = kappa_phi_h * [ (1-s) + s*kappa_phi_d ],   s = 0.217

leaves **3.99 / 1.97 / 0.48**. The 65+ figure is floored at 1.0: read literally
it says homelessness protects the old, which is survivor selection rather than a
causal effect, and the model cannot represent selection on unobserved frailty.
Flooring understates the mortality channel rather than inventing a protective
one.

Now implemented as `kappa_phi_h_age(n_age)`.

Also from Baggett, usable as validation: drug overdose is 35% of deaths among
homeless 25-44 year olds, at rates 16 to 24 times the general population;
opioids are implicated in 81% of overdose deaths.

---

## 11. National homelessness by age, and system dynamics

PIT 2024. The 65+ column is named **"Over 64"**, which is why a first pass
stopped at 64.

| band | homeless | population | rate | **share of homeless** |
|---|---:|---:|---:|---:|
| 25-34 | 146,859 | 46,453,864 | 0.3161% | 26.0% |
| 35-44 | 153,849 | 45,539,224 | 0.3378% | 27.2% |
| 45-54 | 118,740 | 40,780,356 | 0.2912% | 21.0% |
| 55-64 | 104,007 | 41,661,725 | 0.2496% | 18.4% |
| 65-84 | 42,147 | 54,744,775 | 0.0770% | 7.5% |
| total | 565,602 | 229,179,944 | 0.2468% | 100% |

The rate peaks at 35-44 and collapses by a factor of 4.4 after 65, which is the
same selection story as the mortality ratios.

HUD System Performance Measures, national, give three more untargeted moments:

| measure | 2020 | 2022 | 2024 |
|---|---:|---:|---:|
| **returns to homelessness within 24 months** | 19.7% | 16.6% | **17.4%** |
| increase in total income, system leavers | 34.1% | 31.9% | 32.9% |
| increase in earned income, system leavers | 15.5% | 14.2% | 14.8% |

Returns within 24 months is the one that matters: nothing in the calibration
currently disciplines exit and re-entry, and the model produces it endogenously.

---

## Still outstanding

- **SCF bottom-50% net worth share.** Would discipline the bottom of the wealth
  distribution, which is where the homelessness margin lives. `wealth/GDP = 3`
  is a standard target and stays; this would sit alongside it, not replace it.
- **CDC WONDER drug-overdose mortality by single-year age.** `aleph` is
  currently calibrated to a \$7.5m VSL and SUD excess mortality is *inferred*
  rather than measured. Measuring it directly would make the paper's central
  mechanism an input instead of an output.
(Table 5.35B is now read — see section 7.)

---

## 7. `treat_ucost` as a UTILITY cost is directly supported — no change

NSDUH Table 5.35B, adults who perceived an unmet need for substance use
treatment and did not receive it, 2023. Multiple responses allowed, so these do
not sum to 100.

| reason | % | model analogue |
|---|---:|---|
| Thought they should have been able to handle it themselves | **70.7** | none |
| Not ready to start treatment | 62.3 | none |
| Not ready to stop or cut back using | **55.9** | the Stone-Geary `b` term |
| Worried what people would think | **41.5** | `treat_ucost` |
| Thought it would cost too much | 40.1 | a resource cost |
| Did not have enough time | 39.0 | time cost |
| Did not know how or where to get treatment | 37.1 | none |
| Worried information would not stay confidential | 32.4 | `treat_ucost` |
| Insurance would not pay enough | 30.7 | a resource cost |
| Thought that if people knew, [consequences] | 30.9 | `treat_ucost` |
| Did not have health insurance | 28.6 | a resource cost |
| Could not find a programme | 27.4 | none |
| Did not think treatment would help | 24.4 | none |
| Thought they would be forced to stop using | 22.9 | the Stone-Geary `b` term |
| Transport and similar problems | 21.9 | none |
| Thought no one would care | 16.8 | `treat_ucost` |
| No openings in a programme | 13.4 | none |

**The barriers are overwhelmingly non-monetary.** Cost is 40.1% and insurance
another 28.6–30.7%, but every one of the three largest reasons is a belief or a
preference: self-efficacy at 70.7%, not ready to start at 62.3%, not ready to
stop using at 55.9%. The stigma cluster — what people would think,
confidentiality, consequences if known — runs 31–42%.

This settles a modelling choice a referee could reasonably have challenged.
Treatment was switched from a resource cost `treat_cost` to a **utility** cost
`treat_ucost`, which never enters the budget constraint. The data says that is
the right structure: a resource cost would capture at most the 40% who cite
expense, and would entirely miss the majority who decline treatment for reasons
that are, in the model's language, preferences rather than prices.

It also confirms the split already in the model. "Not ready to stop or cut back"
(55.9%) and "would be forced to stop" (22.9%) are *not* `treat_ucost` — they are
the household not wanting to quit, which the model carries in the Stone-Geary
endowment `b`. Loading all of them onto `treat_ucost` would double-count.

One caveat: this is conditional on *perceived unmet need*, so it describes the
margin of people who considered treatment and declined, not the whole SUD
population. That is the right margin for `treat_ucost`, but the levels are not
population shares.

---

## 8. SUD mortality is now MEASURED, not inferred — the biggest win

CDC WONDER provisional mortality, grouped by `MCD - Drug/Alcohol Induced
Cause`. Overdose is the sum of the four drug-poisoning rows (X40-X44 unintentional,
X60-X64 suicide, X85 homicide, Y10-Y14 undetermined), 81,834 deaths at ages
25-84. Against the SSA all-cause table:

| age | overdose q | all-cause q | **overdose share of all deaths** | implied q given SUD (3.68%) |
|---|---:|---:|---:|---:|
| 25-29 | 0.00025 | 0.00123 | **20.4%** | 0.0068 |
| 30-34 | 0.00038 | 0.00166 | **23.2%** | 0.0105 |
| 35-39 | 0.00046 | 0.00205 | **22.3%** | 0.0124 |
| 40-44 | 0.00049 | 0.00262 | 18.6% | 0.0132 |
| 50-54 | 0.00044 | 0.00471 | 9.4% | 0.0121 |
| 65-69 | 0.00028 | 0.01500 | 1.9% | 0.0077 |

**Roughly a fifth of all deaths between 25 and 44 are drug poisonings.** If
those fall on the 3.68% carrying the model's SUD concept, their overdose hazard
alone is about 1.3% a year at peak ages, against an all-cause baseline near
0.26% — roughly **5x baseline mortality from overdose alone**.

That is exactly the object the model's SUD mortality channel represents, and it
is currently backed out of the VSL calibration rather than measured. This makes
it an input. It also bears directly on Referee 1's rival hypothesis: a measured
hazard accounting for a fifth of prime-age deaths is a far stronger answer than
a parameter fitted to hit a VSL target — especially alongside the NSDUH finding
in section 3 that the employment gradient may be too strong by 2.5x.

Restricting to unintentional poisoning (X40-X44) alone, which is what the
ICD-10 113 Cause List offers, understates the total by 7-10% at prime ages and
by much more above 70, where intent is more often recorded as suicide or
undetermined.

### Do not use "All other drug-induced causes" as non-overdose SUD mortality

It looks like the missing piece and it is not. CDC's drug-induced list carries a
long tail of **therapeutic** adverse effects — drug-induced anaemia,
thyroiditis, polyneuropathy, osteoporosis — with no connection to substance use
disorder, and they dominate at older ages: 600 per 100,000 at 80-84, against 6
for overdose. At prime ages it is mostly F11-F19, mental and behavioural
disorders due to psychoactive substance use, and there it is informative. The
script keeps the category and refuses to sum it into the overdose total.

Overdose still understates total SUD excess mortality, which also runs through
liver disease, endocarditis, hepatitis, HIV, suicide and accidents. Published
all-cause SMRs for opioid use disorder are 6-10x, of which overdose is roughly
half. Treat the numbers above as a **lower bound**.

---

## 9. `kappa_r` — use the tenant-based voucher figure, not the all-programs one

The programme-level HUD extract separates what the summary file averaged
together. The model's voucher is a tenant-based Housing Choice Voucher, so that
is the row to compare.

| programme | income/yr | tenant rent/mo | **tenant share** | HUD/mo | wait | beds 0-1/2/3+ | wages major |
|---|---:|---:|---:|---:|---:|---|---:|
| **HCV tenant-based** | \$19,368 | \$503 | **31.2%** | \$1,240 | 29mo | 31/35/34 | 28% |
| HCV project-based | \$18,402 | \$428 | 27.9% | \$1,344 | 24mo | 60/23/17 | 21% |
| Public housing | \$19,743 | \$439 | 26.7% | \$856 | 19mo | 41/30/29 | 29% |
| Project-based S8 | \$16,427 | \$389 | 28.4% | \$1,150 | — | 62/25/13 | 17% |
| all programmes | \$18,483 | \$452 | 29.3% | \$1,135 | 25mo | 46/29/25 | 24% |

`kappa_r = 0.30` against **31.2%** for tenant-based vouchers. Slightly above the
statutory 30%, which is expected: the statute takes 30% of *adjusted* income,
and HCV tenants may pay up to 40% at initial lease-up when the unit rent exceeds
the payment standard.

The waiting time for tenant-based vouchers is **29 months**, which sharpens
rather than resolves the `prob_V` tension in section 4: 0.06 implies 200.

---

## 10. The homelessness mortality penalty was five times too small

Baggett et al. (2013, JAMA Intern Med), Boston Health Care for the Homeless,
race-adjusted all-cause mortality rate ratios against the Massachusetts general
population:

| age | men | women |
|---|---:|---:|
| 25-44 | **8.6** (7.4-9.9) | **9.6** (7.4-12.4) |
| 45-64 | 4.5 (4.1-4.9) | ~4.5 (3.6-5.6) |
| 65-84 | 1.1 (0.9-1.4) | ~1.1 (0.7-1.8) |

`kappa_phi_h` was **1.6, flat across all ages**. That was wrong twice: five
times too small at prime ages, and the wrong shape. A constant multiplier large
enough to match the young implies a 41% annual death rate for a homeless
80-year-old.

Their ratio is the TOTAL for homeless adults, most of whom also have SUD, and
the model already carries a separate `kappa_phi_d = 6.9`. Using 9.1 directly
would stack the two and count SUD mortality twice, giving 59x. Netting out the
SUD composition,

    RR_total = kappa_phi_h * [ (1-s) + s*kappa_phi_d ],   s = 0.217

leaves **3.99 / 1.97 / 0.48**. The 65+ figure is floored at 1.0: read literally
it says homelessness protects the old, which is survivor selection rather than a
causal effect, and the model cannot represent selection on unobserved frailty.
Flooring understates the mortality channel rather than inventing a protective
one.

Now implemented as `kappa_phi_h_age(n_age)`.

Also from Baggett, usable as validation: drug overdose is 35% of deaths among
homeless 25-44 year olds, at rates 16 to 24 times the general population;
opioids are implicated in 81% of overdose deaths.

---

## 11. National homelessness by age, and system dynamics

PIT 2024. The 65+ column is named **"Over 64"**, which is why a first pass
stopped at 64.

| band | homeless | population | rate | **share of homeless** |
|---|---:|---:|---:|---:|
| 25-34 | 146,859 | 46,453,864 | 0.3161% | 26.0% |
| 35-44 | 153,849 | 45,539,224 | 0.3378% | 27.2% |
| 45-54 | 118,740 | 40,780,356 | 0.2912% | 21.0% |
| 55-64 | 104,007 | 41,661,725 | 0.2496% | 18.4% |
| 65-84 | 42,147 | 54,744,775 | 0.0770% | 7.5% |
| total | 565,602 | 229,179,944 | 0.2468% | 100% |

The rate peaks at 35-44 and collapses by a factor of 4.4 after 65, which is the
same selection story as the mortality ratios.

HUD System Performance Measures, national, give three more untargeted moments:

| measure | 2020 | 2022 | 2024 |
|---|---:|---:|---:|
| **returns to homelessness within 24 months** | 19.7% | 16.6% | **17.4%** |
| increase in total income, system leavers | 34.1% | 31.9% | 32.9% |
| increase in earned income, system leavers | 15.5% | 14.2% | 14.8% |

Returns within 24 months is the one that matters: nothing in the calibration
currently disciplines exit and re-entry, and the model produces it endogenously.

---

## Still outstanding

- **SCF bottom-50% net worth share.**
