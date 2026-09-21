#!/bin/bash
# build_transition_nogf.sh [outdir] [T]
#
# The NO-GRANDFATHERING transition at any horizon: the CONTROL arm for
# build_transition_gf.sh. Four compile-time parameters are set and two asserted.
#
#   is_counterfactual                             0 -> 1
#   use_revenues_to_increase_voucher_probability   0 -> 1
#   solve_transition_dynamics                     0 -> 1
#   transition_length                            30 -> T (default 60)
#   grandfather_voucher_states                    0        ASSERTED, not set
#   window_distributions                          1        ASSERTED, not set
#
# THE TWO ARE ASSERTED BECAUSE THE SOURCE ALREADY CARRIES THEM. There is nothing
# to sed, and a sed that matches nothing exits 0 -- which `set -e` never sees, so
# it would build the grandfathered arm in silence. If either default ever moves,
# this refuses instead.
#
# ON THE HORIZON. The T>=60 requirement belongs to the GRANDFATHERED arm alone: it
# exists because the exempt cohort must die out before arm 3 is a valid terminal
# condition, and a household aged 26 at the reform reaches 85 at t=59. With nobody
# exempt that does not bind, so this arm is legitimate at any horizon -- which is
# exactly what makes a T=5 run of it a usable control for a T=5 run of the other.
#
# WRITTEN OUT RATHER THAN SED'D FROM ITS SIBLING. The first attempt generated this
# file by sed from build_transition_gf.sh, and deleting the grandfathering
# expression left a dangling backslash before a blank line -- so sed ran with its
# expressions and NO input file, read stdin, and hung for ten minutes. `bash -n`
# passed, because it is valid syntax that simply never returns.
set -e
SRC=${SRC:-$(cd "$(dirname "$0")" && pwd)/housing_first_or_treatment_first_SR_v1.f90}
OUT=${1:-$(pwd)/tr_nogf}
T=${2:-60}
case "$T" in ''|*[!0-9]*) echo "REFUSING: T must be a positive integer, got '$T'"; exit 1;; esac
mkdir -p "$OUT"

sed -e 's/integer, parameter :: is_counterfactual=0/integer, parameter :: is_counterfactual=1/' \
    -e 's/integer, parameter :: use_revenues_to_increase_voucher_probability=0/integer, parameter :: use_revenues_to_increase_voucher_probability=1/' \
    -e 's/integer, parameter :: solve_transition_dynamics=is_counterfactual\*0+(1-is_counterfactual)\*0/integer, parameter :: solve_transition_dynamics=1/' \
    -e "s/solve_transition_dynamics\\*30\$/solve_transition_dynamics*$T/" \
    "$SRC" > "$OUT/tr_nogf.f90"

n=$(diff "$SRC" "$OUT/tr_nogf.f90" | grep -c '^[<>]' || true)
if [ "$n" -ne 8 ]; then
  echo "REFUSING: expected exactly 4 changed lines (8 diff lines), got $n."
  diff "$SRC" "$OUT/tr_nogf.f90" | grep '^[<>]' || true
  exit 1
fi

assert () { grep -qE "$2" "$OUT/tr_nogf.f90" || { echo "REFUSING: $1"; exit 1; }; }
assert "is_counterfactual=1 is not set"                            'parameter :: is_counterfactual=1 *$'
assert "use_revenues_to_increase_voucher_probability=1 is not set"  'parameter :: use_revenues_to_increase_voucher_probability=1 *$'
assert "solve_transition_dynamics=1 is not set"                    'parameter :: solve_transition_dynamics=1 *$'
assert "transition_length is not solve_transition_dynamics*$T"     "parameter :: transition_length=.*solve_transition_dynamics\\*$T *\$"
assert "grandfather_voucher_states is not 0 -- this is the CONTROL arm" 'parameter :: grandfather_voucher_states=0 *$'
assert "window_distributions is not 1"                             'parameter :: window_distributions=1 *$'
echo "four set, two asserted (grandfathering at 0 -- the CONTROL arm):"
grep -nE 'parameter :: (is_counterfactual|use_revenues_to_increase_voucher_probability|solve_transition_dynamics|transition_length|grandfather_voucher_states|window_distributions)=' "$OUT/tr_nogf.f90" | sed 's/^/    /'

COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$OUT"
echo "bounds..."; gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace $COMMON tr_nogf.f90 -o hftf_trnogf_bounds 2> build_bounds.err
echo "snan..."  ; gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace $COMMON tr_nogf.f90 -o hftf_trnogf_snan 2> build_snan.err
echo "prod..."  ; gfortran -O3 -funroll-loops $COMMON tr_nogf.f90 -o hftf_trnogf_prod 2> build_prod.err
for f in build_bounds.err build_snan.err build_prod.err; do
  e=$(grep -c "Error" "$f" || true)
  [ "$e" -gt 0 ] && { echo "BUILD ERRORS in $f"; head -20 "$f"; exit 1; }
done
echo "built in $OUT: hftf_trnogf_prod (run this), hftf_trnogf_bounds, hftf_trnogf_snan"
echo "EXPECTED PEAK RSS: BELOW the grandfathered fit of 7.3+0.0967*T, since three"
echo "  voucher states rather than four is 1/1.306 on everything carrying the index."
