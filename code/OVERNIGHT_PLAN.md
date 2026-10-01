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

## A. b  -- DONE 10:13. b* = 0.0054222 (0.98x), drug users 10.54 per cent at convergence
## (block move 9.4e-4 < 1e-3 after 11 blocks), rule A.2(a). Five omega_c runs launched 10:13.

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
   two-class omega_c = 0 calibration. Not before b*'s own block 12 (the author, 03:06: "don't
   launch omegac>0 yet / first i want the b").
   WHEN NOT EVERY POINT HAS FINISHED (0.97x and 0.99x run at about 40 minutes a block, the
   other two at 20-23, so they finish about 13:30). A finished point is b* without waiting:
   (a) if its block-12 reading is within 0.10 points of 10.50 -- the author's own tolerance,
       "if you have a b that is very close to 10.5% that is enough"; or
   (b) if no unfinished point can still come closer: an unfinished point ABOVE 10.50 can fall,
       by up to 0.30 (the reference runs fall 0.25 in all from block 5 to 12), and one BELOW
       can rise, by up to 0.10 (no block of this scan after block 2 has risen more than 0.08);
       its latest gap less that margin must exceed the finished point's gap.
   Otherwise wait for it. (08:20 version used 0.30 both ways; refined 09:15 because a point
   below the target only comes closer by rising, which this scan has barely done.)
3. Launch five cloud sessions, ONE PER POINT, each running exactly
   `bash code/remote_omega_point.sh <w> <b*> 1.0 v3` with the v3 worker prompt, for
   w = 0.05, 0.055, 0.06, 0.065, 0.07. Tag omega-c-2c. Results land in
   results/b_scan_childsplit_v3/ (omega_<w>_b<b*>_ku1.0.moments.txt, bench_<w>_b<b*>_ku1.0/).
4. Report the b table to the author. Do NOT move theta (all-users drug share is reported).

THE WORKER PROMPT for every cloud run of remote_omega_point.sh (the v3 prompt), with <args> filled:
    You are a calibration worker. Your whole job is to keep ONE model solve going until it
    finishes. Do not edit any file. 1. From the repository root, run this command with the Bash
    tool's run_in_background=true and timeout 7200000, exactly as written (the repository's
    .claude/settings.json allows it): bash code/remote_omega_point.sh <args>. Never add nohup or
    '&'. The script starts the solve DETACHED from your call (it installs gfortran if missing,
    builds, solves 12 blocks, about 4.5 hours, then HOLDS its benchmark files for up to 8 hours
    until the main session asks for them or releases them), pushes a digest every 20 minutes,
    and your call only waits for it. 2. The call will be stopped at its 2-hour limit before the
    run ends. That is expected and does NOT stop the run. Whenever the call stops, or you are
    woken for any reason, run exactly the same command again the same way: it prints "attaching
    to the running solve" and waits again. Keep doing this until it prints "finished". If it ever
    prints "started detached" a second time, the solve was lost: say so in your report. 3. Then
    report the last lines it printed. Never report success for a run that did not finish.

## B. omega_c and the new benchmark  (trigger trig_014YcDCJiAHBL4BbJLncVXAz at 14:50, re-arming
## every 20 minutes; the five runs finish between about 14:45 and 18:30)

1. For each w: moment = users(omega_c = 0, b*) / users(w) - 1, final block, against 18.3 per
   cent; users(omega_c = 0, b*) = 0.10537369388677348. w* = the GRID POINT closest. Decide when
   all five have finished, or when two finished points adjacent on the grid bracket 18.3 (the
   moment rises with omega_c, so no unfinished point can be closer). The run at (b*, w*) is THE
   NEW BENCHMARK.
2. ITS BENCHMARK FILES ARE HELD IN ITS WORKER'S CONTAINER (since c3fbfd20; the tarred set is
   123 MB, over GitHub's limit). Commit an empty results/b_scan_childsplit_v3/send_bench_<w*>_b<b*>_ku1.0
   and push; within about 5 minutes the run pushes one .dat.gz per file to
   results/b_scan_childsplit_v3/bench_<w*>_b<b*>_ku1.0/files/ (about 123 MB). THEN commit
   release_<tag> for each of the other four (never release_all before the files have landed).
   bench.log.gz and PARAM_HANDOVER.bench.txt are already in bench_<tag>/. If the files do not
   arrive within 30 minutes (the hold lasts 8 hours from the solve's end), fall back to a STAGE 1
   solve in the arms (cf_arm.sh without BENCH_FROM, 4.5 hours).
3. kappa_x on the INCOME basis, as on 24 September: the log's first
   "KAPPA_X PROBE: IMPLIED kappa_x" (x = 0.2 per cent of consumption) times 1.5076 (= 0.9329
   / 0.6188, the income-over-consumption factor that set 0.9329). Record the figure.
4. New reference directory results/reference/hf_2c_omega_<w*>/ : bench.log.gz,
   PARAM_HANDOVER.bench.txt (kappa_x set to the new value) and files/ (the .dat.gz set), so
   cf_arm.sh BENCH_FROM can point at it.
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
