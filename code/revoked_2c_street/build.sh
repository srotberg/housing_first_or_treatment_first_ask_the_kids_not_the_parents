#!/bin/bash
# build.sh -- the SMI x street split's binaries (code/revoked_2c_street/README.md). The same sources and switches as
# code/revoked_2c/build.sh (whose patched sources it regenerates), plus patch_street.py on the tracking copy:
#   work/plain3  (the control), work/track3 (the unsplit tracking, to show groups 1-4 are unchanged),
#   work/street3, work/street10 (the split tracking at T = 3 and T = 10). All -O3.
set -e
R=$(cd "$(dirname "$0")" && pwd); C=$(cd "$R/.." && pwd); W=$R/work; mkdir -p "$W"
python3 "$C/transition_fix/patch_transition_fix.py" "$C/housing_first_or_treatment_first_SR_v1.f90" "$W/tr_fix_src.f90"
n=$(diff "$C/housing_first_or_treatment_first_SR_v1.f90" "$W/tr_fix_src.f90" | grep -c '^[<>]' || true)
[ "$n" -eq 176 ] || { echo "REFUSING: transition patch diff is $n lines, expected 176"; exit 1; }
python3 "$C/revoked_2c/patch_revoked.py" "$W/tr_fix_src.f90" "$W/revk_track.f90" "$W/revk_plain.f90"
n=$(diff "$W/tr_fix_src.f90" "$W/revk_plain.f90" | grep -c '^[<>]' || true)
[ "$n" -eq 3 ] || { echo "REFUSING: plain diff is $n lines, expected 3 (the stop)"; exit 1; }
python3 "$R/patch_street.py" "$W/revk_track.f90" "$W/revk_street.f90"
# the split touches only the module: no line outside 'module revk_track ... end module revk_track' may differ
python3 - "$W/revk_track.f90" "$W/revk_street.f90" <<'PY'
import sys
a, b = (open(p).read() for p in sys.argv[1:3])
cut = lambda s: s[:s.index('    module revk_track\n')] + s[s.index('    end module revk_track\n'):]
assert cut(a) == cut(b), "REFUSING: the street split changes a line outside the tracking module"
print("split confined to the tracking module")
PY
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
build() {   # <name> <source> <T> <flags>
    case " ${ONLY:-$1} " in *" $1 "*) ;; *) echo "skipped $1 (ONLY=$ONLY)"; return 0 ;; esac
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
build plain3 "$W/revk_plain.f90" 3  "-O3 -funroll-loops"
build track3 "$W/revk_track.f90" 3  "-O3 -funroll-loops"
build street3  "$W/revk_street.f90" 3  "-O3 -funroll-loops"
build street10 "$W/revk_street.f90" 10 "-O3 -funroll-loops"
echo "all built"
