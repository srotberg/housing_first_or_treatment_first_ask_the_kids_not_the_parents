#!/bin/bash
# build_treatC2.sh -- cf_fix2 as cf_runs/build_cf_fix2.sh generates it, then patch_treatC2.py: code/cf_fix2_treatC2
# (rule C as cf_fix2_treatC, plus the abstention option for a treated household with the disorder, the EV table keyed on
# the voucher category, internal_computations with the household's own treatment, use counted as v>0, the ABSTAIN print).
# A new file beside build_treatC.sh, which running workers execute.
set -e
CODE=$(cd "$(dirname "$0")/.." && pwd)
cd "$CODE"
[ -f "$CODE/cf_fix2/cf.f90" ] || { GEN_ONLY=1 bash cf_runs/build_cf_fix.sh; GEN_ONLY=1 bash cf_runs/build_cf_fix2.sh; }
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
OUT=$CODE/cf_fix2_treatC2; mkdir -p "$OUT"
python3 "$CODE/treat/patch_treatC2.py" "$CODE/cf_fix2/cf.f90" "$OUT/cf.f90"
( cd "$OUT" && gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err )
[ "$(grep -c Error "$OUT/build_prod.err")" = 0 ] || { echo "REFUSING: treatC2 did not compile"; grep -m3 -A3 Error "$OUT/build_prod.err"; exit 1; }
echo "built $OUT/hftf_cf_prod"
