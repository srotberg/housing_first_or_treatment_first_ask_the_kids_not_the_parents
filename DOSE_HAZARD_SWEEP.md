# A dose-dependent addiction onset hazard: what it does to the price elasticities
# and to the age profile of drug use

## What was run

The onset hazard, at `code/housing_first_or_treatment_first_SR_v1.f90:8225`:

```fortran
if (drug_quantity_1>0) then
    addiction_onset_hazard = min(addiction_onset_base + (1-exp(-lambda_addiction*drug_quantity_1)), 1)
else
    addiction_onset_hazard = 0
end if
```

An abstainer always has zero onset. In the benchmark of record
`addiction_onset_base=0.0428` and `lambda_addiction=0`, so the hazard is FLAT in
quantity: any user, however light, pays 4.28 per cent per period. This sweep asks
what happens with no base and a hazard that rises with the dose.

Four points, all at the `VECTOR` line of `code/benchmark_of_record.txt` and
differing only in the two hazard parameters:

| run | `addiction_onset_base` | `lambda_addiction` | point file | solve |
|---|---|---|---|---|
| A (reference) | 0.0428 | 0 | `code/points/point_6876263050.txt` | 3 min |
| B | 0 | 0.8 | `code/points/point_9f0c7360c6.txt` | 4 min |
| C | 0 | 2 | `code/points/point_18e0037d43.txt` | 4 min |
| D | 0 | 5 | `code/points/point_8d8e01f1b4.txt` | 3 min |

All four carry `MODEL 873cb2fa1f` and `HANDOVER OK: 80 of 80 parameters
applied`. The only source change was
`measure_price_elasticity` 0 -> 1 (line 429, exactly one occurrence); that edit
is deliberately NOT committed.

**No run printed `ELASTICITY HELD` or `ELASTICITY SKIPPED`.** Every elasticity
below was actually computed. (`grep -c` for those two strings returns 0 in all
four point files, and `measure_child_gap=0` throughout, so the omega
counterfactual never displaced the elasticity block.)

## The table

Elasticities are the `UNTARGETED price elasticity, ...` lines; `b` and
`lambda_d` are the `MOMENT` lines; the age block is the `UNTARGETED` age lines;
quantities are the `ELASTICITY_DIAG base` line, i.e. measured at the benchmark
price before the +10 per cent step.

| | data / target | A: base 0.0428, lam 0 | B: base 0, lam 0.8 | C: base 0, lam 2 | D: base 0, lam 5 |
|---|---|---|---|---|---|
| price elasticity, participation | **-0.63** | **-3.1362** | **-0.00844** | **+0.1236** | **+0.8071** |
| price elasticity, intensive (per addict) | **-0.55** | **-1.3739** | **-1.1910** | **-1.2466** | **-1.3240** |
| `b` total drug users | 0.089 | 0.07770 | 0.94537 | 0.73351 | 0.27771 |
| `lambda_d` disorder rate | 0.0368 | 0.033558 | 0.045226 | 0.039578 | 0.018223 |
| mean age of drug users | 39.60 | 34.65 | 50.48 | 48.13 | 39.17 |
| users aged 34 or less | 0.4527 | 0.6373 | 0.1913 | 0.2445 | 0.5206 |
| users aged 35-44 | 0.1915 | 0.1859 | 0.2080 | 0.2508 | 0.2598 |
| users aged 45-54 | 0.1358 | 0.1112 | 0.1983 | 0.1775 | 0.0894 |
| users aged 55-64 | 0.1248 | 0.0519 | 0.1778 | 0.1257 | 0.0276 |
| users aged 65 plus | 0.0951 | 0.0138 | 0.2246 | 0.2016 | 0.1025 |
| quantity per user (base price) | -- | 0.053322 | 0.009267 | 0.006228 | 0.005052 |
| quantity per addict (base price) | -- | 0.069852 | 0.087783 | 0.077412 | 0.063869 |
| addict share of users | -- | 0.4319 | 0.0478 | 0.0540 | 0.0656 |
| `theta` drug spending share | 0.14098 | 0.13211 | 0.017450 | 0.013853 | 0.013380 |

Supporting diagnostics, same point files:

| | A | B | C | D |
|---|---|---|---|---|
| quantity per user at the raised price | 0.045754 | 0.008788 | 0.005807 | 0.004388 |
| users at the raised price | 0.057624 | 0.944613 | 0.742198 | 0.299915 |
| elasticity, quantity per USER (mixed) | -1.6060 | -0.5577 | -0.7344 | -1.4774 |
| elasticity, quantity per EXPERIMENTER | -1.9345 | -0.0294 | +0.2368 | +0.3008 |

