#!/bin/bash
# remote_nish_nodes_C.sh -- THE omega_c = 0.686 SENSITIVITY ON RULE C (12 October; the author: "all the stuff already in
# the paper should be redone for rule C", "start the simulations from guesses that equal each corresponding simulation
# with rule a"). remote_nish_nodes.sh with the Treatment First arm on the rule-C build (cf_fix2_treatC,
# treat/build_treatC.sh, through treat/cf_arm_C.sh), warm-started at rule A's converged price and pi_V for this economy
# (results/omega_nishiyama/nodes/tf/final.txt: 0.8494885, 0.095466831), or at this arm's own last published pass on a
# restart. Housing First (the null arm) has no screen and is NOT re-run: rule A's accepted null
# (results/omega_nishiyama/nodes/null, and cf/null with its net revenue, the budget target) is copied beside the new arm
# so the exporters find both. Results to results/omega_nishiyama_C/nodes/{tf,null} (export_nish_parts.py) and, once
# accepted, the same files to results/omega_nishiyama_C/cf/{tf,null} (export_results.py's x_nish_cev). A COPY.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root, and run it again whenever the call stops (it
# attaches):  bash code/omega_nishiyama/remote_nish_nodes_C.sh
set -u
ARM=nish_nodes_C
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
BREL=results/omega_nishiyama_2c/bench_0.686_b0.004510373_ku1.0
REF=$REPO/$BREL
A=$REPO/results/omega_nishiyama
RC=$REPO/results/omega_nishiyama_C
R=$RC/nodes
mkdir -p "$R"
D=$C/cf_point_$ARM
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
NET_TARGET_NULL=$(cat "$A/cf/null/net_target.txt")
export BENCH_FROM=$REF BENCH_B=0.004510373 BENCH_OMEGA=0.686 BENCH_KU=1.0 KAPPA_X=1.0688562125371026
export OMP_NUM_THREADS=4 SEED_FROM=bench DIAG_TAG=_2c
export PASSES_BASE="0.0904959779,0.0380110071,0.0060061733"
export CEV_CURVE=$D.welfare_curve.dat
NULLLOG=$D.null_cf.log   # rule A's null, unpacked, for finalstats and the digest

