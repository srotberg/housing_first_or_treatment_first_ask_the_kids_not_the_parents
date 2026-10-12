#!/bin/bash
# remote_nish_nodes.sh -- THE omega_c = 0.686 ARMS AGAIN, FOR THEIR VALUES BY NODE (12 October; the author, on the footnote's
# split of the sensitivity's gain: "no, i meant to break it down by externalities and non-externalities!"). Splitting the
# gain as Table 6 does needs each arm's value at 26 by entry node (welfare_by_employment_youngestcounter_arm.txt), which the
# runs of 10 October did not keep. Housing First and Treatment First are re-solved exactly as then (code/omega_nishiyama/
# remote_cf_nishiyama.sh: the benchmark results/omega_nishiyama_2c/bench_0.686_b0.004510373_ku1.0, cf_fix2, the $35 test,
# detection 0.85, the price and pi_V clearing against the null's net revenue), warm-started at their converged prices, the
# two in parallel. Results to results/omega_nishiyama/nodes/{null,tf}/ with value_at_26_by_node.txt.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/omega_nishiyama/remote_nish_nodes.sh
set -u
ARM=nish_nodes
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
NET_TARGET_NULL=$(cat "$(cd "$(dirname "$0")/../.." && pwd)/results/omega_nishiyama/cf/null/net_target.txt")
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
REF=$REPO/results/omega_nishiyama_2c/bench_0.686_b0.004510373_ku1.0
R=$REPO/results/omega_nishiyama/nodes
mkdir -p "$R"
D=$C/cf_point_$ARM
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
export BENCH_FROM=$REF BENCH_B=0.004510373 BENCH_OMEGA=0.686 BENCH_KU=1.0 KAPPA_X=1.0688562125371026
export OMP_NUM_THREADS=4 SEED_FROM=bench DIAG_TAG=_2c
export PASSES_BASE="0.0904959779,0.0380110071,0.0060061733"
export CEV_CURVE=$D.welfare_curve.dat

note() { echo "remote_nish_nodes: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${CF_POINT_DETACHED:-0}" != 1 ]; then
    mkdir -p "$(dirname "$D")"
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_nish_nodes: attaching to the running solve, pid $(cat "$D.pid")"
    else
        ( CF_POINT_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/cf_point_$ARM.detached.log" 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_nish_nodes: started detached, pid $(cat "$D.pid"); log /tmp/cf_point_$ARM.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_nish_nodes: finished"; cat "$D.status" 2>/dev/null
    grep -q "ACCEPTED" "$D.status" 2>/dev/null
    exit $?
fi

digest() (
    cd "$C"
    L="cfarm_${1}_2c/cf.log"
    [ -f "$L" ] && python3 cf_runs/passes.py "$L" "$C/cf_runs/cev.py" 2>/dev/null
)
publish() (
    {
        echo "# $ARM against results/reference/hf_2c_omega_0.085 (omega_c 0.085, b 0.0054222, kappa_uem 1.0, kappa_x 0.934236); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for a in null tf; do [ -f "$C/cfarm_${a}_2c/cf.log" ] && { echo; echo "== $a"; digest $a; }; done
        true
    } > "$R/passes.txt.tmp"; mv "$R/passes.txt.tmp" "$R/passes.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "omega_c 0.686 arms by node: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)

run_arm() (
    a=$1; b=$2; shift 2
    cd "$C"
    note "arm $a on $b: $*"
    env BUILD="$b" "$@" sh cf_runs/cf_arm_set.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 &
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
    case "$a" in tf) grep -q "TARGET CHECK PASS" "$O" || ok=1 ;; *) grep -q "VOUCHER CHECK PASS" "$O" || ok=1 ;; esac
    grep -q "GUARD" "$O" && ok=1
    cp "$C/cfarm_${a}_2c/welfare_by_employment_youngestcounter_arm.txt" "$R/$a/value_at_26_by_node.txt" 2>/dev/null
    [ "$(grep -c . "$R/$a/value_at_26_by_node.txt" 2>/dev/null)" = 26 ] || { note "GUARD: no 26-node value file for $a"; ok=1; }
    [ "$rc" = 0 ] || ok=1
    if [ "$ok" = 0 ]; then note "arm $a ACCEPTED (exit $rc): $(tr '\n' ' ' < "$R/$a/checks.txt")"
    else note "arm $a NOT accepted (exit $rc): $(tail -3 "$O" | tr '\n' ' ')"; fi
    publish "$a finished"
    return $ok
)

[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"
command -v gfortran >/dev/null 2>&1 || {
    note "gfortran missing, installing"
    apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1
}
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"

cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && continue
    note "building $b"
    bash "cf_runs/build_$b.sh" > "/tmp/nish_build_$b.log" 2>&1 || { note "GUARD: build $b failed: $(tail -3 /tmp/nish_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"
publish "built, starting"

P0=0.8495162; V0=0.095426492   # the sensitivity's converged Treatment First (results/omega_nishiyama/cf/tf/final.txt)
note "the two arms, warm-started at their converged prices, in parallel; budget target $NET_TARGET_NULL"
run_arm null cf_fix2 DRUG_PRICE_START=1.0000345 &
for _ in $(seq 1 360); do [ -f "$C/cfarm_bench/BENCH_DONE" ] && break; sleep 10; done
run_arm tf cf_fix2 PDET=0.85 NET_TARGET="$NET_TARGET_NULL" PV_START="$V0" DRUG_PRICE_START="$P0" EXTRA_SET="cost_per_drug_test $CTEST" &
wait
publish "complete"
