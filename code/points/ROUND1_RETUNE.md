# Round 1 re-aimed against the COMBINED point: six, seven and six of nine, and `w_bot` is worse everywhere

`code/batch_round1_retune.txt`, three lines, run one at a time from the
repository root and each allowed to finish before the next was issued. Unsecured
borrowing is off in all three. Nothing under `code/` was edited; in particular
`code/housing_first_or_treatment_first_SR_v1.f90` was not touched. No line
failed to build and no line segfaulted.

| | tag | what it moves off line 1 | MODEL | outcome |
|---|---|---|---|---|
| line 1 | `aa6590231d` | -- (the re-aimed centre) | `b8dc1077ad` | solved, 11 min |
| line 2 | `990da2a08d` | `value_of_life` 45.0 -> 42.0, `max_food_cost` 0.0150 -> 0.0130 | `b8dc1077ad` | solved, 10 min |
| line 3 | `39ef9467b2` | `discount_factor_impatient` 0.62 -> 0.68 | `b8dc1077ad` | solved, 10 min |

## The three MODEL lines agree

**All three carry `MODEL b8dc1077ad`**, the semantic `2f7c317e75` this batch was
synced to and the hash of the source as it stands in the working tree. It is also
the hash `ROUND1_FULL.md` measured on, so this batch and that one are directly
comparable. All three report `HANDOVER OK: 42 of 42 parameters applied`, and all
three pass **16 of 16 invariants with no failures**. The three points are on one
economy and every comparison below is a within-economy comparison.

## What each line moves off the combined point

The combined point is `point_de2d34cf9e.txt`, line 1 of `ROUND1_FULL.md`, on the
same `b8dc1077ad` with 16 of 16 invariants passing. It was not re-run. Each
line's `VECTOR` was compared to it coordinate by coordinate, all forty-three.
The four coordinates the batch does not name -- `measure_child_gap`, `rho_m`,
`rung_ratio_h3`, `rung_ratio_h4` -- sit at `run_one_point.sh` defaults of 0, 1.0,
1.5 and 2.0, which are the combined point's values, so the vectors are comparable
on all forty-three and the diffs below are the whole of the difference.

    line 1 vs combined:  discount_factor            0.99900 -> 0.99950
                         discount_factor_impatient  0.55    -> 0.62
                         max_food_cost              0.0080  -> 0.0150
                         probability_of_voucher...  0.047   -> 0.052
                         value_of_life              54.0    -> 45.0    (five diffs, no others)
    line 2 vs combined:  the same five, with max_food_cost 0.0130 and value_of_life 42.0
    line 3 vs combined:  the same five, with discount_factor_impatient 0.68

**`probability_becoming_unemployed` is held at 0.0122 on all three**, exactly as
the combined point carries it. `pi_eu` landed there and its instrument was left
alone, as instructed.

There is a tighter reference available. `point_9b39dfd463`, line 2 of
`ROUND1_FULL.md`, already carries `discount_factor=0.99950`, so retune line 1
differs from it in **four** coordinates rather than five, isolating the four
instruments this batch actually re-aims. It is carried as its own column below.

## Round 1's nine, plus `h_1`, `gamma` and `emp_homeless`

Targets: `aleph` 80.0, `beta` a BAND of 3.0 to 4.5, `omega_l` 0.40, `sigma_y`
0.172, `tau_l` 0.224, `pi_eu` 0.139, `pi_V` 0.266, `cbar` 0.0042, `w_bot` 0.0250.
`h_1` 0.00399 and `gamma` 0.268 follow. `emp_homeless` is an observed value of
0.46 rather than a target. **IN** marks inside ten per cent.

