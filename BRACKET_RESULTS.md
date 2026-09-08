# Child ratio brackets: what the penalties would have to be

Measured on branch `claude/two-period-addiction-hazard-d7gb61`, model hash
`54498e8679`, four cores. Each point is a benchmark solve at the vector on the
`VECTOR` line of `code/benchmark_of_record.txt` with ONE penalty substituted and
everything else, including the other penalty, held at its calibrated value. Both
ratios are untargeted moments of the benchmark's own moments block, so no
counterfactual was run.

**Neither target lies inside its measured range.** Both sweeps are reported
without an interpolated penalty, because there are no two points to interpolate
between. That is the finding, not a gap in the measurement.

## Sweep A -- child SUD odds ratio, `penalty_child_addicted`, target 2.00

| penalty | ratio | point |
|---------|-----------|--------------|
| 0.24 | 1.0944870 | `6876263050` |
| 0.45 | 1.1953997 | `6ea2e2f284` |
| 0.65 | 1.3123311 | `15be0b98de` |
| 0.85 | 1.3123545 | `4cbe708367` |

Rising, as expected. **The target of 2.00 lies OFF THE TOP of the measured
range** -- above the highest point by 0.6876, more than three times the total
0.2179 the ratio moves across the whole sweep. No interpolated penalty is
reported.

Extrapolating would be worse here than the usual objection to it, because the
curve is not merely short of the target but FLAT at the top. The interval slopes
in ratio per unit of penalty are:

| interval | slope |
|--------------|----------|
| [0.24, 0.45] | 0.480537 |
| [0.45, 0.65] | 0.584657 |
| [0.65, 0.85] | 0.000117 |

The last interval moves the ratio by 2.3e-05 across a penalty change of 0.20 --
a shelf, five thousand times flatter than the interval below it. A linear
extrapolation off the top two points would divide by that and return a penalty
of roughly 5900. This is the seven-node productivity grid described in the header
of `code/child_penalty_bracket.sh`: between node crossings a shift moves no mass
and the ratio does not respond. Where the next step is remains unmeasured, and
nothing in this sweep bounds it.

Near-identical output at 0.65 and 0.85 is also what a failed parameter
substitution looks like, so it was checked rather than assumed: the two points
carry distinct tags, their `VECTOR` lines differ in `penalty_child_addicted` and
in nothing else, and unrelated moments do move between them (`sigma_y` differs in
the sixth decimal). The plateau is the model's, not the harness's.

**Distance from the external estimate.** Nilsson (2017) is 0.24. The measurement
says the model needs MORE than 0.85 to reach the data, so the distance is greater
than 0.61 -- a lower bound only, and given the shelf the true distance is not
bounded above by anything measured here. At Nilsson's own 0.24 the model returns
1.0945 against a data target of 2.00, undershooting by 45.3 per cent.

## Sweep B -- child homelessness odds ratio, `penalty_child_homeless`, target 2.10

| penalty | ratio | point |
|---------|-----------|--------------|
| 0.31 | 3.4477162 | `6876263050` |
| 0.22 | 2.8412781 | `104ae478fe` |
| 0.14 | 2.4286512 | `055326f8ff` |
| 0.07 | 2.1396442 | `e733e86ef3` |

Falling as the penalty falls, as expected. **The target of 2.10 lies OFF THE
BOTTOM of the measured range** -- below the lowest point by 0.0396. No
interpolated penalty is reported.

This one misses narrowly. The sweep very nearly brackets the target and stops
just short of it: the bottom arm at 0.07 is within 1.9 per cent of 2.10 in ratio
terms. One further point below 0.07 would almost certainly close it, and that is
the cheapest way to turn this sweep into an interpolation. Interval slopes:

| interval | slope |
|--------------|----------|
| [0.22, 0.31] | 6.738200 |
| [0.14, 0.22] | 5.157837 |
| [0.07, 0.14] | 4.128671 |

The slope is easing as the penalty falls but is still steep, roughly nine times
sweep A's steepest interval at the bottom and far from any shelf. An extrapolated
crossing would land a little under 0.07; it is deliberately not quoted as a
result, because it is off the end of what was measured.

**Distance from the external estimate.** Chetty, Hendren and Katz (2016) is 0.31.
The measurement says the model needs LESS than 0.07, so the distance is greater
than 0.24 and the penalty is smaller than the external estimate by a factor of
more than 4.4. At their own 0.31 the model returns 3.4477 against a data target
of 2.10, overshooting by 64.2 per cent.

## What the two sweeps say together

The two ratios miss in opposite directions and by very different amounts, which
is a statement about the model rather than about either penalty, since both are
externally set and neither is free.

Sweep A cannot reach its target within a plausible range of the penalty at all;
sweep B overshoots so hard at the external value that it needs a penalty of under
a quarter of Chetty, Hendren and Katz's to come down to the data. Same channel,
same contraction of the newborn draw against the rate at each node -- so the
asymmetry is the model's mapping from a parent's penalty to a child's outcome
being far steeper in homelessness than in disorder, by roughly an order of
magnitude in slope at the calibrated points.

Both anchors quoted in the header of `code/child_penalty_bracket.sh` reproduced
on the current economy: 1.0945 at 0.24 and 3.4477 at 0.31. The stored 0.24 point
had been retired as measured on a superseded economy and was re-solved here; the
change that retired it did not move either child moment.

## Caveats

The two penalties are not independent -- a parent can be both disordered and
homeless -- and each sweep holds the other penalty at its calibrated value. The
cross term is unmeasured and is worth checking before either number is used.

`6876263050` appears in both tables. This is correct and not a duplicate: at
`penalty_child_addicted=0.24` and `penalty_child_homeless=0.31` both
substitutions return the benchmark vector itself, so it is one economy, solved
once and reported for both moments. Seven distinct points were solved for eight
table rows.

## Reproducing

    bash code/run_one_point.sh <benchmark vector, one penalty substituted>

then read `delta_d child SUD ratio` or `delta_h child homelessness ratio` from
`code/points/point_<tag>.txt`. Identify the point by the tag `run_one_point.sh`
reports, not by the newest file in `code/points/`: the script skips a vector that
is already measured on the current economy, and on such a skip the newest file by
modification time belongs to some other point. The 0.31 arm above was served from
cache in exactly that way.
