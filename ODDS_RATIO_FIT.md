# Fitting delta_d, delta_h and omega_c on the lifetime child penalty

`.gitignore` excludes `*.log`, so without this file every number below lives
only on an ephemeral container's disk.

All points share ONE build: `child_penalty_classes=4`,
`voucher_exclusion_states=1`, `measure_child_gap=1`, perfectly elastic drug
supply. Each probe differs from the anchor in exactly ONE parameter, because a
secant taken across two points that differ in anything else is not a secant.

**READ THE LAST BLOCK, AFTER `FROZEN CONVERGED`.** `omega` prints twice and the
earlier print is taken off a state that is not an equilibrium. Quoting the wrong
one produced 0.0824 against a true 0.00755 in this session -- a factor of
eleven -- and it had already produced 0.0613 against a true 0.000252 earlier the
same night.

## The targets

| | target | source |
| --- | --- | --- |
| child SUD odds ratio | 2.00 | `child_sud_ratio_data` |
| child homelessness odds ratio | 2.10 | Bassuk et al. (1997), midpoint of 1.80 and 2.41 |
| `omega`, use rise with the child term off | 0.18343 | `1/0.845 - 1` |

## The points

| point | `delta_d` | `delta_h` | `omega_c` | SUD odds | homeless odds | `omega` | log |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A anchor | 0.24 | 0.31 | 0.007 | **1.5505** | **4.9109** | **0.0075517** | `variant_save_20260910T032800Z` |
| B | 0.36 | 0.31 | 0.007 | **2.0518** | 4.9824 | 0.000242 (noise) | `variant_save_20260910T040639Z` |
| C | 0.24 | **0.15** | 0.007 | 1.5470 | **3.6497** | 0.0074958 | `variant_save_20260910T044518Z` |
| E | **0.36** | **0.14** | **0.17** | **1.9857** | 3.5344 | **0.020909** | `variant_save_20260910T052352Z` |

Anchor underlying rates: SUD exposed 0.053417 against unexposed 0.035118;
homelessness exposed 0.046770 against unexposed 0.0098922.

## Odds ratio, not risk ratio, from 10 September

The author: *"yes, change it to the odds ratio"*. Both targets always were odds
ratios while the model reported `p_exposed/p_unexposed`, a RISK ratio. The two
agree only for a rare outcome and the odds ratio is the larger, so the model was
scored against a target above the quantity it computed. Measured, the gap is
1.9 per cent on the SUD ratio (1.5505 against 1.5212) and 3.9 per cent on
homelessness (4.9109 against 4.7280) -- small, and always in the direction that
flattered the model.


## B: delta_d = 0.36 lands the SUD odds ratio at 2.0518 against 2.00

A 2.6 per cent overshoot from a single extrapolation, so that parameter is
essentially solved. It also pulled total drug use onto its own target without
being asked to: `b` 0.086822 -> 0.088885 against 0.0890, and `lambda_d` 0.036780
-> 0.037654 against 0.0368. `delta_h` moved only 4.9109 -> 4.9824, which is the
confirmation that the two channels are separate class blocks and that a diagonal
secant is justified rather than merely convenient.

| | anchor | B | target |
| --- | --- | --- | --- |
| SUD odds ratio | 1.5505 | **2.0518** | 2.00 |
| homelessness odds ratio | 4.9109 | 4.9824 | 2.10 |
| `b` | 0.086822 | 0.088885 | 0.0890 |
| `lambda_d` | 0.036780 | 0.037654 | 0.0368 |
| `h_1` | 0.013071 | 0.013445 | 0.0116 |

## OMEGA IS BELOW THE SOLVER FLOOR AND MUST NOT BE FITTED TO AT THIS WEIGHT

At B the child counterfactual moves total drug use from 0.088885 to 0.088907, a
difference of **2.15e-5**, while that run's own `FROZEN CONVERGED` distance is
**2.47e-4**. The signal is an order of magnitude BELOW the resolution of the
equilibrium it is measured on, so B's omega of 0.00024 is solver noise and a
secant drawn through it would be a line through two pieces of noise.

The anchor's 0.00076 sits about twenty times above its own 3.33e-5 and is
marginally real. `fit_child_parameters.py` now computes the signal explicitly
and refuses an omega_c step unless BOTH readings clear five times the frozen
distance; it keeps fitting the two odds ratios meanwhile.