| moment | combined `de2d34cf9e` | `9b39dfd463` | line 1 `aa6590231d` | line 2 `990da2a08d` | line 3 `39ef9467b2` |
|---|---|---|---|---|---|
| `aleph` | 97.636370 (+22.0%) | 98.832197 (+23.5%) | 82.285865 (+2.9%) **IN** | 74.001083 (-7.5%) **IN** | 82.566850 (+3.2%) **IN** |
| `beta` | 2.359556 (-21.3% vs floor) | 2.412630 (-19.6% vs floor) | 2.351825 (-21.6% vs floor) | 2.372005 (-20.9% vs floor) | 2.363149 (-21.2% vs floor) |
| `omega_l` | 0.365678 (-8.6%) **IN** | 0.365879 (-8.5%) **IN** | 0.363441 (-9.1%) **IN** | 0.363737 (-9.1%) **IN** | 0.363314 (-9.2%) **IN** |
| `sigma_y` | 0.169050 (-1.7%) **IN** | 0.169050 (-1.7%) **IN** | 0.169050 (-1.7%) **IN** | 0.169050 (-1.7%) **IN** | 0.169050 (-1.7%) **IN** |
| `tau_l` | 0.225582 (+0.7%) **IN** | 0.224862 (+0.4%) **IN** | 0.225532 (+0.7%) **IN** | 0.225810 (+0.8%) **IN** | 0.226059 (+0.9%) **IN** |
| `pi_eu` | 0.137048 (-1.4%) **IN** | 0.137006 (-1.4%) **IN** | 0.136884 (-1.5%) **IN** | 0.136811 (-1.6%) **IN** | 0.135967 (-2.2%) **IN** |
| `pi_V` | 0.241446 (-9.2%) **IN** | 0.240691 (-9.5%) **IN** | 0.253001 (-4.9%) **IN** | 0.253516 (-4.7%) **IN** | 0.253758 (-4.6%) **IN** |
| `cbar` | 0.002262 (-46.2%) | 0.002258 (-46.2%) | 0.004923 (+17.2%) | 0.004091 (-2.6%) **IN** | 0.004870 (+15.9%) |
| `w_bot` | 0.018680 (-25.3%) | 0.018394 (-26.4%) | 0.016676 (-33.3%) | 0.017450 (-30.2%) | 0.018521 (-25.9%) |
| `h_1` | 0.057570 (+1342.9%) | 0.056807 (+1323.7%) | 0.055082 (+1280.5%) | 0.057744 (+1347.2%) | 0.050412 (+1163.5%) |
| `gamma` | 0.121518 (-54.7%) | 0.121500 (-54.7%) | 0.121047 (-54.8%) | 0.120845 (-54.9%) | 0.121832 (-54.5%) |
| `emp_homeless` | 0.983783 obs 0.46 | 0.983773 obs 0.46 | 0.984267 obs 0.46 | 0.983016 obs 0.46 | 0.983392 obs 0.46 |

Unlike line 3 of `ROUND1_FULL.md`, **`emp_homeless` is a real measurement on all
three lines here**: `h_1` runs 0.050 to 0.058, so the share is taken over five
per cent of the population rather than 1.6e-04 of it. It reads about 0.983
against 0.46 observed on every line, which is the same failure the combined point
has and this batch does not touch it.

## The count, per line

### Line 1, `aa6590231d`: **six of nine inside ten per cent**

Inside: `aleph`, `omega_l`, `sigma_y`, `tau_l`, `pi_eu`, `pi_V`.
Outside, with gap and direction:

| moment | model | gap | direction |
|---|---|---|---|
| `beta` | 2.351825 | -21.6% vs the 3.0 floor | **UNDER** the band |
| `cbar` | 0.004923 | +17.2% | **OVER** target |
| `w_bot` | 0.016676 | -33.3% | **UNDER** target |

**`cbar` CROSSED.** It was -46.2% under target at the combined point and is
+17.2% over it here. `max_food_cost` 0.0080 -> 0.0150 overshot: the sign of the
gap has flipped and the moment is outside on the other side. That is a miss, not
a near miss, and it is the second time `cbar` has crossed.

### Line 2, `990da2a08d`: **seven of nine inside ten per cent**

Inside: `aleph`, `omega_l`, `sigma_y`, `tau_l`, `pi_eu`, `pi_V`, `cbar`.
Outside, with gap and direction:

| moment | model | gap | direction |
|---|---|---|---|
| `beta` | 2.372005 | -20.9% vs the 3.0 floor | **UNDER** the band |
| `w_bot` | 0.017450 | -30.2% | **UNDER** target |

**`aleph` CROSSED.** It was +22.0% over target at the combined point and is -7.5%
under it here. It is inside ten per cent, so the crossing costs nothing on the
count, but it is a crossing and `value_of_life` 54.0 -> 42.0 is past the value
that would centre it rather than short of it.

`cbar` did **not** cross on this line: -46.2% at the combined point and -2.6%
here, both under target. It is the closest `cbar` has come.

