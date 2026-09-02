# Round 1 arms B, borrowing OFF: two arms and a re-measured control, all on one economy

`code/batch_r1b_off.txt`, run line by line. Each line moves ONE round-1
instrument off the anchor and leaves the other thirty-nine alone. Unsecured
borrowing is off in both lines and in the control.

| | vector | tag | MODEL | outcome |
|---|---|---|---|---|
| control | `discount_factor` 0.99715, `probability_becoming_unemployed` 0.0437 | `f9c16d5308` | `c823331449` | solved, 11 min |
| line 1 | `discount_factor` 0.99715 -> **0.99800** | `60036d292a` | `c823331449` | solved, 10 min |
| line 2 | `probability_becoming_unemployed` 0.0437 -> **0.0498** | `03fd927a5c` | `c823331449` | solved, 10 min |

**The MODEL lines agree.** All three carry `c823331449` (semantic `17529c7177`),
all three report `HANDOVER OK: 42 of 42 parameters applied`, and all three pass
16 of 16 invariants with no failures. Unlike `ROUND1_ARMS_A`, this batch does not
straddle a source change and no point here is degenerate: `tau_l` is 0.233 to
0.235 rather than NaN, and `beta`, `aleph` and `cbar` are all on a plausible
scale. Both arms are genuine matched pairs with the control.

## The control had to be re-measured, and that is why there is one

The archive already held `point_f9c16d5308.txt` at exactly this vector -- all
forty named parameters matching -- but it was measured on MODEL `d2563e97f3`,
semantic `a734fffba5`. The two lines are on semantic `17529c7177`. Those are
different economies, so the stored anchor could not be differenced against
either line, and **no point in the archive was on `17529c7177`**: the census over
all 400-odd point files returned zero.

Without a control neither line is a pair with anything. Line 1 and line 2 differ
from each other in *both* instruments, so they do not bracket each other either.
The anchor vector was therefore re-run on the current source. `run_one_point.sh`
detected the stale stamp itself, filed the old file under
`points_superseded/point_f9c16d5308.20260902T045754Z.txt` and re-solved; the old
measurement is preserved, not overwritten.

For the record, the superseded reading on `a734fffba5` was `beta` = 2.685 and
`pi_eu` = 0.2608, close enough to the new one that the re-measurement changed no
conclusion -- but that could only be known after taking it.

## Arm 1 -- beta, owned by `discount_factor`

`discount_factor` at 0.99800 is a **probe for the slope**, not an attempt at the
band. beta is steeply nonlinear in it.

| `discount_factor` | beta, wealth over output |
|---|---|
| 0.99715 (control) | 2.688264 |
| 0.99800 (arm) | 2.785097 |
| band | 3.0 to 4.5 |

**Both readings fall below the band, and the pair does not reach it.** The
control is short of the floor by 0.311736 and the arm by 0.214903. Moving the
instrument by 0.00085 moved beta by +0.096833, a slope of about 114 per unit of
`discount_factor` over this interval.

**No value of `discount_factor` that would land beta in the band is projected
here.** The measured pair covers 0.99715 to 0.99800 and nothing outside it. A
linear reading of that slope is exactly the extrapolation that has been made on
this branch before and been wrong every time, and the reason is in the arm
itself: the instrument is inside 0.002 of 1, where the discounted sum it governs
is not close to linear, so a slope measured over a step of 0.00085 does not carry
to the step of several times that size the band is away.

## Arm 2 -- pi_eu, owned by `probability_becoming_unemployed`

| `probability_becoming_unemployed` | pi_eu, unemployment rate |
|---|---|
| 0.0437 (control) | 0.260329 |
| 0.0498 (arm) | 0.276048 |
| target | 0.139 |

**The pair does not bracket the target; both overshoot it, and the arm moves
away from it.** The control is 1.87 times the target and the arm 1.99 times it,
overshooting by +0.121329 and +0.137048. Moving the instrument by 0.0061 moved
pi_eu by +0.015719, a slope of about 2.58 per unit, and the sign says the
instrument has to come DOWN from 0.0437, not up -- so this batch's arm was taken
in the wrong direction for closing the gap, and the interval that would close it
lies below every point measured here. No value is projected for it.

Note the scale: at an instrument of 0.0437 the unemployment rate reads 0.260,
about six times the flow probability driving it. Whatever sets that ratio is not
`probability_becoming_unemployed` alone, and a target of 0.139 is below what the
instrument produces at any value tried on this economy so far.

