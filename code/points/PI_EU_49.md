# `pi_eu` against a 4.9 per cent target: three arms, and the target is bracketed

`code/batch_pi_eu_49.txt`, run line by line from the repository root, each line
issued on its own and allowed to finish before the next was started. Each line
moves ONE coordinate, `probability_becoming_unemployed`, off the round-1 vector
and leaves the other forty-two alone. `include_unsecured_borrowing=0` in all
three. Nothing under `code/` was edited;
`code/housing_first_or_treatment_first_SR_v1.f90` was not touched.

| | instrument | tag | MODEL | outcome |
|---|---|---|---|---|
| line 1 | **0.0050** | `3eb0c715e4` | `e550ca2c82` | solved, 15 min |
| line 2 | **0.0030** | `e3bba3efac` | `e550ca2c82` | solved, 11 min |
| line 3 | **0.0015** | `c9369f375d` | `e550ca2c82` | solved, 12 min |

## The three MODEL lines agree, and that was checked rather than assumed

**All three lines carry `MODEL e550ca2c82`.** That is the md5 of the working
tree's `housing_first_or_treatment_first_SR_v1.f90`, which is the head this
batch was synced to (`de9d7a3`, "unemployment target 13.9 -> 4.9 per cent").
All three report `HANDOVER OK: 43 of 43 parameters applied` and
`INVARIANTS: all PASS`, 16 of 16, no failures anywhere. No build failed and no
run segfaulted.

The three `VECTOR` lines were compared to each other coordinate by coordinate,
all forty-three:

    line 2 vs line 1:  probability_becoming_unemployed  0.0050 -> 0.0030   (only diff)
    line 3 vs line 1:  probability_becoming_unemployed  0.0050 -> 0.0015   (only diff)

So the three arms are a genuine matched triple on one economy, and every
comparison among them is a within-economy comparison.

## Which rows are on this economy and which are not

This matters more than usual here, because the nearest reference points were
measured on **older builds of the model**, and the `MODEL` hash is the md5 of
the Fortran source.

| row | instrument | tag | MODEL | same build as my arms? | same vector? |
|---|---|---|---|---|---|
| **line 1** | **0.0050** | `3eb0c715e4` | `e550ca2c82` | **yes** | **yes** |
| **line 2** | **0.0030** | `e3bba3efac` | `e550ca2c82` | **yes** | **yes** |
| **line 3** | **0.0015** | `c9369f375d` | `e550ca2c82` | **yes** | **yes** |
| round-1 anchor | 0.0122 | `35e8286c4e` | `bb2cd48b81` | **no** | yes, on the 42 shared coordinates |
| earlier arm | 0.0250 | `551e56afd4` | `b8dc1077ad` | **no** | yes, on the 42 shared coordinates |
| PI_EU_LOW anchor | 0.0437 | `f9c16d5308` | `b8dc1077ad` | **no** | **no, 5 coordinates differ** |
| PI_EU_LOW | 0.0300 | `a6ae2d65f0` | `b8dc1077ad` | **no** | **no, 5 coordinates differ** |
| PI_EU_LOW | 0.0150 | `0452c117ed` | `b8dc1077ad` | **no** | **no, 5 coordinates differ** |
| PI_EU_LOW | 0.0080 | `8f1afa07a7` | `b8dc1077ad` | **no** | **no, 5 coordinates differ** |

The four `PI_EU_LOW.md` rows -- the ladder quoted in the brief that commissioned
this run, 0.0437 -> 0.264 through 0.0080 -> 0.110 -- are a **different economy in
both senses**. Besides the instrument they differ in five substantive coordinates, plus one the
older script did not hand over at all:

    discount_factor                        0.99980  vs  0.99715
    discount_factor_impatient              0.75     vs  0.55
    max_food_cost                          0.0130   vs  0.0136
    probability_of_voucher_benchmark_used  0.052000 vs  0.024723
    value_of_life                          42.0     vs  38.4
    financial_grid_expander_negative       2.0      vs  (did not exist)

