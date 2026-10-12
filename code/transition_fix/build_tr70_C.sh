#!/bin/bash
# build_tr70_C.sh [OUT] -- THE PAPER'S T = 70 TRANSITION BINARY ON RULE C (12 October; RULE_C_PLAN.md workstream TR).
# transition_fix/tr70_src.f90 (the source of the paper's T = 70 run, code/remote_transition_2c_t70.sh), then
# treat/patch_treatC.py (rule C: a household with the disorder must be in treatment, nobody may use; the household's own
# treatment choice set at the two distribution call sites; the MILBY SPLIT print), then
# transition_fix/patch_cohort_print.py (print-only: TRANSITION ENTRANT_MASS_BY_PARENT_AGE / ENTRANT_VALUE_BY_PARENT_AGE,
# the cohort-born-at-the-reform print of code/transition_fix/remote_tr70_cohort.sh). The two patches touch disjoint
# anchors; each is checked to have landed. Compiled -O3 as the rule-A prod binary was. Default OUT: code/tr70_C.
set -e
C=$(cd "$(dirname "$0")/.." && pwd)
OUT=${1:-$C/tr70_C}
mkdir -p "$OUT"
python3 "$C/treat/patch_treatC.py" "$C/transition_fix/tr70_src.f90" "$OUT/tr_ruleC.f90"
python3 "$C/transition_fix/patch_cohort_print.py" "$OUT/tr_ruleC.f90" "$OUT/tr.f90"
n() { grep -c "$1" "$OUT/tr.f90" || true; }
[ "$(n 'RULE C (patch_treatC.py)')" = 1 ] || { echo "REFUSING: the rule-C screen line is not in the source ($(n 'RULE C (patch_treatC.py)'))"; exit 1; }
[ "$(n "THE HOUSEHOLD'S OWN TREATMENT CHOICE (patch_treatC.py)")" = 2 ] || { echo "REFUSING: the two treatment-choice call sites are not both patched"; exit 1; }
[ "$(n 'MILBY SPLIT voucher mass rec treat smi')" = 1 ] || { echo "REFUSING: no MILBY SPLIT print"; exit 1; }
[ "$(n 'TRANSITION MILBY t=')" = 1 ] || { echo "REFUSING: the first-year TRANSITION MILBY print is missing"; exit 1; }
[ "$(n 'TRANSITION ENTRANT_VALUE_BY_PARENT_AGE')" = 1 ] || { echo "REFUSING: the cohort print is not in the source"; exit 1; }
[ "$(n 'TRANSITION ENTRANT_MASS_BY_PARENT_AGE')" = 1 ] || { echo "REFUSING: the cohort mass print is not in the source"; exit 1; }
[ "$(n 'TRANSITION ALLALIVE')" -ge 1 ] || { echo "REFUSING: no TRANSITION ALLALIVE print (patch_transition_fix.py)"; exit 1; }
grep -q "parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*70 *$" "$OUT/tr.f90" \
    || { echo "REFUSING: not at transition_length 70"; exit 1; }
# the rule-C patch must change exactly the screen line and add the print and the call-site lines, nothing else
d=$(diff "$C/transition_fix/tr70_src.f90" "$OUT/tr_ruleC.f90" | grep -c '^<' || true)
[ "$d" = 1 ] || { echo "REFUSING: patch_treatC.py removed $d lines from tr70_src.f90, expected 1 (the screen line)"; exit 1; }
md5sum "$C/treat/patch_treatC.py" | cut -c1-32 > "$OUT/patch_treatC.md5"
( cd "$OUT" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium tr.f90 \
    -o hftf_tr_prod 2> build_prod.err )
[ -x "$OUT/hftf_tr_prod" ] && ! grep -q Error "$OUT/build_prod.err" || { echo "REFUSING: did not compile"; grep -m3 Error "$OUT/build_prod.err"; exit 1; }
echo "built $OUT/hftf_tr_prod $(md5sum "$OUT/hftf_tr_prod" | cut -c1-8) (rule C + cohort print, T = 70; patch_treatC.py $(cut -c1-8 "$OUT/patch_treatC.md5"))"
