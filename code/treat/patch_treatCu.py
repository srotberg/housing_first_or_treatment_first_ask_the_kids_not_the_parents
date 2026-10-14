"""patch_treatCu.py IN OUT -- patch_treatC.py WITH THE internal_computations FIX UNGATED (14 October, a diagnostic).

patch_treatC2.py's third fix sets the household's own treatment (and abstention) before internal_computations, which
re-solves each node after the choice and OVERWRITES THE NODE'S VALUE (value_function_1=val_fun_internal) -- without it a
treated household is re-priced as untreated. The fix was gated on the screen (voucher_conditional_on_clean==1) so that the
no-screen arms stayed bit for bit, which leaves Housing First on the old arithmetic and Treatment First on the corrected
one. The symptom: with the drug price and pi_V both held, 24 per cent of households with a SUD are better off under rule
C's screen alone (0 under rule A, where both arms ran the old arithmetic), about the 29 per cent of them in treatment.

This build removes the gate on that one fix, so Housing First runs the corrected arithmetic too. With the screen on the
gate was already true, so a Treatment First arm is unchanged; only the no-screen arms move."""
import os, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'patch_treatC.py'), src, out],
               check=True)
s = open(out).read()
old = "                                            if ((tc2_internal_on==1) .AND. (voucher_conditional_on_clean==1)) then\n"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, "                                            ! INTERNAL UNGATED (patch_treatCu.py): the own-treatment fix in every arm\n"
                   "                                            if (tc2_internal_on==1) then\n")
open(out, 'w').write(s)
print(f'treatCu: internal_computations fix ungated -> {out}')
