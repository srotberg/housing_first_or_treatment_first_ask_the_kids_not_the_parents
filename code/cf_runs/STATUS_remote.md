# Remote worker: five steady-state arms on the corrected build

Started 26 September. Container: 4 cores, 16 GB, 30 GB free disk.
gfortran was not installed in this container; installed from apt: GNU Fortran (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0.

| arm | status |
|---|---|
| permban85 | running (STAGE 2 since 17:56) |
| null_remote | DONE 19:30, pass 5, checks pass; net revenue 6.0373408770945769 (results/counterfactuals_cf_fix2/null_remote) |
| elast5_85 | running (launched 19:31, NET_TARGET 6.0373408770945769) |
| omega1 | pending |
| uniq85 | pending |
| internalise | pending |

## Log
- builds done (sequential, 14:40-14:48), every compile 7 warnings 0 errors:
```
cf_fix build_bounds.err warnings=7 errors=0 / build_snan.err warnings=7 errors=0 / build_prod.err warnings=7 errors=0
cf_fix_permban build_bounds.err warnings=7 errors=0 / build_snan.err warnings=7 errors=0 / build_prod.err warnings=7 errors=0
cf_fix2 build_bounds.err warnings=7 errors=0 / build_snan.err warnings=7 errors=0 / build_prod.err warnings=7 errors=0
cf_fix2_permban build_bounds.err warnings=7 errors=0 / build_snan.err warnings=7 errors=0 / build_prod.err warnings=7 errors=0
```
- permban85 (tf, cf_fix2_permban, PDET 0.85) launched; it runs STAGE 1, the 12-block benchmark in cfarm_bench. No other arm until BENCH_DONE.
- 17:56 STAGE 1 done. BENCHMARK CHECK: the per-block welfare reproduces to about 2e-7 but not 1e-7:

  | block | this container | coordinator (counterfactuals_cf_local/bench) |
  |---|---|---|
  | 1 | 784.49269992490645 | 784.49256322839938 |
  | 11 | 789.34768213467373 | 789.34753850639936 |
  | 12 (final) | **789.34923420870734** | **789.34893176009462** |

  final average_welfare_with_childhood relative difference 3.83e-7 (above 1e-7, below 1e-4);
  final probability_of_voucher 6.7533863251354007E-002 in both, identical.
  Under the coordinator's amended rule (b), 17:50: permban85 keeps running, and the second slot runs the
  no-policy arm first (cfarm_null_fix2, BUILD=cf_fix2, DRUG_PRICE_START=1.0). Its last net_govt_revenues=
  becomes NET_TARGET for elast5_85 and uniq85.
- 18:15 coordinator's second amendment (damped build for a cycling arm) pulled; a watcher checks every running arm for moments >1e-4 three passes running with b alternating.
- 19:30 null_remote finished: VOUCHER CHECK PASS, DIST CHECK PASS (5 passes). Final net_govt_revenues 6.0373408770945769, 2.58e-4 above the coordinator's 6.0370824602930142. This is NET_TARGET for elast5_85 and uniq85.
- 19:31 elast5_85 launched: `... SUPPLY_ELAST=5 DIAG_TAG=_elast5_85 PV_START=0.082 DRUG_PRICE_START=0.94 NET_TARGET=6.0373408770945769 sh cf_runs/cf_arm.sh tf`
