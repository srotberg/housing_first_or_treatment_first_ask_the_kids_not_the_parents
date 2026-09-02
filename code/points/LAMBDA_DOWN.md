# LAMBDA DOWN -- `lambda_addiction` taken BELOW 2.79953, three points, off `35e8286c4e`

`code/batch_lambda_down.txt`, three lines, run one at a time from the repository
root, each allowed to finish before the next was started and each committed before
the next was fired. No rebase was taken between the lines. Borrowing is off
throughout (`include_unsecured_borrowing=0`).

The base is the round-1 point `35e8286c4e`. Each line moves `lambda_addiction` and
nothing else.

| | instrument move | tag | MODEL | outcome |
|---|---|---|---|---|
| line 1 | `lambda_addiction` 2.79953 -> **1.00000** | `2035b208bf` | `bb2cd48b81` | solved, 16 min |
| line 2 | `lambda_addiction` 2.79953 -> **0.30000** | `596012c614` | `bb2cd48b81` | solved, 20 min |
| line 3 | `lambda_addiction` 2.79953 -> **0.05000** | `9e225217bf` | `bb2cd48b81` | solved, 16 min |

Nothing segfaulted, no build failed, and
`code/housing_first_or_treatment_first_SR_v1.f90` was not edited at any point.
All three report `HANDOVER OK: 42 of 42 parameters applied` and `INVARIANTS: all
PASS`, 16 of 16, with no `INVARIANT FAIL` line anywhere.

## LEAD: every arm breaks round 1, and `b` moves the WRONG WAY in this direction too

The order asked to be told first if a drug arm breaks round 1. **All three do.**

| point | `lambda_addiction` | round 1, inside ten per cent |
|---|---|---|
| `9e225217bf` | 0.05000 | **5 of 9** |
| `596012c614` | 0.30000 | **3 of 9** |
| `2035b208bf` | 1.00000 | **6 of 9** |
| `35e8286c4e` (base) | 2.79953 | **9 of 9** |
| `82a955b244` | 8.00000 | **9 of 9** |

And the reading the batch was ordered on does not survive the measurement.
**Lowering `lambda_addiction` RAISES `b`.** The order's reasoning was that raising
lambda makes using riskier, agents cut the quantity `v`, and the two effects nearly
cancel, so going down would not have that offset working against it. What the three
points show instead is that `b` is monotone DECREASING in `lambda_addiction` over
the whole measured ladder, so going down is the direction that makes `b` worse, and
it makes it worse fast: `b` more than doubles between 2.79953 and 0.05000.

**`2.79953` is the LOWEST reading of `b` anywhere in the measured ladder except the
8.00 arm.** Both arms taken off it in the previous batch and this one -- up to 8.00
and down to 1.00 -- were read as "nearly inert" and "should be clean" respectively;
the truth is that 8.00 is the only measured value that lowers `b` at all, and it
lowers it by 0.0151 against a gap of 0.3196.

## The three MODEL lines agree -- and they do NOT agree with the base

**All three of my points carry `MODEL bb2cd48b81`.** So does the working tree:
`md5sum code/housing_first_or_treatment_first_SR_v1.f90` cut to ten characters is
`bb2cd48b81`. The three lines are therefore a matched set with each other.

