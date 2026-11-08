#!/bin/bash
# run_noext_fixp_Cw.sh -- (8 November) run_noext_fixp_Cu.sh AT THE FIRST EXPERIMENT'S OWN DETECTION RATE, RULEC_PDET,
# which pe_noext/run_noext_pdet.sh chooses (the author: "can you rechoose p_det for the no externalities simulations to
# get the same drug use reaction?") and exports before launching this. A COPY: its run, its arm and its results get
# the suffix _Cw instead of _Cu, so the paper's _Cu columns stay where they are until the export is switched. Arm A
# (cfarm_null_pe_noext_Cu), the walk (pe_walk_A_Cu), the library and the arm script are the _Cu ones, shared.
# GUARD if RULEC_PDET is unset. run_noext_fixp_Cu.sh's header follows.
# run_noext_fixp_Cu.sh -- (14 October) run_noext_fixp_C.sh against the CORRECTED Housing First (noext_Cu_lib.sh: Arm A
# on cf_fix2_share_pe_treatCu, the internal_computations fix ungated). Differences: Arm D waits for the corrected Arm A,
# its drug price is HELD at that Arm A's last PE USED price (not rule A's 1.0305058), pi_V clears against that Arm A's
# own final net revenue (NET_A, read, not hard-coded), and pi_V is warm-started at the gated Arm D's accepted value
# (results/noext_fixp_C/arm_D/final.txt). Results: results/noext_fixp_Cw.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/noext_clear/run_noext_fixp_Cu.sh
# run_noext_fixp_C.sh's header follows.
# run_noext_fixp_C.sh -- RULE C (12 October) copy of run_noext_fixp.sh: Treatment First without the externalities, the
# drug price HELD at Arm A's, pi_V clearing the budget against Arm A's net revenue (Arm D), on the rule-C build
# cf_fix2_treatC (treat/patch_treatC.py: a household with the disorder must be in treatment, nobody may use).
#   Arm A  cfarm_null_pe_noext_C  Housing First without the externalities; shared (noext_C_lib.sh)
#   Arm D  cfarm_tf_noext_fixp_Cw  tf85_c35 with the switches on cf_fix2_treatC, drug_market_adjuster 0 at P_A0 (rule A's
#                                 value, checked against the re-solved Arm A to 1e-3 as before), pi_V clearing against
#                                 NET_A. WARM START at rule A's Arm D (results/noext_fixp/arm_D/final.txt): pi_V 0.068872515.
#   Then the walk on Arm A's policies (shared with run_noext_clear_C.sh) and pe_noext/analyse.py A against D.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/noext_clear/run_noext_fixp_C.sh
# Re-running attaches; a finished step is not repeated. Publishes results/noext_fixp_C/status.txt every 20 minutes.
set -u
case "${RULEC_PDET:-}" in 0.[0-9]*) ;; *) echo "GUARD: RULEC_PDET (the detection rate, from run_noext_pdet.sh) is unset or not a rate: '${RULEC_PDET:-}'"; exit 1 ;; esac
TAG=noext_fixp_Cw; STATUS=nc.status
HEADER="Treatment First without externalities, drug price held, budget rebalanced, RULE C, corrected Housing First, at detection $RULEC_PDET (code/noext_clear/run_noext_fixp_Cw.sh)"
_C=$(cd "$(dirname "$0")/.." && pwd)
# (8 November) the columns run in their own sessions (pe_noext/run_noext_col.sh): when results/noext_pdet/columns_elsewhere
# is in the checkout, a launch from run_noext_pdet.sh does nothing; run_noext_col.sh sets NOEXT_COLS_HERE=1
if [ -f "$_C/../results/noext_pdet/columns_elsewhere" ] && [ "${NOEXT_COLS_HERE:-0}" != 1 ]; then
    echo "$(basename "$0"): the columns run in their own sessions (results/noext_pdet/columns_elsewhere): nothing to do here"; exit 0
