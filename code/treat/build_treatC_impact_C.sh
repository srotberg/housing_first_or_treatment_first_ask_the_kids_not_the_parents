#!/bin/bash
# build_treatC_impact_C.sh -- cf_fix2_treatC_impact: the RULE-C counterfactual build (treat/build_treatC.sh, i.e. cf_fix2
# + treat/patch_treatC.py) with fixed_to_benchmark_dis = 1, exactly as deter_2c/build_impact.sh makes cf_fix2_impact
# from cf_fix2. For the who-stops comparison on rule C (deter_2c/run_whostops_C.sh). The 'DIAG who stops' print is in
# the tracked model source, so it carries through; every patch is checked to have landed. Production binary only.
set -e
C=$(cd "$(dirname "$0")/.." && pwd)
cd "$C"
[ -f "$C/cf_fix2_treatC/cf.f90" ] || bash treat/build_treatC.sh
O=$C/cf_fix2_treatC_impact; mkdir -p "$O"
sed 's/^        integer, parameter :: fixed_to_benchmark_dis=0$/        integer, parameter :: fixed_to_benchmark_dis=1/' \
    "$C/cf_fix2_treatC/cf.f90" > "$O/cf.f90"
d=$(diff "$C/cf_fix2_treatC/cf.f90" "$O/cf.f90" | grep -c '^[<>]' || true)
[ "$d" -eq 2 ] || { echo "REFUSING: cf_fix2_treatC_impact expected 2 diff lines, got $d"; exit 1; }
f=$O/cf.f90
[ "$(grep -c 'RULE C (patch_treatC.py)' "$f")" = 1 ] || { echo "REFUSING: rule C screen missing"; exit 1; }
[ "$(grep -c "THE HOUSEHOLD'S OWN TREATMENT CHOICE (patch_treatC.py)" "$f")" = 2 ] || { echo "REFUSING: rule C treatment-choice fix not at 2 sites"; exit 1; }
grep -q 'MILBY SPLIT' "$f" || { echo "REFUSING: MILBY SPLIT print missing"; exit 1; }
grep -q 'DIAG who stops' "$f" || { echo "REFUSING: who-stops print missing"; exit 1; }
grep -q 'DIAG use by voucher state' "$f" || { echo "REFUSING: DIAG use line missing"; exit 1; }
grep -q '^        integer, parameter :: fixed_to_benchmark_dis=1$' "$f" || { echo "REFUSING: distribution not fixed"; exit 1; }
( cd "$O" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium \
    cf.f90 -o hftf_cf_prod 2> build_prod.err )
[ "$(grep -c Error "$O/build_prod.err" || true)" = 0 ] && [ -x "$O/hftf_cf_prod" ] || { echo "REFUSING: did not compile"; grep -m3 Error "$O/build_prod.err"; exit 1; }
echo "built $O/hftf_cf_prod (rule C, distribution fixed; all patches present)"
