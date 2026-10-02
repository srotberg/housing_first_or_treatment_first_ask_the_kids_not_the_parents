#!/bin/bash
# build.sh -- the cf_kid binary: code/cf_fix2/cf.f90 plus the newborn-value
# additions (cf_kid_additions.f90) and a one-line hook (make_source.py).
#
# It is the SAME model as cf_fix2 (and cf_fix2_share, which adds only a write):
# the hook replaces the counterfactual loop by a read of the arm's saved
# equilibrium, so the binary never solves and never saves over an arm.
#
#   sh code/cf_kid/build.sh            # regenerates cf.f90, builds hftf_cf_kid (-O3)
#   CHECK=1 sh code/cf_kid/build.sh    # also the bounds-checked build hftf_cf_kid_bounds
#
# Do NOT run while a solve is reading code/cf_fix2 (it only reads it, but the
# usual rule for build scripts in this repo holds).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
BASE=${BASE:-$HERE/../cf_fix2/cf.f90}
[ -s "$BASE" ] || { echo "GUARD: $BASE missing"; exit 1; }
python3 "$HERE/make_source.py" "$BASE" "$HERE/cf.f90"

# the diff against the base must be the hook (4 lines) plus the appended block
add=$(wc -l < "$HERE/cf_kid_additions.f90")
d=$(diff "$BASE" "$HERE/cf.f90" | grep -c '^>' || true)
r=$(diff "$BASE" "$HERE/cf.f90" | grep -c '^<' || true)
[ "$r" -eq 0 ] || { echo "REFUSING: $r lines of the base were changed or removed"; exit 1; }
[ "$d" -eq $((add + 4)) ] || [ "$d" -eq $((add + 5)) ] || { echo "REFUSING: expected $((add + 4)) added lines, got $d"; exit 1; }
echo "source: $d lines added to $(basename "$(dirname "$BASE")")/cf.f90, none changed"

COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$HERE"
# the module file is written to the build directory; keep it out of the repo root
t0=$(date +%s)
gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_kid 2> build_prod.err
e=$(grep -c "Error" build_prod.err || true); [ "$e" = 0 ] || { echo "BUILD ERRORS"; grep -A3 Error build_prod.err | head -40; exit 1; }
echo "built $HERE/hftf_cf_kid in $(( $(date +%s) - t0 )) s (warnings: $(grep -c Warning build_prod.err || true))"
if [ "$CHECK" = 1 ]; then
  gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON cf.f90 -o hftf_cf_kid_bounds 2> build_bounds.err
  e=$(grep -c "Error" build_bounds.err || true); [ "$e" = 0 ] || { echo "BOUNDS BUILD ERRORS"; exit 1; }
  echo "built $HERE/hftf_cf_kid_bounds"
fi
rm -f "$HERE"/*.mod
