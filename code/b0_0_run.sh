#!/bin/bash
# The author's test: at b_smi = 0 abstaining costs minus infinity, so every SMI
# household that CAN buy will. Prediction stated before the run in
# results/smi_comorbidity/B_ZERO_PREDICTION.md -- r_smi near 6.2, 7.30 still
# missed. Built from a PRIVATE copy with the 1e-6 floor removed.
cd "$(dirname "$0")/b0_0" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1; fi
export OMP_NUM_THREADS=2
exec ./hftf
