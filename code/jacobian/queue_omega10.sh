#!/bin/bash
# queue_omega10.sh -- start omega_c at +10 percent once fewer than two arms run here (11 November; it replaces
# queue_more.sh, whose h2 at -10 percent moved the whole rental ladder and is now run by run_jacobian_rung.sh instead).
cd "$(dirname "$0")/../.."
narms() { pgrep -fc 'cf_arm_C[uj]\.sh null$' || true; }
while [ "$(narms)" -ge 2 ]; do sleep 30; done
JAC_STEP=0.10 JAC_PUSH=1 setsid nohup bash code/jacobian/run_jacobian_omega.sh omega_c > code/jacobian/q_omega_c_010.log 2>&1 < /dev/null &
echo $! > code/jacobian/q_omega_c_010.pid
echo "started omega_c +10% as pid $(cat code/jacobian/q_omega_c_010.pid) ($(date -u +%H:%M))"
while kill -0 "$(cat code/jacobian/q_omega_c_010.pid)" 2>/dev/null; do sleep 60; done
echo "omega_c +10% done ($(date -u +%H:%M))"
