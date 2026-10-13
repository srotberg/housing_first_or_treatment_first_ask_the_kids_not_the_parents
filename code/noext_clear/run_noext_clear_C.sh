#!/bin/bash
# run_noext_clear_C.sh -- RULE C (12 October) copy of run_noext_clear.sh: Treatment First without the externalities,
# the drug price and pi_V both clearing (Arm C), against Housing First without them (Arm A), on the rule-C build
# cf_fix2_treatC (treat/patch_treatC.py: a household with the disorder must be in treatment, nobody may use).
#   Arm A  cfarm_null_pe_noext_C   Housing First without the externalities, as in run_noext_clear.sh; shared with the
#                                  other two rule-C launchers (noext_C_lib.sh)
#   Arm C  cfarm_tf_noext_clear_C  Treatment First as tf85_c35 (detection 0.85, the $35 test, the three-year exclusion)
#                                  with the switches, on cf_fix2_treatC: the drug price clearing and pi_V clearing the
#                                  budget against Arm A's net revenue, rule A's NET_A as before. WARM START at rule A's
#                                  Arm C (results/noext_clear/arm_C/final.txt): price 0.90717489, pi_V 0.076132869.
#   Then the walk on Arm A's policies (shared with run_noext_fixp_C.sh: the same grid) and pe_noext/analyse.py A vs C.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/noext_clear/run_noext_clear_C.sh
# Re-running attaches; a finished step is not repeated. Publishes results/noext_clear_C/status.txt every 20 minutes.
set -u
TAG=noext_clear_C; STATUS=nc.status
HEADER="Treatment First without externalities, savings recycled, RULE C (code/noext_clear/run_noext_clear_C.sh)"
_C=$(cd "$(dirname "$0")/.." && pwd)
W=$_C/noext_clear/work_clear_C; R=$(cd "$_C/.." && pwd)/results/noext_clear_C
ARMS_SHOWN="cfarm_null_pe_noext_C cfarm_tf_noext_clear_C"
. "$_C/noext_clear/noext_C_lib.sh"
P_C0=0.90717489; V_C0=0.076132869  # rule A's Arm C, its last pass
XS="-0.5 -0.3 -0.2 -0.15 -0.1 -0.07 -0.05 -0.03 -0.02 -0.01 -0.005 -0.002 -0.0005 0.0 0.0005 0.002 0.005 0.01 0.02 0.05 0.1 0.15 0.2 0.3"
detach "$0"

note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc), threads per solve $THREADS, at most $MAXSOLVES solves"
build_all
publish "built"
cd "$C"
start_arm_A
if ! arm_ok cfarm_tf_noext_clear_C target; then
    note "arm C (tf_noext_clear_C) on cf_fix2_treatC: detection 0.85, test $CTEST, price and pi_V clearing against $NET_A, from rule A's price $P_C0, pi_V $V_C0"
    start_gated "$W/arm_C.pid" "$C/cfarm_tf_noext_clear_C.out" env BUILD=cf_fix2_treatC OMP_NUM_THREADS=$THREADS DIAG_TAG=_noext_clear_C \
        SEED_FROM=bench PDET=${RULEC_PDET:-0.20} NET_TARGET=$NET_A PV_START=$V_C0 DRUG_PRICE_START=$P_C0 \
        EXTRA_SET="cost_per_drug_test $CTEST;$SWITCHES" sh "$C/pe_noext/cf_arm_pe_noext_C.sh" tf
fi
wait_publishing "arms running" "$SH/arm_A.pid" "$W/arm_C.pid"
wait_arm_A
arm_ok cfarm_tf_noext_clear_C target && note "cfarm_tf_noext_clear_C: $(grep -a 'CHECK PASS' "$C/cfarm_tf_noext_clear_C.out" | tr '\n' ' ')" \
    || { note "GUARD: cfarm_tf_noext_clear_C failed: $(grep -a 'GUARD' "$C/cfarm_tf_noext_clear_C.out" | head -n 3 | tr '\n' ' ')"; publish "arm C failed"; exit 1; }
save_arm A $A_DIR; save_arm C cfarm_tf_noext_clear_C
note "arm A's net revenue $(grep 'net government revenue' "$R/arm_A/final.txt" | awk '{print $4}') (target used for C: $NET_A)"
publish "arms done"
run_walk pe_walk_A_C "$XS"
python3 pe_noext/analyse.py $A_DIR cfarm_tf_noext_clear_C pe_walk_A_C --json "$R/analysis.json" > "$R/analysis.txt" 2>&1 \
    && note "analysis written: $(grep -i 'newborn adult (age 26)' "$R/analysis.txt" | head -n 1 | tr -s ' ')" \
    || note "GUARD: analysis failed: $(tail -n 3 "$R/analysis.txt" | tr '\n' ' ')"
gzip -c "$C/pe_walk_A_C/walk.log" > "$R/walk_A.log.gz" 2>/dev/null
note "done"
publish "done"
