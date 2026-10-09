# Referee item 7: verification against the code (stylized model, Section 3)

**Verdicts.**

- **A, negative value of life: partly true.** The share is right: 2.47 % of period-2 survivors have a
  negative realised flow. It applies only to non-users who are out of work in period 2. In period 1 the
  value of life is negative for 0 % of households, and in period 2 the value of being alive, W, is never
  negative. So footnote 8 is literally true and is not contradicted.
- **B, where users sit: mostly true.** Users are a single band at percentiles 50.1 to 59.0, not 52 to 60.
  Their mean income, 0.74, is above the median of 0.675, so no user is below the median.
- **C, curvature versus insurability: mostly true.** With sigma = 2 and a VSL proportional to income,
  users stay the top 8.9 % at every kappa. Under log they stay at the top up to kappa of about 24 and
  reverse only at 27 to 37. The paper's reversal needs sigma = 2 with additive aleph. Insurability alone
  does not deliver it, and neither does the no-saving demonstration in the right panel.
- **D, novelty and "the poor": quoted below.** "First economic theory" appears at line 200. Users are
  called poor or low-income at lines 164, 200, 258, 396 and 1203.

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

## C. Curvature versus insurability: MOSTLY TRUE ("however large" is literally false under log)

Partial equilibrium. The Section 3 model has no prices to clear. Every specification starts from the same
benchmark. kappa_phi_d - 1 is scaled by x, from 0 to 100 times its calibrated value: kappa runs from 1 to 257,
and survival with a SUD from 0.93 to 0. Unemployment is either switched off (u1 = u0, Figure 1's mortality
curve) or held at its calibrated value. At every point b is refitted so that participation is 8.90 %,
walking up from x = 0 as `gradient.scan` does. The value-of-life variants are made in an in-memory copy of
`gradient.py`'s source; the file itself is not touched.

Script: `code/stylized/referee_item7/c_curvature_scan.py`. Output: `c_output.txt` and `c_scan.json`.

Users' mean income over the population mean (3.51 means the top 8.9 %, 0.27 the bottom 8.9 %):

| x (kappa) | survival with a SUD | sigma=2, additive (paper) | log, additive | log, aleph refit to VSL 80 | sigma=2, VSL proportional to income |
|---|---|---|---|---|---|
| 0 (1.00) | 0.93 | 3.51 / 3.51 | 3.51 / 3.51 | 3.51 / 3.51 | 3.51 / 3.51 |
| 0.5 (2.28) | 0.85 | 1.55 / 1.82 | 3.51 / 3.51 | 3.51 / 3.51 | 3.51 / 3.51 |
| **1 (3.56, calibrated)** | 0.77 | **0.65 / 0.74** | **3.51 / 3.51** | **3.51 / 3.51** | **3.51 / 3.51** |
| 2 (6.12) | 0.64 | 0.27 / 0.27 | 3.51 / 3.51 | 3.51 / 3.51 | 3.51 / 3.51 |
| 8 (21.5) | 0.21 | 0.27 / 0.27 | 3.51 / 3.51 | 3.51 / 3.51 | 3.51 / 3.51 |
| 9 (24.0) | 0.17 | 0.27 / 0.27 | 3.51 / 3.26 | 3.51 / 2.74 | 3.51 / 3.51 |
| 10 (26.6) | 0.14 | 0.27 / 0.27 | 1.66 / 1.20 | 1.44 / 1.01 | 3.51 / 3.51 |
| 12 (31.7) | 0.10 | 0.27 / 0.27 | 0.75 / 0.59 | 0.27 / 0.27 | 3.51 / 3.51 |
| 14 to 100 (37 to 257) | 0.07 to 0 | 0.27 / 0.27 | 0.27 / 0.27 | 0.27 / 0.27 | 3.51 / 3.51 |

Each cell is (unemployment channel off / unemployment at its calibrated value).

The specifications:

- "log, additive" is sigma = 1 at the benchmark aleph, which puts the VSL at mean income at 251.
- "aleph refit" lowers aleph to 4.18 so that the VSL is 80.
- "VSL proportional to income" is sigma = 2 with a value of life aleph * y^(1 - sigma). Then VSL = value of
  life / U'(c) is proportional to y, and the VSL at mean income is still 80. This is the specification the
  referee's phrase describes. Under additive aleph at sigma = 2 the VSL rises roughly with y^2, as the
  paper's own footnote (line 784) says.
- A literal "aleph * y in utils" variant was also run. Its VSL rises roughly with y^3, and it has a
  **negative** period-1 value at y_min (V1 = -2.3 even at x = 0). It is invalid as a test and is reported
  only in `c_output.txt` (columns `prop` and `logprop`).

Findings:

- **sigma = 2 with a VSL proportional to income: users stay the top 8.9 % at every kappa up to 257**,
  that is, with survival after a SUD at zero. The referee's claim holds exactly. An uninsurable death risk
  alone does not reverse the gradient.
- **Log: users stay the top 8.9 % up to kappa of about 24** (survival after a SUD 0.17). They reverse only
  at kappa of about 27 to 37, which is 7 to 10 times the calibrated 3.56 and 4 to 9 times the literature
  range the paper cites (3.91 to 6.6). Refitting aleph to keep the VSL at 80 moves the threshold only
  slightly, to kappa 26 to 32. So "however large the mortality risk" is **literally false** under log, but
  true over any range of kappa the paper treats as plausible. Under log the switch is abrupt: two bands at
  x = 10, and the bottom 8.9 % by x = 14.
