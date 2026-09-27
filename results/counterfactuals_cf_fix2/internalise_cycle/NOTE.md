# Internalisation, no budget clearing (cf_fix2): STOPPED for cycling at pass 9

27 September, 09:55 to 12:37 UTC, remote container. NOT an equilibrium. Stopped under the
coordinator's cycle rule (18:15 amendment); rerun on `cf_fix2_damp` from the last price.

Command, from `code/`:
`OMP_NUM_THREADS=2 BUILD=cf_fix2 SEED_FROM=bench DIAG_TAG=_fix2 DRUG_PRICE_START=0.997 sh cf_runs/cf_arm.sh internalise`

## What it did

Period THREE, the same shape as permban85 on the undamped build (`../permban85_cycle`): b jumps
to 0.08106 on passes 5 and 8 and sits at 0.07961-0.07963 otherwise; the moments change is about
1.4e-3 on each jump and on the pass after it, and 1.6e-4 in between; the drug-market gap is
about 1.5e-2 on the jumps against 1.6-3.5e-3 otherwise. pi_V does not move in this arm (no budget
clearing), so the cycle is not a budget-instrument cycle. Last price 0.99636.

    pass  moments change  b
     1  1.628e+00  0.08295438
     2  1.045e-02  0.07908645
     3  7.700e-04  0.07919292
     4  4.408e-04  0.07963370
     5  1.422e-03  0.08105558
     6  1.438e-03  0.07961720
     7  1.561e-04  0.07960746
     8  1.448e-03  0.08105592
     9  1.438e-03  0.07961763

## Passes (`passes.txt`)

    pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV
      1  1.0018  0.06753    +2.1%    +2.1%    -3.0%  4.83e-02  0.00e+00   789.8605  +1.51%
      2  1.0006  0.06753    -2.7%    -2.7%    -2.5%  1.70e-02  0.00e+00   789.4939  +0.43%
      3  0.9956  0.06753    -2.5%    -2.5%    -2.3%  1.46e-02  0.00e+00   789.4044  +0.16%
      4  0.9949  0.06753    -2.0%    -2.0%    -2.2%  1.61e-03  0.00e+00   789.4012  +0.15%
      5  0.9965  0.06753    -0.2%    -0.2%    -2.2%  1.55e-02  0.00e+00   789.3704  +0.06%
      6  0.9962  0.06753    -2.0%    -2.0%    -2.2%  3.27e-03  0.00e+00   789.3920  +0.13%
      7  0.9951  0.06753    -2.0%    -2.0%    -2.2%  2.78e-03  0.00e+00   789.3966  +0.14%
      8  0.9966  0.06753    -0.2%    -0.2%    -2.2%  1.52e-02  0.00e+00   789.3699  +0.06%
      9  0.9964  0.06753    -2.0%    -2.0%    -2.2%  3.45e-03  0.00e+00   789.3919  +0.13%

## newborn_parent_share at the end of each pass

The disordered-housed share jumps to about 0.02790 on passes 6 and 9, ONE PASS AFTER b jumps
(5 and 8), and is about 0.02742 otherwise: here the share follows b with the one-pass lag, it
does not lead it.

    pass  clean housed  disordered housed  clean street  disordered street
     1  1.000000  0.000000  0.000000  0.000000
     2  0.968862  0.028516  0.001553  0.001069
     3  0.970165  0.027221  0.001564  0.001049
     4  0.970120  0.027262  0.001567  0.001052
     5  0.969949  0.027425  0.001566  0.001060
     6  0.969468  0.027900  0.001564  0.001068
     7  0.969955  0.027421  0.001565  0.001058
     8  0.969954  0.027422  0.001565  0.001059
     9  0.969465  0.027903  0.001564  0.001067
