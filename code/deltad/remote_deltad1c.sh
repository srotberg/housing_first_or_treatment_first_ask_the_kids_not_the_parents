#!/bin/bash
# remote_deltad1c.sh -- NO CHILD PENALTY AT ALL, ONE CLASS (12 October; the author: "run with delta=0 deltah=0. there you dont
# need two classes, so it should be super quick to do"). With delta_d = 0 and delta_h = 0 the two child classes of the
# paper's build are the same economy, so child_penalty_classes = 1 solves it at half the state:
#   STAGE A, the benchmark: the benchmark of record's handover (results/reference/hf_2c_omega_0.085) with every adjuster
#     frozen and omega_c pinned, on code/bench_tdm_1c/hftf_bench (build_bench_tdm_1c.sh), seeded from code/scan_seed_1c.
#   STAGE B, Housing First on code/cf_fix2_1c (deltad/build_cf_fix2_1c.sh), its net revenue the budget target.
#   STAGE C, Treatment First as the paper's arm: detection 0.85, the $35 test, the drug price and pi_V clearing.
# The gain is CEV(tf) - CEV(null) on this benchmark's own curve. Results to results/deltad/dd0_1c/.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/deltad/remote_deltad1c.sh
set -u
DD=0
TAG=dd0_1c
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
R=$REPO/results/deltad/$TAG
mkdir -p "$R"
D=$C/deltad_run_$TAG
REF=$REPO/results/reference/hf_2c_omega_0.085
SEED=$C/scan_seed_1c
BD=$C/deltad_bench_$TAG
BREF=$C/deltad_benchref_$TAG
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
KX=0.9342362271804227; BV=0.0054222; W=0.085
PENALTIES="penalty_child_addicted 0;penalty_child_homeless 0"
BLOCKS=${BLOCKS:-16}
DSIZE=132748200

