#!/usr/bin/env bash
# THE NIGHT'S RUN: seed the stage, search it, promote to the next stage when it
# is done, and never need the coordinator awake.
#
# The author, 4 September: "calibrate the seven inside 10%, then add, pi_V,
# tau_l, aleph, sigma_y, pi_eu....and keep the rest after you finish the first
# one", and "make sure it is automated so it can continue to work while i sleep".
#
# WHY STAGING RATHER THAN ALL TWENTY. nelder_test.py passes 8-dim Rosenbrock at
# 4.6e-14 and FAILS 20-dim at 0.187 with three thousand evaluations. The method
# is competent at seven or twelve instruments and not at twenty, so the stage
# size is chosen to keep it inside its competence. A stage of seven also seeds
# from eight vertices instead of twenty-one.
set -uo pipefail
cd "$(dirname "$0")/.."
B=claude/two-period-addiction-hazard-d7gb61

push() {
    git add -A code/points code/.nm_state.json code/nm_trace.txt code/batch_nm.txt \
        code/nm_stage.txt code/nm_run.log code/calibration_state.dat \
        code/B_SWEEP_GRID.txt code/batch_stage*_seed.txt >/dev/null 2>&1
    git commit -q -m "Stage $(cat code/nm_stage.txt 2>/dev/null) search, $(date -u +%H:%M) UTC

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv" >/dev/null 2>&1
    git pull --rebase -q origin $B >/dev/null 2>&1
    git push -q origin $B >/dev/null 2>&1
}

npoints() { python3 -c "
import sys; sys.path.insert(0,'code')
import newton as N, next_batch as NB
NB._apply_process_mapping(); print(len(N.archive()))" 2>/dev/null || echo 0; }

# 1. SEED. Solve the stage's vertices; run_one_point skips any already measured,
#    so a fleet worker landing one simply removes it from this queue.
echo "$(date -u +%H:%M) seeding stage $(cat code/nm_stage.txt)" >> code/nm_run.log
while read -r l; do
    eval "$l" >> code/nm_run.log 2>&1
    push
done < code/batch_stage1_seed.txt

# 2. SEARCH, restarting the loop if it ever dies.
python3 code/nelder.py --init >> code/nm_run.log 2>&1
while true; do
    bash code/nm_loop.sh 2000 >> code/nm_run.log 2>&1
    echo "$(date -u +%H:%M) nm_loop exited; restarting" >> code/nm_run.log
    push
    sleep 20
done
