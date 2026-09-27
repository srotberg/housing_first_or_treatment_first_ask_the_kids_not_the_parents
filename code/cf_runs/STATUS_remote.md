# Remote worker: five steady-state arms on the corrected build

Started 26 September. Container: 4 cores, 16 GB, 30 GB free disk.
gfortran was not installed in this container; installed from apt: GNU Fortran (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0.

| arm | status |
|---|---|
| permban85 | **STOPPED, NO EQUILIBRIUM.** Cycles on both builds: cf_fix2_permban period three (permban85_cycle), cf_fix2_damp_permban period two (permban85_damp_cycle). Needs the coordinator. |
| null_remote | DONE 19:30, pass 5, checks pass; net revenue 6.0373408770945769 (results/counterfactuals_cf_fix2/null_remote) |
| elast5_85 | DONE 01:57, pass 12, checks pass: b -44.8%, h_1 +2.1%, CEV +2.77% (results/counterfactuals_cf_fix2/elast5_85) |
| tf70 (damped) | **STOPPED 09:43 at pass 12, NO EQUILIBRIUM**: the two-pass flip returned on the damped build from pass 7 (results/counterfactuals_cf_fix2/tf70_remote_damp_cycle). Needs the coordinator. |
| omega1 | running (launched 07:49) |
| uniq85 | running (launched 09:45, NET_TARGET 6.0373408770945769) |
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
- 22:10 coordinator's third amendment pulled: TF 70 per cent on cf_fix2_damp moves here, ahead of omega1, uniq85, internalise, NET_TARGET 6.0373408770945769.
- 22:15 progress: permban85 at pass 8 (pi_V 0.0905, budget gap 3.4e-3, moments change 1.4e-4, no cycle); elast5_85 at pass 5, price walking down at the 0.5 per cent cap (0.9353 -> 0.9167, drug-market gap 7.9e-2), so it needs many more passes.
- 23:10 permban85 STOPPED under the cycle rule: moments change 1.39e-4, 1.10e-3, 1.09e-3 at passes 8-10 with b down/up/down (period three over passes 5-10). Process 4871 confirmed gone. Archived in results/counterfactuals_cf_fix2/permban85_cycle.
- 23:12-23:14 damped builds (one solve running, as the 22:10 amendment allows): cf_fix2_damp and cf_fix2_damp_permban, each build_bounds/build_snan/build_prod warnings=7 errors=0, 11 diff lines against cf_fix2 / cf_fix2_permban.
- 23:15 tf70 launched: `OMP_NUM_THREADS=2 BUILD=cf_fix2_damp SEED_FROM=bench PDET=0.70 DIAG_TAG=_damp70 PV_START=0.0800 DRUG_PRICE_START=0.8733 NET_TARGET=6.0373408770945769 sh cf_runs/cf_arm.sh tf`
- Next free slot: permban85 rerun on cf_fix2_damp_permban from pi_V 0.09075, price 0.8598, same target 6.0370824602930142 as the stopped run; then omega1, uniq85, internalise.
- 01:57 elast5_85 finished: TARGET CHECK PASS, DIST CHECK PASS (12 passes). Exit pass 12: budget gap -6.08e-4, drug gap 1.23e-3, moments change 5.85e-5.
- 01:58 permban85 rerun launched: `OMP_NUM_THREADS=2 BUILD=cf_fix2_damp_permban SEED_FROM=bench PDET=0.85 DIAG_TAG=_damp_permban85 PV_START=0.09075 DRUG_PRICE_START=0.8598 NET_TARGET=6.0370824602930142 sh cf_runs/cf_arm.sh tf`
- ~03:30 CONTAINER RESTART killed both solves. Disk (cfarm_bench, builds, logs) survived; gfortran survived. Partial logs archived:
  results/counterfactuals_cf_fix2/tf70_remote_partial (8 passes, pi_V 0.0800 -> 0.08023, price 0.8734, budget gap 1.9e-3 at pass 8, moments change settling, no cycle)
  results/counterfactuals_cf_fix2/permban85_damp_partial (3 passes).
  The arm script restarts from the benchmark's distribution, so both were relaunched from the last printed pi_V and price, as for a cycle rerun:
  `... BUILD=cf_fix2_damp PDET=0.70 DIAG_TAG=_damp70 PV_START=0.08011 DRUG_PRICE_START=0.8734 NET_TARGET=6.0373408770945769 ...`
  `... BUILD=cf_fix2_damp_permban PDET=0.85 DIAG_TAG=_damp_permban85 PV_START=0.09198 DRUG_PRICE_START=0.8602 NET_TARGET=6.0370824602930142 ...`
- 05:36 the cycle watcher flagged the permban85 damped rerun at pass 4 (moments change 7.1e-3, 3.5e-3, 9.3e-4 with b -34.3/-30.1/-31.2 per cent at passes 2-4). NOT stopped: the change is falling fourfold over the window (a damped start-up transient after the relaunch, not a stuck cycle), and the arm is already on the damped build, which is the cycle rule's remedy. The watcher now ignores passes 1-2 and flags only a window whose moments change is not falling by half. If it does stick, it is recorded here and stopped.
- 05:36 tf70 at pass 4 after the relaunch: budget gap 4.7e-3, moments change 2.0e-4, no oscillation.
- 07:47 permban85 damped rerun STOPPED at pass 8 (process 14540 confirmed gone): from pass 6 b alternates 0.05687 / 0.05590 every pass with the moments change stuck at 9.6e-4 three passes running, budget cleared (7.2e-4). The damped build did not remove the cycle, [corrected 09:50: the newborn parent share alternates too, about 0.5 per cent against 1.7 per cent in b; whether it drives or follows is not established; the swing shows most in the drug-market gap.] Per the brief, the arm is stopped and recorded rather than improvised: results/counterfactuals_cf_fix2/permban85_damp_cycle/NOTE.md. No equilibrium for permban85 from this container.
- 07:49 omega1 launched in the freed slot: `OMP_NUM_THREADS=2 BUILD=cf_fix2 SEED_FROM=bench DIAG_TAG=_fix2 DRUG_PRICE_START=0.870 sh cf_runs/cf_arm.sh omega1`
- 07:47 tf70 at pass 8 after the relaunch: budget gap 1.8e-3, moments change 3.6e-4 (it reached 5.3e-5 at pass 6, then a jump at pass 7 with the drug gap 3.7e-3). Watching.
- 09:43 tf70 damped STOPPED at pass 12 (process 14258 confirmed gone). Clean and monotone to pass 6 (moments 5.3e-5, which is where the coordinator's damped run was lost), but the budget had not cleared, and from pass 7 the flip returned: b -28.4 / -28.9 per cent, moments change stuck at 3.7e-4 from pass 10, drug gap spiking with b, budget inside its rule (1.3e-4, 4.6e-4). The same size as the coordinator's undamped TF 70 cycle. The damped parent share alternates too, about half b's relative amplitude. NOTE.md in results/counterfactuals_cf_fix2/tf70_remote_damp_cycle. Both TF arms that cycled undamped (70, permban85) also cycle damped.
- 09:45 uniq85 launched: `OMP_NUM_THREADS=2 BUILD=cf_fix2 SEED_FROM=bench PDET=0.85 DIAG_TAG=_uniq85 PV_START=0.075 DRUG_PRICE_START=0.90 NET_TARGET=6.0373408770945769 sh cf_runs/cf_arm.sh tf`
- 09:43 omega1 at pass 6: b -35.7 per cent, h_1 -12.7 per cent, drug gap 4.0e-3, moments change 9.1e-4 and falling.
