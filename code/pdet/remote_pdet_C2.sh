#!/bin/bash
# remote_pdet_C2.sh <p_det> -- remote_pdet_C.sh with P0_START/V0_START (the rule-A arm's values) as the warm start. A COPY.
# remote_pdet_C.sh <p_det> -- RULE C (12 October; the author: "all the stuff already in the paper should be redone for
# rule C"). remote_pdet.sh with Treatment First on the rule-C build (cf_fix2_treatC via treat/build_treatC.sh, through
# treat/cf_arm_C.sh), warm-started at the rule-C main arm's latest published pass. Results to
# results/counterfactuals_2c/tf_pdet<p_det>_C/. remote_pdet.sh's header follows.
# remote_pdet.sh <p_det> -- TREATMENT FIRST AT A WEAKER DETECTION RATE (11 October). The referee: "Report welfare at
# half the deterrence"; the paper's footnote claims the results hold at 70 percent on arms from an older calibration.
# One rate per container: the paper's arm exactly (remote_cf_tf_c35.sh: the benchmark of record from
# results/reference/hf_2c_omega_0.085, cf_fix2, the $35 test, the drug price and pi_V clearing against the paper's
# no-policy net revenue 5.8918410999831181) with probability_of_detection <p_det> instead of 0.85, warm-started at
# the paper's tf85_c35 equilibrium. Results to results/counterfactuals_2c/tf_pdet<p_det>/.
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/pdet/remote_pdet.sh 0.70
# and run the same command again whenever the call is stopped: it ATTACHES to the running solve. Every 20 minutes it
# pushes the passes so far; at the end passes.txt, final.txt, the checks, cf.log.gz and run.out.gz.
set -u
PDET=${1:?detection rate, e.g. 0.70 or 0.50}
ARM=tf_pdet$(python3 -c "print('%02d' % round(100*$PDET))")_C
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

note() { echo "remote_pdet $ARM: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${CF_POINT_DETACHED:-0}" != 1 ]; then
    mkdir -p "$(dirname "$D")"
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_pdet $ARM: attaching to the running solve, pid $(cat "$D.pid")"
    else
        ( CF_POINT_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/cf_point_$ARM.detached.log" 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_pdet $ARM: started detached, pid $(cat "$D.pid"); log /tmp/cf_point_$ARM.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_pdet $ARM: finished"; cat "$D.status" 2>/dev/null
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
        echo "# counterfactual $ARM (detection $PDET) against results/reference/hf_2c_omega_0.085 (omega_c 0.085, b 0.0054222, kappa_uem 1.0, kappa_x 0.934236); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        [ -f "$C/cfarm_tf_2c/cf.log" ] && { echo; echo "== tf"; digest tf; }
        true
    } > "$R/passes.txt.tmp"; mv "$R/passes.txt.tmp" "$R/passes.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "counterfactual $ARM (detection $PDET): $1$TRAILER" || return 0
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
    env BUILD="$b" "$@" sh treat/cf_arm_C.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 &
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
    [ -f "$C/cfarm_${a}_2c/cf.log" ] && python3 "$C/cf_runs/finalstats.py" "$C/cfarm_${a}_2c/cf.log" > "$R/$a/final.txt" 2>&1
    digest "$a" > "$R/$a/passes.txt"
    ok=0
    tail -5 "$O" | grep -q "DIST CHECK PASS" || ok=1
    grep -q "TARGET CHECK PASS" "$O" || ok=1
    grep -q "GUARD" "$O" && ok=1
    grep -qx "probability_of_detection $PDET" "$C/cfarm_${a}_2c/PARAM_HANDOVER.arm.txt" 2>/dev/null || { note "GUARD: the arm's handover does not carry probability_of_detection $PDET"; ok=1; }
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
    bash "cf_runs/build_$b.sh" > "/tmp/cf_point_build_$b.log" 2>&1 || {
        note "GUARD: build $b failed: $(tail -3 /tmp/cf_point_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
publish "built, starting"

[ -x "$C/cf_fix2_treatC/hftf_cf_prod" ] || { note "building cf_fix2_treatC (rule C)"; bash treat/build_treatC.sh > /tmp/pdetC_build.log 2>&1 || { note "GUARD: build cf_fix2_treatC failed: $(tail -3 /tmp/pdetC_build.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
grep -q "RULE C (patch_treatC.py)" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: cf_fix2_treatC is not rule C"; publish "failed"; exit 1; }
P0=0.8555; V0=0.0962   # rule A's tf85_c35 equilibrium, replaced by the rule-C main arm's latest pass when there is one
LASTC=$(awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}' "$REPO/results/counterfactuals_2c/tf_ruleC/passes.txt" 2>/dev/null)
[ -n "$LASTC" ] && { P0=${LASTC% *}; V0=${LASTC#* }; note "warm start at the rule-C main arm's latest pass: price $P0, pi_V $V0"; }
# THE AUTHOR, 12 Oct: "we can start the simulations from guesses that equal each corresponding simulation with rule a".
# P0_START and V0_START, when given, are that arm's rule-A values; a restart still resumes from this arm's own passes.
[ -n "${P0_START:-}" ] && [ -n "${V0_START:-}" ] && { P0=$P0_START; V0=$V0_START; note "warm start at the rule-A arm's values: price $P0, pi_V $V0"; }
if [ -f "$R/passes.txt" ]; then
    LAST=$(awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}' "$R/passes.txt")
    [ -n "$LAST" ] && { P0=${LAST% *}; V0=${LAST#* }; note "resuming from the last published pass: price $P0, pi_V $V0"; }
fi
note "TF budget target: the paper's no-policy net revenue $NET_TARGET_NULL; test cost $CTEST (\$35); detection $PDET"
run_arm tf cf_fix2_treatC PDET="$PDET" NET_TARGET="$NET_TARGET_NULL" PV_START="$V0" DRUG_PRICE_START="$P0" EXTRA_SET="cost_per_drug_test $CTEST"
publish "complete"
