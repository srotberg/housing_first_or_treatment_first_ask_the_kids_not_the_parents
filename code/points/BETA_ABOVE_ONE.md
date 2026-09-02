# beta above one: three arms at discount_factor > 1

Three points off `point_35e8286c4e`, moving `discount_factor` and nothing else.

    discount_factor  0.99980 -> 1.00200   point eca09faa90
                             -> 1.00500   point b8d36c0646
                             -> 1.01500   point 1ffd652557

## Headline

**The instrument was never exhausted.** `beta` was reported as having an
exhausted instrument because closing the gap "wants a discount factor above
one". That reasoning was wrong, and these three arms measure how wrong. A
discount factor above one is admissible here: the value function is backward
induction over a finite life span (`do age_index=life_span,1,-1`, line 15935),
so the discounted sum is finite for any `discount_factor`, and the handover has
always clamped to **[0.5, 1.05]** rather than to 1:

    discount_factor=min(max(handover_value,0.5d0),1.05d0)     line 35295

All three arms cleared that clamp untouched. `beta` runs 2.4532 at the base to
**4.3665** at 1.01500 -- it crosses 2.5, crosses 3.0, and by the top arm is most
of the way to the band's upper edge of 4.5. The highest value ever tried before
this batch was 0.99995.

**Both 2.5 and 3.0 are bracketed by measured pairs on one economy.** Neither
figure was out of reach; the old 3.0 target was reachable all along.

## The three runs are sound

|                   | eca09faa90 | b8d36c0646 | 1ffd652557 |
|-------------------|-----------:|-----------:|-----------:|
| `discount_factor` |    1.00200 |    1.00500 |    1.01500 |
| solve time        |     14 min |     14 min |     14 min |
| `HANDOVER`        |   42 of 42 |   42 of 42 |   42 of 42 |
| `MODEL`           | bb2cd48b81 | bb2cd48b81 | bb2cd48b81 |
| INVARIANTS        |   all PASS |   all PASS |   all PASS |

**The three `MODEL` lines agree**: all three are `bb2cd48b81`. The re-solved
base `point_35e8286c4e` carries the same hash, so the base and all three arms
sit on one economy.

Neither watched failure mode fired:

- **`beta IS PINNED AT A BOUND` did not appear** in any of the three runs. It
  should not have, and it did not: 1.01500 is well inside the 1.05 ceiling.
- **Nothing non-finite.** No `NaN`, no `Infinity`, no `Inf`, no `****` field
  overflow anywhere in the three outputs, and each reports `INVARIANTS: all
  PASS` across sixteen invariants. The concern that a discount factor above one
  would amplify later-life utility into a divergent or non-finite solve is not
  borne out at these values. The solves are as clean as the base.

## The ladder

`beta` at each `discount_factor`, all else equal.

| `discount_factor` | `beta` | point | MODEL | |
|------------------:|-------:|-------|-------|---|
| 0.99950 | 2.4133 | 932e3cd75a | b8dc1077ad | old economy |
| 0.99980 | 2.4528 | 35e8286c4e | b8dc1077ad | superseded by the re-solve below |
| 0.99995 | 2.4695 | 44e91bb1d7 | b8dc1077ad | old economy |
| **0.99980** | **2.4532** | 35e8286c4e | bb2cd48b81 | base, re-solved |
| **1.00200** | **2.7287** | eca09faa90 | bb2cd48b81 | measured here |
| **1.00500** | **3.1277** | b8d36c0646 | bb2cd48b81 | measured here |
| **1.01500** | **4.3665** | 1ffd652557 | bb2cd48b81 | measured here |

The four bold rows are ONE economy and are the ladder. The three `b8dc1077ad`
rows are the old economy, are labelled as such, and are **not** fitted with the
new ones; no slope is taken across the hash boundary.

`point_35e8286c4e` appears twice because it was re-solved on the 2.5-target
source (commit `68c3578`) while this batch was in flight. The re-solve is the
row that counts. The two solves differ by very little -- `beta` 2.4528 against
2.4532, four parts in ten thousand -- which is evidence that the 3.0 -> 2.5
target change did not move the economy, but the formal equivalence is still
unrecorded: there is no `EQUIVALENT_MODELS` entry and the semantic hashes differ
(`2f7c317e75` against `08f8470b5d`). Within each half the vectors were checked
and are identical except in `discount_factor`.

