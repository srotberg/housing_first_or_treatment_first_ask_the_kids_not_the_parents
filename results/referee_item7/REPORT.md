# Referee item 7: verification against the code (stylized model, Section 3)

**Which model.** The paper's Section 3 numbers are not produced by `stylized.py` at
`calibrated_stage2.json`. Every Section 3 placeholder is a `g_*` name, written by
`code/stylized/gradient.py` at `code/stylized/gradient.json`. Its docstring says the staged model
(`stylized.py`, `stages.py`, `stage_results.py`) "is no longer read by the paper", apart from footnote 7's
"version of this model with housing". All results here use `gradient.py` / `gradient.json`, unmodified.
Loading it reproduces Table 2 exactly: participation 0.0890, users' income 0.740, spending share 0.160,
VSL 80.0, food-assistance share 0.0042. The parameters are aleph 8.640, b 0.0323, theta 0.222,
kappa 3.559, cbar 0.0977, sigma 2, y_min 0.24, sigma_y 0.946.

Method: 400,000 equal-mass income nodes of the model's truncated lognormal, using the model's own `plan()`
(closed-form use decision plus bisection on saving). Script: `code/stylized/referee_item7/ab_value_of_life_and_band.py`.
Output: `results/referee_item7/ab_output.txt`.

## A. Negative value of life: PARTLY TRUE (the number is right; the contradiction is not)

| Measure | Share negative |
|---|---|
| Period 1, lifetime value V1(y) | **0** (minimum 4.46, at y_min) |
| Period 1, flow U + aleph | **0** (minimum 2.63) |
| Period 2, W(a,y,d), the value of being alive at the start of old age, before the employment draw | **0** |
| Period 2, realised flow U + aleph after the employment draw | **2.47 %** of period-2 survivors |

- The whole 2.47 % is in one state: non-users (d = 0) who are **out of work** in period 2, with incomes
  from 0.240 to 0.676, which is the bottom half of the distribution (percentiles 0 to 50.1). Out of work,
  they consume a + cbar, which falls below y_zero = 0.167, the consumption at which U + aleph = 0. Their
  minimum is -4.44.
- Users never fall into this state, with or without a SUD: they save enough. Employed households never
  do either.
- **Footnote 8 is literally true.** No household has a negative value of life in period 1, whether
  measured as lifetime value or as flow. The code checks this at y_min at every Figure 1 point
  (the assertion in `gradient.scan`).
- **The referee's "about 2 %" is right in magnitude (2.47 %).** It holds only in period 2, and only for
  the realised out-of-work flow.
- **This does not contradict the footnote's claim that "death is never an optimal choice".** Survival is
  drawn before the employment draw, so the value that mortality destroys is W. W is positive in every
  period-2 state. The negative flow therefore enters no decision.
- Caveat: footnote 8 is stated for period 1 only. The paper does not say that the period-2 realised flow
  can be negative. The code comment records that the author decided period 2 need not be positive
  (8 October).

## B. Where users sit: MOSTLY TRUE (the numbers are slightly off)

| Quantity | Model |
|---|---|
| Use band (a single interval) | y in [0.676, 0.809] of mean income = **percentiles 50.1 to 59.0** |
| Users' mean income / population mean | **0.740** (the 54.6th percentile) |
| Users' median income / mean | 0.739 |
| Population **median** income / mean | **0.675** |

- Users are a single band about 9 percentiles wide, starting at the median. The referee's "52nd–60th"
  is about 1 to 2 points high; the band is the 50th to 59th.
- 0.74 is **above** the median (0.675), not roughly equal to it. Every user is at or above the median
  household. Calling users "the poor" or people with "low incomes" is not what the calibrated model
  delivers.
- The model has no use at all below the median. That includes the bottom 20 % of the raw lognormal,
  which is truncated at y_min = 0.24.

## C. Curvature versus insurability: pending

## D. Novelty and "the poor" quotes: pending
