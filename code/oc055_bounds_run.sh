#!/bin/bash
# REPRODUCE THE SILENT DEATH UNDER BOUNDS CHECKING. The -O3 joint run at two
# classes died 70 seconds in with an empty stderr, no OOM record in dmesg and
# no reboot. The production flags carry no -fbacktrace, so a crash in that
# binary prints nothing at all. This is the SAME configuration -- two classes,
# freeze_all_but_omega_c 0 so every adjuster is live, omega_c pinned at 0.055,
# warm started from the same distribution -- run under
# -O1 -fcheck=bounds,pointer -g -fbacktrace, which faults loudly with a line
# number. It exercises the joint update path that no frozen solve touched and
# that the omega_c scan will hit again.
cd "$(dirname "$0")/oc055_bounds" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1; fi
export OMP_NUM_THREADS=2
exec ./hftf
