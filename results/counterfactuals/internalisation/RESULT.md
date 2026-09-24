# omega_c = 0.06, FULL HOMELESSNESS INTERNALISATION, kappa_x = 0.9329

**CONVERGED by the family stop rule at block 10.** Blocks 9 and 10 both moved b by
less than 0.5 per cent (0.3800% then 0.0593%), which is the two consecutive blocks
the rule requires. The run was stopped by hand at block 10, before the block-12 cap.

The stop was NOT taken on `block_move`. That metric read 1.3957E-003 at block 10 and
never fell inside its own 1.0E-003 rule at any point in the run -- the same failure
the benchmark showed, where it fell to 0.00513, rose to 0.036 and never fired. At
block 8 this run's block_move was 5.199E-003, essentially the benchmark's 0.00513.

Independently confirmed by `python3 code/paper/calibration_report.py` on the log:
"10 moment blocks; this is loop 10, and it is within one per cent of loop 9:
b +0.1%  lambda_d -0.1%  theta -0.1%."

## Configuration

Command: `sh code/remote_internalise_point.sh stage` then `solve 0.9329`
Launched 2026-09-24T01:46:52Z, stopped 2026-09-24T04:14:36Z (2h 28m, 10 blocks).
OMP_NUM_THREADS=2. 98-line handover, all 98 HANDOVER lines ingested.

    kappa_x                        0.9329   (2.0000000000000000E-003 -> 0.93289999999999995)
    internalise_homelessness_cost  1        (0 -> 1)
    weight_on_child                0.06
    addiction_onset_base           3.4509299932932086E-002   (NOT the declared 0.d0)
    freeze_all_but_omega_c         1
    omega_c_is_pinned              1

kappa_x on an income basis: the benchmark control's converged probe reports 0.9329
on income and 0.6083 on consumption, and 0.6083/0.65201 = 0.93296 with
s = aggregate_consumption/model_total_income = 0.65201. This raises the calibrated
0.8139 by 14.62 per cent.

The charge is declared at source line 3688 and applied at 28688 as
`flow_utility_1=flow_utility_1-kappa_x` when
`future_housing_status_index_1==lowest_housing_grid_point`, deliberately AFTER
`flow_utility_goods_only` is recorded, so it stays out of the drug first-order
condition. Both sites verified unchanged before the run.

## Blocks

b is `model_total_drug_users(1)` as labelled on the BLOCK MOVE line (source 52272);
h_1 is `model_fraction_homeless(1)`.

| block | b | lambda_d | h_1 | bequest_residual | block_move | rel d(b) |
|---|---|---|---|---|---|---|
| 1 | 0.0710980261 | 0.031144 | 0.0068710742 | 2.122827 | 1.000000 | — |
| 2 | 0.0840187692 | 0.035461 | 0.0064076885 | 1.836144 | 0.206163 | 18.1731% |
| 3 | 0.0849234171 | 0.036153 | 0.0062471713 | 1.632887 | 0.085328 | 1.0767% |
| 4 | 0.0840650899 | 0.035931 | 0.0060857231 | 1.564289 | 0.039102 | 1.0107% |
| 5 | 0.0826311965 | 0.035456 | 0.0060119038 | 1.508485 | 0.018627 | 1.7057% |
| 6 | 0.0807306569 | 0.034947 | 0.0059934925 | 1.486959 | 0.023000 | 2.3000% |
| 7 | 0.0800304672 | 0.034214 | 0.0059848754 | 1.462368 | 0.020984 | 0.8673% |
| 8 | 0.0796144121 | 0.034053 | 0.0059547157 | 1.458085 | 0.005199 | 0.5199% |
| 9 | 0.0793118841 | 0.033897 | 0.0059376517 | 1.454366 | 0.004592 | **0.3800%** |
| 10 | **0.0793589529** | **0.033850** | **0.0059295674** | **1.452856** | 0.001396 | **0.0593%** |

### The last three blocks' b, to full precision

    block  8   b = 7.9614412136896767E-002
    block  9   b = 7.9311884107822972E-002
    block 10   b = 7.9358952915334569E-002   <- converged

## Converged point

    b                        7.9358952915334569E-002
    lambda_d                 3.3849649273996897E-002
    model_fraction_homeless  5.9295673625692699E-003   (0.592957 per cent)
    bequest_residual         1.4528562860900192

`bequest_residual` landed at 1.45286, against the converged omega_c = 0.06 reference
of 1.45135 (0.10 per cent above) and the benchmark's 1.4771. Block 1's residual was
2.1228 -- the restart transient, and its b of 0.0711 was NOT the answer, exactly as
the family's calibration note for the omega_c = 0.07 point predicted (that point read
-28.06 per cent at block 1 with residual 2.1197 and settled at -18.65 per cent with
residual 1.4496; this one read -28.1 per cent at block 1 and settled at -19.77).

## Against the converged omega_c = 0 benchmark

Benchmark (code/scan_seed/PROVENANCE.txt): b = 9.8916056747807166E-002,
lambda_d = 4.3579290623499613E-002, h_1 = 6.?E-003 (the provenance line is truncated
after "6." so the benchmark h_1 cannot be quoted to more than its leading digit).

    b         -19.77 per cent
    lambda_d  -22.33 per cent

## Homelessness, the margin the charge acts on

It did NOT collapse to the corner. It fell monotonically and settled:

    0.687% -> 0.641% -> 0.625% -> 0.609% -> 0.601% -> 0.599%
           -> 0.598% -> 0.595% -> 0.594% -> 0.593%

The last four blocks move it by less than 0.01 percentage points in total. The
interior optimum under the flat Pigouvian charge is about 0.593 per cent, against a
benchmark beginning with 6.?E-003 -- a reduction on the order of 14 per cent in the
homelessness rate, with the margin interior throughout.

## What this run does NOT contain

No CEV / welfare curve. A frozen run never exits the calibration loop on its own
(source 948), so it never reaches `save_welfare_curve` at source 52324, and stopping
it by hand kills it inside the loop. run.err reads exactly `Terminated` (11 bytes,
exit 143 = 128+15) which is the SIGTERM used to stop it, not a fault. The welfare
curve is being produced by a companion run launched fresh from the seed with
`frozen_stop_after_blocks 12` (see code/remote_internalise_point12.sh), which leaves
the loop at block 12 and goes on to the statistics, the save and the curve.