**They are NOT on the same source as the base or the 8.00 arm.** `35e8286c4e` and
`82a955b244` both carry `MODEL b8dc1077ad`, and commit `5ea693e` ("beta's target is
2.5, on the author's instruction") landed between them and this batch. This is
stated plainly rather than smoothed over, because every cross-arm comparison in
this file spans that boundary:

- the diff in `5ea693e` is `wealth_to_output_data` 3.0d0 -> 2.5d0 plus comment, and
  the commit argues at length that the constant reaches the solver only through the
  discount-factor calibration block, which is guarded off, so nothing a household
  faces changes and only `beta`'s PRINTED target moves;
- **that argument has not been checked against a measurement.** `code/batch_target_check.txt`
  exists for exactly this -- it is the base vector re-run on the new source -- and
  it has never been run: **no point in `code/points/` carries `bb2cd48b81` except
  the three in this batch**, and 44 carry `b8dc1077ad`;
- the pair is **not** in `EQUIVALENT_MODELS` in `code/next_batch.py`, whose own
  comment says a hash goes in there only after the diff is read AND nothing
  computed is confirmed unchanged.

The visible symptom is in the point files themselves: `35e8286c4e` and `82a955b244`
print `MOMENT beta ... target 3.0000`, my three print `target 2.5000`. Every `beta`
row below is scored against 2.5 uniformly, per the band in the order.

So the ladder in this file is **one source boundary wide**. If `5ea693e` really is
printed-target-only, the ladder is a single economy and every reading stands as
written. If it is not, the two archive rungs are on a different economy from my
three and only the three-point comparison among 1.00, 0.30 and 0.05 is safe.
Running `code/batch_target_check.txt` settles it in one solve; it was outside this
batch's three lines and was not run.

Each `VECTOR` was diffed against the base coordinate by coordinate, all
forty-three names on both sides:

    line 1 vs base:  1 difference, lambda_addiction 2.79953 -> 1.00000
    line 2 vs base:  1 difference, lambda_addiction 2.79953 -> 0.30000
    line 3 vs base:  1 difference, lambda_addiction 2.79953 -> 0.05000
    8.00 arm vs base: 1 difference, lambda_addiction 2.79953 -> 8.00000

So each point is a matched pair with the base in exactly this one instrument.

## The ladder: `b`, total drug users, target 0.089

The 8.00 rung is `point_82a955b244`, already in the archive on this vector; it is
labelled below and was not re-run.

| `lambda_addiction` | tag | `b` | gap vs 0.089 |
|---|---|---|---|
| 0.05000 | `9e225217bf` | 0.940247 | **+956.46%** |
| 0.30000 | `596012c614` | 0.902885 | **+914.48%** |
| 1.00000 | `2035b208bf` | 0.453616 | **+409.68%** |
| 2.79953 (base) | `35e8286c4e` | 0.408622 | **+359.13%** |
| 8.00000 (archive) | `82a955b244` | 0.393509 | **+342.15%** |

**NO MEASURED PAIR BRACKETS 0.089. All five points lie ABOVE the target**, the
closest by a factor of 4.4. `b` is monotone decreasing in `lambda_addiction` across
all five rungs, so the whole ladder points the same way: the only measured
direction that lowers `b` is UP, and over 2.79953 -> 8.00000 it lowers it by
0.015113 against a gap of 0.319622 -- under five per cent of the distance, for
nearly a tripling of the instrument.

Nothing below 0.05000 and nothing above 8.00000 is measured, and no crossing point,
step size or sign is inferred beyond these five rungs.

## Why it goes this way, from the model's own diagnostics

Not an argument, a reading of the printed rows. The hazard itself does exactly what
it is supposed to do -- `pi_d(v) = 1 - exp(-lambda*v)` at line 6861 falls hard as
lambda falls:

| `lambda_addiction` | onset at the mean quantity | mean drug quantity, users | buyers as a share of clean households |
|---|---|---|---|
| 0.05000 | 0.005160 | 0.103462 | 0.937146 |
| 0.30000 | 0.020389 | 0.068667 | 0.885992 |
| 1.00000 | 0.101207 | 0.106702 | 0.293415 |
| 2.79953 (base) | 0.274011 | 0.114384 | 0.161422 |
| 8.00000 (archive) | 0.607014 | 0.116748 | 0.091141 |

The onset probability falls by a factor of 118 down the ladder and the share of
CLEAN households that buy rises from 0.091 to 0.937. `b` counts users, and the
hazard is what makes using dangerous, so lowering it makes using safe and almost
everyone uses. The quantity response the order expected is there and is small --
mean quantity moves 0.117 -> 0.103 over the whole ladder -- and it is swamped by
the extensive margin.

The same reading explains the 8.00 arm's near-inertia without needing the
offsetting-quantity story: at 8.00 onset at the mean is already 0.607, and pushing
the hazard further up a curve that is flattening out buys very little extra
deterrence.

## `lambda_d` and `theta`: the three drug moments do NOT move together

This is the question the order says decides whether the drug block can be set
instrument-by-instrument, and the answer is that it cannot.

| `lambda_addiction` | `b` (0.089) | `lambda_d` (0.0368) | `theta` (0.162) |
|---|---|---|---|
| 0.05000 | 0.940247 | 0.049341 | 0.234060 |
| 0.30000 | 0.902885 | 0.148176 | 0.169093 |
| 1.00000 | 0.453616 | 0.226726 | 0.286203 |
| 2.79953 (base) | 0.408622 | 0.294785 | 0.304601 |
| 8.00000 (archive) | 0.393509 | 0.332690 | 0.253235 |

as gaps:

| `lambda_addiction` | `b` | `lambda_d` | `theta` |
|---|---|---|---|
| 0.05000 | **+956.46%** | **+34.08%** | **+44.48%** |
| 0.30000 | **+914.48%** | **+302.65%** | **+4.38%** |
| 1.00000 | **+409.68%** | **+516.10%** | **+76.67%** |
| 2.79953 (base) | **+359.13%** | **+701.05%** | **+88.03%** |
| 8.00000 (archive) | **+342.15%** | **+804.05%** | **+56.32%** |

**Lowering `lambda_addiction` moves `b` AWAY from its target, `lambda_d` TOWARD
its target, and `theta` toward it and then away again.** All three moments are
above target at all five rungs, so none of the three brackets.

- **`b`** -- away, monotonically, and by a long way. Worst reading of the five is
  the bottom of the ladder.
- **`lambda_d`** -- toward, monotonically, and this is the largest useful movement
  anywhere in the drug block so far: +701.05% at the base down to **+34.08%** at
  0.05000, closing about 95 per cent of the gap. It does not cross; 0.049341 is
  still above 0.0368. Nothing below 0.05000 is measured and no crossing is claimed.
- **`theta`** -- **non-monotone.** It falls 0.304601 -> 0.169093 between 2.79953 and
  0.30000, passing within **+4.38%** of its target, then REBOUNDS to 0.234060 at
  0.05000. The minimum over the measured rungs is at 0.30000, and
  there is a second turn at the top: `theta` climbs back to 0.304601 at the base
  and falls again to 0.253235 at 8.00000. So 0.05000 and 8.00000 -- instrument
  values 160 times apart -- read 0.234060 and 0.253235, within 0.02 of each other,
  with 0.304601 in between. `theta` alone does not identify `lambda_addiction`.

**So the drug block has to be solved jointly, not instrument-by-instrument.** One
instrument moving one moment 95 per cent of the way to target while moving another
596 percentage points further from it is not a coordinate that can be set on its
own, and a non-monotone response in a third rules out inverting on that one at all.

### A correction to the premise the order gives for expecting them to move together

The order states that `addiction_scalar_1` and `relative_share_of_addiction_1`
"share the buyer threshold `(phi/theta)*p*b` with this". **They do not share it with
`lambda_addiction`.** The source at line 5499 computes that row as

    (relative_share_of_consumption_1 / relative_share_of_addiction_1)
        * price_of_addictive_good * addiction_scalar_1

-- four parameters and no moment. The `b` in the printed label is
`addiction_scalar_1`, not the moment `b`. `lambda_addiction` does not appear in it,
and the measurement agrees: the threshold reads **3.7578401727861761E-002 at all
five rungs, identical to sixteen digits**, while the moment `b` more than doubles.
Whatever couples these three moments, it is not that threshold.

## What the arms did to round 1

`beta` is a BAND, 2.5 to 4.5; a point outside it is scored against the 2.5 floor and
counts as inside ten per cent if the shortfall is within ten per cent of that floor.
Percentages elsewhere are (model - target) / target. **Bold marks a moment outside
ten per cent.** The base is nine of nine on this convention.

| moment | target | 0.05 | 0.30 | 1.00 | 2.79953 (base) | 8.00 |
|---|---|---|---|---|---|---|
| `aleph` value of life / income | 80.0 | 73.196129 | 71.411092 | 74.973898 | 75.828008 | 75.662297 |
| `beta` wealth over output | BAND 2.5-4.5 | 1.884206 | 2.047907 | 2.342895 | 2.452826 | 2.492457 |
| `omega_l` labour supply / hours | 0.40 | 0.360256 | 0.359544 | 0.362459 | 0.363505 | 0.364203 |
| `sigma_y` bottom half earnings share | 0.172 | 0.169050 | 0.169050 | 0.169050 | 0.169050 | 0.169050 |
| `tau_l` average labour income tax | 0.224 | 0.227160 | 0.225085 | 0.225011 | 0.226321 | 0.227453 |
| `pi_eu` unemployment rate | 0.139 | 0.077822 | 0.098158 | 0.117212 | 0.134279 | 0.145312 |
| `pi_V` eligibles with a voucher | 0.266 | 0.246660 | 0.255632 | 0.256817 | 0.255978 | 0.255889 |
| `cbar` food stamps / income | 0.0042 | 0.002310 | 0.002932 | 0.003444 | 0.003935 | 0.004265 |
| `w_bot` net worth share, bottom half | 0.0250 | 0.010435 | 0.014752 | 0.019214 | 0.024270 | 0.027391 |

and the same as gaps:

| moment | 0.05 | 0.30 | 1.00 | 2.79953 (base) | 8.00 |
|---|---|---|---|---|---|
| `aleph` | -8.50% | **-10.74%** | -6.28% | -5.21% | -5.42% |
| `beta` | **OUT -24.63%** | **OUT -18.08%** | OUT -6.28% | OUT -1.89% | OUT -0.30% |
| `omega_l` | -9.94% | **-10.11%** | -9.39% | -9.12% | -8.95% |
| `sigma_y` | -1.72% | -1.72% | -1.72% | -1.72% | -1.72% |
| `tau_l` | +1.41% | +0.48% | +0.45% | +1.04% | +1.54% |
| `pi_eu` | **-44.01%** | **-29.38%** | **-15.67%** | -3.40% | +4.54% |
| `pi_V` | -7.27% | -3.90% | -3.45% | -3.77% | -3.80% |
| `cbar` | **-45.01%** | **-30.19%** | **-18.01%** | -6.31% | +1.55% |
| `w_bot` | **-58.26%** | **-40.99%** | **-23.14%** | -2.92% | +9.56% |

**Inside ten per cent, out of nine:**

| point | `lambda_addiction` | count | out |
|---|---|---|---|
| `9e225217bf` | 0.05000 | **5 of 9** | `beta`, `pi_eu`, `cbar`, `w_bot` |
| `596012c614` | 0.30000 | **3 of 9** | `aleph`, `beta`, `omega_l`, `pi_eu`, `cbar`, `w_bot` |
| `2035b208bf` | 1.00000 | **6 of 9** | `pi_eu`, `cbar`, `w_bot` |
| `35e8286c4e` (base) | 2.79953 | **9 of 9** | none |
| `82a955b244` (archive) | 8.00000 | **9 of 9** | none |

Three moments carry the damage and they carry it together, monotonically in the
instrument: `pi_eu`, `cbar` and `w_bot` all fall as lambda falls, and all three are
already out at 1.00000, the mildest arm.

- **`w_bot`** is the worst, -2.92% at the base to **-58.26%** at 0.05000. The bottom
  half's net worth share collapses as the population moves into drug use.
- **`cbar`** -6.31% to **-45.01%** and **`pi_eu`** -3.40% to **-44.01%** follow the
  same shape.
- **`beta`** is in at the base on the 2.5 floor (-1.89%) and leaves the band's ten
  per cent margin somewhere between 1.00000 and 0.30000: -6.28% at 1.00000,
  **-18.08%** at 0.30000.
- **`aleph`** and **`omega_l`** are the two that go out ONLY at 0.30000 and come
  back in at 0.05000. Both are marginal at every rung -- `omega_l` sits between
  -8.95% and -10.11% across the whole ladder, i.e. it is never more than 1.2
  percentage points from the edge anywhere -- so 0.30000's count of three should not
  be read as a cliff at that value.
- **`sigma_y`** is identical to all sixteen digits at all five points. This
  instrument does not touch it, exactly as the round-2 arms found.

`h_1`, round 1's tenth moment and already far out at the base, worsens
monotonically as lambda falls: 0.033895 (8.00), 0.045147 (base), 0.059724 (1.00),
0.083627 (0.30), 0.107132 (0.05), against a target of 0.00399.

**The best point on this ladder for round 1 is the base, and it is tied with the
8.00 arm.** Every value of `lambda_addiction` below 2.79953 that was measured costs
round-1 moments, and the cost is not small.

## What this leaves

Stated as what was measured, not as a plan.

- `lambda_addiction` cannot deliver `b`. In the measured range it moves `b` the
  wrong way going down and barely at all going up, and the one direction that helps
  is the direction that was already tried and called inert.
- `lambda_addiction` is the strongest mover of `lambda_d` seen so far, closing 95
  per cent of that gap at 0.05000 -- but at a cost of four round-1 moments and with
  `b` ten times its target.
- `theta` is non-monotone in this instrument with a minimum at 0.30000, so it cannot
  be inverted on `lambda_addiction` at all.
- The `b8dc1077ad` / `bb2cd48b81` boundary is open. `code/batch_target_check.txt`
  closes it in one solve.

## What was not done

No extrapolation past the measured rungs. No value of `lambda_addiction` between,
below or above the five is estimated, no crossing point is claimed for any moment,
and no bracket is claimed anywhere, because none was found on any of the three drug
moments. The 8.00 rung is quoted from the archive and was not re-run.
`code/housing_first_or_treatment_first_SR_v1.f90` was not edited.
