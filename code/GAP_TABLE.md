# The full gap table at the best point, 6d1662b473 — 3 September 05:15

The drug block is the only thing the round has been working on and it is now
INSIDE the author's ten per cent standard: b at +6.0 and lambda_d at -7.7.
Seventeen other moments are outside it, several by a very long way.

| moment | model | target | gap | |
|---|---|---|---|---|
| `tau_u` | 0.47012 | 0.24500 | **+91.9%** | treatment take up |
| `pi_eu` | 0.07571 | 0.04900 | **+54.5%** | unemployment rate |
| `pi_V` | 0.38526 | 0.26600 | **+44.8%** | eligibles with a voucher |
| `aleph` | 114.32065 | 80.00000 | **+42.9%** | value of life / income |
| `kappa_uem` | 0.17941 | 0.30000 | **-40.2%** | employment given SMI |
| `omega_l` | 0.25875 | 0.40000 | **-35.3%** | labour supply / total hours |
| `kappa_ued` | 0.21714 | 0.16250 | **+33.6%** | unemployment given SUD |
| `w_bot` | 0.03229 | 0.02500 | **+29.2%** | net worth share, bottom half |
| `theta` | 0.19672 | 0.16200 | **+21.4%** | drug spending share |
| `h_1` | 0.00479 | 0.00399 | **+20.0%** | homelessness rate |
| `beta` | 2.42784 | 3.00000 | **-19.1%** | wealth over output |
| `lambda_m` | 0.21261 | 0.25000 | **-15.0%** | SMI share of the homeless |
| `tau_l` | 0.25213 | 0.22400 | **+12.6%** | average labour income tax |
| `h_2` | 0.08861 | 0.10100 | **-12.3%** | above half of spending |
| `mu_H` | 1.29882 | 1.47321 | **-11.8%** | recovery housed / homeless |
| `cbar` | 0.00465 | 0.00420 | **+10.7%** | food stamps / income |
| `gamma` | 0.24000 | 0.26800 | **-10.4%** | housing over expenditure |
| `lambda_d` | 0.03396 | 0.03680 | -7.7% | disorder rate |
| `p_m` | 0.04453 | 0.04821 | -7.6% | SMI population share |
| `y_u` | 0.79267 | 0.74000 | +7.1% | income of drug users |
| `b` | 0.09435 | 0.08900 | +6.0% | total drug users |
| `sigma_y` | 0.18035 | 0.17200 | +4.9% | bottom half earnings share |
| `h_3` | 0.61124 | 0.62672 | -2.5% | share in the largest unit |

## The mismatch that matters

The author's standard, stated plainly: *"once we get below 10% for everything
we can stop"*. The gate's threshold on b and lambda_d is **5** per cent, and its
own rule keeps the whole fleet on the drug block alone until it gets there.

So the fleet is currently spending every worker driving 7.7 per cent down to 5
on a block that already meets the author's standard, while `tau_u` sits at +91.9,
`pi_eu` at +54.5 and `pi_V` at +44.8. That is the wrong allocation against the
stated objective and it is a threshold choice, not a modelling problem.

## What the drug round established, and its floor

Four points now sit on the (addiction_scalar_1, lambda_addiction) segment and
both moments are fitted as quadratics in position along it. Refitting on all
four puts the minimax at f between 0.72 and 0.74, worth **6.4 to 7.0 per cent**
against 7.72 now. So one more solve on this segment buys about a point and a
half and then the segment is exhausted.

Below that needs a direction that moves lambda_d relative to b, and every
instrument tried does not: `utility_cost_of_treatment` is non-monotone and its
useful range is spent by 2.4; `pi_eu`'s lambda_d slope does not transfer and
cost 26 per cent on the unemployment rate; `theta` and `value_of_life` are
cliffs; `mu_homeless` is flat. **The 5 per cent gate may not be reachable with
the instruments in the model**, which is a finding about identification rather
than a step the gate can take.

---

# Why the gate cannot open: b and lambda_d are not separately identified

Fifteen points now sit in the `(addiction_scalar_1, lambda_addiction)` plane
differing in nothing else. Fitting the two gaps locally on the five points
nearest the target:

    gap_b    = -32073.6 + 555412*scalar +  5067.7*lambda    residual 1.5pp
    gap_lam  = -94960.3 + 1650850*scalar + 14913.8*lambda   residual 1.6pp

**The Jacobian's condition number is 36,711.** The two moments respond almost
identically to both instruments; the plane is effectively one-dimensional as far
as they are concerned. Solving it for both gaps zero gives
`scalar = 0.034997, lambda = 2.49331` — which sits beside `cfb102c1ab` at
`(0.035725, 2.49267)`, a point already MEASURED at gap_b −19.5 and gap_lam −39.2.
The solve points into a region known to be much worse, which is what a
near-singular system does.

## And no other direction is steep enough

Across **452 measured directions** between current-model points differing in
three names or fewer, the ratio `|d(gap_b) / d(gap_lambda)|` runs from 0.04 to
**5.92**. Opening the gate from the best available starting point —
`a8b4808a6d`, gap_b +8.62 and gap_lam −4.65 — requires b to fall 3.6 points
while lambda_d gives up at most 0.35, a ratio of about **10**. Nothing measured
comes close.

## The arithmetic of the segment, for completeness

The gate needs b within +5 AND lambda_d within −5. On the searched segment b
reaches +5 only at f ≳ 0.825 and lambda_d holds −5 only at f ≲ 0.748. **The two
admissible intervals are disjoint.**

## What this is not

Not noise: a repeat of an identical vector agreed to eleven significant figures
on b. Not a bad step: six Jacobian-fitted steps and four bracket interpolations
were solved, and the best of all of them is 7.72 per cent. Not an unexplored
direction: theta and value_of_life are cliffs that take b to zero or to +400 per
cent, mu_homeless is flat, utility_cost_of_treatment is non-monotone with its
useful range spent by 2.4, and pi_eu's lambda_d slope does not transfer and
costs 26 per cent on the unemployment rate.

## The consequence for the engine

`GATE` has **no patience escape**. `STAGE_PATIENCE` opens a stalled *stage*;
the gate is a separate guard and it opens only when some point has BOTH moments
inside 5 per cent. The round has been the drug block alone for six firings at
7.7 per cent, and on this evidence it will stay there.
