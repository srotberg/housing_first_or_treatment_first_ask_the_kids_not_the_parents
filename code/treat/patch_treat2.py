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
open(out, 'w').write(s)
