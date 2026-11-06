# omega_c = 1, stages 2 and 3: the worker prompts

The prompts for the cloud workers of code/OMEGA1_PLAN.md's stages 2 and 3, in the form of the v3 prompt in
code/OVERNIGHT_PLAN.md ("THE WORKER PROMPT"). Fill `<b>` with the benchmark's b exactly as its directory spells it
(`results/omega1_2c/bench_1.0_b<b>_ku1.0`, e.g. 0.00479 or 0.00482), `<p>` with detection rates, `<column>` with one of
null, fixboth, fixp, fixpv, tf. Launch a worker only once the benchmark's `files/` are on the branch (send_bench_<tag>
committed and the files pushed); both scripts stop with a GUARD line otherwise.

The settings go after the script's own arguments as `OMEGA1_B=<b>` and `OMEGA1_PDET=<p>`, so every command starts with
`bash code/omega1/` (see "The permission rule" below).

## Stage 2: the detection rate (run_whostops_omega1.sh)

One worker per set of rates; two rates per worker run side by side (the reference about 30 minutes, then each pair about
40 minutes, as on 13 October). The calibrated share is the third column of the results' scan.txt and the first number of
each "detection" line: ALL tested users who stop, against Mehay and Pacula's 61.

    You are a calibration worker. Your whole job is to keep ONE model run going until it finishes. Do not edit any
    file. 1. From the repository root, run this command with the Bash tool's run_in_background=true and timeout
    7200000, exactly as written: bash code/omega1/run_whostops_omega1.sh <p> <p> OMEGA1_B=<b>. Never add nohup or
    '&'. The script starts the run DETACHED from your call (it installs gfortran if missing, builds, runs Housing
    First's reference on the omega_c = 1 benchmark and then the screen at each detection rate, about an hour and a half
    for two rates), pushes a digest every 20 minutes to results/whostops_omega1_pts_<rates>/status.txt, and your call
    only waits for it. 2. If it prints a line starting GUARD before "started detached", nothing was started: report
    that line word for word and stop; do not try to fix it. 3. The call may be stopped at its 2-hour limit before the
    run ends. That is expected and does NOT stop the run. Whenever the call stops, or you are woken for any reason, run
    exactly the same command again the same way: it prints "attaching to the running worker" and waits again. Keep
    doing this until it prints "finished". If it ever prints "started detached" a second time, the run was lost: say
    so in your report. 4. Then report the last lines it printed, above all the "points (detection, ...)" line. Never
    report success for a run that did not finish.

## Stage 3: one column (remote_omega1_arm.sh)

One worker per column. `null` (Housing First on the corrected build, about 2 to 4 hours) is the budget target and the
held price of the others: fixp and tf wait for its results/omega1_Cu/cf/null/net_target.txt (up to 12 hours,
OMEGA1_NULL_WAIT), so they can be launched beside it. fixboth and fixpv do not wait; fixboth launched before the null is
in holds the benchmark's own price, says so in its status, and is to be re-run for the paper's column once the null is
in (or launched with OMEGA1_WAIT_NULL=1 to wait like the others). The main columns took about 3.5 (fixboth), 4.5
(fixpv), 6 (tf) and 8 (fixp) hours. The null takes no OMEGA1_PDET.

    You are a calibration worker. Your whole job is to keep ONE model solve going until it finishes. Do not edit any
    file. 1. From the repository root, run this command with the Bash tool's run_in_background=true and timeout
    7200000, exactly as written: bash code/omega1/remote_omega1_arm.sh <column> OMEGA1_B=<b> OMEGA1_PDET=<p>. Never
    add nohup or '&'. The script starts the solve DETACHED from your call (it installs gfortran if missing, builds,
    may wait hours for the Housing First column to land before it starts, then solves, a few hours more), pushes its
    status every 20 minutes to results/omega1_Cu/nodes/<column>/status.txt, and your call only waits for it. 2. If it
    prints a line starting GUARD before "started detached", nothing was started: report that line word for word and
    stop; do not try to fix it. 3. The call will be stopped at its 2-hour limit before the solve ends. That is expected
    and does NOT stop the solve. Whenever the call stops, or you are woken for any reason, run exactly the same command
    again the same way: it prints "attaching to the running solve" and waits again. Keep doing this until it prints
    "finished". If it ever prints "started detached" a second time, the solve was lost and has started again: say so
    in your report. 4. Then report the last lines it printed, above all the
    "column <column> ACCEPTED" or "NOT accepted" line. Never report success for a column that was not accepted.

## The permission rule

.claude/settings.json allows `Bash(bash code/remote_omega_point.sh:*)` only. A worker in a session whose permission
mode asks before running commands would need, in addition:

    "Bash(bash code/omega1/run_whostops_omega1.sh:*)",
    "Bash(bash code/omega1/remote_omega1_arm.sh:*)"

A command that starts with the settings (`OMEGA1_B=<b> bash code/omega1/...`) does not start with `bash code/omega1/`,
which is why the prompts pass them as trailing arguments. The 14 October workers (remote_nish_nodes_Cu.sh, and
remote_decomp_shares_Cu2.sh with SHARES_* in front) ran with no rule for their commands either; a worker launched the
way they were needs none.
