#!/bin/bash
# build_share_treatCu.sh -- build_share_treatC.sh share with patch_treatCu.py (the internal_computations fix ungated, so
# Housing First runs it too): code/cf_fix2_share_treatCu. A diagnostic, 14 October.
set -e
C=$(cd "$(dirname "$0")/.." && pwd); cd "$C"
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
[ -f cf_fix2_share/cf.f90 ] || bash transition_fix/build_cf_fix2_share.sh
mkdir -p cf_fix2_share_treatCu
python3 treat/patch_treatCu.py cf_fix2_share/cf.f90 cf_fix2_share_treatCu/cf.f90
grep -q "INTERNAL UNGATED (patch_treatCu.py)" cf_fix2_share_treatCu/cf.f90 || { echo "REFUSING: the ungated fix did not land"; exit 1; }
( cd cf_fix2_share_treatCu && gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err )
[ "$(grep -c Error cf_fix2_share_treatCu/build_prod.err)" = 0 ] && [ -x cf_fix2_share_treatCu/hftf_cf_prod ] || { echo "REFUSING: cf_fix2_share_treatCu did not compile"; grep -m3 Error cf_fix2_share_treatCu/build_prod.err; exit 1; }
echo "built $C/cf_fix2_share_treatCu/hftf_cf_prod"
