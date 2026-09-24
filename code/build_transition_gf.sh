#!/bin/bash
# build_transition_gf.sh [outdir] [T]
#
# THE GRANDFATHERED TRANSITION AT T=60. Five compile-time parameters, and the
# script REFUSES unless the diff is exactly five lines, on build_transition.sh's
# own pattern: a renamed or already-set parameter is a silent wrong build.
#
#   is_counterfactual                             0 -> 1
#   use_revenues_to_increase_voucher_probability   0 -> 1
#   solve_transition_dynamics                     0 -> 1
#   transition_length                            30 -> T (default 60)
#   grandfather_voucher_states                    0 -> 1
#
# window_distributions is ALREADY 1 in the source and is asserted, not sed'd.
#
# WHY T=60 AND NOT LESS. The exempt cohort must die out before arm 3 is a valid
# terminal condition. A household aged 26 at the reform reaches 85 at t=59. At
# any shorter horizon the grandfathered are still alive at the terminal date and
# the boundary condition is wrong.
#
# WHY NOT build_transition.sh. That script sets three of the five and guards on
# a diff of exactly three, so it cannot be told to do this; and the horizon it
# would leave standing is the source's 30.
set -e
SRC=${SRC:-$(cd "$(dirname "$0")" && pwd)/housing_first_or_treatment_first_SR_v1.f90}
OUT=${1:-$(pwd)/tr_gf}
# THE HORIZON. 60 is the run; 3 or 5 is the probe the lessons file requires in
# front of an overnight one, and which also re-checks the memory model.
T=${2:-60}
case "$T" in ''|*[!0-9]*) echo "REFUSING: T must be a positive integer, got '$T'"; exit 1;; esac
mkdir -p "$OUT"

sed -e 's/integer, parameter :: is_counterfactual=0/integer, parameter :: is_counterfactual=1/' \
    -e 's/integer, parameter :: use_revenues_to_increase_voucher_probability=0/integer, parameter :: use_revenues_to_increase_voucher_probability=1/' \
    -e 's/integer, parameter :: solve_transition_dynamics=.*/integer, parameter :: solve_transition_dynamics=1/' \
    -e "s/\(integer, parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*\)[0-9][0-9]*/\1$T/" \
    -e 's/integer, parameter :: grandfather_voucher_states=0/integer, parameter :: grandfather_voucher_states=1/' \
    "$SRC" > "$OUT/tr_gf.f90"

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
stray=$(diff "$SRC" "$OUT/tr_gf.f90" | grep '^[<>]' | \
        grep -vE 'parameter :: (is_counterfactual|use_revenues_to_increase_voucher_probability|solve_transition_dynamics|transition_length|grandfather_voucher_states|window_distributions|grandfather_voucher_states)=' || true)
if [ -n "$stray" ]; then
  echo "REFUSING: the generated source differs from the tracked source outside"
  echo "  the switch lines this script is allowed to set:"
  echo "$stray"
  exit 1
fi

# EVERY ONE OF THE SIX ASSERTED IN THE GENERATED SOURCE, not inferred from the
# sed exit status -- a sed that matches nothing succeeds.
assert () { grep -qE "$2" "$OUT/tr_gf.f90" || { echo "REFUSING: $1 is not set in the generated source"; exit 1; }; }
assert "is_counterfactual=1"                             'parameter :: is_counterfactual=1 *$'
assert "use_revenues_to_increase_voucher_probability=1"   'parameter :: use_revenues_to_increase_voucher_probability=1 *$'
assert "solve_transition_dynamics=1"                     'parameter :: solve_transition_dynamics=1 *$'
assert "transition_length ... *$T"                       "parameter :: transition_length=.*solve_transition_dynamics\\*$T *\$"
assert "grandfather_voucher_states=1"                    'parameter :: grandfather_voucher_states=1 *$'
assert "window_distributions=1"                          'parameter :: window_distributions=1 *$'
echo "all six switches asserted in the generated source:"
grep -nE 'parameter :: (is_counterfactual|use_revenues_to_increase_voucher_probability|solve_transition_dynamics|transition_length|grandfather_voucher_states|window_distributions)=' "$OUT/tr_gf.f90" | sed 's/^/    /'

COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$OUT"
echo "bounds..."; gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON tr_gf.f90 -o hftf_trgf_bounds 2> build_bounds.err
echo "snan..."  ; gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace $COMMON tr_gf.f90 -o hftf_trgf_snan 2> build_snan.err
echo "prod..."  ; gfortran -O3 -funroll-loops $COMMON tr_gf.f90 -o hftf_trgf_prod 2> build_prod.err
for f in build_bounds.err build_snan.err build_prod.err; do
  e=$(grep -c "Error" "$f" || true)
  [ "$e" -gt 0 ] && { echo "BUILD ERRORS in $f"; head -20 "$f"; exit 1; }
done
echo "built in $OUT: hftf_trgf_prod (run this), hftf_trgf_bounds, hftf_trgf_snan"
# THE MEMORY PREDICTION, from the two figures grandfather_voucher_states'
# declaration actually measured -- T=30 at 10.2 GB and T=60 at 13.1 GB with the
# fourth voucher state. Those two give 7.3 + 0.0967*T GB; the intercept is large
# because the steady-state copies and the one working slice of each policy do not
# carry a transition dimension and still pay the 1.306x.
#
# Do NOT use the lessons file's 2.91 + 0.079*T here. That is the THREE-state
# build's fit, it predicts 9.1 GB at T=60 against a measured 13.1, and scaling
# only its slope by 1.306 is the mistake -- the T-independent term scales too.
python3 - "$T" <<'PY'
import sys
T=int(sys.argv[1]); print("EXPECTED PEAK RSS at T=%d: about %.2f GB of 15 (fit 7.3 + 0.0967*T," % (T,7.3+0.0967*T))
print("  from the two measured points T=30 -> 10.2 GB and T=60 -> 13.1 GB).")
print("  Far above it and the re-slotting is not doing what it claims.")
PY
