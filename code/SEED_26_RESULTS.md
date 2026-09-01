# SEED_26: twelve controlled arms from point_9a13317e65

One coordinate moved per arm from the anchor, so each arm yields a controlled
pair `next_batch.py` can form a bracket or an elasticity from. The anchor is

```
b = 0.086789 (-2.5%)   lambda_d = 0.035791 (-2.7%)   sixteen invariants PASS
```

The **coupling** column is what the arm did to `b` and `lambda_d`, and it is the
column that decides whether a moment can be closed on its own or needs a
drug-block repair after every step.

## Arm 1 -- max_food_cost 0.007331089 -> 0.017676 (x2.411), owns cbar

`point_645ca85b44`, all sixteen invariants PASS.

| quantity | anchor | arm | predicted | measured exponent |
|---|---|---|---|---|
| food stamps / output | 0.000701 | 0.003295 | 0.004200 | **1.759** (flat density says 2) |
| recipient share | 0.048961 | 0.101666 | 0.118050 | **0.830** (flat density says 1) |

**The mechanism holds and the flat-density assumption does not, which is the
outcome that was written down in advance as the alternative.** The prediction
was that spending goes as the square of the floor and recipients as the first
power, because the benefit is `max(0, cbar - 0.30*y)` and the eligible range is
narrow. Both exponents come in below their flat-density values, which is what a
FALLING income density over that range does to both at once. The relationship
between the two survives: the ratio of the measured exponents is **2.118 against
the predicted 2.000**, six per cent out. So the formula was right about how the
two moments move together and wrong about the density, and the useful output is
a measured elasticity rather than an assumed one.

On the measured exponent, closing the rest of cbar needs `max_food_cost` x1.148
to **0.020292**, which also predicts a recipient share of 0.114 against 0.125.

### But max_food_cost is strongly coupled to the drug block

| | anchor | arm | move | vs target after |
|---|---|---|---|---|
| b | 0.086789 | 0.103693 | **+19.5%** | +16.5% |
| lambda_d | 0.035791 | 0.046292 | **+29.3%** | +25.8% |

Raising the food floor raises drug use substantially, which is economically what
it should do -- the floor relaxes the budget constraint of exactly the poorest
households, who are the marginal users -- but it means **cbar cannot be closed
by moving its own instrument and stopping**. It joins the coupled list that
`restore.py` was written for: every step on the food floor needs a drug-block
repair behind it, and the step sizes have to stay small enough for that repair
to be possible.

## Arm 2 -- utility_cost_of_treatment 0 -> 2.0, owns tau_u

`point_4150720d61`, all sixteen invariants PASS.

**The corner is broken and the target is bracketed.** `tau_u` goes from
0.9999949 at a price of zero to **0.169372** at a price of 2.0, against a target
of 0.245. It was +308 per cent and is now -30.9 per cent, on the other side, so
two measured points straddle the target and no elasticity is needed. Log-linear
in the price puts the root at `utility_cost_of_treatment` = **1.5842**.

This confirms in one run that the +308 per cent was never a fit failure. Treatment
was free, so everyone carrying the disorder took it; given a price, take-up
behaves and is if anything too sensitive rather than too flat.

### The prediction about the coupling's SIGN was wrong

Written down before the arm ran: *"Charging for treatment lowers take-up, which
lowers recovery, which raises the disorder rate: `lambda_d` should rise when this
parameter leaves zero, and `b` with it."*

It does the opposite, and by a lot:

| | anchor | arm | move |
|---|---|---|---|
| b | 0.086789 | 0.046550 | **-46.4%** |
| lambda_d | 0.035791 | 0.016748 | **-53.2%** |

The recovery channel is real but it is second order. The first-order effect runs
through the ANTICIPATION of the price: a household deciding whether to use knows
that the disorder now carries either an untreated future or a costly treatment,
so the disorder is worse ex ante and fewer households walk into it. Deterrence
beats the recovery loss by enough to cut the drug stock nearly in half. The
earlier note in CALIBRATION_STATE.md predicting a rise is wrong and is corrected
by this measurement.

### The two coupled arms pull in OPPOSITE directions, which is useful

| arm | b | lambda_d |
|---|---|---|
| max_food_cost x2.411 | +19.5% | +29.3% |
| utility_cost_of_treatment 0 -> 2.0 | -46.4% | -53.2% |

`cbar` needs the food floor UP, which raises the drug block; `tau_u` needs the
treatment price UP, which lowers it. Moved together they partly cancel, so the
pair may be closable with a much smaller drug-block repair than either alone
would need. That is a hypothesis from two measured arms and is worth a joint
point once the cheap arms are in, but it is not yet a measurement of the joint
move.
