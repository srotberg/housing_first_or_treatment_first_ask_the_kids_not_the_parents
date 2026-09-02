# ROUND 2 PASS B -- three more points on two drug-block instruments

`code/batch_round2_b.txt`, three lines, run one at a time from the repository
root, each allowed to finish before the next was started and each committed
before the next was fired. No rebase was taken between lines. Borrowing is off
throughout (`include_unsecured_borrowing=0`). `addiction_scalar_1` is dropped
from this pass: `ROUND2_ARMS.md` arm 2 moved its own moment the wrong way and
cost four round-1 moments at once.

The base is the round-1 point `35e8286c4e` as solved on `MODEL b8dc1077ad`, now at
`code/points_superseded/point_35e8286c4e.20260902T125525Z.txt` -- see the provenance
section at the end. It is the eight-of-nine point named in
`code/CALIBRATION_STATE.md`. Each line moves ONE round-2 instrument off it and
nothing else.

| | instrument move | tag | MODEL | outcome |
|---|---|---|---|---|
| line 1 | `relative_share_of_addiction_1` 0.463 -> **0.300** | `16e404103d` | `b8dc1077ad` | solved, 15 min |
| line 2 | `relative_share_of_addiction_1` 0.463 -> **0.200** | `460811e3cb` | `b8dc1077ad` | solved, 14 min |
| line 3 | `lambda_addiction` 2.79953 -> **50.00000** | `99929a9d41` | `b8dc1077ad` | solved, 15 min |

## The three MODEL lines agree, and that was checked rather than assumed

**All three points carry `MODEL b8dc1077ad`.** So does the base `35e8286c4e`, so
do both round-2 arms quoted below as rows (`82a955b244`, `e7c7daf5ca`), and so
did the working tree AT THE TIME THE BATCH RAN: `md5sum code/housing_first_or_treatment_first_SR_v1.f90`
is `b8dc1077adc90fe0d9b497289e93e7c5`, ten characters `b8dc1077ad`. Every number
here is a within-economy comparison against a base measured on the same source.
No source change landed mid-batch. `housing_first_or_treatment_first_SR_v1.f90`
was not edited by this batch; the head has since moved to `e550ca2c82` through two
upstream commits, which the provenance section at the end records.

All three report `HANDOVER OK: 42 of 42 parameters applied` and `INVARIANTS: all
PASS`, 16 of 16, zero `INVARIANT FAIL`. Nothing segfaulted and no build failed.

Each line's `VECTOR` was diffed against the base coordinate by coordinate, all
forty-three names on both sides:

    line 1 vs base:  1 difference, relative_share_of_addiction_1 0.463 -> 0.300
    line 2 vs base:  1 difference, relative_share_of_addiction_1 0.463 -> 0.200
    line 3 vs base:  1 difference, lambda_addiction 2.79953 -> 50.00000

So each line is a matched pair with the base in exactly its own instrument.

---

# Lead: line 1 brackets `theta`, and it costs four round-1 moments to do it

Two things happened at once and they point opposite ways.

**`theta` is bracketed for the first time.** `relative_share_of_addiction_1` at
0.400 gives `theta` 0.240079, above the 0.162 target; at 0.300 it gives
**0.058517, below it**. The target lies between two measured points.

**The same step takes round 1 from eight of nine to four of nine.** Line 1 loses
`omega_l`, `pi_eu`, `cbar` and `w_bot`, all four of which were inside ten per
cent at the base. That is the same failure mode `ROUND2_ARMS.md` flagged on arm
2, on a different instrument, and this time it is the instrument that works.

Line 2, at 0.200, loses the same four and loses them harder -- `pi_eu` -46.79%,
`cbar` -46.09%, `w_bot` -43.21% -- and does not produce a `theta` reading at all
(see the sentinel section below).

So the bracket on `theta` and the round-1 fit are in direct conflict along this
instrument over 0.463 -> 0.300. Nothing here says where between 0.400 and 0.300
that trade turns, and nothing below estimates it.

---

## The two ladders, in one place

