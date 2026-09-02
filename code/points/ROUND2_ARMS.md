# ROUND 2 ARMS -- three drug-block instruments, one coordinate each, off the round-1 point

`code/batch_round2_arms.txt`, three lines, run one at a time from the repository
root, each allowed to finish before the next was started and each committed
before the next was fired. No rebase was taken between lines. Borrowing is off
throughout (`include_unsecured_borrowing=0`).

The base is the round-1 point `35e8286c4e`, the eight-of-nine point named in
`code/CALIBRATION_STATE.md`. Each arm moves ONE round-2 instrument off it and
nothing else.

| | instrument move | tag | MODEL | outcome |
|---|---|---|---|---|
| arm 1 | `lambda_addiction` 2.79953 -> **8.00000** | `82a955b244` | `b8dc1077ad` | solved, 15 min |
| arm 2 | `addiction_scalar_1` 0.0360 -> **0.0120** | `7771720a08` | `b8dc1077ad` | solved, 20 min |
| arm 3 | `relative_share_of_addiction_1` 0.463 -> **0.400** | `e7c7daf5ca` | `b8dc1077ad` | solved, 16 min |

## The three MODEL lines agree, and that was checked rather than assumed

**All three points carry `MODEL b8dc1077ad`.** So does the base `35e8286c4e`, and
so does the working tree: `md5sum code/housing_first_or_treatment_first_SR_v1.f90`
cut to ten characters is `b8dc1077ad`. Every number below is a within-economy
comparison against a base measured on the same source. No source change landed
mid-batch and `housing_first_or_treatment_first_SR_v1.f90` was not edited.

All three report `HANDOVER OK: 42 of 42 parameters applied` and `INVARIANTS: all
PASS`, 16 of 16, with no failure anywhere. Nothing segfaulted and no build failed.

Each arm's `VECTOR` was diffed against the base coordinate by coordinate, all
forty-three names on both sides:

    arm 1 vs base:  1 difference, lambda_addiction 2.79953 -> 8.00000
    arm 2 vs base:  1 difference, addiction_scalar_1 0.0360 -> 0.0120
    arm 3 vs base:  1 difference, relative_share_of_addiction_1 0.463 -> 0.400

So each arm is a matched pair with the base in exactly its own instrument.

## A correction to the numbers this batch was ordered against

The batch was specified against a drug block reading `lambda_d` 0.30520, `b`
0.40068, `theta` 0.35773. **Those are not the round-1 point's values.** They are
`point_846f6a0a53`, which is round-1-combined line 3 and a different economy:
against `35e8286c4e` it differs in `discount_factor` (0.99900 vs 0.99980),
`discount_factor_impatient` (0.55 vs 0.75), `max_food_cost` (0.0080 vs 0.0130),
`probability_becoming_unemployed` (0.0437 vs 0.0122),
`probability_of_voucher_benchmark_used` (0.047 vs 0.052),
`relative_share_of_housing` (0.200 vs 0.100) and `value_of_life` (54.0 vs 42.0).

The base actually measured here reads:

| moment | quoted in the order | `35e8286c4e`, the real base | target |
|---|---|---|---|
| `lambda_d` | 0.30520 | **0.294785** | 0.0368 |
| `b` | 0.40068 | **0.408622** | 0.089 |
| `theta` | 0.35773 | **0.304601** | 0.162 |

The framing survives -- all three are far above target either way -- but every
difference below is taken against `35e8286c4e`'s own numbers, not the quoted ones.

This is the same trap the order warned about, and it sprang inside the order
itself: the archive's 744 points span several economies and a value read off one
of them is not a reading for this one.

## The archive warning, confirmed

`addiction_scalar_1` at exactly 0.0360 produced `lambda_d` of 0.03682 somewhere in
the archive, dead on target. At 0.0360 in THIS economy the base produces `lambda_d`
of **0.294785**, eight times the target. The instrument is economy-dependent to
that degree, and nothing from another economy is quoted below as a prediction.

## Each arm against the moment it owns

Percentages are (model - target) / target.

### arm 1 -- `lambda_addiction` owns `b`, total drug users, target 0.089

