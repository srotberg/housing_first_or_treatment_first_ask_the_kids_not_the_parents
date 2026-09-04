#!/usr/bin/env bash
# LIFT THE PAUSE WHEN THE ARCHIVE CAN ACTUALLY SEED A SIMPLEX.
#
# Nelder-Mead was held (code/PAUSE_NM) while the coordinate scan rebuilt the
# archive on the corrected economy, because a simplex seeded from one point is
# worse than no simplex. The condition for lifting it is not a clock: it is
# having enough spanning points that seed() can find eleven affinely independent
# vertices inside the competitive region.
#
# Left to a human noticing, this waits for the next time someone looks. So it is
# a guard: when the live economy holds MIN_POINTS, the pause comes off, the
# watchdog restarts the solver on its next cycle, and the coverage loop keeps
# running beside it -- which is the intended steady state, not a handover.
set -uo pipefail
cd "$(dirname "$0")/.."
MIN_POINTS=${1:-60}
while true; do
    if [ -f code/PAUSE_NM ]; then
        n=$(python3 -c "
import sys; sys.path.insert(0,'code')
import newton as N, next_batch as NB
NB._apply_process_mapping(); print(len(N.archive()))" 2>/dev/null || echo 0)
        if [ "${n:-0}" -ge "$MIN_POINTS" ]; then
            rm -f code/PAUSE_NM
            echo "$(date -u +%H:%M:%S) archive at $n points, pause lifted" \
                >> code/resume_guard.log
            exit 0
        fi
        echo "$(date -u +%H:%M:%S) archive at $n of $MIN_POINTS, still paused" \
            >> code/resume_guard.log
    else
        exit 0
    fi
    sleep 300
done