Two of those, the two discount factors, are exactly the parameters that set
buffer-stock saving, which is the channel this whole batch is about. **No curve
is fitted across those rows and mine, and none should be.**

The 0.0122 and 0.0250 rows are closer: they share all forty-two substantive
coordinates with my arms, and differ only in the instrument and in
`financial_grid_expander_negative`, which the older `run_one_point.sh` did not
hand over at all. But they were built from a different source. Between
`bb2cd48b81` (the anchor) and `e550ca2c82` (mine) the model gained the
seven-point negative financial grid (`b03b86b`) and the target constant itself
moved from 0.139 to 0.049 (`de9d7a3`). The negative grid is gated off here --
`include_unsecured_borrowing=0` in every one of these runs, so the points below
zero are unreachable -- and the target constant does not enter any equilibrium
condition, so the two builds are **expected** to be equivalent on this vector.
That expectation was not tested: no arm on `e550ca2c82` shares an instrument
value with any arm on `bb2cd48b81`. The anchor row is therefore reported below
as a reference, marked as a different build, and it is not used as a bracketing
endpoint.

## The ladder

Target for `pi_eu` is **0.049**.

### On this economy (`MODEL e550ca2c82`), the three arms measured here

| instrument | `pi_eu` | gap vs 0.049 | **`pi_eu` / instrument** |
|---|---|---|---|
| 0.0050 | 0.08348 | +70.4% | **16.70** |
| 0.0030 | 0.06283 | +28.2% | **20.94** |
| **0.0015** | **0.04155** | **-15.2%** | **27.70** |

### Reference rows, NOT on this economy -- do not fit through these

| instrument | `pi_eu` | ratio | build | vector |
|---|---|---|---|---|
| 0.0437 | 0.26080 | 5.97 | `b8dc1077ad` | 5 coordinates differ |
| 0.0300 | 0.21830 | 7.28 | `b8dc1077ad` | 5 coordinates differ |
| 0.0250 | 0.19479 | 7.79 | `b8dc1077ad` | shares all 42 |
| 0.0150 | 0.15308 | 10.21 | `b8dc1077ad` | 5 coordinates differ |
| 0.0122 | 0.13426 | 11.01 | `bb2cd48b81` | shares all 42 |
| 0.0080 | 0.10972 | 13.72 | `b8dc1077ad` | 5 coordinates differ |

The ratio keeps rising, and it rises on this economy alone: 16.70 -> 20.94 ->
27.70 as the instrument falls from 0.0050 to 0.0015. It does not flatten and it
does not turn over the range measured here. The brief's reading -- that the
ratio rises as the flow falls, so the mapping is not linear -- holds within this
economy and did not need the other rows to establish it.

Within-economy secants, over the measured range only:

| pair | d`pi_eu` / d(instrument) |
|---|---|
| 0.0030 -> 0.0050 | 10.32 |
| 0.0015 -> 0.0030 | 14.19 |

The response is concave here too: the instrument bites harder the lower it goes.

## The bracket

**0.049 is bracketed, by instrument 0.0015 and 0.0030.** `pi_eu` = 0.04155 at
0.0015 and 0.06283 at 0.0030, and

    0.04155  <  0.049  <  0.06283

That is the only bracketing pair among the three arms measured here; the pair
(0.0030, 0.0050) sits entirely above the target. `pi_eu` is monotone increasing
in the instrument across all three arms, so this is a genuine bracket and a
secant inside it is an interpolation rather than an extrapolation.

Linear interpolation between the two bracketing arms puts the crossing at
**instrument ~= 0.00202**. The bracket is narrow -- a factor of two in the
instrument -- but it is also where the curvature is strongest, so 0.00202 is a
place to put the next arm, not a solved value.

