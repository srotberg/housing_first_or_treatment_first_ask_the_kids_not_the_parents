# Treatment First 85 per cent, permanent ban (cf_fix2_permban): STOPPED for cycling at pass 10

26 September, 17:56 to 23:10 UTC, remote container. NOT an equilibrium: stopped under the
coordinator's cycle rule (18:15 amendment), to be rerun on `cf_fix2_damp_permban`.

Command, from `code/`:
`OMP_NUM_THREADS=2 BUILD=cf_fix2_permban SEED_FROM=bench PDET=0.85 DIAG_TAG=_permban85 PV_START=0.082 DRUG_PRICE_START=0.867 NET_TARGET=6.0370824602930142 sh cf_runs/cf_arm.sh tf`

## Why stopped

The CF MOMENTS change stayed above 1e-4 for passes 8-10 (1.39e-4, 1.10e-3, 1.09e-3) while b
went down, up, down. Over passes 5-10 the pattern is period THREE rather than two -- b is
0.05595 / 0.05714 / 0.05597 / 0.05596 / 0.05706 / 0.05597 -- and the moments change jumps
to about 1.1e-3 on each spike and on the pass after it (6-7, 9-10), so it was not settling. The budget cleared
to 6.2e-4 at pass 10 but the moments rule (1e-4) never held.

    pass  moments change  b
     1  1.629e+00  0.05717450
     2  6.997e-03  0.05611731
     3  2.891e-03  0.05322620
     4  2.688e-03  0.05591417
     5  3.593e-04  0.05594914
     6  1.186e-03  0.05713542
     7  1.170e-03  0.05596507
     8  1.393e-04  0.05595540
     9  1.101e-03  0.05705650
    10  1.091e-03  0.05596519

## Passes (`passes.txt`)

    pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV
      1  0.8675  0.08200   -29.6%   -30.3%    +9.1%  5.22e-03  1.52e-01   790.0729  +2.15%
      2  0.8661  0.08200   -30.9%   -31.6%    +9.3%  1.44e-02  6.69e-02   789.7932  +1.31%
      3  0.8626  0.09002   -34.5%   -35.1%    +4.4%  3.53e-02  7.53e-03   790.2189  +2.60%
      4  0.8615  0.08957   -31.2%   -31.9%    +6.3%  7.83e-03  1.41e-02   790.0436  +2.07%
      5  0.8591  0.09000   -31.1%   -31.9%    +6.2%  6.16e-03  6.81e-03   790.0514  +2.09%
      6  0.8605  0.09020   -29.7%   -30.4%    +6.7%  1.42e-02  7.68e-03   790.0211  +2.00%
      7  0.8602  0.09043   -31.1%   -31.9%    +6.1%  4.26e-03  2.20e-03   790.0579  +2.11%
      8  0.8586  0.09050   -31.1%   -31.9%    +6.1%  3.82e-03  3.41e-03   790.0644  +2.13%
      9  0.8601  0.09060   -29.8%   -30.5%    +6.5%  1.42e-02  5.04e-03   790.0393  +2.05%
     10  0.8598  0.09075   -31.1%   -31.9%    +6.0%  3.54e-03  6.17e-04   790.0700  +2.15%

Last pass: pi_V 0.09075, price 0.8598. The rerun starts there.
This arm ran against the coordinator's budget target 6.0370824602930142; this container's own
no-policy run gives 6.0373408770945769 (`../null_remote`).
