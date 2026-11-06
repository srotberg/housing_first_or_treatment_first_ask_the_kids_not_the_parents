#!/bin/bash
# run_whostops_omega1.sh <p> [<p> ...] [OMEGA1_B=<b>] -- THE DETECTION RATE AT omega_c = 1 (6 November; stage 2 of
# code/OMEGA1_PLAN.md; the author: "Then we have to see what p_det gives the reaction as in the data, holding prices
# constant and piv constant, like we did in the main experiment"). A COPY of code/deter_2c/run_whostops_C_points.sh, the
# main experiment's detection calibration (the impact build cf_fix2_treatC_impact on Housing First's distribution, the
# drug price and pi_V held at Housing First's, the share of the tested users who stop on impact), pointed at the
# omega_c = 1 benchmark. That script is left untouched. What differs:
#   * REF is results/omega1_2c/bench_1.0_b<OMEGA1_B>_ku1.0 (code/remote_omega_point.sh 1.0 <b> 1.0 "" 2 omega1_2c, its
#     files/ sent by send_bench_<tag>). OMEGA1_B, the benchmark's b, comes from the environment or a trailing
#     OMEGA1_B=<b> argument (so the command still starts with "bash code/omega1/...") and is read nowhere else. GUARD,
#     before anything starts, if it is unset, if the benchmark's files are not in this checkout, or if its handover is
#     not weight_on_child 1.0, addiction_scalar_1 <b>, kappa_uem 1.0.
#   * BENCH_B=$OMEGA1_B BENCH_OMEGA=1.0 BENCH_KU=1.0. KAPPA_X (inert in impact runs) is the benchmark log's first
#     KAPPA_X PROBE IMPLIED times 1.5076, the rule the 0.686 runs used (results/omega_nishiyama/RESULT.md: it gives their
#     1.0688562125371026); PASSES_BASE is the log's INVARIANT PASS drug users, disorder rate and homelessness rate
#     (code/omega_nishiyama/remote_cf_nishiyama.sh's rule: it gives the 0.686 runs' base). Both read at run time.
#   * P_NULL, V_NULL, Housing First's drug price and pi_V for THIS economy. pi_V is always the benchmark log's own
#     (Housing First holds it there: its VOUCHER CHECK), in full. The price is the re-solved Housing First's
#     (results/omega1_Cu/cf/null/final.txt, code/omega1/remote_omega1_arm.sh null) when that is in this checkout and
#     was solved at this b; until then the benchmark's own (its log's price_of_addictive_good, 1 by construction), said
#     in the status. The main run held 1.0001082 / 0.067533863, the then Housing First's (counterfactuals_2c/nulltf).
#   * THE MEASURE: the paper calibrates detection to the share of ALL tested users who stop, t_stop / t_used of the last
#     'DIAG who stops' line (x_ws_tested_all_pc, code/paper/export_whostops.py; Mehay and Pacula's stayers, 61), not
#     the no-SUD share tn() prints. ta() computes it; each point's note leads with it, and scan.txt's columns are
#     detection, the no-SUD share, the all-tested share.
#   * results to results/whostops_omega1_pts_<rates>; worker files code/whostops_worker_omega1_pts_<rates>.*; the run
#     directories are cfarm_{null,tf}_imp_wo1* (the main runs' are *_imp_ws*), so a container that ran the main
#     economy's who-stops cannot hand this one a finished run of the wrong economy, and a GUARD stops the script if
#     code/cfarm_bench holds another benchmark (cf_arm_pe_C.sh would reuse it without looking).
#   * dropped: NET_TARGET, P_TF, V_TF and TARGET_DROP (the main economy's values, never read by the points script).
#   * slim() is defined before its first use: the original calls it on the reference before the definition, so the
#     reference's copy of the benchmark was never trimmed. The reference is trimmed only once its states file is
#     copied to the worker file.
#   * OMEGA1_DRY=1 runs in the foreground: the checks, the build and the inputs, prints what each run would get, and
#     stops before any solve, with no commit.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root, and run it again whenever the call stops (it
# attaches):  bash code/omega1/run_whostops_omega1.sh 0.15 0.20 OMEGA1_B=0.00479
# run_whostops_C_points.sh's header follows.
# run_whostops_C_points.sh <p> [<p> ...] -- WHO-STOPS AT THE GIVEN DETECTION RATES ONLY (13 October, 15:30; the author:
# "Why an hr?"). run_whostops_C_pscan2.sh's machinery (its own reference, screens two at a time, finished runs trimmed)
# without the rounds: it runs exactly the rates given, so several containers can cover the grid at once. Results to
# results/whostops_2c_C_pts_<rates>; worker files code/whostops_worker_Cpts_<rates>.*. A copy; nothing else touched.
# run_whostops_C_pscan2.sh's header follows.
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
# the detection rates, and OMEGA1_*=<value> settings given as arguments rather than in the environment
PARGS=()
for a in "$@"; do
    case "$a" in
        OMEGA1_[A-Z0-9_]*=*) export "$a" ;;
        *) python3 -c "import sys; p = float('$a'); sys.exit(0 if 0 < p <= 1 else 1)" 2>/dev/null \
               || { echo "GUARD: '$a' is not a detection rate in (0, 1]"; exit 1; }
           PARGS+=("$a") ;;
    esac
