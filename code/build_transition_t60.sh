#!/bin/bash
# build_transition_t60.sh [outdir]
#
# Builds the TRANSITION binary at T=60, NO GRANDFATHERING, windowed.
#
# This is build_transition.sh plus the horizon, and with the two switches that
# define the arm ASSERTED rather than set: grandfather_voucher_states and
# window_distributions already carry the values this arm needs, and a sed that
# silently matches nothing is the failure mode that rule exists to catch. They
# are checked by value in the generated file, so if either ever moves in the
# source this refuses instead of building the other arm.
#
#   is_counterfactual                             0 -> 1
#   use_revenues_to_increase_voucher_probability  0 -> 1
#   solve_transition_dynamics                     0 -> 1
#   transition_length                            30 -> 60   (the horizon)
#   grandfather_voucher_states                    0         ASSERTED
#   window_distributions                          1         ASSERTED
#
# All three builds are made and all three must be clean. Run the -O3 one.
set -e
SRC=${SRC:-$(cd "$(dirname "$0")" && pwd)/housing_first_or_treatment_first_SR_v1.f90}
OUT=${1:-$(pwd)/tr60}
mkdir -p "$OUT"

sed -e 's/integer, parameter :: is_counterfactual=0/integer, parameter :: is_counterfactual=1/' \
    -e 's/integer, parameter :: use_revenues_to_increase_voucher_probability=0/integer, parameter :: use_revenues_to_increase_voucher_probability=1/' \
    -e 's/integer, parameter :: solve_transition_dynamics=is_counterfactual\*0+(1-is_counterfactual)\*0/integer, parameter :: solve_transition_dynamics=1/' \
    -e 's/integer, parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*30/integer, parameter :: transition_length=(1-solve_transition_dynamics)*1+solve_transition_dynamics*60/' \
    "$SRC" > "$OUT/tr.f90"

n=$(diff "$SRC" "$OUT/tr.f90" | grep -c '^[<>]' || true)
if [ "$n" -ne 8 ]; then
  echo "REFUSING: expected exactly 4 changed lines (8 diff lines), got $n."
  echo "  Either a parameter was renamed or one is already set. Look before building."
  exit 1
fi

# THE TWO ASSERTED SWITCHES. Checked in the GENERATED file, by value.
g=$(grep -c "integer, parameter :: grandfather_voucher_states=0" "$OUT/tr.f90" || true)
w=$(grep -c "integer, parameter :: window_distributions=1" "$OUT/tr.f90" || true)
[ "$g" -eq 1 ] || { echo "REFUSING: grandfather_voucher_states is not 0. This is the NO-GRANDFATHERING arm."; exit 1; }
[ "$w" -eq 1 ] || { echo "REFUSING: window_distributions is not 1. T=60 does not fit unwindowed."; exit 1; }
echo "asserted: grandfather_voucher_states=0 (no grandfathering), window_distributions=1"

echo "transition_length will be:"
grep -m1 "parameter :: transition_length" "$OUT/tr.f90" | sed 's/^/    /'

COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$OUT"
echo "bounds..."; gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON tr.f90 -o hftf_tr_bounds 2> build_bounds.err
echo "snan..."  ; gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace $COMMON tr.f90 -o hftf_tr_snan 2> build_snan.err
echo "prod..."  ; gfortran -O3 -funroll-loops $COMMON tr.f90 -o hftf_tr_prod 2> build_prod.err
for f in build_bounds.err build_snan.err build_prod.err; do
  e=$(grep -c "Error" "$f" || true)
  [ "$e" -gt 0 ] && { echo "BUILD ERRORS in $f"; head -20 "$f"; exit 1; }
done
echo "built in $OUT: hftf_tr_prod (run this), hftf_tr_bounds, hftf_tr_snan"
echo
echo "EXPECTED PEAK RSS: about 2.91 + 0.079*T GB; at T=60 about 7.7 GB (the"
echo "brief's figure is 10.0 GB of 15). If it is far above that, the"
echo "re-slotting is not doing what TRANSITION_LESSONS claims."
