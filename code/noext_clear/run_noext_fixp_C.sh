#!/bin/bash
# run_noext_fixp_C.sh -- RULE C (12 October) copy of run_noext_fixp.sh: Treatment First without the externalities, the
# drug price HELD at Arm A's, pi_V clearing the budget against Arm A's net revenue (Arm D), on the rule-C build
# cf_fix2_treatC (treat/patch_treatC.py: a household with the disorder must be in treatment, nobody may use).
#   Arm A  cfarm_null_pe_noext_C  Housing First without the externalities; shared (noext_C_lib.sh)
#   Arm D  cfarm_tf_noext_fixp_C  tf85_c35 with the switches on cf_fix2_treatC, drug_market_adjuster 0 at P_A0 (rule A's
#                                 value, checked against the re-solved Arm A to 1e-3 as before), pi_V clearing against
#                                 NET_A. WARM START at rule A's Arm D (results/noext_fixp/arm_D/final.txt): pi_V 0.068872515.
#   Then the walk on Arm A's policies (shared with run_noext_clear_C.sh) and pe_noext/analyse.py A against D.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/noext_clear/run_noext_fixp_C.sh
# Re-running attaches; a finished step is not repeated. Publishes results/noext_fixp_C/status.txt every 20 minutes.
set -u
TAG=noext_fixp_C; STATUS=nc.status
HEADER="Treatment First without externalities, drug price held, budget rebalanced, RULE C (code/noext_clear/run_noext_fixp_C.sh)"
_C=$(cd "$(dirname "$0")/.." && pwd)
W=$_C/noext_clear/work_fixp_C; R=$(cd "$_C/.." && pwd)/results/noext_fixp_C
ARMS_SHOWN="cfarm_null_pe_noext_C cfarm_tf_noext_fixp_C"
. "$_C/noext_clear/noext_C_lib.sh"
P_A0=1.0305057924439740            # Arm A's drug price, as in run_noext_fixp.sh; checked below
V_D0=0.068872515                   # rule A's Arm D, its last pass
XS="-0.5 -0.3 -0.2 -0.15 -0.1 -0.07 -0.05 -0.03 -0.02 -0.01 -0.005 -0.002 -0.0005 0.0 0.0005 0.002 0.005 0.01 0.02 0.05 0.1 0.15 0.2 0.3"
detach "$0"

note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc), threads per solve $THREADS, at most $MAXSOLVES solves"
build_all
publish "built"
cd "$C"
start_arm_A
if ! arm_ok cfarm_tf_noext_fixp_C target; then
    note "arm D (tf_noext_fixp_C) on cf_fix2_treatC: detection 0.85, test $CTEST, drug price held at $P_A0, pi_V clearing against $NET_A from rule A's $V_D0"
    start_gated "$W/arm_D.pid" "$C/cfarm_tf_noext_fixp_C.out" env BUILD=cf_fix2_treatC OMP_NUM_THREADS=$THREADS DIAG_TAG=_noext_fixp_C \
        SEED_FROM=bench PDET=0.85 NET_TARGET=$NET_A PV_START=$V_D0 DRUG_PRICE_START=$P_A0 DRUG_MARKET_ADJUSTER=0 \
        EXTRA_SET="cost_per_drug_test $CTEST;$SWITCHES" sh "$C/pe_noext/cf_arm_pe_noext_C.sh" tf
fi
wait_publishing "arms running" "$SH/arm_A.pid" "$W/arm_D.pid"
wait_arm_A
arm_ok cfarm_tf_noext_fixp_C target && note "cfarm_tf_noext_fixp_C: $(grep -a 'CHECK PASS' "$C/cfarm_tf_noext_fixp_C.out" | tr '\n' ' ')" \
    || { note "GUARD: cfarm_tf_noext_fixp_C failed: $(grep -a 'GUARD' "$C/cfarm_tf_noext_fixp_C.out" | head -n 3 | tr '\n' ' ')"; publish "arm D failed"; exit 1; }
save_arm A $A_DIR; save_arm D cfarm_tf_noext_fixp_C
note "arm A's net revenue $(grep 'net government revenue' "$R/arm_A/final.txt" | awk '{print $4}') (target used for D: $NET_A)"
P_AS=$(grep -a "PE USED" "$C/$A_DIR/cf.log" | tail -n 1 | awk '{for(i=1;i<=NF;i++) if($i=="drug_price=") print $(i+1)}')
python3 -c "import sys; sys.exit(0 if abs(float('$P_AS')-$P_A0)<1e-3 else 1)" && note "price check: arm A clears at $P_AS, arm D held at $P_A0" \
    || note "GUARD: arm A clears at $P_AS, not the $P_A0 arm D was held at"
publish "arms done"
run_walk pe_walk_A_C "$XS"
python3 pe_noext/analyse.py $A_DIR cfarm_tf_noext_fixp_C pe_walk_A_C --json "$R/analysis.json" > "$R/analysis.txt" 2>&1 \
    && note "analysis written: $(grep -i 'newborn adult (age 26)' "$R/analysis.txt" | head -n 1 | tr -s ' ')" \
    || note "GUARD: analysis failed: $(tail -n 3 "$R/analysis.txt" | tr '\n' ' ')"
gzip -c "$C/pe_walk_A_C/walk.log" > "$R/walk_A.log.gz" 2>/dev/null
note "done"
publish "done"