done
PTS=$(echo "${PARGS[*]:-}" | tr ' .' '_p')
[ -n "$PTS" ] || { echo "usage: run_whostops_omega1.sh <p> [<p> ...] [OMEGA1_B=<b>]"; exit 1; }
# THE omega_c = 1 BENCHMARK: its b from OMEGA1_B, nowhere else
case "${OMEGA1_B:-}" in ''|*[!0-9.]*|*.*.*) echo "GUARD: OMEGA1_B (the omega_c = 1 benchmark's b, e.g. 0.00479) is unset or not a number: '${OMEGA1_B:-}'"; exit 1 ;; esac
BREL=results/omega1_2c/bench_1.0_b${OMEGA1_B}_ku1.0
REF=$REPO/$BREL
for f in bench.log.gz PARAM_HANDOVER.bench.txt files/welfare_curvebaseline_benchmark.dat.gz files/median_incomebaseline_benchmark.dat.gz files/drug_supply_shifterbaseline_benchmark.dat.gz; do
    [ -s "$REF/$f" ] || { echo "GUARD: $BREL/$f is not in this checkout (has the benchmark's worker sent its files, send_bench_1.0_b${OMEGA1_B}_ku1.0, and has this checkout pulled them?)"; exit 1; }
done
for l in "weight_on_child 1.0" "addiction_scalar_1 $OMEGA1_B" "kappa_uem 1.0"; do
    grep -qxF "$l" "$REF/PARAM_HANDOVER.bench.txt" || { echo "GUARD: $BREL/PARAM_HANDOVER.bench.txt has no line '$l'"; exit 1; }
