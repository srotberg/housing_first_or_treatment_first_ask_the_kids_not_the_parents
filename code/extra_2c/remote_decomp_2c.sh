#!/bin/bash
# remote_decomp_2c.sh -- THE TWO DECOMPOSITIONS OF TREATMENT FIRST'S LONG RUN on the omega_c = 0.085 economy,
# for one cloud worker (2 October; the author: "yes. both", to "decomposition runs (pi_V held at the benchmark,
# price held at the benchmark)"). Each is the $35, 85 per cent Treatment First arm of stage E with one
# equilibrium channel shut:
#
#   fixpv  pi_V held at the no-policy value (0.0675...): the budget is NOT cleared (adjust_taxes 0), so what
#          the screen saves and the higher taxes bring in are not spent on more vouchers. The drug price clears.
#   fixp   the drug price held at the no-policy value (1.0001...): drug_market_adjuster 0 freezes it and the
#          source drops the drug market from the stopping test. pi_V clears the budget as in the arm.
#
# Against the accepted arms (results/counterfactuals_2c/nulltf/null and tf85_c35/tf, and stage E's re-solve)
# the difference between tf and fixpv is what recycling the revenue into vouchers does; tf against fixp is what
# the cheaper drug does.
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/extra_2c/remote_decomp_2c.sh
# Run it again if the container restarts: an arm whose checks passed is not run again; one that was killed is.
# Every 20 minutes it pushes results/decomp_2c/status.txt.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
E=$(cd "$(dirname "$0")" && pwd)
C=$(cd "$E/.." && pwd)
REPO=$(cd "$C/.." && pwd)
REF=$REPO/results/reference/hf_2c_omega_0.085
R=$REPO/results/decomp_2c
mkdir -p "$R"
D=$C/decomp_worker
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
NET_TARGET=5.8918410999831181                 # the accepted no-policy run's net revenue (tf85_c35's target)
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
P_NULL=1.0001082; V_NULL=0.067533863          # results/counterfactuals_2c/nulltf/null/final.txt
P_TF=0.85551291;  V_TF=0.096152024            # results/counterfactuals_2c/tf85_c35/tf/final.txt
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export SEED_FROM=bench
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat

note() { echo "remote_decomp_2c: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${DECOMP_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_decomp_2c: attaching to the running worker, pid $(cat "$D.pid")"
    else
        ( DECOMP_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/decomp.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_decomp_2c: started detached, pid $(cat "$D.pid"); log /tmp/decomp.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_decomp_2c: finished"; cat "$D.status" 2>/dev/null
    exit 0
fi

publish() (
    {
        echo "# the two decompositions of Treatment First's long run, omega_c = 0.085; $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for a in fixpv fixp; do
            L="$C/cfarm_tf_2c_$a/cf.log"
            [ -f "$L" ] && { echo; echo "== arm $a"; python3 "$C/cf_runs/passes.py" "$L" "$C/cf_runs/cev.py" 2>/dev/null; }
        done
        true
    } > "$R/status.txt"
    cd "$REPO" || exit 0
    git add "$R" 2>/dev/null
    git commit -q -m "decomp 2c: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)

# arm <name> [VAR=value ...]: Treatment First in code/cfarm_tf_2c_<name>, in the background
arm() {
    a=$1; shift
    note "arm $a: $*"
    ( cd "$C" && env BUILD=cf_fix2 OMP_NUM_THREADS=2 DIAG_TAG="_2c_$a" "$@" sh transition_2c/cf_arm_tr2c.sh tf \
        > "$C/cfarm_tf_2c_$a.out" 2>&1 ) &
    echo $! > "$D.arm_$a.pid"
}
dist_ok() { tail -5 "$C/cfarm_tf_2c_$1.out" 2>/dev/null | grep -q "DIST CHECK PASS" && ! grep -q "GUARD" "$C/cfarm_tf_2c_$1.out"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"
command -v gfortran >/dev/null 2>&1 || {
    note "gfortran missing, installing"
    apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1
}
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
python3 -c "import numpy" 2>/dev/null || pip install -q numpy >/dev/null 2>&1
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"

cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && [ "$C/$b/hftf_cf_prod" -nt "$C/housing_first_or_treatment_first_SR_v1.f90" ] && continue
    note "building $b"
    bash "cf_runs/build_$b.sh" > "/tmp/decomp_build_$b.log" 2>&1 || { note "GUARD: build $b failed: $(tail -3 /tmp/decomp_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
grep -q "if (drug_market_adjuster==0.d0) distance_drug_market=0" "$C/cf_fix2/cf.f90" \
    || { note "GUARD: cf_fix2 lacks the held-price stopping rule"; publish "failed"; exit 1; }
publish "built"

# fixpv first, alone until it has unpacked the shared benchmark (cfarm_bench), then fixp beside it
if ! dist_ok fixpv; then
    arm fixpv PDET=0.85 PV_START=$V_NULL DRUG_PRICE_START=$P_TF EXTRA_SET="cost_per_drug_test $CTEST;adjust_taxes 0"
    while [ ! -f "$C/cfarm_bench/BENCH_DONE" ] && alive "$D.arm_fixpv.pid"; do sleep 10; done
fi
if ! dist_ok fixp; then
    arm fixp PDET=0.85 NET_TARGET="$NET_TARGET" PV_START=$V_TF DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 \
        EXTRA_SET="cost_per_drug_test $CTEST"
fi
while alive "$D.arm_fixpv.pid" || alive "$D.arm_fixp.pid"; do
    for _ in $(seq 1 120); do { alive "$D.arm_fixpv.pid" || alive "$D.arm_fixp.pid"; } || break; sleep 10; done
    publish "arms running"
done

# THE CHECKS. fixpv: the voucher probability never moved and the budget was not cleared; fixp: the price never
# moved and the budget was cleared against the target. Both: the distribution solved every pass.
for a in fixpv fixp; do
    O="$C/cfarm_tf_2c_$a.out"; L="$C/cfarm_tf_2c_$a/cf.log"
    dist_ok $a && note "$a: $(grep -a 'DIST CHECK PASS' "$O")" || note "GUARD: $a failed its distribution check: $(tail -3 "$O" | tr '\n' ' ')"
    mkdir -p "$R/arm_$a"
    python3 "$C/cf_runs/finalstats.py" "$L" "$REPO/results/counterfactuals_2c/nulltf/null/cf.log.gz" > "$R/arm_$a/final.txt" 2>&1 \
        || python3 "$C/cf_runs/finalstats.py" "$L" > "$R/arm_$a/final.txt" 2>&1
    gzip -c "$L" > "$R/arm_$a/cf.log.gz"
    cp "$C/cfarm_tf_2c_$a/welfare_by_employment_youngestcounter_arm.txt" "$R/arm_$a/value_at_26_by_node.txt" 2>/dev/null
    pv=$(grep -a "^ *probability_of_voucher=" "$L" | awk '{print $2}' | sort -u | tr '\n' ' ')
    pr=$(grep -a "^ *price_of_addictive_good=" "$L" | awk '{print $2}' | sort -u | head -3 | tr '\n' ' ')
    note "$a: pi_V values printed: $pv; first drug prices printed: $pr"
done
grep -a "TARGET CHECK PASS" "$C/cfarm_tf_2c_fixp.out" >/dev/null && note "fixp: $(grep -a 'TARGET CHECK PASS' "$C/cfarm_tf_2c_fixp.out")" \
    || note "GUARD: fixp did not clear the budget against $NET_TARGET"
note "decompositions done"
publish "decompositions done"
