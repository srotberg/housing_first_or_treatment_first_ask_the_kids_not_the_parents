# Round 1 carried all together: five instruments at once, and three moments that were closed alone come open

`code/batch_round1_full.txt`, three lines, run one at a time from the repository
root and each allowed to finish before the next was issued. Unsecured borrowing
is off in all three. Nothing under `code/` was edited; in particular
`code/housing_first_or_treatment_first_SR_v1.f90` was not touched.

| | tag | what it moves off the anchor | MODEL | outcome |
|---|---|---|---|---|
| line 1 | `de2d34cf9e` | all five round-1 instruments | `b8dc1077ad` | solved, 12 min |
| line 2 | `9b39dfd463` | line 1 with `discount_factor` 0.99900 -> 0.99950 | `b8dc1077ad` | solved, 13 min |
| line 3 | `29a9f03376` | line 1 plus `relative_share_of_housing` 0.250 and `size_homelessness` 0.300 | `b8dc1077ad` | solved, 12 min |

## The three MODEL lines agree

**All three carry `MODEL b8dc1077ad`**, the semantic `2f7c317e75` this batch was
synced to and the hash of the source as it stands in the working tree. All three
report `HANDOVER OK: 42 of 42 parameters applied`, and all three pass 16 of 16
invariants with no failures. The three points are therefore on one economy and
every comparison below is a within-economy comparison.

The anchor is `point_f9c16d5308.txt`, already in the archive on the same
`b8dc1077ad`, 16 of 16 invariants passing. It was not re-run. Each line's
`VECTOR` was compared to the anchor's coordinate by coordinate, all forty-three:

    line 1 vs anchor:  discount_factor 0.99715 -> 0.99900
                       max_food_cost 0.0136 -> 0.0080
                       probability_becoming_unemployed 0.0437 -> 0.0122
                       probability_of_voucher_benchmark_used 0.024723 -> 0.047000
                       value_of_life 38.4 -> 54.0            (five diffs, no others)
    line 2 vs anchor:  the same five, with discount_factor 0.99950 instead
    line 3 vs anchor:  the same five, plus relative_share_of_housing 0.100 -> 0.250
                       and size_homelessness 0.149 -> 0.300  (seven diffs, no others)

The batch names thirty-nine parameters and the vector has forty-three
coordinates. The four it does not name -- `measure_child_gap`, `rho_m`,
`rung_ratio_h3`, `rung_ratio_h4` -- sit at `run_one_point.sh` defaults of 0, 1.0,
1.5 and 2.0, which are exactly the anchor's values, so the vectors are comparable
on all forty-three and the diff above is the whole of the difference.

## Round 1's nine, at every point

Targets: `aleph` 80.0, `beta` a BAND of 3.0 to 4.5, `omega_l` 0.40, `sigma_y`
0.172, `tau_l` 0.224, `pi_eu` 0.139, `pi_V` 0.266, `cbar` 0.0042, `w_bot` 0.0250.
`h_1` 0.00399, `gamma` 0.268 and `emp_homeless` 0.46 follow. `emp_homeless` is an
observed value rather than a target. **IN** marks inside ten per cent.

