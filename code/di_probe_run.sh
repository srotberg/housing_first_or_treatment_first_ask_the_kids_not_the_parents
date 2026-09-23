#!/bin/bash
# THE AUTHOR'S QUESTION, 23 September: "the question to ask is if they should be
# given a bit of income". zeta_DI is the expected DI payment to a non-employed
# household with SMI and it is ZERO, on their own instruction of 13 September.
# This point is identical to sw_1e5 except zeta_DI = 0.25, the value the paper
# declares and reports against.
#
# REFERENCE, STATED BEFORE THE RUN, from sw_1e5 block 1 at zeta_DI = 0:
#     r_smi 4.0094    SUD|SMI 0.2278    SUD|non-SMI 0.0568
#     u_SMI 0.588     u_non 0.161       users+experimenters 0.18077
cd "$(dirname "$0")/di_probe" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1; fi
export OMP_NUM_THREADS=2
exec ./hftf
