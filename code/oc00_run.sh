#!/bin/bash
# THE AUTHOR'S PLAN, 23 September. Two classes, delta_d = 0.24, omega_c pinned,
# everything else frozen at the benchmark's calibrated vector, so this reads as
# "has the gaps table moved" rather than as a fresh calibration.
#
# THE MODEL, RESTORED: iota_smi 2.0 (Nielsen 2017), mu_m 0.82 (Bradizza 2006)
# AND WIRED at all fifteen addiction_transition call sites -- eleven of them
# silently dropped it before, so no value of mu_m had ever moved an equilibrium.
# b_smi_multiple 1.0 and zeta_DI 0, both already the declared values.
#
# WARM START from seeds/benchmark_dat: the archived two-class stationary
# distribution, verified byte-exact against the warm-start format at
# 265,496,400 and 23,894,676 bytes, with the shape stamp written beside it
# because the reader refuses an unstamped pair.
#
# Handover is seeds/PARAM_HANDOVER_bm_n90repro.txt -- the BENCHMARK, checked
# before use: voucher_conditional_on_clean 0, include_voucher_exclusion 0,
# adjust_taxes 0. The trans_bench seed beside it is Treatment First and is NOT
# what this runs.
cd "$(dirname "$0")/oc00" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1; fi
export OMP_NUM_THREADS=2
exec ./hftf
