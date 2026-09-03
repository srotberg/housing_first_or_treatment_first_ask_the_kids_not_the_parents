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
