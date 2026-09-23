#!/bin/bash
# THE AUTHOR'S INSTRUCTION, 23 September: "set UI for SMI at 3/12 of what the
# ratio was multiplied by 25% that they get, and they all get it". zeta_DI is
# an EXPECTED payment in this model -- the long note at 2255 says so -- so
# 3/12 * 0.25 = 0.0625, paid to every non-employed household with SMI, is
# exactly the mean-field object the parameter was built to carry. It replaces
# the zero set on 13 September.
#
# REFERENCE, STATED BEFORE THE RUN, sw_1e5 block 1 at zeta_DI = 0:
#     r_smi 4.0094   SUD|SMI 0.2278   SUD|non-SMI 0.0568   users+exp 0.18077
# AND the upper bound already measured, di_probe block 1 at zeta_DI = 0.25:
#     r_smi 3.9230   SUD|SMI 0.2278   SUD|non-SMI 0.0581   users+exp 0.17055
# SUD|SMI did not move at four times this payment, so it is not expected to
# move here either. This run is for the model's realism, not for the ratio.
cd "$(dirname "$0")/di_0625" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1; fi
export OMP_NUM_THREADS=3
exec ./hftf
