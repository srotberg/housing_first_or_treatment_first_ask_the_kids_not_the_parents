#!/bin/bash
# b_smi_multiple = 0.001, frozen, b_smi a THOUSANDTH of b. The author's
# question: is the ratio really capped, or was the sweep just not far enough
# down? This is the measurement rather than the extrapolation.
cd "$(dirname "$0")/sw_0001" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then
    cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1
fi
export OMP_NUM_THREADS=2
exec ./hftf