note() { echo "remote_nish_nodes_C: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${CF_POINT_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_nish_nodes_C: attaching to the running solve, pid $(cat "$D.pid")"
    else
        ( CF_POINT_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/cf_point_$ARM.detached.log" 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_nish_nodes_C: started detached, pid $(cat "$D.pid"); log /tmp/cf_point_$ARM.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_nish_nodes_C: finished"; cat "$D.status" 2>/dev/null
    grep -q "arm tf ACCEPTED" "$D.status" 2>/dev/null
    exit $?
fi

digest() ( cd "$C"; [ -f "$1" ] && python3 cf_runs/passes.py "$1" "$C/cf_runs/cev.py" 2>/dev/null )
publish() (
    {
        echo "# omega_c 0.686 sensitivity on RULE C, Treatment First against $BREL (b 0.004510373, kappa_uem 1.0, kappa_x $KAPPA_X; base $PASSES_BASE); Housing First is rule A's (no screen); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        [ -f "$NULLLOG" ] && { echo; echo "== null (rule A's, results/omega_nishiyama/nodes/null)"; digest "$NULLLOG"; }
        [ -f "$C/cfarm_tf_2c/cf.log" ] && { echo; echo "== tf"; digest "$C/cfarm_tf_2c/cf.log"; }
        true
    } > "$R/passes.txt.tmp"; mv "$R/passes.txt.tmp" "$R/passes.txt"
    cd "$REPO"
    git add "$RC" 2>/dev/null
    git commit -q -m "omega_c 0.686 on rule C: $1$TRAILER" || return 0
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
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"

# Housing First: rule A's accepted null, reused (it has no screen)
for d in nodes/null cf/null; do
    [ -f "$RC/$d/final.txt" ] && continue
    mkdir -p "$RC/$d"; cp "$A/$d"/* "$RC/$d/"
done
grep -q "VOUCHER CHECK PASS" "$RC/nodes/null/checks.txt" && [ "$(grep -c . "$RC/nodes/null/value_at_26_by_node.txt")" = 26 ] \
    || { note "GUARD: rule A's null lacks its checks or its 26-node values"; publish "failed"; exit 1; }
gunzip -c "$RC/nodes/null/cf.log.gz" > "$NULLLOG"
note "Housing First reused from rule A (results/omega_nishiyama/nodes/null, cf/null); budget target $NET_TARGET_NULL"

cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && continue
    note "building $b"
    bash "cf_runs/build_$b.sh" > "/tmp/nishC_build_$b.log" 2>&1 || { note "GUARD: build $b failed: $(tail -3 /tmp/nishC_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
[ -x "$C/cf_fix2_treatC/hftf_cf_prod" ] || { note "building cf_fix2_treatC (rule C)"; bash treat/build_treatC.sh > /tmp/nishC_build_treatC.log 2>&1 || { note "GUARD: build cf_fix2_treatC failed: $(tail -3 /tmp/nishC_build_treatC.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
grep -q "RULE C (patch_treatC.py)" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: cf_fix2_treatC is not rule C"; publish "failed"; exit 1; }
publish "built, starting"

# TREATMENT FIRST on rule C: rule A's converged values for this economy, or this arm's own last published pass
P0=0.8494885; V0=0.095466831
LAST=$(awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}' "$R/passes.txt" 2>/dev/null)
if [ -n "$LAST" ]; then P0=${LAST% *}; V0=${LAST#* }; note "resuming from this arm's last published pass: price $P0, pi_V $V0"
else note "warm start at rule A's converged values for this economy: price $P0, pi_V $V0"; fi

a=tf
note "arm tf on cf_fix2_treatC (rule C): PDET=0.85 NET_TARGET=$NET_TARGET_NULL PV_START=$V0 DRUG_PRICE_START=$P0 test $CTEST"
env BUILD=cf_fix2_treatC PDET=0.85 NET_TARGET="$NET_TARGET_NULL" PV_START="$V0" DRUG_PRICE_START="$P0" \
    EXTRA_SET="cost_per_drug_test $CTEST" sh treat/cf_arm_C.sh tf > "$C/cfarm_tf_2c.out" 2>&1 &
P=$!
while kill -0 "$P" 2>/dev/null; do
    for _ in $(seq 1 120); do kill -0 "$P" 2>/dev/null || break; sleep 10; done
    kill -0 "$P" 2>/dev/null && publish "tf running, $(grep -ac '^ *distance_govt_budget=' "$C/cfarm_tf_2c/cf.log" 2>/dev/null) passes"
done
wait "$P"; rc=$?
O="$C/cfarm_tf_2c.out"
T=$R/tf; mkdir -p "$T"
gzip -c "$O" > "$T/run.out.gz"
[ -f "$C/cfarm_tf_2c/cf.log" ] && gzip -c "$C/cfarm_tf_2c/cf.log" > "$T/cf.log.gz"
[ -f "$C/cfarm_tf_2c/PARAM_HANDOVER.arm.txt" ] && cp "$C/cfarm_tf_2c/PARAM_HANDOVER.arm.txt" "$T/"
grep -a "CHECK PASS\|GUARD" "$O" > "$T/checks.txt"
[ -f "$C/cfarm_tf_2c/cf.log" ] && python3 cf_runs/finalstats.py "$C/cfarm_tf_2c/cf.log" "$NULLLOG" > "$T/final.txt" 2>&1
digest "$C/cfarm_tf_2c/cf.log" > "$T/passes.txt"
grep -a "MILBY SPLIT" "$C/cfarm_tf_2c/cf.log" | tail -3 > "$T/milby.txt"
ok=0
tail -5 "$O" | grep -q "DIST CHECK PASS" || ok=1
grep -q "TARGET CHECK PASS" "$O" || ok=1
grep -q "GUARD" "$O" && ok=1
grep -q "RULE C" "$C/cf_fix2_treatC/cf.f90" || ok=1
cp "$C/cfarm_tf_2c/welfare_by_employment_youngestcounter_arm.txt" "$T/value_at_26_by_node.txt" 2>/dev/null
[ "$(grep -c . "$T/value_at_26_by_node.txt" 2>/dev/null)" = 26 ] || { note "GUARD: no 26-node value file for tf"; ok=1; }
[ "$rc" = 0 ] || ok=1
if [ "$ok" = 0 ]; then
    note "arm tf ACCEPTED (exit $rc): $(tr '\n' ' ' < "$T/checks.txt")"
    mkdir -p "$RC/cf/tf"; cp "$T"/* "$RC/cf/tf/"
    # export_results.py reads the benchmark's omega_c off cf/passes.txt's first line
    publish "tf finished"; cp "$R/passes.txt" "$RC/cf/passes.txt"
else note "arm tf NOT accepted (exit $rc): $(tail -3 "$O" | tr '\n' ' ')"; fi
publish "complete"
