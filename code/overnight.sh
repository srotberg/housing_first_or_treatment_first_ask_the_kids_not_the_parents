#!/usr/bin/env bash
# THE OVERNIGHT DRIVER. Runs one search unattended, restarts it if it dies, and
# pushes on its own clock so a container reclaim costs at most one point.
#
#   bash code/overnight.sh nm       Nelder-Mead          (the live choice)
#   bash code/overnight.sh sweep    coordinate brackets  (ready, not running)
#
# THE TWO CANNOT RUN TOGETHER on one container: run_one_point.sh writes
# PARAM_HANDOVER.txt and calibration_state.dat in code/, so two solvers would
# interleave their handovers and each would measure the other's vector. Switching
# is stop-one-start-the-other, and both keep their own state file, so a switch
# loses nothing and can be reversed.
set -uo pipefail
cd "$(dirname "$0")/.."
B=claude/two-period-addiction-hazard-d7gb61
WHICH=${1:-nm}

runner() {
    while true; do
        if [ "$WHICH" = "sweep" ]; then
            python3 code/sweep.py --run >> code/sweep_run.log 2>&1
            echo "$(date +%H:%M:%S) sweep.py exited; restarting" >> code/sweep_run.log
        else
            bash code/nm_loop.sh 2000 >> code/nm_run.log 2>&1
            echo "$(date +%H:%M:%S) nm_loop exited; restarting" >> code/nm_run.log
        fi
        sleep 20
    done
}
runner &
RUN=$!
echo "$(date -u +%H:%M) overnight.sh started $WHICH, pid $RUN" >> code/overnight.log

# A MEASUREMENT THAT IS NOT IN THE REPO DID NOT HAPPEN. The pusher runs
# independently of the solver so it cannot be blocked by a long solve.
while kill -0 $RUN 2>/dev/null; do
    sleep 300
    git add -A code/points code/.nm_state.json code/nm_trace.txt code/batch_nm.txt \
        code/.sweep_state.json code/sweep_trace.txt code/sweep_probes.txt \
        code/nm_run.log code/sweep_run.log code/overnight.log \
        code/calibration_state.dat code/B_SWEEP_GRID.txt >/dev/null 2>&1
    git commit -q -m "$WHICH search, $(date -u +%H:%M) UTC

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv" >/dev/null 2>&1
    git pull --rebase -q origin $B >/dev/null 2>&1
    git push -q origin $B >/dev/null 2>&1
done
