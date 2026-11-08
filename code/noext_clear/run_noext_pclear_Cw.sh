#!/bin/bash
# run_noext_pclear_Cw.sh -- (8 November) run_noext_pclear_Cu.sh AT THE FIRST EXPERIMENT'S OWN DETECTION RATE, RULEC_PDET,
# which pe_noext/run_noext_pdet.sh chooses (the author: "can you rechoose p_det for the no externalities simulations to
# get the same drug use reaction?") and exports before launching this. A COPY: its run, its arm and its results get
# the suffix _Cw instead of _Cu, so the paper's _Cu columns stay where they are until the export is switched. Arm A
# (cfarm_null_pe_noext_Cu), the walk (pe_walk_A_Cu), the library and the arm script are the _Cu ones, shared.
# GUARD if RULEC_PDET is unset. run_noext_pclear_Cu.sh's header follows.
# run_noext_pclear_Cu.sh -- (14 October) run_noext_pclear_C.sh against the CORRECTED Housing First (noext_Cu_lib.sh: Arm A
# on cf_fix2_share_pe_treatCu, the internal_computations fix ungated). Arm E needs nothing from Arm A to run (pi_V is held
# at Housing First's, which no null arm moves; the budget is not cleared), so it starts beside Arm A as before, from the
# gated Arm E's accepted price (results/noext_pclear_C/arm_E/final.txt); only its comparison is against the new Arm A.
# Results: results/noext_pclear_Cw.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/noext_clear/run_noext_pclear_Cu.sh
# run_noext_pclear_C.sh's header follows.
# run_noext_pclear_C.sh -- RULE C: TREATMENT FIRST WITHOUT THE EXTERNALITIES, THE DRUG PRICE CLEARING AND pi_V HELD
# (14 October; the author: "Sure add the price clears only runs", for the long-run table's no-externality block, which
# now has both held, pi_V clearing and both clearing). run_noext_pclear.sh (rule A, 9 October) on the rule-C build, through
# noext_C_lib.sh as run_noext_clear_C2.sh:
#   Arm A  cfarm_null_pe_noext_C     Housing First without the externalities, re-solved in this container (shared lib).
#   Arm E  cfarm_tf_noext_pclear_Cw   Treatment First on cf_fix2_treatC, detection RULEC_PDET (0.20), the $35 test, the
#                                    switches; the drug price CLEARING from NOEXT_P0 (default 0.985, near Arm C's 0.9849),
#                                    pi_V HELD at Housing First's 0.067533863, the budget NOT cleared (adjust_taxes 0, no
#                                    NET_TARGET), as the with-externality decomposition's fixpv arm.
#   Then the walk on Arm A's policies and pe_noext/analyse.py A against E. A pi_V check: Arm E must never move it.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/noext_clear/run_noext_pclear_C.sh
# Re-running attaches; a finished step is not repeated. Publishes results/noext_pclear_C/status.txt every 20 minutes.
set -u
case "${RULEC_PDET:-}" in 0.[0-9]*) ;; *) echo "GUARD: RULEC_PDET (the detection rate, from run_noext_pdet.sh) is unset or not a rate: '${RULEC_PDET:-}'"; exit 1 ;; esac
TAG=noext_pclear_Cw; STATUS=npc.status
HEADER="Treatment First without externalities, price clearing, pi_V held, RULE C, corrected Housing First, at detection $RULEC_PDET (code/noext_clear/run_noext_pclear_Cw.sh)"
_C=$(cd "$(dirname "$0")/.." && pwd)
W=$_C/noext_clear/work_pclear_Cw; R=$(cd "$_C/.." && pwd)/results/noext_pclear_Cw
ARMS_SHOWN="cfarm_null_pe_noext_Cu cfarm_tf_noext_pclear_Cw"
. "$_C/noext_clear/noext_Cu_lib.sh"
P_E0=${NOEXT_P0:-$(awk '/^  drug price /{print $NF}' "$(cd "$_C/.." && pwd)/results/noext_pclear_C/arm_E/final.txt")}   # the gated Arm E's price
V_NULL=0.067533863                 # Housing First's pi_V (results/noext_clear_C2/arm_A), held in Arm E
XS="-0.5 -0.3 -0.2 -0.15 -0.1 -0.07 -0.05 -0.03 -0.02 -0.01 -0.005 -0.002 -0.0005 0.0 0.0005 0.002 0.005 0.01 0.02 0.05 0.1 0.15 0.2 0.3"
detach "$0"

