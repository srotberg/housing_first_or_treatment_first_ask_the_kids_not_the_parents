# Treatment First 85 per cent, permanent ban, DAMPED build (cf_fix2_damp_permban): STOPPED, still cycling

27 September, 03:40 to 07:47 UTC, remote container. NOT an equilibrium. The permban85 arm has now
cycled on both builds; the damped build, the cycle rule's remedy, did not remove it. Stopped
under the brief's rule (anything wrong: record, stop the arm, do not improvise).

Command, from `code/` (relaunched after the 03:30 container restart from the last printed pi_V
and price of the first damped attempt, `../permban85_damp_partial`, which had started from the
undamped run's last pass, `../permban85_cycle`):
`OMP_NUM_THREADS=2 BUILD=cf_fix2_damp_permban SEED_FROM=bench PDET=0.85 DIAG_TAG=_damp_permban85 PV_START=0.09198 DRUG_PRICE_START=0.8602 NET_TARGET=6.0370824602930142 sh cf_runs/cf_arm.sh tf`

## What it did

Passes 2-4 were a shrinking start-up swing (moments change 7.1e-3, 3.5e-3, 9.3e-4) and pass 5
reached 1.15e-4, just above the 1e-4 rule. From pass 6 it flips with period TWO: b alternates
0.05687 / 0.05590 / 0.05687, the moments change is stuck at 9.6e-4 three passes running, and the
drug-market gap alternates 1.1-1.3e-2 / 3.3-3.5e-3. The budget cleared (7.2e-4 at pass 8, the
rule is 1e-3), so pi_V is not what moves; the flip is in the drug market and the moments.

    pass  moments change  b
     1  1.628e+00  0.05705922
     2  7.071e-03  0.05334552
     3  3.470e-03  0.05681521
     4  9.300e-04  0.05588524
     5  1.154e-04  0.05589389
     6  9.735e-04  0.05686736
     7  9.633e-04  0.05590401
     8  9.637e-04  0.05686768

## Passes (`passes.txt`)

    pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV
      1  0.8618  0.09198   -29.8%   -30.5%    +5.4%  1.59e-02  9.18e-02   790.4587  +3.33%
      2  0.8591  0.09198   -34.3%   -35.1%    +3.6%  2.70e-02  7.41e-03   790.3573  +3.02%
      3  0.8599  0.09109   -30.1%   -30.8%    +5.9%  1.16e-02  8.69e-03   790.1091  +2.26%
      4  0.8597  0.09161   -31.2%   -32.0%    +5.8%  3.86e-03  9.95e-04   790.1265  +2.32%
      5  0.8583  0.09167   -31.2%   -32.0%    +5.8%  3.52e-03  7.02e-04   790.1192  +2.29%
      6  0.8596  0.09165   -30.0%   -30.8%    +6.0%  1.32e-02  1.06e-05   790.0924  +2.21%
      7  0.8593  0.09165   -31.2%   -32.0%    +5.8%  3.34e-03  2.81e-03   790.1094  +2.26%
      8  0.8605  0.09157   -30.0%   -30.8%    +6.0%  1.14e-02  7.18e-04   790.0839  +2.19%

Undamped (`../permban85_cycle`), the same arm flipped with period three and an amplitude of
about 1.1e-3 in b; damped, period two with about 1e-3. The parent share alternates
too but by much less: its disordered-housed entry, the one the damping acts on, is 0.018668 /
0.018656 / 0.018815 / 0.018734 over passes 5-8, about 0.5 per cent, against about 1.7 per cent in
b. The swing shows most in the drug market (gap alternating 1.1-1.3e-2 / 3.3-3.5e-3, price moving
about 0.1 per cent a pass). Whether the share drives the flip or follows it is not established. Diagnosing
it is the coordinator's call; no further build was tried here.

## newborn_parent_share at the end of each pass

    pass  clean housed  disordered housed  clean street  disordered street
     1  1.000000  0.000000  0.000000  0.000000
     2  0.977865  0.019045  0.001553  0.001537
     3  0.978533  0.018429  0.001549  0.001488
     4  0.978244  0.018691  0.001556  0.001509
     5  0.978262  0.018668  0.001558  0.001512
     6  0.978271  0.018656  0.001558  0.001514
     7  0.978103  0.018815  0.001559  0.001523
     8  0.978187  0.018734  0.001559  0.001520
