# The households whose voucher Treatment First revokes: SUD and mortality, short run, fixed prices

4 October 2026. The author: *"Can we test a short run experiment with fixed prices and fixed pi_V, where you do
Treatment First and check what happens to the SUD of those whose voucher was revoked in the first 3 years?"*, and the
*"MORTALITY of those whose voucher was revoked relative to what would happen to them if they had stayed housed"*. For
the associate editor's comment on Costantini (2025) (HF_or_TF_RED_reviews/decision/AE_R1.txt). Code and design detail:
`code/revoked_2c/README.md`. Full tables: `tables.md`. Guards: `guard_T3_pair.txt`, `guard_T3_rest.txt` and the top of
`tables.md`. Logs: `*_run.log.gz`.

## Headline

**Of the households whose voucher is revoked in years 1-3, 6.92 per cent are dead three years later under Treatment
First, against 6.12 per cent had the same households kept the voucher under Housing First's rules: +0.80 percentage
points**, all of it through the survival draw (the end of life contributes +0.00). The gap keeps widening: +1.02 pp at
four years, +1.42 pp at six. The channel is homelessness, not the disorder: 27 to 29 per cent of the year-1 cohort
are on the street in each of the three years after the revocation, against none in the counterfactual, while their
SUD share is the same under both (86.8 against 86.9 per cent three years on, down from 96.1 per cent at the
revocation).

**The SUD of the revoked does not respond to the revocation.** The share with the disorder falls by about three
points a year under both (recovery and the deaths of the disordered), and the two paths stay within 0.1 to 0.5 points
of each other, Treatment First marginally LOWER, which is the disordered dying faster and the street's recovery
multiplier, not abstinence.

## Design

* **Start**: the Housing First (no-policy) steady state of the omega_c = 0.085 economy, re-solved here
  (`cfarm_null_2c`, cf_fix2_share; 5 passes, distribution rule 5e-5 passed; against the accepted run
  `counterfactuals_2c/nulltf/null`, worst relative difference 1.6e-4, the drug price, which cleared at 1.0002655
  against 1.0001082).
* **Reform**: Treatment First at the start of year 1: vouchers conditional on no use and no disorder, detection 85
  per cent, no false positives, the $35 test, the three-year exclusion.
* **Fixed paths**: drug price 1.0001082 and pi_V 0.067533863 (the accepted no-policy values) in every year, budget not
  cleared (`adjust_taxes 0`), price not moved (`drug_market_adjuster 0`). One forward pass (loop 0): the build stops
  after it, so nothing is updated.
* **End point** (T = 10): Treatment First with both channels held, the `fixboth` arm of
  `extra_2c/remote_decomp_2c_both.sh`, re-solved (`cfarm_tf_2c_fixboth`, 4 passes; against
  `results/decomp_2c_both/arm_fixboth`, worst relative difference 2.1e-4, lambda_d).
* **Counterfactual path**: the same machinery with the no-policy steady state at both ends and the same fixed paths,
  so every year runs Housing First's own policy functions.
* **Tracking** (print-only module; no equation changes): the shadow step is the model's forward kernel written out a
  second time, term for term, with no newborn row.
  * *Revoked in year t*: the terms that move a holder (voucher state 1) into the exclusion state in the step that
    makes year t. With no false positives each is a failed test of a holder. A queued household that wins the lottery
    and fails the test is excluded too but never held a voucher, and is not tagged.
  * *(a) actual*: that mass followed under Treatment First's kernel. *(b) counterfactual*: the same mass in voucher
    state 1 instead (the voucher draw is the last factor of the kernel, so these are the same households with the same
    year-t choices, voucher kept), followed under Housing First's kernel.
  * *Holders at the reform*: voucher state 1 in the t = 0 distribution, followed under each kernel from year 1.
  * Deaths: mass times one minus the survival probability the kernel applies (homelessness, the disorder and SMI
    enter through the mortality multipliers), plus the mass at the last age (age 85), which the kernel does not carry.
* With the paths fixed, loop 0's policy functions do not depend on the distribution, and the shadow step is serial, so
  the tracked numbers are exactly reproducible (identical on one and two threads).

## Guards