note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc), threads per solve $THREADS, at most $MAXSOLVES solves"
build_all
publish "built"
cd "$C"
start_arm_A
python3 -c "float('$P_E0')" || { note "GUARD: no warm start ('$P_E0')"; publish "arm E inputs missing"; exit 1; }
if ! arm_ok cfarm_tf_noext_pclear_Cw; then
    note "arm E (tf_noext_pclear_Cw) on cf_fix2_treatC: detection $RULEC_PDET, test $CTEST, price clearing from $P_E0, pi_V held at $V_NULL (adjust_taxes 0)"
    start_gated "$W/arm_E.pid" "$C/cfarm_tf_noext_pclear_Cw.out" env BUILD=cf_fix2_treatC OMP_NUM_THREADS=$THREADS DIAG_TAG=_noext_pclear_Cw \
        SEED_FROM=bench PDET=$RULEC_PDET PV_START=$V_NULL DRUG_PRICE_START=$P_E0 \
        EXTRA_SET="cost_per_drug_test $CTEST;adjust_taxes 0;$SWITCHES" sh "$C/pe_noext/cf_arm_pe_noext_Cu.sh" tf
fi
wait_publishing "arms running" "$SH/arm_A.pid" "$W/arm_E.pid"
wait_arm_A
arm_ok cfarm_tf_noext_pclear_Cw && note "cfarm_tf_noext_pclear_Cw: $(grep -a 'CHECK PASS' "$C/cfarm_tf_noext_pclear_Cw.out" | tr '\n' ' ')" \
    || { note "GUARD: cfarm_tf_noext_pclear_Cw failed: $(grep -a 'GUARD' "$C/cfarm_tf_noext_pclear_Cw.out" | head -n 3 | tr '\n' ' ')"; publish "arm E failed"; exit 1; }
# THE CHECK THAT MATTERS: pi_V never moved in Arm E (the budget was not cleared)
PVS=$(grep -a "^ *probability_of_voucher=" "$C/cfarm_tf_noext_pclear_Cw/cf.log" | awk '{print $2}' | sort -u | tr '\n' ' ')
python3 -c "import sys; v=[float(x) for x in '$PVS'.split()]; sys.exit(0 if v and all(abs(x-$V_NULL)<=1e-8 for x in v) else 1)" \
    && note "PI_V CHECK PASS: arm E ran at pi_V $PVS" || { note "GUARD: arm E's pi_V moved: $PVS"; publish "pi_V moved"; exit 1; }
save_arm A $A_DIR; save_arm E cfarm_tf_noext_pclear_Cw
note "arm A's net revenue $(grep 'net government revenue' "$R/arm_A/final.txt" | awk '{print $4}'), arm E's $(grep 'net government revenue' "$R/arm_E/final.txt" | awk '{print $4}') (not cleared)"
publish "arms done"
run_walk pe_walk_A_Cu "$XS"
python3 pe_noext/analyse.py $A_DIR cfarm_tf_noext_pclear_Cw pe_walk_A_Cu --json "$R/analysis.json" > "$R/analysis.txt" 2>&1 \
    && note "analysis written: $(grep -i 'newborn adult (age 26)' "$R/analysis.txt" | head -n 1 | tr -s ' ')" \
    || note "GUARD: analysis failed: $(tail -n 3 "$R/analysis.txt" | tr '\n' ' ')"
gzip -c "$C/pe_walk_A_Cu/walk.log" > "$R/walk_A.log.gz" 2>/dev/null
clean_arm cfarm_tf_noext_pclear_Cw E
note "done"
publish "done"
