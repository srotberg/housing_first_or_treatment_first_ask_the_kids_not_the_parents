# OVERNIGHT PLAN, 1 October -- the author's instruction, run without them

The author, 1 October ~04:00 UTC: *"overnight, i need you to finish getting the omega_c>0
calibration when im not here. i want to wake up to it calibrated and the paper updated with
the new calibrated numbers. Then you can launch the estimate kappa_x, simulate the optimal
sud, and optimal homelessness, and ratioed TF like we had before. And also launch a
transition after with T=60. you should write this plan so it moves automatically"*; *"if you
have a b that is very close to 10.5% that is enough"*; *"all the omega_c runs should run each
on a separate machine"*; TF *"should include 85% [detection] and tests costs. and exclusion
for an average of 3 years. like we did before"*.

Every step below is executed by a self-addressed check-in in this session (send_later /
the trigger trig_014YcDCJiAHBL4BbJLncVXAz). Each check-in reads this file, does the first
step whose inputs exist and whose outputs do not, records it in CALIBRATION_STATE.md,
commits, pushes, and re-arms the next check-in. Nothing here needs the author.

THE MODEL is the TWO-CLASS one (child_penalty_classes = 2, compiled in), one discount
factor, kappa_uem = 1, the child in the drug split, the build bench_tdm_childsplit (rule 5e-5,
at least 70 sweeps, 12 frozen blocks). The b scan running since 03:01 is already it.

## A. b  (10:15 UTC, trigger trig_014YcDCJiAHBL4BbJLncVXAz; was 07:45)

RE-TIMED 05:45. The eight 03:04 workers' solves were killed at the 2-hour tool-call limit
after 5 blocks (the setsid child stayed a child of the waiting call; fixed be8ec376, tested
here). Relaunched at 05:43 on the fixed script, four points only, those that bracket 10.5 per
cent at block 5 (0.96x 11.64, 0.97x 11.17, 0.98x 10.79, 0.99x 10.35; the reference runs fall
another 0.2 to 0.25 points from block 5 to block 12): sessions tagged b-scan-childsplit-v3,
results in results/b_scan_childsplit_v3/. Archiving the old 0.98x and 0.99x workers was
refused, so they and 0.995x / 1.0x restart on their own at about 07:05 into
results/b_scan_childsplit/; they finish about 11:40 and are not needed to pick b.

1. Read results/b_scan_childsplit_v3/omega_0.0_b*_ku1.0.moments.txt (four points), block 12:
   drug users (MOMENT b), SUD, users' income, SMI share of the homeless, and from the gz log
   "DIAG drug share, all users, sum spend / sum income".
