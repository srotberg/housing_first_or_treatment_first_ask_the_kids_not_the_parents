# Remote worker: five steady-state arms on the corrected build

Started 26 September. Container: 4 cores, 16 GB, 30 GB free disk.
gfortran was not installed in this container; installed from apt: GNU Fortran (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0.

| arm | status |
|---|---|
| permban85 | launched 14:5x, STAGE 1 running |
| elast5_85 | pending |
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
