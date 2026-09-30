#!/bin/bash
# remote_omega_point.sh <omega_c> -- one point of the omega_c scan on the corrected code (the
# child-penalty fix d45b36ea and the child in the drug split ec1358e1), for a cloud worker.
#
# The author, 30 September: "i think youll need to first run omega_c=0", "to have the case with no
# parents", "and then you can spawn several sessions to test many omega_c vlaue at once". The
# omega_c = 0 case is pointrun_childsplit_omega0 in the main session; each worker solves the SAME
# economy at one positive omega_c, and omega_c's moment is the rise in drug users from the worker's
# point to omega_c = 0 (NSDUH: 18.3 per cent).
#
# Exactly what pointrun_childsplit.sh does in the main session: build_bench_tdm_childsplit.sh (rule
# 5e-5, at least 70 sweeps a block), the benchmark of record's handover
# (results/reference/hf_omega_c_006_tdm/PARAM_HANDOVER.bench.txt, 12 frozen blocks) with only
# weight_on_child changed, and the scan seed.
#
# START IT WITH THE BASH TOOL'S run_in_background=true, never with nohup or &, from the repo root:
#     bash code/remote_omega_point.sh 0.08
# It needs no agent after launch. Every 20 minutes it pushes the MOMENT and BLOCK MOVE lines so
# far to results/omega_c_scan_childsplit/omega_<w>.moments.txt, and at the end that file and the
# gzipped log. The log itself lives in an untracked directory, so git pull --rebase cannot replace
# it under the running solve; the push rebases onto the fetched tip and pushes HEAD, so a
# container that checked the branch out detached still delivers (both lessons recorded in
# CALIBRATION_STATE.md, 29 September).
set -u
W="$1"
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$C/.." && pwd)
R=$REPO/results/omega_c_scan_childsplit; mkdir -p "$R"
D=$C/omega_point_$W
OUT=$R/omega_$W.moments.txt
REF=$REPO/results/reference/hf_omega_c_006_tdm/PARAM_HANDOVER.bench.txt
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'

note() { echo "remote_omega_point $W: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

# THE SOLVE OUTLIVES THE TOOL CALL. A cloud session stops a background command at its time
# limit (two hours at most) and the solve takes four to four and a half, so the first
# workers of 30 September would have died half way. The real work therefore runs in its own
# process session (setsid, the way the main session's runs have always survived), and this
# foreground call only waits for it. When the wait is stopped, running the same command again
# ATTACHES to the running solve rather than starting a second one.
if [ "${OMEGA_POINT_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_omega_point $W: attaching to the running solve, pid $(cat "$D.pid")"
    else
        OMEGA_POINT_DETACHED=1 setsid nohup bash "$0" "$W" > "/tmp/omega_point_$W.detached.log" 2>&1 < /dev/null &
        echo $! > "$D.pid"
        echo "remote_omega_point $W: started detached, pid $(cat "$D.pid"); log /tmp/omega_point_$W.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_omega_point $W: finished"; cat "$D.status" 2>/dev/null
    grep -q "solve exited 0\|dry run" "$D.status" 2>/dev/null
    exit $?
fi

publish() (  # publish <message>; a subshell, so its cd cannot leak into the caller
    {
        echo "# omega_c scan point, weight_on_child $W, corrected code; $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        [ -f "$D/BUILD_USED" ] && echo "build md5: $(cut -c1-32 "$D/BUILD_USED")"
        [ -f "$D/bench.log" ] && grep -a "HANDOVER weight_on_child\|MOMENT\|BLOCK MOVE\|newborn_parent_share (clean\|FROZEN\|simulation ended" "$D/bench.log"
        # the group's status is its last test's: without this, a publish before the solve (no
        # bench.log yet) skipped the mv and committed the .tmp file instead (worker 0.0, 23:04)
        true
    } > "$OUT.tmp"; mv "$OUT.tmp" "$OUT"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "omega_c scan point $W: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)

: > "$D.status"
# A FRESH CLOUD CONTAINER HAS NO FORTRAN COMPILER (worker 0.0 failed on this at 23:04); install it,
# as remote_internalise_point.sh does.
command -v gfortran >/dev/null 2>&1 || {
    note "gfortran missing, installing"
    apt-get update -qq >/dev/null 2>&1
    apt-get install -y -qq gfortran >/dev/null 2>&1
}
command -v gfortran >/dev/null || { note "GUARD: no gfortran and it could not be installed"; publish "failed"; exit 1; }
if [ ! -x "$C/bench_tdm_childsplit/hftf_bench" ]; then
    note "building"
    bash "$C/build_bench_tdm_childsplit.sh" > "/tmp/omega_point_build_$W.log" 2>&1 || {
        note "GUARD: build failed: $(tail -3 /tmp/omega_point_build_$W.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi

mkdir -p "$D" && cd "$D"
[ -e data ] || ln -s ../../data data
cp "$C/scan_seed/calibration_state.dat" "$C/scan_seed/calibration_distribution_shape.dat" .
gunzip -c "$C/scan_seed/calibration_distribution1.dat.gz" > calibration_distribution1.dat
gunzip -c "$C/scan_seed/calibration_distribution2.dat.gz" > calibration_distribution2.dat
[ "$(stat -c%s calibration_distribution1.dat)" = "265496400" ] || { note "GUARD: distribution 1 wrong size"; publish "failed"; exit 1; }
sed -e "s/^weight_on_child .*/weight_on_child $W/" "$REF" > PARAM_HANDOVER.txt
[ "$(grep -c "^weight_on_child $W\$" PARAM_HANDOVER.txt)" = 1 ] || { note "GUARD: weight_on_child not $W"; publish "failed"; exit 1; }
[ "$(wc -l < PARAM_HANDOVER.txt)" = "$(wc -l < "$REF")" ] || { note "GUARD: handover length changed"; publish "failed"; exit 1; }
cp PARAM_HANDOVER.txt PARAM_HANDOVER.kept.txt
cp "$C/bench_tdm_childsplit/hftf_bench" ./hftf_bench
md5sum hftf_bench > BUILD_USED
[ "${DRY:-0}" = 1 ] && { note "dry run: staged, not launched"; exit 0; }

note "solving, $(nproc) cores"
env OMP_NUM_THREADS=4 ./hftf_bench > bench.log 2> bench.err < /dev/null &
PID=$!
while kill -0 "$PID" 2>/dev/null; do
    for _ in $(seq 1 120); do kill -0 "$PID" 2>/dev/null || break; sleep 10; done
    kill -0 "$PID" 2>/dev/null && publish "$(grep -ac 'BLOCK MOVE' "$D/bench.log") blocks"
done
wait "$PID"; RC=$?
note "solve exited $RC after $(grep -ac 'BLOCK MOVE' "$D/bench.log") blocks; bench.err: $(tail -2 "$D/bench.err" | tr '\n' ' ')"
gzip -c "$D/bench.log" > "$R/omega_$W.bench.log.gz"
publish "complete (exit $RC)"
