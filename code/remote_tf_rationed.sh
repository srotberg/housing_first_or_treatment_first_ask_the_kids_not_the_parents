#!/bin/sh
# TREATMENT FIRST, RATIONED VOUCHERS, EVERY HOLDER TESTED (arm-3 spec).
#
# NOT "universal": that word means universal PROVISION in this code and in the
# paper -- probability_of_voucher_benchmark_used == 1, the counter_VTE_TF arm at
# line 13469. Here the voucher lottery stays at the benchmark's calibrated rate,
# which is the code's counter_TF, and what changes is that every HOLDER is tested.
#
#     ./remote_tf_rationed.sh 0.06
#
# THE AUTHOR'S SPECIFICATION, 24 September: "TF should test everyone who has a
# voucher! not just the homeless. And if you fail, you are not eligible for an
# average of 3 years. And false negative occurs at a rate of 30%. Also, no false
# positive." That is the arm-3 specification of 19 September.
#
# Needs the holder-testing binary from build_tf_rationed.sh: the two branches that
# test a voucher HOLDER are guarded on is_counterfactual==1 in the tracked
# source, and is_counterfactual is a compile-time parameter fixed at 0.
#
# frozen_stop_after_blocks 12 takes the run out of the calibration loop at block
# 12 and straight into save_welfare_curve -- no kill, no resume. A RESUME from a
# converged state re-enters the restart transient and writes the curve for a
# different economy; that design failed its control on omega_c = 1.
set -e
cd "$(dirname "$0")"
OMEGA="$1"
[ -n "$OMEGA" ] || { echo "usage: $0 <omega_c>"; exit 1; }
# SECOND ARGUMENT "tested": APPLICANTS ARE TESTED BEFORE BEING REJECTED.
# The author, 24 September: "it should be tested before being rejected. the
# false negative should apply to applicants too." With the homeless-addicted
# multiplier at 0, a failing applicant's offer is (1-p_det)*prob*0 = 0 -- an
# outright ban, detection never enters (voucher_probabilities, ~line 36711).
# At 1 the applicant is offered at the base rate and then tested: 30 per cent
# get the voucher, 70 per cent are caught and go to the three-year exclusion.
# Holders are tested exactly as before. No Fortran change is involved.
MODE="${2:-ban}"
case "$MODE" in
  ban)    INC=0; DIR="scan_tfu$(echo "$OMEGA" | tr -d '.')" ;;
  tested) INC=1; DIR="scan_tft$(echo "$OMEGA" | tr -d '.')" ;;
  *) echo "usage: $0 <omega_c> [ban|tested]"; exit 1 ;;
esac
SEED=scan_seed
BIN=${TFU:-$(pwd)/tfu/tfu_prod}

[ -x "$BIN" ] || { echo "GUARD: no holder-testing binary at $BIN -- run ./build_tf_rationed.sh first"; exit 1; }
[ -f "$SEED/PARAM_HANDOVER_base.txt" ] || { echo "GUARD: $SEED/PARAM_HANDOVER_base.txt is missing"; exit 1; }
head -1 "$SEED/calibration_state.dat" | grep -qx 'calibration_state_v3' || { echo "GUARD: seed state is not v3"; exit 1; }
grep -q 'child_penalty_classes=2' housing_first_or_treatment_first_SR_v1.f90 || { echo "GUARD: source is not child_penalty_classes=2"; exit 1; }

# the Fortran opens ../data/*.csv relative to the RUN directory
[ -e data ] || ln -s ../data data

rm -rf "$DIR" && mkdir -p "$DIR"
cp "$BIN" "$DIR/hftf"; chmod +x "$DIR/hftf"
cp "$SEED/calibration_state.dat" "$DIR/"
gunzip -c "$SEED/calibration_distribution1.dat.gz" > "$DIR/calibration_distribution1.dat"
gunzip -c "$SEED/calibration_distribution2.dat.gz" > "$DIR/calibration_distribution2.dat"
cp "$SEED/calibration_distribution_shape.dat" "$DIR/"
[ "$(stat -c%s "$DIR/calibration_distribution1.dat")" = "265496400" ] || { echo "GUARD: distribution 1 wrong size"; exit 1; }
[ "$(tr -d ' ' < "$DIR/calibration_distribution_shape.dat")" = "8564400" ] || { echo "GUARD: shape stamp is not two-class"; exit 1; }

cd "$DIR"
# THE FULL CONVERGED VECTOR, 97 lines. Three lines would leave
# addiction_onset_base at its declared 0.d0 and nobody would develop a disorder.
cp ../scan_seed/PARAM_HANDOVER_base.txt PARAM_HANDOVER.txt
set_line() { sed -i "s|^$1 .*|$1 $2|" PARAM_HANDOVER.txt; grep -qx "$1 $2" PARAM_HANDOVER.txt || { echo "GUARD: $1 is not '$2' in the file the run reads"; exit 1; }; }

set_line weight_on_child                                    "$OMEGA"
set_line voucher_conditional_on_clean                       1
set_line increased_prob_of_voucher_if_homeless_and_addicted "$INC"
set_line probability_of_detection                           0.70
set_line probability_of_false_positive                      0
set_line include_voucher_exclusion                          1
set_line frozen_stop_after_blocks                           12
set_line kappa_x                                            0.9329
cp PARAM_HANDOVER.txt PARAM_HANDOVER.relaunch.txt

n=$(wc -l < PARAM_HANDOVER.txt)
[ "$n" -gt 50 ] || { echo "GUARD: handover is only $n lines -- ZERO onset hazard"; exit 1; }
ob=$(awk '$1=="addiction_onset_base"{print $2}' PARAM_HANDOVER.txt | tr 'Dd' 'Ee')
awk -v v="$ob" 'BEGIN{exit !(v+0>0)}' || { echo "GUARD: addiction_onset_base is '$ob', not positive"; exit 1; }
grep -qx 'freeze_all_but_omega_c 1' PARAM_HANDOVER.txt || { echo "GUARD: must be FROZEN"; exit 1; }
grep -qx 'omega_c_is_pinned 1'      PARAM_HANDOVER.txt || { echo "GUARD: omega_c must be pinned"; exit 1; }
awk '$1=="voucher_conditional_on_clean_just_addicts"{v=$2} END{exit !(v+0==0)}' PARAM_HANDOVER.txt || { echo "GUARD: just_addicts variant is on"; exit 1; }
echo "handover: $n lines, all eight switches asserted by value"

export OMP_NUM_THREADS=2
date +%s > START_EPOCH
echo "solving RATIONED TF (every holder tested, applicants: $MODE) at omega_c=$OMEGA, OMP_NUM_THREADS=2 ..."
./hftf > run.log 2> run.err