- **The paper's mechanism (sigma = 2, additive aleph)** reverses at 73 % of calibrated strength, as the paper
  says: 0.65 at the calibrated kappa with unemployment off, 0.74 with it on, and the bottom 8.9 % from
  kappa of about 4.2 to 6.1. **This reproduces the paper's Figure 1 numbers** (0.64, 0.27).

**The other half of the argument: the unemployment channel alone** (kappa = 1, u1 = u0 + x(u1 - u0), b refitted
in steps of 0.05; script `c2_unemployment_and_vsl.py`, output `c2_output.txt`). Users' income over the mean:

| x (u1) | sigma=2 additive, saving on / off | log, saving on / off | sigma=2 VSL proportional to income, saving on / off |
|---|---|---|---|
| 0.5 (0.11) | 3.51 / 1.83 | 3.51 / 3.51 | 3.51 / 1.83 |
| **1 (0.1625, calibrated)** | **3.51 / 0.75** | **3.51 / 3.51** | **3.51 / 0.75** |
| 2 (0.28) | 3.51 / 0.27 | 3.51 / 3.51 | 3.51 / 0.27 |
| 6 (0.73) | 3.51 / 0.27 | 3.51 / 3.51 | 3.51 / 0.27 |
| 8 (0.95) | 3.51 / 0.27 | 3.51 / 0.27 | 3.51 / 0.27 |

- The paper's right panel is reproduced: 0.75 at the calibrated strength with saving off, 0.27 at 200 %.
- With kappa = 1, the value-of-life specification cannot matter, because aleph cancels in the use decision.
  That is why the last column equals the first.
- **Under log, the unemployment channel without saving does not reverse the gradient until u1 is about
  0.95.** So the paper's no-saving demonstration (the right panel) also rests on sigma = 2.
- With saving on, unemployment never reverses the gradient under any specification. That part of the
  insurability argument holds whatever the curvature.

**Verdict on the paper's explanation.** Insurability is not sufficient for the reversal, and on these
numbers it is not what does the work:

- With death equally uninsurable, the reversal disappears when the VSL is proportional to income (sigma = 2),
  and needs a mortality ratio about ten times the literature's under log.
- The reversal at plausible kappa needs a value of life that rises faster than income. With sigma = 2 and
  additive aleph the VSL rises roughly with y^2, which is the Hall–Jones property the paper's own footnote
  at line 784 attributes to its specification.
- The explanation in the text at line 396 ("it cannot be insured ... so the loss grows with income") is
  therefore **incomplete**. In the model, the loss grows faster than the drug's value only because of
  sigma = 2 with additive aleph.

## D. Novelty claims and "the poor" (writing/housing_first_children_later.src.tex)

Novelty:

- **Line 200** (Introduction): "The literature has explained the two facts together only by assuming that
  lower-education households have a systematic preference for drugs (Greenwood et al., 2025). ... As far as
  I know, this is the first economic theory that can explain both facts without systematic differences in
  preferences."
- Line 232 (Related literature) contrasts the paper with Greenwood et al. ("here no preference parameter
  varies with income, and the gradient comes from the uninsurable mortality risk of a SUD"). It makes no
  priority claim.
- No other "first", "novel" or "to my knowledge" claim appears. Every other "first" in the file refers to a
  period, a column, an experiment or an item. Hall and Jones (2007) is cited once, in the aleph footnote at
  line 784, for the VSL rising with roughly the square of consumption. It is not cited in Section 3.

Users described as poor or low-income:

- **Line 164** (abstract): "Use concentrates among the poor because a substance use disorder's mortality
  risk, unlike its unemployment risk, is uninsurable."
- **Line 200**: "Use is concentrated at the bottom of the income distribution ... so in equilibrium use
  concentrates at the bottom."
- **Line 258** (Section 3 opening): "their use is concentrated among people with low incomes ... which
  deters the rich and not the poor and so reverses the income gradient in drug use."
- **Line 396**: "no greater in utility terms for a rich household than for a poor one ... deterring the
  rich and not the poor."
- **Line 1203** (Appendix A, the progressivity parameter): "households with low incomes, among them most
  voucher holders and most drug users". This is about the quantitative model.
- Line 1163 ("job loss concentrates further among the poorest") is about job loss, not users.

Lines 164, 200 and 258 describe the data (users at 0.74 of mean income in the NSDUH). The model statements
(lines 200, 258, 396) claim the model puts use at the bottom. In the calibrated stylized model, users are
percentiles 50.1 to 59.0, all at or above the median (claim B).

## Caveats

- **Model choice.** All numbers are for `gradient.py`, the model the paper prints. The referee task named
  `stylized.py` / `calibrated_stage2.json`. That is the older staged model behind footnote 7's "version with
  housing", and it was not re-examined here.
- **No grid coarseness in A and B.** The model is semi-analytic: the use set is found by root-finding on a
  2,500-point log grid, and the moments are exact lognormal integrals. The shares in A use 400,000
  equal-mass nodes. The grid's upper end is y = 80, so "the top" band is reported as [2.13, 80]. Above 80
  the mass is negligible.
- **Where the log thresholds sit.** In C the log reversal thresholds are bracketed by the scan points
  (x = 9, 10, 11, 12, 14). The exact crossing was not solved.
- **Partial equilibrium.** Throughout C, only b is refitted. aleph, theta, kappa and cbar are not
  recalibrated to the other targets (VSL, spending share, users' income, food share). The exception is the
  log80 column, where aleph alone is refitted to the VSL.
