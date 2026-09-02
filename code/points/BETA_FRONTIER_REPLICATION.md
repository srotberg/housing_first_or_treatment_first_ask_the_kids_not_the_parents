# The `beta` frontier, measured a second time: every conclusion holds, `w_bot` does not reproduce

`code/batch_beta_frontier.txt` was run twice, by two workers, concurrently and
independently, without either knowing of the other. Both runs used the same
three lines off `point_35e8286c4e`, the same `run_one_point.sh`, and the same
binary. The first run is the one recorded in `BETA_FRONTIER.md` and it owns the
canonical `point_*.txt` files. This note is the second run.

The duplicate was an accident of scheduling, not a designed experiment. It is
kept because a second cold measurement of three vectors is exactly the check
`DETERMINISM.md` performs, and this one does not come out the way that one did.

## What is stored here

The second run's point files are kept beside the first run's rather than over
them, following the `RUN1_`/`RUN2_` convention `DETERMINISM.md` established:

| line | canonical (first run) | this note (second run) |
|---|---|---|
| 1 | `point_a3456efb23.txt` | `REPLICATE_a3456efb23.txt` |
| 2 | `point_44e91bb1d7.txt` | `REPLICATE_44e91bb1d7.txt` |
| 3 | `point_551e56afd4.txt` | `REPLICATE_551e56afd4.txt` |

**Nothing in `BETA_FRONTIER.md` is amended and no canonical point file is
touched.** The first run's numbers remain the numbers of record.

## The two runs are the same experiment, and that was checked

For all three tags, the `VECTOR` line is byte-identical between the two runs,
across all forty-three coordinates, and both carry **`MODEL b8dc1077ad`** — the
same binary the base point `point_35e8286c4e` was measured on. Both runs report
`HANDOVER OK: 42 of 42 parameters applied` and `INVARIANTS: all PASS`, 16 of 16,
on every line. The second run's three lines solved in 16 minutes each.

So the two runs differ in nothing that is under the experiment's control. Any
disagreement below is the solver.

## Moment by moment

Relative spread is |second − first| / |first|. `DETERMINISM.md` set the
threshold at **1e-3** and measured a worst case of **5.13e-05** over 23 targeted
moments, median 8.80e-06. Readings above the threshold are marked.

### line 1, `discount_factor_impatient` 0.78 — `point_a3456efb23`

| moment | first run | replication | relative spread | verdict |
|---|---|---|---|---|
| `aleph` | 76.62137286 | 76.77017342 | 1.94e-03 **>1e-3** | both IN |
| `beta` | 2.46516799 | 2.46520754 | 1.60e-05 | both below the 3.0 floor |
| `omega_l` | 0.36321134 | 0.36321209 | 2.06e-06 | both IN |
| `sigma_y` | 0.16905002 | 0.16905002 | 0.00e+00 | both IN |
| `tau_l` | 0.22674517 | 0.22636376 | 1.68e-03 **>1e-3** | both IN |
| `pi_eu` | 0.13323980 | 0.13323691 | 2.16e-05 | both IN |
| `pi_V` | 0.25715950 | 0.25687592 | 1.10e-03 **>1e-3** | both IN |
| `cbar` | 0.00387939 | 0.00387943 | 1.02e-05 | both IN |
| `w_bot` | 0.02627010 | 0.02655800 | 1.10e-02 **>1e-3** | both IN |

### line 2, `discount_factor` 0.99995 — `point_44e91bb1d7`

| moment | first run | replication | relative spread | verdict |
|---|---|---|---|---|
| `aleph` | 76.34291222 | 76.13582208 | 2.71e-03 **>1e-3** | both IN |
| `beta` | 2.46948870 | 2.46920810 | 1.14e-04 | both below the 3.0 floor |
| `omega_l` | 0.36356389 | 0.36356478 | 2.43e-06 | both IN |
| `sigma_y` | 0.16905002 | 0.16905002 | 0.00e+00 | both IN |
| `tau_l` | 0.22568361 | 0.22615310 | 2.08e-03 **>1e-3** | both IN |
| `pi_eu` | 0.13426863 | 0.13427572 | 5.28e-05 | both IN |
| `pi_V` | 0.25560477 | 0.25601361 | 1.60e-03 **>1e-3** | both IN |
| `cbar` | 0.00393306 | 0.00393352 | 1.17e-04 | both IN |
| `w_bot` | 0.02477090 | 0.02437550 | 1.60e-02 **>1e-3** | both IN |

### line 3, `probability_becoming_unemployed` 0.0250 — `point_551e56afd4`