| moment | target | anchor | line 1 | line 2 | line 3 |
|---|---|---|---|---|---|
| `aleph` | 80.0 | 50.333555 (-37.1%) | 97.636370 (+22.0%) | 98.832197 (+23.5%) | 96.748487 (+20.9%) |
| `beta` | 3.0 to 4.5 | 2.684638 (-10.5% vs floor) | 2.359556 (-21.3% vs floor) | 2.412630 (-19.6% vs floor) | 2.262021 (-24.6% vs floor) |
| `omega_l` | 0.40 | 0.378556 (-5.4%) **IN** | 0.365678 (-8.6%) **IN** | 0.365879 (-8.5%) **IN** | 0.360617 (-9.8%) **IN** |
| `sigma_y` | 0.172 | 0.169050 (-1.7%) **IN** | 0.169050 (-1.7%) **IN** | 0.169050 (-1.7%) **IN** | 0.169050 (-1.7%) **IN** |
| `tau_l` | 0.224 | 0.234373 (+4.6%) **IN** | 0.225582 (+0.7%) **IN** | 0.224862 (+0.4%) **IN** | 0.227908 (+1.7%) **IN** |
| `pi_eu` | 0.139 | 0.260796 (+87.6%) | 0.137048 (-1.4%) **IN** | 0.137006 (-1.4%) **IN** | 0.138467 (-0.4%) **IN** |
| `pi_V` | 0.266 | 0.179213 (-32.6%) | 0.241446 (-9.2%) **IN** | 0.240691 (-9.5%) **IN** | 0.259238 (-2.5%) **IN** |
| `cbar` | 0.0042 | 0.008617 (+105.2%) | 0.002262 (-46.2%) | 0.002258 (-46.2%) | 0.002347 (-44.1%) |
| `w_bot` | 0.0250 | 0.029487 (+17.9%) | 0.018680 (-25.3%) | 0.018394 (-26.4%) | 0.016525 (-33.9%) |
| `h_1` | 0.00399 | 0.084177 (+2009.7%) | 0.057570 (+1342.9%) | 0.056807 (+1323.7%) | **0.000161 (-96.0%)** |
| `gamma` | 0.268 | 0.137603 (-48.7%) | 0.121518 (-54.7%) | 0.121500 (-54.7%) | 0.163269 (-39.1%) |
| `emp_homeless` | 0.46 obs | 0.964191 (+109.6%) | 0.983783 (+113.9%) | 0.983773 (+113.9%) | 0.158904 (-65.5%) -- see below, not a measurement |

## The answer: five of nine, and three of them broke on combining

**Five of round 1's nine are inside ten per cent on a single point**, and it is
the same five on all three lines: `omega_l`, `sigma_y`, `tau_l`, `pi_eu` and
`pi_V`. `aleph`, `cbar` and `w_bot` are outside on every line, and `beta` is
outside its band on every line.

The single-instrument arms this is measured against are all in the archive on the
same `b8dc1077ad`, all 16 of 16 invariants passing.

| moment | alone | combined (line 1) | verdict |
|---|---|---|---|
| `aleph` | **80.896129 (+1.1%)** at `value_of_life=54.0`, `point_85a8b00de2` | **97.636370 (+22.0%)** | **BROKE** |
| `cbar` | **0.004560 (+8.6%)** at `max_food_cost=0.0080`, `point_531868d8bd` | **0.002262 (-46.2%)** | **BROKE**, and it crossed its target |
| `w_bot` | **0.023671 (-5.3%)** at `value_of_life=54.0`, `point_85a8b00de2` | **0.018680 (-25.3%)** | **BROKE** |
| `pi_V` | 0.270715 (+1.8%) at `probability_of_voucher_benchmark_used=0.048`, `point_9724dc31eb` | 0.241446 (-9.2%) | held, but moved to the edge |
| `pi_eu` | never measured alone at 0.0122 | 0.137048 (-1.4%) | landed |
| `omega_l` | 0.378556 (-5.4%) at the anchor | 0.365678 (-8.6%) | held |
| `sigma_y` | 0.169050 (-1.7%) at the anchor | 0.169050 (-1.7%) | held, immobile everywhere |
| `tau_l` | 0.234373 (+4.6%) at the anchor | 0.225582 (+0.7%) | held, and improved |
| `beta` | 2.896544, -3.4% below the floor, at `discount_factor=0.99900`, `point_906b19d36f` | 2.359556, -21.3% below the floor | was never in the band; combining made it worse |

**Three moments were inside alone and are outside combined: `aleph`, `cbar` and
`w_bot`.** That is the finding, and it matters more than the count.

- **`aleph`**: 80.896129 alone, +1.1% -- as close to 80.0 as the search has come.
  Combined, 97.636370, +22.0%. It does not merely drift; it overshoots by
  seventeen units of `aleph` in a direction `value_of_life` was not moved in.
