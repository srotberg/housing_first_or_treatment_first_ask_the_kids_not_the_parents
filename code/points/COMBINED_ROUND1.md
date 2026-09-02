# ROUND 1 COMBINED -- four instruments that each landed alone, put on one point

`code/batch_combined.txt`, three lines, run one at a time from the repository
root, each allowed to finish before the next was started and each committed
before the next was fired. No rebase was taken between lines. Borrowing is off
throughout (`include_unsecured_borrowing=0`).

Round 1's four solved instruments were each measured ALONE against the anchor
and each landed its moment. Four instruments that each work alone need not work
together, and the arms are demonstrably not orthogonal. This batch is the test.

| | vector off the anchor | tag | MODEL | outcome |
|---|---|---|---|---|
| line 1 | `value_of_life` 54.0, `probability_of_voucher_benchmark_used` 0.047, `max_food_cost` 0.0080, `discount_factor` **0.99900** | `30121503f4` | `b8dc1077ad` | solved, 12 min |
| line 2 | the same three, `discount_factor` **0.99950** | `54f94f5ab3` | `b8dc1077ad` | solved, 12 min |
| line 3 | the same as line 1 plus `relative_share_of_housing` **0.200** | `846f6a0a53` | `b8dc1077ad` | solved, 11 min |

## The three MODEL lines agree, and that was checked rather than assumed

**All three points carry `MODEL b8dc1077ad`**, the head this batch was synced to
(semantic `2f7c317e75`). All three report `HANDOVER OK: 42 of 42 parameters
applied` and `INVARIANTS: all PASS`, 16 of 16, with no failure anywhere -- line
3 included, which matters because the closest thing to it in the archive
(`point_044813dbd2`, housing weight 0.300) fails two invariants on an empty
street.

The comparison anchor, `point_f9c16d5308.r2a_anchor.txt`, is on the same
`b8dc1077ad`, and so are all four alone-arms differenced against below. Every
number in this note is a within-economy comparison. No source change landed
mid-batch; the build happened once, at the top of line 1, from
`b8dc1077adc90fe0d9b497289e93e7c5`, and lines 2 and 3 reused that binary.

Each line's `VECTOR` was diffed against the anchor's coordinate by coordinate,
all forty-three:

    line 1 vs anchor:  4 differences, and they are exactly the four intended
    line 2 vs anchor:  the same four, discount_factor at 0.99950 instead
    line 3 vs anchor:  those four plus relative_share_of_housing 0.100 -> 0.200

    line 1 vs line 2:  discount_factor, and nothing else
    line 1 vs line 3:  relative_share_of_housing, and nothing else

So lines 1 and 2 are a matched pair in `discount_factor` and lines 1 and 3 are a
matched pair in the housing weight.

## The alone readings this is differenced against

Each is a verified single-coordinate move off the same anchor on the same model.

| moment | instrument | alone value | alone reading | target | alone gap |
|---|---|---|---|---|---|
| `aleph` | `value_of_life` | 54.0 | 80.896129 | 80.0 | **+1.12%** |
| `pi_V` | `probability_of_voucher_benchmark_used` | 0.048 | 0.270715 | 0.266 | **+1.77%** |
| `cbar` | `max_food_cost` | 0.0080 | 0.004560 | 0.0042 | **+8.56%** |
| `w_bot` | (closed on the `value_of_life` arm) | 54.0 | 0.023671 | 0.0250 | **-5.32%** |
| `beta` | `discount_factor` | 0.99900 | 2.896544 | band 3.0-4.5 | below floor by 0.103456 |

One difference to keep in view: **the alone `pi_V` arm was measured at an
instrument of 0.048 and this batch runs 0.047.** That is not a like-for-like
instrument value, and `pi_V` is the one moment here whose combined reading is
*better* than its alone reading.

## The round-1 block, a full row per point

Percentages are (model - target) / target. `beta` is a BAND, 3.0 to 4.5, not a
point, so it is scored in or out of the band and its shortfall is quoted against
the floor.