done
# from the benchmark's log: the first KAPPA_X PROBE IMPLIED, the INVARIANT PASS users, SUD and h_1, its pi_V and price
read -r KX_PROBE PB_B PB_L PB_H V_BENCH P_BENCH < <(zcat "$REF/bench.log.gz" | awk '
    /KAPPA_X PROBE: IMPLIED kappa_x=/ && kx == "" {kx = $5}
    /INVARIANT PASS +drug users/ {b = $NF} /INVARIANT PASS +disorder rate/ {l = $NF} /INVARIANT PASS +homelessness rate/ {h = $NF}
    /^ *probability_of_voucher=/ {v = $2} /^ *price_of_addictive_good=/ {p = $2}
    END {print (kx == "" ? "NA" : kx), (b == "" ? "NA" : b), (l == "" ? "NA" : l), (h == "" ? "NA" : h), (v == "" ? "NA" : v), (p == "" ? "NA" : p)}')
python3 -c "import sys; [float(x) for x in sys.argv[1:]]" "$KX_PROBE" "$PB_B" "$PB_L" "$PB_H" "$V_BENCH" "$P_BENCH" 2>/dev/null \
    || { echo "GUARD: $BREL/bench.log.gz lacks a KAPPA_X PROBE, INVARIANT PASS, probability_of_voucher or price line (kappa_x probe '$KX_PROBE', base '$PB_B,$PB_L,$PB_H', pi_V '$V_BENCH', price '$P_BENCH'): did the solve reach save_welfare_curve?"; exit 1; }
if [ -f "$C/cfarm_bench/BENCH_DONE" ] && [ "$(cat "$C/cfarm_bench/BENCH_FROM" 2>/dev/null)" != "$REF" ]; then
    echo "GUARD: code/cfarm_bench holds another benchmark ($(cat "$C/cfarm_bench/BENCH_FROM" 2>/dev/null || echo 'one solved in place')), which the impact runs would reuse: move it aside and run again"; exit 1
fi
R=$REPO/results/whostops_omega1_pts_$PTS
[ "${OMEGA1_DRY:-0}" = 1 ] || mkdir -p "$R"
D=$C/whostops_worker_omega1_pts_$PTS
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
THREADS=${THREADS:-$(python3 -c "import os; print(max(1, min(4, os.cpu_count() // 2)))")}
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
# Housing First's price and pi_V for this economy: pi_V the benchmark's (Housing First holds it there), the price the
# re-solved Housing First's once it is in (code/omega1/remote_omega1_arm.sh null), until then the benchmark's own
V_NULL=$V_BENCH
P_NULL=$P_BENCH; PSRC="the benchmark's own, $BREL/bench.log.gz: no re-solved Housing First at omega_c = 1 in this checkout"
NF=$REPO/results/omega1_Cu/cf/null
if [ -s "$NF/final.txt" ] && grep -qxF "addiction_scalar_1 $OMEGA1_B" "$NF/PARAM_HANDOVER.arm.txt" 2>/dev/null; then
    P_NULL=$(awk '/^ *drug price /{print $3}' "$NF/final.txt")
    VN=$(awk '/^ *pi_V \(voucher probability\) /{print $4}' "$NF/final.txt")
    python3 -c "import sys; p, v, vb = map(float, sys.argv[1:]); sys.exit(0 if 0 < p and abs(v / vb - 1) < 1e-7 else 1)" "$P_NULL" "$VN" "$V_BENCH" 2>/dev/null \
        || { echo "GUARD: results/omega1_Cu/cf/null/final.txt: price '$P_NULL', pi_V '$VN' against the benchmark's $V_BENCH"; exit 1; }
    PSRC="the re-solved Housing First's, results/omega1_Cu/cf/null/final.txt"
fi
export BENCH_FROM=$REF BENCH_B=$OMEGA1_B BENCH_OMEGA=1.0 BENCH_KU=1.0
export KAPPA_X=$(python3 -c "print(repr(float('$KX_PROBE') * 1.5076))")
export PASSES_BASE="$PB_B,$PB_L,$PB_H"
export CEV_CURVE=$D.welfare_curve.dat

note() { echo "run_whostops_omega1: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

if [ "${WSPT_DETACHED:-0}" != 1 ] && [ "${OMEGA1_DRY:-0}" != 1 ]; then
    if alive "$D.pid"; then
        echo "run_whostops_omega1: attaching to the running worker, pid $(cat "$D.pid")"
    else
        ( WSPT_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/whostops_omega1_pts_$PTS.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "run_whostops_omega1: started detached, pid $(cat "$D.pid"); log /tmp/whostops_omega1_pts_$PTS.detached.log"
    fi
    while alive "$D.pid"; do sleep 60; done
    echo "run_whostops_omega1: finished"; cat "$D.status" 2>/dev/null
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
    [ "${OMEGA1_DRY:-0}" = 1 ] && return 0
    {
        echo "# who stops using under Treatment First at omega_c = 1, state by state, on Housing First's distribution: $BREL (b $OMEGA1_B, kappa_x $KAPPA_X; base $PASSES_BASE), price $P_NULL and pi_V $V_NULL held (the price $PSRC); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for d in "$C"/cfarm_*_imp_wo1*; do
            [ -f "$d/cf.log" ] || continue
            echo; echo "== $(basename "$d"): $(grep -ac 'CF MOMENTS' "$d/cf.log") passes; use among holders, eligible, tested; eligible mass: $(diag "$d/cf.log")"
            python3 "$C/cf_runs/passes.py" "$d/cf.log" "$C/cf_runs/cev.py" 2>/dev/null | tail -n 4
        done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO" || exit 0
    git add "$R" 2>/dev/null
    git commit -q -m "whostops omega_c 1 (b $OMEGA1_B) detection points $PTS: $1$TRAILER" || return 0
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
slim() {   # <dir>: keep a finished run's log, drop its copies of the benchmark and its output files (the disk)
    [ -d "$1" ] || return 0
    find "$1" -maxdepth 1 -type f ! -name 'cf.log' ! -name 'cf.err' ! -name '*.txt' ! -name '*.out' -size +1M -delete 2>/dev/null
}
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
    bash treat/build_treatC_impact_C.sh > /tmp/whostops_omega1_build.log 2>&1 \
        || { note "GUARD: build failed: $(tail -3 /tmp/whostops_omega1_build.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
note "build: $(tail -1 /tmp/whostops_omega1_build.log 2>/dev/null)"
f=$C/cf_fix2_treatC_impact/cf.f90
[ "$(grep -c 'RULE C (patch_treatC.py)' "$f")" = 1 ] && [ "$(grep -c "THE HOUSEHOLD'S OWN TREATMENT CHOICE (patch_treatC.py)" "$f")" = 2 ] \
    && grep -q 'DIAG use by voucher state' "$f" && grep -q '^        integer, parameter :: fixed_to_benchmark_dis=1$' "$f" \
    || { note "GUARD: cf_fix2_treatC_impact lacks a patch"; publish "failed"; exit 1; }
publish "built"

TF_SET="cost_per_drug_test $CTEST;adjust_taxes 0"
grep -q "DIAG who stops" "$C/cf_fix2_treatC_impact/cf.f90" || { note "GUARD: cf_fix2_treatC_impact lacks the who-stops line"; publish "failed"; exit 1; }
tag() { echo "wo1_p$(python3 -c "print('%03d' % round(1000 * $1))")"; }
note "benchmark $BREL: kappa_x $KAPPA_X (probe $KX_PROBE x 1.5076), base $PASSES_BASE; Housing First's price $P_NULL ($PSRC), pi_V $V_NULL (the benchmark's)"
if [ "${OMEGA1_DRY:-0}" = 1 ]; then
    note "DRY: the reference would run as: imp wo1ref null cf_fix2_treatC_impact, BENCH_FROM=$BENCH_FROM BENCH_B=$BENCH_B BENCH_OMEGA=$BENCH_OMEGA BENCH_KU=$BENCH_KU KAPPA_X=$KAPPA_X SEED_FROM=bench PV_START=$V_NULL DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0, 4 threads"
    for p in "${PARGS[@]}"; do note "DRY: detection $p would run as: imp $(tag "$p") tf cf_fix2_treatC_impact PDET=$p EXTRA_SET=$TF_SET DIAG_HF_FROM=$D.hf_states.bin, 2 threads"; done
    note "DRY: results would go to ${R#$REPO/}; nothing solved, nothing committed"
    exit 0
fi
if ! imp_done null wo1ref; then THREADS=4 imp wo1ref null cf_fix2_treatC_impact; wait_all "reference" "$D.imp_wo1ref.pid"; fi
imp_done null wo1ref || { note "GUARD: the reference printed no DIAG line: $(tail -3 "$C/cfarm_null_imp_wo1ref.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
HFF=$C/cfarm_null_imp_wo1ref/DIAG_STATES_OUT.bin
[ -s "$D.hf_states.bin" ] || cp "$HFF" "$D.hf_states.bin" 2>/dev/null
[ -s "$D.hf_states.bin" ] && HFF=$D.hf_states.bin
[ -s "$HFF" ] || { note "GUARD: the reference wrote no DIAG_STATES_OUT.bin"; publish "failed"; exit 1; }
note "reference: $(diag "$C/cfarm_null_imp_wo1ref/cf.log")  [use among holders, eligible, tested; eligible mass]; states file $(du -h "$HFF" | cut -f1)"
THREADS=2
[ "$HFF" = "$D.hf_states.bin" ] && slim "$C/cfarm_null_imp_wo1ref"
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
# ta <tag>: ALL the tested users who stop, per cent (t_stop / t_used), the share detection is calibrated to
# (x_ws_tested_all_pc in code/paper/export_whostops.py, whose KEYS name the line's thirteen numbers)
ta() {
    L=$(grep -a "DIAG who stops" "$C/cfarm_tf_imp_$1/cf.log" 2>/dev/null | tail -n 1)
    python3 - "$L" <<'PYEOF'
import re, sys
v = [float(x) for x in re.findall(r'=\s*([-+0-9.Ee]+)', sys.argv[1].replace('=', ' = '))]
print('%.4f' % (100 * v[8] / v[7]) if len(v) >= 13 and v[0] == 1 and v[7] else 'NA')
PYEOF
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
        for p in $batch; do t=$(tag "$p"); echo "$p $(tn "$t") $(ta "$t")" >> "$D.scan"; note "detection $p: $(ta "$t") per cent of ALL tested users stop (the calibrated share, target $TARGET_WS), $(tn "$t") per cent of tested users without a SUD"; slim "$C/cfarm_tf_imp_$t"; done
        publish "$l"
    done
}
round "detection points ${PARGS[*]}" "${PARGS[@]}"
note "points (detection, per cent of tested users without a SUD who stop, per cent of ALL tested users who stop; target $TARGET_WS on the last): $(sort -n -u "$D.scan" | tr '\n' ';')"
{ echo "# detection, per cent of tested users without a SUD who stop, per cent of ALL tested users who stop (t_stop / t_used, the calibrated share; target $TARGET_WS)"; sort -n -u "$D.scan"; } > "$R/scan.txt"
for d in "$C"/cfarm_*_imp_wo1*; do mkdir -p "$R/$(basename "$d")"; gzip -c "$d/cf.log" > "$R/$(basename "$d")/cf.log.gz" 2>/dev/null; done
note "detection points done"
publish "detection points done"
