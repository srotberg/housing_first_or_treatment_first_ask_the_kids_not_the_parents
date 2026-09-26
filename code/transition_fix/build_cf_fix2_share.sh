#!/bin/bash
# cf_fix2 PLUS one write: after the counterfactual loop ends, the final statistics
# sweep has rebuilt newborn_parent_share from the converged distribution, and this
# saves it as newborn_parent_share_counter.dat (F30.15, the layout
# read_calibration_state and the transition read). Used for the NO-POLICY rerun, so
# the transition's t = 0 parent share is that run's own (TRANSITION_LESSONS 16).
# Nothing the run computes changes. Do NOT build while a solve is running.
set -e
C=$(cd "$(dirname "$0")/.." && pwd)
BASE=$C/cf_fix2/cf.f90; OUT=$C/cf_fix2_share; mkdir -p "$OUT"
python3 - "$BASE" "$OUT/cf.f90" <<'PYEOF'
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
anchor = ("        simulation_ended=1\n                \n"
          "        call calculate_homeownership_by_characteristics(transition_length)\n"
          "        call stationary_equilibrium_statistics(transition_length)            \n")
assert s.count(anchor) == 1, ("anchor not unique", s.count(anchor))
add = ("        open(unit=421,file=\"newborn_parent_share_counter.dat\",status='replace')\n"
       "            write(421,'(F30.15)') newborn_parent_share\n"
       "        close(421)\n"
       "        write(*,*) \"PARENT SHARE SAVED: clean housed=\", sum(newborn_parent_share(:,0,1)), &\n"
       "            \" disordered housed=\", sum(newborn_parent_share(:,1,1)), &\n"
       "            \" clean street=\", sum(newborn_parent_share(:,0,2)), &\n"
       "            \" disordered street=\", sum(newborn_parent_share(:,1,2))\n")
s = s.replace(anchor, anchor + add)
assert "unit=421" not in open(src).read()
open(dst, "w").write(s)
PYEOF
d=$(diff "$BASE" "$OUT/cf.f90" | grep -c '^[<>]' || true); [ "$d" -eq 7 ] || { echo "REFUSING: expected 7 diff lines, got $d"; exit 1; }
[ -n "$GEN_ONLY" ] && { echo "generated $OUT/cf.f90"; exit 0; }
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$OUT"
gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON cf.f90 -o hftf_cf_bounds 2> build_bounds.err
gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace $COMMON cf.f90 -o hftf_cf_snan 2> build_snan.err
gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err
for f in build_bounds.err build_snan.err build_prod.err; do echo "$OUT $f warnings=$(grep -c Warning $f) errors=$(grep -c Error $f)"; done
