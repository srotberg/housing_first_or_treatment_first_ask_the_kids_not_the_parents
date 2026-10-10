#!/bin/bash
# build_hh.sh [bench|cf|both] [bounds] -- THE HOMELESSNESS-LATCH BUILDS (10 October, patch_latch.py: the latch where the SUD history was).
#   bench: the benchmark binary exactly as build_bench_tdm_childsplit.sh builds the benchmark of record
#          (the source with the distribution rule 5e-5 and at least 70 sweeps), then patch_latch.py
#          -> code/bench_hh/hftf_bench
#   cf:    cf_fix2 exactly as cf_runs/build_cf_fix.sh and build_cf_fix2.sh generate it, then patch_latch.py
#          -> code/cf_fix2_hh/hftf_cf_prod
# A second argument "bounds" also builds the -fcheck=bounds binary (hftf_bench_bounds, hftf_cf_bounds).
# Source untouched; every generated file is checked for the expected number of patch sites.
set -e
CODE=$(cd "$(dirname "$0")/.." && pwd)
SRC=$CODE/housing_first_or_treatment_first_SR_v1.f90
WHAT="${1:-both}"; BOUNDS="${2:-}"
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"

if [ "$WHAT" = bench ] || [ "$WHAT" = both ]; then
    OUT=$CODE/bench_hh; mkdir -p "$OUT"
    ln_of() { n=$(grep -n -F -x -- "$1" "$SRC" | cut -d: -f1); [ "$(echo "$n" | wc -w)" = 1 ] || { echo "REFUSING: anchor not unique: $1"; exit 1; }; echo $n; }
    BL=$(ln_of "                    stopping_rule_stationary_distribution=6*10.d0**(-4)")
    WL=$(ln_of "        do while (distance_distribution>stopping_rule_stationary_distribution)")
    sed -e "${BL}s/6\*10.d0\*\*(-4)/5*10.d0**(-5)/" \
        -e "${WL}s/do while (distance_distribution>stopping_rule_stationary_distribution)/do while ((distance_distribution>stopping_rule_stationary_distribution) .OR. (loop_count_dist<70))/" \
        "$SRC" > "$OUT/base.f90"
    n=$(diff "$SRC" "$OUT/base.f90" | grep -c '^[<>]' || true)
    [ "$n" -eq 4 ] || { echo "REFUSING: expected 4 diff lines in the benchmark base, got $n"; exit 1; }
    grep -q "integer, parameter :: is_counterfactual=0" "$OUT/base.f90" || { echo "REFUSING: not a benchmark build"; exit 1; }
    python3 "$CODE/deltah/patch_latch.py" "$OUT/base.f90" "$OUT/cf.f90"
    cd "$OUT"
    gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_bench 2> build_prod.err
    [ "$BOUNDS" = bounds ] && gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON cf.f90 -o hftf_bench_bounds 2> build_bounds.err
    for f in build_*.err; do echo "$OUT $f warnings=$(grep -c Warning $f) errors=$(grep -c Error $f)"; done
    [ "$(grep -c Error build_prod.err)" = 0 ] || exit 1
fi

if [ "$WHAT" = cf ] || [ "$WHAT" = both ]; then
    cd "$CODE"
    GEN_ONLY=1 bash cf_runs/build_cf_fix.sh
    GEN_ONLY=1 bash cf_runs/build_cf_fix2.sh
    OUT=$CODE/cf_fix2_hh; mkdir -p "$OUT"
    python3 "$CODE/deltah/patch_latch.py" "$CODE/cf_fix2/cf.f90" "$OUT/cf.f90"
    grep -q "integer, parameter :: is_counterfactual=1" "$OUT/cf.f90" || { echo "REFUSING: not a counterfactual build"; exit 1; }
    cd "$OUT"
    gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err
    [ "$BOUNDS" = bounds ] && gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON cf.f90 -o hftf_cf_bounds 2> build_bounds.err
    for f in build_*.err; do echo "$OUT $f warnings=$(grep -c Warning $f) errors=$(grep -c Error $f)"; done
    [ "$(grep -c Error build_prod.err)" = 0 ] || exit 1
fi