## The realised hazard, which is not the intended one

The grid was anchored on the claim that mean quantity per user is about 0.053,
so that `1-exp(-0.8*0.053) = 0.0416` reproduces the flat 0.0428 at the mean. That
holds at run A's quantity. **It does not hold at B's, C's or D's**, because
quantity per user collapses by a factor of five to ten the moment the base is
removed:

| | lambda | realised q/user | hazard at that q | hazard at q = 0.053 | hazard at that run's q/addict |
|---|---|---|---|---|---|
| A | 0 | 0.053322 | 0.042800 | 0.042800 | 0.042800 |
| B | 0.8 | 0.009267 | 0.007386 | 0.041514 | 0.067817 |
| C | 2 | 0.006228 | 0.012379 | 0.100575 | 0.143434 |
| D | 5 | 0.005052 | 0.024941 | 0.232794 | 0.273375 |

So B is not "the same average risk, proportional to use". At the quantity B
actually produces the typical user faces 0.74 per cent onset per period against
A's 4.28 — about one sixth. That is the fixed point of the mechanism, not a
mis-set parameter: with no base, a household can buy an arbitrarily small dose
at arbitrarily small onset risk, so the extensive margin becomes nearly free and
almost everyone takes it. `b` goes from 0.0777 to 0.945 at lambda = 0.8. The
addict share of users falls from 0.43 to 0.05: the population is now a very
large number of very light experimenters and a small unchanged core of addicts,
whose own dose (0.064 to 0.088) is comparable to A's.

## The three questions

### 1. The participation elasticity does not fall toward -0.63. It rises, straight past it, and turns positive.

-3.136 (A) -> -0.008 (B) -> +0.124 (C) -> +0.807 (D). It is monotone increasing
in the steepness of the dose response over this grid. -0.63 does lie between A
and B, so a crossing exists somewhere below lambda = 0.8 — but the sweep's own
direction is away from the data value once the base is gone, not toward it, and
by C the model has the wrong SIGN: raising the price of the drug raises the
number of users.

The wrong sign is not a numerical artefact, it is the composition effect. With a
dose-dependent hazard and no base, the price rise pushes incumbent users down to
smaller doses (quantity per user falls 6 per cent in B, 7 per cent in C, 13 per
cent in D), and a smaller dose is a SAFER dose. Marginal households that would
not have used at all now find a tiny, nearly risk-free amount worth buying. In A
that channel does not exist: the 4.28 per cent base is charged whatever the
dose, so cutting the dose buys no safety and the only way to escape the hazard is
to stop, which is why A's participation elasticity is so violently negative
(-3.14, five times the data).

The intensive elasticity, by contrast, barely moves: -1.374, -1.191, -1.247,
-1.324 across the whole grid, all roughly 2.2 to 2.5 times the -0.55 target. The
per-addict margin is essentially untouched by the shape of the onset hazard —
which makes sense, since onset is about becoming an addict, not about what an
addict already addicted then consumes. **Nothing in this sweep is an instrument
for the intensive elasticity.**

### 2. The age profile moves a very long way, overshoots, and comes back — it is not monotone in lambda.

Today the model's users are far too young: 0.637 under 35 against 0.453
observed, mean age 34.65 against 39.60.

- **B (lambda 0.8)** overshoots hard in the opposite direction: mean age 50.48,
  only 0.191 under 35, and 0.225 aged 65-plus against 0.095 observed. The old are
  now over-represented by more than a factor of two.
- **C (lambda 2)** is a little less extreme: mean 48.13, 0.245 under 35, 0.202
  aged 65-plus.
- **D (lambda 5)** lands nearest the data on the two headline numbers: mean age
  **39.17 against 39.60**, and 65-plus **0.1025 against 0.0951**. The under-35
  share, 0.521 against 0.453, is still too high but is far closer than A's 0.637.

So a dose-dependent hazard does fix the "users are too young" problem, and at
lambda = 5 it very nearly fixes it exactly on the mean. The mechanism is
straightforward: the flat base taxes any use at all, so under A only the young —
who have the most life left to discount the disorder against, and least wealth —
find it worth paying; once the hazard is proportional to the dose, an older
household can hold a small, cheap, low-risk habit and does.

