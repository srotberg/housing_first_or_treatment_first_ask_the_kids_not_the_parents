# Stylized model (Section 3) recalibrated under log utility (sigma = 1)

**Status: step 1 (calibration) done; the tests are still running and will be added below.**

Model: `code/stylized/gradient.py`, unmodified, with `FIXED['sigma'] = 1.0`. Scripts are in
`code/stylized/referee_item7/log_utility/`. Outputs are in `results/referee_item7/log_utility/`.
Every formula gradient.py uses in the calibration is already valid at sigma = 1: U switches to log, and the
marginal utilities are X^(1-sigma)/c. The one exception is `y_zero`, which divides by (sigma - 1). Its log
limit, exp(-aleph), is in `common.py`.

## 1. Calibration

All five parameters are fitted jointly with `gradient.calibrate` (least squares on aleph, theta, kappa and
cbar, with b solved inside on participation). The targets are the benchmark's. The fit was run from eight
starting points (`calibrate_log.py`; one file per start, `start_*.json`).

| Parameter | sigma = 2 (benchmark) | sigma = 1 (log) |
|---|---|---|
| aleph | 8.64 | 3.69 |
| b | 0.032 | 0.0030 |
| theta | 0.22 | 0.17 |
| kappa | 3.56 | 11.95 |
| cbar | 0.098 | 0.10 |

| Moment | Target | sigma = 2 | log |
|---|---|---|---|
| VSL / income | 80 | 80.0 | 80.0 |
| Participation | 8.90 % | 8.90 % | 8.90 % |
| Drug spending share | 16.0 % | 16.0 % | 16.0 % |
| Users' income / mean | 0.74 | 0.74 | 0.74 |
| Food assistance share | 0.42 % | 0.42 % | 0.42 % |

All five targets are hit, to a maximum relative error of 1e-12. Two of the eight starts converged to this
point.

**The fit hits 0.74 in a way that differs from the benchmark.** Under log, users form **two bands**:

- the bottom 8.44 % (y from 0.24 to 0.296, mean 0.27);
- the top 0.46 % (y above 6.68, percentiles 99.54 to 100, mean 9.33).

Their average income is 0.74. In the sigma = 2 benchmark, users are one band at percentiles 50 to 59.
Under log, therefore, the users' income target is met by a mix of the poorest and the richest households,
not by middle-income users.

The other six starts:

- Four ended with every user in the bottom band. All targets were hit except users' income, at 0.27, which is
  64 % short. kappa ran off to between 33 and 75.
- One ended in a single middle band (percentiles about 50 to 59) at kappa 20.4, with users' income 0.737. It
  missed the VSL (86.6) and the spending share (20.1 %), so it is not a solution. Whether a single-band
  solution exists is being checked next.
- One stopped near the two-band solution without converging.
