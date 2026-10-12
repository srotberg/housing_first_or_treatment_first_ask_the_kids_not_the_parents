#!/bin/bash
# build_both_sp.sh -- THE BOTH-PENALTIES BUILDS IN SINGLE PRECISION, TREATMENT FIRST ON RULE C (12 October).
# The sources are generated exactly as build_both.sh generates them (the benchmark of record's base with patch_both.py;
# cf_fix2 with patch_both.py), and then:
#   code/bench_both_sp/hftf_bench        = patch_sp.py(bench_both source)                      the benchmark
#   code/cf_fix2_both_spC/hftf_cf_prod   = patch_sp.py(patch_treatC.py(cf_fix2_both source))   the arms, rule C
# patch_sp.py stores the value function and policies in four bytes (integers in two) and keeps the distributions double;
# patch_treatC.py is the paper's screen from 12 October (in treatment if disordered, nobody may use).
# Nothing is written into code/bench_both or code/cf_fix2_both: a run of build_both.sh's binaries is never disturbed.
set -e
CODE=$(cd "$(dirname "$0")/.." && pwd)
SRC=$CODE/housing_first_or_treatment_first_SR_v1.f90
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
G=$CODE/both_sp_gen; mkdir -p "$G"

# the benchmark source, as build_both.sh makes it
ln_of() { n=$(grep -n -F -x -- "$1" "$SRC" | cut -d: -f1); [ "$(echo "$n" | wc -w)" = 1 ] || { echo "REFUSING: anchor not unique: $1"; exit 1; }; echo $n; }
BL=$(ln_of "                    stopping_rule_stationary_distribution=6*10.d0**(-4)")
WL=$(ln_of "        do while (distance_distribution>stopping_rule_stationary_distribution)")
sed -e "${BL}s/6\*10.d0\*\*(-4)/5*10.d0**(-5)/" \
    -e "${WL}s/do while (distance_distribution>stopping_rule_stationary_distribution)/do while ((distance_distribution>stopping_rule_stationary_distribution) .OR. (loop_count_dist<70))/" \
    "$SRC" > "$G/bench_base.f90"
n=$(diff "$SRC" "$G/bench_base.f90" | grep -c '^[<>]' || true)
[ "$n" -eq 4 ] || { echo "REFUSING: expected 4 diff lines in the benchmark base, got $n"; exit 1; }
grep -q "integer, parameter :: is_counterfactual=0" "$G/bench_base.f90" || { echo "REFUSING: not a benchmark build"; exit 1; }
python3 "$CODE/deltah/patch_both.py" "$G/bench_base.f90" "$G/bench_both.f90"

# the counterfactual source, as build_both.sh makes it
cd "$CODE"
[ -f "$CODE/cf_fix2/cf.f90" ] || { GEN_ONLY=1 bash cf_runs/build_cf_fix.sh; GEN_ONLY=1 bash cf_runs/build_cf_fix2.sh; }
python3 "$CODE/deltah/patch_both.py" "$CODE/cf_fix2/cf.f90" "$G/cf_both.f90"
grep -q "integer, parameter :: is_counterfactual=1" "$G/cf_both.f90" || { echo "REFUSING: not a counterfactual build"; exit 1; }
python3 "$CODE/treat/patch_treatC.py" "$G/cf_both.f90" "$G/cf_bothC.f90"
grep -q "RULE C (patch_treatC.py)" "$G/cf_bothC.f90" || { echo "REFUSING: rule C not in the arms' source"; exit 1; }

B=$CODE/bench_both_sp; A=$CODE/cf_fix2_both_spC; mkdir -p "$B" "$A"
python3 "$CODE/deltah/patch_sp.py" "$G/bench_both.f90" "$B/cf.f90"
python3 "$CODE/deltah/patch_sp.py" "$G/cf_bothC.f90" "$A/cf.f90"
( cd "$B" && gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_bench 2> build_prod.err ) &
( cd "$A" && gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err ) &
wait
for d in "$B" "$A"; do
    echo "$d warnings=$(grep -c Warning "$d/build_prod.err") errors=$(grep -c Error "$d/build_prod.err")"
    [ "$(grep -c Error "$d/build_prod.err")" = 0 ] || exit 1
done
[ -x "$B/hftf_bench" ] && [ -x "$A/hftf_cf_prod" ] || { echo "REFUSING: a binary is missing"; exit 1; }
echo "built $B/hftf_bench and $A/hftf_cf_prod"