| moment | target | anchor | line 1 | line 2 | line 3 | l1 gap | l2 gap | l3 gap |
|---|---|---|---|---|---|---|---|---|
| `aleph` value of life / income | 80.0 | 50.627977 | 80.958644 | 81.756310 | 81.841737 | **+1.20%** | **+2.20%** | **+2.30%** |
| `beta` wealth over output | BAND 3.0-4.5 | 2.688315 | 2.858569 | 2.918631 | 2.800366 | OUT, -0.141431 below floor | OUT, -0.081369 below floor | OUT, -0.199634 below floor |
| `omega_l` labour supply / hours | 0.40 | 0.378574 | 0.370568 | 0.370826 | 0.367601 | **-7.36%** | **-7.29%** | **-8.10%** |
| `sigma_y` bottom half earnings share | 0.172 | 0.169050 | 0.169050 | 0.169050 | 0.169050 | **-1.72%** | **-1.72%** | **-1.72%** |
| `tau_l` average labour income tax | 0.224 | 0.233623 | 0.233299 | 0.232948 | 0.234964 | **+4.15%** | **+3.99%** | **+4.89%** |
| `pi_eu` unemployment rate | 0.139 | 0.260325 | 0.260758 | 0.260755 | 0.264014 | +87.60% | +87.59% | +89.94% |
| `pi_V` eligibles with a voucher | 0.266 | 0.179386 | 0.267921 | 0.267863 | 0.279442 | **+0.72%** | **+0.70%** | **+5.05%** |
| `cbar` food stamps / income | 0.0042 | 0.008598 | 0.004721 | 0.004713 | 0.004839 | +12.39% | +12.22% | +15.22% |
| `w_bot` net worth share, bottom half | 0.0250 | 0.030199 | 0.023319 | 0.023447 | 0.023247 | **-6.73%** | **-6.21%** | **-7.01%** |
| `h_1` homelessness rate | 0.00399 | 0.082821 | 0.053862 | 0.053772 | 0.000538 | +1249.93% | +1247.67% | -86.51% |
| `gamma` housing over expenditure | 0.268 | 0.137692 | 0.132225 | 0.132174 | 0.165435 | -50.66% | -50.68% | -38.27% |
| `emp_homeless` employed share of the homeless | 0.46 | 0.964216 | 0.963730 | 0.963750 | 0.867900 † | +109.51% | +109.51% | +88.67% † |

Bold is inside ten per cent. † see the line-3 section: that reading is taken
over a street that has all but emptied and is not a measurement.

## The answer: SIX of round 1's nine moments are inside ten per cent on one point

The same six on all three lines:

    IN   aleph    +1.20% / +2.20% / +2.30%
    IN   omega_l  -7.36% / -7.29% / -8.10%
    IN   sigma_y  -1.72% / -1.72% / -1.72%
    IN   tau_l    +4.15% / +3.99% / +4.89%
    IN   pi_V     +0.72% / +0.70% / +5.05%
    IN   w_bot    -6.73% / -6.21% / -7.01%

    OUT  beta     below the band floor at all three points
    OUT  cbar     +12.39% / +12.22% / +15.22%
    OUT  pi_eu    +87.60% / +87.59% / +89.94%

Six of nine, and the count is the same whichever line is read. Line 2 is the
best single point of the three on this scoring: it holds the same six and its
`beta` shortfall is the smallest.

### Which moved out of range when combined that was inside alone: `cbar`, and only `cbar`

Named individually, for all four instruments that landed alone:

| moment | alone | combined (line 1) | verdict |
|---|---|---|---|
| `aleph` | +1.12% | +1.20% | **held.** Cost 0.08 points of gap. |
| `pi_V` | +1.77% | +0.72% | **held, and improved** -- though at 0.047 rather than the 0.048 it was measured at alone. |
| `w_bot` | -5.32% | -6.73% | **held.** Drifted 1.4 points further out but stayed well inside. |
| `cbar` | +8.56% | **+12.39%** | **BROKE.** Inside alone, outside combined. |

