#!/bin/bash
# MEASURE PARTICIPATION INSTEAD OF INFERRING IT. b_smi_multiple = 1e-12, where
# abstaining costs an SMI household 170 times what using costs, and the author's
# point is that every household with income should then buy. Two inferences
# disagreed on the share who do -- 0.59 from r_smi = u_SMI/u_non, 0.34 from the
# never-disordered stock and the onset hazard -- so this prints the xtab masses
# the model already accumulates.
cd "$(dirname "$0")/u_probe" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1; fi
export OMP_NUM_THREADS=2
exec ./hftf