**No value outside 0.0015 to 0.0050 is offered here.** In particular the arms
measured here say nothing about what the instrument would have to be on the
older builds, and nothing about instrument values below 0.0015.

## The nine round-1 moments at each point

Gaps are per cent of target. `beta` is scored against the **band 2.5-4.5**: the
gap shown is the distance to the nearer band edge, which is 2.5 at every point
here, and "inside ten per cent" means within ten per cent of that edge.

| moment | target | 0.0122 (**other build**) | 0.0050 | 0.0030 | 0.0015 |
|---|---|---|---|---|---|
| `aleph` | 80.0 | 76.068 (-4.9%) | 84.849 (+6.1%) | 88.764 (+10.9%) | 93.177 (+16.5%) |
| `beta` | band 2.5-4.5 | 2.4532 (-1.9%) | **2.2247 (-11.0%)** | **2.1378 (-14.5%)** | **2.0427 (-18.3%)** |
| `omega_l` | 0.40 | 0.36351 (-9.1%) | 0.36244 (-9.4%) | 0.36216 (-9.5%) | 0.36181 (-9.6%) |
| `sigma_y` | 0.172 | 0.16905 (-1.7%) | 0.16905 (-1.7%) | 0.16905 (-1.7%) | 0.16905 (-1.7%) |
| `tau_l` | 0.224 | 0.22574 (+0.8%) | 0.22347 (-0.2%) | 0.22283 (-0.5%) | 0.22205 (-0.9%) |
| `pi_eu` | 0.049 | 0.13426 (+174.0%) | 0.08348 (+70.4%) | 0.06283 (+28.2%) | **0.04155 (-15.2%)** |
| `pi_V` | 0.266 | 0.25561 (-3.9%) | 0.24257 (-8.8%) | 0.23737 (-10.8%) | 0.23129 (-13.1%) |
| `cbar` | 0.0042 | 0.0039343 (-6.3%) | 0.0024962 (-40.6%) | 0.0019566 (-53.4%) | 0.0014370 (-65.8%) |
| `w_bot` | 0.0250 | 0.024727 (-1.1%) | **0.018940 (-24.2%)** | **0.017129 (-31.5%)** | **0.013311 (-46.8%)** |
| **inside ten per cent** | | **8 of 9** | **5 of 9** | **3 of 9** | **3 of 9** |

Which ones are inside ten per cent, line by line:

- **0.0122 (other build), 8 of 9**: `aleph`, `beta`, `omega_l`, `sigma_y`,
  `tau_l`, `pi_V`, `cbar`, `w_bot`. Only `pi_eu` is out, and it is out by
  +174% against the new target.
- **0.0050, 5 of 9**: `aleph`, `omega_l`, `sigma_y`, `tau_l`, `pi_V`.
  Out: `beta`, `pi_eu`, `cbar`, `w_bot`.
- **0.0030, 3 of 9**: `omega_l`, `sigma_y`, `tau_l`.
  Out: `aleph`, `beta`, `pi_eu`, `pi_V`, `cbar`, `w_bot`.
- **0.0015, 3 of 9**: `omega_l`, `sigma_y`, `tau_l`.
  Out: `aleph`, `beta`, `pi_eu`, `pi_V`, `cbar`, `w_bot`.

The count falls from 8 to 3 as the instrument falls, and it is already 3 at the
arm that brackets the target from below.

## How far `beta` and `w_bot` fall: the price of the new target

Both were inside ten per cent before this target moved -- `beta` 1.9 per cent
below the band floor, `w_bot` 1.1 per cent below its target -- and both fall
monotonically as the flow falls, through precautionary saving: less unemployment
risk, less buffer-stock saving, less wealth, and less of it at the bottom.

### `beta`, wealth over output, band 2.5-4.5

