#!/bin/bash
# run_noext_col.sh <pe|fixp|pclear|clear> -- ONE OF THE FIRST EXPERIMENT'S FOUR COLUMNS IN ITS OWN SESSION (8 November;
# the author: "Can you use additional sessions to minimize time?"). pe_noext/run_noext_pdet.sh chooses the detection
# rate and would then run the four columns in its own container, two solves at a time (about five hours on 14
# October). Instead, each column gets a container: while the rate is being chosen it solves the no-children Housing
# First (arm A, shared library noext_clear/noext_Cu_lib.sh) and the walk on its policies, both at four threads; then it
# waits for results/noext_pdet/columns_pdet.txt on the branch (written by hand from the points of run_noext_pdet.sh and
# run_noext_pdet_x.sh), and runs its column's _Cw launcher alone, at four threads (NOEXT_THREADS=4, NOEXT_COLS_HERE=1,
# which results/noext_pdet/columns_elsewhere otherwise blocks). If the rate is 0.20 the _Cu column stands and it stops.
# Warm starts as run_noext_pdet.sh's: the _Cu columns' finals. Its own status: results/noext_col_<col>/status.txt; the
# column's results: results/<column>_Cw, pushed again at the end until they are on the branch.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root, and run it again whenever the call stops (it
# attaches):  bash code/pe_noext/run_noext_col.sh <pe|fixp|pclear|clear>
set -u
COL=${1:-}
case "$COL" in
    pe)     LAUNCH=pe_noext/run_pe_Cw.sh;            RD=pe_noext_Cw;     LW=pe_noext/work_Cw ;;
    fixp)   LAUNCH=noext_clear/run_noext_fixp_Cw.sh;   RD=noext_fixp_Cw;   LW=noext_clear/work_fixp_Cw ;;
    pclear) LAUNCH=noext_clear/run_noext_pclear_Cw.sh; RD=noext_pclear_Cw; LW=noext_clear/work_pclear_Cw ;;
    clear)  LAUNCH=noext_clear/run_noext_clear_Cw.sh;  RD=noext_clear_Cw;  LW=noext_clear/work_clear_Cw ;;
    *) echo "GUARD: usage: bash code/pe_noext/run_noext_col.sh <pe|fixp|pclear|clear>, not '$COL'"; exit 1 ;;
esac
TAG=noext_col_$COL; STATUS=col.status
HEADER="The first experiment's column '$COL' in its own session: arm A and the walk now, the column once the detection rate is chosen (code/pe_noext/run_noext_col.sh)"
_C=$(cd "$(dirname "$0")/.." && pwd)
_REPO=$(cd "$_C/.." && pwd)
W=$_C/pe_noext/work_col_$COL; R=$_REPO/results/noext_col_$COL
ARMS_SHOWN="cfarm_null_pe_noext_Cu"
CU_P_NULL=${CU_P_NULL:-$(zcat "$_REPO/results/pe_noext_Cu/arm_A/cf.log.gz" 2>/dev/null | grep -a 'PE USED' | tail -n 1 | awk '{for(i=1;i<=NF;i++) if($i=="drug_price=") print $(i+1)}')}
export CU_P_NULL
export NOEXT_THREADS=4
. "$_C/noext_clear/noext_Cu_lib.sh"
CU=$REPO/results
WS_V_D=$(awk '/^  pi_V /{print $NF}' "$CU/noext_fixp_Cu/arm_D/final.txt" 2>/dev/null)
WS_P_E=$(awk '/^  drug price /{print $NF}' "$CU/noext_pclear_Cu/arm_E/final.txt" 2>/dev/null)
WS_P_C=$(awk '/^  drug price /{print $NF}' "$CU/noext_clear_Cu/arm_C/final.txt" 2>/dev/null)
WS_V_C=$(awk '/^  pi_V /{print $NF}' "$CU/noext_clear_Cu/arm_C/final.txt" 2>/dev/null)
python3 -c "import sys; [float(x) for x in sys.argv[1:]]" "$CU_P_NULL" "$WS_V_D" "$WS_P_E" "$WS_P_C" "$WS_V_C" 2>/dev/null \
    || { echo "GUARD: an input is missing: arm A's warm start '$CU_P_NULL', warm starts D '$WS_V_D', E '$WS_P_E', C '$WS_P_C' '$WS_V_C'"; exit 1; }
[ -s "$C/$LAUNCH" ] || { echo "GUARD: code/$LAUNCH missing"; exit 1; }
if [ -f "$C/cfarm_bench/BENCH_DONE" ] && [ "$(cat "$C/cfarm_bench/BENCH_FROM" 2>/dev/null)" != "$REF" ]; then
    echo "GUARD: code/cfarm_bench holds another benchmark ($(cat "$C/cfarm_bench/BENCH_FROM" 2>/dev/null))"; exit 1
