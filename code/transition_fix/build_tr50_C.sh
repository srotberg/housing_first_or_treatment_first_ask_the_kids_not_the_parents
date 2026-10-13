#!/bin/bash
# build_tr50_C.sh [OUT] -- build_tr70_C2.sh at T = 50 (13 October; the author: "for the old rule A we know T had to be
# 70...50 was not enough", "but here we can probably use T=50"). The same source and patches, then transition_length
# 70 -> 50, checked. remote_tr50_C.sh checks the horizon after the fact (the last ten years of the price and pi_V paths
# flat). Default OUT: code/tr50_C. build_tr70_C2.sh's header follows.
# build_tr70_C2.sh [OUT] -- build_tr70_C.sh with treat/patch_treatC2.py in place of patch_treatC.py (12 October): rule C plus
# the abstention option for a treated household with the disorder, the EV table keyed on the voucher category, the
# internal grid with the household's own treatment, use counted as v>0 and the ABSTAIN print. The transition's household
# problem is renter_to_renter_problem in tr70_src.f90, the same routine as the steady state's in its own copy of the source,
# so the same patch applies; its user rule has 3 sites to the steady state's 6. A new file; build_tr70_C.sh untouched.
# Default OUT: code/tr70_C2. build_tr70_C.sh's header follows.
# build_tr70_C.sh [OUT] -- THE PAPER'S T = 70 TRANSITION BINARY ON RULE C (12 October; RULE_C_PLAN.md workstream TR).
# transition_fix/tr70_src.f90 (the source of the paper's T = 70 run, code/remote_transition_2c_t70.sh), then
# treat/patch_treatC.py (rule C: a household with the disorder must be in treatment, nobody may use; the household's own
# treatment choice set at the two distribution call sites; the MILBY SPLIT print), then
# transition_fix/patch_cohort_print.py (print-only: TRANSITION ENTRANT_MASS_BY_PARENT_AGE / ENTRANT_VALUE_BY_PARENT_AGE,
# the cohort-born-at-the-reform print of code/transition_fix/remote_tr70_cohort.sh). The two patches touch disjoint
# anchors; each is checked to have landed. Compiled -O3 as the rule-A prod binary was. Default OUT: code/tr70_C.
set -e
C=$(cd "$(dirname "$0")/.." && pwd)
OUT=${1:-$C/tr50_C}
mkdir -p "$OUT"
python3 "$C/treat/patch_treatC2.py" "$C/transition_fix/tr70_src.f90" "$OUT/tr_ruleC.f90"
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
    || { echo "REFUSING: the source is not at transition_length 70 before the change"; exit 1; }
sed -i 's/\(parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*\)70 *$/\150/' "$OUT/tr.f90"
grep -q "parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*50$" "$OUT/tr.f90" \
    || { echo "REFUSING: not at transition_length 50"; exit 1; }
[ "$(grep -c "solve_transition_dynamics\*70" "$OUT/tr.f90")" = 0 ] || { echo "REFUSING: a second T = 70 left in the source"; exit 1; }
# the treatC2 pieces must all be there
[ "$(n 'do abstain_choice_1=0,abstain_top_1')" = 1 ] || { echo "REFUSING: no abstention loop"; exit 1; }
[ "$(n 'THE ABSTAINER (patch_treatC2.py)')" = 1 ] || { echo "REFUSING: no abstainer branch in calculate_addiction_spending"; exit 1; }
[ "$(n 'evx_oc=evx_opp+2\*evx_vidx')" = 2 ] || { echo "REFUSING: the EV key is not in ensure_ev_table and fill_ev_table"; exit 1; }
[ "$(n "THE HOUSEHOLD'S OWN TREATMENT AND ABSTENTION (patch_treatC2.py)")" = 1 ] || { echo "REFUSING: internal grid not patched"; exit 1; }
[ "$(n 'write(\*,\*) "ABSTAIN", &')" = 1 ] || { echo "REFUSING: no ABSTAIN print"; exit 1; }
[ "$(n 'write(\*,\*) "TRANSITION ABSTAIN t=", time_index')" = 1 ] || { echo "REFUSING: no TRANSITION ABSTAIN t= print"; exit 1; }
md5sum "$C/treat/patch_treatC2.py" | cut -c1-32 > "$OUT/patch_treatC2.md5"
( cd "$OUT" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium tr.f90 \
    -o hftf_tr_prod 2> build_prod.err )
[ -x "$OUT/hftf_tr_prod" ] && ! grep -q Error "$OUT/build_prod.err" || { echo "REFUSING: did not compile"; grep -m3 Error "$OUT/build_prod.err"; exit 1; }
echo "built $OUT/hftf_tr_prod $(md5sum "$OUT/hftf_tr_prod" | cut -c1-8) (rule C2 + cohort print, T = 50; patch_treatC2.py $(cut -c1-8 "$OUT/patch_treatC2.md5"))"
