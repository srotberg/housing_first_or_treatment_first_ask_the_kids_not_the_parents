#!/bin/bash
# run_pe_Cw.sh -- (8 November) run_pe_Cu.sh AT THE FIRST EXPERIMENT'S OWN DETECTION RATE, RULEC_PDET,
# which pe_noext/run_noext_pdet.sh chooses (the author: "can you rechoose p_det for the no externalities simulations to
# get the same drug use reaction?") and exports before launching this. A COPY: its run, its arm and its results get
# the suffix _Cw instead of _Cu, so the paper's _Cu columns stay where they are until the export is switched. Arm A
# (cfarm_null_pe_noext_Cu), the walk (pe_walk_A_Cu), the library and the arm script are the _Cu ones, shared.
# GUARD if RULEC_PDET is unset. run_pe_Cu.sh's header follows.
# run_pe_Cu.sh -- (14 October) run_pe_C.sh against the CORRECTED Housing First (noext_clear/noext_Cu_lib.sh: Arm A on
# cf_fix2_share_pe_treatCu, the internal_computations fix ungated). Arm B is unchanged in kind: Treatment First with the
# drug price, pi_V and the house price HELD at the corrected Arm A's last PE USED values, seeded from it. Nothing to warm-
# start (Arm B's prices are Arm A's; the gated Arm B held 1.0304909 / 0.067533863). Results: results/pe_noext_Cw.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/pe_noext/run_pe_Cu.sh
# run_pe_C.sh's header follows.
# run_pe_C.sh -- RULE C (12 October) copy of run_pe.sh + run_walk.sh: the partial-equilibrium, no-externality experiment
# on the rule-C build. Arm B is Treatment First (tf85_c35: detection $RULEC_PDET, the $35 test, the three-year exclusion, no
# false positives) with the switches, on cf_fix2_pe_treatC (pe_noext/build_pe_C.sh: cf_fix2_pe + treat/patch_treatC.py,
# a household with the disorder must be in treatment, nobody may use), with the drug price, pi_V and the house price
# HELD at the values Arm A's LAST solve used (its last PE USED line), adjust_taxes 0, seeded from Arm A's distribution.
# Arm A (cfarm_null_pe_noext_C) is Housing First, unchanged by the rule, shared with the other two rule-C launchers
# (noext_clear/noext_C_lib.sh). Nothing to warm-start: Arm B's prices are Arm A's. Then the walk on Arm A's policies and
# pe_noext/analyse.py A against B. THE WALK IS SHARED with the other two launchers (pe_walk_A_C, their grid, which is
# run_walk.sh's plus x = 0.15, 0.2, 0.3): the disk holds the benchmark, Arm A and three Treatment First arms, about 4 GB
# each, and has no room for a second copy of Arm A. The extra points only put more of the grid under any gain above 10%.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/pe_noext/run_pe_C.sh
# Re-running attaches; a finished step is not repeated. Publishes results/pe_noext_C/status.txt every 20 minutes.
set -u
case "${RULEC_PDET:-}" in 0.[0-9]*) ;; *) echo "GUARD: RULEC_PDET (the detection rate, from run_noext_pdet.sh) is unset or not a rate: '${RULEC_PDET:-}'"; exit 1 ;; esac
TAG=pe_noext_Cw; STATUS=pe.status
HEADER="PE experiment without externalities, RULE C, corrected Housing First, at detection $RULEC_PDET (code/pe_noext/run_pe_Cw.sh)"
_C=$(cd "$(dirname "$0")/.." && pwd)
# (8 November) the columns run in their own sessions (pe_noext/run_noext_col.sh): when results/noext_pdet/columns_elsewhere
# is in the checkout, a launch from run_noext_pdet.sh does nothing; run_noext_col.sh sets NOEXT_COLS_HERE=1
if [ -f "$_C/../results/noext_pdet/columns_elsewhere" ] && [ "${NOEXT_COLS_HERE:-0}" != 1 ]; then
    echo "$(basename "$0"): the columns run in their own sessions (results/noext_pdet/columns_elsewhere): nothing to do here"; exit 0