fi
XS="-0.5 -0.3 -0.2 -0.15 -0.1 -0.07 -0.05 -0.03 -0.02 -0.01 -0.005 -0.002 -0.0005 0.0 0.0005 0.002 0.005 0.01 0.02 0.05 0.1 0.15 0.2 0.3"
if [ "${NOEXT_DRY:-0}" = 1 ]; then
    echo "DRY: column $COL: arm A from $CU_P_NULL at $THREADS threads, the walk, then wait for results/noext_pdet/columns_pdet.txt and run NOEXT_COLS_HERE=1 bash code/$LAUNCH (results/$RD); warm starts D $WS_V_D, E $WS_P_E, C $WS_P_C $WS_V_C"
    exit 0
fi
# detach, keeping the column argument (the library's detach re-runs the script with none)
if [ "${NC_COL_DETACHED:-0}" != 1 ]; then
    if alive "$W/run.pid"; then echo "attached to pid $(cat "$W/run.pid")"; else
        ( NC_COL_DETACHED=1 setsid nohup bash "$0" "$COL" > "$W/run.detached.log" 2>&1 < /dev/null & echo $! > "$W/run.pid" )
        echo "started detached, pid $(cat "$W/run.pid")"
    fi
    while alive "$W/run.pid"; do sleep 60; done
    echo "$TAG: finished"; cat "$W/$STATUS" 2>/dev/null
    exit 0
fi

note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc), threads per solve $THREADS"
build_all
publish "built"
cd "$C"
start_arm_A
wait_arm_A
note "arm A: $(grep -a 'CHECK PASS' "$C/$A_DIR.out" | tr '\n' ' ')"
publish "arm A done"
run_walk pe_walk_A_Cu "$XS"
publish "walk done; waiting for the detection rate"

# the rate: results/noext_pdet/columns_pdet.txt on the branch, checked every two minutes, for up to 14 hours
fetch_rate() {
    ( cd "$REPO"; exec 8> "$SH/git.lock"; flock 8; git fetch -q origin "$BRANCH" 2>/dev/null
      git show "FETCH_HEAD:results/noext_pdet/columns_pdet.txt" 2>/dev/null | head -n 1 | tr -d ' \r' )
}
P=""
for i in $(seq 1 420); do
    P=$(fetch_rate)
    [ -n "$P" ] && break
    [ $((i % 10)) = 0 ] && publish "waiting for the detection rate"
    sleep 120
done
python3 -c "import sys; p = float('$P'); sys.exit(0 if 0 < p < 1 else 1)" 2>/dev/null || { note "GUARD: no detection rate on the branch after 14 hours ('$P')"; publish "no rate"; exit 1; }
if python3 -c "import sys; sys.exit(0 if abs(float('$P') - 0.20) < 1e-9 else 1)"; then
    note "the detection rate is 0.20, the one the _Cu column ran at: it stands"
    publish "done (0.20 stands)"; exit 0
fi
export RULEC_PDET=$P
note "detection rate $RULEC_PDET: launching $LAUNCH alone at $THREADS threads"
publish "column launched at $RULEC_PDET"
( cd "$REPO" && NC_C_DETACHED=0 NOEXT_COLS_HERE=1 CU_V0=$WS_V_D NOEXT_P0=$( [ "$COL" = clear ] && echo "$WS_P_C" || echo "$WS_P_E" ) NOEXT_V0=$WS_V_C \
    bash "code/$LAUNCH" > "$W/launch.log" 2>&1 & )
sleep 120
wait_publishing "column $COL running at $RULEC_PDET" "$C/$LW/run.pid"
if [ -s "$REPO/results/$RD/analysis.json" ]; then
    note "$RD: $(grep -i 'newborn adult (age 26)' "$REPO/results/$RD/analysis.txt" | head -n 1 | tr -s ' ')"
else
    note "GUARD: $RD has no analysis (results/$RD/status.txt)"
fi
publish "column done"
# the column's results must reach the branch: push until they are there
for i in $(seq 1 30); do
    ok=$( cd "$REPO"; exec 8> "$SH/git.lock"; flock 8
          git add "results/$RD" "${R#$REPO/}" 2>/dev/null; git commit -q -m "$TAG: results$TRAILER" 2>/dev/null
          git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && git push -q origin HEAD:"$BRANCH" 2>/dev/null
          git rebase --abort 2>/dev/null
          git fetch -q origin "$BRANCH" && git diff --quiet FETCH_HEAD -- "results/$RD" && echo yes )
    [ "$ok" = yes ] && break
    sleep $((30 + RANDOM % 60))
done
[ "${ok:-}" = yes ] && note "results/$RD is on the branch" || note "GUARD: results/$RD could not be pushed after 30 tries"
note "done"
publish "done"
