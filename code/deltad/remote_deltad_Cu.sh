#!/bin/bash
# remote_deltad_Cu.sh <delta_d> -- A COPY of remote_deltad.sh (18 October; the author: "can you add in the lit review a
# footnote saying that even if we use delta_d=0 and half, the qualitative results continue to hold?", then "please do
# these checks then for the long run" and "you have to solve the benchmark for each first, and then the long run").
# The same three stages on the CURRENT model:
#   STAGE A, the benchmark: unchanged (the benchmark of record's handover with penalty_child_addicted <delta_d>, every
#     adjuster frozen, omega_c pinned), so every other parameter is as calibrated.
#   STAGE B, Housing First re-solved against that benchmark on the CORRECTED build (cf_fix2_share_treatCu,
#     treat/cf_arm_Cu.sh, the internal_computations fix ungated), the drug price clearing and pi_V held; its net
#     revenue is the budget target.
#   STAGE C, Treatment First as the paper's main arm: RULE C (cf_fix2_treatC, treat/cf_arm_C.sh), detection 0.20, the
#     $35 test, the drug price and pi_V clearing, warm-started at the main arm's equilibrium (0.946231, 0.078054).
#   STAGE D, the newborn values (cf_kid_C, share_newborns.py) and the files the welfare split reads, as
#     extra_2c/newborn_Cu4.sh and collect_shares_Cu4.sh do for the paper's columns.
# Results to results/deltad_Cu/dd<delta_d>/, worker files code/deltadCu_*. remote_deltad.sh's header follows.
# remote_deltad.sh <delta_d> -- THE delta_d SCAN (11 October). The referee: "Report full general-equilibrium results at
# delta_d = 0, 0.05 and 0.12"; the author: "work on all of them", "run tests in parallel sessions". One value per
# container, each the paper's own build and recipe with the child earnings penalty set to <delta_d> and EVERY OTHER
# PARAMETER AS CALIBRATED:
#   STAGE A, the benchmark: the benchmark of record's handover (results/reference/hf_2c_omega_0.085, omega_c 0.085,
#     b 0.0054222, kappa_uem 1.0, kappa_x 0.934236) with penalty_child_addicted <delta_d>, every adjuster frozen and
#     omega_c pinned (as that benchmark itself was solved), on code/bench_tdm_childsplit/hftf_bench, warm-started from
#     code/scan_seed as remote_omega_point.sh starts every benchmark point.
#   STAGE B, Housing First re-solved on code/cf_fix2 against that benchmark (the null arm: the drug price clears,
#     pi_V held), its net revenue the budget target.
#   STAGE C, Treatment First as the paper's arm: detection 0.85, the $35 test, the drug price and pi_V clearing,
#     warm-started at the paper's tf85_c35 equilibrium.
# The welfare gain is CEV(tf) - CEV(null), each the arm's cf.log 'CEV from the saved benchmark curve' line, read the
# paper's way afterwards by code/paper/welfare_nok.py. Results to results/deltad/dd<delta_d>/.
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/deltad/remote_deltad.sh 0.05
# and run the same command again whenever the call is stopped: it ATTACHES to the running work. Every 20 minutes it
# pushes results/deltad/dd<delta_d>/status.txt; a restart skips what is done (the benchmark, then the null arm).
set -u
DD=${1:?delta_d value: 0 or 0.12}
TAG=dd$DD
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
R=$REPO/results/deltad_Cu/$TAG
mkdir -p "$R"
D=$C/deltadCu_run_$TAG
REF=$REPO/results/reference/hf_2c_omega_0.085
SEED=$C/scan_seed
BD=$C/deltadCu_bench_$TAG
BREF=$C/deltadCu_benchref_$TAG
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
KX=0.9342362271804227; BV=0.0054222; W=0.085
PENALTIES="penalty_child_addicted $DD"
BLOCKS=${BLOCKS:-16}
DSIZE=265496400

