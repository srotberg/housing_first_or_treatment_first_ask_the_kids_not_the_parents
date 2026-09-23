#!/bin/bash
# MEASURE THE MODEL'S TOTAL-DRUG-USERS RATIO BY SMI, which is the object the
# author wants against the data's any-drug-use-disorder ratio of 4.51. Same
# source as oc055 -- two classes, iota_smi 2.0, mu_m 0.82 wired, b_smi = b,
# zeta_DI 0, omega_c 0.055 -- plus three write statements that print the four
# xtab masses the model already accumulates. No value is assigned by them, so
# this is the same equilibrium oc055 is solving.
cd "$(dirname "$0")/up2c" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1; fi
export OMP_NUM_THREADS=1
exec ./hftf
