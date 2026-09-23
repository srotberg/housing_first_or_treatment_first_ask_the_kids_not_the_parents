#!/bin/bash
# RELAUNCH sw_001 IN PLACE, SAFELY.
#
# A resume must never be started by running the binary on its own here. The
# worker note results/b_smi_sweep/point_0p01.md established that
# freeze_all_but_omega_c is declared 0 in the source, is set ONLY from
# PARAM_HANDOVER, and is never banked in calibration_state.dat. The handover is
# consumed on its first read, so a bare relaunch comes back with all forty seven
# adjusters LIVE, which turns a one-parameter walk into a joint calibration and
# makes the trace unreadable -- exactly the confound that forced the retraction
# in results/oneclass_bsmi/CHANNEL_NOT_IDENTIFIED.md.
#
# PARAM_HANDOVER.relaunch.txt carries the switches and the adjuster but NOT
# b_smi_multiple itself, because the walked value is banked in
# calibration_state.dat at 45283 and reasserting the start value would throw
# away every block since the launch.
cd "$(dirname "$0")/sw_001" || exit 1
if [ ! -f PARAM_HANDOVER.relaunch.txt ]; then
    echo "no PARAM_HANDOVER.relaunch.txt -- refusing to start with the freeze off"
    exit 1
fi
cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1
export OMP_NUM_THREADS=2
exec ./hftf
