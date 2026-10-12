#!/bin/bash
# build_treat.sh -- cf_fix2 as cf_runs/build_cf_fix2.sh generates it, then patch_treat.py: code/cf_fix2_split
# (the paper's rule, plus the MILBY SPLIT print) and code/cf_fix2_treat (treatment meets the condition, plus the print).
set -e
CODE=$(cd "$(dirname "$0")/.." && pwd)
cd "$CODE"
[ -f "$CODE/cf_fix2/cf.f90" ] || { GEN_ONLY=1 bash cf_runs/build_cf_fix.sh; GEN_ONLY=1 bash cf_runs/build_cf_fix2.sh; }
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
for m in split treat; do
    OUT=$CODE/cf_fix2_$m; mkdir -p "$OUT"
    python3 "$CODE/treat/patch_treat.py" $m "$CODE/cf_fix2/cf.f90" "$OUT/cf.f90"
    ( cd "$OUT" && gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err )
    [ "$(grep -c Error "$OUT/build_prod.err")" = 0 ] || { echo "REFUSING: $m did not compile"; grep -m3 Error "$OUT/build_prod.err"; exit 1; }
    echo "built $OUT/hftf_cf_prod"
done