| guard | result |
|---|---|
| tracking changes nothing (T = 3, one thread): plain and tracking builds, all 48 aggregate lines (MECH, VOUCHER CENSUS, BUDGET, BUDGET PARTS/SPEND, DRUG, WELFARE, MILBY, RECOVERY, ALLALIVE, BETTER OFF, CEV, ...) | identical, bit for bit. PASS |
| the shadow step IS the model's step (whole population at t-1 through it, against the model's distribution at t, ages 2+) | one thread: 0.0 in every cell. PASS. Four threads (the T = 10 runs): at most 8.5e-6 of the mass, the model's own race (below) |
| mass accounting: alive + cumulative deaths = starting mass | worst 3.4e-13 relative (rule 1e-10), every group, both paths, every year. PASS |
| fixed paths | price 1.0001082 and pi_V 0.067533863 printed in all 9 years of both T = 10 paths (and every T = 3 run), one value each. PASS |
| tags | written by the Treatment First run, read by the Housing First run, same mass to the last digit (0.13989, 0.020557, 0.0057635). PASS |
| Housing First stays stationary | the no-policy steady state through its own kernel, newborns added: SUD share 0.038139 at t = 1 and 0.038133 at t = 9, homelessness 0.0061309 and 0.0061299, deaths 0.99998 to 1.00001 a year, mass alive 50.8276 to 50.8280; sum over cells of the year's change 2e-3 to 5e-3 of a mass of 50.8 (1e-4 relative). The drift is the arms' own tolerance (distribution rule 5e-5 per cell), the 1.6e-4 gap between the held price and the re-solved arm's, and the race; it is two orders of magnitude below every effect reported. PASS |
| Housing First from the tags on one thread, and a bounds-checked tracking build | Housing First on one thread: the shadow step reproduces the model's to 0.0, accounting 3.3e-14, tags read back exactly. Bounds-checked (-fcheck=bounds,pointer) tracking build: no runtime error, tracked groups within 2.5e-8 of the -O3 build (optimisation rounding). PASS |

## Results

Shares in per cent of each group's starting mass (population: 1 newborn a year, 50.8 alive). Full tables, including
the year-2 and year-3 cohorts separately: `tables.md`.

**Revoked in year 1** (mass 0.1399, 3.9 per cent of the 3.60 holders at the reform; 96 per cent with the disorder;
mean age about 46):

| years since revocation | cum. deaths (a) | cum. deaths (b) | gap pp | SUD (a) | SUD (b) | homeless (a) | homeless (b) | holding (a) | holding (b) |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.00 | 0.00 | 0.00 | 96.14 | 96.14 | 0.00 | 0.00 | 0.00 | 100.00 |
| 1 | 2.37 | 2.08 | +0.29 | 92.96 | 93.02 | 28.61 | 0.00 | 0.00 | 86.34 |
| 2 | 4.68 | 4.13 | +0.56 | 89.84 | 89.93 | 28.24 | 0.00 | 0.35 | 75.33 |
| 3 | 6.95 | 6.14 | +0.81 | 86.78 | 86.86 | 27.37 | 0.00 | 0.68 | 65.87 |
| 5 | 11.31 | 10.05 | +1.26 | 80.75 | 80.79 | 24.01 | 0.11 | 1.31 | 51.02 |
| 8 | 17.50 | 15.75 | +1.75 | 71.87 | 71.87 | 18.24 | 0.62 | 2.22 | 36.15 |

**The three revoked cohorts pooled** (mass 0.1662; each from its own revocation year):

| years since | cum. deaths (a) | cum. deaths (b) | gap pp |
|---|---|---|---|
| 1 | 2.36 | 2.08 | +0.28 |
| 2 | 4.66 | 4.12 | +0.54 |
| **3** | **6.92** | **6.12** | **+0.80** |
| 4 | 9.11 | 8.09 | +1.02 |
| 6 | 13.37 | 11.95 | +1.42 |

The year-2 (mass 0.0206) and year-3 (0.0058) cohorts look like the first: three-year gaps of +0.77 and +0.53 pp,
homelessness 26 and 20 per cent. Revocations fall off quickly because the condition deters use: the deterred margin is
not empty, but most of the revocation happens to the stock of disordered holders in year 1.

**Every holder at the reform, revoked or not** (mass 3.603): cumulative deaths 12.51 against 12.48 per cent at three
years (+0.03 pp), 32.71 against 32.63 at nine (+0.08 pp); homelessness 1.35 against 0.01 per cent at three years;
SUD 5.23 against 5.34. The revocations of years 1-3 add up to 4.6 per cent of the holders at the reform, and are diluted across the rest.

**The whole population, Treatment First path against Housing First** (per year):

