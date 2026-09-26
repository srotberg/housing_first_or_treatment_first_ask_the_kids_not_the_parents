# Steady-state counterfactual runs on the corrected build

These are the scripts the 26 September runs use, committed so that another
container can reproduce them. Checked on commit: `build_cf_fix.sh` then
`build_cf_fix2.sh` regenerate, byte for byte, the source the running TF arms
were compiled from.

The build is `cf_fix2` (`cf_fix2_permban` for the permanent ban). Against the
tracked source it:

- solves the population distribution fully in every pass: at least 70 sweeps
  (more than one lifetime), then until the change is below 5e-5
  (`code/CALIBRATION_STATE.md`, 26 September 02:30 and 03:20);
- keeps the benchmark's labour tax: the hard-coded tax warm starts are
  neutralised (`code/ENGINE.md`, 26 September 10:00, the hidden tax);
- clears the budget to 1e-3 with pi_V, whose step starts at 0.12 of the gap,
  ignores pass 1 and halves on every sign change;
- seeds the distribution from a finished run (`SEED_FROM`).

## Order

    cd code
    bash cf_runs/build_cf_fix.sh                  # code/cf_fix, three builds
    PERMBAN=1 bash cf_runs/build_cf_fix.sh        # code/cf_fix_permban
    bash cf_runs/build_cf_fix2.sh                 # code/cf_fix2
    PERMBAN=1 bash cf_runs/build_cf_fix2.sh       # code/cf_fix2_permban

Build SEQUENTIALLY, and never while a solve is running. Expect 7 warnings and
0 errors in each of the three builds.

Then an arm, for example Treatment First at 85 per cent detection:

    OMP_NUM_THREADS=2 BUILD=cf_fix2 SEED_FROM=bench PDET=0.85 DIAG_TAG=_x \
      PV_START=0.082 DRUG_PRICE_START=0.867 NET_TARGET=6.0370824602930142 \
      sh cf_runs/cf_arm.sh tf > cfarm_tf_x.out 2>&1

The first arm in a fresh container runs STAGE 1, the 12-block benchmark in
`code/cfarm_bench` (about 2.5 hours), and every later arm reuses it. Arms are
`tf`, `omega1`, `internalise` and `null`. The optional settings are
`SUPPLY_ELAST` (refits the supply level, see `code/ENGINE.md`), `PV_START`,
`DRUG_PRICE_START` and `NET_TARGET`.

`NET_TARGET` 6.0370824602930142 is the no-policy run's net revenue on this
build against this benchmark (`results/counterfactuals_cf_local/null_fix`). A
re-solved benchmark must reproduce the saved one
(`results/counterfactuals_cf_local/bench/bench.log.gz`, final
`average_welfare_with_childhood` 789.34893176009462) before that target is used.
If it does not, run `null` first and use its final net revenue.

A run is accepted only if its `.out` file ends with `DIST CHECK PASS`, and also
with `TARGET CHECK PASS` for `tf` or `VOUCHER CHECK PASS` for the arms that
don't clear the budget.

## Reading a run

    python3 cf_runs/passes.py cfarm_<arm><tag>/cf.log "$(pwd)/cf_runs/cev.py"

This prints one row per pass: price, pi_V, the changes in drug use, SUD and
homelessness, the drug-market and budget gaps, welfare and CEV. CEV is read off
`results/reference/hf_omega_c_006/welfare_curvebaseline_benchmark.dat`.

## Limits

Each solve holds about 4.9 GB, so run at most two at once on 16 GB. An arm's
directory grows to about 4.7 GB, most of it when the value functions are
written at the end. Write the `RESULT.md` first, then free the directory.
