#!/bin/sh
# build_tf_rationed.sh [outdir]
#
# Builds the TREATMENT FIRST (rationed vouchers, every holder tested) binary: the tracked source with the
# `(is_counterfactual==1) .AND. ` guard removed from EXACTLY TWO branches, by
# sed into a BUILD-DIRECTORY COPY. The tracked .f90 is never modified -- other
# solves are live against it and the transition builds from it.
#
#   32257  the branch that puts a HOUSED household which fails the test into
#          category 3, so a voucher HOLDER is tested, not only an applicant.
#   32381  the branch giving a category-3 household the transition to drop to
#          no voucher. With include_voucher_exclusion=1 a caught holder goes to
#          voucher_excl rather than to 0, so this is not strictly needed; it is
#          removed anyway so the two branches stay consistent.
#
# Neither removal can disturb another run: both branches also require a TF
# switch (increased_prob_..._and_addicted==0, or voucher_conditional_on_clean==1),
# and every non-TF handover carries those at 1 and 0 respectively.
#
# ASSERTED BY VALUE, NEVER BY DIFF COUNT (ENGINE.md): each target line must lose
# the token, and the diff against the tracked source must contain nothing else.
set -e
S=$(cd "$(dirname "$0")" && pwd)
SRC=$S/housing_first_or_treatment_first_SR_v1.f90
OUT=${1:-$S/tfu}
GEN=$OUT/tfu.f90
mkdir -p "$OUT"

A='(is_counterfactual==1) .AND. (fails_1==1) .AND.'
B='(is_counterfactual==1) .AND. (voucher_index_1==3) .AND.'

for p in "$A" "$B"; do
  n=$(grep -Fc "$p" "$SRC" || true)
  [ "$n" = "1" ] || { echo "GUARD: expected exactly 1 occurrence of:"; echo "    $p"; echo "  got $n -- the source moved, look before building"; exit 1; }
done

sed -e 's/(is_counterfactual==1) \.AND\. (fails_1==1) \.AND\./(fails_1==1) .AND./' \
    -e 's/(is_counterfactual==1) \.AND\. (voucher_index_1==3) \.AND\./(voucher_index_1==3) .AND./' \
    "$SRC" > "$GEN"

# 1. the two target lines must no longer carry the token
grep -Fq "(fails_1==1) .AND. &" "$GEN"        || { echo "GUARD: 32257 was not rewritten"; exit 1; }
grep -Fq "(voucher_index_1==3) .AND. &" "$GEN" || { echo "GUARD: 32381 was not rewritten"; exit 1; }
grep -Fq "$A" "$GEN" && { echo "GUARD: 32257 still contains is_counterfactual"; exit 1; }
grep -Fq "$B" "$GEN" && { echo "GUARD: 32381 still contains is_counterfactual"; exit 1; }

# 2. the diff must contain NOTHING BUT those two lines. Print anything else.
diff "$SRC" "$GEN" | grep '^[<>]' > "$OUT/expected.diff" || true
stray=$(grep '^[<>]' "$OUT/expected.diff" \
        | grep -Fv "$A" | grep -Fv "$B" \
        | grep -Fv "(fails_1==1) .AND. &" | grep -Fv "(voucher_index_1==3) .AND. &" || true)
if [ -n "$stray" ]; then
  echo "GUARD: the diff touches lines other than the two intended. Offending lines:"
  echo "$stray"
  exit 1
fi
echo "diff asserted by value -- exactly the two guard removals:"
sed 's/^/    /' "$OUT/expected.diff"

COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$OUT"
echo "bounds..." ; gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON tfu.f90 -o tfu_bounds 2> build_bounds.err
echo "snan..."   ; gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace $COMMON tfu.f90 -o tfu_snan 2> build_snan.err
echo "prod..."   ; gfortran -O3 -funroll-loops $COMMON tfu.f90 -o tfu_prod 2> build_prod.err
for f in build_bounds.err build_snan.err build_prod.err; do
  e=$(grep -c "Error" "$f" || true); w=$(grep -c "Warning" "$f" || true)
  echo "  $f: $w warnings, $e errors (expect 7 and 0)"
  [ "$e" -gt 0 ] && { echo "BUILD ERRORS in $f"; head -20 "$f"; exit 1; }
done
echo "built in $OUT: tfu_prod (run this), tfu_bounds, tfu_snan"