- **`cbar`**: 0.004560 alone, +8.6% and inside. Combined, 0.002262, -46.2%. It
  crosses its target and comes out on the far side at roughly half of it. The
  sign of the gap flips, so an instrument step read off the alone arm would be
  pointed the wrong way here.
- **`w_bot`**: 0.023671 alone, -5.3%. Combined, 0.018680, -25.3%. This is the one
  the brief predicted: `w_bot` was closed on `value_of_life`, which does not own
  it, and it does not survive the company of instruments that do move it.

Two cautions on reading that table. `pi_V`'s alone arm is at
`probability_of_voucher_benchmark_used=0.048` and the batch runs 0.047, so that
row is a near pair rather than an exact one. And `pi_eu` has no alone arm at
0.0122: the value came from interpolating inside the 0.0080/0.0150 bracket in
`PI_EU_LOW.md`, and this batch is the first measurement at it. It landed --
0.137048 against 0.139, -1.4% -- so the interpolation held up when four other
instruments moved with it.

## What broke them is `probability_becoming_unemployed`, and it can be attributed exactly

Another session measured `point_30121503f4` on this same `b8dc1077ad`, 16 of 16
invariants passing. Its vector was compared to line 1's coordinate by coordinate:
**exactly one of the forty-three differs**, `probability_becoming_unemployed`,
0.0437 against line 1's 0.0122. That makes the two a matched pair isolating the
fifth instrument, the one this batch adds and that batch does not carry.

| moment | four instruments (0.0437) | five instruments (0.0122) | what the fifth instrument did |
|---|---|---|---|
| `pi_eu` | 0.260758 (+87.6%) | 0.137048 (-1.4%) **IN** | closed it |
| `aleph` | 80.958644 (+1.2%) **IN** | 97.636370 (+22.0%) | **broke it** |
| `w_bot` | 0.023319 (-6.7%) **IN** | 0.018680 (-25.3%) | **broke it** |
| `cbar` | 0.004721 (+12.4%) | 0.002262 (-46.2%) | already out; drove it a further 34 points out |
| `beta` | 2.858569 (-4.7% vs floor) | 2.359556 (-21.3% vs floor) | cost it 0.499 of the 0.537 it lost |
| `pi_V` | 0.267921 (+0.7%) **IN** | 0.241446 (-9.2%) **IN** | held, moved to the edge |
| `omega_l` | 0.370568 (-7.4%) **IN** | 0.365678 (-8.6%) **IN** | held |
| `tau_l` | 0.233299 (+4.2%) **IN** | 0.225582 (+0.7%) **IN** | held, improved |
| `sigma_y` | 0.169050 (-1.7%) **IN** | 0.169050 (-1.7%) **IN** | nothing |

So the four-instrument combination is **six of nine** inside and the
five-instrument combination is **five of nine**. Carrying `pi_eu` buys `pi_eu`
and costs `aleph` and `w_bot`, a net loss of one. The whole of the difference
between the two counts is that single coordinate.

This is the same non-orthogonality the brief describes, now measured rather than
inferred: `probability_becoming_unemployed` moves `aleph` and `w_bot`, which it
does not own, hard enough to take both from inside ten per cent to outside it in
one step. `PI_EU_LOW.md` saw the `w_bot` half of this on its own arms; `aleph` is
new here, and it is the larger of the two, because at four instruments `aleph`
had already been closed to +1.2 per cent and had that much less room.

## `beta`: where each `discount_factor` lands, and no projection

| point | `discount_factor` | `beta` | distance below the 3.0 floor |
|---|---|---|---|
| anchor | 0.99715 | 2.684638 | 0.315362 (-10.5%) |
| alone, `point_906b19d36f` | 0.99900 | 2.896544 | 0.103456 (-3.4%) |
| **line 1** | **0.99900** | **2.359556** | **0.640444 (-21.3%)** |
| **line 2** | **0.99950** | **2.412630** | **0.587370 (-19.6%)** |
| **line 3** | **0.99900** | **2.262021** | **0.737979 (-24.6%)** |

