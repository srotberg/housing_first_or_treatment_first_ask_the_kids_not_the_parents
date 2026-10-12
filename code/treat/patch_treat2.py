"""patch_treat2.py IN OUT -- the treatment-conditional voucher, done right (12 October).

patch_treat.py's MODE treat let a household with the disorder that is in treatment pass the disorder test but kept the
use test, and a household with a SUD keeps using, so it failed the screen anyway: the arm reproduced the paper's
Treatment First (pass 8: CEV 4.38 against 4.37, the same voucher holders with a SUD). The author's request was "test
whether vouchers conditional on being in treatment help": a household with the disorder that is in treatment keeps
(or is offered) the voucher although it uses. Here it passes BOTH tests; a household without the disorder that uses
still fails, and one with the disorder that is not in treatment fails as before. The MILBY SPLIT print is kept.
Built on patch_treat.py's MODE split output, so the print is the same code."""
import subprocess, sys
src, out = sys.argv[1], sys.argv[2]
subprocess.run([sys.executable, __file__.replace('patch_treat2.py', 'patch_treat.py'), 'split', src, out], check=True)
s = open(out).read()
old = ("            if (unemployment_index>threshold_addiction_index) fails_1=1\n"
       "            if (drug_share_1>0) fails_1=1\n")
assert s.count(old) == 1, s.count(old)
s = s.replace(old,
    "            ! TREATMENT MEETS THE CONDITION, USE INCLUDED (patch_treat2.py): a household with the disorder that\n"
    "            ! is in treatment passes although it uses; without the disorder, use still fails\n"
    "            if ((unemployment_index>threshold_addiction_index) .AND. (meets_condition_1==0)) fails_1=1\n"
    "            if ((drug_share_1>0) .AND. (.NOT. ((unemployment_index>threshold_addiction_index) .AND. &\n"
    "                (meets_condition_1==1)))) fails_1=1\n")
# THE HOUSEHOLD'S OWN TREATMENT CHOICE IN THE DISTRIBUTION (12 October, second fix). meets_condition_1 reads
# treatment_choice_now, a threadprivate that the value-function solve sets to the CANDIDATE treatment inside its choice
# loop and resets to 0 after it. The distribution (converge_to_stationary_equilibrium) and the homelessness-duration
# statistics call the screen with it still 0, so no household in treatment ever kept its voucher there and the arm
# reproduced the paper's to four digits (pass 1 welfare 789.9398 in both). Here the two distribution call sites set it
# from the household's own policy first, and put it back to 0 after.
call = ("                                                call compute_voucher_index_1(is_homeless_2,&\n"
        "                                                    (policy_function_frac_spent_on_addiction(years_left_on_mortgage_index)%&\n"
        "                                                    vector_transition_real(time_period,age_index,financial_index,&\n"
        "                                                    unemployment_index,employment_index,housing_status_index,voucher_index)),&\n"
        "                                                    voucher_index_1)\n")
assert s.count(call) == 2, s.count(call)
s = s.replace(call,
    "                                                ! THE HOUSEHOLD'S OWN TREATMENT CHOICE (patch_treat2.py)\n"
    "                                                treatment_choice_now=policy_function_treatment(years_left_on_mortgage_index)%&\n"
    "                                                    vector_transition_integer(time_period,age_index,financial_index,&\n"
    "                                                    unemployment_index,employment_index,housing_status_index,voucher_index)\n"
    + call +
    "                                                treatment_choice_now=0\n")
open(out, 'w').write(s)
