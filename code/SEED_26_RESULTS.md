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