**`cbar` is the one that combining broke,** and it is the finding. It was the
narrowest of the four alone -- +8.56% against a ten per cent bar leaves 1.44
points of headroom -- and the cross-effects ate all of it and 2.4 points more.

`beta` and `pi_eu` were never inside on any point, alone or combined, so neither
can be said to have broken; but `beta` got materially worse when combined, and
that is the second finding, below.

### What pushed `cbar` out, and it is `pi_V`'s instrument

Each alone-arm's effect on `cbar` off the anchor:

| arm | `cbar` | ratio to anchor |
|---|---|---|
| anchor | 0.00859817 | -- |
| `value_of_life` 54.0 | 0.00865712 | 1.006855 |
| `probability_of_voucher_benchmark_used` 0.048 | 0.00890442 | **1.035617** |
| `discount_factor` 0.99900 | 0.008548 | 0.994167 |
| `max_food_cost` 0.0080 (own arm) | 0.00455962 | 0.530302 |

The voucher instrument raises `cbar` by 3.56 per cent, the value of life by 0.69
per cent. Applied multiplicatively to the alone `cbar` arm:

    0.00455962 x 1.035617 x 1.006855  =  0.00475439
    observed on line 1                =  0.00472050    (0.7% apart)

So the cross-effects on `cbar` are close to **proportional**, not additive: they
scale the level rather than shift it. That is why the arm survives being halved
and still fails -- halving `cbar` also halves the absolute cross-effects, but it
leaves the *percentage* gap they add untouched, and a +3.6% and a +0.7% on top
of +8.56% clears the ten per cent bar on their own. The three points are
consistent with that reading; they do not prove it, and it is offered as the
mechanism to check next, not as a law.

The practical consequence: **`max_food_cost` has to be set below 0.0080 on the
joint point, and the alone arm cannot tell you how far below** -- the arm was
solved against a `cbar` level that the voucher instrument then moved.

### `beta` got worse when combined, at the same instrument value

`discount_factor` is 0.99900 on both the alone arm and combined line 1.

    alone (arm 906b19d36f)  beta 2.896544   short of the 3.0 floor by 0.103456
    combined (line 1)       beta 2.858569   short of the 3.0 floor by 0.141431

**The same instrument value buys 0.037975 less `beta` in company than it does
alone**, a 37 per cent widening of the shortfall. Line 2 raises the instrument
to 0.99950 and recovers to 2.918631, short by 0.081369 -- so 0.00050 more
`discount_factor` bought +0.060062 of `beta`, a slope of about 120 per unit over
that interval, in line with the 114 measured twice before.

**No `discount_factor` that would land `beta` in the band is projected here.**
The measured pair covers 0.99900 to 0.99950 and nothing outside it, the
instrument is inside 0.001 of 1 where the discounted sum is nowhere near linear,
and that extrapolation has been made on this branch repeatedly and been wrong
every time. What the pair does establish is that the shortfall is now small --
2.7 per cent of the floor at line 2, against 10.4 per cent at the anchor -- and
that the cross-effects work against it.

### `pi_eu` is untouched and remains the largest failure in the block

0.2603 at the anchor, 0.2608 combined, against a target of 0.139. **No
instrument in this batch moves it**: the spread across all three lines is 0.0033,
and 0.0033 of that is line 3's housing weight. `probability_becoming_unemployed`
is at its anchor value of 0.0437 on every line here, so this is not a test of
that arm and nothing here revises `ROUND1_PASS2_B`'s finding that the target may
lie below what the instrument alone can reach.

## Line 3: the street empties, and `emp_homeless` there is not a measurement

**Checked before reading `emp_homeless`, as required, and the caveat applies.**

| | line 1 | line 3 | anchor |
|---|---|---|---|
| `h_1` homelessness rate | 0.053862 | **0.000538** | 0.082821 |
| working-age homeless mass | 3.4063 | **0.047363** | 5.2121 |
| total population mass | ~87.55 | ~87.97 | ~87.67 |
| `emp_homeless` | 0.963730 | *0.867900* | 0.964216 |