note() { echo "remote_deltad_Cu $TAG: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${DELTADCU_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_deltad_Cu $TAG: attaching to the running work, pid $(cat "$D.pid")"
    else
        ( DELTADCU_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/deltadCu_$TAG.detached.log" 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_deltad $TAG: started detached, pid $(cat "$D.pid"); log /tmp/deltadCu_$TAG.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_deltad_Cu $TAG: finished"; cat "$D.status" 2>/dev/null
    grep -q "STAGE D done" "$D.status" 2>/dev/null
    exit $?
fi

digest() (
    cd "$C"
    L="cfarm_${1}_2c/cf.log"
    [ -f "$L" ] && python3 cf_runs/passes.py "$L" "$C/cf_runs/cev.py" 2>/dev/null
)
publish() (
    {
        echo "# delta_d $DD, every other parameter as calibrated, the current model: corrected Housing First, rule C, detection 0.20 (code/deltad/remote_deltad_Cu.sh); $(date -u '+%d %b %H:%M UTC')"
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
    git commit -q -m "delta_d check (current model) $TAG: $1$TRAILER" || return 0
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
if [ ! -x "$C/bench_tdm_childsplit/hftf_bench" ]; then
    note "building the benchmark binary of record"
    bash build_bench_tdm_childsplit.sh > /tmp/deltad_build_bench.log 2>&1 || {
        note "GUARD: benchmark build failed: $(tail -3 /tmp/deltad_build_bench.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && continue
    note "building $b"
    bash "cf_runs/build_$b.sh" > "/tmp/deltad_build_$b.log" 2>&1 || {
        note "GUARD: build $b failed: $(tail -3 /tmp/deltad_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
[ -x "$C/cf_fix2_share/hftf_cf_prod" ] || { note "building cf_fix2_share"; bash transition_fix/build_cf_fix2_share.sh > /tmp/dd_build_share.log 2>&1 || { note "GUARD: build cf_fix2_share failed"; publish "failed"; exit 1; }; }
[ -x "$C/cf_fix2_share_treatCu/hftf_cf_prod" ] || { note "building cf_fix2_share_treatCu (Housing First, internal_computations fix ungated)"; bash treat/build_share_treatCu.sh > /tmp/dd_build_shareCu.log 2>&1 || { note "GUARD: build cf_fix2_share_treatCu failed: $(tail -3 /tmp/dd_build_shareCu.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
grep -q "INTERNAL UNGATED (patch_treatCu.py)" "$C/cf_fix2_share_treatCu/cf.f90" || { note "GUARD: cf_fix2_share_treatCu is not ungated"; publish "failed"; exit 1; }
[ -x "$C/cf_fix2_treatC/hftf_cf_prod" ] || { note "building cf_fix2_treatC (rule C)"; bash treat/build_treatC.sh > /tmp/dd_build_treatC.log 2>&1 || { note "GUARD: build cf_fix2_treatC failed: $(tail -3 /tmp/dd_build_treatC.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
grep -q "RULE C (patch_treatC.py)" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: cf_fix2_treatC is not rule C"; publish "failed"; exit 1; }
[ -x "$C/cf_kid_C/hftf_cf_kid" ] || { note "building cf_kid_C"; bash cf_kid/build_C.sh "$C/cf_kid_C" > /tmp/dd_build_kid.log 2>&1 || { note "GUARD: cf_kid/build_C.sh failed: $(tail -3 /tmp/dd_build_kid.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
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
    setl penalty_child_addicted $DD
    setl omega_c_is_pinned 1
    setl freeze_all_but_omega_c 1
    setl weight_on_child $W
    setl addiction_scalar_1 $BV
    setl kappa_uem 1.0
    setl kappa_x $KX
    setl frozen_stop_after_blocks $BLOCKS
    cp PARAM_HANDOVER.txt PARAM_HANDOVER.kept.txt
    cp "$C/bench_tdm_childsplit/hftf_bench" ./hftf_bench
    note "benchmark: solving from the scan seed, delta_d $DD, at most $BLOCKS frozen blocks"
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
    if [ "$a" = null ]; then B=cf_fix2_share_treatCu; S=treat/cf_arm_Cu.sh; else B=cf_fix2_treatC; S=treat/cf_arm_C.sh; fi
    note "arm $a on $B ($S): $*"
    env BUILD=$B "$@" sh $S "$a" > "$C/cfarm_${a}_2c.out" 2>&1 &
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
    run_arm null DRUG_PRICE_START=0.99938969 EXTRA_SET="$PENALTIES" || { publish "null not accepted, stopping"; exit 1; }
    NT=$(grep -a "^ *net_govt_revenues=" "$C/cfarm_null_2c/cf.log" | tail -1 | awk '{print $2}')
    echo "$NT" > "$R/null/net_target.txt"
fi
note "no-policy net revenue $NT is the TF budget target; test cost $CTEST (\$35)"

# STAGE C: TREATMENT FIRST, rule C at detection 0.20, warm-started at the paper's main arm (or the last published pass)
P0=0.946231; V0=0.078054
if [ -f "$R/status.txt" ]; then
    LAST=$(awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}' "$R/status.txt")
    [ -n "$LAST" ] && { P0=${LAST% *}; V0=${LAST#* }; note "resuming from the last published pass: price $P0, pi_V $V0"; }
fi
run_arm tf PDET=0.20 NET_TARGET="$NT" PV_START="$V0" DRUG_PRICE_START="$P0" EXTRA_SET="cost_per_drug_test $CTEST;$PENALTIES"
[ -f "$C/cfarm_tf_2c/cf.log" ] || { note "GUARD: no Treatment First log"; publish "failed"; exit 1; }

# STAGE D: newborn values (cf_kid_C) and the files the welfare split reads
cd "$C"
python3 transition_2c/shares.py cfarm_tf_2c cfarm_null_2c counter_arm > "$R/shares.txt" 2>&1 \
    && note "shares: $(grep 'all households' "$R/shares.txt" | head -1 | tr -s ' ')" || note "shares.py failed: $(tail -2 "$R/shares.txt" | tr '\n' ' ')"
mkdir -p "$D.newborn"
for a in null_2c tf_2c; do
    [ -s "$D.newborn/$a/child_value_at_birth_partscounter_arm.dat" ] && continue
    rm -rf "$D.newborn/$a"
    note "cf_kid_C on $a"
    BIN=$C/cf_kid_C/hftf_cf_kid FORCE_BUILD=1 THREADS=4 sh cf_kid/run_child_value.sh "$C/cfarm_$a" "$D.newborn/$a" > "$R/cf_kid_$a.out" 2>&1 \
        || { note "GUARD: cf_kid_C on $a failed: $(tail -3 "$R/cf_kid_$a.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
done
python3 cf_kid/share_newborns.py --tf "$D.newborn/tf_2c" --hf "$D.newborn/null_2c" --json "$R/newborn_shares.json" > "$R/newborn_shares.txt" 2>&1 \
    && note "newborns: $(grep -i -m1 'better' "$R/newborn_shares.txt" | tr -s ' ')" || note "share_newborns failed: $(tail -3 "$R/newborn_shares.txt" | tr '\n' ' ')"
for a in tf null; do
    d=$C/cfarm_${a}_2c; mkdir -p "$R/$a"
    [ -f "$d/welfare_by_employment_youngestcounter_arm.txt" ] && cp "$d/welfare_by_employment_youngestcounter_arm.txt" "$R/$a/value_at_26_by_node.txt"
    grep -a "MILBY SPLIT" "$d/cf.log" 2>/dev/null | tail -1 > "$R/$a/milby_split.txt"
done
note "STAGE D done"
publish "complete"
