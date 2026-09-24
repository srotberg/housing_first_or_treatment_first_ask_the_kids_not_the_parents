# omega_c = 0.06 -- FULL INTERNALISATION OF THE HOMELESSNESS EXTERNALITY

Run 2026-09-24 01:46Z to 2026-09-24 04:14Z, `sh code/remote_internalise_point.sh stage`
then `solve 0.9329`, frozen on the published two-class omega_c = 0 benchmark seed.
Reference: b = 0.098916, lambda_d = 0.043579.

`internalise_homelessness_cost = 1` turns kappa_x from `-kappa_x*H` with H the
AGGREGATE -- a constant inside every household's problem, shifting welfare levels and
moving no policy function -- into a FLAT kappa_x charged to any household that
CHOOSES the lowest housing grid point. Declared at source line 3688, applied at
28688 as `flow_utility_1=flow_utility_1-kappa_x` when
`future_housing_status_index_1==lowest_housing_grid_point`, deliberately AFTER
`flow_utility_goods_only` is recorded so the charge stays out of the drug
first-order condition. Both sites verified unchanged before the run.

kappa_x = 0.9329 is the income-basis value: the benchmark control's converged probe
reports 0.9329 on income and 0.6083 on consumption, and 0.6083/0.65201 = 0.93296
with s = aggregate_consumption/model_total_income = 0.65201. It raises the
calibrated 0.8139 by 14.62 per cent. Handover: 98 lines, all 98 ingested, including
`addiction_onset_base: 0.0000000000000000 -> 3.4509299932932086E-002`.
OMP_NUM_THREADS=2.

## THE BLOCK TABLE

Verbatim from `run.log`. Every block printed b, lambda_d and exactly one
`BUDGET bequest_residual`, so the pairing is 1:1 with no interpolation.
`y` is carried through because it is on the same line.

| block | b | lambda_d | bequest_residual | block_move | h_1 | y |
|---|---|---|---|---|---|---|
| 1 | 7.1098026061373346E-002 | 3.1144378905135835E-002 | 2.1228272555288870 | 1.0000000000000000 | 6.8710741839086448E-003 | 1.1458868172758896 |
| 2 | 8.4018769155587897E-002 | 3.5461117870651156E-002 | 1.8361440967148581 | 0.20616323657568172 | 6.4076885304465642E-003 | 1.3821265522748938 |
| 3 | 8.4923417103446308E-002 | 3.6152596556971492E-002 | 1.6328873366486207 | 8.5328034946797970E-002 | 6.2471712970331612E-003 | 1.5000606950283033 |
| 4 | 8.4065089862316686E-002 | 3.5930846581628914E-002 | 1.5642889922918679 | 3.9101797027572389E-002 | 6.0857230871332046E-003 | 1.5587157638543392 |
| 5 | 8.2631196496110032E-002 | 3.5455543885840518E-002 | 1.5084854328514625 | 1.8626674824120698E-002 | 6.0119037830127326E-003 | 1.5877494555308849 |
| 6 | 8.0730656893682001E-002 | 3.4947264391769019E-002 | 1.4869587190246965 | 2.3000267247945527E-002 | 5.9934924791487532E-003 | 1.6021584983011876 |
| 7 | 8.0030467171749609E-002 | 3.4213947776865115E-002 | 1.4623680954341500 | 2.0983519816693243E-002 | 5.9848753667856424E-003 | 1.6093210316797117 |
| 8 | 7.9614412136896767E-002 | 3.4053334139597102E-002 | 1.4580853864885828 | 5.1987080615181870E-003 | 5.9547156897888798E-003 | 1.6129425345222077 |
| 9 | 7.9311884107822972E-002 | 3.3896960539928224E-002 | 1.4543664966369221 | 4.5920202417726753E-003 | 5.9376517239772024E-003 | 1.6148067434259019 |
| 10 | 7.9358952915334569E-002 | 3.3849649273996897E-002 | 1.4528562860900192 | 1.3957377056151542E-003 | 5.9295673625692699E-003 | 1.6157606544236343 |

## WHY IT STOPPED

