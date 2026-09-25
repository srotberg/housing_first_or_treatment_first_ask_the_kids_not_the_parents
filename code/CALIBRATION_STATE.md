# 25 September 04:50: omega1 restarted at drug_price_start 0.81

The omega1 arm started at 0.6. Pass 1 printed demand V = 1.91 (b = 0.157)
against supply 0.5014*0.6^1.46 = 0.238, so the price rose at the 0.5 per cent
cap, which is about 60 passes (10 hours) to anywhere near 0.8. The fixed-price
omega1 run had b = 0.0202 at p = 1, so demand there is about 0.12. The log-linear
demand through the two points has elasticity 5.4. Against supply elasticity 1.46
it clears at p^6.88 = 0.12/0.5014, so p = 0.81. Killed (pid 3063) and relaunched
with DRUG_PRICE_START=0.81 (task b14c0bziq). The same arithmetic puts TF near
0.79 (fixed-price b = 0.0154), about 54 passes from its 0.6 start.

# IN FLIGHT, 25 September 04:25: both remaining local arms from ONE local benchmark

- Local benchmark (code/cfarm_bench) done 04:15: b = 0.081255009769345327,
  -6.9e-5 against the reference; voucher probability 0.067533863251354.
  bench_files.tar.gz is 131 MB, over GitHub's 100 MB limit, which is why v2
  never pushed it. Deleted; the set lives in code/cfarm_bench only.
- Local internalise at adjuster 0.1 (task b3hj81odq), stage 2 since 04:15.
- Local omega1 at adjuster 0.1 (task b08fa7bn8), from the same benchmark, since
  04:24. Deleted code/trans_bench_to_tf (4.5 GB, the 21 September arm 3
  transition on the superseded model, results in results/transition/) to make
  disk room: one arm directory is 2.5 GB.
- v3 (session_012k9WecRrXzogSi5ZtEuDRN): tf at 0.1 since about 01:25. Archive
  it once tf is pushed; its omega1 duplicates the local one.

# IN FLIGHT, 25 September 01:35

- internalise v2 (results/counterfactuals_cf_v2/internalise/): the voucher
  check PASSED and stage-1 b is -1.8e-5 against the reference. At adjuster 0.2
  b sawtooths +/-0.65 per cent with the price (0.9949 to 0.9967), so its b
  change of -1.67 per cent is +/-0.6 pp. lambda_d -2.19 per cent and h_1 -2.50
  per cent are steady. bench_files.tar.gz was NOT pushed. v2 archived.
- THIS container: `remote_cf_arm.sh internalise` at adjuster 0.1. The 01:32
  launch used nohup and DIED when the turn ended (the container is suspended
  between firings); relaunched 01:43 as a harness background task (Bash
  run_in_background), which survives. Stage 1 started 01:43 in code/cfarm_bench (out: code/cfarm_internalise.out). The
  container restarted once (01:21), so check `uptime -s` each firing and
  relaunch the same line if it is newer than the launch. Push
  cfarm_bench/bench_files.tar.gz when stage 1 finishes.
- v3 (session_012k9WecRrXzogSi5ZtEuDRN): stage 1 passed; tf at 0.1 running
  since about 01:25, omega1 after it.

# PLAN, 24 September 22:25: ONE benchmark (v2's), every remaining arm run from it

The author: *"Wouldn't it be more efficient to run it once in this session and
use it for the other sessions??"* Yes. v2's benchmark finishes first. Its worker
pushes results/counterfactuals_cf_v2/bench/{bench_files.tar.gz,bench.log.gz}.
When those land, run tf and omega1 from them in THIS container:
`cd code && BENCH_FROM=../results/counterfactuals_cf_v2/bench sh remote_cf_arm.sh <arm>`
(4 cores, 16 GB; two arms at OMP 2 each; check the first arm's RSS before
starting the second). Then archive v3 (session_012k9WecRrXzogSi5ZtEuDRN), whose
own benchmark is a hedge only in case v2's tarball is over 40 MB and not pushed.

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

