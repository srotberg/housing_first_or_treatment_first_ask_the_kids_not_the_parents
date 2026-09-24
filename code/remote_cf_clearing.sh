#!/bin/sh
# remote_cf_clearing.sh <arm>     arm = tf | omega1 | internalise
#
# COUNTERFACTUALS WITH AN ENDOGENOUS DRUG PRICE, against Housing First at
# omega_c = 0.06 (results/reference/hf_omega_c_006/). Needs the binary from
# build_cf_clearing.sh, which takes the clearing branch of clear_drug_market.
#
# THE SUPPLY CURVE IS THE BENCHMARK'S. The clearing branch reads
# drug_supply_shifterbaseline_benchmark.dat; this script writes it from the
# Housing First omega_c = 0.06 run's LAST block, where the benchmark normalised
# the price to one at its own quantity V = 0.50141078281734985:
#     shifter = 1/V**(1/1.46) = 1.6045261392144357
# so every arm prices drugs on the curve that passes through (V_HF, 1) with
# elasticity 1.46, and the price is endogenous in every arm.
#
#   tf           Treatment First, rationed, holders AND applicants tested
#                (30% false negatives, no false positives, 3-year exclusion)
#   omega1       omega_c = 1
#   internalise  full homelessness internalisation at omega_c = 0.06
#
# The run leaves the loop on the stillness rule (frozen_stop_tolerance, 1e-3 in
# the base) or at block 30. The stillness rule does NOT look at the drug market,
# so the worker must check distance_drug_market < stopping_rule_drug_market (5e-3)
# at the exit block before calling the price cleared.
cd "$(dirname "$0")"
ARM="$1"
BIN=${CFC:-$(pwd)/cfc/cfc_prod}
SEED=scan_seed
SHIFTER=1.6045261392144357
case "$ARM" in
  tf|omega1|internalise) ;;
  *) echo "usage: $0 tf|omega1|internalise"; exit 1 ;;
esac
DIR="scan_cfc_$ARM"

[ -x "$BIN" ] || { echo "GUARD: no clearing binary at $BIN -- run ./build_cf_clearing.sh first"; exit 1; }
grep -q 'if (\.false\.) then' cfc/cfc.f90 2>/dev/null || [ -n "$CFC" ] || { echo "GUARD: cfc/cfc.f90 does not carry the clearing edit"; exit 1; }
[ -f "$SEED/PARAM_HANDOVER_base.txt" ] || { echo "GUARD: $SEED/PARAM_HANDOVER_base.txt is missing"; exit 1; }
head -1 "$SEED/calibration_state.dat" | grep -qx 'calibration_state_v3' || { echo "GUARD: seed state is not v3"; exit 1; }
[ -e data ] || ln -s ../data data

rm -rf "$DIR" && mkdir -p "$DIR"
cp "$BIN" "$DIR/hftf"; chmod +x "$DIR/hftf"
cp "$SEED/calibration_state.dat" "$DIR/"
gunzip -c "$SEED/calibration_distribution1.dat.gz" > "$DIR/calibration_distribution1.dat"
gunzip -c "$SEED/calibration_distribution2.dat.gz" > "$DIR/calibration_distribution2.dat"
cp "$SEED/calibration_distribution_shape.dat" "$DIR/"
[ "$(stat -c%s "$DIR/calibration_distribution1.dat")" = "265496400" ] || { echo "GUARD: distribution 1 wrong size"; exit 1; }

cd "$DIR"
python3 -c "print(f'{$SHIFTER:35.20f}')" > drug_supply_shifterbaseline_benchmark.dat
python3 -c "import sys; v=float(open('drug_supply_shifterbaseline_benchmark.dat').read()); sys.exit(abs(v-$SHIFTER)>1e-15)" \
  || { echo "GUARD: shifter file does not hold $SHIFTER"; exit 1; }

cp ../scan_seed/PARAM_HANDOVER_base.txt PARAM_HANDOVER.txt
# replace the line if present, append it if not; then assert it by value
set_line() {
  if grep -q "^$1 " PARAM_HANDOVER.txt; then sed -i "s|^$1 .*|$1 $2|" PARAM_HANDOVER.txt; else echo "$1 $2" >> PARAM_HANDOVER.txt; fi
  grep -qx "$1 $2" PARAM_HANDOVER.txt || { echo "GUARD: $1 is not '$2' in the file the run reads"; exit 1; }
}
set_line kappa_x                  0.9329
set_line frozen_stop_after_blocks 30
case "$ARM" in
  tf)
    set_line weight_on_child                                    0.06
    set_line voucher_conditional_on_clean                       1
    set_line increased_prob_of_voucher_if_homeless_and_addicted 1
    set_line probability_of_detection                           0.70
    set_line probability_of_false_positive                      0
    set_line include_voucher_exclusion                          1
    set_line drug_price_start                                   0.6 ;;
  omega1)
    set_line weight_on_child                                    1
    set_line drug_price_start                                   0.6 ;;
  internalise)
    set_line weight_on_child                                    0.06
    set_line internalise_homelessness_cost                      1
    set_line drug_price_start                                   1.0 ;;
esac
cp PARAM_HANDOVER.txt PARAM_HANDOVER.relaunch.txt

n=$(wc -l < PARAM_HANDOVER.txt)
[ "$n" -gt 50 ] || { echo "GUARD: handover is only $n lines -- ZERO onset hazard"; exit 1; }
grep -qx 'freeze_all_but_omega_c 1' PARAM_HANDOVER.txt || { echo "GUARD: must be FROZEN"; exit 1; }
grep -qx 'omega_c_is_pinned 1'      PARAM_HANDOVER.txt || { echo "GUARD: omega_c must be pinned"; exit 1; }
grep -q  '^drug_supply_elasticity 1.46' PARAM_HANDOVER.txt || { echo "GUARD: drug_supply_elasticity is not 1.46"; exit 1; }
echo "handover: $n lines, arm $ARM, every switch asserted by value; shifter $SHIFTER"

export OMP_NUM_THREADS=2
date +%s > START_EPOCH
echo "solving arm $ARM with an ENDOGENOUS drug price, OMP_NUM_THREADS=2 ..."
./hftf > run.log 2> run.err
