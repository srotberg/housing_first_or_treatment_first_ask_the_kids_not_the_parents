# Round 1, second pass, arms B: three arms on `b8dc1077ad`, one brackets

`code/batch_r2b.txt`, run line by line from the repository root, each line
issued on its own and allowed to finish before the next was started. Each moves
ONE round-1 instrument off the anchor and leaves the other forty-two
coordinates alone. `include_unsecured_borrowing=0` throughout, in all three
lines and in the control.

| | instrument moved | value | tag | MODEL | outcome |
|---|---|---|---|---|---|
| control | -- | -- | `f9c16d5308` | `b8dc1077ad` | solved, 14 min |
| line 1 | `value_of_life` 38.4 -> **54.0** | 54.0 | `85a8b00de2` | `b8dc1077ad` | solved, 10 min |
| line 2 | `discount_factor` 0.99715 -> **0.99900** | 0.99900 | `906b19d36f` | `b8dc1077ad` | solved, 10 min |
| line 3 | `probability_becoming_unemployed` 0.0437 -> **0.0300** | 0.0300 | `a6ae2d65f0` | `b8dc1077ad` | solved, 11 min |

## The MODEL lines agree, and that was checked rather than assumed

**All four points carry `MODEL b8dc1077ad`** (semantic `2f7c317e75`, the head this
batch was synced to). All four report `HANDOVER OK: 42 of 42 parameters
applied` and `INVARIANTS: all PASS`, 16 of 16, with no failures anywhere.

The control was not run here. It was read out of `code/points/` at the end, as
the batch instructions required, and it is `point_f9c16d5308.txt` -- the anchor
vector, which arrived on this branch from the determinism work at commit
`6b53f49`. Two things were checked before differencing against it:

1. Its `MODEL` line is `b8dc1077ad`, the same source as all three lines.
2. Its vector was compared to each line's vector **coordinate by coordinate**,
   all forty-three. A census over every `point_*.txt` in the archive found
   exactly one file on `b8dc1077ad` carrying the anchor vector on all
   forty-three coordinates, and this is it.

The diff against each line is a single coordinate and nothing else:

    line 1 vs control:  value_of_life                    38.4    -> 54.0
    line 2 vs control:  discount_factor                  0.99715 -> 0.99900
    line 3 vs control:  probability_becoming_unemployed  0.0437  -> 0.0300

So all three are genuine matched pairs with the control on one economy, and
every comparison below is a within-economy comparison. No source change landed
mid-batch and no rebase was taken between two lines; the pull happened only
after line 3 had finished.

For scale, `DETERMINISM.md` puts two cold runs of one vector on one source at
5.13e-05 on the worst targeted moment. Every movement reported below is orders
of magnitude larger than that, so none of it is solver noise.

## The previous pass was on a different economy and is not differenced against here

The readings quoted in the batch instructions -- aleph 50.67 -> 81.27, beta
2.688 -> 2.785, pi_eu 0.260 -> 0.276 -- were measured on `MODEL c823331449`
(semantic `17529c7177`). This batch is on `2f7c317e75`, which is after the
commit that fixed three wealth walks keyed on an unset age. The economies
differ, and the anchor shows it: aleph reads **50.333555** here against
50.667083 there, and beta **2.684638** against 2.688264.

Those old numbers appear below only to say what the previous pass was aiming
at. Every gap, slope and bracketing verdict is computed from the four points in
this batch alone.

## Arm 1 -- aleph, owned by `value_of_life`. Target 80.0

| `value_of_life` | aleph, value of life / income |
|---|---|
| 38.4 (control) | 50.333555 |
| 54.0 (line 1) | 80.896129 |
| target | 80.000000 |

**BRACKETS.** 50.333555 < 80.0 < 80.896129. The target is enclosed by the
measured pair, and the points fall **one below and one above**: the control is
29.666445 short of the target, and line 1 overshoots it by **0.896129**.

This was the arm's purpose and it did what it was for. The previous pass
bracketed at 38.4 -> 54.5 with an overshoot of 1.268076; 54.0 was an attempt to
land inside rather than over. It did not land inside -- 54.0 still overshoots --
but the overshoot at this instrument value is 0.896129, and the bracket is now
38.4 to 54.0 rather than 38.4 to 54.5. The interval that contains the target has
been narrowed from the high side.

No instrument value is projected. For the record the pair spans a slope of
1.959139 in aleph per unit of `value_of_life` over 38.4 to 54.0, which is a
statement about that interval and nothing outside it.

## Arm 2 -- beta, owned by `discount_factor`. Band 3.0 to 4.5

| `discount_factor` | beta, wealth over output |
|---|---|
| 0.99715 (control) | 2.684638 |
| 0.99900 (line 2) | 2.896544 |
| band | 3.0 to 4.5 |

**DOES NOT BRACKET. Both points fall BELOW the band**, under its floor of 3.0.
The control is short by 0.315362 and line 2 by **0.103456**. The arm moved beta
toward the band -- raising the instrument raises beta -- but at 0.99900 it has
not reached the floor.