**Every point is below the floor and none of them reaches the band.** Line 2's
higher `discount_factor` is the closest of the three and is still short of 3.0 by
0.587370.

**No value of `discount_factor` that would put `beta` in the band is projected
here**, and the arms give two independent reasons not to attempt one. First, the
local slope, line 1 to line 2, is 0.053074 of `beta` for 0.0005 of the
instrument, about 106 per unit -- measured inside 0.001 of 1, where the
discounted sum is nowhere near linear, over a step far shorter than the distance
to the floor. That projection has been made repeatedly on this branch and has
been wrong every time. Second, and more to the point:

**the combination moved `beta` away from the band, and it did so by more than
`discount_factor` moved it toward it.** Alone, raising `discount_factor` from
0.99715 to 0.99900 gained `beta` 0.211906. Combined at the same 0.99900, `beta`
is 0.536988 *below* where the alone arm put it -- and `point_30121503f4` locates
0.499013 of that 0.536988, ninety-three per cent, in
`probability_becoming_unemployed` alone. A `discount_factor` chosen off the alone
arm would therefore be solving for a `beta` that the rest of round 1 has already
taken away.

## Line 3: the street empties, and `emp_homeless` there is not a measurement

**`h_1` first, as the brief instructs.** On line 3, at
`relative_share_of_housing=0.250` and `size_homelessness=0.300`:

    h_1 = 1.6054257667378854E-004      target 0.00399      -96.0%

That is **0.016 per cent of the population homeless**, one twenty-fifth of the
target, and it is the only line of the three where `h_1` is below its target
rather than three orders of magnitude above it. For scale, the same housing and
street pair measured *alone* against the anchor, `point_f88fc8a75f`, gives `h_1` =
0.001322. Adding the other four instruments divides the remaining homeless mass
by a further **8.2**.

The upper bands are empty in absolute terms, not merely thin:

| band | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| homelessness rate | 5.60e-04 | 9.46e-05 | 1.26e-04 | **5.46e-06** | **9.93e-07** |

**`emp_homeless` = 0.158904 on line 3 is therefore not a measurement**, and it
should not be read as one or compared with the 0.46 observed. It is a share taken
over 1.61e-04 of the population, concentrated almost entirely in band 1, with
bands 4 and 5 holding about five in a million and one in a million respectively.
The apparent movement is dramatic -- 0.9838 on lines 1 and 2 against 0.1589 here,
which would look like the model's worst failure suddenly repaired -- and it is an
artefact of the denominator collapsing. The same pair measured alone, over a
homeless mass 8.2 times larger, reads `emp_homeless` = 0.586962; that number is
worth something and this one is not.

Line 3's other moments are unaffected by this and stand: it is the best of the
three on `pi_V` (-2.5%) and `pi_eu` (-0.4%) and on `gamma` (-39.1%, against -54.7%
on lines 1 and 2, which is the housing weight doing what it is for), and the worst
of the three on `beta` (-24.6%) and `w_bot` (-33.9%).

## A cross-check on the state file's "seven of nine", which is six

`code/CALIBRATION_STATE.md` gained a `READ THIS FIRST` header at `2740cb6`,
during this batch. It reports **"Round 1: seven of nine inside ten per cent on one
point"** for `point_846f6a0a53`, and lists among the seven:

    aleph   +2.3 *   pi_V   +5.1 *   w_bot  -7.0 *
    sigma_y -1.7 *   beta   +6.7 *   omega_l -8.1 *
    tau_l   +4.9 *

`beta` should not be in that group. Read off the point file:

    MOMENT beta   wealth over output   model = 2.8003658069118642   target = 3.0

**2.800366 is below the 3.0 floor, not above it**, so the entry is 6.7 per cent
*short of* the band rather than inside it, and the sign has been dropped. `beta`
is a BAND of 3.0 to 4.5 rather than a point target, and 2.800366 is outside it on
either edge. Counting the other eight the same way the header does, that point is
**six of nine, not seven**: `aleph`, `sigma_y`, `tau_l`, `pi_V`, `w_bot` and
`omega_l` inside; `beta` below the band, `cbar` +15.2 per cent and `pi_eu` +89.9
per cent outside.