At a housing weight of 0.200 the homeless are **0.054 per cent of the
population**, a working-age mass of 0.047 against line 1's 3.406 -- **72 times
smaller**. `h_1` lands 86.5 per cent BELOW its target of 0.00399, having been
1250 per cent above it on line 1; the instrument does not close the gap, it
overshoots it by an order of magnitude in the other direction.

Worse for the reading, what mass remains is not spread over the life cycle. From
line 3's age bands:

    age 26  homeless rate 0.019559  of cohort mass 2.000000  ->  homeless mass 0.039118
    age 27  homeless rate 0.002297                           ->            0.004588
    age 28  homeless rate 0.000225                           ->            0.000449
    ...

Age 26 alone holds **82.6 per cent of the entire working-age homeless mass**
(0.039118 of 0.047363), and the rate has fallen by two orders of magnitude by
age 28. So line 3's `emp_homeless` of 0.8679 is very nearly a statement about
26-year-old newborns and almost nothing else.

**That number should not be read as the employed share of the homeless.** It is
not degenerate the way `point_044813dbd2` was -- the denominator is positive,
every invariant passes, and the five age bands do hold all of the homeless -- but
it is a share taken over a population the model has all but eliminated, and it is
not comparable to line 1's 0.9637, which is taken over seventy-two times the
mass. The same caveat applies to line 3's `h_1` and to any other
conditional-on-homeless quantity on that point.

For the record, the housing weight's effect on `emp_homeless` in isolation
(`point_ba54a7ef7d`, weight 0.200, `h_1` = 0.000522, mass 0.046249) has exactly
the same problem, and `HOUSING_WEIGHT.md` reported the movement there as real.
This batch does not contradict that; it adds that on the combined point the same
instrument produces the same near-empty street, so the apparent 0.096 improvement
in `emp_homeless` on line 3 is bought by deleting the population it is measured
over. **The housing weight is not a usable instrument for `emp_homeless` at
0.200 on this point.**

Line 3's `gamma` and `omega_l` are population averages, not conditional on
homelessness, and are used without that caveat: the housing weight moves `gamma`
from 0.132225 to 0.165435, closing a quarter of the gap to 0.268 -- the largest
movement in `gamma` anywhere in this batch -- while costing `pi_V` 4.3 points of
accuracy and `cbar` another 3 points of overshoot.

## What this batch establishes

1. All three points are on one economy, `b8dc1077ad` / semantic `2f7c317e75`,
   built once at the top of the batch, with healthy solves and all sixteen
   invariants passing on each. Every vector was verified coordinate by
   coordinate against the anchor and against the other lines.
2. **Six of round 1's nine moments are inside ten per cent on a single point**,
   the same six on all three lines: `aleph`, `omega_l`, `sigma_y`, `tau_l`,
   `pi_V` and `w_bot`.
3. **Combining broke exactly one moment that was inside alone, and it is
   `cbar`** -- +8.56% alone, +12.39% combined. `aleph`, `pi_V` and `w_bot` all
   survived the joint step.
4. The mechanism is `pi_V`'s instrument, which scales `cbar` by 1.0356, and the
   cross-effects on `cbar` are proportional rather than additive. `max_food_cost`
   must come below 0.0080 on the joint point and the alone arm cannot say how far.
5. **`beta` is worse in company than alone at the same instrument value**,
   2.858569 against 2.896544, a 37 per cent wider shortfall. It is still out of
   the band at all three points; line 2's 2.918631 is the closest approach
   measured on this economy. No instrument value is projected for it.
6. `pi_eu` is untouched by everything in this batch and remains the block's
   largest failure at +88%.
7. **Line 3's `emp_homeless` and `h_1` are not usable.** The housing weight at
   0.200 empties the street to 0.054 per cent of the population, 83 per cent of
   what is left is a single age, and `h_1` overshoots its target 86 per cent
   low. Its `gamma` gain is real; its homelessness readings are not measurements.
