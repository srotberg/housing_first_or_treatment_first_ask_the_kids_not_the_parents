#!/bin/bash
# build_treatCA.sh -- cf_fix2 as cf_runs/build_cf_fix2.sh generates it, then patch_treatCA.py: code/cf_fix2_treatCA
# (rule A's screen on rule C's build: the disorder fails in treatment or not, nobody may use, treatment publicly paid
# for, the abstention option off). A new file beside build_treatC.sh, which running workers execute.
set -e
CODE=$(cd "$(dirname "$0")/.." && pwd)
cd "$CODE"
[ -f "$CODE/cf_fix2/cf.f90" ] || { GEN_ONLY=1 bash cf_runs/build_cf_fix.sh; GEN_ONLY=1 bash cf_runs/build_cf_fix2.sh; }
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
OUT=$CODE/cf_fix2_treatCA; mkdir -p "$OUT"
python3 "$CODE/treat/patch_treatCA.py" "$CODE/cf_fix2/cf.f90" "$OUT/cf.f90"
( cd "$OUT" && gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err )
[ "$(grep -c Error "$OUT/build_prod.err")" = 0 ] || { echo "REFUSING: treatCA did not compile"; grep -m3 -A3 Error "$OUT/build_prod.err"; exit 1; }
echo "built $OUT/hftf_cf_prod"