2. b* = the GRID POINT whose block-12 drug users is closest to 10.50 per cent. No
   interpolation and no confirming run (the author: "very close is enough"). Its run IS the
   two-class omega_c = 0 calibration. Not before block 12 (the author, 03:06: "don't launch
   omegac>0 yet / first i want the b").
3. Launch five cloud sessions, ONE PER POINT, each running exactly
   `bash code/remote_omega_point.sh <w> <b*> 1.0 v3` with the v3 worker prompt, for
   w = 0.05, 0.055, 0.06, 0.065, 0.07. Tag omega-c-2c. Results land in
   results/b_scan_childsplit_v3/ (omega_<w>_b<b*>_ku1.0.moments.txt, bench_<w>_b<b*>_ku1.0/).
4. Report the b table to the author. Do NOT move theta (all-users drug share is reported).

## B. omega_c and the new benchmark  (~15:00 UTC, when the five are done; was 12:30)

1. For each w: moment = users(omega_c = 0, b*) / users(w) - 1, block 12, against 18.3 per
   cent. w* = the GRID POINT closest. The run at (b*, w*) is THE NEW BENCHMARK.
2. Its files are in results/b_scan_childsplit_v3/bench_<w*>_b<b*>_ku1.0/ (bench_files.tar.gz,
   bench.log.gz, PARAM_HANDOVER.bench.txt -- remote_omega_point.sh saves them since 1 Oct).
   If that directory is missing (the run predates the change), fall back to a STAGE 1 solve
   in the arms (cf_arm.sh without BENCH_FROM, 4.5 hours).
3. kappa_x on the INCOME basis, as on 24 September: the log's first
   "KAPPA_X PROBE: IMPLIED kappa_x" (x = 0.2 per cent of consumption) times 1.5076 (= 0.9329
   / 0.6188, the income-over-consumption factor that set 0.9329). Record the figure.
4. New reference directory results/reference/hf_2c_omega_<w*>/ : the three files above,
   with kappa_x in PARAM_HANDOVER.bench.txt set to the new value.
5. Paper: point code/paper/calib_tables.py BENCH at it, and the omega_c moment's omega_c = 0
   reading (B_OFF) at the b* run's block-12 users; `calib_tables.py --freeze`; strip red is
   NOT done (the author reads red); splice (numbers that moved print red); build with
   -jobname=children_first_housing_later; check_numbers / check_acronyms / check_hyphens /
   check_red; commit, push, fast-forward main, send the PDF. Section 6 keeps its numbers
   until D.
6. The gaps table for the new benchmark goes to the author with the PDF.

## C. counterfactuals  (right after B)

Common settings, every arm: BUILD=cf_fix2, BENCH_FROM=<abs path of the new reference dir>,
BENCH_B=<b*> BENCH_OMEGA=<w*> BENCH_KU=1.0 KAPPA_X=<new kappa_x>, OMP_NUM_THREADS=2.
A fresh container first builds: `cd code && bash cf_runs/build_cf_fix.sh && bash
cf_runs/build_cf_fix2.sh` (7 warnings, 0 errors each; checked against today's source on
1 October). Accept an arm only if its .out ends with DIST CHECK PASS and TARGET CHECK PASS
(tf) or VOUCHER CHECK PASS (the others).

1. CLOUD, one session each: `sh cf_runs/cf_arm.sh omega1` (optimal SUD: the parent counts
   the child fully) and `sh cf_runs/cf_arm.sh internalise` (optimal homelessness: the
   homeless bear kappa_x). Results to results/counterfactuals_2c/<arm>/.
2. HERE, in sequence: `sh cf_runs/cf_arm.sh null` (no policy: its final net revenue is the
   budget target), then `PDET=0.85 NET_TARGET=<null's net revenue> PV_START=0.082
   DRUG_PRICE_START=0.867 sh cf_runs/cf_arm.sh tf` -- rationed Treatment First: every holder
   tested, detection 85 per cent, no false positives, test cost charged, exclusion with
   release rate 1/3 (three years on average), pi_V clears the budget, the drug price clears.
   Keep its directory: it is the transition's terminal state.

## D. Section 6

As each arm is accepted: export_results.py (it runs export_elasticity, export_longrun and
transition_figure after it), splice, build, checkers, commit, push, send.

## E. the T = 60 transition  (after C.2's TF 85 is accepted)

Here, from TF 85's terminal state and the no-policy run's newborn parent share, with the
tr60_fix build and stage_transition.sh (HANDOVER set to the new benchmark's), 4 threads,
alone on the machine (~9.8 GiB peak). As on 26 September: a flat no-reform control first if
the build changed, then the TF 85 path. Then transition_figure.py and Section 6.3.

## Check-ins

Every 90 minutes from 07:45 until E is running, then every 3 hours. Each one: fetch, guard
(ENGINE.md unchanged, processes, memory, disk), advance the plan, record, push, re-arm.
A worker that died is relaunched by the same command (remote_omega_point.sh attaches to a
solve that is alive, which since be8ec376 survives the call's limit, or restarts from the
seed). A local run killed by a container restart restarts
from the beginning of its stage, never from a saved block state (lesson of 30 September).
