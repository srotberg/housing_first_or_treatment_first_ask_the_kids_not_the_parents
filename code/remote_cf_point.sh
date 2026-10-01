#!/bin/bash
# remote_cf_point.sh <arm> -- one steady-state counterfactual against the omega_c = 0.085
# two-class benchmark (stage C of code/OVERNIGHT_PLAN.md), for a cloud worker.
#
#   arm = omega1        the parent counts the child fully (optimal SUD)
#         internalise   the homeless bear kappa_x (optimal homelessness)
#         nulltf        no policy, then rationed Treatment First at 85 per cent detection,
#                       cleared against the no-policy run's net revenue
#
# The benchmark is NOT re-solved: cf_arm.sh takes it from results/reference/hf_2c_omega_0.085
# (BENCH_FROM), the run the author chose on 1 October. Each arm warm-starts its drug price (and
# TF its pi_V) at the old arm's equilibrium (results/counterfactuals_cf_fix2/<arm>/final.txt):
# the author, 1 October, "you may be able to use the old equilibria values from other
# simulations to speed things up".
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root, and run the same
# command again whenever the call is stopped: it ATTACHES to the running solve (the detach is
# remote_omega_point.sh's, which survived the 2-hour limit on 1 October). Every 20 minutes it
# pushes the passes so far to results/counterfactuals_2c/<arm>/passes.txt; at the end it
# pushes passes.txt, final.txt, the checks, cf.log.gz and run.out.gz, and RESULT.md.
set -u
ARM="$1"
case "$ARM" in omega1|internalise|nulltf) ;; *) echo "usage: $0 omega1|internalise|nulltf [drug price start]"; exit 1 ;; esac
# OPTIONAL SECOND ARGUMENT: the drug price the arm starts from, overriding the old arm's equilibrium.
# The price moves at most 0.5 per cent a pass, so a warm start far from the new equilibrium costs
# passes rather than saving them: omega1 started at the old 0.863 sat at 0.87 after two passes
# while its supply curve implied about 0.98 (1 October, 21:10). Its runs publish to <arm>_p<price>.
PSTART="${2:-}"
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$C/.." && pwd)
REF=$REPO/results/reference/hf_2c_omega_0.085
R=$REPO/results/counterfactuals_2c/$ARM${PSTART:+_p$PSTART}
mkdir -p "$R"
D=$C/cf_point_$ARM${PSTART:+_p$PSTART}
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
# the benchmark: b*, omega_c and kappa_uem of the run, kappa_x on the income basis
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export OMP_NUM_THREADS=2 SEED_FROM=bench DIAG_TAG=_2c
# passes.py measures changes against THIS benchmark and its CEV on THIS benchmark's curve
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat

note() { echo "remote_cf_point $ARM: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${CF_POINT_DETACHED:-0}" != 1 ]; then
    mkdir -p "$(dirname "$D")"
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_cf_point $ARM: attaching to the running solve, pid $(cat "$D.pid")"
    else
        ( CF_POINT_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/cf_point_$ARM.detached.log" 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_cf_point $ARM: started detached, pid $(cat "$D.pid"); log /tmp/cf_point_$ARM.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_cf_point $ARM: finished"; cat "$D.status" 2>/dev/null
    grep -q "ACCEPTED" "$D.status" 2>/dev/null
    exit $?
fi

# digest <sub-arm>: passes so far, from the arm's own log
digest() (
    cd "$C"
    L="cfarm_${1}_2c/cf.log"
    [ -f "$L" ] && python3 cf_runs/passes.py "$L" "$C/cf_runs/cev.py" 2>/dev/null
)
publish() (
    {
        echo "# counterfactual $ARM against results/reference/hf_2c_omega_0.085 (omega_c 0.085, b 0.0054222, kappa_uem 1.0, kappa_x 0.934236); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for a in null omega1 internalise tf; do
            [ -f "$C/cfarm_${a}_2c/cf.log" ] && { echo; echo "== $a"; digest "$a"; }
        done
        true
    } > "$R/passes.txt.tmp"; mv "$R/passes.txt.tmp" "$R/passes.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "counterfactual $ARM (omega_c 0.085): $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)

# run_arm <cf_arm.sh arm> <build> [VAR=value ...]: one arm, published every 20 minutes;
# returns 0 only if its checks pass
run_arm() (
    a=$1; b=$2; shift 2
    cd "$C"
    note "arm $a on $b: $*"
    env BUILD="$b" "$@" sh cf_runs/cf_arm.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 &
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
    [ "$rc" = 0 ] || ok=1
    if [ "$ok" = 0 ]; then note "arm $a ACCEPTED (exit $rc): $(tr '\n' ' ' < "$R/$a/checks.txt")"
    else note "arm $a NOT accepted (exit $rc): $(tail -3 "$O" | tr '\n' ' ')"; fi
    publish "$a finished"
    return $ok
)

: > "$D.status"
command -v gfortran >/dev/null 2>&1 || {
    note "gfortran missing, installing"
    apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1
}
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"

# THE BUILDS, SEQUENTIALLY (cf_runs/README.md): cf_fix, then cf_fix2, and the damped build for
# internalise, which cycled on cf_fix2 on 26 September and converged on cf_fix2_damp
cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && continue
    note "building $b"
    bash "cf_runs/build_$b.sh" > "/tmp/cf_point_build_$b.log" 2>&1 || {
        note "GUARD: build $b failed: $(tail -3 /tmp/cf_point_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
if [ "$ARM" = internalise ] && [ ! -x "$C/cf_fix2_damp/hftf_cf_prod" ]; then
    note "building cf_fix2_damp"
    bash cf_runs/build_cf_fix2_damp.sh > /tmp/cf_point_build_damp.log 2>&1 || {
        note "GUARD: build cf_fix2_damp failed"; publish "failed"; exit 1; }
fi
publish "built, starting"

case "$ARM" in
    omega1)
        run_arm omega1 cf_fix2 DRUG_PRICE_START=${PSTART:-0.863} ;;
    internalise)
        run_arm internalise cf_fix2_damp DRUG_PRICE_START=${PSTART:-0.995} ;;
    nulltf)
        if run_arm null cf_fix2 DRUG_PRICE_START=1.0; then
            NT=$(grep -a "^ *net_govt_revenues=" "$C/cfarm_null_2c/cf.log" | tail -1 | awk '{print $2}')
            note "no-policy net revenue $NT is the TF budget target"
            run_arm tf cf_fix2 PDET=0.85 NET_TARGET="$NT" PV_START=0.0814 DRUG_PRICE_START=${PSTART:-0.867}
        fi ;;
esac
publish "complete"
