#!/bin/bash
# remote_treat2.sh -- Treatment First with vouchers conditional on being in treatment (12 October), the corrected
# version of remote_treat.sh treat: there the household with the disorder in treatment still failed the USE test, and
# since it keeps using the arm reproduced the paper's (see code/treat/patch_treat2.py). Here it passes both tests.
# The paper's arm otherwise: detection 0.85, the $35 test, the drug price and pi_V clearing against the paper's no-policy
# net revenue, warm-started at the paper's equilibrium. Build cf_fix2_treat2 (build_treat2.sh), arms through
# cf_arm_y.sh. Results to results/counterfactuals_2c/tf_treat2/.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/treat/remote_treat2.sh
# and run the same command again whenever the call is stopped: it ATTACHES to the running solve.
set -u
MODE=treat2; ARM=tf_treat2
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
NET_TARGET_NULL=5.8918410999831181
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
REF=$REPO/results/reference/hf_2c_omega_0.085
R=$REPO/results/counterfactuals_2c/$ARM
mkdir -p "$R"
D=$C/cf_point_$ARM
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export OMP_NUM_THREADS=4 SEED_FROM=bench DIAG_TAG=_2c
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat

note() { echo "remote_treat $ARM: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${CF_POINT_DETACHED:-0}" != 1 ]; then
    mkdir -p "$(dirname "$D")"
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_treat $ARM: attaching to the running solve, pid $(cat "$D.pid")"
    else
        ( CF_POINT_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/cf_point_$ARM.detached.log" 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_treat $ARM: started detached, pid $(cat "$D.pid"); log /tmp/cf_point_$ARM.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_treat $ARM: finished"; cat "$D.status" 2>/dev/null
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
        for a in null tf; do [ -f "$C/cfarm_${a}_2c/cf.log" ] && { echo; echo "== $a"; digest $a; grep -a "MILBY SPLIT" "$C/cfarm_${a}_2c/cf.log" | tail -1; }; done
        true
    } > "$R/passes.txt.tmp"; mv "$R/passes.txt.tmp" "$R/passes.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "$ARM: $1$TRAILER" || return 0
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
    env BUILD="$b" "$@" sh treat/cf_arm_y.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 &
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
    grep -a -q "MILBY SPLIT" "$C/cfarm_${a}_2c/cf.log" || { note "GUARD: no MILBY SPLIT line in the log"; ok=1; }
    grep -a "MILBY SPLIT" "$C/cfarm_${a}_2c/cf.log" | tail -1 > "$R/$a/milby_split.txt"
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
if [ ! -x "$C/cf_fix2_treat2/hftf_cf_prod" ]; then
    note "building cf_fix2_treat2"
    bash treat/build_treat2.sh > /tmp/treat_build.log 2>&1 || { note "GUARD: build failed: $(tail -3 /tmp/treat_build.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
publish "built, starting"

P0=0.85551291; V0=0.096152024   # the paper's tf85_c35 equilibrium
if [ -f "$R/passes.txt" ]; then
    LAST=$(awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}' "$R/passes.txt")
    [ -n "$LAST" ] && { P0=${LAST% *}; V0=${LAST#* }; note "resuming from the last published pass: price $P0, pi_V $V0"; }
fi
note "Treatment First, treatment meets the condition, use included; budget target $NET_TARGET_NULL; test cost $CTEST"
run_arm tf cf_fix2_treat2 PDET=0.85 NET_TARGET="$NET_TARGET_NULL" PV_START="$V0" DRUG_PRICE_START="$P0" EXTRA_SET="cost_per_drug_test $CTEST"
publish "complete"
