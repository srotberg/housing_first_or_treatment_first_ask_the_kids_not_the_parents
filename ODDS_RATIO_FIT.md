# Fitting delta_d, delta_h and omega_c on the lifetime child penalty

`.gitignore` excludes `*.log`, so without this file every number below lives
only on an ephemeral container's disk.

All points share ONE build: `child_penalty_classes=4`,
`voucher_exclusion_states=1`, `measure_child_gap=1`, perfectly elastic drug
supply. Each probe differs from the anchor in exactly ONE parameter, because a
secant taken across two points that differ in anything else is not a secant.

**READ THE LAST BLOCK, AFTER `FROZEN CONVERGED`.** `omega` prints twice and the
earlier print is taken off a state that is not an equilibrium. Quoting the wrong
one produced 0.0824 against a true 0.00755 in this session -- a factor of
eleven -- and it had already produced 0.0613 against a true 0.000252 earlier the
same night.

## The targets

| | target | source |
| --- | --- | --- |
| child SUD odds ratio | 2.00 | `child_sud_ratio_data` |
| child homelessness odds ratio | 2.10 | Bassuk et al. (1997), midpoint of 1.80 and 2.41 |
| `omega`, use rise with the child term off | 0.18343 | `1/0.845 - 1` |

## The points

| point | `delta_d` | `delta_h` | `omega_c` | SUD odds | homeless odds | `omega` | log |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A anchor | 0.24 | 0.31 | 0.007 | **1.5505** | **4.9109** | **0.0075517** | `variant_save_20260910T032800Z` |
| B | 0.36 | 0.31 | 0.007 | | | | `fit_delta_d.log` |
| C | 0.24 | 0.15 | 0.007 | | | | `fit_delta_h.log` |
| D | 0.24 | 0.31 | 0.05 | | | | `fit_omega_c.log` |

Anchor underlying rates: SUD exposed 0.053417 against unexposed 0.035118;
homelessness exposed 0.046770 against unexposed 0.0098922.

## Odds ratio, not risk ratio, from 10 September

The author: *"yes, change it to the odds ratio"*. Both targets always were odds
ratios while the model reported `p_exposed/p_unexposed`, a RISK ratio. The two
agree only for a rare outcome and the odds ratio is the larger, so the model was
scored against a target above the quantity it computed. Measured, the gap is
1.9 per cent on the SUD ratio (1.5505 against 1.5212) and 3.9 per cent on
homelessness (4.9109 against 4.7280) -- small, and always in the direction that
flattered the model.