Percentages are (model - target) / target. Rows marked `--` were measured in
`ROUND2_ARMS.md`; rows marked `**` are measured here.

### `relative_share_of_addiction_1` owns `theta`, drug spending share, target 0.162

| `relative_share_of_addiction_1` | tag | `theta` | gap |
|---|---|---|---|
| 0.463 (base) | `35e8286c4e` | 0.304601 | +88.03% |
| 0.400 -- | `e7c7daf5ca` | 0.240079 | +48.20% |
| **0.300** ** | `16e404103d` | **0.058517** | **-63.88%** |
| **0.200** ** | `460811e3cb` | **not measured (sentinel -1)** | -- |

**BRACKETS.** 0.400 (0.240079, above) and 0.300 (0.058517, below) straddle the
0.162 target. This is the first bracket found on any round-2 moment.

The step is violently non-linear over the measured range. 0.463 -> 0.400, a cut
of 0.063, moved `theta` by -0.064522. 0.400 -> 0.300, a cut of 0.100, moved it by
-0.181562, nearly three times as far for less than twice the step. The bracket is
therefore wide in the moment even though it is narrow in the instrument, and no
crossing point inside it is estimated here.

### `lambda_addiction` owns `b`, total drug users, target 0.089

| `lambda_addiction` | tag | `b` | gap |
|---|---|---|---|
| 2.79953 (base) | `35e8286c4e` | 0.408622 | +359.13% |
| 8.00000 -- | `82a955b244` | 0.393509 | +342.15% |
| **50.00000** ** | `99929a9d41` | **0.366047** | **+311.29%** |

**Does NOT bracket. All three points lie above the target, and far above it.**

---

## `b` has no working instrument in this range

This is the finding of line 3, and it matters more than the size of the gap.

Movement in `b` per unit of `lambda_addiction`, on the two measured intervals:

| interval | change in `lambda_addiction` | change in `b` | per unit |
|---|---|---|---|
| 2.79953 -> 8.00000 | +5.20047 | -0.015113 | **-0.00290612** |
| 8.00000 -> 50.00000 | +42.00000 | -0.027462 | **-0.00065386** |

**The response per unit falls by a factor of 4.44 as the instrument rises.** The
instrument is not merely slow, it is flattening: an eight-fold larger step in
`lambda_addiction` bought less than twice the movement in `b`.

Taken end to end, 2.79953 -> 50.00000 is a **17.9-fold increase in the
instrument** and it moved `b` from 0.408622 to 0.366047, a fall of 0.042575, or
10.4 per cent of its own value. `b` goes from 4.59x its target to 4.11x it. The
target is 0.089 and the instrument's own order-of-magnitude arm leaves the moment
four times above it.

**`b` has no working instrument in this range.** `lambda_addiction` cannot reach
the target from 2.79953 by being pushed, and the measured curvature runs the
wrong way for pushing it further.

Recorded and not extrapolated: no value of `lambda_addiction` beyond 50.0 is
estimated, no crossing is projected, and the two slopes above are two secants
between three measured points, not a derivative.

### The one thing that did move `b`

`b` came to within +2.38% of its target at line 2 -- 0.091116 against 0.089 --
and `lambda_addiction` was **at its base value 2.79953** there. What moved it was
`relative_share_of_addiction_1`, `theta`'s instrument, cut to 0.200. Over the same
step `lambda_d` fell to 0.023780, **below** its 0.0368 target.

So on the four points of the `relative_share_of_addiction_1` ladder:

| `relative_share_of_addiction_1` | `b` (target 0.089) | `lambda_d` (target 0.0368) |
|---|---|---|
| 0.463 (base) | 0.408622 | 0.294785 |
| 0.400 | 0.405744 | 0.269404 |
| **0.300** | **0.351526** | **0.186283** |
| **0.200** | **0.091116** | **0.023780** |

**`lambda_d` BRACKETS on this ladder**: 0.300 gives 0.186283 (above target) and
0.200 gives 0.023780 (below it). `b` does not bracket -- 0.091116 is still above
0.089 -- but it is +2.38% away, against +311.29% at the far end of its own
instrument's ladder.

