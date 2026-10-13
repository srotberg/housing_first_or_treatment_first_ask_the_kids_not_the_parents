#!/bin/bash
# stop_clear_C.sh -- stops ONLY run_noext_clear_C.sh and its Arm C (cfarm_tf_noext_clear_C) in the NOEXT container, leaving
# Arm A (cfarm_null_pe_noext_C), Arm D (run_noext_fixp_C.sh) and Arm B (run_pe_C.sh) running (13 October 19:45: Arm C is
# rerun from a nearer start by run_noext_clear_C2.sh in a fresh container). Run from the repo root. Never `pkill hftf_cf`
# here: the other arms run the same binary name.
C=$(cd "$(dirname "$0")/.." && pwd)
W=$C/noext_clear/work_clear_C
echo "before:"; for p in $(pgrep -x hftf_cf); do echo "  hftf_cf $p in $(readlink /proc/$p/cwd)"; done
pkill -f 'run_noext_clear_C\.sh' && echo "stopped the run_noext_clear_C.sh launcher"
[ -f "$W/arm_C.pid" ] && { pkill -P "$(cat "$W/arm_C.pid")" 2>/dev/null; kill "$(cat "$W/arm_C.pid")" 2>/dev/null; }
for p in $(pgrep -f .); do
    [ "$(readlink /proc/$p/cwd 2>/dev/null)" = "$C/cfarm_tf_noext_clear_C" ] && { echo "  killing $p ($(tr '\0' ' ' < /proc/$p/cmdline | cut -c1-60))"; kill "$p"; }
done
sleep 5
echo "after:"; for p in $(pgrep -x hftf_cf); do echo "  hftf_cf $p in $(readlink /proc/$p/cwd)"; done
pgrep -af 'run_noext_clear_C\.sh' >/dev/null && echo "STILL RUNNING: run_noext_clear_C.sh" || echo "run_noext_clear_C.sh stopped"
for p in $(pgrep -x hftf_cf); do [ "$(readlink /proc/$p/cwd)" = "$C/cfarm_tf_noext_clear_C" ] && echo "STILL RUNNING: arm C solver $p"; done
pgrep -af 'run_noext_fixp_C\.sh|run_pe_C\.sh' >/dev/null && echo "the other two launchers are still running (as they should be)" || echo "WARNING: the other launchers are not running"
