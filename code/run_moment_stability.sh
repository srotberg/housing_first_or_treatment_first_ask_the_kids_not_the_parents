#!/bin/sh
# Does the distribution's max-norm keep bouncing after the AGGREGATES settle?
#
# WHY IT IS IN THE REPOSITORY AND NOT IN A SCRATCH DIRECTORY. This is the third
# time this test has been launched. The first copy was written to /tmp and the
# container rebuilt out from under it; the second was written to the session's
# scratchpad, which came back from a snapshot three days old and took the run
# with it. The repository is re-cloned from the remote on restart, so a script
# that is committed is a script that is still there afterwards.
#
# WHAT IT ANSWERS. The stopping rule is a max over CELLS of a difference in
# levels, and the calibration reads integrals rather than cells. If the
# aggregates stop moving at sweep one hundred while the max is still bouncing at
# four thousand, the rule is testing the wrong thing and every solve is finishing
# hundreds of sweeps late. diagnose_distribution_max prints DIST_MAX and DIST_MOM
# every hundredth sweep; this runs past where a normal solve would stop so the
# two can be read against each other.
#
#   sh run_moment_stability.sh [output_log]
set -u
cd "$(dirname "$0")" || exit 1
LOG=${1:-moment_stability.log}
ulimit -s unlimited
export OMP_STACKSIZE=512M OMP_NUM_THREADS=4 GFORTRAN_UNBUFFERED_ALL=1
# -fimplicit-none: see the note in run_one_point.sh. It turns an undeclared
# name into a compile error, which is how the unemployment typo of 29 August
# would have been caught.
gfortran housing_first_or_treatment_first_SR_v1.f90 -mcmodel=medium -fopenmp -fimplicit-none -O3 \
    -funroll-loops -ffree-line-length-none -o hftf_mom || exit 1
# COLD ON PURPOSE. A warm start makes the first solve start somewhere else, and
# where it starts is exactly what is under test.
rm -f calibration_distribution1.dat calibration_distribution2.dat \
      calibration_distribution_shape.dat calibration_state.dat
exec ./hftf_mom > "$LOG" 2>&1
