# Remote worker: five steady-state arms on the corrected build

Started 26 September. Container: 4 cores, 16 GB, 30 GB free disk.
gfortran was not installed in this container; installed from apt: GNU Fortran (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0.

| arm | status |
|---|---|
| permban85 | running (STAGE 2 since 17:56) |
| null_remote | running (launched 17:57, gives this container's budget target) |
| elast5_85 | pending (waits for null_remote's net revenue) |
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
