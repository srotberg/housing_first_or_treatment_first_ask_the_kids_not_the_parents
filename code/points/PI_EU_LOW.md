# `pi_eu` an order of magnitude down: two arms, and the target is bracketed

`code/batch_pi_eu_low.txt`, run line by line from the repository root, each line
issued on its own and allowed to finish before the next was started. Each moves
ONE coordinate, `probability_becoming_unemployed`, off the anchor 0.0437 and
leaves the other forty-two alone. `include_unsecured_borrowing=0` throughout,
in both lines and in the control.

| | instrument | tag | MODEL | outcome |
|---|---|---|---|---|
| control | 0.0437 | `f9c16d5308` | `b8dc1077ad` | solved, 14 min |
| line 1 | **0.0150** | `0452c117ed` | `b8dc1077ad` | solved, 9 min |
| line 2 | **0.0080** | `8f1afa07a7` | `b8dc1077ad` | solved, 9 min |

## The MODEL lines agree, and that was checked rather than assumed

**Both lines and the control carry `MODEL b8dc1077ad`** (semantic `2f7c317e75`,
the head this batch was synced to). All three report `HANDOVER OK: 42 of 42
parameters applied` and `INVARIANTS: all PASS`, 16 of 16, no failures anywhere.
Nothing under `code/` was edited; `code/housing_first_or_treatment_first_SR_v1.f90`
was not touched.

The control was not re-run. It is `code/points/point_f9c16d5308.txt`, read out
of the archive, and its `VECTOR` was compared to each line's **coordinate by
coordinate**, all forty-three:

    line 1 vs control:  probability_becoming_unemployed  0.0437 -> 0.0150   (only diff)
    line 2 vs control:  probability_becoming_unemployed  0.0437 -> 0.0080   (only diff)

Both are genuine matched pairs with the control on one economy, so everything
below is a within-economy comparison.

One correction to the brief that commissioned this run: it gives the anchor's
`pi_eu` as 0.26377. The anchor's own `MOMENT pi_eu` line reads **0.26080**, and
that is the number used here -- it is also the number the brief's own quoted
ratio of 5.96 is built from (0.26080 / 0.0437 = 5.968; 0.26377 / 0.0437 would be
6.036). The 0.0300 arm, `point_a6ae2d65f0.txt`, is quoted correctly at 0.21830.

## The four instrument values on this economy

Target for `pi_eu` is **0.139** throughout.

| instrument | `pi_eu` | target | gap vs target | **`pi_eu` / instrument** |
|---|---|---|---|---|
| 0.0437 (anchor) | 0.26080 | 0.139 | +87.6% | **5.97** |
| 0.0300 | 0.21830 | 0.139 | +57.1% | **7.28** |
| **0.0150** | **0.15308** | 0.139 | **+10.1%** | **10.21** |
| **0.0080** | **0.10972** | 0.139 | **-21.1%** | **13.72** |

### The ratio keeps rising. It does not flatten and it does not turn.

5.97 -> 7.28 -> 10.21 -> 13.72, monotone over the whole measured range, and
rising faster at the bottom than at the top: the step from 0.0300 to 0.0150
adds 2.93 to the ratio, the step from 0.0150 to 0.0080 adds another 3.51 over
half the distance in the instrument. Over the four arms the instrument falls by
a factor of 5.5 and `pi_eu` falls by a factor of only 2.4.

So the reading that motivated this batch survives: a large part of the
unemployment rate is not set by `probability_becoming_unemployed`. But the
ratio overstates how large, and the arms say so directly. Fit a local secant to
each adjacent pair and read off the implied floor -- the part of `pi_eu` that
the secant says would survive at instrument zero:

| pair | d`pi_eu`/d(instrument) | implied floor at zero |
|---|---|---|
| 0.0300 -> 0.0437 | 3.10 | 0.1252 |
| 0.0150 -> 0.0300 | 4.35 | 0.0879 |
| 0.0080 -> 0.0150 | 6.19 | 0.0602 |

The response is concave: the instrument bites HARDER the lower it goes, and the
apparent floor shrinks as you descend into it -- 0.125, then 0.088, then 0.060.
A rising ratio therefore does not mean a fixed unreachable floor sitting above
the target. It means the mapping is curved, and the curvature is in the helpful
direction. (These floors are secant extrapolations to instrument zero, well
outside the measured range; they are reported as a description of the curvature,
not as a claim about the model at zero.)

## The target is bracketed, between the two new arms

**0.139 is bracketed by 0.0080 and 0.0150**: `pi_eu` = 0.10972 at 0.0080 and
0.15308 at 0.0150, and 0.10972 < 0.139 < 0.15308. This is the only bracketing
pair among the four; every other pair sits entirely above the target.

`pi_eu` is monotone increasing in the instrument across all four arms, so the
bracket is a genuine one and a secant inside it is an interpolation rather than
an extrapolation. Linear interpolation between the two bracketing arms puts the
crossing at **instrument ~= 0.0127**. That is inside the measured interval, but
the interval is where the curvature is strongest, so treat 0.0127 as a place to
put the next arm rather than as a solved value.

