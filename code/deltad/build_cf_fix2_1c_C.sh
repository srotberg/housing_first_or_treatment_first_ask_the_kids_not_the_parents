#!/bin/bash
# build_cf_fix2_1c_C.sh -- build_cf_fix2_1c.sh's one-class counterfactual source, then rule C (treat/patch_treatC.py):
# code/cf_fix2_1c_treatC/hftf_cf_prod (12 October, the delta_d = 0 economy on the paper's rule C).
set -e
CODE=$(cd "$(dirname "$0")/.." && pwd)
cd "$CODE"
[ -f "$CODE/cf_fix2/cf.f90" ] || { GEN_ONLY=1 bash cf_runs/build_cf_fix.sh; GEN_ONLY=1 bash cf_runs/build_cf_fix2.sh; }
OUT=$CODE/cf_fix2_1c_treatC; mkdir -p "$OUT"
sed -e "s/^        integer, parameter :: child_penalty_classes=2\$/        integer, parameter :: child_penalty_classes=1/" "$CODE/cf_fix2/cf.f90" > "$OUT/cf_1c.f90"
[ "$(diff "$CODE/cf_fix2/cf.f90" "$OUT/cf_1c.f90" | grep -c '^[<>]')" = 2 ] || { echo "REFUSING: expected one changed line"; exit 1; }
python3 "$CODE/treat/patch_treatC.py" "$OUT/cf_1c.f90" "$OUT/cf.f90"
grep -q -x "        integer, parameter :: child_penalty_classes=1" "$OUT/cf.f90" || { echo "REFUSING: not one class"; exit 1; }
grep -q "RULE C (patch_treatC.py)" "$OUT/cf.f90" || { echo "REFUSING: not rule C"; exit 1; }
grep -q "if (drug_market_adjuster==0.d0) distance_drug_market=0" "$OUT/cf.f90" || { echo "REFUSING: no held-price stopping rule"; exit 1; }
cd "$OUT"
gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium cf.f90 -o hftf_cf_prod 2> build_prod.err
[ "$(grep -c Error build_prod.err)" = 0 ] || { echo "REFUSING: build errors"; grep -m3 Error build_prod.err; exit 1; }
echo "built $OUT/hftf_cf_prod"