### Line 3, `39ef9467b2`: **six of nine inside ten per cent**

Inside: `aleph`, `omega_l`, `sigma_y`, `tau_l`, `pi_eu`, `pi_V`.
Outside, with gap and direction:

| moment | model | gap | direction |
|---|---|---|---|
| `beta` | 2.363149 | -21.2% vs the 3.0 floor | **UNDER** the band |
| `cbar` | 0.004870 | +15.9% | **OVER** target |
| `w_bot` | 0.018521 | -25.9% | **UNDER** target |

**`cbar` CROSSED**, the same crossing as line 1 and for the same reason: line 3
carries `max_food_cost=0.0150`.

## Does the batch improve on five of nine? Yes -- and one thing got worse

**Every line improves on the combined point's five of nine.** Line 1 is six, line
2 is seven, line 3 is six. The gain is not sideways and it is not a re-labelling:
`aleph` moves from +22.0 per cent to inside on all three lines, `cbar` moves from
-46.2 per cent to inside on line 2, and `pi_V` moves from -9.2 per cent, on the
edge, to about -4.7 per cent on all three. `pi_eu` stayed landed with its
instrument untouched, as instructed.

**`w_bot` is worse than the combined point on all three lines**, and this is the
honest cost of the batch:

| point | `w_bot` | gap |
|---|---|---|
| combined `de2d34cf9e` | 0.018680 | -25.3% |
| line 1 | 0.016676 | **-33.3%** |
| line 2 | 0.017450 | **-30.2%** |
| line 3 | 0.018521 | **-25.9%** |

It never crosses -- it is under target everywhere -- and no line brings it within
even twenty per cent. Line 3 is the least bad and is still 0.6 points worse than
the combined point. Lowering `value_of_life` from 54.0 to 45.0 to fix `aleph`
takes `w_bot` down with it, which is the same non-orthogonality `ROUND1_FULL.md`
recorded in the other direction: `w_bot` and `aleph` both ride
`value_of_life`, and closing one on it opens the other.

**`beta` did not move at all.** All three lines sit between -20.9 and -21.6 per
cent below the 3.0 floor, against the combined point's -21.3 per cent, and all
three are *worse* than `point_9b39dfd463`'s -19.6 per cent at the same
`discount_factor=0.99950`. Raising `discount_factor_impatient` from 0.55 to 0.62
and 0.68 bought `beta` nothing. No instrument value is projected for it here.

## The one clean single-coordinate pair in this batch

Lines 1 and 3 differ in **exactly one** of the forty-three coordinates,
`discount_factor_impatient` 0.62 -> 0.68. That makes them a matched pair
isolating the impatient discount factor on this economy:

| moment | 0.62 | 0.68 | delta |
|---|---|---|---|
| `w_bot` | 0.016676 | 0.018521 | **+0.001845** |
| `h_1` | 0.055082 | 0.050412 | -0.004671 |
| `aleph` | 82.285865 | 82.566850 | +0.280985 |
| `beta` | 2.351825 | 2.363149 | +0.011324 |
| `pi_V` | 0.253001 | 0.253758 | +0.000757 |
| `pi_eu` | 0.136884 | 0.135967 | -0.000917 |
| `gamma` | 0.121047 | 0.121832 | +0.000785 |
| `tau_l` | 0.225532 | 0.226059 | +0.000527 |
| `cbar` | 0.004923 | 0.004870 | -0.000054 |
| `omega_l` | 0.363441 | 0.363314 | -0.000128 |
| `sigma_y` | 0.169050 | 0.169050 | 0.000000 |

`discount_factor_impatient` moves `w_bot` in the right direction and moves almost
nothing else: 0.06 of the instrument buys 0.001845 of `w_bot` and leaves `aleph`,
`cbar`, `pi_V` and `pi_eu` inside where they already were. It is the closest
thing to an orthogonal instrument this branch has measured on round 1.

**No value is projected from it.** The remaining `w_bot` gap at line 3 is
0.006479, three and a half times the step just measured, and
`IMPATIENCE_LADDER.md` reads `w_bot` = 0.04178 at 0.70 and 0.07383 at 0.95 on a
different anchor -- an order of magnitude steeper than the slope here. The two
readings cannot both be a local slope, so the local one is reported and not
extended.