**The 0.5 per cent rule fired at block 10.** Not block 12, and not block_move.

    |b(9)  - b(8)| / b(8) = |0.079311884 - 0.079614412| / 0.079614412 = 0.3800%
    |b(10) - b(9)| / b(9) = |0.079358953 - 0.079311884| / 0.079311884 = 0.0593%

Two consecutive blocks under 0.5 per cent, so the run was stopped by hand at block
10 in accordance with the family rule. `block_move` never came near its own 1e-3
rule -- it was still 1.396e-3 at block 10 -- and was correctly not used. At block 8
it read 5.199e-3, essentially the benchmark's 0.00513, the value from which the
benchmark's own metric ROSE to 0.036 and never fired.

Independently confirmed by `python3 code/paper/calibration_report.py` on the log:
"10 moment blocks; this is loop 10, and it is within one per cent of loop 9:
b +0.1%  lambda_d -0.1%  theta -0.1%."

Last three b, for checking the arithmetic:

    block  8   0.079614412136896767
    block  9   0.079311884107822972
    block 10   0.079358952915334569

## HEADLINE OUTCOMES, MODEL UNITS, BLOCK 10

    b          total drug users     0.079358952915334569
    lambda_d   disorder rate        0.033849649273996897
    h_1        homelessness rate    0.0059295673625692699
    theta      drug spending share  0.53528206981865201
    tau_u      treatment take up    0.25190064023140868
    pi_eu      unemployment rate    0.056184460245911345
    y                               1.6157606544236343
    bequest_residual                1.4528562860900192

## AGAINST HOUSING FIRST AT omega_c = 0.06

    b    internalisation  0.079358953
         Housing First    0.081242
         difference       -2.32 per cent

    h_1  internalisation  0.0059295674
         Housing First    PENDING -- results/reference/hf_omega_c_006/RESULT.md does
                          not exist on the branch as of origin 3dc7bc0, so the
                          Housing First homelessness rate cannot be quoted here.

## AGAINST THE omega_c = 0 BENCHMARK

    b         -19.77 per cent   (0.098916 -> 0.079359)
    lambda_d  -22.33 per cent   (0.043579 -> 0.033850)

## NOT A CORNER

    h_1        0.005930   NOT zero, and approached from ABOVE by a monotone decline
                          0.687% -> 0.641% -> 0.625% -> 0.609% -> 0.601% -> 0.599%
                          -> 0.598% -> 0.595% -> 0.594% -> 0.593%
                          The last four blocks move it less than 0.01 percentage
                          points in total. The homelessness margin the charge acts
                          on stayed interior for the whole run.
    b          0.079359   ~4/5 of benchmark, not zero
    pi_eu      0.056184   unemployment normal, against a 0.049 target

Block 1 was the restart transient and NOT the answer: bequest_residual 2.1228 and b
-28.1 per cent against benchmark, settling to residual 1.4529 and -19.77 per cent.
The converged residual sits 0.10 per cent above the converged omega_c = 0.06
reference of 1.45135, and below the benchmark's 1.4771. This repeats the family's
omega_c = 0.07 pattern (-28.06 per cent at residual 2.1197, settling -18.65 at
1.4496) almost exactly.

## CEV

**NOT AVAILABLE, AND CANCELLED BY THE AUTHOR.** A frozen run never exits the
calibration loop (source 948), so it never reaches `save_welfare_curve` (52324);
stopping at the family rule kills it inside the loop. `run.err` contains exactly
`Terminated` -- the SIGTERM used to stop it at block 10, exit 143 = 128+15 -- not a
fault. A companion run (`code/remote_internalise_point12.sh`, fresh from the seed
with `frozen_stop_after_blocks 12`, which leaves the loop at block 12 and reaches
the curve) was launched and reached block 4, reproducing this run's blocks 1-4 to
about 1e-4; it was stopped when the author cancelled the CEV for this point. It
wrote no welfare_curve file and logged zero KAPPA_X PROBE lines, both verified.

That companion run also measured this model's reproducibility: two runs identical
but for `frozen_stop_after_blocks` differ by 3e-5 to 2.4e-4 on b, lambda_d and h_1,
fluctuating without compounding. A 1e-4 relative agreement test is therefore AT OR
BELOW this model's own noise floor and cannot by itself distinguish one equilibrium
from another.
