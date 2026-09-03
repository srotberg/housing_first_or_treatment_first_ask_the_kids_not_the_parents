# batch_kkk.txt — the productivity process, measured four ways

Every line carries `ssi_floor_takeup=0.5` and differs from the others in the
productivity process alone, so the four are a matched bracket.

**Why 0.5 and not the committed default of 0.** At 0 there is no SSI floor at
all, 6.6 per cent of the population is priced out of the cheapest rental in
retirement, and the model's own comment names that as the direct cause of
retirement-age homelessness at 3.75 times the observed rate. Measuring a
productivity process against a benchmark broken in a way I already know about
wastes four solves. Real SSI has a $2,000 asset test and take-up among eligible
elderly of roughly half, so 0.5 is the defensible middle. It is the SAME in all
four lines, so nothing in the process comparison turns on it — and it finally
runs the bracket that was owed after every PIA point was run with the dial at 0.

**Why every KKK line uses `kkk_s_deviation_bottom=3.35`.** The declared default
of 3 is a grid width, not a calibrated choice: it puts 0.621 per cent of
households on the bottom node. 3.35 puts 0.198 per cent there, which is the
design target from the homelessness bands and exactly what `y_grid_kappa=3.2`
delivers on the quantile grid. So the control and all three KKK arms carry the
same bottom-node mass and the arms differ only in dispersion and persistence.

| line | process | sigma_fixed | sigma_shock | rho_shock | pooled sd of log y | var rise, 26 -> 65 |
|---|---|---|---|---|---|---|
| 1 | quantile grid (control) | — | — | — | 0.953 (frozen) | 0 |
| 2 | KKK, the author's own numbers | 0.309 | 0.200 | 0.90 | 0.446 | +0.043 |
| 3 | KKK, dispersion scaled to sigma_y | 0.68273 | 0.44190 | 0.90 | 1.000 | +0.211 |
| 4 | KKK, dispersion scaled, data fan | 0.59620 | 0.32801 | 0.952 | 1.000 | +0.555 |

## What each line answers

**1 vs 2** — what the author's process does to the model, at his own numbers.
Line 2 will have a bottom-half earnings share near 33 per cent against a target
of 17.2, so it is expected to fail `sigma_y` badly; the question is what it does
to the homelessness bands, which is the reason for adding risk at all.

**2 vs 3** — whether the dispersion miss is the whole story. Scaling both
innovation sds by 2.209 hits the SCF bottom-half share while leaving the shape
of the age profile untouched.

**3 vs 4** — whether the FAN is what matters. Both hit `sigma_y`; they differ
only in how the dispersion is distributed over the life cycle. Line 3 keeps the
author's `rho_shock=0.9` and the within-cohort variance rises by 0.211 over
forty years. Line 4 uses 0.952, which is Storesletten, Telmer and Yaron's
persistence, and the rise is 0.555 — in the region the earnings literature
finds.

The bands the four are being read on: model homelessness by age band against the
data was 1.54x, 0.05x, 0.02x, 0.03x, 3.75x. Bands 2 to 4 carry 0.00030 against
0.00879 observed, a factor of 29, and that hole in the middle of the age
distribution is what a fanning-out process is supposed to fill.

## Read off each point file

`emp_homeless`, `income_of_homeless`, homelessness by age band (all five),
`sigma_y` (the bottom-half earnings share), overall homelessness, `w_bot`, and
the DIAG line for `smallest_house_size*rent(1)/net_income_lowest`.
