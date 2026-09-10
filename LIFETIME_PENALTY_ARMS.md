# The arms on the benchmark with the lifetime child penalty

`.gitignore` excludes `*.log`, so without this file every number below lives
only on an ephemeral container's disk.

**The benchmark** is `variant_save_20260910T052352Z`, `FROZEN CONVERGED` in 2
passes at 3.64e-4, at `penalty_child_addicted` 0.36, `penalty_child_homeless`
0.14, `weight_on_child` 0.17, four child classes, perfectly elastic drug supply.
Its SUD odds ratio is 1.9857 against a target of 2.00.

Every arm carries the SAME three child parameters as the benchmark. An arm that
changed them would be measuring the penalty rather than the policy.

## Rationed Treatment First

Converged: government budget 1.69e-2 inside 2.5e-2, drug market 3.88e-10. 79
minutes.

| | benchmark | rationed TF | change | ONE-CLASS TABLE |
| --- | --- | --- | --- | --- |
| `b` | 0.086312 | 0.013760 | -84.1% | -85.7% |
| `lambda_d` | 0.037097 | 0.0045343 | -87.8% | -89.3% |
| `h_1` | 0.013270 | 0.013679 | **+3.1%** | -0.1% |
| `pi_V` | 0.24750 | 0.13147 | -46.9% | -- |
| `tau_l` | 0.20637 | 0.19683 | -4.6% | -- |
| `beta` | 3.51466 | 3.63467 | -- | -- |
| **welfare** | -- | **-4.82%** | -- | **-2.14%** |

## TREATMENT FIRST DOES NOT GAIN FROM THE BIGGER EXTERNALITY. IT LOSES MORE.

The author's hypothesis was that Treatment First should gain now that it
eliminates a larger externality. It does the opposite: welfare falls from
-2.14 per cent on the one-class benchmark to **-4.82** on this one.

The drug reductions are essentially unchanged, -84.1 against -85.7 per cent, so
the child channel buys nothing on the use margin. What moved is HOMELESSNESS:
flat at -0.1 per cent before, **+3.1 per cent** now.

A LIKELY mechanism, offered as a hypothesis and not as a finding, because a
mechanism narrated off partial evidence has been wrong three times in this
work: rationed TF bars the homeless-with-SUD from voucher offers, so coverage
nearly halves, homelessness edges up, and homelessness now carries an
intergenerational cost that it did not carry when the penalty decayed at 0.9.
The decomposition that would settle it is the same arm with
`child_penalty_off=1`, which the shutdown ladder can now express and could not
before today.
