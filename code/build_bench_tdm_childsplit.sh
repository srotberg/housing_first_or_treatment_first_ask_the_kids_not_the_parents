#!/bin/bash
# THE CHILD-PENALTY FIX (d45b36ea) PLUS THE CHILD IN THE DRUG SPLIT (30 September), BUILT AS THE BENCHMARK OF RECORD WAS: THE BENCHMARK BINARY WITH THE COUNTERFACTUAL'S DISTRIBUTION NUMERICS (26 September;
# the author: "run the benchmark re-solve first"). Two lines: the calibration loop's
# distribution rule 6e-4 -> 5e-5 (source 47815, the include_addiction branch) and the
# sweep loop's condition "at least 70 sweeps" -- exactly what code/cf_tdm does in the
# counterfactual loop. Source untouched. All three builds.
set -e
CODE=$(cd "$(dirname "$0")" && pwd)   # the repo was renamed: workers clone it as children_first_housing_later (18 Oct)
SRC=$CODE/housing_first_or_treatment_first_SR_v1.f90
OUT=$CODE/bench_tdm_childsplit; mkdir -p "$OUT"
ln_of() { n=$(grep -n -F -x -- "$1" "$SRC" | cut -d: -f1); [ "$(echo "$n" | wc -w)" = 1 ] || { echo "REFUSING: anchor not unique: $1"; exit 1; }; echo $n; }
BL=$(ln_of "                    stopping_rule_stationary_distribution=6*10.d0**(-4)")
WL=$(ln_of "        do while (distance_distribution>stopping_rule_stationary_distribution)")
sed -e "${BL}s/6\*10.d0\*\*(-4)/5*10.d0**(-5)/" \
    -e "${WL}s/do while (distance_distribution>stopping_rule_stationary_distribution)/do while ((distance_distribution>stopping_rule_stationary_distribution) .OR. (loop_count_dist<70))/" \
    "$SRC" > "$OUT/cf.f90"
n=$(diff "$SRC" "$OUT/cf.f90" | grep -c '^[<>]' || true)
[ "$n" -eq 4 ] || { echo "REFUSING: expected 4 diff lines, got $n"; exit 1; }
[ "$(sed -n "${BL}p" "$OUT/cf.f90")" = "                    stopping_rule_stationary_distribution=5*10.d0**(-5)" ] || { echo "REFUSING: rule not 5e-5"; exit 1; }
grep -q -x "        do while ((distance_distribution>stopping_rule_stationary_distribution) .OR. (loop_count_dist<70))" "$OUT/cf.f90" || { echo "REFUSING: minimum sweeps not set"; exit 1; }
grep -q "integer, parameter :: is_counterfactual=0" "$OUT/cf.f90" || { echo "REFUSING: not a benchmark build"; exit 1; }
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$OUT"
gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON cf.f90 -o hftf_bench_bounds 2> build_bounds.err
gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace $COMMON cf.f90 -o hftf_bench_snan 2> build_snan.err
gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_bench 2> build_prod.err
for f in build_bounds.err build_snan.err build_prod.err; do echo "$OUT $f warnings=$(grep -c Warning $f) errors=$(grep -c Error $f)"; done
