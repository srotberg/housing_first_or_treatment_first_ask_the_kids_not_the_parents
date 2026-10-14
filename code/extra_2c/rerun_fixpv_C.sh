#!/bin/bash
# rerun_fixpv_C.sh -- THE PRICE-CLEARS DECOMPOSITION COLUMN AGAIN (14 October). The first worker (session_016yrmFb) finished
# its solve at 00:46 but its container went before collect_shares_C.sh copied the arms' logs and values at 26 into
# results/decomp_2c_shares_C/arm_fixpv/{tf,null}, which the table's CEV and childhood share read. Re-solved from the
# converged price 0.9446 (pi_V held), then collected. No newborn step: no table row reads it.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/extra_2c/rerun_fixpv_C.sh
# Re-running attaches to the running solve; the collect runs once the solve has finished.
set -u
C=$(cd "$(dirname "$0")/.." && pwd)
SHARES_P0=${SHARES_P0:-0.9446} bash "$C/extra_2c/remote_decomp_shares_C2.sh" fixpv
if [ -f "$C/cfarm_tf_2c_fixpv/cf.log" ] && tail -5 "$C/cfarm_tf_2c_fixpv.out" 2>/dev/null | grep -q "DIST CHECK PASS"; then
    bash "$C/extra_2c/collect_shares_C.sh" fixpv && echo "rerun_fixpv_C: finished"
else
    echo "rerun_fixpv_C: the solve has not finished (run the same command again to attach)"
fi
