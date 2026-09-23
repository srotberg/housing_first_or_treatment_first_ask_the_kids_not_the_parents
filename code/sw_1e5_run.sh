#!/bin/bash
# b_smi_multiple = 1e-5, frozen. The author asked for it twice: is the ratio
# capped, or was the sweep simply not far enough down? The update floors the
# multiple at 1e-6, so this is one decade above the lowest the code allows.
cd "$(dirname "$0")/sw_1e5" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then
    cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1
fi
export OMP_NUM_THREADS=2
exec ./hftf
