#!/usr/bin/env python3
"""patch_revoked_C.py <tr_fix_C.f90> <out_track.f90> <out_plain.f90> -- RULE C (12 October) for the revoked-voucher
experiment. The input is the corrected transition source with treat/patch_treatC.py applied (revoked_2c/build_C.sh).
Runs patch_revoked.py unchanged, then makes ONE change to the tracking copy: the shadow step's screen call is given
the household's own treatment choice, exactly as patch_treatC.py gives it to the model's two distribution call sites
(treatment_choice_now from policy_function_treatment, put back to 0 after). Without it the shadow step would screen
every household as untreated while the model's step does not, and the kernel guard (REVK POP ... kernel_maxabs) would
fail. The plain copy is patch_revoked.py's output as is."""
import subprocess, sys
src, out_track, out_plain = sys.argv[1:4]
subprocess.run([sys.executable, __file__.replace('patch_revoked_C.py', 'patch_revoked.py'), src, out_track, out_plain],
               check=True)
s = open(out_track).read()
call = ("                                            call compute_voucher_index_1(is_homeless_2,&\n"
        "                                                (policy_function_frac_spent_on_addiction(years_left_on_mortgage_index)%&\n"
        "                                                vector_transition_real(time_period,age_index,rk_fin,&\n"
        "                                                unemployment_index,employment_index,housing_status_index,voucher_index)),&\n"
        "                                                rk_vi1)\n")
assert s.count(call) == 1, s.count(call)
s = s.replace(call,
    "                                            ! THE HOUSEHOLD'S OWN TREATMENT CHOICE (patch_revoked_C.py, as patch_treatC.py)\n"
    "                                            treatment_choice_now=policy_function_treatment(years_left_on_mortgage_index)%&\n"
    "                                                vector_transition_integer(time_period,age_index,rk_fin,&\n"
    "                                                unemployment_index,employment_index,housing_status_index,voucher_index)\n"
    + call +
    "                                            treatment_choice_now=0\n")
assert s.count("THE HOUSEHOLD'S OWN TREATMENT CHOICE") == 3
open(out_track, 'w').write(s)
print(f'rule C shadow screen: patched {out_track}')
