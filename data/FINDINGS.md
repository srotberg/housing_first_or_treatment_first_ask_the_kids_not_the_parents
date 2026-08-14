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

## 3. A genuine tension in the SUD–employment link — INVESTIGATE

NSDUH gives the gradient directly, aged 26+, 2023:

| employment | drug use disorder | all SUD |
|---|---:|---:|
| Full-time | 8.3% | 18.5% |
| Part-time | 8.3% | 16.4% |
| Unemployed | **19.2%** | 28.3% |
| Other (not in labour force) | 8.0% | 13.1% |
| total | 8.6% | 16.6% |

Relative risk of drug use disorder, unemployed against the population: **2.23×**.

The model targets the *reverse* conditioning, `unemp rate | SUD = 26.9%` against
an overall rate of 4.9% — a relative risk of **5.5×**. By Bayes those are the
same object, and 5.5 against 2.23 is a factor of 2.5 apart.

Two caveats before concluding the target is wrong. NSDUH's "unemployed" is
self-reported and not the BLS concept. And the model's SUD is narrower than
NSDUH's drug use disorder — marijuana is 5.5 of the 8.6 points, and severe
disorders plausibly carry a steeper employment gradient than marijuana does. So
the true comparison for the model's concept lies somewhere above 2.23.

### Computed from the published tables

Tables 5.4A (counts) and 5.4B (rates) together give the joint, ages 26+, 2023.
Dividing counts by rates recovers each employment cell's population:

| cell | population (000s) | with DUD (000s) | DUD rate |
|---|---:|---:|---:|
| full-time | 107,759 | 8,944 | 8.3% |
| part-time | 23,145 | 1,921 | 8.3% |
| unemployed | 8,099 | 1,555 | 19.2% |
| other | 85,500 | 6,840 | 8.0% |

- unemployment rate overall (U / [FT+PT+U]): **5.83%**
- **unemployment rate given drug use disorder: 12.52%**
- relative risk **2.15x**, against the model's implied **5.49x**

**So 26.9% is roughly 2.15x the NSDUH figure for ANY drug use disorder.** But
the model's concept is moderate/severe, which is worse-off than the average
case, so the true comparison is higher than 12.52%. An extreme upper bound —
assuming every unemployed person with a disorder has a moderate/severe one —
puts it near 31%. So 26.9% is not refuted; it sits at the very top of the
plausible range and requires nearly all disorder-related unemployment to fall
in the severe tail.

### Getting the exact number — one variable

No published table crosses severity with employment, so this needs microdata.
`data/NSDUH_2024.dta` already has severity (`svyrdudany`) and the weight, but
the extract dropped employment. Add **`irwrkstat`** (1 full-time, 2 part-time,
3 unemployed, 4 other/NILF) to the same `keep` list and re-export, or compute it
in Stata directly:

```stata
use "NSDUH_2024.dta", clear
keep if age3 >= 7                             // ages 26+
gen byte modsev = inlist(svyrdudany, 2, 3)    // moderate/severe drug UD
gen byte inlf   = inlist(irwrkstat, 1, 2, 3)  // labour force
gen byte unemp  = irwrkstat == 3
tab modsev if inlf [aw=analwt2_c], summarize(unemp) means
```

The `modsev == 1` mean is the moment. Check `tab irwrkstat` first — some
vintages name it `irwrkstat18`.

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

## Still outstanding

- **SCF bottom-50% net worth share.**