| `lambda_addiction` | `b` | gap |
|---|---|---|
| 2.79953 (base) | 0.408622 | **+359.13%** |
| 8.00000 (arm 1) | 0.393509 | **+342.15%** |

**Does NOT bracket. Both points lie ABOVE the target, and far above it.** Nearly
tripling the instrument moved `b` by -0.015113, from 4.59x the target to 4.42x it.
The pair does not reach down to 0.089 and does not come close.

### arm 2 -- `addiction_scalar_1` owns `lambda_d`, disorder rate, target 0.0368

| `addiction_scalar_1` | `lambda_d` | gap |
|---|---|---|
| 0.0360 (base) | 0.294785 | **+701.05%** |
| 0.0120 (arm 2) | 0.410701 | **+1016.03%** |

**Does NOT bracket. Both points lie ABOVE the target**, and the move went the
WRONG WAY: cutting the instrument by two thirds RAISED `lambda_d` by +0.115915,
from 8.0x the target to 11.2x it. Whatever sign the step was chosen on, this
economy does not have it. The step made the moment worse, not better.

### arm 3 -- `relative_share_of_addiction_1` owns `theta`, drug spending share, target 0.162

| `relative_share_of_addiction_1` | `theta` | gap |
|---|---|---|
| 0.463 (base) | 0.304601 | **+88.03%** |
| 0.400 (arm 3) | 0.240079 | **+48.20%** |

**Does NOT bracket. Both points lie ABOVE the target.** This is the one arm whose
owned moment moved the right way and moved usefully: -0.064522 for a 0.063 cut in
the instrument, closing roughly half the gap in percentage terms. It still stops
short of 0.162.

### Summary of the three

**No arm brackets its target. All six measured points, on all three moments, lie
above target.** Arm 3 moves toward it, arm 1 barely moves, arm 2 moves away.

## What the arms did to round 1

Base is eight of nine, `beta` the only one out. Percentages are (model - target)
/ target; `beta` is a BAND, 3.0 to 4.5, scored in or out with its shortfall quoted
against the 3.0 floor. **Bold marks a moment outside ten per cent.**

| moment | target | base | arm 1 | arm 2 | arm 3 |
|---|---|---|---|---|---|
| `aleph` value of life / income | 80.0 | 75.828008 | 75.662297 | 43.464472 | 77.659727 |
| `beta` wealth over output | BAND 3.0-4.5 | 2.452826 | 2.492457 | 2.513934 | 2.382602 |
| `omega_l` labour supply / hours | 0.40 | 0.363505 | 0.364203 | 0.405819 | 0.362301 |
| `sigma_y` bottom half earnings share | 0.172 | 0.169050 | 0.169050 | 0.169050 | 0.169050 |
| `tau_l` average labour income tax | 0.224 | 0.226321 | 0.227453 | 0.231784 | 0.226199 |
| `pi_eu` unemployment rate | 0.139 | 0.134279 | 0.145312 | 0.154858 | 0.128701 |
| `pi_V` eligibles with a voucher | 0.266 | 0.255978 | 0.255889 | 0.228969 | 0.256401 |
| `cbar` food stamps / income | 0.0042 | 0.003935 | 0.004265 | 0.003953 | 0.003790 |
| `w_bot` net worth share, bottom half | 0.0250 | 0.024270 | 0.027391 | 0.027980 | 0.024994 |

and the same as gaps:

| moment | base | arm 1 | arm 2 | arm 3 |
|---|---|---|---|---|
| `aleph` | -5.21% | -5.42% | **-45.67%** | -2.93% |
| `beta` | **OUT -0.5472** | **OUT -0.5075** | **OUT -0.4861** | **OUT -0.6174** |
| `omega_l` | -9.12% | -8.95% | +1.45% | -9.42% |
| `sigma_y` | -1.72% | -1.72% | -1.72% | -1.72% |
| `tau_l` | +1.04% | +1.54% | +3.48% | +0.98% |
| `pi_eu` | -3.40% | +4.54% | **+11.41%** | -7.41% |
| `pi_V` | -3.77% | -3.80% | **-13.92%** | -3.61% |
| `cbar` | -6.31% | +1.55% | -5.87% | -9.77% |
| `w_bot` | -2.92% | +9.56% | **+11.92%** | -0.02% |

