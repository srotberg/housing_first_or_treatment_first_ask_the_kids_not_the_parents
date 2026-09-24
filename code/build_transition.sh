#!/bin/bash
# build_transition.sh [outdir]
#
# Builds the TRANSITION binary. is_counterfactual and solve_transition_dynamics
# are compile-time parameters, so the transition needs its own binary.
#
#   is_counterfactual         0 -> 1
#   solve_transition_dynamics 0 -> 1   (this alone sets transition_length to 75)
#   use_revenues_to_increase_voucher_probability 0 -> 1
#
# All three builds are made and all three must be clean. Run the -O3 one.
set -e
SRC=${SRC:-$(cd "$(dirname "$0")" && pwd)/housing_first_or_treatment_first_SR_v1.f90}
OUT=${1:-$(pwd)/tr}
mkdir -p "$OUT"

sed -e 's/integer, parameter :: is_counterfactual=0/integer, parameter :: is_counterfactual=1/' \
    -e 's/integer, parameter :: solve_transition_dynamics=.*/integer, parameter :: solve_transition_dynamics=1/' \
    -e "s/\(integer, parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*\)[0-9][0-9]*/\130/" \
    -e 's/integer, parameter :: use_revenues_to_increase_voucher_probability=0/integer, parameter :: use_revenues_to_increase_voucher_probability=1/' \
    "$SRC" > "$OUT/tr.f90"

# THE GUARD IS BY VALUE, NOT BY COUNT.
#
# Counting diff lines breaks the moment the SOURCE already carries a value this
# script sets. That happened when transition_length moved from 30 to 60: six of
# the seven transition build scripts refused, and build_transition.sh -- which
# had no horizon sed at all -- silently built a T=60 binary under its own T=30
# heading. A count cannot tell "already correct" from "no longer matches", and
# only one of those two is safe.
#
# So the switches are ASSERTED BY VALUE in the generated file, which is the rule
# this repository already applied to grandfather_voucher_states and
# window_distributions, and the diff is required to contain NOTHING BUT the
# parameter lines this script is allowed to touch.
stray=$(diff "$SRC" "$OUT/tr.f90" | grep '^[<>]' | \
        grep -vE 'parameter :: (is_counterfactual|use_revenues_to_increase_voucher_probability|solve_transition_dynamics|transition_length|grandfather_voucher_states|window_distributions)=' || true)
if [ -n "$stray" ]; then
  echo "REFUSING: the generated source differs from the tracked source outside"
  echo "  the switch lines this script is allowed to set:"
  echo "$stray"
  exit 1
fi

assert () { grep -qE "$2" "$OUT/tr.f90" || { echo "REFUSING: $1"; exit 1; }; }
assert "is_counterfactual=1 is not set"                            'parameter :: is_counterfactual=1 *$'
assert "use_revenues_to_increase_voucher_probability=1 is not set"  'parameter :: use_revenues_to_increase_voucher_probability=1 *$'
assert "solve_transition_dynamics=1 is not set"                    'parameter :: solve_transition_dynamics=1 *$'
assert "transition_length is not solve_transition_dynamics*30"    "parameter :: transition_length=.*solve_transition_dynamics[*]30 *\$"

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
echo "EXPECTED PEAK RSS at 75 periods: about 2.91 + 0.079*T GB; at T=30 about 10.0 GB."
echo "If it is far above that, the re-slotting is not doing what it claims."
