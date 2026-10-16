"""patch_treatCAu.py IN OUT -- patch_treatCA.py WITH THE internal_computations FIX UNGATED (16 October), for the
revoked-voucher paths at detection 1.00 (revoked_2c/build_CA100.sh, revoked_2c_street/build_CA100.sh).

patch_treatCA.py (rule A's screen on rule C's build) and then exactly patch_treatCu.py's one-line change: the household's
own treatment before internal_computations runs in every arm, not only under the screen. With the screen on the gate was
already true, so Treatment First's years are unchanged; the Housing First years of a path then run the corrected
arithmetic, as the corrected Housing First steady state (cf_fix2_share_treatCu) the paths start from does."""
import os, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'patch_treatCA.py'), src, out],
               check=True)
s = open(out).read()
old = "                                            if ((tc2_internal_on==1) .AND. (voucher_conditional_on_clean==1)) then\n"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, "                                            ! INTERNAL UNGATED (patch_treatCAu.py, as patch_treatCu.py): the own-treatment fix in every arm\n"
                   "                                            if (tc2_internal_on==1) then\n")
open(out, 'w').write(s)
print(f'treatCAu: rule A screen, abstention off, internal_computations fix ungated -> {out}')