## What brackets what

Only same-economy pairs can bracket. On `bb2cd48b81`, with the re-solved base:

- **2.5 is bracketed by 0.99980 and 1.00200** -- 2.4532 below, 2.7287 above.
- **3.0 is bracketed by 1.00200 and 1.00500** -- 2.7287 below, 3.1277 above.

Both brackets are tight in `beta` and narrow in the instrument: 2.5 is crossed
somewhere inside a 0.0022 window of `discount_factor`, and 3.0 inside a 0.0030
window.

No extrapolation past the measured arms is offered, and nothing here locates the
`discount_factor` returning exactly 2.5 or exactly 3.0 -- only which measured
pair straddles each. The ladder is monotone and steeply convex over the range
measured: the same 0.003 step in `discount_factor` buys 0.40 of `beta` between
1.00200 and 1.00500, and the 0.010 step above that buys 1.24 more.

Note that 1.00200 -- the smallest step above one in this batch -- **overshoots
2.5 by +9.1 per cent**. An overshoot is as much a miss as a shortfall, so the
useful arm for the 2.5 target is below 1.00200, not at it. Against the old 3.0
figure the same point reads -9.0 per cent, and 1.00500 reads +4.3 per cent.

## The nine round-1 moments

Targets as given: `aleph` 80.0, `beta` BAND 2.5-4.5, `omega_l` 0.40, `sigma_y`
0.172, `tau_l` 0.224, `pi_eu` 0.139, `pi_V` 0.266, `cbar` 0.0042, `w_bot`
0.0250.

| moment | target | 0.99980 base | 1.00200 | 1.00500 | 1.01500 |
|--------|-------:|---:|---:|---:|---:|
| `aleph`   | 80.0         | 76.0677 | 78.6669 | 81.6898 | **95.0551** |
| `beta`    | BAND 2.5-4.5 |  2.4532 |  2.7287 |  3.1277 |  4.3665 |
| `omega_l` | 0.40         |  0.3635 |  0.3646 |  0.3660 |  0.3709 |
| `sigma_y` | 0.172        |  0.1691 |  0.1691 |  0.1691 |  0.1691 |
| `tau_l`   | 0.224        |  0.2257 |  0.2242 |  0.2219 |  0.2152 |
| `pi_eu`   | 0.139        |  0.1343 |  0.1343 |  0.1343 |  0.1343 |
| `pi_V`    | 0.266        |  0.2556 |  0.2553 |  0.2476 |  0.2474 |
| `cbar`    | 0.0042       |  0.0039 |  0.0039 |  0.0038 | **0.0036** |
| `w_bot`   | 0.0250       |  0.0247 |  0.0250 |  0.0251 |  0.0250 |

Per cent gaps. `beta` follows the repository's own `gap()` in `gaps.py`: a
banded moment scores zero anywhere inside 2.5-4.5 and otherwise the distance to
the nearer edge, so 0.0 means in band, not on target.

| moment | 0.99980 base | 1.00200 | 1.00500 | 1.01500 |
|--------|--------:|--------:|--------:|--------:|
| `aleph`   |  -4.9 |  -1.7 |  +2.1 | **+18.8** |
| `beta`    |  -1.9 |   0.0 |   0.0 |   0.0 |
| `omega_l` |  -9.1 |  -8.9 |  -8.5 |  -7.3 |
| `sigma_y` |  -1.7 |  -1.7 |  -1.7 |  -1.7 |
| `tau_l`   |  +0.8 |  +0.1 |  -0.9 |  -3.9 |
| `pi_eu`   |  -3.4 |  -3.4 |  -3.4 |  -3.4 |
| `pi_V`    |  -3.9 |  -4.0 |  -6.9 |  -7.0 |
| `cbar`    |  -6.3 |  -7.2 |  -8.4 | **-13.1** |
| `w_bot`   |  -1.1 |  +0.2 |  +0.2 |  -0.2 |
| **inside ten per cent** | **9/9** | **9/9** | **9/9** | **7/9** |