**No value of `discount_factor` that would land beta in the band is projected
here, and that is a refusal, not an omission.** The measured pair covers
0.99715 to 0.99900 and nothing outside it. The instrument sits inside 0.001 of
1, where the discounted sum it governs is nowhere near linear, and the
projection from a local slope has been made on this branch repeatedly and been
wrong every time.

The slope over this interval happens to be 114.544 in beta per unit of
`discount_factor`, essentially the 114 the previous pass measured over
0.99715 to 0.99800 on the older economy. The stability of that number across
two intervals and two sources is **not** a licence to extrapolate it: both
intervals are short and both sit at the same place on the curve. It is also a
*partial* slope holding `probability_becoming_unemployed` at 0.0437, and the
next section shows why that qualification matters more for beta than for
anything else here.

## Arm 3 -- pi_eu, owned by `probability_becoming_unemployed`. Target 0.139

| `probability_becoming_unemployed` | pi_eu, unemployment rate |
|---|---|
| 0.0300 (line 3) | 0.218296 |
| 0.0437 (control) | 0.260796 |
| target | 0.139000 |

**DOES NOT BRACKET. Both points fall ABOVE the target**, overshooting it by
0.079296 at 0.0300 and 0.121796 at 0.0437.

**The direction is right this time.** The previous pass took this arm upward,
0.0437 -> 0.0498, and moved pi_eu away from the target. Taking it down from
0.0437 to 0.0300 moved pi_eu down by 0.042501, closing a third of the gap. The
target still lies below both points, so the interval that would bracket it is
below 0.0300 and no point measured here reaches it.

### The ratio, which is the finding

The ratio of the unemployment rate to the flow probability driving it, at each
of the four points on this economy:

| point | `probability_becoming_unemployed` | pi_eu | ratio |
|---|---|---|---|
| line 3 | 0.0300 | 0.218296 | **7.2765** |
| control | 0.0437 | 0.260796 | **5.9679** |
| line 1 (aleph arm) | 0.0437 | 0.259722 | 5.9433 |
| line 2 (beta arm) | 0.0437 | 0.260607 | 5.9635 |

**The ratio does not hold near six. It RISES as the instrument comes down** --
from 5.97 at 0.0437 to 7.28 at 0.0300, a rise of 1.31 over a fall of 0.0137 in
the instrument.

The reading at 0.0437 is solid: three independent points sit at that instrument
value in this batch and the ratio at all three is 5.94 to 5.97, a spread of
0.025 across arms that moved two entirely different instruments. So the rise to
7.28 at 0.0300 is a real feature of the arm and not scatter.

What the rise means is that pi_eu is **not proportional** to the instrument. If
it were, the ratio would be flat and halving the instrument would halve the
rate. Instead the rate falls more slowly than the instrument does, which is the
signature of a component of unemployment that the instrument does not set at
all. The two points put that component at roughly 0.125 -- the intercept of the
line through them -- against a target of 0.139.

That is the substance of this arm, and it is worse news than the gap alone
suggests. **The target sits only a little above a floor the instrument appears
not to be able to go below**, so the closer the instrument comes to zero the
less of the remaining gap each step buys. The previous pass's suspicion -- that
the instrument does not set the rate on its own and the target may lie below
anything it can reach -- is supported here and sharpened: the target may lie
just barely *above* what the instrument alone can reach, in a region where the
arm has almost no leverage left.

No instrument value is projected for pi_eu, and the 0.125 figure above is a
two-point reading of a curve that these two points have just shown to be
curved. It is offered as the reason to stop treating this as a one-instrument
problem, not as a number to solve against.

## beta is still not cleanly owned, and the cross-effect got larger

Each arm moves the other arms' moments. Change from the control, with the
cross-effect as a share of the moment's own arm:

| moment | own arm | `value_of_life` moved it | `discount_factor` moved it | `probability_becoming_unemployed` moved it |
|---|---|---|---|---|
| aleph | +30.562573 | **(own)** | +1.928320 (6.3%) | +3.404423 (11.1%) |
| beta | +0.211906 | -0.048614 (22.9%) | **(own)** | **-0.156323 (73.8%)** |
| pi_eu | -0.042501 | -0.001074 (2.5%) | -0.000189 (0.4%) | **(own)** |

Three things follow.

1. **pi_eu is cleanly owned.** Neither other instrument moves it by more than
   2.5 per cent of what its own instrument does. The arm-3 movement is arm 3's.
2. **beta is not, and it is worse than the previous pass found.**
   `probability_becoming_unemployed` moved wealth over output by **73.8** per
   cent as much as `discount_factor` itself did, up from 62.9 per cent last
   pass, and `value_of_life` moved it by another 22.9 per cent. Both cross
   terms are negative where beta's own arm is positive, so a joint step that
   moves `probability_becoming_unemployed` down -- which arm 3 says is the
   direction pi_eu needs -- will push beta *further below* the band while
   `discount_factor` is trying to raise it. These two arms fight each other.
