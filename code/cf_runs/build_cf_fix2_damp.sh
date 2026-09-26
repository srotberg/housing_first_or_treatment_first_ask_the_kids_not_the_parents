#!/bin/bash
# PERMBAN=1 patches cf_fix2_permban into cf_fix2_damp_permban instead.
# cf_fix2 PLUS a damped parent-share update between passes. The newborn draw of pass k+1 uses
# the parents who died in pass k (ONE BLOCK OF LAG); at 70 per cent detection that map
# overshoots and cycles with period two (TF 70, passes 4-8: disordered housed share
# 0.01917 / 0.01905 alternating, drug use -28.4 / -28.9 per cent, moments change stuck at
# 3.6e-4 against 1e-4). The update becomes half the new share and half the one in use,
# which leaves the fixed point unchanged and removes the cycle. Not applied while the share
# in use is still the clean housed start-up default (no disordered parents), so a seeded
# run's first real share is taken whole. stationary_equilibrium_statistics runs once per
# pass inside the loop, so the damping acts once per pass. Do NOT build beside two solves.
set -e
C=$(cd "$(dirname "$0")/.." && pwd)
BASE=$C/cf_fix2${PERMBAN:+_permban}/cf.f90; OUT=$C/cf_fix2_damp${PERMBAN:+_permban}; mkdir -p "$OUT"
python3 - "$BASE" "$OUT/cf.f90" <<'PYEOF'
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
old = ("        if (sum(newborn_parent_share_acc(:,:,:))>10.d0**(-12)) then\n\n"
       "            newborn_parent_share(:,:,:)=newborn_parent_share_acc(:,:,:)/&\n"
       "                sum(newborn_parent_share_acc(:,:,:))\n\n"
       "        end if\n")
new = ("        if (sum(newborn_parent_share_acc(:,:,:))>10.d0**(-12)) then\n"
       "            if (sum(newborn_parent_share(:,1,:))>10.d0**(-12)) then\n"
       "                newborn_parent_share(:,:,:)=0.5d0*newborn_parent_share(:,:,:)+&\n"
       "                    0.5d0*newborn_parent_share_acc(:,:,:)/sum(newborn_parent_share_acc(:,:,:))\n"
       "            else\n"
       "                newborn_parent_share(:,:,:)=newborn_parent_share_acc(:,:,:)/&\n"
       "                    sum(newborn_parent_share_acc(:,:,:))\n"
       "            end if\n"
       "        end if\n")
assert s.count(old) == 1, ("anchor", s.count(old))
s = s.replace(old, new)
open(dst, "w").write(s)
PYEOF
d=$(diff "$BASE" "$OUT/cf.f90" | grep -c '^[<>]' || true); [ "$d" -eq 11 ] || { echo "REFUSING: expected 11 diff lines, got $d"; diff "$BASE" "$OUT/cf.f90"; exit 1; }
[ -n "$GEN_ONLY" ] && { echo "generated $OUT/cf.f90"; exit 0; }
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$OUT"
gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON cf.f90 -o hftf_cf_bounds 2> build_bounds.err
gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace $COMMON cf.f90 -o hftf_cf_snan 2> build_snan.err
gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err
for f in build_bounds.err build_snan.err build_prod.err; do echo "$OUT $f warnings=$(grep -c Warning $f) errors=$(grep -c Error $f)"; done