fi
W=$_C/noext_clear/work_fixp_Cw; R=$(cd "$_C/.." && pwd)/results/noext_fixp_Cw
ARMS_SHOWN="cfarm_null_pe_noext_Cu cfarm_tf_noext_fixp_Cw"
. "$_C/noext_clear/noext_Cu_lib.sh"
V_D0=${CU_V0:-$(awk '/^  pi_V /{print $NF}' "$(cd "$_C/.." && pwd)/results/noext_fixp_C/arm_D/final.txt")}   # the gated Arm D's pi_V
XS="-0.5 -0.3 -0.2 -0.15 -0.1 -0.07 -0.05 -0.03 -0.02 -0.01 -0.005 -0.002 -0.0005 0.0 0.0005 0.002 0.005 0.01 0.02 0.05 0.1 0.15 0.2 0.3"
detach "$0"

note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc), threads per solve $THREADS, at most $MAXSOLVES solves"
build_all
publish "built"
cd "$C"
start_arm_A
wait_arm_A
set_net_A
P_A0=$(grep -a "PE USED" "$C/$A_DIR/cf.log" | tail -n 1 | awk '{for(i=1;i<=NF;i++) if($i=="drug_price=") print $(i+1)}')
python3 -c "float('$P_A0'); float('$V_D0')" || { note "GUARD: no PE USED price in arm A's log or no warm start ('$P_A0', '$V_D0')"; publish "arm D inputs missing"; exit 1; }
if ! arm_ok cfarm_tf_noext_fixp_Cw target; then
    note "arm D (tf_noext_fixp_Cw) on cf_fix2_treatC: detection $RULEC_PDET, test $CTEST, drug price held at $P_A0, pi_V clearing against $NET_A from $V_D0 (CU_V0 or the gated arm D's)"
    start_gated "$W/arm_D.pid" "$C/cfarm_tf_noext_fixp_Cw.out" env BUILD=cf_fix2_treatC OMP_NUM_THREADS=$THREADS DIAG_TAG=_noext_fixp_Cw \
        SEED_FROM=bench PDET=$RULEC_PDET NET_TARGET=$NET_A PV_START=$V_D0 DRUG_PRICE_START=$P_A0 DRUG_MARKET_ADJUSTER=0 \
        EXTRA_SET="cost_per_drug_test $CTEST;$SWITCHES" sh "$C/pe_noext/cf_arm_pe_noext_Cu.sh" tf
fi
wait_publishing "arm D running" "$W/arm_D.pid"
arm_ok cfarm_tf_noext_fixp_Cw target && note "cfarm_tf_noext_fixp_Cw: $(grep -a 'CHECK PASS' "$C/cfarm_tf_noext_fixp_Cw.out" | tr '\n' ' ')" \
    || { note "GUARD: cfarm_tf_noext_fixp_Cw failed: $(grep -a 'GUARD' "$C/cfarm_tf_noext_fixp_Cw.out" | head -n 3 | tr '\n' ' ')"; publish "arm D failed"; exit 1; }
save_arm A $A_DIR; save_arm D cfarm_tf_noext_fixp_Cw
note "arm A's net revenue $(grep 'net government revenue' "$R/arm_A/final.txt" | awk '{print $4}') (target used for D: $NET_A)"
P_AS=$(grep -a "PE USED" "$C/$A_DIR/cf.log" | tail -n 1 | awk '{for(i=1;i<=NF;i++) if($i=="drug_price=") print $(i+1)}')
python3 -c "import sys; sys.exit(0 if abs(float('$P_AS')-$P_A0)<1e-3 else 1)" && note "price check: arm A clears at $P_AS, arm D held at $P_A0" \
    || note "GUARD: arm A clears at $P_AS, not the $P_A0 arm D was held at"
publish "arms done"
run_walk pe_walk_A_Cu "$XS"
python3 pe_noext/analyse.py $A_DIR cfarm_tf_noext_fixp_Cw pe_walk_A_Cu --json "$R/analysis.json" > "$R/analysis.txt" 2>&1 \
    && note "analysis written: $(grep -i 'newborn adult (age 26)' "$R/analysis.txt" | head -n 1 | tr -s ' ')" \
    || note "GUARD: analysis failed: $(tail -n 3 "$R/analysis.txt" | tr '\n' ' ')"
gzip -c "$C/pe_walk_A_Cu/walk.log" > "$R/walk_A.log.gz" 2>/dev/null
clean_arm cfarm_tf_noext_fixp_Cw D
note "done"
publish "done"
