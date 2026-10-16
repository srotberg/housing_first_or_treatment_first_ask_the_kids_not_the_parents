#!/bin/bash
# build_CA100.sh -- COPY of build_C.sh (16 October) for the Costantini comparison at detection 1.00 under the CA rule:
# treat/patch_treatCAu.py (rule A's screen on rule C's build -- the disorder fails in treatment or not, any use fails --
# with the internal_computations fix ungated so the paths' Housing First years run the corrected Housing First's
# arithmetic) in place of treat/patch_treatC.py, guards on its markers, work directory work_CA100. build_C.sh follows.
# build_C.sh -- RULE-C COPY of revoked_2c/build.sh (12 October). The corrected transition source gets
# treat/patch_treatC.py (the rule-C screen, the household's own treatment choice at the model's two distribution call
# sites, the MILBY SPLIT print), then revoked_2c/patch_revoked_C.py (patch_revoked.py, and the same treatment choice
# at the shadow step's screen call). Work directory revoked_2c/work_C. Every patch is checked to have landed. The
# original's header follows.
# build.sh -- the revoked-voucher experiment's binaries (code/revoked_2c/README.md), all from the tracked source:
#   transition_fix/patch_transition_fix.py  (the corrected transition, the 176-line patch stage E runs)
#   revoked_2c/patch_revoked.py             (plain: + stop after loop 0; track: + the print-only revk_track module)
# then the transition switches exactly as transition_fix/build_transition_t10_copy.sh sets them, at the horizon asked.
#   [ONLY="track3 track10"] bash build.sh   -> work/plain3, work/track3, work/track10 (prod, -O3), work/track3b (bounds-checked)
set -e
R=$(cd "$(dirname "$0")" && pwd); C=$(cd "$R/.." && pwd); W=$R/work_CA100; mkdir -p "$W"; printf "*\n" > "$W/.gitignore"   # work_CA100 is never committed
python3 "$C/transition_fix/patch_transition_fix.py" "$C/housing_first_or_treatment_first_SR_v1.f90" "$W/tr_fix_src.f90"
n=$(diff "$C/housing_first_or_treatment_first_SR_v1.f90" "$W/tr_fix_src.f90" | grep -c '^[<>]' || true)
[ "$n" -eq 176 ] || { echo "REFUSING: transition patch diff is $n lines, expected 176"; exit 1; }
python3 "$C/treat/patch_treatCAu.py" "$W/tr_fix_src.f90" "$W/tr_fix_C.f90"
[ "$(grep -c 'RULE CA (patch_treatCA.py)' "$W/tr_fix_C.f90")" = 1 ] || { echo "REFUSING: rule CA screen missing"; exit 1; }
[ "$(grep -c 'RULE C (patch_treatC.py)' "$W/tr_fix_C.f90")" = 0 ] || { echo "REFUSING: rule C screen still present"; exit 1; }
grep -A1 '^ *if (unemployment_index>threshold_addiction_index) fails_1=1$' "$W/tr_fix_C.f90" | grep -q '^ *if (drug_share_1>0) fails_1=1$' \
    || { echo "REFUSING: the CA screen line (the disorder fails in treatment or not; any use fails) is not in the source"; exit 1; }
[ "$(grep -c 'INTERNAL UNGATED (patch_treatCAu.py' "$W/tr_fix_C.f90")" = 1 ] || { echo "REFUSING: internal_computations fix not ungated"; exit 1; }
grep -q 'integer :: tc2_abstain_on=0,' "$W/tr_fix_C.f90" || { echo "REFUSING: abstention not off"; exit 1; }
[ "$(grep -c "THE HOUSEHOLD'S OWN TREATMENT CHOICE (patch_treatC.py)" "$W/tr_fix_C.f90")" = 2 ] || { echo "REFUSING: treatment choice not at 2 sites"; exit 1; }
grep -q 'MILBY SPLIT' "$W/tr_fix_C.f90" || { echo "REFUSING: MILBY SPLIT missing"; exit 1; }
python3 "$R/patch_revoked_C.py" "$W/tr_fix_C.f90" "$W/revk_track.f90" "$W/revk_plain.f90"
[ "$(grep -c "THE HOUSEHOLD'S OWN TREATMENT CHOICE (patch_revoked_C.py" "$W/revk_track.f90")" = 1 ] || { echo "REFUSING: shadow treatment choice missing"; exit 1; }
grep -q 'module revk_track' "$W/revk_track.f90" || { echo "REFUSING: tracking module missing"; exit 1; }
n=$(diff "$W/tr_fix_C.f90" "$W/revk_plain.f90" | grep -c '^[<>]' || true)
[ "$n" -eq 3 ] || { echo "REFUSING: plain diff is $n lines, expected 3 (the stop)"; exit 1; }
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
build plain3  "$W/revk_plain.f90" 3  "-O3 -funroll-loops"
build track3  "$W/revk_track.f90" 3  "-O3 -funroll-loops"
build track10 "$W/revk_track.f90" 10 "-O3 -funroll-loops"
build track3b "$W/revk_track.f90" 3  "-O1 -fcheck=bounds,pointer -g -fbacktrace"
echo "all built"
