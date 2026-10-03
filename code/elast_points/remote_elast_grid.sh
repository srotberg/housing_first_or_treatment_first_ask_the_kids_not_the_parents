#!/bin/bash
# remote_elast_grid.sh <worker 0-1> -- the drug price elasticities on a grid from -95 to +100 per cent
# (the author, 3 October: "maybe then do the elasticity based on -100, -90, -80, ....10, 20, 30....100?", and on
# -100, where the drug is free: "95% is fine"). Twenty points, ten per worker, alternating so each worker has small
# and large steps on both sides: worker 0 takes -95,-80,-60,-40,-20,10,30,50,70,90 and worker 1
# -90,-70,-50,-30,-10,20,40,60,80,100. A copy of remote_elast_points.sh with only the list, the
# directories and the output files changed.
#
# Each worker re-solves the omega_c = 0.085 benchmark from the scan seed with the reference
# handover (about 4.5 hours, as the 2 October measurement did), then raises or lowers the drug
# price by each of its points from the restored benchmark state and prints one ELASTICITY_MULTI line
# per point (about 7 minutes each, so about 2.5 hours for twenty). The binary is make_binary.sh's: the accepted measurement's,
# with only the list of steps changed. Elasticities are log ratios against the worker's own
# restored base, so the small run-to-run differences between workers' benchmarks do not enter.
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root, and run it again
# whenever the call stops: it attaches to the running solve (the detach is remote_omega_point.sh's).
# Every 20 minutes it pushes results/elast_grid/w<i>.txt; at the end the gzipped log too.
set -u
W="$1"
case "$W" in [0-1]) ;; *) echo "usage: $0 <worker 0-1>"; exit 1 ;; esac
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
R=$REPO/results/elast_grid; mkdir -p "$R"
D=$C/elast_g$W
OUT=$R/w$W.txt
REF=$REPO/results/reference/hf_2c_omega_0.085/PARAM_HANDOVER.bench.txt
PTS=$([ "$W" = 0 ] && echo "-95,-80,-60,-40,-20,10,30,50,70,90" || echo "-90,-70,-50,-30,-10,20,40,60,80,100")
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
note() { echo "remote_elast_grid w$W: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${ELAST_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_elast_grid w$W: attaching to the running solve, pid $(cat "$D.pid")"
    else
        ( ELAST_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/elast_g$W.detached.log" 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_elast_grid w$W: started detached, pid $(cat "$D.pid"); log /tmp/elast_g$W.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_elast_grid w$W: finished"; cat "$D.status" 2>/dev/null
    grep -q "solve exited 0" "$D.status" 2>/dev/null
    exit $?
fi

publish() (
    {
        echo "# elasticity grid, worker $W, points $PTS; $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        [ -f "$D/run/bench.log" ] && grep -a "BLOCK MOVE\|ELASTICITY_MULTI dp=\|ELASTICITY_MULTI average\|ELASTICITY_NULL dp\|simulation ended" "$D/run/bench.log"
        true
    } > "$OUT.tmp"; mv "$OUT.tmp" "$OUT"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "elasticity grid w$W: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)

[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"
command -v gfortran >/dev/null 2>&1 || {
    note "gfortran missing, installing"
    apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1
}
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
[ -d "$D" ] && mv "$D" "$D.dead_$(date -u +%H%M%S)"
mkdir -p "$D/run"
note "building, points $PTS"
# THE BINARY IS BUILT FROM d62835db, and a cloud session clones fifty commits deep, so that commit is
# not in its history: both workers of 03 Oct 02:05 failed on 'invalid object name'. Fetch it first.
git -C "$C/.." cat-file -e d62835db^{commit} 2>/dev/null || git -C "$C/.." fetch -q --unshallow origin 2>/dev/null || \
    git -C "$C/.." fetch -q --depth=1000 origin "$BRANCH"
git -C "$C/.." cat-file -e d62835db^{commit} 2>/dev/null || { note "GUARD: d62835db not reachable"; publish "failed"; exit 1; }
bash "$C/elast_points/make_binary.sh" "$D/build" "$PTS" > "$D/build.log" 2>&1 || {
    note "GUARD: build failed: $(tail -3 "$D/build.log" | tr '\n' ' ')"; publish "failed"; exit 1; }
note "$(tail -1 "$D/build.log")"
cd "$D/run"
# staged as remote_omega_point.sh stages a run: the scan seed, the data link, the reference
# handover unchanged (the 2 October measurement used it the same way)
[ -e "$C/data" ] || { note "GUARD: code/data missing"; publish "failed"; exit 1; }
ln -s "$C/data" "$D/data"
cp "$C/scan_seed/calibration_state.dat" "$C/scan_seed/calibration_distribution_shape.dat" .
gunzip -c "$C/scan_seed/calibration_distribution1.dat.gz" > calibration_distribution1.dat
gunzip -c "$C/scan_seed/calibration_distribution2.dat.gz" > calibration_distribution2.dat
[ "$(stat -c%s calibration_distribution1.dat)" = "265496400" ] || { note "GUARD: distribution 1 wrong size"; publish "failed"; exit 1; }
cp "$REF" PARAM_HANDOVER.txt
cp "$D/build/hftf_elast" ./hftf_elast
note "solving, $(nproc) cores"
env OMP_NUM_THREADS=4 ./hftf_elast > bench.log 2> bench.err < /dev/null &
PID=$!
while kill -0 "$PID" 2>/dev/null; do
    for _ in $(seq 1 120); do kill -0 "$PID" 2>/dev/null || break; sleep 10; done
    kill -0 "$PID" 2>/dev/null && publish "$(grep -ac 'BLOCK MOVE' bench.log) blocks, $(grep -ac 'ELASTICITY_MULTI dp=' bench.log) points"
done
wait "$PID"; RC=$?
note "solve exited $RC after $(grep -ac 'BLOCK MOVE' bench.log) blocks and $(grep -ac 'ELASTICITY_MULTI dp=' bench.log) points; bench.err: $(tail -2 bench.err | tr '\n' ' ')"
gzip -c bench.log > "$R/w$W.bench.log.gz"
publish "complete (exit $RC)"
