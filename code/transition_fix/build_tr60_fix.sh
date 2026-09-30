#!/bin/bash
# build_tr60_fix.sh -- the T=60, no-grandfathering transition with the fixes of
# TRANSITION_LESSONS.md section 16 (patch_transition_fix.py), built by the
# tracked build_transition_t60.sh from the patched copy. Output: code/tr60_fix.
# Do NOT run while two steady-state solves are running: the three builds take
# the cores the solves are using.
set -e
S=$(cd "$(dirname "$0")" && pwd)
C=$(cd "$(dirname "$0")/.." && pwd)
python3 $S/patch_transition_fix.py $C/housing_first_or_treatment_first_SR_v1.f90 $S/tr_fix_src.f90
n=$(diff $C/housing_first_or_treatment_first_SR_v1.f90 $S/tr_fix_src.f90 | grep -c '^[<>]' || true)
[ "$n" -eq 176 ] || { echo "REFUSING: patch diff is $n lines, expected 176"; exit 1; }
SRC=$S/tr_fix_src.f90 bash $C/build_transition_t60.sh $C/tr60_fix
for f in build_bounds.err build_snan.err build_prod.err; do
  echo "$f: $(grep -c -i warning $C/tr60_fix/$f) warnings, $(grep -c Error $C/tr60_fix/$f) errors"
done
