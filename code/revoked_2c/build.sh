#!/bin/bash
# build.sh -- the revoked-voucher experiment's binaries (code/revoked_2c/README.md), all from the tracked source:
#   transition_fix/patch_transition_fix.py  (the corrected transition, the 176-line patch stage E runs)
#   revoked_2c/patch_revoked.py             (plain: + stop after loop 0; track: + the print-only revk_track module)
# then the transition switches exactly as transition_fix/build_transition_t10_copy.sh sets them, at the horizon asked.
#   bash build.sh                 -> work/plain3, work/track3, work/track10 (prod, -O3), work/track3b (bounds-checked)
set -e
R=$(cd "$(dirname "$0")" && pwd); C=$(cd "$R/.." && pwd); W=$R/work; mkdir -p "$W"
python3 "$C/transition_fix/patch_transition_fix.py" "$C/housing_first_or_treatment_first_SR_v1.f90" "$W/tr_fix_src.f90"
n=$(diff "$C/housing_first_or_treatment_first_SR_v1.f90" "$W/tr_fix_src.f90" | grep -c '^[<>]' || true)
[ "$n" -eq 176 ] || { echo "REFUSING: transition patch diff is $n lines, expected 176"; exit 1; }
python3 "$R/patch_revoked.py" "$W/tr_fix_src.f90" "$W/revk_track.f90" "$W/revk_plain.f90"
n=$(diff "$W/tr_fix_src.f90" "$W/revk_plain.f90" | grep -c '^[<>]' || true)
[ "$n" -eq 3 ] || { echo "REFUSING: plain diff is $n lines, expected 3 (the stop)"; exit 1; }
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
build() {   # <name> <source> <T> <flags>
    O=$W/$1; mkdir -p "$O"
    sed -e 's/integer, parameter :: is_counterfactual=0/integer, parameter :: is_counterfactual=1/' \
        -e 's/integer, parameter :: use_revenues_to_increase_voucher_probability=0/integer, parameter :: use_revenues_to_increase_voucher_probability=1/' \
        -e 's/integer, parameter :: solve_transition_dynamics=.*/integer, parameter :: solve_transition_dynamics=1/' \
        -e "s/\(integer, parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*\)[0-9][0-9]*/\1$3/" \
        "$2" > "$O/tr.f90"
    stray=$(diff "$2" "$O/tr.f90" | grep '^[<>]' | grep -vE 'parameter :: (is_counterfactual|use_revenues_to_increase_voucher_probability|solve_transition_dynamics|transition_length)=' || true)
    [ -z "$stray" ] || { echo "REFUSING: stray diff in $1: $stray"; exit 1; }
    grep -qE "parameter :: transition_length=.*solve_transition_dynamics[*]$3 *\$" "$O/tr.f90" || { echo "REFUSING: T not $3 in $1"; exit 1; }
    grep -q "integer, parameter :: grandfather_voucher_states=0" "$O/tr.f90" || { echo "REFUSING: grandfathering on"; exit 1; }
    grep -q "integer, parameter :: window_distributions=1" "$O/tr.f90" || { echo "REFUSING: not windowed"; exit 1; }
    ( cd "$O" && gfortran $4 $COMMON tr.f90 -o hftf_tr 2> build.err ) || { echo "BUILD FAILED $1"; head -30 "$O/build.err"; exit 1; }
    echo "built $1 (T=$3, $4): $(grep -c -i warning "$O/build.err") warnings"
}
build plain3  "$W/revk_plain.f90" 3  "-O3 -funroll-loops"
build track3  "$W/revk_track.f90" 3  "-O3 -funroll-loops"
build track10 "$W/revk_track.f90" 10 "-O3 -funroll-loops"
build track3b "$W/revk_track.f90" 3  "-O1 -fcheck=bounds,pointer -g -fbacktrace"
echo "all built"
