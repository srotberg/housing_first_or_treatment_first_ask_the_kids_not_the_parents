#!/bin/bash
# queue_rungtwin.sh -- h2 alone at +10 percent with the child's weight at zero (the twin for h2's cell in omega_c's
# column), started here once h2 alone at +10 percent has finished and fewer than two arms run (11 November). It replaces
# queue_rung5.sh: h2's row is taken at ten percent, alone, as the author chose.
cd "$(dirname "$0")/../.."
narms() { pgrep -fc 'cf_arm_C[uj]\.sh null$' || true; }
while kill -0 "$(cat code/jacobian/rung_h2_10.pid)" 2>/dev/null; do sleep 60; done
while [ "$(narms)" -ge 2 ]; do sleep 30; done
JAC_STEP=0.10 JAC_PUSH=1 setsid nohup bash code/jacobian/run_jacobian_rungtwin.sh h2 > code/jacobian/rungtwin_h2_10.log 2>&1 < /dev/null &
echo $! > code/jacobian/rungtwin_h2_10.pid
echo "started h2 alone +10% with omega_c 0 as pid $(cat code/jacobian/rungtwin_h2_10.pid) ($(date -u +%H:%M))"
while kill -0 "$(cat code/jacobian/rungtwin_h2_10.pid)" 2>/dev/null; do sleep 60; done
echo "done ($(date -u +%H:%M))"