## The two instruments are NOT both clean, and this is the finding to carry forward

Each arm moves the other's moment as well, and the two cases are not alike:

| | own arm moved it | the other arm moved it | cross as a share of own |
|---|---|---|---|
| pi_eu | +0.015719 | +0.000374 | **2.4%** |
| beta | +0.096833 | +0.060904 | **62.9%** |

`pi_eu` is cleanly owned: `discount_factor` barely touches it. **`beta` is not.**
`probability_becoming_unemployed` moved wealth over output by 63 per cent as much
as `discount_factor` itself did, on steps that were each one round-1 arm. Treating
`discount_factor` as the sole instrument for beta will therefore mis-assign the
movement whenever pi_eu's instrument is also in play, which on a joint step it
always is.

This is a reason to be more careful about the beta projection, not less. The
slope of 114 per unit above is a *partial* derivative holding
`probability_becoming_unemployed` at 0.0437, and a joint step that also moves
pi_eu's instrument will not see it.

## Other moments, for scale

All three points, same economy, all 16 invariants passing at each:

| moment | control | line 1 (df up) | line 2 (pi_eu up) | target |
|---|---|---|---|---|
| `sigma_y` bottom half earnings share | 0.16905 | 0.16905 | 0.16905 | 0.17200 |
| `tau_l` average labour income tax | 0.23342 | 0.23370 | 0.23479 | 0.22400 |
| `omega_l` labour supply / total hours | 0.37857 | 0.37899 | 0.37962 | 0.40000 |
| `beta` wealth over output | 2.68826 | 2.78510 | 2.74917 | 3.0 to 4.5 |
| `h_1` homelessness rate | 0.08254 | 0.08343 | 0.08159 | 0.00399 |
| `b` total drug users | 0.39632 | 0.39923 | 0.39609 | 0.08900 |
| `lambda_d` disorder rate | 0.29135 | 0.29418 | 0.29016 | 0.03680 |
| `theta` drug spending share | 0.33131 | 0.33121 | 0.33245 | 0.16200 |
| `aleph` value of life / income | 50.667 | 51.126 | 49.479 | 80.000 |
| `pi_eu` unemployment rate | 0.26033 | 0.26070 | 0.27605 | 0.13900 |
| `cbar` food stamps / income | 0.00860 | 0.00858 | 0.00921 | 0.00420 |
| `gamma` housing over income | 0.13774 | 0.13763 | 0.13967 | 0.26800 |

`sigma_y`, `tau_l` and `omega_l` are close to their targets. `h_1`, `b` and
`lambda_d` are an order of magnitude above theirs at every point, which is the
same picture the superseded anchor showed and is not something either arm here
addresses.

## A source change landed mid-batch and these points are already superseded

While line 2 was solving, `d9ff1a8` ("the bounds checker found a real one: three
wealth walks keyed on an unset age") was pushed to the branch. It changes the
Fortran: semantic `17529c7177` becomes `2f7c317e75`.

The batch was NOT rebased onto it, deliberately. Pulling between lines would have
rebuilt the model underneath the batch and left line 1, line 2 and the control on
two different economies, which is the defect that spoiled `ROUND1_ARMS_A` and the
h_2 ladder. All three points here are internally consistent on `17529c7177`, and
every comparison above is a within-economy comparison.

The cost is that **all three are on a superseded source as of the rebase**, and
the commit that superseded them fixed wealth walks keyed on an unset age -- which
is exactly the machinery behind `beta`, the moment arm 1 measures. The arm-1
numbers should be expected to move on `2f7c317e75`, and the 63 per cent
cross-effect on beta is the first thing to re-measure there.

## What these arms establish, and what they do not

1. Both arms are clean matched pairs on one economy with healthy solves. That is
   more than round 1 arms A produced, and the comparisons above stand on their
   own terms.
2. Neither pair brackets its objective. beta is below the 3.0 to 4.5 band at both
   points; pi_eu is above 0.139 at both, and the arm moved away from it.
3. No instrument value is projected for either moment, and for beta that is a
   standing refusal, not a gap to be filled in later from this pair.
4. beta is not cleanly owned by `discount_factor` at this vector. Any round-1
   step that treats it as though it were will mis-attribute the movement.
5. All of it needs re-measuring on `2f7c317e75` before it is used, because the
   commit that superseded these points touched the wealth accumulation that
   `beta` is computed from.
