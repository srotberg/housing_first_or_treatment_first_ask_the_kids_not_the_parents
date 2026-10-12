# batch_ssi_ab.txt — is the SSI floor what made the arms slow?

Four arms of `batch_kkk.txt` were launched and none finished on schedule. The
CONTROL, which runs the frozen quantile grid whose archive median is **3
minutes**, was still solving at **13 minutes**. So the slowdown is not the KKK
transition — it is hitting the frozen grid too.

Two suspects were named. This batch settles the first of them.

## The evidence that points at the SSI floor

Every seven-node point in the archive, and its solve time:

| ssi_floor_takeup | n | times |
|---|---|---|
| 0.0 or absent | 22 | 2–4 min |
| 0.5 | 0 | never run |

**`ssi_floor_takeup=0.5` has never been solved.** It is in all four arms of
`batch_kkk.txt` and in none of the fast points.

The mechanism is plausible rather than established. At 0.5 the floor is
`0.5 * 0.1774 = 0.0887` and the bottom node's PIA is `0.9 * 0.0317 = 0.0285`,
so the poorest retirees' income is lifted by a factor of **3.1**. That moves a
large block of households from "cannot afford the cheapest rental" to "can",
which is a jump in rental demand, and the rental market price has to travel to
meet it. `distance_rental_market` is one of the terms in the calibration loop's
`do while` and it is not frozen, so a slow-converging rental market lengthens
the run directly.

## The other suspect, and why this batch does not test it

The outer calibration loop is a `do while` over about forty distances with **no
`loop_count < max` term**, so a point runs until every distance is under its
stopping rule rather than for a fixed number of loops.

That is a real hazard but it is NOT the sigma instrument, which was the first
guess. `freeze_fitted_internals=1`, so `freeze_sd_permanent_productivity=1`, so
both `sd_permanent_productivity_adjuster` and `kkk_sigma_scale_adjuster` are
zero and `distance_sd_permanent_productivity` is `(1-freeze)*|gap| = 0`. It
cannot hold the loop open. The same is true of every other frozen internal.
What is left un-frozen is the equilibrium block — the rental market, average
labour income, the median, the standard deduction — and those are exactly the
things the SSI floor moves.

So the two suspects are not independent, and this A/B tests the one that can
be tested in two solves.

## The design

Both lines run **in one container**, so the build is paid once and the two
share a CPU. That removes the confound that has been sitting under every
timing claim tonight: the archive's 3 minutes was measured on other machines.

| line | vector | expectation if the SSI floor is the cause |
|---|---|---|
| 1 | the committed defaults, `ssi_floor_takeup=0.0` | 2–4 min, matching the archive |
| 2 | the same vector with `ssi_floor_takeup=0.5` | much longer |

If line 1 is also slow, the SSI floor is exonerated and the cause is something
that changed in the source tonight, which is then the thing to bisect.
