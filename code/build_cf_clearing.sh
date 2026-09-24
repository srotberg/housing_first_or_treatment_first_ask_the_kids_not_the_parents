#!/bin/sh
# build_cf_clearing.sh [outdir]
#
# THE COUNTERFACTUAL BINARY WITH AN ENDOGENOUS DRUG PRICE.
#
# The author, 24 September: "you need to allow the drug price to be endogenous
# based on that elasticities". On the frozen scan path every counterfactual runs
# the BENCHMARK binary (is_counterfactual = 0, a compile-time parameter), and on
# that branch clear_drug_market re-normalises the supply shifter every block so
# the price stays at the benchmark's 1 at whatever quantity is consumed:
# drug_supply_elasticity 1.46 is set and does nothing. The clearing branch -- read
# the BENCHMARK's shifter, then move the price until the supply price at the
# quantity demanded equals the price faced -- sits in the else branch and was
# only reachable at is_counterfactual = 1.
#
# This generates a BUILD-DIRECTORY COPY with exactly four one-line changes. The
# tracked .f90 is never modified.
#
#   1. clear_drug_market: the `if (is_counterfactual==0)` that picks the
#      normalising branch becomes `if (.false.)`, so the clearing branch runs.
#      It reads drug_supply_shifterbaseline_benchmark.dat, which the run script
#      writes from the Housing First omega_c = 0.06 benchmark's own last block.
#   2. the drug_price_start handover: its `if (is_counterfactual==1)` becomes
#      `if (.true.)`, so a warm start is honoured rather than IGNORED.
#   3, 4. the two holder-testing guards build_tf_rationed.sh removes (32257,
#      32381). Inert whenever voucher_conditional_on_clean = 0 and the
#      homeless-addicted multiplier is 1, so one binary serves every arm.
#
# NOTHING ELSE. Every other is_counterfactual branch -- rental supply, the FMR
# standard, file names -- keeps its frozen-path behaviour, which is the path the
# Housing First benchmark was solved on.
#
# ASSERTED BY VALUE (ENGINE.md): each target is located by the text around it,
# must occur exactly once, must change, and the diff must contain nothing else.
set -e
S=$(cd "$(dirname "$0")" && pwd)
SRC=$S/housing_first_or_treatment_first_SR_v1.f90
OUT=${1:-$S/cfc}
GEN=$OUT/cfc.f90
mkdir -p "$OUT"

python3 - "$SRC" "$GEN" <<'PY'
import sys
src, gen = sys.argv[1], sys.argv[2]
L = open(src).read().split('\n')
def one(pred, what):
    hits = [i for i in range(len(L)) if pred(i)]
    if len(hits) != 1:
        sys.exit(f"GUARD: expected exactly 1 {what}, found {len(hits)} -- the source moved, look before building")
    return hits[0]
# 1. the normalising branch of clear_drug_market
i = one(lambda i: L[i].strip() == "if (is_counterfactual==0) then" and i+2 < len(L)
        and "Normalise: pick the shifter that puts the price at one here" in L[i+2],
        "normalising branch in clear_drug_market")
L[i] = L[i].replace("if (is_counterfactual==0) then", "if (.false.) then")
# 2. drug_price_start honoured on this path
j = one(lambda i: L[i].strip() == "if (is_counterfactual==1) then" and i+1 < len(L)
        and 'HANDOVER drug_price_start:' in L[i+1], "drug_price_start gate")
L[j] = L[j].replace("if (is_counterfactual==1) then", "if (.true.) then")
# 3, 4. the two holder-testing guards
for pat, new in [("(is_counterfactual==1) .AND. (fails_1==1) .AND.", "(fails_1==1) .AND."),
                 ("(is_counterfactual==1) .AND. (voucher_index_1==3) .AND.", "(voucher_index_1==3) .AND.")]:
    k = one(lambda i, p=pat: p in L[i], f"guard '{pat}'")
    L[k] = L[k].replace(pat, new)
open(gen, 'w').write('\n'.join(L))
print(f"edited lines: {i+1} {j+1} and the two guards")
PY

# the diff must be exactly four changed lines, and each must be one of ours
diff "$SRC" "$GEN" > "$OUT/expected.diff" || true
n_old=$(grep -c '^<' "$OUT/expected.diff"); n_new=$(grep -c '^>' "$OUT/expected.diff")
[ "$n_old" = 4 ] && [ "$n_new" = 4 ] || { echo "GUARD: expected 4 changed lines, got $n_old/$n_new"; cat "$OUT/expected.diff"; exit 1; }
stray=$(grep '^>' "$OUT/expected.diff" | grep -v 'if (\.false\.) then' | grep -v 'if (\.true\.) then' \
        | grep -Fv '(fails_1==1) .AND. &' | grep -Fv '(voucher_index_1==3) .AND. &' || true)
[ -z "$stray" ] || { echo "GUARD: unexpected change:"; echo "$stray"; exit 1; }
echo "diff asserted by value -- exactly the four intended lines:"
sed 's/^/    /' "$OUT/expected.diff"

COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$OUT"
if [ "${CFC_QUICK:-0}" != 1 ]; then
  echo "bounds..." ; gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON cfc.f90 -o cfc_bounds 2> build_bounds.err
  echo "snan..."   ; gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace $COMMON cfc.f90 -o cfc_snan 2> build_snan.err
fi
echo "prod..."   ; gfortran -O3 -funroll-loops $COMMON cfc.f90 -o cfc_prod 2> build_prod.err
for f in build_*.err; do
  e=$(grep -c "Error" "$f" || true); w=$(grep -c "Warning" "$f" || true)
  echo "  $f: $w warnings, $e errors (expect 7 and 0)"
  [ "$e" -gt 0 ] && { echo "BUILD ERRORS in $f"; head -20 "$f"; exit 1; }
done
echo "built in $OUT: cfc_prod (run this)"
