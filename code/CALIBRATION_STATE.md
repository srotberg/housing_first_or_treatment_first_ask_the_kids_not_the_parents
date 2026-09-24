# IN FLIGHT, 24 September 22:10: v3 for tf and omega1; v2 is kept for internalise only

- session_012k9WecRrXzogSi5ZtEuDRN (v3) runs the benchmark, then tf, then omega1,
  at drug_market_adjuster 0.1, to results/counterfactuals_cf_v3/<arm>/.
- session_011HE2FoD9oEfGDmCFwFg9gx (v2) runs at the declared adjuster 0.2.
  Its internalise arm is fine, because the price barely moves there (0.991).
  ARCHIVE v2 AS SOON AS results/counterfactuals_cf_v2/internalise/ IS PUSHED,
  before its omega1 and tf run at 0.2.
- The first tf run (session_01LxhTRbB5QNDAeLqvVag69e) runs at 0.2 and started
  its price at 0.6. When it pushes, read its price path. It gives the tf
  clearing price and shows whether the run cycled; do not report its numbers
  unless the movement decayed into the stop.

# IN FLIGHT, 24 September 20:40: counterfactuals v2, one benchmark and three arms

- session_011HE2FoD9oEfGDmCFwFg9gx runs remote_cf_arm.sh: the HF omega_c = 0.06
  benchmark once (cfarm_bench), then internalise, omega1 and tf, each carrying
  the benchmark's voucher probability 0.067533863251354. Results go to
  results/counterfactuals_cf_v2/<arm>/. Expected: internalise about 01:00 UTC,
  the other two a few hours after.
- The first internalise arm (results/counterfactuals_cf/internalise/) ran at the
  declared 0.06 and is superseded. The first omega1 arm had the same fault and
  was archived before it finished.
- The first tf arm (session_01LxhTRbB5QNDAeLqvVag69e) is still running. pi_V is
  its budget instrument, so the start value washes out at convergence. Check its
  stage-1 b: its benchmark stage ended after about 50 minutes, where the others
  took 2.5 to 4 hours.

# THE REDO RUNS THE WAY THE OLD ARMS DID, 24 September 16:55

The author: *"the budget clearing in rationed TF is done with pi_v and in the
omega_c=1 case and internlization case for homelessness there is no budget
clear"*, and chose the old counterfactual build over patching the frozen one.

The market-clearing pilot on the frozen build was archived: that setup zeroes
voucher_probability_adjuster, so pi_V could not clear the budget.

`code/remote_cf_arm.sh tf|omega1|internalise`, one container per arm:

    STAGE 1  Housing First omega_c = 0.06 benchmark on the TRACKED source,
             12 blocks into save_welfare_curve, in the arm's own directory.
             Its full saved files were lost with the reference container, and
             the counterfactual binary reads them.
    STAGE 2  the arm on build_cf.sh's binary (is_counterfactual=1,
             use_revenues_to_increase_voucher_probability=1), in the same
             directory.

Checked in the source before writing it:
- the drug price clears in clear_drug_market's counterfactual branch against the
  benchmark's own shifter, drug_supply_shifterbaseline_benchmark.dat;
- adjust_taxes 1 plus use_revenues=1 sets tax_system_type 3 (53091), so pi_V
  moves with gain 0.05 and the tax does not. adjust_taxes 0 gives no budget
  clearing. That is tf, and omega1/internalise, respectively;
- upload_vars imports the median income, the labour income profile, the net
  revenue constraint and the rest from the benchmark's saved files. So the
  STALE CONSTANT declarations are overwritten before use, and no Fortran edit
  is needed; I told the author otherwise and corrected it;
- inc = 1 (applicants tested) takes the file-name branch 'counter_arm', and
  old_results is still 'baseline_benchmark', so every arm reads the right files.

A relaunch skips stage 1 when BENCH_DONE and the benchmark files are on disk.