For the record, the two old-economy rows are 9 of 9 as well: 0.99950 with
`beta` -3.5 and `w_bot` -4.3, and 0.99995 with `beta` -1.2 and `w_bot` -0.9.

### w_bot did not break

`w_bot` was flagged as the moment most likely to break here, on the reasoning
that a more patient population saves more. **It did not break. It improved onto
target and then held.** It runs -1.1 per cent at the base and then +0.2, +0.2,
-0.2 across the three arms above one -- the best-matched of the nine at every
arm measured, and flat in the instrument that moves `beta` by 78 per cent.

The reasoning had the direction right and the consequence wrong. More patience
does raise saving, but `w_bot` is a *share* -- net worth of the bottom half over
total net worth -- and the extra saving accrues across the whole distribution,
so the ratio barely moves while `beta`, a level ratio of wealth to output,
climbs steeply. `beta` and `w_bot` are close to orthogonal in `discount_factor`
over this range, which is the useful part of the result: the instrument that
closes `beta` does not cost the wealth-share moment.

### What breaks instead is aleph

The binding cost of pushing `discount_factor` this far is `aleph`, not `w_bot`.
`aleph` is monotone in `discount_factor` at every row and leaves the ten per
cent range between 1.00500 (+2.1) and 1.01500 (**+18.8**). `cbar` follows it out
at the top arm (-13.1). Both are comfortably inside at 1.00200 and 1.00500.

So the usable range of this instrument is bounded by `aleph`, well below the
1.05 clamp: **1.00500 is nine of nine, 1.01500 is seven of nine.**

### The best of the arms

`1.00200` is nine of nine with the largest margin -- its worst moment is
`omega_l` at -8.9 per cent, and `omega_l` sits at roughly -9 per cent at every
row in this table, above and below one alike. It does not respond to
`discount_factor` and is not this parameter's to fix. Setting it aside, every
other moment at 1.00200 is inside 7.2 per cent and four of the nine inside 2.

`1.00500` is also nine of nine and puts `beta` nearest the old 3.0 figure
(3.1277, +4.3 per cent) at the cost of `aleph` crossing from below to above its
target and `pi_V` and `cbar` drifting further out.

## Two changes landed on the branch while this batch ran

Reported because they bound what the numbers above are good for.

1. **The unemployment target moved 13.9 -> 4.9 per cent** (commit `de9d7a3`).
   `unemployment_rate_data` is now `0.049`. The table above scores `pi_eu`
   against 0.139 as specified for this batch. Against the new target every row
   here, base included, reads **+174 per cent** and fails -- but that is the
   target moving, not anything these arms did: `pi_eu` is 0.1343 at all four
   rows and is flat in `discount_factor` to three decimal places.
2. **The negative asset grid went from 3 points to 7** (commit `b03b86b`).

The current source is `e550ca2c82` / semantic `0afbde300f`, so these arms were
solved two model revisions back and their nine-of-nine counts do not transfer to
the current economy. `CALIBRATION_STATE.md` records zero scoreable points on
`0afbde300f`.

**What does transfer is the finding itself.** That `discount_factor` above one
is admissible, unclamped below 1.05, solves cleanly with finite moments and
passing invariants, and carries `beta` across both 2.5 and 3.0 while leaving
`w_bot` on target -- these are properties of the instrument, not of the target
vector. `CALIBRATION_STATE.md` states that the move to a 4.9 per cent
unemployment target breaks `beta` and `w_bot` through precautionary saving and
that both must be re-closed. This measurement says the instrument for re-closing
`beta` exists, has roughly 0.010 of usable range above one before `aleph` gives
way, and does not cost `w_bot` on the way.

## Caveats

- Three arms, one parameter, no search. Nothing here says the vector at 1.00200
  or 1.00500 is a better calibration overall, only that it is nine of nine on
  the round-1 moments as the base is.
- The brackets are on `bb2cd48b81` and would have to be re-measured on the
  current source.
- `omega_l` is roughly -9 per cent at every arm and is untouched by this
  instrument.
- The `b8dc1077ad` rows remain formally a different economy; the re-solve is
  strong evidence they are equivalent, but no `EQUIVALENT_MODELS` record exists.
