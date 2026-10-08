#!/bin/bash
# run_whostops.sh -- WHO STOPS USING, STATE BY STATE (8 October). The author: "do a PE iteration on the HF benchmark.
# keep piv and pv constant. and then apply TF and examine what happens only to the drug use rate of those with vouchers
# or who are offered a voucher. And it has to look only at those with a voucher and who use drugs under HF", "that is
# what we need to do exactly to compare" (with Mehay and Pacula's stayers, 61 per cent).
#
# Two impact runs (build cf_fix2_impact: Housing First's benchmark distribution held fixed, the drug price and pi_V at
# Housing First's, the budget not cleared): the Housing First reference, which writes every state's drug choice and
# tested weight to DIAG_STATES_OUT.bin; then the paper's Treatment First (detection 0.85, the $35 test, the three-year
# exclusion), which reads that file and prints 'DIAG who stops': of the mass that used under Housing First, how much
# does not under Treatment First -- among holders, and among the tested (holders, and eligible non-holders at their
# offer rate) -- for all users and for users without a SUD (who alone can stop on impact). Same machinery as
# run_validate.sh.
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/deter_2c/run_whostops.sh
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
E=$(cd "$(dirname "$0")" && pwd)
C=$(cd "$E/.." && pwd)
REPO=$(cd "$C/.." && pwd)
REF=$REPO/results/reference/hf_2c_omega_0.085
R=$REPO/results/whostops_2c
mkdir -p "$R"
D=$C/whostops_worker
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

if [ "${WS_DETACHED:-0}" != 1 ]; then
    if alive "$D.pid"; then
        echo "run_deter: attaching to the running worker, pid $(cat "$D.pid")"
    else
        ( WS_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/whostops.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "run_deter: started detached, pid $(cat "$D.pid"); log /tmp/whostops.detached.log"
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
        echo "# who stops using under Treatment First, state by state, on Housing First's distribution; $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for d in "$C"/cfarm_*_imp_* "$C"/cfarm_tf_2c_det*; do
            [ -f "$d/cf.log" ] || continue
            echo; echo "== $(basename "$d"): $(grep -ac 'CF MOMENTS' "$d/cf.log") passes; use among holders, eligible, tested; eligible mass: $(diag "$d/cf.log")"
            python3 "$C/cf_runs/passes.py" "$d/cf.log" "$C/cf_runs/cev.py" 2>/dev/null | tail -n 4
        done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO" || exit 0
    git add "$R" 2>/dev/null
    git commit -q -m "whostops 2c: $1$TRAILER" || return 0
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
for o in cf_fix2_impact; do
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
    for o in cf_fix2_impact; do
        ( cd "$C/$o" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium \
            cf.f90 -o hftf_cf_prod 2> build_prod.err ) &
    done
    wait
    for o in cf_fix2_impact; do
        [ -x "$C/$o/hftf_cf_prod" ] || { note "GUARD: $o did not compile: $(grep -m2 Error "$C/$o/build_prod.err" | tr '\n' ' ')"; publish "failed"; exit 1; }
    done
fi
for b in cf_fix2; do
    grep -q "DIAG use by voucher state" "$C/${b}_impact/cf.f90" || { note "GUARD: ${b}_impact lacks the DIAG line"; publish "failed"; exit 1; }
done
publish "built"

TF_SET="cost_per_drug_test $CTEST;adjust_taxes 0"
grep -q "DIAG who stops" "$C/cf_fix2_impact/cf.f90" || { note "GUARD: cf_fix2_impact lacks the who-stops line"; publish "failed"; exit 1; }
if ! imp_done null wsref; then imp wsref null cf_fix2_impact; wait_all "reference" "$D.imp_wsref.pid"; fi
imp_done null wsref || { note "GUARD: the reference printed no DIAG line: $(tail -3 "$C/cfarm_null_imp_wsref.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
HFF=$C/cfarm_null_imp_wsref/DIAG_STATES_OUT.bin
[ -s "$HFF" ] || { note "GUARD: the reference wrote no DIAG_STATES_OUT.bin"; publish "failed"; exit 1; }
note "reference: $(diag "$C/cfarm_null_imp_wsref/cf.log")  [use among holders, eligible, tested; eligible mass]; states file $(du -h "$HFF" | cut -f1)"
if ! imp_done tf ws850; then imp ws850 tf cf_fix2_impact PDET=0.85 EXTRA_SET="$TF_SET" DIAG_HF_FROM="$HFF"; wait_all "screen" "$D.imp_ws850.pid"; fi
note "screen at 0.85: $(diag "$C/cfarm_tf_imp_ws850/cf.log")"
L=$(grep -a "DIAG who stops" "$C/cfarm_tf_imp_ws850/cf.log" | tail -n 1)
note "last who-stops line: $L"
python3 - "$L" <<'PYEOF' | while IFS= read -r x; do note "$x"; done
import re, sys
l = sys.argv[1].replace('=', ' = ')
v = [float(x) for x in re.findall(r'=\s*([-+0-9.Ee]+)', l)]
if len(v) < 13 or v[0] != 1:
    print('GUARD: the screen run did not read the Housing First file (hf file = %s)' % (v[0] if v else 'NA')); raise SystemExit
names = ['holders, all users', 'holders, users without a SUD', 'holders and offered, all users', 'holders and offered, users without a SUD']
for k, n in enumerate(names):
    used, stop, start = v[1 + 3 * k: 4 + 3 * k]
    print('%s: %.1f per cent of those who used under Housing First stop under Treatment First (mass used %.6g, stop %.6g, start %.6g)'
          % (n, 100 * stop / used if used else float('nan'), used, stop, start))
PYEOF
for d in "$C"/cfarm_*_imp_ws*; do mkdir -p "$R/$(basename "$d")"; gzip -c "$d/cf.log" > "$R/$(basename "$d")/cf.log.gz" 2>/dev/null; done
note "who stops done"
publish "who stops done"