## Against the previous best on this economy

`ROUND1_FULL.md` names `point_846f6a0a53` as the best round-1 point on
`b8dc1077ad`, a genuine six of nine. Line 2 beats it on the count, and the two
fail in different places:

| moment | `846f6a0a53` | line 2 `990da2a08d` |
|---|---|---|
| `aleph` | 81.841737 (+2.3%) **IN** | 74.001083 (-7.5%) **IN** |
| `beta` | 2.800366 (-6.7% vs floor) | 2.372005 (-20.9% vs floor) |
| `omega_l` | 0.367601 (-8.1%) **IN** | 0.363737 (-9.1%) **IN** |
| `sigma_y` | 0.169050 (-1.7%) **IN** | 0.169050 (-1.7%) **IN** |
| `tau_l` | 0.234964 (+4.9%) **IN** | 0.225810 (+0.8%) **IN** |
| `pi_eu` | 0.264014 (+89.9%) | 0.136811 (-1.6%) **IN** |
| `pi_V` | 0.279442 (+5.1%) **IN** | 0.253516 (-4.7%) **IN** |
| `cbar` | 0.004839 (+15.2%) | 0.004091 (-2.6%) **IN** |
| `w_bot` | 0.023247 (-7.0%) **IN** | 0.017450 (-30.2%) |
| | **six of nine** | **seven of nine** |

Line 2 buys `pi_eu` and `cbar` and gives up `w_bot`; it is also much further
below the `beta` floor, -20.9 per cent against -6.7 per cent. **Seven of nine is
the best count measured on this economy**, but `846f6a0a53` remains the only
point in this family that holds `w_bot` inside ten per cent, and it does so at
`probability_becoming_unemployed=0.0437` with `pi_eu` 90 per cent out.

## What this batch establishes

1. All three lines are on one economy, `b8dc1077ad`, with full handover and 16 of
   16 invariants passing. The comparisons are sound.
2. **The batch helps.** Six, seven and six of nine against the combined point's
   five. Line 2, `990da2a08d`, is **seven of nine** and is the best round-1 count
   measured on this economy.
3. `aleph` is closed on all three lines and is **bracketed**: 82.29 at
   `value_of_life=45.0` and 74.00 at 42.0 straddle the target of 80.0. The
   bracket is over the line-1/line-2 pair rather than over `value_of_life` alone,
   because those two lines differ in `max_food_cost` as well.
4. `cbar` is bracketed too and **crossed on two of the three lines**: +17.2 per
   cent at `max_food_cost=0.0150`, -2.6 per cent at 0.0130. The step to 0.0150
   was too large; 0.0130 lands it.
5. **`w_bot` is outside on every line and worse than the combined point on every
   line**, -25.9 to -33.3 per cent, always under target. It is the moment this
   batch pays for the others with.
6. `beta` is untouched: -20.9 to -21.6 per cent below the floor everywhere, no
   better than the combined point and worse than `point_9b39dfd463` at the same
   `discount_factor`. `discount_factor_impatient` at 0.62 and 0.68 does not
   reach it.
7. Lines 1 and 3 are a **one-coordinate pair** isolating
   `discount_factor_impatient`. It moves `w_bot` +0.001845 for +0.06 and moves
   essentially nothing else -- the least entangled instrument round 1 has. Its
   slope here is far shallower than `IMPATIENCE_LADDER.md`'s, so nothing is
   projected from it.
8. `h_1` (+1164 to +1347 per cent), `gamma` (about -55 per cent) and
   `emp_homeless` (about 0.983 against 0.46) are unchanged by this batch and
   remain where the combined point left them. `emp_homeless` here is a genuine
   measurement, taken over five per cent of the population.

**The step sizes in this batch were read off a single combined point and were
described as probes. They behaved like probes**: two of the four carried their
moment across its target -- `max_food_cost` at 0.0150 put `cbar` +17.2 per cent
over and outside, and `value_of_life` at 42.0 put `aleph` -7.5 per cent under,
crossing but staying inside -- and both moments are now bracketed, which is the
useful thing a probe does. `probability_of_voucher_benchmark_used` at 0.052
neither overshot nor undershot: it moved `pi_V` off the edge and left it there on
all three lines. `discount_factor_impatient` undershot at both 0.62 and 0.68,
leaving `w_bot` further out than it started.
