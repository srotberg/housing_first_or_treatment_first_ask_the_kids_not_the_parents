# The conditional arms at the corrected enforcement rates

Recorded here because `.gitignore` line 5 excludes `*.log`, so every number
below otherwise lives only on an ephemeral container's disk.

## Why these were re-run

`benchmark_of_record.txt`'s VECTOR carried `probability_of_detection=0.9` and
`probability_of_false_positive=0.05`, and its handover beats both the Fortran
declaration and `run_one_point.sh`'s defaults, so the author's chosen 0.95 /
0.005 never bound. The record regenerates from a run that echoes its own
vector, so the wrong values self-perpetuated. These arms pass the rates on the
command line, and each log is verified: `voucher_probabilities` prints
`0.995 0.995 0.05`, i.e. `1-p_fp` and `1-p_det`.

## Benchmark of record

Frozen-equilibrium converged, `FROZEN CONVERGED after 3 passes,
distance = 1.66e-5`, log `variant_save_20260909T075231Z.log`.

    b 0.0853159   lambda_d 0.0363024   h_1 0.0125524   pi_V 0.251031
    tau_l 0.207843   beta 3.49804   aleph 75.1749   price 1.0

## The arms

| | benchmark | rationed TF | conditionality only | universal HF | universal TF |
|---|---|---|---|---|---|
| rates | -- | 0.95/0.005 | 0.95/0.005 | n/a, no condition | 0.95/0.005 |
| `b` | 0.08532 | 0.05253 (-38.4%) | 0.05036 (-41.0%) | 0.11412 (+33.8%) | -- |
| `lambda_d` | 0.03630 | 0.02097 (-42.2%) | 0.01901 (-47.6%) | 0.05067 (+39.6%) | -- |
| `h_1` | 0.01255 | 0.01531 (+22.0%) | 0.01472 (+17.3%) | 0.00019 (-98.5%) | -- |
| `pi_V` | 0.2510 | 0.1765 | 0.1790 | 0.8527 | -- |
| `tau_l` | 0.2078 | 0.2028 | 0.2028 | 0.2479 | -- |
| `beta` | 3.4980 | 3.5601 | 3.5582 | 2.6743 | -- |
| `aleph` | 75.17 | 75.55 | 75.75 | 100.91 | -- |
| welfare (CEV) | -- | -3.99% | -4.18% | +38.4% | **unusable** |
| drug price | 1.0 | 0.8033 | 0.7807 | -- | 0.6696 |
| loops | -- | 50 | 51 | 42 | 80 (the cap) |
| drug-market gap | -- | 3.85e-3 | 1.57e-3 | 1.55e-3 | **0.541** |

Tolerances: drug market 5e-3, government budget 2.5e-2, counterfactual moments
5e-4. Logs: `variant_cf_20260909T150812Z` (rationed TF),
`variant_cf_20260909T173844Z` (conditionality only),
`variant_cf_20260909T064500Z` (universal HF),
`variant_cf_20260909T160315Z` (universal TF).

## What the arms say

**The sobriety condition is the whole mechanism.** Conditionality alone gets
MORE drug-use reduction than rationed treatment first (-41.0 against -38.4),
LESS homelessness (+17.3 against +22.0), the same tax to four digits and
welfare within 0.2 points. The steering machinery on top of the condition
buys nothing.

**`beta`'s rise was the false-positive rate.** Two independent converged arms
put it at 3.5601 and 3.5582 against a benchmark 3.4980 -- up 1.7 to 1.8 per
cent. At the buggy rates the same rationed arm gave 3.8320 (+9.6%) and
universal TF gave 4.3296 (+23.8%). `p_fp = 0.05` was a five per cent annual
chance of wrongful voucher removal for every CLEAN eligible household, an
uninsurable shock to exactly the households with the least buffer; they
self-insured by saving. At 0.005 the motive nearly disappears. Bequests move
the same way: 0.6907 benchmark, 0.7693 at the old rates, 0.6993 corrected.

