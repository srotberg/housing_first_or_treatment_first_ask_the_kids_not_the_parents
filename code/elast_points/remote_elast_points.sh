#!/bin/bash
# remote_elast_points.sh <worker 0-4> -- the drug price elasticities at every whole per cent from -50
# to +50, twenty points per cloud worker (the author: "5 workers, 20 points each") (the author, 2 October: "can you try every single point
# betweeen -50 and +50 and average that for both?"). Worker i takes the points p with
# (p+50) mod 5 = i, p != 0, so each worker has small and large steps on both sides.
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
# Every 20 minutes it pushes results/elast_points/w<i>.txt; at the end the gzipped log too.
set -u
W="$1"
case "$W" in [0-4]) ;; *) echo "usage: $0 <worker 0-4>"; exit 1 ;; esac
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
R=$REPO/results/elast_points; mkdir -p "$R"
D=$C/elast_w$W
OUT=$R/w$W.txt
REF=$REPO/results/reference/hf_2c_omega_0.085/PARAM_HANDOVER.bench.txt
PTS=$(python3 -c "print(','.join(str(p) for p in range(-50,51) if p and (p+50)%5==$W))")
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
note() { echo "remote_elast_points w$W: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${ELAST_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_elast_points w$W: attaching to the running solve, pid $(cat "$D.pid")"
    else
        ( ELAST_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/elast_w$W.detached.log" 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_elast_points w$W: started detached, pid $(cat "$D.pid"); log /tmp/elast_w$W.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_elast_points w$W: finished"; cat "$D.status" 2>/dev/null
    grep -q "solve exited 0" "$D.status" 2>/dev/null
    exit $?
fi

publish() (
    {
        echo "# elasticity points, worker $W, points $PTS; $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        [ -f "$D/run/bench.log" ] && grep -a "BLOCK MOVE\|ELASTICITY_MULTI dp=\|ELASTICITY_MULTI average\|ELASTICITY_NULL dp\|simulation ended" "$D/run/bench.log"
        true
    } > "$OUT.tmp"; mv "$OUT.tmp" "$OUT"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "elasticity points w$W: $1$TRAILER" || return 0
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
