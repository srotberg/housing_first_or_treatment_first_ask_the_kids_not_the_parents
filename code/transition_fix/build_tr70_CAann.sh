#!/bin/bash
# build_tr70_CAann.sh [OUT] [LAG] [MODE] -- build_tr70_CA.sh with one more patch on top (19 October; the author: "Consider
# HF but with announcement about TF to happen in 5 years. And consider another case in which treatment alone is exempted
# even if there is drug use, but only in the first 5 years"):
#   MODE announce (default): transition_fix/patch_announce.py -- the screen is off for t <= LAG (default 5) and on after,
#     the lottery is rebuilt from zero at both transition sites, and the own-treatment fix is ungated as the corrected
#     Housing First runs it. Default OUT code/tr70_CAann.
#   MODE grace: transition_fix/patch_grace.py -- the screen is on from year 1, and for t <= LAG a household in treatment
#     passes it whatever it uses; rule CA after. Default OUT code/tr70_CAgrace.
# A COPY; build_tr70_CA.sh untouched. Its header follows.
# build_tr70_CA.sh [OUT] -- build_tr50_CA.sh at T = 70 (16 October, 21:20; the author on detection 1.00 with no escape: "you
# can do T=70 in that too", "We would need to run a transition to make that statement for the conclusion"). The source,
# tr70_src.f90, is at T = 70 already: this copy drops build_tr50_CA.sh's 70 -> 50 edit and checks the source is at 70, as
# build_tr70_C2.sh does. Default OUT: code/tr70_CA. A COPY; build_tr50_CA.sh untouched. Its header follows.
# build_tr50_CA.sh [OUT] -- build_tr50_C.sh with treat/patch_treatCA.py in place of patch_treatC2.py (16 October; the author:
# "do one run in which pdet is say 100% and those with SUD cannot get a voucher at all ... we should check also the
# transition for this case"). patch_treatCA.py is patch_treatC.py (= patch_treatC2.py) with rule A's screen line (the
# disorder fails in treatment or not, any use fails) and the abstention option off by default; on tr70_src.f90 its output
# differs from patch_treatC2.py's at those two places only. The guards are build_tr50_C.sh's, adapted to the CA markers.
# Default OUT: code/tr50_CA. A COPY; build_tr50_C.sh untouched. build_tr50_C.sh's header follows.
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
MODE=${3:-announce}
case "$MODE" in announce) DEF=tr70_CAann ;; grace) DEF=tr70_CAgrace ;; *) echo "REFUSING: MODE $MODE"; exit 1 ;; esac
OUT=${1:-$C/$DEF}
LAG=${2:-5}
mkdir -p "$OUT"
python3 "$C/treat/patch_treatCA.py" "$C/transition_fix/tr70_src.f90" "$OUT/tr_ruleCA.f90"
python3 "$C/transition_fix/patch_cohort_print.py" "$OUT/tr_ruleCA.f90" "$OUT/tr_cohort.f90"
python3 "$C/transition_fix/patch_$MODE.py" "$OUT/tr_cohort.f90" "$OUT/tr.f90" "$LAG"
n() { grep -c "$1" "$OUT/tr.f90" || true; }
[ "$(n 'RULE CA (patch_treatCA.py)')" = 1 ] || { echo "REFUSING: the rule-CA screen line is not in the source ($(n 'RULE CA (patch_treatCA.py)'))"; exit 1; }
[ "$(n 'RULE C (patch_treatC.py)')" = 0 ] || { echo "REFUSING: rule C's screen line is still in the source"; exit 1; }
# the CA screen: with the screen on, the disorder fails whether or not the household is in treatment, and any use fails
grep -A1 "! whether or not it is in treatment, and nobody may use" "$OUT/tr.f90" | grep -q "^ *if (unemployment_index>threshold_addiction_index) fails_1=1$" \
    || { echo "REFUSING: the CA screen line (the disorder fails, in treatment or not) is not in the source"; exit 1; }
