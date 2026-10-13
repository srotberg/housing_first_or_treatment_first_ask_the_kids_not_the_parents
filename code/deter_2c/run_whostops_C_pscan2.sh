#!/bin/bash
# run_whostops_C_pscan2.sh -- run_whostops_C_pscan.sh made to fit the disk (13 October, 15:20). The first scan filled the
# container's disk at the end of round 1 (five run directories, each a full copy of the benchmark's files plus its own
# output) and its container was lost. Changes: the screens run TWO at a time at two threads each; every finished run is
# cut down to its cf.log and .out at once, and the reference to its states file; round 1 is 0.02, 0.05, 0.10 and 0.20
# (the first scan's published use rates put the crossing low: tested use fell 29% at 0.05 and 51% at 0.15, all users).
# Results to results/whostops_2c_C_pscan2; worker files code/whostops_worker_Cp2.*. The first scan's header follows.
# run_whostops_C_pscan.sh -- THE DETECTION RATE AT WHICH WHO-STOPS MATCHES MEHAY AND PACULA (13 October; the author: "I
# would look for the detection rate that gives the 61% first"). On the current rule-C build (every switch on), the share of
# the tested (holders and applicants at their offer rate) who used under Housing First, have no SUD, and stop on impact
# under Treatment First is 100.0 per cent at detection 0.85 (results/whostops_2c_C). This copy of
# run_whostops_C_switch.sh runs the same reference, then the screen at detection 0.05, 0.15, 0.30 and 0.50 side by side
# (one thread each), then four more points inside whichever interval crosses the target (default 61, Mehay and Pacula's
# stayers, lit 'mp_stay_rel_pc'), and interpolates linearly for the detection rate that gives it. Results to
# results/whostops_2c_C_pscan; worker files code/whostops_worker_Cp.*. A copy; nothing else is touched.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/deter_2c/run_whostops_C_pscan.sh
# run_whostops_C.sh's header follows.
# run_whostops_C.sh -- RULE-C COPY of deter_2c/run_whostops.sh (12 October; the author: "all the stuff already in the paper
# should be redone for rule C including any validation we rely on"). Changes: both impact runs on cf_fix2_treatC_impact
# (treat/build_treatC_impact_C.sh: cf_fix2 + treat/patch_treatC.py + the fixed distribution), through
# pe_noext/cf_arm_pe_C.sh; results to results/whostops_2c_C; worker files code/whostops_worker_C.*; status published
# every 20 minutes. The reference (Housing First, no screen) runs on the same binary: it must reproduce rule A's
# reference, 0.0608335618 0.1808173217 0.0796507461 11.6337833103, which is the check that rule C changes only the
# screen. No warm start applies: both runs hold the drug price and pi_V at Housing First's. The header follows.
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
R=$REPO/results/whostops_2c_C_pscan2
mkdir -p "$R"
D=$C/whostops_worker_Cp2
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
TARGET_DROP=${TARGET_DROP:-0.16}
THREADS=${THREADS:-$(python3 -c "import os; print(max(1, min(4, os.cpu_count() // 2)))")}
# 13 Oct: Housing First's net revenue with its own treatment spending (treat/net_target_with_treatment.py)
NET_TARGET=5.8275447063                 # the accepted no-policy run's net revenue (tf85_c35's target)
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
P_NULL=1.0001082; V_NULL=0.067533863          # results/counterfactuals_2c/nulltf/null/final.txt
P_TF=0.85551291;  V_TF=0.096152024            # results/counterfactuals_2c/tf85_c35/tf/final.txt
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat

