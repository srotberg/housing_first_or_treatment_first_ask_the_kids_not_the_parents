# The two-class benchmark at omega_c = 0.085 (1 October)

The author, about 17:55 on 1 October: *"ok, so we will go with omega_c=0.085"*.

- Run: `bash code/remote_omega_point.sh 0.085 0.0054222 1.0 v3` on its own cloud machine
  (session_01XjWFNZPCFtgf2oiVPb3YYT), two child-penalty classes, frozen blocks with only
  omega_c's adjuster live, b* = 0.0054222 (stage A of code/OVERNIGHT_PLAN.md).
- Finished 19:15 UTC, exit 0, 10 moment blocks, last block move 5.5e-4 against a rule of 1e-3.
- Drug users 8.956 per cent; with the child's weight off (the b* run at omega_c = 0,
  results/b_scan_childsplit_v3/omega_0.0_b0.0054222_ku1.0.*) 10.537, so removing the weight
  raises use by 17.65 per cent against 18.34 in NSDUH 2024 (1/0.845 - 1).
- kappa_x on the income basis: the log's first KAPPA_X PROBE, IMPLIED 0.61968, times 1.5076
  (= 0.9329 / 0.6188, the income-over-consumption factor of 24 September) = 0.934236, against
  0.9329 before. PARAM_HANDOVER.bench.txt here carries it; the run's own handover does not.
- files/ holds the benchmark's *baseline_benchmark.dat set, one .dat.gz each, for
  cf_runs/cf_arm.sh BENCH_FROM.