| year | deaths (Treatment First) | deaths (Housing First) | SUD % (Treatment First) | SUD % (Housing First) | homeless % (Treatment First) | homeless % (Housing First) | excluded % (Treatment First) |
|---|---|---|---|---|---|---|---|
| 1 | 0.99999 | 0.99998 | 3.69 | 3.81 | 0.61 | 0.61 | 0.40 |
| 2 | 1.00022 | 0.99999 | 3.58 | 3.81 | 0.70 | 0.61 | 0.42 |
| 3 | 1.00008 | 0.99999 | 3.47 | 3.81 | 0.71 | 0.61 | 0.41 |
| 5 | 0.99970 | 0.99999 | 3.26 | 3.81 | 0.72 | 0.61 | 0.39 |
| 9 | 0.99887 | 1.00001 | 2.89 | 3.81 | 0.71 | 0.61 | 0.37 |

Deaths are higher for the first three years (the revoked on the street) and then fall below Housing First's as the deterrent shrinks the
disorder (SUD 2.89 against 3.81 per cent by year 9, still falling towards the steady state's 1.35).

## Against Costantini (2025)

Costantini finds that a permanent voucher (HUD-VASH, Housing First) cuts three-year mortality by 4.6 percentage points
for homeless veterans, while transitional housing (Treatment First) has no lasting health effect. The model's
analogue, with the sign reversed, is the effect of LOSING the voucher on the households Treatment First revokes:
**+0.80 pp three-year mortality, a 13 per cent rise on a base of 6.1 per cent**. It points the same way as his
estimate: housing a household saves lives in the model, and only through the street (the disorder itself barely moves
in three years under either rule). The magnitudes are not comparable one for one:

* **The population.** His sample is homeless veterans at programme entry, older and sicker, all on the street when
  treated. The model's revoked households are housed voucher holders, mean age about 46, nearly all with the disorder,
  and only 27 to 29 per cent of them end up on the street after losing the voucher; the rest find other housing.
* **The estimand.** His 4.6 pp is a LATE: the effect for the compliers whose housing the instrument moves. The model's
  0.80 pp is the average effect on everyone revoked, most of whose housing the revocation does not change. Scaled by
  the 28 percentage points of homelessness the revocation causes (a Wald-style rescaling, not a model output), it is
  about 2.9 pp of three-year mortality per household moved onto the street, the same order as his 4.6 pp for a
  population with a higher baseline.
* **Treatment First is not transitional housing.** The model's Treatment First is a sobriety condition on a permanent
  voucher; his comparison arm is a time-limited place. That his transitional arm shows no lasting effect is consistent
  with the model in that the model's health effect runs through being housed, not through the conditionality.

## A bug found on the way: the model's forward kernel has a data race

The first T = 3 tracking run disagreed with the model's own step by 7e-6 in one cell, and two runs of the SAME plain
binary on two threads disagreed with each other (b at t = 1: 0.056421324900 against 0.056421298660; lambda_d
0.038139160889 against 0.038139143152; h_1 identical). On one thread the plain and tracking builds agree bit for bit
and the shadow step reproduces the model's to 0.0, so the model's parallel distribution loop is not deterministic.
The likely cause: in `converge_to_stationary_equilibrium`, `is_addicted_1` is
in the `shared` clause of the `!$omp parallel do`, and every iteration writes `is_addicted_1=0` and then `=1` for a
disorder state, so one thread can read another's transient 0 and push a disordered household with the clean survival
and transition rows. The comment there calls it benign because the final value depends only on the outer index; the
transient is what is not benign. It touches only disorder states, which is what the data show (b and lambda_d move,
h_1 does not). Size: about 1e-6 relative in b at t = 1 on two threads, and up to 8.5e-6 of the mass per step on four.
Not fixed here (the brief: no change to the model). Every arm and transition in the repository carries it, at a size
far below any reported number; making `is_addicted_1` private in each of those parallel loops would remove it. It has
not been checked against the stylized model, which has no parallel loop.

## Files

* `RESULT.md` (this), `tables.md` (every table, all four groups, nine years), `status.txt`.
* `guard_T3_pair.txt`, `guard_T3_rest.txt`; `arms/` (the two re-solved steady states' statistics).
* Logs: `tf10_run.log.gz`, `hf10_run.log.gz` (the two T = 10 paths); `plain3_1t`, `track3_1t`, `hf3_1t`, `track3b`
  (the guard runs); `plain3_2t`, `track3_2t` (the two-thread runs that exposed the race).