This is also the quantitative explanation of the pre-frozen trap. Pre-frozen the
baseline is 0.0795 against its own fixed point of 0.0889, so the pre-frozen
omega of 0.1027 is mostly measuring the distance from an unconverged state and
almost nothing about the child term.

**What it means for the fit.** At omega_c = 0.007 the child externality is not
observable. The combined point at 0.17 should put it about 24 times higher and
comfortably above the floor, so the fit can proceed -- but no slope estimated
from the current pair means anything.


## C: delta_h CANNOT REACH 2.10. Its floor is about 2.5.

| | anchor | C | target |
| --- | --- | --- | --- |
| `delta_h` | 0.31 | 0.15 | -- |
| homelessness odds ratio | 4.9109 | **3.6497** | 2.10 |
| child of a homeless parent, rate | 0.046770 | 0.035136 | -- |
| child of a housed parent, rate | 0.0098922 | 0.0098793 | -- |
| SUD odds ratio | 1.5505 | 1.5470 | -- |

The unexposed rate does not move at all -- 0.0098922 against 0.0098793 -- while
the exposed rate falls roughly linearly in the penalty. Extrapolated to
`delta_h` = 0, meaning NO homelessness penalty on the child whatsoever, the odds
ratio is still about **2.5**: 2.49 reading the rates linearly, 2.90 reading the
ratio in logs. The target of 2.10 is BELOW the model's floor.

The reason is the channel the author asked to keep: homeless parents are poor,
`rho_intergenerational` is 0.35, and the child inherits that productivity
whether or not a penalty is applied on top. Income persistence ALONE
over-explains Bassuk et al.'s odds ratio.

So `delta_h` is not a dial that reaches 2.10 from above. Either the ratio is
accepted at about 2.5 with `delta_h` near zero -- a 19 per cent overshoot,
outside the author's 10 per cent rule -- or the excess has to come out of the
persistence channel, which is not a child parameter and is the author's call.

The `delta_d` secant across B and C is well behaved by contrast: elasticity
-1.64 in log(1-delta), pointing at delta_d = 0.350 against the 0.36 already
measured at 2.0518.


## E, the author's combined point: delta_d IS SOLVED, and omega has a ceiling

| | model | target | gap |
| --- | --- | --- | --- |
| SUD odds ratio | **1.9857** | 2.00 | **-0.7%** |
| homelessness odds ratio | 3.5344 | 2.10 | +68% |
| `lambda_d` | 0.037097 | 0.0368 | +0.8% |
| `b` | 0.086312 | 0.0890 | -3.0% |
| `h_1` | 0.013270 | 0.0116 | +14.4% |
| `omega` | 0.020909 | 0.18343 | -89% |

**delta_d = 0.36 is the answer.** It hits the SUD odds ratio at 1.9857 against
2.00 and holds `lambda_d` within 0.8 per cent at the same time.

**omega IS STRONGLY CONCAVE IN omega_c AND CANNOT REACH ITS TARGET WITH b HELD.**
The anchor and C both sit at omega_c = 0.007 and both give omega about 0.0075;
E at 0.17 gives 0.0209. A TWENTY-FOUR fold rise in the weight bought a 2.8 fold
rise in omega, an elasticity of about 0.32. A linear reading -- which is what
produced the 0.17 guess -- was wrong by an order of magnitude.

The reason is visible in the counterfactual's own numbers:

    baseline users        0.086312
    counterfactual users  0.088117   <- the child term switched off

The counterfactual level is what use would be with no child concern at all, and
it is pinned by `addiction_scalar_1`. So omega = 0.18343 requires the BASELINE
to sit at 0.088117/1.18343 = **0.0745**, sixteen per cent below b's own target of
0.0890. omega and b cannot both be hit while addiction_scalar_1 is held: getting
the child externality to the size the data implies means the child term must
suppress use by sixteen per cent, and having that AND b = 0.0890 requires
addiction_scalar_1 to rise to compensate.

**So omega_c and b's parameter have to be fitted jointly.** That is an amendment
to the author's sequencing of 10 September, which held b fixed while the three
child parameters were fitted, and it is flagged rather than quietly acted on.

## Where step 1 ends

| | value | moment | target | verdict |
| --- | --- | --- | --- | --- |
| `delta_d` | **0.36** | 1.9857 | 2.00 | **solved** |
| `delta_h` | -- | floor ~2.5 | 2.10 | target below the model's floor; the author's call |
| `omega_c` | -- | 0.0209 at 0.17 | 0.18343 | unreachable with b held; needs a joint fit |