note() { echo "run_deter_pscan2: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

if [ "${WSP2_DETACHED:-0}" != 1 ]; then
    if alive "$D.pid"; then
        echo "run_deter_pscan2: attaching to the running worker, pid $(cat "$D.pid")"
    else
        ( WSP2_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/whostops_Cp2.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "run_deter_pscan2: started detached, pid $(cat "$D.pid"); log /tmp/whostops_Cp2.detached.log"
    fi
    while alive "$D.pid"; do sleep 60; done
    echo "run_deter_pscan2: finished"; cat "$D.status" 2>/dev/null
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
        for d in "$C"/cfarm_*_imp_ws*; do
            [ -f "$d/cf.log" ] || continue
            echo; echo "== $(basename "$d"): $(grep -ac 'CF MOMENTS' "$d/cf.log") passes; use among holders, eligible, tested; eligible mass: $(diag "$d/cf.log")"
            python3 "$C/cf_runs/passes.py" "$d/cf.log" "$C/cf_runs/cev.py" 2>/dev/null | tail -n 4
        done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO" || exit 0
    git add "$R" 2>/dev/null
    git commit -q -m "whostops 2c rule C detection scan 2: $1$TRAILER" || return 0
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
        PV_START=$V_NULL DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 "$@" sh pe_noext/cf_arm_pe_C.sh "$a" \
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
if ! { [ -x "$C/cf_fix2_treatC_impact/hftf_cf_prod" ] && [ "$C/cf_fix2_treatC_impact/hftf_cf_prod" -nt "$C/housing_first_or_treatment_first_SR_v1.f90" ]; }; then
    note "building cf_fix2_treatC_impact (cf_fix2 + patch_treatC.py + the fixed distribution)"
    bash treat/build_treatC_impact_C.sh > /tmp/whostops_C_build.log 2>&1 \
        || { note "GUARD: build failed: $(tail -3 /tmp/whostops_C_build.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
note "build: $(tail -1 /tmp/whostops_C_build.log 2>/dev/null)"
f=$C/cf_fix2_treatC_impact/cf.f90
[ "$(grep -c 'RULE C (patch_treatC.py)' "$f")" = 1 ] && [ "$(grep -c "THE HOUSEHOLD'S OWN TREATMENT CHOICE (patch_treatC.py)" "$f")" = 2 ] \
    && grep -q 'DIAG use by voucher state' "$f" && grep -q '^        integer, parameter :: fixed_to_benchmark_dis=1$' "$f" \
    || { note "GUARD: cf_fix2_treatC_impact lacks a patch"; publish "failed"; exit 1; }
publish "built"

TF_SET="cost_per_drug_test $CTEST;adjust_taxes 0"
grep -q "DIAG who stops" "$C/cf_fix2_treatC_impact/cf.f90" || { note "GUARD: cf_fix2_treatC_impact lacks the who-stops line"; publish "failed"; exit 1; }
if ! imp_done null wsref; then THREADS=4 imp wsref null cf_fix2_treatC_impact; wait_all "reference" "$D.imp_wsref.pid"; fi
imp_done null wsref || { note "GUARD: the reference printed no DIAG line: $(tail -3 "$C/cfarm_null_imp_wsref.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
HFF=$C/cfarm_null_imp_wsref/DIAG_STATES_OUT.bin
[ -s "$D.hf_states.bin" ] || cp "$HFF" "$D.hf_states.bin" 2>/dev/null
[ -s "$D.hf_states.bin" ] && HFF=$D.hf_states.bin
[ -s "$HFF" ] || { note "GUARD: the reference wrote no DIAG_STATES_OUT.bin"; publish "failed"; exit 1; }
note "reference: $(diag "$C/cfarm_null_imp_wsref/cf.log")  [use among holders, eligible, tested; eligible mass]; states file $(du -h "$HFF" | cut -f1)"
THREADS=2
slim "$C/cfarm_null_imp_wsref"
TARGET_WS=${TARGET_WS:-61}
# tn <tag>: the tested users without a SUD who stop, per cent, from the run's last who-stops line
tn() {
    L=$(grep -a "DIAG who stops" "$C/cfarm_tf_imp_$1/cf.log" 2>/dev/null | tail -n 1)
    python3 - "$L" <<'PYEOF'
import re, sys
v = [float(x) for x in re.findall(r'=\s*([-+0-9.Ee]+)', sys.argv[1].replace('=', ' = '))]
print('%.4f' % (100 * v[11] / v[10]) if len(v) >= 13 and v[0] == 1 and v[10] else 'NA')
PYEOF
}
tag() { echo "ws_p$(python3 -c "print('%03d' % round(1000 * $1))")"; }
slim() {   # <dir>: keep a finished run's log, drop its copies of the benchmark and its output files (the disk)
    [ -d "$1" ] || return 0
    find "$1" -maxdepth 1 -type f ! -name 'cf.log' ! -name 'cf.err' ! -name '*.txt' ! -name '*.out' -size +1M -delete 2>/dev/null
}
round() {   # <label> <p>...: the screen at each detection rate, two at a time, two threads each
    l=$1; shift
    set -- "$@"
    while [ $# -gt 0 ]; do
        pids=""; batch=""
        for p in "$1" "${2:-}"; do
            [ -n "$p" ] || continue
            t=$(tag "$p"); batch="$batch $p"
            imp_done tf "$t" || alive "$D.imp_$t.pid" || imp "$t" tf cf_fix2_treatC_impact PDET="$p" EXTRA_SET="$TF_SET" DIAG_HF_FROM="$HFF"
            pids="$pids $D.imp_$t.pid"
        done
        shift; [ $# -gt 0 ] && shift
        wait_all "$l" $pids
        for p in $batch; do t=$(tag "$p"); echo "$p $(tn "$t")" >> "$D.scan"; note "detection $p: $(tn "$t") per cent of tested users without a SUD stop"; slim "$C/cfarm_tf_imp_$t"; done
        publish "$l"
    done
}
[ -f "$D.scan" ] || printf '0 0\n0.85 100\n' > "$D.scan"   # 0.85 from results/whostops_2c_C; no screen, nobody stops
round "detection scan, round 1" 0.02 0.05 0.10 0.20
BR=$(sort -n -u "$D.scan" | awk -v T="$TARGET_WS" '$2!="NA" {if (pp!="" && pv<T && $2>=T) {print pp, $1; exit} pp=$1; pv=$2}')
if [ -n "$BR" ]; then
    lo=${BR% *}; hi=${BR#* }
    note "round 1 brackets $TARGET_WS per cent between detection $lo and $hi"
    round "detection scan, round 2" $(python3 -c "print(' '.join('%.3f' % ($lo + k * ($hi - $lo) / 5) for k in range(1, 5)))")
else
    note "GUARD: no interval in round 1 crosses $TARGET_WS per cent: $(sort -n -u "$D.scan" | tr '\n' ';')"
fi
note "scan (detection, per cent stopping): $(sort -n -u "$D.scan" | tr '\n' ';')"
note "$(sort -n -u "$D.scan" | awk -v T="$TARGET_WS" '$2!="NA" {if (pp!="" && pv<T && $2>=T) {printf "detection giving %s per cent: %.3f (linear between %s and %s)", T, pp + (T - pv) * ($1 - pp) / ($2 - pv), pp, $1; f=1; exit} pp=$1; pv=$2} END{if (!f) print "no crossing found"}')"
cp "$D.scan" "$R/scan.txt"
for d in "$C"/cfarm_*_imp_ws*; do mkdir -p "$R/$(basename "$d")"; gzip -c "$d/cf.log" > "$R/$(basename "$d")/cf.log.gz" 2>/dev/null; done
note "detection scan done"
publish "detection scan done"
