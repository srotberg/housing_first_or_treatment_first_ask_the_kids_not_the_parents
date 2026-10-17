#!/bin/bash
# run_arms_CA20.sh -- A COPY of run_arms_CA100.sh at detection 0.20 (17 October; the author: "I want to launch
# both because I want to see if homelessness rises with 20% detection and no escape"): every CA100 name is CA20 and the
# detection default 0.20, so nothing here touches the detection-1.00 results. The original follows.
# run_arms_CA20.sh -- COPY of run_arms_C.sh (16 October) for the Costantini comparison under the CA rule at detection 0.20: Treatment
# First on cf_fix2_treatCA (treat/build_treatCA.sh, rule A's screen on rule C's build) at PDET 1.00, Housing First the
# CORRECTED one (cf_fix2_share_treatCu, internal_computations fix ungated; NET_TARGET 5.8371628), arms
# cfarm_null_2c_CA20 and cfarm_tf_2c_fixboth_CA20, work directories work_CA20, results to results/revoked_2c_CA20
# and results/revoked_2c_street_CA20. Otherwise the original, which follows.
# run_arms_C.sh -- RULE-C COPY of revoked_2c/run_arms.sh (12 October). The no-policy arm is Housing First, which has no
# screen, so it is re-solved exactly as before (cf_fix2_share, cfarm_null_2c). The Treatment First arm runs on
# cf_fix2_treatC (treat/build_treatC.sh) through treat/cf_arm_C.sh, into cfarm_tf_2c_fixboth_C. It holds the drug price
# and pi_V at the no-policy values, so there is no price or pi_V to warm-start; the distribution starts from the
# benchmark's, as before. Work directory revoked_2c/work_C. Waits for code/cfarm_bench/BENCH_DONE when another
# launcher in this container (deter_2c/run_whostops_C.sh) is unpacking the shared benchmark. The header follows.
# run_arms.sh -- STAGE 1 of the revoked-voucher experiment (code/revoked_2c/README.md): re-solve the two
# steady states the short-run path needs, because the containers that held them are gone.
#
#   null     the no-policy (Housing First) arm on cf_fix2_share, exactly as remote_transition_2c.sh ran it
#            ('arm null cf_fix2_share DRUG_PRICE_START=$P_NULL'); it also writes newborn_parent_share_counter.dat,
#            the path's t = 0 parent share. -> code/cfarm_null_2c
#   fixboth  Treatment First with pi_V AND the drug price held at the no-policy values, budget not cleared:
#            exactly the arm of extra_2c/remote_decomp_2c_both.sh. The path's terminal state. -> code/cfarm_tf_2c_fixboth
#
# Calls the tracked scripts unchanged. Detached (setsid nohup), so it survives the end of a turn:
#   bash code/revoked_2c/run_arms.sh            (re-running attaches if the worker is alive)
set -u
C=$(cd "$(dirname "$0")/.." && pwd)
W=$C/revoked_2c/work_CA20; mkdir -p "$W"; printf "*\n" > "$W/.gitignore"   # work_C is never committed
REF=$C/../results/reference/hf_2c_omega_0.085
P_NULL=1.0001082; V_NULL=0.067533863
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export SEED_FROM=bench
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"

