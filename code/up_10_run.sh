#!/bin/bash
# MAP PARTICIPATION AGAINST b_smi. At 1e-12 the participation ratio is 7.82
# against a data USE ratio of 2.44 (any illicit), 3.75 (excluding marijuana) or
# 4.51 (any disorder) -- overshooting threefold. b_smi is the natural instrument
# for that moment and participation has been measured at only one value of it.
# This is b_smi_multiple = 1.0 on the u_probe binary, which prints MOMENT u_any.
#
# REFERENCE, b_smi_multiple = 1e-12 block 1:
#   participation SMI 0.99752  non-SMI 0.12759  ratio 7.8182   r_smi 4.01404
#   settled r_smi at that point and at 1e-5 and 0.001: 3.58
cd "$(dirname "$0")/up_10" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1; fi
export OMP_NUM_THREADS=2
exec ./hftf
