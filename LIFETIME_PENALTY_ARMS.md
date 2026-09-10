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


## Universal Housing First: +40.28 per cent, against +40.74 on the one-class table

Converged: budget 2.43e-2 inside 2.5e-2, drug market 4.03e-10, 13 loops.

**This is the only arm tonight that is directly comparable to the old table**,
because it does no drug testing and so never reads `probability_of_false_positive`,
which the two Treatment First arms were run at the wrong value of.

| | benchmark | universal HF | ONE-CLASS TABLE |
| --- | --- | --- | --- |
| `b` | 0.086312 | 0.148456 (+72.0%) | +70.2% |
| `lambda_d` | 0.037097 | 0.065151 (+75.6%) | +74.8% |
| `h_1` | 0.013270 | 0.00030464 (-97.7%) | -98.5% |
| `pi_V` | 0.24750 | 0.85115 | 0.85375 |
| `tau_l` | 0.20637 | 0.24990 | 0.24838 |
| `beta` | 3.51466 | 2.68971 | 2.67526 |
| **welfare** | -- | **+40.28%** | **+40.74%** |

### THE LIFETIME CHILD PENALTY DOES NOT MOVE HOUSING FIRST

Welfare differs by less than half a percentage point, and every other moment
matches the one-class table within a couple of points.

That is the answer to the author's question, and it points away from the hope
behind it. The child externality -- permanent penalty, delta_d at 0.36, omega_c
at 0.17 -- is `omega` = 0.021 against a target of 0.183, about a NINTH of the
size the data implies. A channel that small cannot move a 43 point welfare gap.
Here it moves 0.46 of a point.

## A PARAMETER MISMATCH THAT INVALIDATED BOTH TREATMENT FIRST ARMS

`probability_of_false_positive` is 0.05 in the benchmark's vector and 0.005 in
the arms the one-class table was built from. It does NOTHING in the benchmark --
it binds only under conditionality -- so taking the vector from the benchmark's
own log carried the wrong value in silently, and nothing in the output said so.

Under the three-year exclusion every false positive bars an innocent household
from vouchers for three years, so a tenfold difference is not a detail:

| | old table, p_fp 0.005 | run at p_fp 0.05 |
| --- | --- | --- |
| rationed TF welfare | -2.14% | -4.82% |
| universal TF welfare | **+26.41%** | **-3.18%** |
| universal TF `pi_V` | 0.8363 | 0.6865 |
| universal TF `b` | 0.001230 | 0.007750 |

The lower coverage and the weaker drug reduction are the signature of innocent
households being excluded, not of a stronger child channel. Both TF arms are
being re-run at 0.005 so that the child penalty is the only thing that differs
from the one-class table. **The -3.18 per cent above must not be quoted as a
result.**

This is the same class of fault `CLAUDE.md` already records: a parameter that
binds only in a counterfactual does not belong with the calibration, and is
exactly the kind that travels unnoticed when a vector is lifted from a
benchmark log.