note() { echo "run_arms: $* ($(date -u '+%d %b %H:%M'))" | tee -a "$W/arms.status"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

if [ "${ARMS_DETACHED:-0}" != 1 ]; then
    if alive "$W/arms.pid"; then echo "attached to pid $(cat "$W/arms.pid")"; else
        ( ARMS_DETACHED=1 setsid nohup bash "$0" > "$W/arms.detached.log" 2>&1 < /dev/null & echo $! > "$W/arms.pid" )
        echo "started detached, pid $(cat "$W/arms.pid")"
    fi
    exit 0
fi

note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"
cd "$C"
if ! [ -x "$C/cf_fix2_treatCA/hftf_cf_prod" ]; then
    note "building cf_fix2_treatCA"
    bash treat/build_treatCA.sh > "$W/build_treatCA.log" 2>&1 || { note "GUARD: build cf_fix2_treatCA failed"; exit 1; }
fi
if [ ! -x "$C/cf_fix2_share_treatCu/hftf_cf_prod" ]; then
    note "building cf_fix2_share_treatCu"
    bash treat/build_share_treatCu.sh > "$W/build_share_treatCu.log" 2>&1 || { note "GUARD: build cf_fix2_share_treatCu failed"; exit 1; }
fi
grep -q "if (drug_market_adjuster==0.d0) distance_drug_market=0" "$C/cf_fix2_treatCA/cf.f90" || { note "GUARD: cf_fix2_treatCA lacks the held-price rule"; exit 1; }
[ "$(grep -c 'RULE CA (patch_treatCA.py)' "$C/cf_fix2_treatCA/cf.f90")" = 1 ] && [ "$(grep -c 'RULE C (patch_treatC.py)' "$C/cf_fix2_treatCA/cf.f90")" = 0 ] \
    && [ "$(grep -c "THE HOUSEHOLD'S OWN TREATMENT CHOICE (patch_treatC.py)" "$C/cf_fix2_treatCA/cf.f90")" = 2 ] \
    && grep -A1 '^ *if (unemployment_index>threshold_addiction_index) fails_1=1$' "$C/cf_fix2_treatCA/cf.f90" | grep -q '^ *if (drug_share_1>0) fails_1=1$' \
    || { note "GUARD: cf_fix2_treatCA lacks the CA screen (the disorder fails in treatment or not; any use fails)"; exit 1; }
grep -q "INTERNAL UNGATED (patch_treatCu.py)" "$C/cf_fix2_share_treatCu/cf.f90" || { note "GUARD: cf_fix2_share_treatCu lacks the ungated fix"; exit 1; }
note "builds done"

# another launcher may be unpacking the shared benchmark: wait for it
while [ -d "$C/cfarm_bench" ] && [ ! -f "$C/cfarm_bench/BENCH_DONE" ]; do sleep 30; done
# the no-policy arm first, alone until it has unpacked the shared benchmark
if ! { tail -5 "$C/cfarm_null_2c_CA20.out" 2>/dev/null | grep -q "DIST CHECK PASS"; }; then
    note "arm null on cf_fix2_share_treatCu (the corrected Housing First)"
    ( env BUILD=cf_fix2_share_treatCu OMP_NUM_THREADS=2 DIAG_TAG=_2c_CA20 DRUG_PRICE_START=$P_NULL \
        sh treat/cf_arm_Cu.sh null > "$C/cfarm_null_2c_CA20.out" 2>&1 ) &
    echo $! > "$W/arm_null.pid"
    while [ ! -f "$C/cfarm_bench/BENCH_DONE" ] && alive "$W/arm_null.pid"; do sleep 10; done
    sleep 120
fi
if ! { tail -5 "$C/cfarm_tf_2c_fixboth_CA20.out" 2>/dev/null | grep -q "DIST CHECK PASS"; }; then
    note "arm fixboth on cf_fix2_treatCA (rule CA, detection ${RULEC_PDET:-0.20})"
    ( env BUILD=cf_fix2_treatCA OMP_NUM_THREADS=2 DIAG_TAG=_2c_fixboth_CA20 PDET=${RULEC_PDET:-0.20} PV_START=$V_NULL DRUG_PRICE_START=$P_NULL \
        DRUG_MARKET_ADJUSTER=0 EXTRA_SET="cost_per_drug_test $CTEST;adjust_taxes 0" \
        sh treat/cf_arm_CA.sh tf > "$C/cfarm_tf_2c_fixboth_CA20.out" 2>&1 ) &
    echo $! > "$W/arm_fixboth.pid"
fi
while alive "$W/arm_null.pid" || alive "$W/arm_fixboth.pid"; do sleep 60; done
for a in null_2c_CA20 tf_2c_fixboth_CA20; do
    note "$a: $(grep -a 'CHECK PASS\|GUARD' "$C/cfarm_$a.out" | tr '\n' ' ')"
done
note "arms done"
touch "$W/ARMS_DONE"
