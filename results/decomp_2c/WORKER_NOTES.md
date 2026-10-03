# Worker notes: the two decompositions of Treatment First's long run (omega_c = 0.085)

Run by `code/extra_2c/remote_decomp_2c.sh`. First launch 2 Oct 22:00 UTC; the container restarted at about
23:45 UTC and killed both arms after their first pass, so the driver was rerun and both arms started again
from the shared benchmark at 23:46. Both finished at 02:52 UTC on 3 Oct ("decompositions done"). No GUARD
line was written, and no build failed.

## fixpv (pi_V held at its no-policy value)

- Every `probability_of_voucher=` the log prints (8 lines) equals the starting value: 6.7533863000000000E-002,
  i.e. 0.067533863. The arm reports "first printed 6.7533863E-002, last 6.7533863E-002".
- The drug price cleared: 0.85551291 at the start, 0.87427523 at the end.
- Ended by convergence: `loop_count` stops at 7, far below 250. The drug-market gap fell to 1.89e-04 on pass 7.
- DIST CHECK PASS: 7 passes, sweeps [71, 70, 72, 70, 70, 70, 70], largest final 4.55e-05 (rule 5e-05).
- Last pass line:

      pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV     V(chg)  V/user(chg)
        7  0.8742  0.06753   -27.1%   -28.8%   +13.2%  1.89e-04  0.00e+00   787.5597  +0.19%   -17.8%   +12.7%

## fixp (drug price held at its no-policy value)

- The drug price stayed at 1.0001082 throughout: all 15 `price_of_addictive_good=` lines print
  1.0001081999999999.
- The budget cleared: TARGET CHECK PASS, cleared against 5.8918410999830000. pi_V cleared it, moving from
  0.096152024 to 0.11459676.
- Ended by convergence: `loop_count` stops at 7, far below 250 and far below the loop-60 alarm. The budget gap
  fell to 5.52e-04 on pass 7.
- DIST CHECK PASS: 7 passes, sweeps [70, 70, 70, 70, 70, 70, 70], largest final 3.71e-05 (rule 5e-05).
- Last pass line:

      pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV     V(chg)  V/user(chg)
        7  1.0001  0.11453   -74.2%   -74.4%   -22.8%  0.00e+00  5.52e-04   791.6756  +13.11%   -77.8%   -14.0%

The pass-7 pi_V column reads 0.11453; the log's last print, 0.11459676, is the value after pass 7's update.