fi
W=$_C/pe_noext/work_Cw; R=$(cd "$_C/.." && pwd)/results/pe_noext_Cw
ARMS_SHOWN="cfarm_null_pe_noext_Cu cfarm_tf_pe_noext_Cw"
. "$_C/noext_clear/noext_Cu_lib.sh"
XS="-0.5 -0.3 -0.2 -0.15 -0.1 -0.07 -0.05 -0.03 -0.02 -0.01 -0.005 -0.002 -0.0005 0.0 0.0005 0.002 0.005 0.01 0.02 0.05 0.1 0.15 0.2 0.3"
detach "$0"

note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc), threads per solve $THREADS, at most $MAXSOLVES solves"
build_all
publish "built"
cd "$C"
start_arm_A
wait_arm_A
note "arm A: $(grep -a 'CHECK PASS' "$C/$A_DIR.out" | tr '\n' ' ')"
U=$(grep -a "PE USED" "$C/$A_DIR/cf.log" | tail -n 1)
HP_A=$(echo "$U" | awk '{for(i=1;i<=NF;i++) if($i=="housing_price=") print $(i+1)}')
P_A=$(echo "$U" | awk '{for(i=1;i<=NF;i++) if($i=="drug_price=") print $(i+1)}')
PV_A=$(echo "$U" | awk '{for(i=1;i<=NF;i++) if($i=="pi_V=") print $(i+1)}')
python3 -c "import sys; [float(x) for x in sys.argv[1:4]]" "$HP_A" "$P_A" "$PV_A" || { note "GUARD: no PE USED prices in arm A's log"; publish "arm A prices missing"; exit 1; }
note "arm A's last solve used: drug price $P_A, pi_V $PV_A, house price $HP_A"
if ! arm_ok cfarm_tf_pe_noext_Cw; then
    note "arm B (tf_pe_noext_Cw) on cf_fix2_pe_treatC: detection $RULEC_PDET, test $CTEST, held price $P_A, pi_V $PV_A, house price $HP_A, adjust_taxes 0"
    start_gated "$W/arm_B.pid" "$C/cfarm_tf_pe_noext_Cw.out" env BUILD=cf_fix2_pe_treatC OMP_NUM_THREADS=$THREADS DIAG_TAG=_pe_noext_Cw \
        SEED_FROM=$A_DIR PDET=$RULEC_PDET PV_START=$PV_A DRUG_PRICE_START=$P_A DRUG_MARKET_ADJUSTER=0 HOUSING_PRICE_HOLD=$HP_A \
        EXTRA_SET="cost_per_drug_test $CTEST;adjust_taxes 0;$SWITCHES" sh "$C/pe_noext/cf_arm_pe_noext_Cu.sh" tf
fi
wait_publishing "arm B running" "$W/arm_B.pid"
arm_ok cfarm_tf_pe_noext_Cw && note "arm B: $(grep -a 'CHECK PASS' "$C/cfarm_tf_pe_noext_Cw.out" | tr '\n' ' ')" \
    || { note "GUARD: arm B failed: $(grep -a 'GUARD' "$C/cfarm_tf_pe_noext_Cw.out" | head -n 3 | tr '\n' ' ')"; publish "arm B failed"; exit 1; }
save_arm A $A_DIR; save_arm B cfarm_tf_pe_noext_Cw
publish "arms done"
run_walk pe_walk_A_Cu "$XS"
python3 pe_noext/analyse.py $A_DIR cfarm_tf_pe_noext_Cw pe_walk_A_Cu --json "$R/analysis.json" > "$R/analysis.txt" 2>&1 \
    && note "analysis written: $(grep -i 'newborn adult (age 26)' "$R/analysis.txt" | head -n 1 | tr -s ' ')" \
    || note "GUARD: analysis failed: $(tail -n 3 "$R/analysis.txt" | tr '\n' ' ')"
gzip -c "$C/pe_walk_A_Cu/walk.log" > "$R/walk_A.log.gz" 2>/dev/null
clean_arm cfarm_tf_pe_noext_Cw B
note "done"
publish "done"
