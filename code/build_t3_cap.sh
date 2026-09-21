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
    -e 's/integer, parameter :: solve_transition_dynamics=is_counterfactual\*0+(1-is_counterfactual)\*0/integer, parameter :: solve_transition_dynamics=1/' \
    -e 's/integer, parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*30/integer, parameter :: transition_length=(1-solve_transition_dynamics)*1+solve_transition_dynamics*3/' \
    -e "s/real(8), parameter :: max_drug_price_move=0.005/real(8), parameter :: max_drug_price_move=$CAP/" \
    "$SRC" > "$OUT/tr.f90"

n=$(diff "$SRC" "$OUT/tr.f90" | grep -c '^[<>]' || true)
exp=10
[ "$CAP" = "0.005" ] && exp=8      # the control changes the cap to itself: no diff line
if [ "$n" -ne "$exp" ]; then
  echo "REFUSING: expected $exp diff lines for cap=$CAP, got $n."; exit 1
fi
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