This is recorded rather than corrected in place, because the header is another
session's and the file says its own sections are to be checked before being acted
on. It is the same arithmetic everywhere else in this note: `GAPS_0405.md` prints
`beta` as `2.55337  3-4.5  +14.9% out`, with the `out` that the header omits.

`point_846f6a0a53` is a genuine six-of-nine and the best round-1 point on this
economy -- better than any of this batch's three. It reaches it by NOT carrying
`pi_eu`, which is the trade this batch measures: it holds
`probability_becoming_unemployed` at the anchor's 0.0437 and leaves `pi_eu` at
+89.9 per cent.

### The emp_homeless comparisons rest on a thin street as well

The header's first open decision quotes `emp_homeless` "best is 0.587 against
0.46". That is `point_f88fc8a75f`, where `h_1` = 0.001322, sixty-seven per cent
below its target. `point_846f6a0a53` reads `emp_homeless` = 0.867900 at `h_1` =
5.38e-04, eighty-seven per cent below target. Line 3 of this batch reads 0.158904
at `h_1` = 1.61e-04.

| point | `relative_share_of_housing` | `h_1` | vs target | `emp_homeless` |
|---|---|---|---|---|
| `point_f88fc8a75f` | 0.250 | 0.001322 | -66.9% | 0.586962 |
| `point_846f6a0a53` | 0.200 | 0.000538 | -86.5% | 0.867900 |
| line 3, `29a9f03376` | 0.250 | 0.000161 | -96.0% | 0.158904 |

`emp_homeless` and `h_1` move together and in opposite directions here, and every
one of these three sits below the `h_1` target rather than above it. Whatever is
concluded about `emp_homeless` from this family of points is being concluded over
a homeless mass that is itself a long way from where it is supposed to be, and at
line 3's 1.61e-04 there is not enough of it left to read a share off at all. The
numbers are given so the reader can judge; which of them is usable is not this
note's call.

## What this batch establishes

1. All three lines are on one economy, `b8dc1077ad`, with full handover and no
   invariant failures. The comparisons are sound.
2. **Five of round 1's nine are inside ten per cent** on a single point, the same
   five on all three lines: `omega_l`, `sigma_y`, `tau_l`, `pi_eu`, `pi_V`.
3. **Three that were inside alone are outside combined: `aleph` (+1.1% -> +22.0%),
   `cbar` (+8.6% -> -46.2%, crossing its target), and `w_bot` (-5.3% -> -25.3%).**
   Combining broke them; this is the finding.
4. The breakage is attributable to one coordinate.
   `probability_becoming_unemployed` at 0.0122 rather than 0.0437 is the entire
   difference between a six-of-nine point and a five-of-nine point, and it is what
   takes `aleph` and `w_bot` out.
5. `beta` reaches the band at none of the three, and the combination moves it
   *away* from the band by more than `discount_factor` moves it toward the band.
   No instrument value is projected for it.
6. Line 3's `emp_homeless` is void: the street holds 1.61e-04 of the population
   there. `h_1`, `gamma` and the rest of line 3 stand.
7. The `READ THIS FIRST` header added to `code/CALIBRATION_STATE.md` at `2740cb6`
   counts `point_846f6a0a53` as seven of nine by scoring `beta` = 2.800366 as
   `+6.7` inside. It is 6.7 per cent BELOW the 3.0 floor and outside the band.
   That point is six of nine, and it is still the best round-1 point on this
   economy.

The instrument-by-instrument arms are not additive on this economy, and the three
moments that fail are the three that were closed on instruments which do not own
them -- `aleph` and `w_bot` both on `value_of_life`, `cbar` on a `max_food_cost`
arm that `probability_becoming_unemployed` moves as hard. Round 1 cannot be closed
by setting each instrument on its own arm and then running them together; that is
what this batch tried and it loses three of the five it had.