| instrument | `beta` | fall from the 0.0122 row (level) | fall from the 0.0122 row (per cent) | gap to the band floor 2.5 |
|---|---|---|---|---|
| 0.0122 (**other build**) | 2.45317 | -- | -- | -1.87% |
| 0.0050 | **2.22465** | **-0.2285** | **-9.32%** | **-11.01%** |
| 0.0030 | **2.13783** | **-0.3154** | **-12.85%** | **-14.49%** |
| 0.0015 | **2.04270** | **-0.4105** | **-16.73%** | **-18.29%** |

`beta` leaves the band immediately. It is already 11.0 per cent below the floor
at 0.0050, the highest arm measured, and 18.3 per cent below it at 0.0015. It
does not re-enter the band at any arm here, and it is monotone, so there is no
instrument value inside 0.0015-0.0050 at which it does.

### `w_bot`, net worth share of the bottom half, target 0.0250

| instrument | `w_bot` | fall from the 0.0122 row (level) | fall from the 0.0122 row (per cent) | gap to target |
|---|---|---|---|---|
| 0.0122 (**other build**) | 0.024727 | -- | -- | -1.09% |
| 0.0050 | **0.018940** | **-0.005786** | **-23.40%** | **-24.24%** |
| 0.0030 | **0.017129** | **-0.007598** | **-30.73%** | **-31.48%** |
| 0.0015 | **0.013311** | **-0.011416** | **-46.17%** | **-46.76%** |

`w_bot` is the more expensive of the two. It loses a quarter of its value at
0.0050 and nearly half at 0.0015: 0.0247 becomes 0.0133, a fall of 0.0114 in
level. At the arm that brackets the target from below it is 46.8 per cent short
of 0.025.

Comparisons in these two tables are against a row on a **different build**
(`bb2cd48b81`), which is why the level falls are stated alongside the gaps to
target: the gaps to target are properties of each arm on its own and do not
depend on the anchor at all. The gap-to-target columns tell the same story --
`beta` -11.0 -> -14.5 -> -18.3, `w_bot` -24.2 -> -31.5 -> -46.8 -- entirely
within this economy.

## What this batch establishes

1. `pi_eu` = 0.049 **is reachable on this economy**, and it is bracketed between
   instrument 0.0015 and 0.0030, near 0.00202 by linear interpolation inside the
   bracket.
2. The ratio `pi_eu` / instrument rises over all three arms, 16.70 -> 20.94 ->
   27.70, and the map is concave over the measured range. This is established
   within one economy, on three arms that differ in exactly one coordinate.
3. Reaching 4.9 per cent costs `beta` and `w_bot`, both of which were inside ten
   per cent before the target moved. At the bracketing arm 0.0015 `beta` is
   2.043 against a band floor of 2.5 (-18.3%) and `w_bot` is 0.0133 against
   0.0250 (-46.8%). `cbar` and `pi_V` also leave the ten per cent band, and
   `aleph` overshoots 80 from below and leaves it at 0.0030. Only `omega_l`,
   `sigma_y` and `tau_l` survive at every arm.
4. The count of moments inside ten per cent falls from 8 of 9 at the old
   instrument to 3 of 9 at the arm that brackets the new target.

Point 3 is the one that matters. `w_bot` was closed on an instrument that does
not own it, and `probability_becoming_unemployed` moves it harder than it moves
`pi_eu` in proportional terms over this range. It cannot stay closed while this
instrument is retuned; both it and `beta` have to be re-closed afterwards, on
whatever instruments are chosen to own them.

## One thing worth doing next, not done here

The batch was three lines and three lines were run. But there is **no arm on
`MODEL e550ca2c82` at instrument 0.0122**, so the claim that the anchor row
transfers across the build change is an argument from the source diff rather
than a measurement. Re-running the round-1 vector unchanged on the current head
would cost one solve and would either confirm the anchor row or reveal that the
seven-point negative grid is not as inert as `include_unsecured_borrowing=0`
suggests. Until that is run, every falls-from-anchor figure above should be read
alongside its gap-to-target twin, which does not depend on the anchor.
