#!/bin/bash
# run_noext_clear_Cw.sh -- (8 November) run_noext_clear_Cu.sh AT THE FIRST EXPERIMENT'S OWN DETECTION RATE, RULEC_PDET,
# which pe_noext/run_noext_pdet.sh chooses (the author: "can you rechoose p_det for the no externalities simulations to
# get the same drug use reaction?") and exports before launching this. A COPY: its run, its arm and its results get
# the suffix _Cw instead of _Cu, so the paper's _Cu columns stay where they are until the export is switched. Arm A
# (cfarm_null_pe_noext_Cu), the walk (pe_walk_A_Cu), the library and the arm script are the _Cu ones, shared.
# GUARD if RULEC_PDET is unset. run_noext_clear_Cu.sh's header follows.
# run_noext_clear_Cu.sh -- (14 October) run_noext_clear_C2.sh against the CORRECTED Housing First (noext_Cu_lib.sh: Arm A
# on cf_fix2_share_pe_treatCu, the internal_computations fix ungated). Differences: Arm C waits for the corrected Arm A,
# clears pi_V against that Arm A's own final net revenue (NET_A, read, not hard-coded), and starts at the gated Arm C's
# accepted price and pi_V (results/noext_clear_C2/arm_C/final.txt). Results: results/noext_clear_Cw.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/noext_clear/run_noext_clear_Cu.sh
# run_noext_clear_C2.sh's header follows.
# run_noext_clear_C2.sh -- run_noext_clear_C.sh from a NEARER START (13 October 19:45; the author: "are you now relaunching
# the long run with better price guess?"). The 16:58 launch started Arm C at rule A's price 0.907, which at detection 0.20
# is far below where the no-externality market clears: after four passes it sat at 0.926 with a 32% drug gap, walking up
# 0.5% a pass (max_drug_price_move). Arm A clears at 1.031; with the paper's economy's demand slope at 0.20 (about -6.4 in
# the log gap per log price, from its 0.868 and 1.00 points) the gap at 0.926 closes near 0.97. So Arm C starts at
# NOEXT_P0 (default 0.97) and NOEXT_V0 (default 0.071, the budget already clears there). Run in a FRESH container: Arm A
# is re-solved there (identical inputs), Arm C runs beside it, and the original container keeps its two slots for
# Arms B and D. Everything else is run_noext_clear_C.sh's; its header follows.
# run_noext_clear_C.sh -- RULE C (12 October) copy of run_noext_clear.sh: Treatment First without the externalities,
# the drug price and pi_V both clearing (Arm C), against Housing First without them (Arm A), on the rule-C build
# cf_fix2_treatC (treat/patch_treatC.py: a household with the disorder must be in treatment, nobody may use).
#   Arm A  cfarm_null_pe_noext_C   Housing First without the externalities, as in run_noext_clear.sh; shared with the
#                                  other two rule-C launchers (noext_C_lib.sh)
#   Arm C  cfarm_tf_noext_clear_Cw  Treatment First as tf85_c35 (detection $RULEC_PDET, the $35 test, the three-year exclusion)
#                                  with the switches, on cf_fix2_treatC: the drug price clearing and pi_V clearing the
#                                  budget against Arm A's net revenue, rule A's NET_A as before. WARM START at rule A's
#                                  Arm C (results/noext_clear/arm_C/final.txt): price 0.90717489, pi_V 0.076132869.
#   Then the walk on Arm A's policies (shared with run_noext_fixp_C.sh: the same grid) and pe_noext/analyse.py A vs C.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/noext_clear/run_noext_clear_C.sh
# Re-running attaches; a finished step is not repeated. Publishes results/noext_clear_C/status.txt every 20 minutes.
set -u
case "${RULEC_PDET:-}" in 0.[0-9]*) ;; *) echo "GUARD: RULEC_PDET (the detection rate, from run_noext_pdet.sh) is unset or not a rate: '${RULEC_PDET:-}'"; exit 1 ;; esac
TAG=noext_clear_Cw; STATUS=nc.status
HEADER="Treatment First without externalities, savings recycled, RULE C, corrected Housing First, at detection $RULEC_PDET (code/noext_clear/run_noext_clear_Cw.sh)"
_C=$(cd "$(dirname "$0")/.." && pwd)
W=$_C/noext_clear/work_clear_Cw; R=$(cd "$_C/.." && pwd)/results/noext_clear_Cw
ARMS_SHOWN="cfarm_null_pe_noext_Cu cfarm_tf_noext_clear_Cw"
. "$_C/noext_clear/noext_Cu_lib.sh"
_F=$(cd "$_C/.." && pwd)/results/noext_clear_C2/arm_C/final.txt   # the gated Arm C, accepted
P_C0=${NOEXT_P0:-$(awk '/^  drug price /{print $NF}' "$_F")}; V_C0=${NOEXT_V0:-$(awk '/^  pi_V /{print $NF}' "$_F")}
XS="-0.5 -0.3 -0.2 -0.15 -0.1 -0.07 -0.05 -0.03 -0.02 -0.01 -0.005 -0.002 -0.0005 0.0 0.0005 0.002 0.005 0.01 0.02 0.05 0.1 0.15 0.2 0.3"
detach "$0"

