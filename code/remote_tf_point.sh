#!/bin/sh
# ONE TREATMENT FIRST POINT, frozen, on the omega_c scan path.
#
#     ./remote_tf_point.sh 0.06
#
# A COPY of remote_scan_point.sh, not an edit of it: other runs in this family
# depend on that script unchanged. The only difference is the handover, which
# adds the TWO switches that make a run Treatment First:
#
#     voucher_conditional_on_clean                        1
#     increased_prob_of_voucher_if_homeless_and_addicted  0
#
# Everything else is the converged benchmark vector. In particular the three
# test parameters are LEFT AT THEIR DECLARED VALUES, which the seed carries:
#     probability_of_detection      0.95    line 487
#     probability_of_false_positive 0.005   line 488
#     cost_per_drug_test            0.00031 line 504
# They are inert in the benchmark (voucher_conditional_on_clean=0 there) and
# bind for the first time here, so the guards below assert them explicitly.
set -e
cd "$(dirname "$0")"
OMEGA="$1"
[ -n "$OMEGA" ] || { echo "usage: $0 <omega_c>"; exit 1; }
DIR="scan_tf$(echo "$OMEGA" | tr -d '.')"
SEED=scan_seed

[ -f "$SEED/PARAM_HANDOVER_base.txt" ] || { echo "GUARD: $SEED/PARAM_HANDOVER_base.txt is missing -- that file IS the converged vector"; exit 1; }
[ -f "$SEED/calibration_state.dat" ] || { echo "GUARD: no $SEED/calibration_state.dat"; exit 1; }
head -1 "$SEED/calibration_state.dat" | grep -qx 'calibration_state_v3' || { echo "GUARD: seed state is not v3"; exit 1; }
grep -q 'child_penalty_classes=2' housing_first_or_treatment_first_SR_v1.f90 || { echo "GUARD: source is not child_penalty_classes=2"; exit 1; }

command -v gfortran >/dev/null 2>&1 || {
  echo "gfortran is missing -- installing it (a rebuilt container loses it)"
  apt-get update -qq >/dev/null 2>&1
  apt-get install -y -qq gfortran >/dev/null 2>&1
  command -v gfortran >/dev/null 2>&1 || { echo "GUARD: gfortran could not be installed"; exit 1; }
}

# code/data MUST EXIST: the Fortran opens "../data/*.csv" relative to the run
# directory, so a scan point running from code/scan_<x>/ needs code/data. Absent,
# it prints "not found. stopping." and halts. Guard taken from remote_scan_point.sh.
[ -e data ] || ln -s ../data data

rm -rf "$DIR" && mkdir -p "$DIR"
echo "building (-O3 with -g -fbacktrace)..."
gfortran -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium \
         -O3 -funroll-loops -g -fbacktrace \
         -o "$DIR/hftf" housing_first_or_treatment_first_SR_v1.f90 2>build_$DIR.log
echo "built: $(grep -c Warning build_$DIR.log) warnings, $(grep -ci error build_$DIR.log) errors  (expect 7 and 0)"

cp "$SEED/calibration_state.dat" "$DIR/"
gunzip -c "$SEED/calibration_distribution1.dat.gz" > "$DIR/calibration_distribution1.dat"
gunzip -c "$SEED/calibration_distribution2.dat.gz" > "$DIR/calibration_distribution2.dat"
cp "$SEED/calibration_distribution_shape.dat" "$DIR/"
[ "$(stat -c%s "$DIR/calibration_distribution1.dat")" = "265496400" ] || { echo "GUARD: distribution 1 wrong size"; exit 1; }
[ "$(tr -d ' ' < "$DIR/calibration_distribution_shape.dat")" = "8564400" ] || { echo "GUARD: shape stamp is not two-class"; exit 1; }

cd "$DIR"
# THE FULL CONVERGED VECTOR. Three lines would leave addiction_onset_base at its
# declared 0.d0 and nobody would ever develop a disorder.
cp ../scan_seed/PARAM_HANDOVER_base.txt PARAM_HANDOVER.txt
sed -i "s|^weight_on_child .*|weight_on_child $OMEGA|" PARAM_HANDOVER.txt
sed -i "s|^voucher_conditional_on_clean .*|voucher_conditional_on_clean 1|" PARAM_HANDOVER.txt
sed -i "s|^increased_prob_of_voucher_if_homeless_and_addicted .*|increased_prob_of_voucher_if_homeless_and_addicted 0|" PARAM_HANDOVER.txt
cp PARAM_HANDOVER.txt PARAM_HANDOVER.relaunch.txt

n=$(wc -l < PARAM_HANDOVER.txt)
[ "$n" -gt 50 ] || { echo "GUARD: handover is only $n lines -- ZERO onset hazard"; exit 1; }
ob=$(awk '$1=="addiction_onset_base"{print $2}' PARAM_HANDOVER.txt | tr 'Dd' 'Ee')
awk -v v="$ob" 'BEGIN{exit !(v+0>0)}' || { echo "GUARD: addiction_onset_base is '$ob', not positive"; exit 1; }
grep -qx "weight_on_child $OMEGA"                             PARAM_HANDOVER.txt || { echo "GUARD: weight_on_child"; exit 1; }
grep -qx 'freeze_all_but_omega_c 1'                           PARAM_HANDOVER.txt || { echo "GUARD: must be FROZEN"; exit 1; }
grep -qx 'omega_c_is_pinned 1'                                PARAM_HANDOVER.txt || { echo "GUARD: omega_c must be pinned"; exit 1; }
# the two switches that make it Treatment First
grep -qx 'voucher_conditional_on_clean 1'                     PARAM_HANDOVER.txt || { echo "GUARD: drug test not on"; exit 1; }
grep -qx 'increased_prob_of_voucher_if_homeless_and_addicted 0' PARAM_HANDOVER.txt || { echo "GUARD: HF steering not off -- this would not be TF"; exit 1; }
# the variant that tests ONLY addicts must stay off
awk '$1=="voucher_conditional_on_clean_just_addicts"{v=$2} END{exit !(v+0==0)}' PARAM_HANDOVER.txt || { echo "GUARD: just_addicts variant is on"; exit 1; }
# the three test parameters, asserted at their declared values
awk '$1=="probability_of_detection"{v=$2} END{exit !(v+0==0.95)}'      PARAM_HANDOVER.txt || { echo "GUARD: p_det moved"; exit 1; }
awk '$1=="probability_of_false_positive"{v=$2} END{exit !(v+0==0.005)}' PARAM_HANDOVER.txt || { echo "GUARD: p_fp moved"; exit 1; }
awk '$1=="cost_per_drug_test"{v=$2} END{exit !(v+0==0.00031)}'          PARAM_HANDOVER.txt || { echo "GUARD: c_test moved"; exit 1; }
echo "handover: $n lines, TF switches set, test parameters at declared values"

export OMP_NUM_THREADS=2
date +%s > START_EPOCH
echo "solving TF at omega_c=$OMEGA with OMP_NUM_THREADS=2 ..."
./hftf > run.log 2> run.err
