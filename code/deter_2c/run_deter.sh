#!/bin/bash
# run_deter.sh -- THE SCREEN'S DETERRENCE MATCHED TO THE MILITARY'S (8 October). The author: "use the benchmark
# distribution of HF and then check how many respond to it", and that share "has to match the 16%" Mehay and Pacula
# (1999, NBER WP 7383) find for random testing with discharge in the military.
#
# THE MEASURE. Treatment First's policies, solved at Housing First's drug price and pi_V (both held, the budget not
# cleared), applied to Housing First's benchmark distribution (build cf_fix2_impact: fixed_to_benchmark_dis = 1, so
# no run moves the distribution). The population is the tested one, the same under either programme: every
# income-eligible voucher holder, and every income-eligible non-holder weighted by its offer rate (the Fortran's
# 'DIAG use by voucher state ... tested=' line). The drop is 1 - (users among the tested under Treatment First) /
# (the same under Housing First), at detection rates 0.85, 0.20 and 0.05; the rate that gives 16 per cent is
# interpolated between the two that bracket it (from zero at zero detection below the lowest).
#
# THEN THE EXPERIMENT AT THAT RATE: Treatment First on cf_fix2 with the drug price and pi_V clearing against the
# accepted no-policy net revenue, exactly as the paper's tf85_c35 arm except the detection rate, plus the impact run
# at the same rate to confirm the 16 per cent.
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/deter_2c/run_deter.sh
# Re-running attaches to a live worker; a finished arm is not run again. Publishes results/deter_2c/status.txt.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
E=$(cd "$(dirname "$0")" && pwd)
C=$(cd "$E/.." && pwd)
REPO=$(cd "$C/.." && pwd)
REF=$REPO/results/reference/hf_2c_omega_0.085
R=$REPO/results/deter_2c
mkdir -p "$R"
D=$C/deter_worker
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
TARGET_DROP=${TARGET_DROP:-0.16}
THREADS=${THREADS:-$(python3 -c "import os; print(max(1, min(4, os.cpu_count() // 2)))")}
NET_TARGET=5.8918410999831181                 # the accepted no-policy run's net revenue (tf85_c35's target)
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
P_NULL=1.0001082; V_NULL=0.067533863          # results/counterfactuals_2c/nulltf/null/final.txt
P_TF=0.85551291;  V_TF=0.096152024            # results/counterfactuals_2c/tf85_c35/tf/final.txt
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat

note() { echo "run_deter: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

if [ "${DETER_DETACHED:-0}" != 1 ]; then
    if alive "$D.pid"; then
        echo "run_deter: attaching to the running worker, pid $(cat "$D.pid")"
    else
        ( DETER_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/deter.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "run_deter: started detached, pid $(cat "$D.pid"); log /tmp/deter.detached.log"
    fi
    while alive "$D.pid"; do sleep 60; done
    echo "run_deter: finished"; cat "$D.status" 2>/dev/null
    exit 0
fi

# the tested users' share and the other DIAG figures of an arm's last print
diag() {   # <cf.log>
    python3 - "$1" <<'PYEOF'
import re, sys
t = open(sys.argv[1], errors='replace').read()
L = [l for l in t.splitlines() if 'DIAG use by voucher state' in l]
if not L:
    print('NA'); raise SystemExit
l = L[-1].replace('=', ' = ')
def g(k):
    m = re.search(re.escape(k) + r'\s*=\s*(\S+)', l)
    return float(m.group(1)) if m else float('nan')
print('%.10f %.10f %.10f %.10f %.10f' % (g('tested'), g('holding'), g('eligible'), g('tested mass'), g('users tested')))
PYEOF
}

publish() (
    {
        echo "# the screen's deterrence matched to $TARGET_DROP among the tested, omega_c = 0.085; $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for d in "$C"/cfarm_*_imp_* "$C"/cfarm_tf_2c_det*; do
            [ -f "$d/cf.log" ] || continue
            echo; echo "== $(basename "$d"): $(grep -ac 'CF MOMENTS' "$d/cf.log") passes; tested/holding/eligible use, tested mass, tested users: $(diag "$d/cf.log")"
            python3 "$C/cf_runs/passes.py" "$d/cf.log" "$C/cf_runs/cev.py" 2>/dev/null | tail -n 4
        done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO" || exit 0
    git add "$R" code/deter_2c 2>/dev/null
    git commit -q -m "deter 2c: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)

# imp <tag> <null|tf> [VAR=value ...]: an impact run (cf_fix2_impact) at Housing First's price and pi_V
imp() {
    t=$1; a=$2; shift 2
    note "impact $a $t: $*"
    ( cd "$C" && env BUILD=cf_fix2_impact OMP_NUM_THREADS=${THREADS:-2} DIAG_TAG="_imp_$t" SEED_FROM=bench \
        PV_START=$V_NULL DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 "$@" sh pe_noext/cf_arm_pe.sh "$a" \
        > "$C/cfarm_${a}_imp_$t.out" 2>&1 ) &
    echo $! > "$D.imp_$t.pid"
}
imp_done() { [ "$(diag "$C/cfarm_$1_imp_$2/cf.log" 2>/dev/null)" != NA ] && [ -f "$C/cfarm_$1_imp_$2/cf.log" ]; }
wait_all() {   # <label> <pid file>...
    l=$1; shift
    while :; do
        any=0; for p in "$@"; do alive "$p" && any=1; done
        [ $any = 1 ] || break
        for _ in $(seq 1 120); do any=0; for p in "$@"; do alive "$p" && any=1; done; [ $any = 1 ] || break; sleep 10; done
        publish "$l"
    done
}

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
    bash "cf_runs/build_$b.sh" > "/tmp/deter_build_$b.log" 2>&1 || { note "GUARD: build $b failed: $(tail -3 /tmp/deter_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
if [ ! -x "$C/cf_fix2_impact/hftf_cf_prod" ] || [ "$C/cf_fix2_impact/hftf_cf_prod" -ot "$C/cf_fix2/hftf_cf_prod" ]; then
    note "building cf_fix2_impact"
    bash deter_2c/build_impact.sh > /tmp/deter_build_impact.log 2>&1 || { note "GUARD: build cf_fix2_impact failed: $(tail -3 /tmp/deter_build_impact.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
grep -q "DIAG use by voucher state" "$C/cf_fix2_impact/cf.f90" || { note "GUARD: the impact build lacks the DIAG line"; publish "failed"; exit 1; }
publish "built"

TF_SET="cost_per_drug_test $CTEST;adjust_taxes 0"
# ROUND 1: Housing First (the reference) alone until the benchmark is unpacked, then detection 0.85 beside it
if ! imp_done null ref; then
    imp ref null
    while [ ! -f "$C/cfarm_bench/BENCH_DONE" ] && alive "$D.imp_ref.pid"; do sleep 10; done
fi
imp_done tf p085 || imp p085 tf PDET=0.85 EXTRA_SET="$TF_SET"
wait_all "round 1" "$D.imp_ref.pid" "$D.imp_p085.pid"
# ROUND 2
imp_done tf p020 || imp p020 tf PDET=0.20 EXTRA_SET="$TF_SET"
imp_done tf p005 || imp p005 tf PDET=0.05 EXTRA_SET="$TF_SET"
wait_all "round 2" "$D.imp_p020.pid" "$D.imp_p005.pid"

for k in "null ref" "tf p085" "tf p020" "tf p005"; do
    set -- $k; note "impact $2: $(diag "$C/cfarm_$1_imp_$2/cf.log")  [tested, holding, eligible use; tested mass; tested users]"
done
PSTAR=$(python3 - "$TARGET_DROP" "$C" <<'PYEOF'
import sys, re
tgt, C = float(sys.argv[1]), sys.argv[2]
def share(d):
    L = [l for l in open(f'{C}/{d}/cf.log', errors='replace') if 'DIAG use by voucher state' in l]
    return float(re.search(r'tested=\s*(\S+)', L[-1].replace('=', '= ')).group(1))
r0 = share('cfarm_null_imp_ref')
pts = [(0.0, 0.0)] + sorted((p, 1 - share(f'cfarm_tf_imp_{t}') / r0) for p, t in ((0.05, 'p005'), (0.20, 'p020'), (0.85, 'p085')))
for (p1, d1), (p2, d2) in zip(pts, pts[1:]):
    if d1 <= tgt <= d2 and d2 > d1:
        print('%.4f' % (p1 + (tgt - d1) * (p2 - p1) / (d2 - d1))); break
else:
    print('NA ' + ' '.join('%.2f:%.4f' % x for x in pts))
PYEOF
)
note "drops: $(python3 - "$C" <<'PYEOF'
import sys, re
C = sys.argv[1]
def share(d):
    L = [l for l in open(f'{C}/{d}/cf.log', errors='replace') if 'DIAG use by voucher state' in l]
    return float(re.search(r'tested=\s*(\S+)', L[-1].replace('=', '= ')).group(1))
r0 = share('cfarm_null_imp_ref')
print('Housing First tested users %.4f; ' % r0 + ', '.join('detection %s: %.1f%%' % (p, 100 * (1 - share(f'cfarm_tf_imp_{t}') / r0)) for p, t in (('0.05', 'p005'), ('0.20', 'p020'), ('0.85', 'p085'))))
PYEOF
)"
case "$PSTAR" in NA*) note "GUARD: $TARGET_DROP is not bracketed by the grid: $PSTAR"; publish "target not bracketed"; exit 1 ;; esac
note "detection rate for a $TARGET_DROP drop among the tested: $PSTAR"
publish "detection $PSTAR"
TAG=$(python3 -c "print('%03d' % round(1000*float('$PSTAR')))")

# ROUND 3: the experiment at that rate (prices and pi_V clearing) and the impact run confirming the drop
if ! { tail -5 "$C/cfarm_tf_2c_det$TAG.out" 2>/dev/null | grep -q "DIST CHECK PASS"; }; then
    note "Treatment First at detection $PSTAR, price and pi_V clearing against $NET_TARGET"
    ( cd "$C" && env BUILD=cf_fix2 OMP_NUM_THREADS=${THREADS:-2} DIAG_TAG="_2c_det$TAG" SEED_FROM=bench PDET=$PSTAR \
        NET_TARGET="$NET_TARGET" PV_START=$V_TF DRUG_PRICE_START=$P_TF EXTRA_SET="cost_per_drug_test $CTEST" \
        sh pe_noext/cf_arm_pe.sh tf > "$C/cfarm_tf_2c_det$TAG.out" 2>&1 ) &
    echo $! > "$D.main.pid"
fi
imp_done tf "c$TAG" || imp "c$TAG" tf PDET=$PSTAR EXTRA_SET="$TF_SET"
wait_all "round 3" "$D.main.pid" "$D.imp_c$TAG.pid"

note "confirmation, impact at $PSTAR: $(diag "$C/cfarm_tf_imp_c$TAG/cf.log")"
O="$C/cfarm_tf_2c_det$TAG.out"; L="$C/cfarm_tf_2c_det$TAG/cf.log"
tail -5 "$O" | grep -q "DIST CHECK PASS" && note "main arm: $(grep -a 'DIST CHECK PASS' "$O")" || note "GUARD: main arm failed its distribution check: $(tail -3 "$O" | tr '\n' ' ')"
grep -a "TARGET CHECK PASS" "$O" >/dev/null && note "main arm: $(grep -a 'TARGET CHECK PASS' "$O")" || note "GUARD: main arm did not clear the budget against $NET_TARGET"
mkdir -p "$R/arm_det$TAG"
python3 "$C/cf_runs/finalstats.py" "$L" "$REPO/results/counterfactuals_2c/nulltf/null/cf.log.gz" > "$R/arm_det$TAG/final.txt" 2>&1 \
    || python3 "$C/cf_runs/finalstats.py" "$L" > "$R/arm_det$TAG/final.txt" 2>&1
gzip -c "$L" > "$R/arm_det$TAG/cf.log.gz"
cp "$C/cfarm_tf_2c_det$TAG/welfare_by_employment_youngestcounter_arm.txt" "$R/arm_det$TAG/value_at_26_by_node.txt" 2>/dev/null
for d in "$C"/cfarm_*_imp_*; do
    mkdir -p "$R/$(basename "$d")"; gzip -c "$d/cf.log" > "$R/$(basename "$d")/cf.log.gz" 2>/dev/null
done
note "CEV: $(grep -a 'CEV from the saved benchmark curve' "$L" | tail -1)"
note "deterrence runs done"
publish "deterrence runs done"