This is the same mismatch `ROUND2_ARMS.md` recorded and it is now much larger:
**the instrument assigned to `theta` moves `b` and `lambda_d` across their whole
range, while the instrument assigned to `b` barely moves `b` at all.** That is an
observation about these seven points; it is not a Jacobian and no step size, sign
or crossing is inferred from it.

---

## Round 1's nine moments at each point

`beta` is a BAND, 3.0 to 4.5, scored in or out with its shortfall quoted against
the 3.0 floor. Everything else is (model - target) / target. **Bold marks a
moment outside ten per cent.**

| moment | target | base | `l`8.0 -- | `r`0.400 -- | **`r`0.300** | **`r`0.200** | **`l`50.0** |
|---|---|---|---|---|---|---|---|
| `aleph` value of life / income | 80.0 | 75.828008 | 75.662297 | 77.659727 | 78.963148 | 77.129999 | 74.357300 |
| `beta` wealth over output | BAND 3.0-4.5 | 2.452826 | 2.492457 | 2.382602 | 2.205863 | 1.895766 | 2.501607 |
| `omega_l` labour supply / hours | 0.40 | 0.363505 | 0.364203 | 0.362301 | 0.356669 | 0.346716 | 0.364550 |
| `sigma_y` bottom half earnings share | 0.172 | 0.169050 | 0.169050 | 0.169050 | 0.169050 | 0.169050 | 0.169050 |
| `tau_l` average labour income tax | 0.224 | 0.226321 | 0.227453 | 0.226199 | 0.228048 | 0.235223 | 0.229745 |
| `pi_eu` unemployment rate | 0.139 | 0.134279 | 0.145312 | 0.128701 | 0.111355 | 0.073962 | 0.150927 |
| `pi_V` eligibles with a voucher | 0.266 | 0.255978 | 0.255889 | 0.256401 | 0.258054 | 0.255444 | 0.258316 |
| `cbar` food stamps / income | 0.0042 | 0.003935 | 0.004265 | 0.003790 | 0.003368 | 0.002264 | 0.004433 |
| `w_bot` net worth share, bottom half | 0.0250 | 0.024270 | 0.027391 | 0.024994 | 0.021806 | 0.014199 | 0.026601 |

and the same as gaps:

| moment | base | `l`8.0 -- | `r`0.400 -- | **`r`0.300** | **`r`0.200** | **`l`50.0** |
|---|---|---|---|---|---|---|
| `aleph` | -5.21% | -5.42% | -2.93% | -1.30% | -3.59% | -7.05% |
| `beta` | **OUT -0.5472** | **OUT -0.5075** | **OUT -0.6174** | **OUT -0.7941** | **OUT -1.1042** | **OUT -0.4984** |
| `omega_l` | -9.12% | -8.95% | -9.42% | **-10.83%** | **-13.32%** | -8.86% |
| `sigma_y` | -1.72% | -1.72% | -1.72% | -1.72% | -1.72% | -1.72% |
| `tau_l` | +1.04% | +1.54% | +0.98% | +1.81% | +5.01% | +2.56% |
| `pi_eu` | -3.40% | +4.54% | -7.41% | **-19.89%** | **-46.79%** | +8.58% |
| `pi_V` | -3.77% | -3.80% | -3.61% | -2.99% | -3.97% | -2.89% |
| `cbar` | -6.31% | +1.55% | -9.77% | **-19.80%** | **-46.09%** | +5.55% |
| `w_bot` | -2.92% | +9.56% | -0.02% | **-12.78%** | **-43.21%** | +6.40% |

**Inside ten per cent, out of nine:**

| point | count | out |
|---|---|---|
| base `35e8286c4e` | **8 of 9** | `beta` |
| `lambda_addiction` 8.0 `82a955b244` -- | **8 of 9** | `beta` |
| `relative_share_of_addiction_1` 0.400 `e7c7daf5ca` -- | **8 of 9** | `beta` |
| **`relative_share_of_addiction_1` 0.300 `16e404103d`** | **4 of 9** | `beta`, `omega_l`, `pi_eu`, `cbar`, `w_bot` |
| **`relative_share_of_addiction_1` 0.200 `460811e3cb`** | **4 of 9** | `beta`, `omega_l`, `pi_eu`, `cbar`, `w_bot` |
| **`lambda_addiction` 50.0 `99929a9d41`** | **8 of 9** | `beta` |

