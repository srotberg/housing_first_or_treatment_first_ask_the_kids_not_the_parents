# The households whose voucher Treatment First revokes, split by serious mental illness (SMI)

5 October 2026. The author: *"you need to condition on the SMI for the constantini comparison, no?"*, *"are you
measuring this in the model for the SMI and homeless?"*, *"you need to include SMI!"*. Costantini (2025) estimates
4.6 pp of three-year mortality for homeless veterans WITH MENTAL ILLNESS; the comparable model number is the gap among
the revoked households with SMI. The experiment is `results/revoked_2c` unchanged (Treatment First switched on with
the drug price 1.0001082 and pi_V 0.067533863 held at the no-policy values, T = 10, one forward pass; the revoked
followed under Treatment First (a) and, voucher kept, under Housing First (b)), with each tracked group cut by its SMI
state AT REVOCATION. Code: `code/revoked_2c_smi/README.md`. Full tables: `tables.md`. Guards: `guard_T3.txt` and the
top of `tables.md`. Logs: `*_run.log.gz`.

## Headline

**Of the households revoked in years 1-3 who have SMI at revocation, 8.31 per cent are dead three years later under
Treatment First, against 6.40 per cent had they kept the voucher: +1.92 percentage points**, a 30 per cent rise,
against +0.64 pp for the revoked without SMI. The difference is mostly the street: **51 to 53 per cent of the
revoked with SMI are homeless in each of the three years after the revocation**, against 24 to 25 per cent of those
without, and none of either in the counterfactual. **Per household made homeless, the gap is 3.7 pp** with SMI
(2.6 pp without, 2.9 pp for all), against Costantini's 4.6 pp.

Pooled over the three revoked cohorts, each read from its own revocation year (as `code/paper/export_revoked.py`
pools them):

| revoked in years 1-3 | share of the revoked | 3-yr deaths (a) | 3-yr deaths (b) | gap | homeless (a), yrs 1 / 2 / 3 | per household made homeless | 4-yr gap | 6-yr gap |
|---|---|---|---|---|---|---|---|---|
| **with SMI** | **12.2 %** | **8.31 %** | **6.40 %** | **+1.92 pp** | **50.8 / 52.2 / 52.8 %** | **3.7 pp** | **+2.48 pp** | **+3.49 pp** |
| without SMI | 87.8 % | 6.72 % | 6.08 % | +0.64 pp | 24.8 / 24.3 / 23.5 % | 2.6 pp | +0.82 pp | +1.14 pp |
| all | 100 % | 6.91 % | 6.12 % | +0.80 pp | 27.9 / 27.7 / 27.0 % | 2.9 pp | +1.02 pp | +1.42 pp |

The year-1 cohort alone (85 per cent of the revoked mass):

| revoked in year 1 | share | 3-yr deaths (a) | 3-yr deaths (b) | gap | homeless (a), yrs 1 / 2 / 3 | per household made homeless | 4-yr gap | 6-yr gap |
|---|---|---|---|---|---|---|---|---|
| **with SMI** | **12.2 %** | **8.35 %** | **6.41 %** | **+1.94 pp** | **51.6 / 52.9 / 53.4 %** | **3.7 pp** | **+2.51 pp** | **+3.52 pp** |
| without SMI | 87.8 % | 6.75 % | 6.09 % | +0.65 pp | 25.4 / 24.8 / 23.8 % | 2.6 pp | +0.84 pp | +1.15 pp |
| all | 100 % | 6.94 % | 6.13 % | +0.81 pp | 28.6 / 28.2 / 27.4 % | 2.9 pp | +1.04 pp | +1.44 pp |

Homeless shares are of the survivors; nobody in either group is homeless in the counterfactual in years 1-3 (0.0 per
cent to one decimal). "Per household made homeless" is the three-year gap over the average rise in the survivors'
homeless share across years 1-3, the Wald-style rescaling used for the unsplit number (a rescaling, not a model
output).

**The split reproduces the unsplit numbers.** Weighting the two halves by their mass at revocation gives 6.9129 and
6.1176 per cent, gap +0.7953 pp, identical to the unsplit groups to the fourth decimal (pooled, and in each cohort).
Against `results/revoked_2c`'s 6.92 / 6.12 / +0.80: 6.91 / 6.12 / +0.80. The 0.01 pp in (a) is from the re-solved
steady states (against the accepted runs, worst relative difference 1.2e-4 in the no-policy drug price and 2.5e-4 in
the held-price Treatment First SUD share, the same order as the first re-solve). The paper's x_rv_* still read
`results/revoked_2c` and are unchanged.

## What lies behind the SMI gap

* **Twice as many end up on the street.** Revocation puts about 52 per cent of the households with SMI on the street,
  against 24 per cent without. (SMI shifts employment in the model; which channel moves them onto the street was not
  decomposed here.)
* **The street is deadlier for them.** The gap per household made homeless is 3.7 pp against 2.6 pp: SMI and
  homelessness both enter the survival probability, so the street costs more years of life to a household with SMI.
* **SMI is over-represented among the revoked.** It is 6.3 per cent of the holders at the reform and 12.2 per cent of
  the revoked: the revoked are nearly all disordered (96.7 per cent with SMI, 96.1 per cent without), and the disorder
  and SMI go together in the model.
