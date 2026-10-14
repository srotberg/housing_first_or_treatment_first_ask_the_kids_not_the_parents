#!/bin/bash
# build_share_pe_treatCu.sh -- build_share_treatCu.sh for the no-externality economy's Housing First (Arm A), 14 October:
# code/cf_fix2_share_pe_treatCu = cf_fix2_share_pe (pe_noext/build_pe.sh) + treat/patch_treatCu.py, the internal_computations
# fix ungated so Housing First runs the same arithmetic as Treatment First (code/RULE_C_PLAN.md, '05:20 THE DIAGNOSTIC').
# Against cf_fix2_share_pe_treatC (treat/build_share_treatC.sh share_pe) the source differs at the gate's one line (plus
# the marker comment). Used by noext_clear/noext_Cu_lib.sh for Arm A (cfarm_null_pe_noext_Cu).
set -e
C=$(cd "$(dirname "$0")/.." && pwd); cd "$C"
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
[ -f cf_fix2_share_pe/cf.f90 ] || bash pe_noext/build_pe.sh
mkdir -p cf_fix2_share_pe_treatCu
python3 treat/patch_treatCu.py cf_fix2_share_pe/cf.f90 cf_fix2_share_pe_treatCu/cf.f90
grep -q "INTERNAL UNGATED (patch_treatCu.py)" cf_fix2_share_pe_treatCu/cf.f90 || { echo "REFUSING: the ungated fix did not land"; exit 1; }
grep -q "RULE C (patch_treatC.py)" cf_fix2_share_pe_treatCu/cf.f90 || { echo "REFUSING: rule C did not land"; exit 1; }
( cd cf_fix2_share_pe_treatCu && gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err )
[ "$(grep -c Error cf_fix2_share_pe_treatCu/build_prod.err)" = 0 ] && [ -x cf_fix2_share_pe_treatCu/hftf_cf_prod ] || { echo "REFUSING: cf_fix2_share_pe_treatCu did not compile"; grep -m3 Error cf_fix2_share_pe_treatCu/build_prod.err; exit 1; }
if [ -f cf_fix2_share_pe_treatC/cf.f90 ]; then
    echo "diff against cf_fix2_share_pe_treatC:"; diff cf_fix2_share_pe_treatC/cf.f90 cf_fix2_share_pe_treatCu/cf.f90 || true
fi
echo "built $C/cf_fix2_share_pe_treatCu/hftf_cf_prod"