### Lines 1 and 2 each break four round-1 moments, and it is the same four

The order asked that this lead if it happened, and it happened on both
`relative_share_of_addiction_1` lines. The four lost are identical at 0.300 and
at 0.200, and they worsen monotonically along the ladder:

| moment | 0.463 base | 0.400 | **0.300** | **0.200** |
|---|---|---|---|---|
| `omega_l` | -9.12% | -9.42% | **-10.83%** | **-13.32%** |
| `pi_eu` | -3.40% | -7.41% | **-19.89%** | **-46.79%** |
| `cbar` | -6.31% | -9.77% | **-19.80%** | **-46.09%** |
| `w_bot` | -2.92% | -0.02% | **-12.78%** | **-43.21%** |

`pi_eu` and `cbar` roughly double their gap at each of the last two steps and
`w_bot` goes from on target at 0.400 to -43% at 0.200. `beta`, already out
everywhere, also falls furthest here: 1.895766 at 0.200 is 1.1042 below the floor
against 0.5472 at the base, the worst `beta` measured in either round-2 pass.

Against that, `aleph` is best on this ladder, not worst: -1.30% at 0.300 is the
closest reading of `aleph` at any point in either pass. And `sigma_y` is
identical to all sixteen digits at all six points -- no round-2 instrument on
either ladder touches it.

### Line 3 holds round 1 at eight of nine

`lambda_addiction` at 50.0 loses nothing that was held. It is the third point in
this pass and the second on its ladder to stay at eight of nine, and its margins
are comfortable rather than borderline: `w_bot` +6.40% where the 8.0 arm was at
+9.56%, `cbar` +5.55%, `pi_eu` +8.58%. `beta` is the best of all six points at
2.501607, still out of band. `aleph` is the worst of the six at -7.05%, still
inside ten per cent.

So the instrument that does nothing to its own moment also does very little
damage. That is consistent with inertness and is not independent evidence of it.

---

## `theta` at `relative_share_of_addiction_1` = 0.200 is a sentinel, not a value

The point file reads:

    MOMENT theta     drug spending share         model=  -1.0000000000000000       target=  0.16200000047683716

**-1 is the model's "not computable" flag, not a measurement.** It is returned by
`weighted_drug_share_now()` at `code/housing_first_or_treatment_first_SR_v1.f90:6505`,
which computes the share on the experimenter branch and the addict branch and
falls through to `share_1=-1` only when NEITHER branch passes its validity test.
Each branch requires positive mass, a non-negative share, and total income above
one tenth of average labour income times that mass.

The point is otherwise fully solved: `HANDOVER OK: 42 of 42`, `INVARIANTS: all
PASS`, 16 of 16, and the drug block is populated -- `b` 0.091116, `lambda_d`
0.023780, use rates and band diagnostics all present, `DIAG mean drug quantity,
users = 0.019818`. So the economy exists and has drug users in it; the share
statistic specifically did not qualify.

This was NOT investigated further and the Fortran was NOT edited, per the order.
**`theta` at 0.200 is treated throughout this file as unmeasured.** It is not
read as a value below target, it is not used as a bracket endpoint, and the -1
is not differenced against anything. The `theta` bracket claimed above rests on
0.400 and 0.300 only, both of which are real readings.

---

## Every line moved moments it does not own

Deltas off the base, on the three drug-block moments:

| | `lambda_d` (owned by `addiction_scalar_1`) | `b` (owned by `lambda_addiction`) | `theta` (owned by `relative_share_of_addiction_1`) |
|---|---|---|---|
| `lambda_addiction` 8.0 -- | +0.037905 | *owned:* -0.015113 | -0.051366 |
| `relative_share_of_addiction_1` 0.400 -- | -0.025381 | -0.002878 | *owned:* -0.064522 |
| **`relative_share_of_addiction_1` 0.300** | **-0.108503** | **-0.057096** | *owned:* **-0.246084** |
| **`relative_share_of_addiction_1` 0.200** | **-0.271006** | **-0.317507** | *owned:* not measured |
| **`lambda_addiction` 50.0** | **+0.050180** | *owned:* **-0.042575** | **-0.049032** |

