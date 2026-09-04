#!/usr/bin/env bash
# THE OVERNIGHT DRIVER. Restarts sweep.py if it ever dies, commits and pushes
# every few minutes so a container reclaim costs at most one point, and never
# needs the coordinator awake.
#
#   bash code/sweep_loop.sh
set -uo pipefail
cd "$(dirname "$0")/.."
B=claude/two-period-addiction-hazard-d7gb61
while true; do
    python3 code/sweep.py --run >> code/sweep_run.log 2>&1
    echo "$(date +%H:%M:%S) sweep.py exited; restarting in 30s" >> code/sweep_run.log
    sleep 30
done &
SWEEP=$!
# A MEASUREMENT THAT IS NOT IN THE REPO DID NOT HAPPEN, so the pusher runs
# independently of the solver and cannot be blocked by it.
while kill -0 $SWEEP 2>/dev/null; do
    sleep 240
    git add -A code/points code/.sweep_state.json code/sweep_trace.txt \
        code/sweep_probes.txt code/sweep_run.log code/calibration_state.dat \
        code/B_SWEEP_GRID.txt >/dev/null 2>&1
    git commit -q -m "Coordinate sweep, $(date -u +%H:%M) UTC

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv" >/dev/null 2>&1
    git pull --rebase -q origin $B >/dev/null 2>&1
    git push -q origin $B >/dev/null 2>&1
done