* **Not the disorder.** Three years on, the SUD share among the survivors with SMI is 90.7 per cent under Treatment
  First against 90.4 under Housing First (86.2 against 86.4 without SMI). As in the unsplit result, the disorder does
  not respond to the revocation within three years.
* **SMI later on.** SMI is not absorbing: it is left at rate lambda_m and entered at the onset hazard. Of the revoked
  with SMI at revocation, 93.4 per cent of the survivors still have it a year later, 81.3 per cent three years later
  and 65.8 per cent six years later, the same under both kernels (housing does not enter the SMI chain). Of those
  without it at revocation, 0.8 per cent have it three years on and 1.4 per cent six years on.

By years since the revocation, pooled:

| years since | with SMI (a) | (b) | gap | without SMI (a) | (b) | gap | all (a) | (b) | gap |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2.80 | 2.13 | +0.67 | 2.30 | 2.07 | +0.23 | 2.36 | 2.08 | +0.28 |
| 2 | 5.57 | 4.26 | +1.31 | 4.53 | 4.10 | +0.44 | 4.66 | 4.12 | +0.54 |
| **3** | **8.31** | **6.40** | **+1.92** | 6.72 | 6.08 | +0.64 | 6.91 | 6.12 | +0.80 |
| 4 | 11.01 | 8.53 | +2.48 | 8.85 | 8.03 | +0.82 | 9.11 | 8.09 | +1.02 |
| 6 | 16.28 | 12.80 | +3.49 | 12.96 | 11.82 | +1.14 | 13.36 | 11.94 | +1.42 |

**Every holder at the reform, revoked or not:** with SMI (6.3 per cent of the holders) +0.11 pp at three years and
4.7 per cent homeless; without SMI +0.02 pp and 1.1 per cent homeless.

## Against Costantini (2025)

Conditioning on SMI moves the model's numbers towards his. The average effect on the revoked with SMI is +1.92 pp,
and per household moved onto the street it is 3.7 pp, against his 4.6 pp for homeless veterans with mental illness.
The caveats in `results/revoked_2c/RESULT.md` still hold:
* his estimate is a LATE for compliers in a population already on the street at entry;
* the model's revoked with SMI are housed voucher holders with a SUD, mean age about 45, about half of whom the
  revocation puts on the street;
* his comparison arm is transitional housing, not a sobriety condition.

## Guards

| guard | result |
|---|---|
| the split changes nothing in the model (T = 3, one thread): plain build against the split build, all 48 aggregate lines | identical, bit for bit. PASS |
| groups 1-4 unchanged (T = 3, one thread): unsplit tracking build against the split build, every REVK GROUP, POP, TAG, LEAK, INIT, MASK and aggregate line (68 lines) | identical, byte for byte. PASS |
| the halves sum to the unsplit group (levels, and shares times survivors; T = 3 and both T = 10 paths) | worst relative difference 1.5e-13 (rule 1e-12): 48 comparisons at T = 3 (14 bit for bit) and 272 in each T = 10 path (23 and 52 bit for bit). PASS. Not bit for bit throughout (see below) |
| the cut is by SMI at the start | SMI share exactly 0 in every half without SMI, 1 to 1.9e-14 in every half with it. PASS |
| mass accounting, every group and half, both paths | worst 4.9e-13 (rule 1e-10). PASS |
| shadow kernel is the model's kernel | 0.0 on one thread at T = 3; at most 7.4e-6 of the mass on four threads (the model's distribution-loop race, recorded in `results/revoked_2c`). PASS |
| fixed paths | price 1.0001082 and pi_V 0.067533863 in all 9 years of both paths. PASS |
| same households under both kernels | starting mass of every half identical in (a) and (b). PASS |

**Why the sums are not bit for bit.** The brief asked for the halves to sum to the unsplit groups bit for bit. They
cannot, even in the year of revocation:
* the module totals a group over the whole array, but totals each half over its own cells, so the same numbers are
  added in a different order;
* after that year, the halves pass through the kernel separately and then share cells as households enter and leave
  SMI, so their rounding diverges.

The cut itself is exact: every cell goes to exactly one half, which the 0 and 1 SMI shares confirm. The guard
therefore requires agreement to rounding (worst 1.5e-13), not identity. Exact identity is shown where it can hold:
the aggregates against the plain build, and groups 1-4 against the unsplit build.

## Runs

The two steady states were re-solved with `code/revoked_2c/run_arms.sh` (no policy: 5 passes, voucher check passed;
held-price Treatment First: 4 passes; both met the distribution rule). Guards ran on one thread and the T = 10 paths on
four. The container restarted twice during the Housing First path, which was rerun from scratch from the same
Treatment First tags; nothing else was affected.

## Files

* `RESULT.md` (this), `tables.md` (guards; pooled and per-cohort tables by SMI; holders at the reform), `status.txt`,
  `guard_T3.txt`, `arms/` (the re-solved steady states against no policy).
* Logs: `tf10_run.log.gz`, `hf10_run.log.gz` (the T = 10 paths); `plain3_1t`, `smi3_1t`, `track3_1t` (the guard runs).
