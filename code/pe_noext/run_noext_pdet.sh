#!/bin/bash
# run_noext_pdet.sh -- THE FIRST EXPERIMENT'S OWN DETECTION RATE, THEN ITS FOUR COLUMNS AT IT (8 November; the author:
# "can you rechoose p_det for the no externalities simulations to get the same drug use reaction? and tell the reader
# you do", and "ok do it properly"). The first experiment (Section 6.2, Table 5's columns 2 to 5) is the no-children
# economy: weight_on_child 0, penalty_child_addicted 0, penalty_child_homeless 0, every other parameter calibrated. Its
# Treatment First ran at the main experiment's detection rate, 0.20, chosen in the economy WITH children; the omega_c = 1
# experiment re-chose its own (0.15). This does the same for the first experiment, by the main experiment's rule:
#
#   1. ARM A, the no-children Housing First (cfarm_null_pe_noext_Cu, noext_clear/noext_Cu_lib.sh's start_arm_A), re-solved
#      because only its summary is in the repo (results/pe_noext_Cu/arm_A) and the impact runs need its distribution.
#      Warm start CU_P_NULL = its 14 October run's last PE USED price, from which it took 3 passes then.
#   2. WHO STOPS ON IMPACT, as code/omega1/run_whostops_omega1.sh and code/deter_2c/run_whostops_C_points.sh measure it:
#      the impact build cf_fix2_treatC_impact (the distribution fixed), the drug price and pi_V held at Arm A's last PE
#      USED values, the Housing First reference writing each state's choice, then Treatment First at each detection
#      rate, and the share of ALL tested users who stop (t_stop / t_used, x_ws_tested_all_pc's measure; target
#      Mehay and Pacula's 61, lit 'mp_stay_rel_pc'). What differs: the switches are on in every run, and the fixed
#      distribution is ARM A'S, not the benchmark's (pe_noext/cf_arm_pe_noext_ws.sh, FIXED_DIST_FROM). The house price
#      is not held, as in the main and omega_c = 1 measures: cf_fix2 pegs it near the calibrated value, where Arm A's
#      also sits (12.04925).
#   3. THE CHOICE: the grid NOEXT_GRID (0.15 0.20 0.25 0.30), two at a time; the point closest to the target; if it is
#      more than 1.5 points off, the rate interpolated between the bracketing points (to 0.005), or past the grid's end
#      if the target is outside it, at most three more rounds. results/noext_pdet/chosen_pdet.txt.
#   4. If the choice is not 0.20, THE FOUR COLUMNS at it: pe_noext/run_pe_Cw.sh (both held), noext_clear/
#      run_noext_fixp_Cw.sh (pi_V clears), run_noext_pclear_Cw.sh (the price clears), run_noext_clear_Cw.sh (both clear),
#      the _Cu launchers with RULEC_PDET and their own results (results/*_Cw), sharing this container's Arm A, walk and
#      solve gate (two solves of two threads). Warm starts: the _Cu columns' own final prices.
#
# NOEXT_DRY=1 runs in the foreground: checks the inputs, prints what each step would run, and stops (no solve, no commit).
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root, and run it again whenever the call stops (it
# attaches):  bash code/pe_noext/run_noext_pdet.sh
set -u
TAG=noext_pdet; STATUS=pdet.status
HEADER="The first experiment's detection rate (who stops on impact in the no-children economy), then its four columns at it (code/pe_noext/run_noext_pdet.sh)"
_C=$(cd "$(dirname "$0")/.." && pwd)
_REPO=$(cd "$_C/.." && pwd)
W=$_C/pe_noext/work_pdet; R=$_REPO/results/noext_pdet
ARMS_SHOWN="cfarm_null_pe_noext_Cu"
CU_P_NULL=${CU_P_NULL:-$(zcat "$_REPO/results/pe_noext_Cu/arm_A/cf.log.gz" 2>/dev/null | grep -a 'PE USED' | tail -n 1 | awk '{for(i=1;i<=NF;i++) if($i=="drug_price=") print $(i+1)}')}
export CU_P_NULL
. "$_C/noext_clear/noext_Cu_lib.sh"
TARGET_WS=${TARGET_WS:-$(python3 -c "import json; print(json.load(open('$REPO/code/paper/lit_numbers.json'))['mp_stay_rel_pc'])")}
GRID=${NOEXT_GRID:-"0.15 0.20 0.25 0.30"}
CU=$REPO/results
# the four columns' warm starts: the _Cu columns' own finals (at 0.20)
WS_V_D=$(awk '/^  pi_V /{print $NF}' "$CU/noext_fixp_Cu/arm_D/final.txt" 2>/dev/null)
WS_P_E=$(awk '/^  drug price /{print $NF}' "$CU/noext_pclear_Cu/arm_E/final.txt" 2>/dev/null)
WS_P_C=$(awk '/^  drug price /{print $NF}' "$CU/noext_clear_Cu/arm_C/final.txt" 2>/dev/null)
WS_V_C=$(awk '/^  pi_V /{print $NF}' "$CU/noext_clear_Cu/arm_C/final.txt" 2>/dev/null)
python3 -c "import sys; [float(x) for x in sys.argv[1:]]; t = float(sys.argv[-1]); sys.exit(0 if 30 < t < 90 else 1)" \
    "$CU_P_NULL" "$WS_V_D" "$WS_P_E" "$WS_P_C" "$WS_V_C" "$TARGET_WS" 2>/dev/null \
    || { echo "GUARD: an input is missing: arm A's warm start '$CU_P_NULL', warm starts D '$WS_V_D', E '$WS_P_E', C '$WS_P_C' '$WS_V_C', target '$TARGET_WS'"; exit 1; }
for g in $GRID; do python3 -c "import sys; sys.exit(0 if 0 < float('$g') < 1 else 1)" 2>/dev/null || { echo "GUARD: '$g' in NOEXT_GRID is not a rate"; exit 1; }; done
if [ -f "$C/cfarm_bench/BENCH_DONE" ] && [ "$(cat "$C/cfarm_bench/BENCH_FROM" 2>/dev/null)" != "$REF" ]; then
    echo "GUARD: code/cfarm_bench holds another benchmark ($(cat "$C/cfarm_bench/BENCH_FROM" 2>/dev/null)), which every run here would reuse: move it aside and run again"; exit 1
fi
for f in pe_noext/run_pe_Cw.sh noext_clear/run_noext_fixp_Cw.sh noext_clear/run_noext_pclear_Cw.sh noext_clear/run_noext_clear_Cw.sh \
         pe_noext/cf_arm_pe_noext_ws.sh treat/build_treatC_impact_C.sh; do
    [ -s "$C/$f" ] || { echo "GUARD: code/$f missing"; exit 1; }
done
if [ "${NOEXT_DRY:-0}" = 1 ]; then
    echo "DRY: arm A ($A_DIR) from drug price $CU_P_NULL, switches '$SWITCHES', 4 threads"
    echo "DRY: reference: env BUILD=cf_fix2_treatC_impact DIAG_TAG=_imp_nxref SEED_FROM=$A_DIR FIXED_DIST_FROM=$A_DIR PV_START=<arm A's pi_V> DRUG_PRICE_START=<arm A's last PE USED price> DRUG_MARKET_ADJUSTER=0 EXTRA_SET='$SWITCHES' sh pe_noext/cf_arm_pe_noext_ws.sh null"
    for g in $GRID; do echo "DRY: detection $g: the same with PDET=$g EXTRA_SET='cost_per_drug_test $CTEST;adjust_taxes 0;$SWITCHES' DIAG_HF_FROM=<the reference's states> ... tf"; done
    echo "DRY: target $TARGET_WS per cent of ALL tested users; columns' warm starts: D pi_V $WS_V_D, E price $WS_P_E, C price $WS_P_C pi_V $WS_V_C"
    echo "DRY: results to ${R#$REPO/}; nothing solved, nothing committed"
    exit 0
fi
detach "$0"

note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc); target $TARGET_WS per cent of all tested users; grid $GRID"
build_all
exec 6> "$SH/build.lock"; flock 6
if ! { [ -x "$C/cf_fix2_treatC_impact/hftf_cf_prod" ] && [ ! "$C/cf_fix2_treatC_impact/hftf_cf_prod" -ot "$C/cf_fix2_treatC/hftf_cf_prod" ]; }; then
    note "building cf_fix2_treatC_impact (treat/build_treatC_impact_C.sh)"
    ( cd "$C" && bash treat/build_treatC_impact_C.sh ) > "$W/build_impact.log" 2>&1 \
        || { note "GUARD: impact build failed: $(tail -n 3 "$W/build_impact.log" | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
flock -u 6; exec 6>&-
f=$C/cf_fix2_treatC_impact/cf.f90
[ "$(grep -c 'RULE C (patch_treatC.py)' "$f")" = 1 ] && grep -q 'DIAG who stops' "$f" && grep -q 'DIAG use by voucher state' "$f" \
    && grep -q '^        integer, parameter :: fixed_to_benchmark_dis=1$' "$f" \
    || { note "GUARD: cf_fix2_treatC_impact lacks a patch"; publish "failed"; exit 1; }
publish "built"
cd "$C"

# 1. ARM A
THREADS=4; start_arm_A; THREADS=2
wait_arm_A
U=$(grep -a "PE USED" "$C/$A_DIR/cf.log" | tail -n 1)
P_A=$(echo "$U" | awk '{for(i=1;i<=NF;i++) if($i=="drug_price=") print $(i+1)}')
PV_A=$(echo "$U" | awk '{for(i=1;i<=NF;i++) if($i=="pi_V=") print $(i+1)}')
python3 -c "import sys; [float(x) for x in sys.argv[1:3]]" "$P_A" "$PV_A" || { note "GUARD: no PE USED prices in arm A's log"; publish "arm A prices missing"; exit 1; }
B_A=$(python3 cf_runs/finalstats.py "$A_DIR/cf.log" 2>/dev/null | awk '/drug use b/{print $NF}')
note "arm A: $(grep -a 'CHECK PASS' "$C/$A_DIR.out" | tr '\n' ' '); last solve's drug price $P_A, pi_V $PV_A; drug use $B_A (14 October: 0.089691198)"
publish "arm A done"

# 2. WHO STOPS ON IMPACT
diag() {   # <cf.log>: use among holders, eligible, tested; eligible mass (the last 'DIAG use by voucher state' line)
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
    m = re.search(re.escape(k) + r'\s*=\s*(\S+)', l)
    return float(m.group(1)) if m else float('nan')
print('%.10f %.10f %.10f %.10f' % (g('holding'), g('eligible'), g('tested'), g('eligible mass')))
PYEOF
}
whostops() {   # <tag> <field index>: per cent, from the run's last who-stops line (8/7 all tested, 11/10 tested without a SUD)
    L=$(grep -a "DIAG who stops" "$C/cfarm_tf_imp_$1/cf.log" 2>/dev/null | tail -n 1)
    python3 - "$L" "$2" <<'PYEOF'
import re, sys
v = [float(x) for x in re.findall(r'=\s*([-+0-9.Ee]+)', sys.argv[1].replace('=', ' = '))]
n, d = {'all': (8, 7), 'nosud': (11, 10)}[sys.argv[2]]
print('%.4f' % (100 * v[n] / v[d]) if len(v) >= 13 and v[0] == 1 and v[d] else 'NA')
PYEOF
}
imp() {   # <tag> <null|tf> <threads> [VAR=value ...]: an impact run on Arm A's distribution at Arm A's price and pi_V
    t=$1; a=$2; th=$3; shift 3
    note "impact $a $t ($th threads): $*"
    ( cd "$C" && env BUILD=cf_fix2_treatC_impact OMP_NUM_THREADS=$th DIAG_TAG="_imp_$t" SEED_FROM=$A_DIR FIXED_DIST_FROM=$A_DIR \
        PV_START=$PV_A DRUG_PRICE_START=$P_A DRUG_MARKET_ADJUSTER=0 "$@" sh pe_noext/cf_arm_pe_noext_ws.sh "$a" \
        > "$C/cfarm_${a}_imp_$t.out" 2>&1 ) &
    echo $! > "$W/imp_$t.pid"
}
imp_done() { [ -f "$C/cfarm_$1_imp_$2/cf.log" ] && [ "$(diag "$C/cfarm_$1_imp_$2/cf.log")" != NA ]; }
slim() {   # <dir>: keep a finished run's log, drop its copies of the benchmark's files (the disk)
    [ -d "$1" ] || return 0
    find "$1" -maxdepth 1 -type f ! -name 'cf.log' ! -name 'cf.err' ! -name '*.txt' ! -name '*.out' -size +1M -delete 2>/dev/null
}
tag() { echo "nx_p$(python3 -c "print('%03d' % round(1000 * $1))")"; }

if ! imp_done null nxref; then imp nxref null 4 EXTRA_SET="$SWITCHES"; wait_publishing "reference" "$W/imp_nxref.pid"; fi
imp_done null nxref || { note "GUARD: the reference printed no DIAG line: $(grep -a GUARD "$C/cfarm_null_imp_nxref.out" | head -n 2 | tr '\n' ' ') $(tail -n 2 "$C/cfarm_null_imp_nxref.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
grep -aq "distribution fixed at $A_DIR's" "$C/cfarm_null_imp_nxref.out" || { note "GUARD: the reference did not fix the distribution at arm A's"; publish "failed"; exit 1; }
HFF=$W/hf_states.bin
[ -s "$HFF" ] || cp "$C/cfarm_null_imp_nxref/DIAG_STATES_OUT.bin" "$HFF" 2>/dev/null
[ -s "$HFF" ] || { note "GUARD: the reference wrote no DIAG_STATES_OUT.bin"; publish "failed"; exit 1; }
B_REF=$(grep -a "MOMENT b " "$C/cfarm_null_imp_nxref/cf.log" | tail -n 1 | awk '{for(i=1;i<=NF;i++) if($i=="model=") print $(i+1)}')
note "reference: drug use $B_REF (arm A $B_A); use among holders, eligible, tested; eligible mass: $(diag "$C/cfarm_null_imp_nxref/cf.log"); states file $(du -h "$HFF" | cut -f1)"
slim "$C/cfarm_null_imp_nxref"
publish "reference done"

TF_SET="cost_per_drug_test $CTEST;adjust_taxes 0;$SWITCHES"
touch "$W/scan"
round() {   # <p>...: the screen at each rate, two at a time, two threads each
    while [ $# -gt 0 ]; do
        pids=""; batch=""
        for p in "$1" "${2:-}"; do
            [ -n "$p" ] || continue
            t=$(tag "$p"); batch="$batch $p"
            imp_done tf "$t" || alive "$W/imp_$t.pid" || imp "$t" tf 2 PDET="$p" EXTRA_SET="$TF_SET" DIAG_HF_FROM="$HFF"
            pids="$pids $W/imp_$t.pid"
        done
        shift; [ $# -gt 0 ] && shift
        wait_publishing "detection$batch" $pids
        for p in $batch; do
            t=$(tag "$p")
            grep -q "^$p " "$W/scan" || echo "$p $(whostops "$t" nosud) $(whostops "$t" all)" >> "$W/scan"
            note "detection $p: $(whostops "$t" all) per cent of ALL tested users stop (target $TARGET_WS), $(whostops "$t" nosud) per cent of those without a SUD"
            slim "$C/cfarm_tf_imp_$t"
        done
        publish "detection$batch done"
    done
}
# next: DONE <p> when the closest point is within 1.5 of the target (or nothing new is left to try), else RUN <p>...
next() {
    python3 - "$W/scan" "$TARGET_WS" <<'PYEOF'
import sys
T = float(sys.argv[2])
pts = {}
for l in open(sys.argv[1]):
    f = l.split()
    if len(f) == 3 and f[2] != 'NA':
        pts[round(float(f[0]), 4)] = float(f[2])
if not pts:
    print('FAIL'); raise SystemExit
best = min(pts, key=lambda p: (abs(pts[p] - T), p))
if abs(pts[best] - T) <= 1.5:
    print('DONE', best); raise SystemExit
below = [p for p in pts if pts[p] < T]
above = [p for p in pts if pts[p] > T]
if below and above:
    lo, hi = max(below), min(above)
    if hi > lo:
        q = lo + (T - pts[lo]) * (hi - lo) / (pts[hi] - pts[lo])
    else:
        q = (lo + hi) / 2
    q = round(round(q / 0.005) * 0.005, 3)
    new = [q] if q not in pts and 0 < q < 1 else []
elif below:
    top = max(pts)
    new = [round(min(top + d, 0.95), 3) for d in (0.10, 0.20) if round(min(top + d, 0.95), 3) not in pts]
else:
    bot = min(pts)
    new = [round(x, 3) for x in (bot / 2, bot / 4) if round(x, 3) not in pts and x > 0.005]
print(('RUN ' + ' '.join('%g' % q for q in new)) if new else 'DONE %g' % best)
PYEOF
}
round $GRID
for _ in 1 2 3; do
    N=$(next)
    case "$N" in RUN*) set -- ${N#RUN }; note "closest point more than 1.5 off the target: running $*"; round "$@" ;; *) break ;; esac
done
N=$(next)
case "$N" in DONE*) CHOSEN=${N#DONE } ;; *) note "GUARD: no detection rate chosen ($N)"; publish "failed"; exit 1 ;; esac
{ echo "# detection, per cent of tested users without a SUD who stop, per cent of ALL tested users who stop (t_stop / t_used, the calibrated share; target $TARGET_WS); no-children economy, on arm A's distribution at drug price $P_A, pi_V $PV_A"; sort -n -u "$W/scan"; } > "$R/scan.txt"
echo "$CHOSEN" > "$R/chosen_pdet.txt"
for d in "$C"/cfarm_*_imp_nx*; do [ -d "$d" ] || continue; mkdir -p "$R/$(basename "$d")"; gzip -c "$d/cf.log" > "$R/$(basename "$d")/cf.log.gz" 2>/dev/null; cp "$d.out" "$R/$(basename "$d")/arm.out" 2>/dev/null; done
rm -rf "$C"/cfarm_*_imp_nx*/
note "DETECTION CHOSEN: $CHOSEN, $(awk -v p="$CHOSEN" '$1 + 0 == p + 0 {print $3}' "$W/scan" | head -n 1) per cent of all tested users stop (target $TARGET_WS); points: $(sort -n -u "$W/scan" | awk '{print $1 " -> " $3}' | tr '\n' ';')"
publish "detection chosen: $CHOSEN"

# 4. THE FOUR COLUMNS at the chosen rate, unless it is the 0.20 they ran at
if python3 -c "import sys; sys.exit(0 if abs(float('$CHOSEN') - 0.20) < 1e-9 else 1)"; then
    note "the chosen rate is 0.20, the one the _Cu columns ran at: they stand, nothing more to run"
    publish "done (0.20 stands)"
    exit 0
fi
export RULEC_PDET=$CHOSEN
# NC_C_DETACHED=0 below: this script runs with NC_C_DETACHED=1 (the library's detach), which the launchers would
# inherit and then run in the foreground with no run.pid to wait on
note "launching the four columns at detection $RULEC_PDET (results/*_Cw)"
( cd "$REPO" && NC_C_DETACHED=0 bash code/pe_noext/run_pe_Cw.sh > "$W/col_pe.log" 2>&1 & )
( cd "$REPO" && NC_C_DETACHED=0 CU_V0=$WS_V_D bash code/noext_clear/run_noext_fixp_Cw.sh > "$W/col_fixp.log" 2>&1 & )
( cd "$REPO" && NC_C_DETACHED=0 NOEXT_P0=$WS_P_E bash code/noext_clear/run_noext_pclear_Cw.sh > "$W/col_pclear.log" 2>&1 & )
( cd "$REPO" && NC_C_DETACHED=0 NOEXT_P0=$WS_P_C NOEXT_V0=$WS_V_C bash code/noext_clear/run_noext_clear_Cw.sh > "$W/col_clear.log" 2>&1 & )
COLS="$C/pe_noext/work_Cw/run.pid $C/noext_clear/work_fixp_Cw/run.pid $C/noext_clear/work_pclear_Cw/run.pid $C/noext_clear/work_clear_Cw/run.pid"
sleep 120
wait_publishing "four columns running at $RULEC_PDET" $COLS
for c in pe_noext_Cw noext_fixp_Cw noext_pclear_Cw noext_clear_Cw; do
    a=$REPO/results/$c/analysis.txt
    if [ -s "$REPO/results/$c/analysis.json" ]; then note "$c: $(grep -i 'newborn adult (age 26)' "$a" | head -n 1 | tr -s ' ')"; else note "GUARD: $c has no analysis (see results/$c/status.txt)"; fi
done
note "done"
publish "done"
