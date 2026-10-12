#!/bin/bash
# build_C.sh [OUT] -- the cf_kid binary for a RULE-C arm (12 October; code/treat/patch_treatC.py). A copy of build.sh with
# two differences, so the newborn values of the rule-C Treatment First arm are computed under the arm's own law of motion:
#   1. the base is code/cf_fix2_treatC/cf.f90 (rule C's screen) instead of code/cf_fix2/cf.f90;
#   2. cf_kid_additions.f90's one screen call (compute_voucher_index_1 in the backward pass) is preceded by
#      treatment_choice_now = the household's own treatment policy and followed by treatment_choice_now = 0, as
#      patch_treatC.py does at the law of motion's two call sites. cf_kid's header says it mirrors the law of motion
#      by setting it to 0, which is right on cf_fix2 and wrong on rule C, where the law of motion sets it.
# Writes code/cf_kid_C/ (cf.f90, the patched additions, hftf_cf_kid); build.sh and code/cf_kid/ are not touched.
# Use with run_child_value.sh: BIN=code/cf_kid_C/hftf_cf_kid FORCE_BUILD=1 (the arm's BUILD_USED is cf_fix2_treatC).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
CODE=$(cd "$HERE/.." && pwd)
OUT=${1:-$CODE/cf_kid_C}
BASE=$CODE/cf_fix2_treatC/cf.f90
[ -s "$BASE" ] || { echo "GUARD: $BASE missing (bash code/treat/build_treatC.sh)"; exit 1; }
grep -q "RULE C (patch_treatC.py)" "$BASE" || { echo "GUARD: $BASE is not rule C"; exit 1; }
mkdir -p "$OUT"
cp "$HERE/make_source.py" "$OUT/make_source.py"
python3 - "$HERE/cf_kid_additions.f90" "$OUT/cf_kid_additions.f90" <<'PYEOF'
import sys
s = open(sys.argv[1]).read()
call = ("                                call compute_voucher_index_1(ish_l,&\n"
        "                                    policy_function_frac_spent_on_addiction(1)%vector_transition_real&\n"
        "                                    (1,j_1,fin_1,u_1,e_1,h_1,v_1),vidx_l)\n")
assert s.count(call) == 1, s.count(call)
s = s.replace(call,
    "                                ! RULE C (cf_kid/build_C.sh): the household's own treatment choice, as the law of motion\n"
    "                                treatment_choice_now=trt_l\n" + call +
    "                                treatment_choice_now=0\n")
open(sys.argv[2], 'w').write(s)
PYEOF
python3 "$OUT/make_source.py" "$BASE" "$OUT/cf.f90"
add=$(wc -l < "$OUT/cf_kid_additions.f90")
d=$(diff "$BASE" "$OUT/cf.f90" | grep -c '^>' || true)
r=$(diff "$BASE" "$OUT/cf.f90" | grep -c '^<' || true)
[ "$r" -eq 0 ] || { echo "REFUSING: $r lines of the base were changed or removed"; exit 1; }
[ "$d" -eq $((add + 4)) ] || [ "$d" -eq $((add + 5)) ] || { echo "REFUSING: expected $((add + 4)) added lines, got $d"; exit 1; }
[ "$(grep -c 'treatment_choice_now=trt_l' "$OUT/cf.f90")" = 1 ] || { echo "REFUSING: the treatment line is not in the source"; exit 1; }
echo "source: $d lines added to cf_fix2_treatC/cf.f90, none changed"
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$OUT"
t0=$(date +%s)
gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_kid 2> build_prod.err
e=$(grep -c "Error" build_prod.err || true); [ "$e" = 0 ] || { echo "BUILD ERRORS"; grep -A3 Error build_prod.err | head -40; exit 1; }
echo "built $OUT/hftf_cf_kid in $(( $(date +%s) - t0 )) s (warnings: $(grep -c Warning build_prod.err || true))"
rm -f "$OUT"/*.mod
