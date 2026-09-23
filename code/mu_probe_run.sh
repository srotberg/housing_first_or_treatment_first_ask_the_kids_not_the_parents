#!/bin/bash
# DIAGNOSTIC, NOT A CALIBRATION. One frozen point at mu_m = 0.10, everything
# else at the sweep's vector and b common (b_smi_multiple = 1.0), to measure
# whether the SUD RECOVERY channel has the reach that the Stone-Geary shifter
# turned out to lack. mu_m is a Fortran parameter, so it is set in a PRIVATE
# copy of the source inside this gitignored directory; the shared
# housing_first_or_treatment_first_SR_v1.f90 is untouched and still carries
# mu_m = 1.0.
cd "$(dirname "$0")/mu_probe" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then
    cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1
fi
export OMP_NUM_THREADS=2
exec ./hftf