Two readings deserve the author's eye, and both are statements about these seven
points only:

- **`relative_share_of_addiction_1` moved `b` by -0.317507 over its full ladder,
  while `b`'s own instrument moved it by -0.042575 over a 17.9-fold increase.**
  Seven and a half times as far, from a much smaller relative move.
- **`lambda_addiction` moves `lambda_d` the WRONG way and keeps doing it**:
  +0.037905 at 8.0 and +0.050180 at 50.0, against a moment already eight times
  its target. Raising `b`'s instrument makes the disorder rate worse
  monotonically over the whole measured range.

On the lines measured here the assigned ownership does not match which instrument
drives which moment. That is an observation about five steps at five particular
sizes, not a Jacobian; no step size, sign or crossing point is inferred from it,
and none should be read into it.

---

## Provenance: the branch head moved under this batch, and the base file moved with it

Recorded because the numbers above cannot be checked against the repository as it
now stands without it.

**Every point in this file was measured on `MODEL b8dc1077ad`**, and so was the
base they are all differenced against. That has not changed and nothing above is
affected. But two commits landed on
`claude/two-period-addiction-hazard-d7gb61` while this batch was running, and the
single rebase taken after line 3 brought them in:

- `68c3578`, which **re-solved `point_35e8286c4e` on a newer source** and moved
  the `b8dc1077ad` reading to
  `code/points_superseded/point_35e8286c4e.20260902T125525Z.txt`. The file now at
  `code/points/point_35e8286c4e.txt` carries `MODEL bb2cd48b81` and is NOT the
  base used here.
- `de9d7a3`, which changed **`unemployment_rate_data` from 0.139 to 0.049** on the
  author's instruction, giving source `e550ca2c82`, which is what the working tree
  holds now.

**The base for every comparison in this file is
`code/points_superseded/point_35e8286c4e.20260902T125525Z.txt`, not
`code/points/point_35e8286c4e.txt`.** Its drug block reads `b` 0.408622,
`lambda_d` 0.294785, `theta` 0.304601 and its `pi_eu` 0.134279 against a 0.139
target, which is what every table above uses.

### What the new `pi_eu` target does to the counts above

All nine round-1 rows above are scored against the targets that each point file
carries, which for `pi_eu` is **0.139**, the target in force when all seven points
were solved. Under the author's new 0.049 target, `pi_eu` is out at every one of
them -- the seven readings span 0.073962 to 0.150927, and the closest, line 2's
0.073962, is still +50.9% above 0.049.

So the eight-of-nine counts above become seven-of-nine, and the four-of-nine
counts become three-of-nine, on the target alone. That re-scoring is arithmetic on
the readings already in this file; **it is not a measurement.** `probability_
becoming_unemployed` is pinned at 0.0122 in all seven vectors, so the target does
not enter the solve at a pinned point, but `de9d7a3` also moved the semantic hash
(`197407b07d -> 0afbde300f`) and no point in this file has been re-solved on it.
Nothing here claims these seven points would reproduce on the current source.

`de9d7a3`'s own commit message says the change is expected to pull `beta` and
`w_bot` further down, and `beta` is already out at all seven points here and
`w_bot` is the moment lines 1 and 2 break hardest. Those two records are worth
reading together; this file does not combine them.

---

## What was not done

No extrapolation past these three lines. No instrument value between or beyond
the measured points is estimated -- not the `theta` crossing inside 0.400-0.300,
not a `lambda_addiction` value past 50.0, not the `lambda_d` crossing inside
0.300-0.200. The `theta = -1` sentinel was recorded and left alone. No build
failed and nothing segfaulted, so nothing had to be stopped for.
`code/housing_first_or_treatment_first_SR_v1.f90` was not edited.
