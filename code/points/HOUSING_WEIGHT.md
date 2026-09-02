# THE WEIGHT ON HOUSING -- does it move `emp_homeless`, where the wealth tail and the price of the rung could not

Three points, run in sequence in one container on one binary, no rebase between
them. Each moves ONE coordinate off the anchor. Borrowing is off throughout
(`include_unsecured_borrowing=0`).

The question is the third explanation for the same failure: **96 per cent of the
homeless are employed against a target of 46.** Two explanations have already
been measured and both were wrong -- a thin wealth tail (the tail thinned
eightfold, by-choice fell under two points) and the price of the cheapest rental
(the rung more than doubled, the employed share moved 0.007 against a gap of
0.494).

Flow utility is Cobb-Douglas and multiplicative in housing and consumption, with
`relative_share_of_housing` the weight on housing. If housing barely enters
utility, the street's rent saving may dominate its size penalty for everyone,
employed or not. Lines 1 and 2 raise that weight. Line 3 is the control on a
rival story -- that the employed take the street because working leaves them
less time to enjoy a dwelling -- and moves the leisure weight instead.

## All four points are on the same model

    point_f9c16d5308.r2a_anchor   MODEL b8dc1077ad   CONTROL, batch_r2a line 1
    point_ba54a7ef7d              MODEL b8dc1077ad   line 1, housing weight 0.200
    point_044813dbd2              MODEL b8dc1077ad   line 2, housing weight 0.300
    point_9d3e583617              MODEL b8dc1077ad   line 3, leisure weight 1.500000

**The four MODEL lines agree**, and were confirmed equal before any number below
was compared, so the arms are differences in the instrument and not differences
in the Fortran.

Each arm's `VECTOR` line was diffed against the control's, coordinate by
coordinate. Each differs in **exactly one** coordinate -- the instrument named.
The three arms are matched pairs with the control.

The control was run by another worker, in another container. It is `batch_r2a`
line 1, recorded at `point_f9c16d5308.r2a_anchor.txt` rather than at the plain
tag path because `point_f9c16d5308.txt` already holds RUN3 of the determinism
study on the same vector. Those two independent runs of the control vector
differ by **2.5e-05** on `emp_homeless`, which is the cross-container noise floor
for the quantity this note is about. Every movement reported below for the
housing weight is four orders of magnitude larger than that.

`INVARIANTS: all PASS` on the control, on line 1 and on line 3. **Line 2 fails
two invariants**, for the reason given in its own section.

## The four points

| | control | line 1 | line 2 | line 3 |
|---|---|---|---|---|
| instrument | -- (anchor) | `relative_share_of_housing` | `relative_share_of_housing` | `relative_share_of_leisure` |
| value | 0.100 / 3.050529 | **0.200** | **0.300** | **1.500000** |
| employed share of the homeless (target 0.46) | 0.964216 | **0.691657** | *undefined* † | **0.957242** |
| homeless by choice | 0.980735 | 1.000000 | *NaN* † | 0.982628 |
| homeless who could afford it on INCOME ALONE | 0.979523 | 1.000000 | *0* † | 0.981978 |
| `h_1` (target 0.00399) | 0.0828210 | **0.000522114** | **0.000000000** | 0.0681361 |
| `gamma` (target 0.268) | 0.137692 | 0.177880 | 0.191698 | 0.127449 |
| `omega_l` (target 0.40) | 0.378574 | 0.374760 | 0.368400 | **0.467902** |

† **Line 2 has no homeless population at all.** `h_1` is exactly zero, so every
"share of the homeless" is a ratio with zero in the denominator. The `1.000000`
the code prints for the employed share is what an empty set returns, not a
measurement, and it is not used anywhere in the analysis below. Two invariants
fail on this point and say so directly:

    INVARIANT FAIL   homeless by choice, share of the homeless  =  NaN  outside [0,1]
    INVARIANT FAIL   the five age bands hold all of the homeless =  NaN  want 1.0000

Line 2's `gamma` and `omega_l` are still well defined -- they are population
averages, not conditional-on-homeless shares -- and are reported and used.

## The answer: the housing weight moves it, the leisure weight does not

**Yes, one of the two instruments moves `emp_homeless` materially toward 0.46,
and it is the housing weight.** This is the first of the three explanations
tested on this branch that moves the quantity at all.

    gap to close at the control:  0.964216 - 0.46  =  0.504216

    housing weight  0.100 -> 0.200   emp_homeless  0.964216 -> 0.691657
                                     movement      -0.272559
                                     PER UNIT OF INSTRUMENT   -2.7256
                                     elasticity               -0.2827
                                     share of the gap closed  54.1 per cent

    leisure weight  3.050529 -> 1.500000   emp_homeless  0.964216 -> 0.957242
                                     movement      -0.006975
                                     PER UNIT OF INSTRUMENT   +0.004498
                                     elasticity               +0.014231
                                     share of the gap closed  1.38 per cent