**Treatment first loses on welfare by construction, and that is a modelling
choice rather than a defect.** The addictive good enters utility at line 23044
as `(b_shifter + addiction/price)**relative_share_of_addiction_1` with weight
0.27, and the compensating variation scales ONLY non-drug consumption (line
17903). Conditionality destroys utility from a good carrying a 27 per cent
weight and the CEV must buy it back in the one good it may move. Whether the
paper's welfare criterion should count addicts' drug consumption at full
weight is the author's call.

## UNIVERSAL TF DID NOT CONVERGE. DO NOT USE ITS NUMBER.

It exited on `max_counterfactual_loops = 80` with the drug market at 0.541,
price 0.6696 against an implied supply price of 0.1323 -- a market five times
from clearing. It nevertheless printed
`welfare_of_gains_by_addiction = +0.1269`, which looks like a result and is
not one.

WHY. Correcting `p_fp` collapses demand in that arm to `V = 0.0072`, so the
market clears at a small fraction of the benchmark price.
`max_drug_price_move = 0.005` -- the author's half a per cent a loop, set 8
September -- cannot walk from 1.0 to there inside 80 loops. The cap bound on
every one of the 80 loops.

This is specific to the collapsed-demand regime and NOT general to the
corrected rates: conditionality only converged in 51 loops because its
quantity RISES as the price falls (0.1023, 0.1054, 0.1063) so the implied
price climbs to meet it, which is an ordinary demand curve. A prediction that
it would hit the cap too was made and withdrawn on the evidence.

THE FIX IS A WARM START, not a bigger cap: seed the counterfactual's starting
price near the answer. It changes no equilibrium condition and leaves
`max_drug_price_move` exactly as the author set it. `relative_price_change` at
line 22 is a compile-time `parameter`, so this needs a `drug_price_start`
handover case.

## THESE SIT ON A BENCHMARK THAT IS NOT CALIBRATED

Eight of twenty-five moments miss by more than the author's ten per cent
rule: `w_bot` +268%, `kappa_uem` +174%, `h_3` -89%, `kappa_ued` +27%,
`h_2` +25%, `lambda_m` -24%, `y_u` -23%, `beta` +17%. Of those:

- **`w_bot` is the newborn endowment and no refit will reach it.** Splitting
  2,785 archived points on that switch alone: `newborn_endowment_scale = 0`
  gives median `w_bot` 0.0351, `> 0` gives 0.0848, against a 0.025 target.
  Cross-tabulated against `kappa_uem` to rule out confounding: holding
  `kappa_uem > 10`, endowment 0 -> positive moves `w_bot` 0.0342 -> 0.094;
  holding the endowment positive, `kappa_uem > 10` -> `<= 1.5` moves it only
  0.0936 -> 0.0911. The target and the author's fixed newborn endowment are in
  direct conflict.
- **`kappa_uem` is a regression, not an unexplored lever.** The archive holds
  points at 12 and 34; the benchmark of record carries 1, so SMI households
  separate at exactly the same rate as everyone else and the channel is off.
  One archived point has `kappa_uem = 12` and `w_bot = 0.0230` together.
- **`beta` is ordinary.** The `endowment > 0` bucket has median `beta` 3.000,
  exactly on target; 3.498 is a point in the spread, reachable by
  `discount_factor`.

## The scoring tools carried targets the Fortran had stopped using

`code/suggest_next.py` and `code/converge.py` scored against `h_1` 0.00399
(live `fraction_homeless_data` 0.01160), `h_2` 0.132065 (live
`severe_cost_burden_data` 0.08), `theta` 0.1620 (live
`drug_spending_share_data` 0.14098), `p_m` 0.0 (live 0.0484785) and `pi_eu`
0.0485 (live `unemployment_rate_data` 0.049). The Fortran calibrates against
its own `_data` parameters and was never affected, but a refit that used these
tools to choose directions would have driven `h_1` down by a factor of three.
