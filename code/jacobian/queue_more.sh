#!/bin/bash
# queue_more.sh -- start each queued solve once fewer than two arms run on this machine, one at a time, so two queued
# scripts never see the same free slot (11 November: omega_c at +10 percent, h2 at -10 percent).
cd "$(dirname "$0")/../.."
narms() { pgrep -fc 'cf_arm_C[uj]\.sh null$' || true; }
for spec in "run_jacobian_omega.sh 0.10 omega_c" "run_jacobian_step.sh -0.10 h2"; do
    set -- $spec
    while [ "$(narms)" -ge 2 ]; do sleep 30; done
    tag=$(echo "$3_$2" | tr -d '.-'); 
    JAC_STEP=$2 JAC_PUSH=1 setsid nohup bash code/jacobian/$1 $3 > code/jacobian/q_$tag.log 2>&1 < /dev/null &
    echo $! > code/jacobian/q_$tag.pid
    echo "started $spec as pid $(cat code/jacobian/q_$tag.pid) ($(date -u +%H:%M))"
    sleep 150
done
for p in code/jacobian/q_*.pid; do while kill -0 "$(cat "$p")" 2>/dev/null; do sleep 60; done; done
echo "queue done ($(date -u +%H:%M))"