**The middle of the distribution is where D still fails**, and it fails in a way
the mean hides: 45-54 is 0.089 against 0.136 and 55-64 is 0.028 against 0.125,
while 35-44 is 0.260 against 0.192 and 65-plus is 0.103 against 0.095. D's age
distribution is bimodal — a large young/prime-age mass and a separate elderly
mass, with a hole through the fifties — and its correct mean is the average of
two wrong lumps. B and C, whose means are badly wrong, actually have a smoother
45-64 region (B: 0.198 and 0.178; C: 0.177 and 0.126, the latter almost exactly
on target). No point on this grid gets both the level and the shape.

### 3. These runs are NOT recalibrated, and that is a real limit on what the table above compares.

Only the two hazard parameters were changed. Nothing else in the vector moved,
and no internal calibration loop was re-run. Three consequences, all visible in
the table and none of them buried:

- **`b` and `lambda_d` drift a long way off their targets.** `b` goes 0.0777
  (target 0.089) -> 0.945 -> 0.734 -> 0.278. B and C are economies in which
  three quarters to nineteen twentieths of the population uses drugs, against a
  target of 8.9 per cent — off by an order of magnitude, not by a calibration
  miss. `lambda_d` is better behaved (0.0336, 0.0452, 0.0396, 0.0182 against
  0.0368) but D is half its target.
- **Each elasticity is measured at whatever level of use its own run produces,
  and those levels are not comparable.** The elasticity is a local derivative at
  the run's own equilibrium; A's is taken at 7.8 per cent participation and
  quantity 0.0533, B's at 94.5 per cent and 0.0093. Reading down the elasticity
  row is therefore reading across four different economies, not four settings of
  one economy. `theta`, the drug spending share, makes the same point: 0.132 in A
  against 0.014-0.017 in B, C and D, an order of magnitude apart.
- **In particular, the direction reported in question 1 is a statement about
  this uncalibrated family**, not a prediction about what a recalibrated
  dose-dependent model would deliver. A recalibration that pulled `b` back to
  0.089 would have to raise the cost of use sharply (through
  `addiction_scalar_1`, `relative_share_of_addiction_1`, or the drug price
  itself), which moves quantity per user back up, which moves the realised
  hazard back up the exp curve — and the realised hazard is exactly what the
  participation elasticity turned out to be a function of. The sign flip at
  lambda >= 2 may well not survive that. **Nothing here should be read as
  "dose-dependence breaks the participation elasticity".** What it establishes
  is narrower and still useful:

  1. the participation elasticity is extremely sensitive to the SHAPE of the
     onset hazard — it moves across four units, from -3.14 to +0.81, on two
     parameters — so the hazard shape is a live instrument for a moment that
     currently misses by a factor of five;
  2. the intensive elasticity is NOT sensitive to it, and needs a different
     instrument;
  3. the age profile is also a strong function of the hazard shape, and moves in
     the direction the data wants;
  4. but a hazard with no base cannot hold `b` anywhere near 0.089 at this
     vector, so base and lambda have to be calibrated jointly with `b`'s own
     instruments rather than swept alone. A grid with `addiction_onset_base` held
     positive and lambda added on top is the obvious next diagnostic, and it was
     not run here.

## Reproducing

```
sed -i 's/integer, parameter :: measure_price_elasticity=0/integer, parameter :: measure_price_elasticity=1/' \
    code/housing_first_or_treatment_first_SR_v1.f90
bash code/run_one_point.sh $(grep -m1 '^VECTOR' code/benchmark_of_record.txt | sed 's/^VECTOR //')
bash code/run_one_point.sh $(grep -m1 '^VECTOR' code/benchmark_of_record.txt | sed 's/^VECTOR //') addiction_onset_base=0 lambda_addiction=0.8
bash code/run_one_point.sh $(grep -m1 '^VECTOR' code/benchmark_of_record.txt | sed 's/^VECTOR //') addiction_onset_base=0 lambda_addiction=2
bash code/run_one_point.sh $(grep -m1 '^VECTOR' code/benchmark_of_record.txt | sed 's/^VECTOR //') addiction_onset_base=0 lambda_addiction=5
```

Four cores, gfortran 13.3.0, `-O3`; 3 to 4.5 minutes a point including the second
solve the elasticity block needs. The point files are NOT committed with this
report — only the report is — so the four solves above have to be re-run to
recover them.