**Inside ten per cent, out of nine:**

| point | count | out |
|---|---|---|
| base `35e8286c4e` | **8 of 9** | `beta` |
| arm 1 `82a955b244` | **8 of 9** | `beta` |
| arm 2 `7771720a08` | **4 of 9** | `aleph`, `beta`, `pi_eu`, `pi_V`, `w_bot` |
| arm 3 `e7c7daf5ca` | **8 of 9** | `beta` |

### Arm 2 breaks round 1, and this is the most important line in this file

**`addiction_scalar_1` 0.0360 -> 0.0120 takes round 1 from eight of nine to four
of nine.** It loses four moments that were in at the base:

- `aleph` **75.828 -> 43.464**, from -5.21% to **-45.67%**. This is not a drift,
  it is a collapse: the value of life per unit income falls by 42.7 per cent while
  `value_of_life` itself is untouched at 42.0.
- `pi_V` 0.255978 -> 0.228969, from -3.77% to **-13.92%**.
- `w_bot` 0.024270 -> 0.027980, from -2.92% to **+11.92%**.
- `pi_eu` 0.134279 -> 0.154858, from -3.40% to **+11.41%**.

`h_1`, round 1's tenth moment and already far out at the base, also worsens:
0.045147 -> 0.075067 against a target of 0.00399.

So the arm that moved its own moment the wrong way is also the arm that costs
four round-1 moments. It is unusable in both directions at once.

### Arms 1 and 3 hold round 1 at eight of nine, but not with the same margins

Neither arm loses a moment. Both move several, and two margins are worth naming
because they are close to the edge:

- **arm 1 pushes `w_bot` from -2.92% to +9.56%.** It crosses zero and lands just
  inside the band. `pi_eu` likewise crosses zero, -3.40% to +4.54%, and `cbar`
  crosses zero the other way, -6.31% to +1.55%, which is an improvement.
- **arm 3 pushes `cbar` from -6.31% to -9.77%** and `omega_l` from -9.12% to
  -9.42%, both still inside ten per cent and both with very little room left.
  Against that, arm 3 improves `aleph` to -2.93% and lands `w_bot` at -0.02%,
  the best reading of that moment anywhere in this batch.
- **arm 3 is the worst of the four for `beta`**, 2.382602, 0.6174 below the floor
  where the base is 0.5472 below it. `beta` is out everywhere, so this loses
  nothing that was held, but it moves the one open round-1 moment further away.

`sigma_y` is identical to all sixteen digits at all four points. No round-2
instrument touches it.

## Every arm moved moments it does not own

Recorded because the order asked for it and because round 1 took four passes for
this reason. Deltas off the base:

| | `lambda_d` (owned by `addiction_scalar_1`) | `b` (owned by `lambda_addiction`) | `theta` (owned by `relative_share_of_addiction_1`) |
|---|---|---|---|
| arm 1, `lambda_addiction` | +0.037905 | *owned:* -0.015113 | -0.051366 |
| arm 2, `addiction_scalar_1` | *owned:* +0.115915 | +0.468640 | -0.090798 |
| arm 3, `relative_share_of_addiction_1` | -0.025381 | -0.002878 | *owned:* -0.064522 |

Two things in that table are worth the author's eye, and both are statements
about these six points only:

- **`addiction_scalar_1` moved `b` by +0.468640 while `b`'s own instrument moved
  it by -0.015113**, thirty-one times as far, and in the opposite direction.
- **`addiction_scalar_1` moved `theta` by -0.090798 while `theta`'s own instrument
  moved it by -0.064522**, half again as far.

On the arms measured here the assigned ownership does not match which instrument
actually drives which moment. That is an observation about three steps at three
particular sizes, not a Jacobian; no step size, sign or crossing point is inferred
from it below, and none should be read into it.

## What was not done

No extrapolation past these three arms. No instrument value between or beyond the
measured pairs is estimated, and no bracket is claimed anywhere, because none was
found. `code/housing_first_or_treatment_first_SR_v1.f90` was not edited.