note() { echo "remote_deltad1c: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${DELTAD_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_deltad1c: attaching to the running work, pid $(cat "$D.pid")"
    else
        ( DELTAD_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/deltad_$TAG.detached.log" 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_deltad1c: started detached, pid $(cat "$D.pid"); log /tmp/deltad_$TAG.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_deltad1c: finished"; cat "$D.status" 2>/dev/null
    grep -q "arm tf ACCEPTED" "$D.status" 2>/dev/null
    exit $?
fi

digest() (
    cd "$C"
    L="cfarm_${1}_2c/cf.log"
    [ -f "$L" ] && python3 cf_runs/passes.py "$L" "$C/cf_runs/cev.py" 2>/dev/null
)
publish() (
    {
        echo "# delta_d 0 and delta_h 0, one class, every other parameter as calibrated (code/deltad/remote_deltad1c.sh); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        if [ -f "$BD/bench.log" ]; then
            echo; echo "== benchmark"
            grep -a "HANDOVER penalty_child\|HANDOVER omega_c_is_pinned\|BLOCK MOVE\|newborn_parent_share (clean\|INVARIANT PASS\|FROZEN" "$BD/bench.log" | tail -40
        fi
        for a in null tf; do
            [ -f "$C/cfarm_${a}_2c/cf.log" ] && { echo; echo "== $a"; digest "$a"; }
        done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "delta_d 0 one class: $1$TRAILER" || return 0
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
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"

cd "$C"
if [ ! -x "$C/bench_tdm_1c/hftf_bench" ]; then
    note "building the one-class benchmark binary"
    bash build_bench_tdm_1c.sh > /tmp/deltad1c_build_bench.log 2>&1 || {
        note "GUARD: benchmark build failed: $(tail -3 /tmp/deltad1c_build_bench.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
if [ ! -x "$C/cf_fix2_1c/hftf_cf_prod" ]; then
    note "building cf_fix2_1c"
    bash deltad/build_cf_fix2_1c.sh > /tmp/deltad1c_build_cf.log 2>&1 || {
        note "GUARD: cf build failed: $(tail -3 /tmp/deltad1c_build_cf.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
publish "built, starting"

# STAGE A: THE BENCHMARK, every parameter fixed, delta_d set
if [ -s "$BREF/bench_files.tar.gz" ] && [ -s "$BREF/bench.log.gz" ]; then
    note "benchmark already solved, $BREF"
else
    [ -d "$BD" ] && mv "$BD" "$BD.dead_$(date -u +%H%M%S)"
    mkdir -p "$BD" && cd "$BD"
    [ -e data ] || ln -s ../../data data
    cp "$SEED/calibration_state.dat" "$SEED/calibration_distribution_shape.dat" .
    gunzip -c "$SEED/calibration_distribution1.dat.gz" > calibration_distribution1.dat
    gunzip -c "$SEED/calibration_distribution2.dat.gz" > calibration_distribution2.dat
    [ "$(stat -c%s calibration_distribution1.dat)" = "$DSIZE" ] || { note "GUARD: seed distribution 1 wrong size"; publish "failed"; exit 1; }
    cp "$REF/PARAM_HANDOVER.bench.txt" PARAM_HANDOVER.txt
    setl() {
        if grep -q "^$1 " PARAM_HANDOVER.txt; then sed -i "s|^$1 .*|$1 $2|" PARAM_HANDOVER.txt; else echo "$1 $2" >> PARAM_HANDOVER.txt; fi
        grep -qx "$1 $2" PARAM_HANDOVER.txt || { note "GUARD: $1 is not $2"; publish "failed"; exit 1; }
    }
    setl penalty_child_addicted 0
    setl penalty_child_homeless 0
    setl omega_c_is_pinned 1
    setl freeze_all_but_omega_c 1
    setl weight_on_child $W
    setl addiction_scalar_1 $BV
    setl kappa_uem 1.0
    setl kappa_x $KX
    setl frozen_stop_after_blocks $BLOCKS
    cp PARAM_HANDOVER.txt PARAM_HANDOVER.kept.txt
    cp "$C/bench_tdm_1c/hftf_bench" ./hftf_bench
    note "benchmark: one class, solving from the one-class scan seed, at most $BLOCKS frozen blocks"
    env OMP_NUM_THREADS=4 ./hftf_bench > bench.log 2> bench.err < /dev/null &
    PID=$!
    for _ in $(seq 1 60); do grep -q -a "HANDOVER penalty_child_addicted" bench.log 2>/dev/null && break; sleep 5; done
    grep -a "HANDOVER penalty_child_addicted\|HANDOVER omega_c_is_pinned" bench.log | head -2 | while read -r l; do note "$l"; done
    while kill -0 "$PID" 2>/dev/null; do
        for _ in $(seq 1 120); do kill -0 "$PID" 2>/dev/null || break; sleep 10; done
        if ! grep -q -a "HANDOVER penalty_child_addicted" bench.log; then
            kill "$PID"; note "GUARD: no HANDOVER line in the benchmark log; killed"; publish "failed"; exit 1
        fi
        kill -0 "$PID" 2>/dev/null && publish "benchmark running, $(grep -ac 'BLOCK MOVE' bench.log) blocks"
    done
    wait "$PID"; RC=$?
    note "benchmark exited $RC after $(grep -ac 'BLOCK MOVE' bench.log) blocks; bench.err: $(tail -2 bench.err | tr '\n' ' ')"
    gzip -c bench.log > "$R/bench.log.gz"
    for f in welfare_curvebaseline_benchmark.dat median_incomebaseline_benchmark.dat drug_supply_shifterbaseline_benchmark.dat; do
        [ -s "$f" ] || { note "GUARD: the benchmark did not write $f"; publish "failed"; exit 1; }
    done
    mkdir -p "$BREF"
    tar czf "$BREF/bench_files.tar.gz" *baseline_benchmark.dat
    gzip -c bench.log > "$BREF/bench.log.gz"
    cp PARAM_HANDOVER.kept.txt "$R/PARAM_HANDOVER.bench.txt"
    gzip -c welfare_curvebaseline_benchmark.dat > "$R/welfare_curvebaseline_benchmark.dat.gz"
    mkdir -p "$R/files" && cp "$R/welfare_curvebaseline_benchmark.dat.gz" "$R/files/"
    # the curves the paper's welfare script reads (welfare_nok.Bench): the all-ages and childhood curves, if written
    for f in *welfare*baseline_benchmark.dat *childhood*baseline_benchmark.dat; do [ -s "$f" ] && gzip -c "$f" > "$R/$f.gz"; done
    publish "benchmark done"
    cd "$C"
fi

export BENCH_FROM=$BREF BENCH_B=$BV BENCH_OMEGA=$W BENCH_KU=1.0 KAPPA_X=$KX
export OMP_NUM_THREADS=4 SEED_FROM=bench DIAG_TAG=_2c
export CEV_CURVE=$D.welfare_curve.dat
tar xzf "$BREF/bench_files.tar.gz" -O welfare_curvebaseline_benchmark.dat > "$CEV_CURVE"
export PASSES_BASE=$(zcat "$BREF/bench.log.gz" | awk '/INVARIANT PASS +drug users/{b=$NF} /INVARIANT PASS +disorder rate/{l=$NF} /INVARIANT PASS +homelessness rate/{h=$NF} END{print b","l","h}')
note "benchmark (users, SUD, h_1) $PASSES_BASE"

# run_arm <arm> [VAR=value ...]: as remote_deltah.sh's, on cf_fix2, the penalty in EXTRA_SET
run_arm() (
    a=$1; shift
    cd "$C"
    note "arm $a on cf_fix2_1c: $*"
    env BUILD=cf_fix2_1c "$@" sh treat/cf_arm_x.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 &
    P=$!
    while kill -0 "$P" 2>/dev/null; do
        for _ in $(seq 1 120); do kill -0 "$P" 2>/dev/null || break; sleep 10; done
        kill -0 "$P" 2>/dev/null && publish "$a running, $(grep -ac '^ *distance_govt_budget=' "$C/cfarm_${a}_2c/cf.log" 2>/dev/null) passes"
    done
    wait "$P"; rc=$?
    O="$C/cfarm_${a}_2c.out"
    mkdir -p "$R/$a"
    gzip -c "$O" > "$R/$a/run.out.gz"
    [ -f "$C/cfarm_${a}_2c/cf.log" ] && gzip -c "$C/cfarm_${a}_2c/cf.log" > "$R/$a/cf.log.gz"
    [ -f "$C/cfarm_${a}_2c/PARAM_HANDOVER.arm.txt" ] && cp "$C/cfarm_${a}_2c/PARAM_HANDOVER.arm.txt" "$R/$a/"
    grep -a "CHECK PASS\|GUARD" "$O" > "$R/$a/checks.txt"
    NULLLOG=""; [ "$a" != null ] && [ -f "$C/cfarm_null_2c/cf.log" ] && NULLLOG="$C/cfarm_null_2c/cf.log"
    [ -f "$C/cfarm_${a}_2c/cf.log" ] && python3 "$C/cf_runs/finalstats.py" "$C/cfarm_${a}_2c/cf.log" $NULLLOG > "$R/$a/final.txt" 2>&1
    digest "$a" > "$R/$a/passes.txt"
    ok=0
    tail -5 "$O" | grep -q "DIST CHECK PASS" || ok=1
    case "$a" in
        tf) grep -q "TARGET CHECK PASS" "$O" || ok=1 ;;
        *)  grep -q "VOUCHER CHECK PASS" "$O" || ok=1 ;;
    esac
    grep -q "GUARD" "$O" && ok=1
    grep -q -a "HANDOVER penalty_child_addicted" "$C/cfarm_${a}_2c/cf.log" || { note "GUARD: arm $a did not apply penalty_child_addicted"; ok=1; }
    [ "$rc" = 0 ] || ok=1
    if [ "$ok" = 0 ]; then note "arm $a ACCEPTED (exit $rc): $(tr '\n' ' ' < "$R/$a/checks.txt")"
    else note "arm $a NOT accepted (exit $rc): $(tail -3 "$O" | tr '\n' ' ')"; fi
    publish "$a finished"
    return $ok
)

# STAGE B: HOUSING FIRST
if [ -s "$R/null/net_target.txt" ] && [ -f "$C/cfarm_null_2c/cf.log" ]; then
    NT=$(cat "$R/null/net_target.txt"); note "null arm already accepted, net revenue $NT"
else
    run_arm null DRUG_PRICE_START=1.0 EXTRA_SET="$PENALTIES" || { publish "null not accepted, stopping"; exit 1; }
    NT=$(grep -a "^ *net_govt_revenues=" "$C/cfarm_null_2c/cf.log" | tail -1 | awk '{print $2}')
    echo "$NT" > "$R/null/net_target.txt"
fi
note "no-policy net revenue $NT is the TF budget target; test cost $CTEST (\$35)"

# STAGE C: TREATMENT FIRST, warm-started at the paper's tf85_c35 equilibrium (or the last published pass)
P0=0.8555; V0=0.0962
if [ -f "$R/status.txt" ]; then
    LAST=$(awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}' "$R/status.txt")
    [ -n "$LAST" ] && { P0=${LAST% *}; V0=${LAST#* }; note "resuming from the last published pass: price $P0, pi_V $V0"; }
fi
run_arm tf PDET=0.85 NET_TARGET="$NT" PV_START="$V0" DRUG_PRICE_START="$P0" EXTRA_SET="cost_per_drug_test $CTEST;$PENALTIES"
publish "complete"
