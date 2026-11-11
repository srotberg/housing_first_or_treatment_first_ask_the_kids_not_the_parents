#!/bin/bash
# queue_rung5.sh -- h2 alone at +5 percent (rungs held), started here once the +10 percent run has finished and fewer than
# two arms run (11 November).
cd "$(dirname "$0")/../.."
narms() { pgrep -fc 'cf_arm_C[uj]\.sh null$' || true; }
while kill -0 "$(cat code/jacobian/rung_h2_10.pid)" 2>/dev/null; do sleep 60; done
while [ "$(narms)" -ge 2 ]; do sleep 30; done
JAC_STEP=0.05 JAC_PUSH=1 setsid nohup bash code/jacobian/run_jacobian_rung.sh h2 > code/jacobian/rung_h2_5.log 2>&1 < /dev/null &
echo $! > code/jacobian/rung_h2_5.pid
echo "started h2 +5% rungs held as pid $(cat code/jacobian/rung_h2_5.pid) ($(date -u +%H:%M))"
while kill -0 "$(cat code/jacobian/rung_h2_5.pid)" 2>/dev/null; do sleep 60; done
echo "h2 +5% rungs held done ($(date -u +%H:%M))"