| moment | first run | replication | relative spread | verdict |
|---|---|---|---|---|
| `aleph` | 68.51581354 | 68.50388232 | 1.74e-04 | both OUT |
| `beta` | 2.72394157 | 2.72377383 | 6.16e-05 | both below the 3.0 floor |
| `omega_l` | 0.36536738 | 0.36536937 | 5.43e-06 | both IN |
| `sigma_y` | 0.16905002 | 0.16905002 | 0.00e+00 | both IN |
| `tau_l` | 0.22943305 | 0.22943702 | 1.73e-05 | both IN |
| `pi_eu` | 0.19479102 | 0.19481088 | 1.02e-04 | both OUT |
| `pi_V` | 0.27069087 | 0.27069058 | 1.09e-06 | both IN |
| `cbar` | 0.00579501 | 0.00579576 | 1.31e-04 | both OUT |
| `w_bot` | 0.02994875 | 0.02992972 | 6.36e-04 | both OUT |

## The headline: every conclusion in `BETA_FRONTIER.md` survives

**No moment changes its verdict on any line.** Twenty-seven paired readings,
zero flips of `IN` to `OUT` or the reverse, and `beta` is below the 3.0 floor on
all three lines in both runs. Specifically, and these are the three questions
the batch was built to answer:

1. **No line puts `beta` in the 3.0–4.5 band.** Second run: line 1 at 2.465208,
   line 2 at 2.469208, line 3 at 2.723774, short of the floor by 0.534792,
   0.530792 and 0.276226. The first run's figures are 2.465168, 2.469489 and
   2.723942. The two runs agree on `beta` to between 1.6e-05 and 1.1e-04 — it is
   among the best-reproducing moments in the set — and the answer is the same
   either way.
2. **Line 3's price is the same in both runs.** `beta` gains +0.270947 in the
   second run (+0.270 in the first), closing 49.5% of the 0.547174 shortfall;
   `pi_eu` goes from 0.134279 to 0.194811, **+6.05 percentage points**, carrying
   it from −3.40% inside to +40.15% outside. Both runs put `pi_eu` at +40.1%.
3. **The same three further moments break on line 3, in both runs**: `cbar` to
   +38.0%, `w_bot` to +19.7–19.8%, `aleph` to −14.4%. Lines 1 and 2 break
   nothing in either run.

The `w_bot` and `cbar` watch from `ROUND1_LAST2.md` also replicates. At
`discount_factor_impatient` 0.78 both runs put `w_bot` inside (+5.08% and
+6.23%) and `cbar` inside (−7.63% in both), so the +29.82% `w_bot` overshoot and
the −13.41% `cbar` break remain 0.85 phenomena and 0.78 is clear of them.

## The finding: `w_bot` is noisier than the calibration reads it

`w_bot` disagrees between the two runs by **1.10e-02 on line 1 and 1.60e-02 on
line 2** — 1.1 and 1.6 per cent. That is 210 and 310 times `DETERMINISM.md`'s
measured worst case of 5.13e-05, and 11 and 16 times its 1e-3 threshold.

Three other moments also cross the threshold, all on lines 1 and 2: `aleph`
(1.94e-03, 2.71e-03), `tau_l` (1.68e-03, 2.08e-03) and `pi_V` (1.10e-03,
1.60e-03). `beta`, `omega_l`, `sigma_y`, `pi_eu` and `cbar` reproduce to 1e-4 or
better everywhere.

Why this matters rather than being a curiosity: **the calibration scores `w_bot`
against a ten per cent band, and on line 2 the two runs read it as −0.92% and
−2.50%.** A moment whose own measurement moves 1.6 points of a 10-point budget
between identical runs cannot be ranked finely. `ROUND1_LAST2.md` separated its
two eight-of-nine candidates partly on `w_bot` −2.92% against −4.28%, a gap of
1.36 points — smaller than the noise measured here. That comparison should not
be treated as resolved.

`DETERMINISM.md` records a previous episode of exactly this shape: tag
`f9c16d5308` disagreed by 2.85 per cent on `w_bot`, it was traced to a bug
rather than to the solver, the bug was fixed, and three cold runs then agreed to
5.13e-05. **`w_bot` is the moment that broke before and it is the moment
breaking now**, at the same order of magnitude, on a later binary.

One pattern to hand to whoever picks this up, offered as an observation and not
a diagnosis: **the disagreement is confined to the two patience lines.** Line 3,
which moves `probability_becoming_unemployed` instead, reproduces to 6.36e-04
worst and is under the threshold on all nine moments. Lines 1 and 2 are the two
that move a discount factor. Whether that is the mechanism or a coincidence of
three observations is not something three lines can settle.

## What this note claims and what it does not

- It **confirms** `BETA_FRONTIER.md`: no line reaches the band, line 3's price is
  half of `beta`'s shortfall for `pi_eu`'s whole margin plus three more moments,
  and lines 1 and 2 cost nothing and buy almost nothing.
- It **does not** revise any number of record. Where the two runs differ, the
  first run's figure stands.
- It **flags** `w_bot` as reproducing an order of magnitude worse than the
  documented bound, and asks that comparisons resting on `w_bot` differences of
  a point or two be re-examined before they are relied on.
- It **projects nothing**. No instrument value that would put `beta` in the band
  is inferred here, from these three lines or from the earlier
  `discount_factor` readings.