No extrapolation past 0.0080 or above 0.0437 is offered here.

## The round-1 moments, and this is the part that should worry the reader

The brief asked for `w_bot`, `aleph`, `h_1` and `emp_homeless` at each point,
because the arms on this branch are not orthogonal and a move this large in one
coordinate was expected to disturb moments it does not own. It did.

| instrument | `w_bot` (t 0.025) | `aleph` (t 80.0) | `h_1` (t 0.00399) | `emp_homeless` (obs 0.46) |
|---|---|---|---|---|
| 0.0437 (anchor) | 0.02949 (+17.9%) | 50.334 (-37.1%) | 0.08418 | 0.96419 |
| 0.0300 | 0.02837 (+13.5%) | 53.738 (-32.8%) | 0.08369 | 0.97033 |
| **0.0150** | **0.02494 (-0.2%)** | 59.281 (-25.9%) | 0.08791 | 0.98188 |
| **0.0080** | **0.02089 (-16.5%)** | 64.884 (-18.9%) | 0.09152 | 0.98842 |

- **`w_bot` moves a lot, and it crosses its target inside this batch.** It runs
  +17.9% -> +13.5% -> -0.2% -> -16.5%, monotone falling, and it lands
  essentially exactly on 0.025 at instrument 0.0150. This is the concrete form
  of the non-orthogonality the brief warned about: `w_bot` was closed on an
  instrument that does not own it, and `probability_becoming_unemployed` moves
  it about as hard as it moves `pi_eu`. It cannot stay closed while this
  instrument is retuned; it has to be re-closed afterwards, on whatever
  instrument is chosen to own it.
- **`aleph` improves monotonically**, -37.1% -> -18.9%, roughly halving its gap.
  Still short of 80, but every step down in the instrument helps it.
- **`h_1` gets slightly worse**, 0.0842 -> 0.0915, and is three orders of
  magnitude above its target at every arm. This instrument is not the lever on
  homelessness and none of these arms changes that.
- **`emp_homeless` gets worse**, 0.964 -> 0.988 against 0.46 observed. Fewer
  unemployment shocks means an even larger share of the homeless are working,
  which is already the model's most conspicuous failure. Moving `pi_eu` toward
  its target pushes this one further away.

### Two moments that were inside ten per cent at the anchor and are not any more

Scanning all twenty-three targeted moments rather than only the four requested:

| moment | target | 0.0437 | 0.0300 | 0.0150 | 0.0080 |
|---|---|---|---|---|---|
| `h_2` | 0.101 | 0.10682 (+5.8%) | 0.09501 (-5.9%) | 0.07113 (**-29.6%**) | 0.05356 (**-47.0%**) |
| `beta` | 3.0 | 2.6846 (-10.5%) | 2.5283 (-15.7%) | 2.2463 (**-25.1%**) | 2.0577 (**-31.4%**) |
| `y_u` | 0.74 | 0.71012 (-4.0%) | 0.75511 (+2.0%) | 0.82946 (**+12.1%**) | 0.87382 (**+18.1%**) |

`h_2` is the casualty. It was inside six per cent at the anchor and is nearly
halved at 0.0080; the share of households spending above half their budget on
housing collapses when unemployment does. `beta` (wealth over output) was
already just outside ten per cent and degrades to -31%. `y_u` was inside five
per cent at the anchor, crosses its target between 0.0437 and 0.0300, and is
+18% at 0.0080.

Three moments improve alongside `pi_eu`: `tau_l` (+4.6% -> +0.2%), `cbar`
(+105% -> -21%, crossing its target inside the bracket) and `kappa_ued` (+222%
-> +17%). `kappa_uem` improves from -77.8% to -33.7%.

Unchanged or near-unchanged everywhere: `sigma_y`, `b`, `lambda_d`, `theta`,
`mu_H`, `p_m`, `tau_u` (still identically zero, no treatment take-up at any arm).

## What this batch establishes

1. `pi_eu` = 0.139 **is reachable on this economy**, and it is bracketed between
   instrument 0.0080 and 0.0150, near 0.0127.
2. The ratio `pi_eu`/instrument rises monotonically over all four arms and
   shows no sign of flattening -- but the underlying map is concave, and the
   floor the ratio seems to imply shrinks as the instrument falls rather than
   holding at the anchor's 0.125.
3. Closing `pi_eu` this way costs `w_bot`, which crosses its target inside the
   bracket, and costs `h_2` and `beta` outright. `aleph`, `tau_l`, `cbar`,
   `kappa_ued` and `kappa_uem` all improve. `h_1` and `emp_homeless` get
   modestly worse.

Point 3 is the one that matters for what to do next. The instrument that closes
`pi_eu` is not free, and the moment it disturbs most, `w_bot`, is one that was
closed on an instrument that does not own it. Re-closing `pi_eu` at ~0.0127
requires re-closing `w_bot` afterwards, and `h_2` will need its own instrument.
