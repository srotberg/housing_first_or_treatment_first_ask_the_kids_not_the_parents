# Who stops, rule C (12 October): identical to rule A

code/deter_2c/run_whostops_C.sh: both impact runs on cf_fix2_treatC_impact (cf_fix2 + treat/patch_treatC.py, distribution
fixed at Housing First's benchmark; BUILD_USED confirms, and the MILBY SPLIT print that only the rule-C build carries is in
the log). The drug price and pi_V are held at Housing First's (1.0001082, 0.067533863), so no warm start applies.

Result: every number equals rule A's (results/whostops_2c) to all printed digits: of the tested (holders and offered) who
used under Housing First, 58.9 per cent of users without a SUD stop and 19.4 per cent of all users; among holders 53.2 and
6.0. Apart from the MILBY SPLIT lines and timings, the screen run's cf.log is identical to rule A's, line for line.

Why: rule C differs from rule A only for a household WITH the disorder (it may keep the voucher in treatment if it does not
use). On impact such a household cannot stop (a disorder ends only with recovery), and with the distribution held at
Housing First's the rule-C change at the distribution's screen call sites is never exercised, so the policy functions and
every statistic of this comparison are unchanged. The x_ws_* numbers are therefore the same under rule C.

Guards: the runs' .out files carry 'GUARD FAIL: distribution not solved ... []' (the distribution is fixed, so nothing is
swept) and, on the reference, the hand-carried pi_V 0.067533863 against the benchmark's 0.0675338633 (rounding of the
held value). Both are the design of the impact run and were present under rule A; run_whostops.sh never gated on them.
