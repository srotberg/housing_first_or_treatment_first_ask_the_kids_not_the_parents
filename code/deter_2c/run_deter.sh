#!/bin/bash
# run_deter.sh -- THE DETECTION RATE IDENTIFIED FROM THE MILITARY'S DETERRENCE (8 October). The author: "get the detection
# probability such that in PE, from the benchmark distribution with HF, a drug test with the penalty similar to the one
# in the military (I think permanent exclusion?), deters only 16% of users", "the deterrence has to be applied only to
# those with vouchers ... not those outside", "if you account also for others outside the program, you are measuring
# ... on the wrong margin". Mehay and Pacula (1999, NBER WP 7383): random testing with discharge, about 16 per cent.
#
# THE MEASURE. On Housing First's benchmark distribution, held fixed (build *_impact: fixed_to_benchmark_dis = 1), at
# Housing First's drug price and pi_V (both held, the budget not cleared): the share of voucher holders who use, under
# Housing First's policies and under a screen whose penalty is the military's -- a PERMANENT voucher ban (build
# cf_fix2_permban: voucher_exclusion_release = 0). The deterrence is 1 - (holders' use under the screen) / (holders' use
# under Housing First), the Fortran's 'DIAG use by voucher state ... holding=' field (the author: "just the use").
# Detection rates 0.02 to 0.85; the rate giving TARGET_DROP is interpolated between the two that bracket it.
#
# THEN, AT THAT RATE: the paper's Treatment First (exclusion released at 1/3 a year, build cf_fix2) with the drug price
# and pi_V clearing against the accepted no-policy net revenue, exactly as the tf85_c35 arm except the detection rate;
# beside it, the impact run with the permanent ban at that rate (the confirmation) and the impact run of the paper's
# Treatment First at that rate (how much the paper's own screen deters holders on impact).
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/deter_2c/run_deter.sh
# Re-running attaches to a live worker; a finished run is not repeated. Publishes results/deter_2c/status.txt.
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

# holders' use (the measure), then eligible use, the tested population's use, and the eligible mass, from the last print
diag() {   # <cf.log>
    python3 - "$1" <<'PYEOF'
import re, sys
try:
    t = open(sys.argv[1], errors='replace').read()
except OSError:
    print('NA'); raise SystemExit
L = [l for l in t.splitlines() if 'DIAG use by voucher state' in l]
if not L:
    print('NA'); raise SystemExit
l = L[-1].replace('=', ' = ')
def g(k):
    m = re.search(re.escape(k) + r'\s*=\s*(\S+)', l)   # the first match: 'eligible' before 'eligible mass'
    return float(m.group(1)) if m else float('nan')
print('%.10f %.10f %.10f %.10f' % (g('holding'), g('eligible'), g('tested'), g('eligible mass')))
PYEOF
}
holders() { diag "$1" | awk '{print $1}'; }