[ "$(n 'integer :: tc2_abstain_on=0,')" = 1 ] || { echo "REFUSING: the abstention option is not off by default"; exit 1; }
[ "$(n "THE HOUSEHOLD'S OWN TREATMENT CHOICE (patch_treatC.py)")" = 2 ] || { echo "REFUSING: the two treatment-choice call sites are not both patched"; exit 1; }
[ "$(n 'MILBY SPLIT voucher mass rec treat smi')" = 1 ] || { echo "REFUSING: no MILBY SPLIT print"; exit 1; }
[ "$(n 'TRANSITION MILBY t=')" = 1 ] || { echo "REFUSING: the first-year TRANSITION MILBY print is missing"; exit 1; }
[ "$(n 'TRANSITION ENTRANT_VALUE_BY_PARENT_AGE')" = 1 ] || { echo "REFUSING: the cohort print is not in the source"; exit 1; }
[ "$(n 'TRANSITION ENTRANT_MASS_BY_PARENT_AGE')" = 1 ] || { echo "REFUSING: the cohort mass print is not in the source"; exit 1; }
[ "$(n 'TRANSITION ALLALIVE')" -ge 1 ] || { echo "REFUSING: no TRANSITION ALLALIVE print (patch_transition_fix.py)"; exit 1; }
grep -q "parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*70 *$" "$OUT/tr.f90" \
    || { echo "REFUSING: not at transition_length 70"; exit 1; }
# the treatC2 pieces must all be there
[ "$(n 'do abstain_choice_1=0,abstain_top_1')" = 1 ] || { echo "REFUSING: no abstention loop"; exit 1; }
[ "$(n 'THE ABSTAINER (patch_treatC2.py)')" = 1 ] || { echo "REFUSING: no abstainer branch in calculate_addiction_spending"; exit 1; }
[ "$(n 'evx_oc=evx_opp+2\*evx_vidx')" = 2 ] || { echo "REFUSING: the EV key is not in ensure_ev_table and fill_ev_table"; exit 1; }
[ "$(n "THE HOUSEHOLD'S OWN TREATMENT AND ABSTENTION (patch_treatC2.py)")" = 1 ] || { echo "REFUSING: internal grid not patched"; exit 1; }
[ "$(n 'write(\*,\*) "ABSTAIN", &')" = 1 ] || { echo "REFUSING: no ABSTAIN print"; exit 1; }
[ "$(n 'write(\*,\*) "TRANSITION ABSTAIN t=", time_index')" = 1 ] || { echo "REFUSING: no TRANSITION ABSTAIN t= print"; exit 1; }
if [ "$MODE" = announce ]; then
    # the announcement (patch_announce.py): the lag, both sites, the zeroed lottery, the ungated fix
    [ "$(n "integer :: ann_flag_terminal=-1,ann_lag=$LAG ")" = 1 ] || { echo "REFUSING: the lag $LAG is not in the source"; exit 1; }
    [ "$(n 'if (time_index<=ann_lag) voucher_conditional_on_clean=0')" = 2 ] || { echo "REFUSING: the screen is not set by year at both transition sites"; exit 1; }
    [ "$(n '^ *voucher_probabilities=0$')" = 3 ] || { echo "REFUSING: the lottery is not rebuilt from zero at both sites (and create_unemployment_process)"; exit 1; }
    [ "$(n 'TRANSITION ANNOUNCE t=')" = 1 ] || { echo "REFUSING: no TRANSITION ANNOUNCE print"; exit 1; }
    [ "$(n 'INTERNAL UNGATED (patch_treatCu.py, by patch_announce.py)')" = 1 ] || { echo "REFUSING: the own-treatment fix is still gated"; exit 1; }
    [ "$(n 'if ((tc2_internal_on==1) .AND. (voucher_conditional_on_clean==1)) then')" = 0 ] || { echo "REFUSING: a gated own-treatment fix is left"; exit 1; }
else
    # the grace years (patch_grace.py): the lag, the exemption in the rule-CA branch, both sites, the print
    [ "$(n "integer :: grace_now=0,grace_lag=$LAG ")" = 1 ] || { echo "REFUSING: the lag $LAG is not in the source"; exit 1; }
    grep -A3 "if (unemployment_index>threshold_addiction_index) fails_1=1$" "$OUT/tr.f90" | grep -q "if ((grace_now==1) .AND. (meets_condition_1==1)) fails_1=0" \
        || { echo "REFUSING: the grace exemption is not in the rule-CA branch of the screen"; exit 1; }
    [ "$(n 'if (time_index<=grace_lag) grace_now=1')" = 2 ] || { echo "REFUSING: grace_now is not set by year at both transition sites"; exit 1; }
    [ "$(n 'TRANSITION GRACE t=')" = 1 ] || { echo "REFUSING: no TRANSITION GRACE print"; exit 1; }
fi
md5sum "$C/transition_fix/patch_$MODE.py" | cut -c1-32 > "$OUT/patch_$MODE.md5"
md5sum "$C/treat/patch_treatCA.py" | cut -c1-32 > "$OUT/patch_treatCA.md5"
md5sum "$C/treat/patch_treatC.py" | cut -c1-32 > "$OUT/patch_treatC.md5"
( cd "$OUT" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium tr.f90 \
    -o hftf_tr_prod 2> build_prod.err )
[ -x "$OUT/hftf_tr_prod" ] && ! grep -q Error "$OUT/build_prod.err" || { echo "REFUSING: did not compile"; grep -m3 Error "$OUT/build_prod.err"; exit 1; }
echo "built $OUT/hftf_tr_prod $(md5sum "$OUT/hftf_tr_prod" | cut -c1-8) (rule CA + cohort print + $MODE at lag $LAG, T = 70; patch_treatCA.py $(cut -c1-8 "$OUT/patch_treatCA.md5"))"
