#!/bin/sh
# remote_cf_arm.sh <arm>     arm = tf | omega1 | internalise
#
# A COUNTERFACTUAL THE WAY THE OLD ARMS RAN IT: the counterfactual binary
# (build_cf.sh: is_counterfactual=1, use_revenues_to_increase_voucher_probability=1)
# against a Housing First omega_c = 0.06 benchmark solved IN THE SAME DIRECTORY.
#
#   * the drug price CLEARS on the benchmark's supply curve, elasticity 1.46
#     (clear_drug_market's counterfactual branch reads the benchmark's shifter);
#   * tf clears the budget with pi_V (adjust_taxes 1 -> tax_system_type 3: the
#     voucher lottery moves, the tax does not); omega1 and internalise have NO
#     budget clearing (adjust_taxes 0) -- the author, 24 September;
#   * upload_vars imports the benchmark's median income, labour income profile,
#     net revenue constraint and the rest from its own saved files, so no
#     declaration has to be edited.
#
# STAGE 1 solves the benchmark (12 blocks, straight into save_welfare_curve) and
# writes BENCH_DONE. STAGE 2 runs the arm. A relaunch after a container rebuild
# skips stage 1 when BENCH_DONE and the benchmark files are on disk.
set -e
cd "$(dirname "$0")"
ARM="$1"
case "$ARM" in tf|omega1|internalise) ;; *) echo "usage: $0 tf|omega1|internalise"; exit 1 ;; esac
DIR="cfarm_$ARM"; SEED=scan_seed
export OMP_NUM_THREADS=2
command -v gfortran >/dev/null || { echo "GUARD: no gfortran"; exit 1; }
[ -e data ] || ln -s ../data data
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"

# the benchmark binary is the TRACKED source, unmodified
if [ ! -x bench/hftf_bench ]; then
  mkdir -p bench
  gfortran -O3 -funroll-loops $COMMON housing_first_or_treatment_first_SR_v1.f90 -o bench/hftf_bench 2> bench/build_prod.err
  e=$(grep -c Error bench/build_prod.err || true); [ "$e" = 0 ] || { echo "GUARD: benchmark build errors"; exit 1; }
fi
[ -x cf/hftf_cf_prod ] || sh build_cf.sh "$(pwd)/cf"

set_line() {
  if grep -q "^$1 " PARAM_HANDOVER.txt; then sed -i "s|^$1 .*|$1 $2|" PARAM_HANDOVER.txt; else echo "$1 $2" >> PARAM_HANDOVER.txt; fi
  grep -qx "$1 $2" PARAM_HANDOVER.txt || { echo "GUARD: $1 is not '$2' in the file the run reads"; exit 1; }
}
stage_handover() {
  cp ../$SEED/PARAM_HANDOVER_base.txt PARAM_HANDOVER.txt
  n=$(wc -l < PARAM_HANDOVER.txt); [ "$n" -gt 50 ] || { echo "GUARD: handover only $n lines"; exit 1; }
  set_line kappa_x 0.9329
}

if [ -f "$DIR/BENCH_DONE" ] && [ -f "$DIR/welfare_curvebaseline_benchmark.dat" ] && [ -f "$DIR/median_incomebaseline_benchmark.dat" ]; then
  echo "STAGE 1 already done in $DIR -- skipping the benchmark"
  cd "$DIR"
else
  rm -rf "$DIR" && mkdir -p "$DIR"
  cp "$SEED/calibration_state.dat" "$SEED/calibration_distribution_shape.dat" "$DIR/"
  gunzip -c "$SEED/calibration_distribution1.dat.gz" > "$DIR/calibration_distribution1.dat"
  gunzip -c "$SEED/calibration_distribution2.dat.gz" > "$DIR/calibration_distribution2.dat"
  [ "$(stat -c%s "$DIR/calibration_distribution1.dat")" = "265496400" ] || { echo "GUARD: distribution 1 wrong size"; exit 1; }
  cd "$DIR"
  cp ../bench/hftf_bench ./hftf_bench
  stage_handover
  set_line weight_on_child          0.06
  set_line frozen_stop_after_blocks 12
  cp PARAM_HANDOVER.txt PARAM_HANDOVER.bench.txt
  echo "STAGE 1: Housing First omega_c = 0.06 benchmark, 12 blocks ..."
  ./hftf_bench > bench.log 2> bench.err
  for f in welfare_curvebaseline_benchmark.dat median_incomebaseline_benchmark.dat drug_supply_shifterbaseline_benchmark.dat; do
    [ -s "$f" ] || { echo "GUARD: the benchmark did not write $f -- it never reached the save"; exit 1; }
  done
  date +%s > BENCH_DONE
  echo "STAGE 1 done"
fi

cp ../cf/hftf_cf_prod ./hftf_cf
stage_handover
case "$ARM" in
  tf)          set_line weight_on_child 0.06
               set_line voucher_conditional_on_clean 1
               set_line increased_prob_of_voucher_if_homeless_and_addicted 1
               set_line probability_of_detection 0.70
               set_line probability_of_false_positive 0
               set_line include_voucher_exclusion 1
               set_line adjust_taxes 1
               set_line drug_price_start 0.6 ;;
  omega1)      set_line weight_on_child 1
               set_line adjust_taxes 0
               set_line drug_price_start 0.6 ;;
  internalise) set_line weight_on_child 0.06
               set_line internalise_homelessness_cost 1
               set_line adjust_taxes 0
               set_line drug_price_start 1.0 ;;
esac
cp PARAM_HANDOVER.txt PARAM_HANDOVER.arm.txt
echo "STAGE 2: arm $ARM on the counterfactual binary ..."
./hftf_cf > cf.log 2> cf.err
echo "STAGE 2 exited"
