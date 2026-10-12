# batch_kkk0.txt — the four arms again, at ssi_floor_takeup = 0

On the author's instruction: *"Rerun the four arms with ssi_floor_takeup=0"*.

This REPLACES `batch_kkk.txt`, which carried `ssi_floor_takeup=0.5` in every
line. That value was added by the coordinator rather than asked for, it has
never been solved in this model, and it is the leading suspect for why none of
the four arms finished: all 22 seven-node points in the archive ran at 0 or
absent and took 2 to 4 minutes, while the arms at 0.5 were still going at 13,
30 and 32. Every worker on `batch_kkk.txt` has been archived.

`ssi_floor_takeup` is now at its committed default of 0.0 in all four lines, so
these points are directly comparable both to each other AND to the whole
archive.

| line | process | sigma_fixed | sigma_shock | rho_shock | pooled sd of log y | var rise, 26 → 65 |
|---|---|---|---|---|---|---|
| 1 | quantile grid (control) | — | — | — | 0.953, frozen | 0 |
| 2 | KKK, the author's own numbers | 0.309 | 0.200 | 0.90 | 0.446 | +0.043 |
| 3 | KKK, dispersion scaled to sigma_y | 0.68273 | 0.44190 | 0.90 | 1.000 | +0.211 |
| 4 | KKK, dispersion scaled, data fan | 0.59620 | 0.32801 | 0.952 | 1.000 | +0.555 |

Line 1 is the committed defaults with no argument at all, which is also line 1
of `batch_ssi_ab.txt`; the same vector run twice in different containers is
harmless and gives a second reading on the solve time.

Every KKK line carries `kkk_s_deviation_bottom=3.35`, which puts 0.2395 per
cent of households on the bottom node against the 0.198 that `y_grid_kappa=3.2`
delivers on the quantile grid. The same in all three, so nothing in the
comparison between them turns on it.

## What each pair answers

**1 vs 2** — what the author's process does at his own numbers. Expected to
fail `sigma_y` badly: the bottom half share should come back near 33 per cent
against 17.2, because the poorest household earns 0.232 of mean productivity
and can pay the cheapest rent out of income. The question is what it does to
the homelessness bands.

**2 vs 3** — whether the dispersion miss is the whole story. Both innovation
sds scaled by 2.20949, which leaves the shape of the age profile untouched.

**3 vs 4** — whether the FAN is what matters. Both hit the same cross sectional
dispersion and differ only in how it is spread over the life cycle.

## The band the arms are read against

Model homelessness by age band against the data, at the current base:

| band | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| model | 0.00036 | 0.00008 | 0.00003 | 0.00001 | 0.03122 |
| data | 0.00316 | 0.00338 | 0.00291 | 0.00250 | 0.00077 |

Bands 2 to 4 carry 0.00030 against 0.00879 observed, a factor of 29. That hole
in the middle of the age distribution is what a fanning-out process is supposed
to fill. Band 5 is 40 times too high and is a SEPARATE problem, owned by the
SSI floor — which is exactly the dial that has been taken back out of these
four lines, so expect band 5 to stay bad here and do not read it as a failure
of the process.
