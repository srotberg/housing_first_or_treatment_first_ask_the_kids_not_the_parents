#!/bin/bash
# build_pe_C.sh -- RULE C (12 October) for the no-externality experiment: cf_fix2_pe_treatC = cf_fix2_pe (pe_noext/
# build_pe.sh: cf_fix2 + patch_pe.py hold, the PE USED print and the house-price hold; Arm B) + treat/patch_treatC.py
# (a household with the disorder must be in treatment, nobody may use; plus the MILBY SPLIT print). Also builds, when
# missing, everything the rule-C no-externality launchers use: cf_fix, cf_fix2, cf_fix2_share, the two pe builds,
# cf_fix2_treatC (treat/build_treatC.sh; Arms C and D) and cf_walk (pe_noext/patch_walk.py on cf_fix2_share_pe).
# Production binary only. Do NOT build while a solve of the same build is running. A COPY: build_pe.sh is unchanged.
set -e
C=$(cd "$(dirname "$0")/.." && pwd)
cd "$C"
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
for b in cf_fix cf_fix2; do
    [ -x "$b/hftf_cf_prod" ] && [ "$b/hftf_cf_prod" -nt housing_first_or_treatment_first_SR_v1.f90 ] || bash "cf_runs/build_$b.sh"
done
[ -x cf_fix2_share/hftf_cf_prod ] && [ ! cf_fix2_share/hftf_cf_prod -ot cf_fix2/hftf_cf_prod ] || bash transition_fix/build_cf_fix2_share.sh
[ -x cf_fix2_pe/hftf_cf_prod ] && [ -x cf_fix2_share_pe/hftf_cf_prod ] && [ ! cf_fix2_share_pe/hftf_cf_prod -ot cf_fix2_share/hftf_cf_prod ] || bash pe_noext/build_pe.sh
[ -x cf_fix2_treatC/hftf_cf_prod ] && [ ! cf_fix2_treatC/hftf_cf_prod -ot cf_fix2/hftf_cf_prod ] || bash treat/build_treatC.sh
if [ ! -x cf_walk/hftf_cf_prod ] || [ cf_walk/hftf_cf_prod -ot cf_fix2_share_pe/hftf_cf_prod ]; then
    mkdir -p cf_walk
    python3 pe_noext/patch_walk.py cf_fix2_share_pe/cf.f90 cf_walk/cf.f90
    ( cd cf_walk && gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err )
    [ -x cf_walk/hftf_cf_prod ] || { echo "REFUSING: cf_walk did not compile"; exit 1; }
fi
OUT=cf_fix2_pe_treatC; mkdir -p $OUT
python3 treat/patch_treatC.py cf_fix2_pe/cf.f90 $OUT/cf.f90
grep -q "RULE C (patch_treatC.py)" $OUT/cf.f90 || { echo "REFUSING: rule C did not land in $OUT"; exit 1; }
grep -q "PE HOLD housing_price set to" $OUT/cf.f90 || { echo "REFUSING: the house-price hold is not in $OUT"; exit 1; }
( cd $OUT && gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err )
[ "$(grep -c Error $OUT/build_prod.err)" = 0 ] && [ -x $OUT/hftf_cf_prod ] || { echo "REFUSING: $OUT did not compile"; grep -m3 Error $OUT/build_prod.err; exit 1; }
for b in cf_fix2_treatC cf_fix2_pe_treatC; do
    echo "$b: rule C $(grep -c 'RULE C (patch_treatC.py)' $b/cf.f90), diff lines against cf_fix2 $(diff cf_fix2/cf.f90 $b/cf.f90 | grep -c '^[<>]')"
done
echo "built $C/$OUT/hftf_cf_prod"
