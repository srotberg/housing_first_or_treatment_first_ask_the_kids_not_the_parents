# The arms at perfectly elastic drug supply

`.gitignore` line 5 excludes `*.log`, so without this file every number below
lives only on an ephemeral container's disk.

All five runs share ONE benchmark, ONE build and ONE supply curve, which is the
first time today that has been true. Benchmark
`variant_save_20260909T224807Z`, `FROZEN CONVERGED` in 3 passes at 1.91e-5.

## Why perfectly elastic

The author, 9 September: *"the drug market does not need to be cleared... It is
perfectly elastic supply"*, and separately that 1.46 is *"way too low"*.

`drug_supply_curvature = 1 + 1/elasticity`, so at 1e6 the exponent on quantity
is 1e-6 and `implied_price = shifter`, which the benchmark normalises to one.
The gap is identically zero at EVERY quantity: the market clears at a price of
one by construction. Clearing is a step only when the curve slopes up. Measured
`drug_supply_shifter (normalised) = 1.0000015`, and every arm's
`distance_drug_market` came in between 2.7e-10 and 1.5e-8 on loop one.

The literature supports this over 1.46: 1.46 is Mace, Patel and Seegert's
CANNABIS figure from LICENSED Washington producers, and licence caps are what
make that curve slope up. Retail-to-farmgate for cocaine is about 262:1, so
production is ~0.4% of the retail price; commercialisation estimates put the
fall at 96% (cocaine) and 98% (heroin). Rhodes et al. (2002) assume very
elastic supply for exactly this reason.

## The arms

| | benchmark | rationed TF | universal TF | universal HF | universal TF, 1-yr |
|---|---|---|---|---|---|
| `b` | 0.084902 | 0.012160 | 0.001230 | 0.144530 | 0.000217 |
| | | −85.7% | −98.6% | **+70.2%** | −99.7% |
| `lambda_d` | 0.035920 | 0.003855 | 0.000316 | 0.062794 | 0.0000849 |
| | | −89.3% | −99.1% | **+74.8%** | −99.8% |
| `h_1` | 0.012529 | 0.012513 | 0.000991 | 0.000188 | 0.000319 |
| | | **−0.1%** | −92.1% | −98.5% | −97.5% |
| `pi_V` | 0.251825 | 0.224890 | 0.836326 | 0.853754 | 0.701447 |
| `tau_l` | 0.207885 | 0.206578 | 0.241038 | 0.248381 | 0.227756 |
| `beta` | 3.49741 | 3.48067 | 2.78483 | 2.67526 | 2.94713 |
| **welfare** | -- | **−2.14%** | **+26.41%** | **+40.74%** | +12.75% |
| loops | -- | 3 | 13 | 10 | 11 |
| budget gap | -- | 1.35e-2 | 2.02e-2 | 1.65e-2 | 1.04e-2 |
| moment gap | -- | 1.37e-4 | 1.67e-4 | 1.53e-4 | 9.2e-5 |

Tolerances: drug market 5e-3, budget 2.5e-2, moments 5e-4. All five inside.

## What changed against the 1.46 runs, and why

At 1.46 with a one-period sanction, rationed TF cut drug use 39% and RAISED
homelessness 21%. At flat supply it cuts use 86% and leaves homelessness flat.
The reason is visible in the earlier run's own trace: at loop 11, with the
price still at 0.975, `b` was 0.01238 -- almost exactly today's 0.01216. The
deterrent at an unchanged price was always about −86%; the falling price then
clawed back two thirds of it and manufactured the homelessness increase.

The same artefact was flattering Housing First in the opposite direction: it
RAISES use, so the 1.46 curve let the price rise to 1.2077 and choked off half
the increase. Flat supply takes +34.2% to **+70.2%**.

## Rationing, not conditionality, is what makes treatment first fail

Rationed and universal TF carry the SAME sobriety condition and the SAME
three-year exclusion. Rationed leaves homelessness at −0.1%; universal clears
it at −92.1%. The difference is coverage: 0.2249 against 0.8363. Under
rationing the addicted homeless who get housed are replaced by voucher-losers,
and the two cancel.

## THE HEADLINE IS A NORMATIVE CHOICE, NOT A FINDING

Universal HF scores +40.74% against universal TF's +26.41% while causing 70%
more drug use, 75% more disorder and a higher tax, its only advantage being 6
points of homelessness. That ordering is produced by the welfare criterion
counting the addictive good: it enters utility with weight 0.27 and a
Stone-Geary shifter of `addiction_scalar_1 = 0.00255` against a typical
quantity per user of 0.0515 -- only 5% of consumption -- so quitting destroys
`1 - (0.00255/0.05403)**0.27 = 56%` of that utility factor, for the 8.5% of
people who use.

Excluding drug utility from the planner's objective would raise TF (0.12% users)
and lower HF (14.5% users) relative to a benchmark at 8.5%, and could flip the
ranking. It needs a policy-evaluation sweep under a modified flow utility on
both sides, reusing `compute_value_function_comparison`'s pattern.

## The externalities are small, and one is small for a suspicious reason

Priced off the bisection trace, `dV/dx = 194.6`, with a discounted annuity of
14.97 at beta 0.934317 over 60 periods:

| | homelessness | externality gain, CEV |
|---|---|---|
| universal TF | 0.01253 -> 0.00099 | **+0.00018%** |
| rationed TF | 0.01253 -> 0.01251 | +0.0000004% |

One part in 150,000 of universal TF's +26.41%. The reason is the
specification: line 18050 subtracts `kappa_x * model_fraction_homeless(1)`, so
what a household feels is kappa_x times the RATE. `kappa_x = 0.002` was agreed
as "roughly 50 euro a year"; at a 1.25% homelessness rate the felt cost is
1/80th of that. If the 50 euro is meant to be the cost of homelessness AS
OBSERVED, kappa_x should be near 0.16. That is a question about intent.

The child externality is larger but bounded: at most 4.8% of children inherit
any penalty (the benchmark SUD rate plus the homelessness rate), at 24% and 31%
of earnings. `weight_on_child = 0.007`, so it barely enters the parent's
decision at all, and `measure_child_gap = 0`, so it is not even computed as a
moment.

## OPEN, AND NOT TO BE PAPERED OVER

**The exclusion decomposition is not interpretable.** The three-year exclusion
gives 5.7x more drug use, 3.1x more homelessness AND higher coverage than the
one-year sanction. Coverage rising when people are barred for three years is
not economics. Two explanations were tested and REJECTED: precautionary saving
from a perceived-risk asymmetry (it predicts beta up, beta went down, 2.785
against 2.947), and `pi_V` miscounting the excluded (it accumulates only on
`housing_voucher_2 > 0`). No third theory is offered here. The model reports no
mass by voucher state, so how many households sit in the excluded state is
unknown; a diagnostic print would settle it in one run.

**A clean voucher holder never perceives the false-positive risk.** Its range
starts at `first_voucher_index = include_vouchers` = 1, so the `(1,0) = p_fp`
transition is outside the integration range. Addicted holders under TF get the
override branch and DO perceive detection. This is a defect in the original
model, present in every arm measured today, and fixing it invalidates this
table.

**`pi_V` counts payment RECIPIENTS, not holders.** A homeless household's
voucher pays exactly zero, so homeless holders are not in the numerator. The
0.266 target is administrative holding data.

**Eight benchmark moments remain outside the author's 10% rule**, `w_bot` at
+268% and `kappa_uem` at +174% among them. Nothing here is publishable until
that is repaired.
