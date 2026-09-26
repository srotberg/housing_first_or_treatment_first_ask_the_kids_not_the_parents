#!/bin/bash
# cf_fix PLUS a pi_V update that (1) ignores pass 1, whose budget is contaminated by the
# pass-1 parent-share artefact (newborn_parent_share (1,0,0,0) until the first update), and
# (2) starts its step at 0.12 (about 1/slope; the budget answers pi_V at roughly -9 in TF) and
# still halves it on each sign change (floor 0.05/8). Without (1) the artefact's surplus pushes
# pi_V up in pass 1, pass 2's deficit flips the sign, the step halves to 0.025 and pi_V crawls
# (cf_fix TF runs, 26 September: about 0.001 a pass against a deficit of 0.04). PERMBAN=1 patches
# cf_fix_permban instead. Source untouched. All three builds.
set -e
CODE=$(cd "$(dirname "$0")/.." && pwd)
BASE=$CODE/cf_fix${PERMBAN:+_permban}/cf.f90; OUT=$CODE/cf_fix2${PERMBAN:+_permban}; mkdir -p "$OUT"
python3 - "$BASE" "$OUT/cf.f90" <<'PYEOF'
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, ("not exactly once", old)
    s = s.replace(old, new)
rep("        real(8) :: pv_gain_1=0.05d0,pv_last_gap_1=0.d0,pv_gap_now_1\n        integer :: pv_have_gap_1=0\n",
    "        real(8) :: pv_gain_1=0.12d0,pv_last_gap_1=0.d0,pv_gap_now_1\n        integer :: pv_have_gap_1=0,pv_pass_1=0\n")
rep("                            pv_gap_now_1=net_govt_revenues(transition_length)-net_govt_revenue_constraint\n"
    "                            if ((pv_have_gap_1==1) .AND. (pv_gap_now_1*pv_last_gap_1<0.d0)) pv_gain_1=max(0.5d0*pv_gain_1,0.05d0/8.d0)\n"
    "                            pv_last_gap_1=pv_gap_now_1\n"
    "                            pv_have_gap_1=1\n",
    "                            pv_gap_now_1=net_govt_revenues(transition_length)-net_govt_revenue_constraint\n"
    "                            pv_pass_1=pv_pass_1+1\n"
    "                            if ((pv_pass_1>=2) .AND. (pv_have_gap_1==1) .AND. (pv_gap_now_1*pv_last_gap_1<0.d0)) pv_gain_1=max(0.5d0*pv_gain_1,0.05d0/8.d0)\n"
    "                            if (pv_pass_1>=2) pv_last_gap_1=pv_gap_now_1\n"
    "                            if (pv_pass_1>=2) pv_have_gap_1=1\n")
rep("                                pv_gain_1*pv_gap_now_1,1.d0),0.d0)\n",
    "                                merge(1.d0,0.d0,pv_pass_1>=2)*pv_gain_1*pv_gap_now_1,1.d0),0.d0)\n")
rep('                            write(*,*) "PV STEP: gap=", pv_gap_now_1, " gain=", pv_gain_1\n',
    '                            write(*,*) "PV STEP: gap=", pv_gap_now_1, " gain=", pv_gain_1, " pass=", pv_pass_1\n')
open(dst, "w").write(s)
PYEOF
d=$(diff "$BASE" "$OUT/cf.f90" | grep -c '^[<>]' || true); [ "$d" -eq 15 ] || { echo "REFUSING: expected 15 diff lines, got $d"; diff "$BASE" "$OUT/cf.f90"; exit 1; }
[ -n "$GEN_ONLY" ] && { echo "generated $OUT/cf.f90"; exit 0; }
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$OUT"
gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON cf.f90 -o hftf_cf_bounds 2> build_bounds.err
gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace $COMMON cf.f90 -o hftf_cf_snan 2> build_snan.err
gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err
for f in build_bounds.err build_snan.err build_prod.err; do echo "$OUT $f warnings=$(grep -c Warning $f) errors=$(grep -c Error $f)"; done
