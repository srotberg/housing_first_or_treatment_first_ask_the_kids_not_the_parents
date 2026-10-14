"""patch_treatCA.py IN OUT -- RULE A'S SCREEN ON RULE C'S BUILD (14 October).

The author, 14 October: "I also want a run with rule a but where gov't doesn't give vouchers or revokes them to those
with Sud. So treatment doesn't help them retain it ... Use the same pdet. Just to be able to answer to those who might
say that people can't stop using in treatment. Gov't still pays for treatment, but doesn't give vouchers to those in
treatment even if they don't use.... Unless they can't detect it".

So: everything patch_treatC.py does (the public cost of treatment, the household's own treatment choice at the
distribution's screen sites, the EV table keyed on the voucher category, internal_computations with the household's own
treatment, use counted as v>0, the MILBY SPLIT / ABSTAIN / TREATSHARE prints), with two changes:

1. THE SCREEN IS RULE A'S. A household with the disorder fails it whether or not it is in treatment, and any use fails
   it, as before rule C. Detection is unchanged: a household that fails is caught with probability_of_detection, so one
   the screen does not catch keeps its voucher. Every place that decides the voucher (the distribution, the EV table's
   category, the value function's candidates) reads fails_1 from compute_voucher_index_1, so this one line carries it.

2. THE ABSTENTION OPTION IS OFF (tc2_abstain_on defaults to 0). Under rule A's screen it cannot keep a voucher, and the
   run is the answer to "people cannot stop using in treatment". TC2_ABSTAIN=1 in the environment would put it back.
"""
import os, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'patch_treatC.py'), src, out],
               check=True)
s = open(out).read()
old = ("            ! RULE C (patch_treatC.py): a household with the disorder must be in treatment, and nobody may use\n"
       "            if ((unemployment_index>threshold_addiction_index) .AND. (meets_condition_1==0)) fails_1=1\n")
assert s.count(old) == 1, s.count(old)
s = s.replace(old,
    "            ! RULE CA (patch_treatCA.py): rule A's screen on rule C's build -- a household with the disorder fails\n"
    "            ! whether or not it is in treatment, and nobody may use; treatment is still publicly paid for\n"
    "            if (unemployment_index>threshold_addiction_index) fails_1=1\n")
old = "        integer :: tc2_abstain_on=1,tc2_evkey_on=1,tc2_internal_on=1,tc2_env_read=0\n"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, "        integer :: tc2_abstain_on=0,tc2_evkey_on=1,tc2_internal_on=1,tc2_env_read=0   ! patch_treatCA.py: abstention off\n")
open(out, 'w').write(s)
print(f'treatCA: rule A screen, abstention off -> {out}')