3. **aleph is mostly but not entirely owned.** The cross terms are 6 to 11 per
   cent of its own arm and both positive. The bracket in arm 1 is a bracket at
   this vector; it will move if either other instrument moves.

## Every targeted moment, all four points, one economy

| moment | control | l1 aleph | l2 beta | l3 pi_eu | target |
|---|---|---|---|---|---|
| `sigma_y` bottom half earnings share | 0.169050 | 0.169050 | 0.169050 | 0.169050 | 0.172000 |
| `tau_l` average labour income tax | 0.234373 | 0.233658 | 0.232966 | 0.230144 | 0.224000 |
| `omega_l` labour supply / total hours | 0.378556 | 0.377775 | 0.379336 | 0.375999 | 0.400000 |
| `beta` wealth over output | 2.684638 | 2.636023 | 2.896544 | 2.528314 | 3.0 to 4.5 |
| `h_1` homelessness rate | 0.084177 | 0.069239 | 0.081923 | 0.083694 | 0.003990 |
| `b` total drug users | 0.399892 | 0.394193 | 0.398518 | 0.395872 | 0.089000 |
| `lambda_d` disorder rate | 0.294582 | 0.291546 | 0.293804 | 0.294026 | 0.036800 |
| `theta` drug spending share | 0.331143 | 0.329243 | 0.331368 | 0.329695 | 0.162000 |
| `aleph` value of life / income | 50.333555 | 80.896129 | 52.261875 | 53.737979 | 80.000000 |
| `pi_eu` unemployment rate | 0.260796 | 0.259722 | 0.260607 | 0.218296 | 0.139000 |
| `cbar` food stamps / income | 0.008617 | 0.008657 | 0.008548 | 0.007022 | 0.004200 |
| `gamma` housing over expenditure | 0.137603 | 0.139865 | 0.137714 | 0.132886 | 0.268000 |
| `h_2` above half of spending | 0.106817 | 0.107237 | 0.107434 | 0.095011 | 0.101000 |
| `h_3` share in the largest unit | 0.479582 | 0.478761 | 0.481067 | 0.454860 | 0.626723 |
| `kappa_ued` unemployment given SUD | 0.522616 | 0.520087 | 0.522504 | 0.428498 | 0.162500 |
| `kappa_uem` employment given SMI | 0.066519 | 0.066493 | 0.066539 | 0.066552 | 0.300000 |
| `p_m` SMI population share | 0.050516 | 0.050616 | 0.050568 | 0.050922 | 0.052249 |
| `lambda_m` SMI share of the homeless | 0.025974 | 0.026094 | 0.026606 | 0.026189 | 0.250000 |
| `pi_V` eligibles with a voucher | 0.179213 | 0.179843 | 0.179036 | 0.174311 | 0.266000 |
| `tau_u` treatment take up | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.245000 |
| `mu_H` recovery housed / homeless | 1.091717 | 1.091853 | 1.091706 | 1.091544 | 1.473214 |

Two side effects worth flagging, neither of them anything these arms were aimed
at:

- **Line 1 moved the homelessness rate a long way.** `h_1` falls from 0.084177
  to 0.069239 when `value_of_life` goes from 38.4 to 54.0, an 18 per cent fall,
  much the largest move in that moment anywhere in this batch. `h_1` is an
  order of magnitude above its target of 0.003990 at every point, so this does
  not fix anything, but `value_of_life` is evidently a live instrument for it.
- **Line 3 moved `kappa_ued` from 0.522616 to 0.428498**, a fall of 0.094118
  toward its target of 0.1625 -- proportionally a larger move than the one it
  made in its own moment. Lowering the flow probability into unemployment does
  more for the unemployment-given-SUD ratio than it does for the unemployment
  rate.

`h_1`, `b` and `lambda_d` remain an order of magnitude above their targets at
every point, and `tau_u` is zero at every point against a target of 0.245.
Nothing in this batch addresses any of those.

## What this pass establishes

1. All four points are on one economy, `b8dc1077ad` / semantic `2f7c317e75`,
   with healthy solves and all invariants passing, and each line is a
   verified single-coordinate move off a control whose vector was checked on
   all forty-three coordinates.
2. **aleph brackets**, 50.333555 below and 80.896129 above the target of 80.0,
   with the high point overshooting by 0.896129 at `value_of_life` = 54.0.
3. **beta does not bracket**; both points sit below the band, short by 0.315362
   and 0.103456, and no instrument value is projected for it.
4. **pi_eu does not bracket**; both points sit above the target, but the arm
   was taken in the right direction this time and closed a third of the gap.
5. The pi_eu ratio **rises** as the instrument falls, 5.97 at 0.0437 to 7.28 at
   0.0300. It does not hold near six. The instrument does not set the rate on
   its own, and the target sits close above a floor the instrument has
   diminishing power over.
6. `beta`'s dependence on `probability_becoming_unemployed` has grown to 73.8
   per cent of its own instrument's effect, and the two arms pull beta in
   opposite directions. A joint round-1 step that treats these as separable
   will mis-assign the movement, and moving pi_eu the way arm 3 says it must go
   will make beta's shortfall worse.
