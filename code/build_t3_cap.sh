#!/bin/bash
# build_t3_cap.sh <cap>
#
# T=3, NO GRANDFATHERING, with max_drug_price_move set to <cap>. The author,
# 21 September: "test the cap at 0.01 and 0.02 on T=3", and the standing rule
# that transition tests are done at T=3 "so that it is quick to check".
#
# The cap is the whole question. Measured on the T=45: the price step is
# EXACTLY -0.500 per cent in every period of every loop, so 0.005 binds 100 per
# cent of the time and the secant inside clear_drug_market never expresses
# itself. The source's reason for a cap is real -- the map is expansive, slope
# -2.25 at t=1 falling to -7.8 by t=28, so a raw step diverges -- but 0.005 was
# sized for a four-minute steady-state loop, not a 4.7-hour transition one.
set -e
CAP=${1:?usage: build_t3_cap.sh <cap>}
S=$(cd "$(dirname "$0")" && pwd)
SRC=$S/housing_first_or_treatment_first_SR_v1.f90
OUT=${2:-$S/tr3_cap$CAP}
mkdir -p "$OUT"

sed -e 's/integer, parameter :: is_counterfactual=0/integer, parameter :: is_counterfactual=1/' \
    -e 's/integer, parameter :: use_revenues_to_increase_voucher_probability=0/integer, parameter :: use_revenues_to_increase_voucher_probability=1/' \
    -e 's/integer, parameter :: solve_transition_dynamics=.*/integer, parameter :: solve_transition_dynamics=1/' \
    -e "s/\(integer, parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*\)[0-9][0-9]*/\13/" \
    -e "s/real(8), parameter :: max_drug_price_move=0.005/real(8), parameter :: max_drug_price_move=$CAP/" \
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
        grep -vE 'parameter :: (is_counterfactual|use_revenues_to_increase_voucher_probability|solve_transition_dynamics|transition_length|grandfather_voucher_states|window_distributions|max_drug_price_move)=' || true)
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
assert "transition_length is not solve_transition_dynamics*3"    "parameter :: transition_length=.*solve_transition_dynamics[*]3 *\$"
grep -m1 "parameter :: transition_length" "$OUT/tr.f90" | sed 's/^/    /'
grep -m1 "parameter :: max_drug_price_move" "$OUT/tr.f90" | sed 's/^/    /'
g=$(grep -c "integer, parameter :: grandfather_voucher_states=0" "$OUT/tr.f90" || true)
w=$(grep -c "integer, parameter :: window_distributions=1" "$OUT/tr.f90" || true)
[ "$g" -eq 1 ] || { echo "REFUSING: grandfathering is not off"; exit 1; }
[ "$w" -eq 1 ] || { echo "REFUSING: windowing is not on"; exit 1; }

COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
cd "$OUT"
gfortran -O3 -funroll-loops $COMMON tr.f90 -o hftf 2> build.err
e=$(grep -c "Error" build.err || true)
[ "$e" -gt 0 ] && { echo "BUILD ERRORS"; head -20 build.err; exit 1; }
echo "built $OUT/hftf   warnings: $(grep -c Warning build.err || true)"
