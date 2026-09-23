#!/bin/sh
# The two-class omega_c = 0 benchmark, 23 September. JOINT, not frozen.
#
# This is step 1 of the author's run order: "run the omega_c=0 two class model
# to have the benchmark with omega_c=0. then we scan omega_c>0 around
# 0.055-0.075 to find the 18% reduction."
#
# THE HANDOVER IS COPIED TO PARAM_HANDOVER.txt, WHICH IS THE ONLY NAME THE
# READER OPENS -- see the open at 45793. A first version of this script staged
# PARAM_HANDOVER.relaunch.txt alone, the reader found nothing, and the run
# solved the DECLARED vector for two and a half minutes before the missing
# HANDOVER echo gave it away. The .relaunch.txt is the saved copy; the .txt is
# what is read. The guard at the bottom now fails the launch rather than
# letting a silent default run for a block.
#
# The handover is oc00's, which is the two-class omega_c = 0 vector, with ONE
# line changed: freeze_all_but_omega_c 1 -> 0, so every adjuster works rather
# than omega_c alone. weight_on_child stays 0, omega_c_is_pinned stays 1 and
# penalty_child_addicted stays 0.24, all as the author set them.
#
# It starts from the DECLARED addiction_scalar_1 of 4.9191800065755218E-03 and
# is NOT seeded toward the value b's gap implies. The loop's own bracket is the
# measurement; an elasticity read off blocks that are still settling after the
# mu_m wiring is the substitute this project does not accept.
#
# Warm start is oc00's two-class distribution, shape stamp checked at 8564400.
#
# The binary is build2c/hftf_trace: -O3 with -g -fbacktrace, so a repeat of the
# 05:14:52 silent death prints a stack into run.err instead of nothing.
set -e
cd "$(dirname "$0")"
# SUPERSEDED, AND ITS INPUTS ARE GONE. This is the FIRST-launch script. oc2c0
# now exists and is continued with oc2c0_resume.sh, which inherits
# calibration_state.dat and the committed oc2c0_resume_handover.txt. On 23
# September the finished run directories had their .dat files reclaimed for
# disk (962 MB), so oc00's distributions no longer exist and this script cannot
# run as written. Kept for the record of how oc2c0 was first staged.
[ -f oc00/calibration_distribution1.dat ] || {
    echo "REFUSING: oc00's distributions were reclaimed for disk on 23 September."
    echo "This is the first-launch script and oc2c0 already exists."
    echo "To continue the benchmark use:  ./oc2c0_resume.sh"
    exit 1; }
# EVERY launch script in this project caps threads at 2 -- oc00_run.sh:22,
# oc055_bounds_run.sh:13, oc1c0_run.sh:19 -- and the first version of THIS
# script was the one that did not. libgomp then defaulted to nproc = 4, which
# with oc1c0's 2 put six threads on four cores, and the run livelocked in the
# distribution loop's spin barrier for twenty-five minutes at 2.3 cores of pure
# spin. It was not a crash, not the optimiser and not the joint loop: all four
# threads sat in libgomp at src_trace.f90:32652 and the run resumed the instant
# the other solve was stopped.
export OMP_NUM_THREADS=2
rm -rf oc2c0 && mkdir -p oc2c0
cp build2c/hftf_trace oc2c0/hftf
cp oc00/PARAM_HANDOVER.relaunch.txt oc2c0/PARAM_HANDOVER.relaunch.txt
cp oc00/calibration_distribution1.dat oc00/calibration_distribution2.dat \
   oc00/calibration_distribution_shape.dat oc2c0/
cd oc2c0
cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt
sed -i 's/^freeze_all_but_omega_c 1$/freeze_all_but_omega_c 0/' PARAM_HANDOVER.txt
sed -i 's/^freeze_all_but_omega_c 1$/freeze_all_but_omega_c 0/' PARAM_HANDOVER.relaunch.txt
# the four switches the author set, asserted on the file the reader opens
grep -qx 'weight_on_child 0'          PARAM_HANDOVER.txt || { echo "GUARD: weight_on_child";     exit 1; }
grep -qx 'omega_c_is_pinned 1'        PARAM_HANDOVER.txt || { echo "GUARD: omega_c_is_pinned";   exit 1; }
grep -qx 'freeze_all_but_omega_c 0'   PARAM_HANDOVER.txt || { echo "GUARD: freeze_all_but";      exit 1; }
grep -qx 'penalty_child_addicted 0.24' PARAM_HANDOVER.txt || { echo "GUARD: penalty_child";      exit 1; }
nohup ./hftf > run.log 2> run.err &
echo "launched pid $!; confirm with: grep -ac HANDOVER oc2c0/run.log  (oc00 printed 102)"
