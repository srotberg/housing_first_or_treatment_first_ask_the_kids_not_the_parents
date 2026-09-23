#!/bin/bash
# THE AUTHOR'S PLAN, 23 September: go back to one class, calibrate with
# omega_c = 0, and bring the use rate down to target. One class is 2.3 GB and
# about half the wall clock a block, which is why the b search happens here.
#
# JOINT, not frozen: freeze_all_but_omega_c 0 so the drug block's adjusters are
# live. b and lambda_d cannot be moved alone from the vector -- they have no
# handover name -- and b alone would not land both anyway, since b drives
# participation while the onset hazard drives lambda_d.
#
# TARGETS: b -> 0.10502, which is 1.180 x the data's 0.0890, and lambda_d ->
# 0.043424, which is 1.180 x 0.0368. Same eighteen per cent uplift on both.
#
# Warm start is mu_probe's one-class distribution, the only archived one solved
# at b_smi_multiple = 1.0, which is where the model now sits. It is a starting
# guess and cannot change the converged answer.
cd "$(dirname "$0")/oc1c0" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1; fi
export OMP_NUM_THREADS=2
exec ./hftf
