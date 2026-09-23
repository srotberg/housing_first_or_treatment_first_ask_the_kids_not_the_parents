#!/bin/sh
# Resume the two-class omega_c = 0 benchmark. NEVER resume without a handover.
#
# WHY THIS SCRIPT EXISTS. oc2c0 was resumed in place with no PARAM_HANDOVER.txt
# -- the reader consumes it at startup, so the directory had none -- and the
# run COLLAPSED: b = 0.952, lambda_d = 0.000, r_smi = 0.000. Ninety-five per
# cent using and nobody with a disorder.
#
# THE CAUSE. calibration_state.dat banks 108 names. The handover supplies 100,
# and SIXTY-NINE OF THOSE ARE NOT BANKED. Every one of them reverts to its
# Fortran declaration on a resume. addiction_onset_base is declared
#
#     real(8) :: addiction_onset_base=0.d0
#
# and with lambda_addiction pinned at 0 the onset hazard is
# min(base + (1-exp(-0*q)),1), so a zero base means NOBODY EVER DEVELOPS A
# DISORDER. lambda_d goes to zero, the deterrent to using goes with it, and use
# runs to 95 per cent. The run looked healthy: no error, no fault, stderr empty.
#
# THREE OF THE SIXTY-NINE ARE ALSO MOVED BY THE LOOP, so the staging value is
# stale for them and they are overridden below with the values the calibration
# actually reached:
#
#     addiction_onset_base       0.0336007  ->  0.0334310
#     multiple_find_if_addicted  4.8855     ->  4.4688      (8.5 per cent)
#     newborn_endowment_scale    0.11211    ->  0.10478     (6.5 per cent)
#
# The other 66 are constants the loop never touches, so staging is correct.
set -e
cd "$(dirname "$0")"
DIR=oc2c0
[ -f "$DIR/calibration_state.dat" ] || { echo "GUARD: no state to resume from"; exit 1; }
head -1 "$DIR/calibration_state.dat" | grep -qx 'calibration_state_v3' || { echo "GUARD: state not v3; it would be ignored and the declarations would run"; exit 1; }

cd "$DIR"
[ -f run.log ] && cp run.log "run.log.$(date +%H%M%S)"

# The distributions left by the collapsed block are garbage. The benchmark's
# own stationary distribution, written before the collapse, is the good one and
# is byte-identical in size.
if [ -f distribution_stationary1baseline_benchmark.dat ]; then
    cp distribution_stationary1baseline_benchmark.dat calibration_distribution1.dat
    cp distribution_stationary2baseline_benchmark.dat calibration_distribution2.dat
    printf '     8564400\n' > calibration_distribution_shape.dat
fi

cp ../oc00/PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt
sed -i 's/^addiction_onset_base .*/addiction_onset_base   3.3431004637304002E-02/'        PARAM_HANDOVER.txt
sed -i 's/^multiple_find_if_addicted .*/multiple_find_if_addicted   4.4688291440779171E+00/' PARAM_HANDOVER.txt
sed -i 's/^newborn_endowment_scale .*/newborn_endowment_scale   1.0477955188261341E-01/'  PARAM_HANDOVER.txt
sed -i 's/^weight_on_child .*/weight_on_child 0/'                                          PARAM_HANDOVER.txt
sed -i 's/^omega_c_is_pinned .*/omega_c_is_pinned 1/'                                      PARAM_HANDOVER.txt
sed -i 's/^freeze_all_but_omega_c .*/freeze_all_but_omega_c 0/'                            PARAM_HANDOVER.txt
cp PARAM_HANDOVER.txt PARAM_HANDOVER.relaunch.txt

for g in "weight_on_child 0" "omega_c_is_pinned 1" "freeze_all_but_omega_c 0" "penalty_child_addicted 0.24"; do
    grep -qx "$g" PARAM_HANDOVER.txt || { echo "GUARD: $g"; exit 1; }
done
grep -qE '^addiction_onset_base +3\.34310' PARAM_HANDOVER.txt || { echo "GUARD: onset base is not the calibrated value -- a zero here collapses the model"; exit 1; }

nohup ./hftf > run.log 2> run.err &
echo "oc2c0 resumed, pid $!"
echo "CONFIRM WITHIN THE FIRST BLOCK, and stop it if either fails:"
echo "  grep -ac HANDOVER oc2c0/run.log                  # ~100, never 0"
echo "  grep -a 'MOMENT lambda_d' oc2c0/run.log | tail -1 # must NOT be 0.000000"
