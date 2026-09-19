> **NOT REPRODUCED. THE NUMBERS BELOW ARE NOT PINNED TO BETTER THAN ABOUT A
> FACTOR OF TWO ON WELFARE.** 19 September. Arm 3 was solved a second time from
> the same seed with the same parameters, and the two runs both reported
> CONVERGED on all three live rules while landing 4 per cent apart on b,
> lambda_d and h_1, 8 per cent apart on pi_v, and giving a CEV of +1.646 per
> cent against +3.291 per cent. The cause is the stopping rules, not the model:
> frozen_stop_tolerance halts on block-to-block MOVEMENT so a run stops wherever
> the descent is slow, the CF-moments rule is 5e-4 ABSOLUTE across moments whose
> sizes differ by an order of magnitude (7.7 per cent of h_1), and nothing
> constrains pi_v or the drug price directly. See CALIBRATION_STATE.md, top
> entry. Arms 1 and 2 ran under the same rules and have not been re-checked.

# ARM 1 -- THE OPTIMAL DRUG USE RATE (omega_c = 1, no internalisation)

**CONVERGED**, block 9, run completed cleanly (exit 0, `simulation_ended`).

    weight_on_child 1.0   internalise_homelessness_cost 0   kappa_x 0.8139
    penalty_child_addicted 0.24   adjust_taxes 1   drug price cleared at eps_s = 1.46
    warm start: price 0.8750, pi_v 0.0689 (both guesses, off arm 2's answer)

## THE EQUILIBRIUM

| quantity | value |
|---|---|
| price of the addictive good | 0.870124 |
| drug quantity V | 0.403503 |
| b, total drug users | 0.052083 |
| lambda_d, SUD rate | 0.021257 |
| h_1, homelessness rate | 0.0053099 |
| homeless and addicted | 0.109189 |
| pi_v | 0.068989 |
| average welfare with childhood | 780.98697 |

## THE THREE LIVE RULES

    CF moments   3.6023e-04   (rule 5e-4)   ok
    budget       1.6628e-02   (rule 2.5e-2) ok
    drug gap    -7.6616e-05   (rule 5e-3)   ok, essentially exactly cleared

Rental, housing and inheritance are identically 0.0 on every loop -- the rent is
pinned at 1 and supply is set equal to demand -- so they are unmeasured, not
satisfied. THREE rules were checked, not six.

Signed drug-gap path (reconstructed; the log prints only |gap|):

    +0.06753 +0.00897 -0.01953 -0.01146 -0.00405 +0.00163 +0.00118 -0.00427 -0.00008

## Q1: THE OPTIMAL DRUG USE RATE AND SUD RATE

| | benchmark (n90) | arm 1 | change |
|---|---|---|---|
| b, total drug users | 0.081813 | 0.052083 | **-36.3%** |
| lambda_d, SUD | 0.033609 | 0.021257 | **-36.8%** |
| lambda_d / b, SUD per user | 0.41080 | 0.40814 | -0.6% |
| drug quantity V | 0.494427 | 0.403503 | -18.4% |
| price | 1.000000 | 0.870124 | -13.0% |

SUD per user barely moves. The whole fall in SUD comes through the extensive
margin -- fewer users -- not through users becoming less likely to develop a
disorder.

## THE CEV IS -0.2443 AND IT IS NOT A WELFARE RESULT

The model's own number, `CEV from the saved benchmark curve: target=780.98697
x=-0.24428680`. **Do not quote it.** omega_c is a term in the OBJECTIVE, not an
instrument: the flow is [A_parent + omega_c*A_child]/(1-sigma) with sigma = 2,
so the bracket is divided by -1 and raising omega_c from 0.055 to 1 adds 0.945
times more of a negative quantity. The level falls mechanically whether or not
anyone is worse off.

MEASURED across the calibration trials, which is why this is not a guess:

    omega_c 0.055 -> welfare 791.25 (n86), 791.39 (n90)
    omega_c 0.100 -> welfare 790.88 (n85)
    omega_c 0.135 -> welfare 789.97 (n84)

about -16 utils per unit of omega_c. Note the asymmetry that causes it: the
CHILD'S OWN welfare does carry value_of_life, inside the factor at 27942,
`(xi-1)*(child_flow_out + value_of_life)`. The term the PARENT weighs by omega_c
does not -- value_of_life is added once at 27896, outside the weight.

A real welfare statement would evaluate arm 1's allocation under the BENCHMARK's
objective. That is a separate exercise and no arm here produces it.