note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc), threads per solve $THREADS, at most $MAXSOLVES solves"
build_all
publish "built"
cd "$C"
start_arm_A
wait_arm_A
set_net_A
python3 -c "float('$P_C0'); float('$V_C0')" || { note "GUARD: no warm start ('$P_C0', '$V_C0')"; publish "arm C inputs missing"; exit 1; }
if ! arm_ok cfarm_tf_noext_clear_Cw target; then
    note "arm C (tf_noext_clear_Cw) on cf_fix2_treatC: detection $RULEC_PDET, test $CTEST, price and pi_V clearing against $NET_A, from price $P_C0, pi_V $V_C0 (warm start NOEXT_P0, NOEXT_V0 or the gated arm C's)"
    start_gated "$W/arm_C.pid" "$C/cfarm_tf_noext_clear_Cw.out" env BUILD=cf_fix2_treatC OMP_NUM_THREADS=$THREADS DIAG_TAG=_noext_clear_Cw \
        SEED_FROM=bench PDET=$RULEC_PDET NET_TARGET=$NET_A PV_START=$V_C0 DRUG_PRICE_START=$P_C0 \
        EXTRA_SET="cost_per_drug_test $CTEST;$SWITCHES" sh "$C/pe_noext/cf_arm_pe_noext_Cu.sh" tf
fi
wait_publishing "arm C running" "$W/arm_C.pid"
arm_ok cfarm_tf_noext_clear_Cw target && note "cfarm_tf_noext_clear_Cw: $(grep -a 'CHECK PASS' "$C/cfarm_tf_noext_clear_Cw.out" | tr '\n' ' ')" \
    || { note "GUARD: cfarm_tf_noext_clear_Cw failed: $(grep -a 'GUARD' "$C/cfarm_tf_noext_clear_Cw.out" | head -n 3 | tr '\n' ' ')"; publish "arm C failed"; exit 1; }
save_arm A $A_DIR; save_arm C cfarm_tf_noext_clear_Cw
note "arm A's net revenue $(grep 'net government revenue' "$R/arm_A/final.txt" | awk '{print $4}') (target used for C: $NET_A)"
publish "arms done"
run_walk pe_walk_A_Cu "$XS"
python3 pe_noext/analyse.py $A_DIR cfarm_tf_noext_clear_Cw pe_walk_A_Cu --json "$R/analysis.json" > "$R/analysis.txt" 2>&1 \
    && note "analysis written: $(grep -i 'newborn adult (age 26)' "$R/analysis.txt" | head -n 1 | tr -s ' ')" \
    || note "GUARD: analysis failed: $(tail -n 3 "$R/analysis.txt" | tr '\n' ' ')"
gzip -c "$C/pe_walk_A_Cu/walk.log" > "$R/walk_A.log.gz" 2>/dev/null
clean_arm cfarm_tf_noext_clear_Cw C
note "done"
publish "done"
