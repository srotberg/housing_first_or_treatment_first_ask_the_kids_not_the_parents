#!/bin/sh
# Resume the two-class omega_c = 0 benchmark. TWO WAYS TO GET THIS WRONG, and
# both were got wrong today, an hour apart.
#
# WRONG WAY 1: RESUME WITH NO HANDOVER. The reader CONSUMES PARAM_HANDOVER.txt
# at startup, so a finished run directory has none, and `./hftf` alone looks
# like a resume. calibration_state.dat banks 108 names; the handover supplies
# 100 and SIXTY-NINE ARE NOT BANKED, so they revert to their declarations.
# addiction_onset_base is declared 0.d0 and with lambda_addiction pinned the
# onset hazard is min(base + (1-exp(-0*q)),1), so a zero base means NOBODY EVER
# DEVELOPS A DISORDER. Measured: b = 0.952, lambda_d = 0.000, r_smi = 0.000.
#
# WRONG WAY 2: RESUME WITH THE FULL STAGING HANDOVER. The handover is applied
# AFTER the state and OVERRIDES it, so copying the original 100-line file
# resets every CALIBRATED parameter back to where the run started. Measured:
# addiction_scalar_1 went from its reached 5.5336E-3 back to the declared
# 4.9192E-3, discarding ten blocks of work, while lambda_d looked perfectly
# healthy. This is the same trap omega_scan_run.sh already guards against.
#
# THE CORRECT HANDOVER, WHICH IS oc2c0_resume_handover.txt, IS NEITHER. It is
#   * the 69 UNBANKED names, which the state cannot carry, and
#   * the 22 banked names whose reached value can be read back out of the log,
# each at the value the calibration ACTUALLY REACHED. The remaining 7 banked
# names are left out on purpose so the state file keeps them.
#
# Ten parameters moved from staging over loops 1-20 and all ten are carried:
#   addiction_scalar_1        +12.49%   multiple_find_if_addicted  -8.53%
#   kappa_find_smi             -7.30%   newborn_endowment_scale    -6.54%
#   utility_cost_of_treatment  -4.31%   value_of_life              +2.02%
#   max_food_cost              -0.59%   addiction_onset_base       -0.50%
#   discount_factor            -0.12%   mu_homeless                -0.00%
#
# TO REBUILD IT after further blocks, re-read the reached values from the log:
#   grep -aoE "^ <name>= +[-0-9.E+]+" run.log | tail -1
set -e
cd "$(dirname "$0")"
DIR=oc2c0
[ -f "$DIR/calibration_state.dat" ] || { echo "GUARD: no state to resume from"; exit 1; }
head -1 "$DIR/calibration_state.dat" | grep -qx 'calibration_state_v3' || { echo "GUARD: state not v3"; exit 1; }
[ -f oc2c0_resume_handover.txt ] || { echo "GUARD: no resume handover"; exit 1; }

cd "$DIR"
[ -f run.log ] && cp run.log "run.log.$(date +%H%M%S)"

# Any distribution left by a bad block is garbage. The benchmark's own
# stationary distribution, written at 09:29 before the first collapse, is the
# good one and is byte-identical in size.
if [ -f distribution_stationary1baseline_benchmark.dat ]; then
    cp distribution_stationary1baseline_benchmark.dat calibration_distribution1.dat
    cp distribution_stationary2baseline_benchmark.dat calibration_distribution2.dat
    printf '     8564400\n' > calibration_distribution_shape.dat
fi

cp ../oc2c0_resume_handover.txt PARAM_HANDOVER.txt
cp PARAM_HANDOVER.txt PARAM_HANDOVER.relaunch.txt

# PROPERTY, NOT LITERAL. An earlier version pinned the first resume's exact
# values here and went stale the moment the loop moved them: it refused a
# perfectly good handover whose onset base had simply walked from 3.34310E-2 to
# 3.32622E-2. A guard that has to be edited every resume is a guard that gets
# deleted. These test what actually matters -- the onset base exists and is
# positive, and the scalar is not the DECLARED value.
ob=$(awk '$1=="addiction_onset_base"{print $2}' PARAM_HANDOVER.txt | tr 'Dd' 'Ee')
[ -n "$ob" ] || { echo "GUARD: no addiction_onset_base line -- the model would run the declared 0.d0 and NOBODY would develop a disorder"; exit 1; }
awk -v v="$ob" 'BEGIN{exit !(v+0>0)}' || { echo "GUARD: addiction_onset_base is $ob, not positive -- that is the collapse"; exit 1; }
as=$(awk '$1=="addiction_scalar_1"{print $2}' PARAM_HANDOVER.txt | tr 'Dd' 'Ee')
[ -n "$as" ] || { echo "GUARD: no addiction_scalar_1 line"; exit 1; }
case "$as" in 4.9191800*) echo "GUARD: addiction_scalar_1 is the DECLARED value -- every block of calibration would be discarded"; exit 1;; esac
grep -qx 'weight_on_child 0'                PARAM_HANDOVER.txt || { echo "GUARD: weight_on_child"; exit 1; }
grep -qx 'freeze_all_but_omega_c 0'         PARAM_HANDOVER.txt || { echo "GUARD: joint loop"; exit 1; }

nohup ./hftf > run.log 2> run.err &
echo "oc2c0 resumed, pid $!"
echo "CONFIRM IN BLOCK 1 -- stop the run if either fails:"
echo "  grep -a 'MOMENT lambda_d' oc2c0/run.log | tail -1     # NOT 0.000000"
echo "  grep -a '^ addiction_scalar_1=' oc2c0/run.log | tail -1 # NOT 4.9191800E-3"