Per unit of instrument the housing weight is **606 times** the leisure weight.
The instruments have very different natural scales, so on the scale-free
comparison -- elasticity of `emp_homeless` with respect to the instrument -- the
housing weight is still **19.9 times** the leisure weight.

The leisure arm's 0.006975 is the same order as the 0.007 the rental-rung arm
produced against the same 0.494-wide gap, and that movement was reported as a
failure. It is 280 times the 2.5e-05 noise floor, so it is a real movement and
not noise -- it is simply far too small to matter against a gap of 0.504.

**The rival story is refuted, and refuted by an arm that had every chance to show
itself.** The leisure weight is not a weak instrument in general: the same move
took `omega_l` from 0.378574 to 0.467902, an 0.089 swing that carries it clean
across its own target of 0.40. So the leisure arm moved labour supply hard and
left the composition of the homeless where it found it. **The employed are not on
the street because working leaves them no time to enjoy a dwelling.**

## What the housing weight costs, and the limit of what was measured

The movement is real but it is not free, and the two measured arms **do not
bracket 0.46**:

    housing 0.100   emp_homeless 0.964216      above target
    housing 0.200   emp_homeless 0.691657      still above target
    housing 0.300   no homeless population -- nothing to measure

The employed share is still 0.232 above target at the far usable arm, and the
next arm out has already emptied the set. **No instrument value is projected
here.** Extrapolating past the measured arms has been done on this branch
repeatedly and has been wrong every time. What is established is the sign, the
magnitude over the measured step, and the fact that the instrument runs out
before the target is reached.

The reason it runs out is that the housing weight is doing this by **destroying
the homelessness rate**:

    h_1   0.0828210  ->  0.000522114  ->  0.000000000        target 0.00399

`h_1` falls by a factor of 159 across the first arm and to exactly zero across
the second. The target 0.00399 lies between the control and line 1, so the
housing weight **BRACKETS `h_1`** -- which is a live and useful finding for that
moment in its own right, since the control sits 21 times above target. But it
means `emp_homeless` and `h_1` cannot both be delivered by this instrument: the
employed share is being computed over a set that is vanishing underneath it, and
by the time the weight is large enough to have taken the employed share halfway
to target, the homelessness rate has already crossed its own target and gone
seven times below it.

Two further readings of the same collapse, both from line 1:

- `homeless by choice` rises 0.980735 -> **1.000000** and `could afford it on
  INCOME ALONE` rises 0.979523 -> **1.000000**. What survives at housing weight
  0.200 is entirely voluntary and entirely able to pay. The involuntary margin is
  gone, not reduced.
- The direction is the one the hypothesis predicted. Making housing matter more
  in utility pulls people off the street, and it pulls the *employed* off faster
  than the unemployed -- which is what a mechanism where the employed were on the
  street *because housing was nearly worthless in utility* looks like.

## The other targeted moments across the arms

`gamma`, the moment that motivated the test, moves the right way under the
housing weight and the wrong way under leisure, and does not bracket under
either:

    gamma   control 0.137692   housing 0.200 -> 0.177880   housing 0.300 -> 0.191698
                               leisure 1.5   -> 0.127449                target 0.268

All four points are **below** the target of 0.268. The housing weight closes
0.054 of a 0.130 gap over a tripling, and does not reach it. No bracket.

`omega_l` brackets under the leisure weight and moves slightly away under the
housing weight:

    omega_l control 0.378574   housing 0.200 -> 0.374760   housing 0.300 -> 0.368400
                               leisure 1.5   -> 0.467902                target 0.40

0.378574 < 0.40 < 0.467902. **The leisure weight BRACKETS `omega_l`.**

## Summary

1. **The housing weight moves `emp_homeless` and the leisure weight does not.**
   -2.7256 per unit against +0.004498 per unit; 19.9 to 1 on elasticity. Over the
   one usable arm the housing weight closes 54.1 per cent of the gap to 0.46 and
   the leisure weight closes 1.38 per cent.
2. **The third explanation is the first one that is not simply wrong** -- but it
   does not deliver the target either. The two arms do not bracket 0.46, and the
   second has no homeless population to measure. Nothing is projected past them.
3. **It works by emptying the street.** `h_1` goes 0.0828 -> 0.000522 -> 0, and
   the survivors at 0.200 are 100 per cent by choice and 100 per cent able to
   afford housing. `emp_homeless` and `h_1` are not separately deliverable by
   this instrument.
4. **`h_1` is bracketed by the housing weight** (0.00399 sits between 0.0828 and
   0.000522) and **`omega_l` is bracketed by the leisure weight** (0.40 sits
   between 0.3786 and 0.4679). Both are usable findings for those moments.
5. **`gamma` is not bracketed by either.** All four points are below 0.268.
