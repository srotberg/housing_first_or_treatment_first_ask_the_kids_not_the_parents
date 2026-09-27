# Treatment First 70 per cent, DAMPED build (cf_fix2_damp): STOPPED at pass 12, the two-pass flip returned

27 September, 03:39 to 09:43 UTC, remote container. NOT an equilibrium. Stopped under the brief's
rule (record, stop, do not improvise): the damped build is the cycle rule's remedy and it did not hold.

Command, from `code/` (relaunched after the 03:30 container restart from the last printed pi_V and
price of `../tf70_remote_partial`, which had reached pass 8 with the same behaviour):
`OMP_NUM_THREADS=2 BUILD=cf_fix2_damp SEED_FROM=bench PDET=0.70 DIAG_TAG=_damp70 PV_START=0.08011 DRUG_PRICE_START=0.8734 NET_TARGET=6.0373408770945769 sh cf_runs/cf_arm.sh tf`

## What it did

Passes 3-6 were clean and monotone, and the moments rule was met at pass 6 (5.3e-5) -- which is
as far as the coordinator's damped run got (`../tf70_damp_partial`, lost at pass 7) -- but the
budget had not cleared (3.1e-3), so the run went on. From pass 7 the flip is back: b jumps to
0.05816-0.05818 on passes 7, 10 and 12 and returns to 0.05780-0.05781 in between, the moments change
is 3.7e-4 on every jump and its return (5.5e-6 at pass 9), and from pass 9 it is period two. The
drug-market gap spikes with b (3.0-3.7e-3 on the high passes, 3e-4-7e-4 on the low). The budget is
inside its rule at passes 10 and 12 (1.3e-4, 4.6e-4), so pi_V is not what moves.

The size is the coordinator's undamped TF 70 cycle again (`../tf70_cycle`: b -28.4 / -28.9 per
cent, moments change stuck at 3.6e-4); here -28.4 / -28.9 per cent and 3.7e-4.

    pass  moments change  b
     1  1.628e+00  0.05841380
     2  7.089e-03  0.05763981
     3  3.999e-04  0.05763647
     4  1.971e-04  0.05772901
     5  1.072e-04  0.05777402
     6  5.337e-05  0.05778936
     7  3.736e-04  0.05816299
     8  3.632e-04  0.05779983
     9  5.463e-06  0.05780530
    10  3.717e-04  0.05817702
    11  3.695e-04  0.05780752
    12  3.682e-04  0.05817572

## Passes (`passes.txt`)

    pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV
      1  0.8744  0.08011   -28.1%   -28.8%    +4.2%  1.04e-02  9.61e-02   790.2125  +2.58%
      2  0.8742  0.08011   -29.1%   -29.7%    +4.5%  3.18e-03  9.54e-03   789.9250  +1.71%
      3  0.8731  0.08126   -29.1%   -29.7%    +4.2%  2.82e-03  3.80e-03   789.9407  +1.76%
      4  0.8730  0.08103   -29.0%   -29.6%    +4.3%  1.51e-04  4.71e-03   789.9104  +1.66%
      5  0.8730  0.08074   -28.9%   -29.6%    +4.5%  2.30e-04  3.94e-03   789.8884  +1.60%
      6  0.8731  0.08051   -28.9%   -29.5%    +4.7%  2.97e-04  3.13e-03   789.8733  +1.55%
      7  0.8734  0.08032   -28.4%   -29.1%    +4.8%  3.72e-03  1.80e-03   789.8513  +1.49%
      8  0.8734  0.08021   -28.9%   -29.5%    +4.7%  3.58e-04  1.82e-03   789.8557  +1.50%
      9  0.8733  0.08010   -28.9%   -29.5%    +4.8%  2.76e-04  1.43e-03   789.8507  +1.49%
     10  0.8736  0.08002   -28.4%   -29.1%    +4.9%  3.49e-03  1.34e-04   789.8355  +1.44%
     11  0.8736  0.08001   -28.9%   -29.5%    +4.9%  7.36e-04  9.64e-04   789.8453  +1.47%
     12  0.8739  0.07995   -28.4%   -29.1%    +4.9%  3.00e-03  4.56e-04   789.8321  +1.43%

## newborn_parent_share at the end of each pass

The damped share alternates too, in step with b but with about half its relative amplitude
(disordered housed 0.019054 / 0.019112 / 0.019074, about 0.3 per cent, against 0.6 per cent in b).
Whether it drives the flip or follows it is not established here.

    pass  clean housed  disordered housed  clean street  disordered street
     1  1.000000  0.000000  0.000000  0.000000
     2  0.977699  0.019263  0.001528  0.001511
     3  0.977842  0.019123  0.001531  0.001503
     4  0.977921  0.019051  0.001527  0.001500
     5  0.977941  0.019033  0.001526  0.001499
     6  0.977942  0.019030  0.001528  0.001500
     7  0.977937  0.019033  0.001530  0.001501
     8  0.977866  0.019098  0.001532  0.001505
     9  0.977896  0.019067  0.001534  0.001503
    10  0.977908  0.019054  0.001535  0.001503
    11  0.977846  0.019112  0.001536  0.001506
    12  0.977885  0.019074  0.001537  0.001504