publish() (
    {
        echo "# the detection rate at which a permanent ban deters $TARGET_DROP of voucher holders who use, omega_c = 0.085; $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for d in "$C"/cfarm_*_imp_* "$C"/cfarm_tf_2c_det*; do
            [ -f "$d/cf.log" ] || continue
            echo; echo "== $(basename "$d"): $(grep -ac 'CF MOMENTS' "$d/cf.log") passes; use among holders, eligible, tested; eligible mass: $(diag "$d/cf.log")"
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

# imp <tag> <null|tf> <build> [VAR=value ...]: an impact run at Housing First's price and pi_V on the fixed distribution
imp() {
    t=$1; a=$2; b=$3; shift 3
    note "impact $a $t on $b: $*"
    ( cd "$C" && env BUILD=$b OMP_NUM_THREADS=$THREADS DIAG_TAG="_imp_$t" SEED_FROM=bench \
        PV_START=$V_NULL DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 "$@" sh pe_noext/cf_arm_pe.sh "$a" \
        > "$C/cfarm_${a}_imp_$t.out" 2>&1 ) &
    echo $! > "$D.imp_$t.pid"
}
imp_done() { [ -f "$C/cfarm_$1_imp_$2/cf.log" ] && [ "$(diag "$C/cfarm_$1_imp_$2/cf.log")" != NA ]; }
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
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc), threads per solve $THREADS"

cd "$C"
# ONLY WHAT THE RUNS USE IS COMPILED (the author: "that deterrence calibration should be very quick to do"). cf_fix and
# cf_fix_permban are sources the next step patches, so they are generated, not compiled; the three binaries the runs
# execute (cf_fix2 for the experiment, the two impact builds for the calibration) are compiled production-only, at once.
need=0
for o in cf_fix2 cf_fix2_impact cf_fix2_permban_impact; do
    [ -x "$C/$o/hftf_cf_prod" ] && [ "$C/$o/hftf_cf_prod" -nt "$C/housing_first_or_treatment_first_SR_v1.f90" ] || need=1
done
if [ $need = 1 ]; then
    note "generating the sources"
    { GEN_ONLY=1 bash cf_runs/build_cf_fix.sh && PERMBAN=1 GEN_ONLY=1 bash cf_runs/build_cf_fix.sh && \
      GEN_ONLY=1 bash cf_runs/build_cf_fix2.sh && PERMBAN=1 GEN_ONLY=1 bash cf_runs/build_cf_fix2.sh && \
      IMPACT_BASE=cf_fix2 GEN_ONLY=1 bash deter_2c/build_impact.sh && \
      IMPACT_BASE=cf_fix2_permban GEN_ONLY=1 bash deter_2c/build_impact.sh; } > /tmp/deter_gen.log 2>&1 \
        || { note "GUARD: generating the sources failed: $(tail -3 /tmp/deter_gen.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "compiling cf_fix2, cf_fix2_impact and cf_fix2_permban_impact (production only, in parallel)"
    for o in cf_fix2 cf_fix2_impact cf_fix2_permban_impact; do
        ( cd "$C/$o" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium \
            cf.f90 -o hftf_cf_prod 2> build_prod.err ) &
    done
    wait
    for o in cf_fix2 cf_fix2_impact cf_fix2_permban_impact; do
        [ -x "$C/$o/hftf_cf_prod" ] || { note "GUARD: $o did not compile: $(grep -m2 Error "$C/$o/build_prod.err" | tr '\n' ' ')"; publish "failed"; exit 1; }
    done
fi
for b in cf_fix2 cf_fix2_permban; do
    grep -q "DIAG use by voucher state" "$C/${b}_impact/cf.f90" || { note "GUARD: ${b}_impact lacks the DIAG line"; publish "failed"; exit 1; }
done
grep -q "voucher_exclusion_release=0.d0" "$C/cf_fix2_permban_impact/cf.f90" || { note "GUARD: the permanent-ban impact build releases the exclusion"; publish "failed"; exit 1; }
publish "built"

TF_SET="cost_per_drug_test $CTEST;adjust_taxes 0"
PB=cf_fix2_permban_impact
# THE GRID, cheap because the distribution never moves: Housing First (the reference) alone until the benchmark is
# done, then the permanent ban at six detection rates, two at a time
GRID="0.02 0.05 0.10 0.20 0.40 0.85"
tagof() { python3 -c "print('pb%03d' % round(1000*float('$1')))"; }
if ! imp_done null ref; then
    imp ref null cf_fix2_impact
    wait_all "reference" "$D.imp_ref.pid"     # alone: it unpacks the benchmark, and three solves would not fit in 15 GB
fi
imp_done null ref || { note "GUARD: the Housing First reference printed no DIAG line: $(tail -3 "$C/cfarm_null_imp_ref.out" | tr '\n' ' ')"; publish "reference failed"; exit 1; }
set -- $GRID
while [ $# -gt 0 ]; do
    pids=""
    for p in $1 ${2:-}; do
        t=$(tagof $p); imp_done tf $t || imp $t tf $PB PDET=$p EXTRA_SET="$TF_SET"; pids="$pids $D.imp_$t.pid"
    done
    wait_all "grid" $pids
    shift; [ $# -gt 0 ] && shift
done

note "impact ref: $(diag "$C/cfarm_null_imp_ref/cf.log")  [use among holders, eligible, tested; eligible mass]"
for p in $GRID; do t=$(tagof $p); note "impact $t: $(diag "$C/cfarm_tf_imp_$t/cf.log")"; done
H0=$(holders "$C/cfarm_null_imp_ref/cf.log")
DROPS=$(for p in $GRID; do echo "$p $(holders "$C/cfarm_tf_imp_$(tagof $p)/cf.log")"; done)
note "holders' use under Housing First $H0; under the permanent ban: $(echo $DROPS)"
PSTAR=$(python3 - "$TARGET_DROP" "$H0" <<PYEOF
import sys
tgt, h0 = float(sys.argv[1]), float(sys.argv[2])
rows = [l.split() for l in """$DROPS""".strip().splitlines()]
pts = [(0.0, 0.0)] + sorted((float(p), 1 - float(h) / h0) for p, h in rows)
print('drops ' + ', '.join('%.2f: %.1f%%' % (p, 100 * d) for p, d in pts[1:]), file=sys.stderr)
for (p1, d1), (p2, d2) in zip(pts, pts[1:]):
    if d1 <= tgt <= d2 and d2 > d1:
        print('%.4f' % (p1 + (tgt - d1) * (p2 - p1) / (d2 - d1))); break
else:
    print('NA')
PYEOF
)
case "$PSTAR" in NA*|"") note "GUARD: a $TARGET_DROP drop is not bracketed by the grid"; publish "target not bracketed"; exit 1 ;; esac
note "detection rate at which the permanent ban deters $TARGET_DROP of holders who use: $PSTAR"
publish "detection $PSTAR"
TAG=$(python3 -c "print('%03d' % round(1000*float('$PSTAR')))")

# ROUND 3: the paper's Treatment First at that rate with the price and pi_V clearing; beside it, one after the other,
# the permanent ban's impact run at that rate (the confirmation) and the paper's screen's impact run at that rate
if ! { tail -5 "$C/cfarm_tf_2c_det$TAG.out" 2>/dev/null | grep -q "DIST CHECK PASS"; }; then
    note "Treatment First at detection $PSTAR, price and pi_V clearing against $NET_TARGET"
    ( cd "$C" && env BUILD=cf_fix2 OMP_NUM_THREADS=$THREADS DIAG_TAG="_2c_det$TAG" SEED_FROM=bench PDET=$PSTAR \
        NET_TARGET="$NET_TARGET" PV_START=$V_TF DRUG_PRICE_START=$P_TF EXTRA_SET="cost_per_drug_test $CTEST" \
        sh pe_noext/cf_arm_pe.sh tf > "$C/cfarm_tf_2c_det$TAG.out" 2>&1 ) &
    echo $! > "$D.main.pid"
fi
if ! imp_done tf "pbc$TAG"; then imp "pbc$TAG" tf $PB PDET=$PSTAR EXTRA_SET="$TF_SET"; wait_all "round 3a" "$D.imp_pbc$TAG.pid"; fi
note "confirmation, permanent ban at $PSTAR: holders' use $(holders "$C/cfarm_tf_imp_pbc$TAG/cf.log") against $H0"
if ! imp_done tf "ty$TAG"; then imp "ty$TAG" tf cf_fix2_impact PDET=$PSTAR EXTRA_SET="$TF_SET"; wait_all "round 3b" "$D.imp_ty$TAG.pid"; fi
note "the paper's screen at $PSTAR on impact: holders' use $(holders "$C/cfarm_tf_imp_ty$TAG/cf.log") against $H0"
wait_all "round 3" "$D.main.pid"

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
