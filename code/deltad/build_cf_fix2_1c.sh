#!/bin/bash
# build_cf_fix2_1c.sh -- cf_fix2 as cf_runs/build_cf_fix2.sh generates it, with child_penalty_classes 2 -> 1 (12 October,
# the author: delta_d = 0 and delta_h = 0 "there you dont need two classes, so it should be super quick"): with no penalty
# the two child classes are the same economy, and one class halves the state. -> code/cf_fix2_1c/hftf_cf_prod
set -e
CODE=$(cd "$(dirname "$0")/.." && pwd)
cd "$CODE"
[ -f "$CODE/cf_fix2/cf.f90" ] || { GEN_ONLY=1 bash cf_runs/build_cf_fix.sh; GEN_ONLY=1 bash cf_runs/build_cf_fix2.sh; }
OUT=$CODE/cf_fix2_1c; mkdir -p "$OUT"
sed -e "s/^        integer, parameter :: child_penalty_classes=2\$/        integer, parameter :: child_penalty_classes=1/" "$CODE/cf_fix2/cf.f90" > "$OUT/cf.f90"
[ "$(diff "$CODE/cf_fix2/cf.f90" "$OUT/cf.f90" | grep -c '^[<>]')" = 2 ] || { echo "REFUSING: expected one changed line"; exit 1; }
grep -q -x "        integer, parameter :: child_penalty_classes=1" "$OUT/cf.f90" || { echo "REFUSING: not one class"; exit 1; }
grep -q "integer, parameter :: is_counterfactual=1" "$OUT/cf.f90" || { echo "REFUSING: not a counterfactual build"; exit 1; }
cd "$OUT"
gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium cf.f90 -o hftf_cf_prod 2> build_prod.err
[ "$(grep -c Error build_prod.err)" = 0 ] || { echo "REFUSING: build errors"; grep -m3 Error build_prod.err; exit 1; }
echo "built $OUT/hftf_cf_prod"
