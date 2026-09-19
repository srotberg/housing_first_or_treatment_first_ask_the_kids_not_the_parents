#!/bin/bash
# build_cf.sh [outdir]
#
# Builds the COUNTERFACTUAL binary. is_counterfactual and
# use_revenues_to_increase_voucher_probability are compile-time parameters, so
# an arm needs its own binary; one binary serves all three arms.
#
# All three builds are made and all three must be clean -- that is the standing
# build check, not a formality. The -O3 one is what you run.
set -e
SRC=$(cd "$(dirname "$0")" && pwd)/housing_first_or_treatment_first_SR_v1.f90
OUT=${1:-$(pwd)/cf}
mkdir -p "$OUT"

# The counterfactual differs from the benchmark source in exactly two lines.
# Checked with diff, not assumed: any third difference means the source moved
# under this script and it should be looked at.
sed -e 's/integer, parameter :: is_counterfactual=0/integer, parameter :: is_counterfactual=1/' \
    -e 's/integer, parameter :: use_revenues_to_increase_voucher_probability=0/integer, parameter :: use_revenues_to_increase_voucher_probability=1/' \
    "$SRC" > "$OUT/cf.f90"

n=$(diff "$SRC" "$OUT/cf.f90" | grep -c '^[<>]' || true)
if [ "$n" -ne 4 ]; then
  echo "REFUSING: expected exactly 2 changed lines (4 diff lines), got $n."
  echo "Either the parameters were renamed or they are already set. Look before building."
  exit 1
fi

COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$OUT"
echo "bounds..." ; gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON cf.f90 -o hftf_cf_bounds 2> build_bounds.err
echo "snan..."   ; gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace $COMMON cf.f90 -o hftf_cf_snan 2> build_snan.err
echo "prod..."   ; gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err

for f in build_bounds.err build_snan.err build_prod.err; do
  e=$(grep -c "Error" "$f" || true)
  [ "$e" -gt 0 ] && { echo "BUILD ERRORS in $f"; head -20 "$f"; exit 1; }
done
echo "built in $OUT: hftf_cf_prod (run this), hftf_cf_bounds, hftf_cf_snan"
