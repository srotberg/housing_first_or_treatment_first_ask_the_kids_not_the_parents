#!/bin/sh
# One point of the omega_c scan.   usage:  ./omega_scan_run.sh 0.075
#
# WHAT THE EXPERIMENT IS. The benchmark is calibrated ONCE at omega_c = 0. Each
# scan point then HOLDS that entire parameter vector and only raises omega_c,
# and the fall in b is the reduction. This is why the point must be FROZEN:
#   freeze_all_but_omega_c 1   zeroes every adjuster but omega_c's
#   omega_c_is_pinned 1        and pinning kills that one too, so nothing moves
# A JOINT run at omega_c > 0 refits b back to 0.10502 and measures a reduction
# of ZERO by construction. oc055_bounds was joint and is NOT a scan point.
#
# HOW THE CONVERGED VECTOR IS CARRIED, WHICH IS THE WHOLE TRICK.
# read_calibration_state() loads the full vector from calibration_state.dat,
# and apply_param_handover() THEN overrides the names in PARAM_HANDOVER.txt on
# top and deletes the file (45768 onward). So:
#
#   calibration_state.dat  <- inherited from oc2c0: the CONVERGED parameters
#   PARAM_HANDOVER.txt     <- THREE LINES ONLY: the switches, nothing else
#
# A FULL HANDOVER WOULD DESTROY THE EXPERIMENT. The first version of this
# script copied oc2c0's PARAM_HANDOVER.relaunch.txt, which is a hand-made
# STAGING artefact -- the model never writes one, it only ever reads
# PARAM_HANDOVER.txt -- and still holds addiction_scalar_1 at its DECLARED
# 4.9191800065755218E-03. Every calibrated parameter would have been overridden
# back to its declared value and the scan would have measured the wrong model,
# silently, with a healthy-looking log.
#
# THE INPUT MUST BE CONVERGED. Do not run this until oc2c0's b and lambda_d
# sequences have FLATTENED -- not merely until they are near target. oc1c0
# crossed its target on a monotone path at block 12, was wrongly called
# converged, and was still falling at -11.9 per cent by block 16.
#
# THE TWO STAGING TRAPS THAT COST A RUN EACH TODAY, both closed below:
#   1. PARAM_HANDOVER.txt is the ONLY name the reader opens. A directory
#      holding only a .relaunch.txt runs the declared vector with no error.
#   2. OMP_NUM_THREADS must be 2. Unset, libgomp takes nproc = 4; two solves
#      then put six threads on four cores and livelock in the distribution
#      loop's spin barrier -- a dead stop, not a slowdown.
set -e
cd "$(dirname "$0")"
OMEGA="$1"
[ -n "$OMEGA" ] || { echo "usage: $0 <omega_c>   e.g. $0 0.075"; exit 1; }
SRC=oc2c0
DIR="scan_$(echo "$OMEGA" | tr -d '.')"

[ -f "$SRC/calibration_state.dat" ] || { echo "GUARD: $SRC has no calibration_state.dat -- there is no converged vector to inherit"; exit 1; }
head -1 "$SRC/calibration_state.dat" | grep -qx 'calibration_state_v3' || { echo "GUARD: state file is not version 3; the model would ignore it and run the declarations"; exit 1; }
[ -f "$SRC/calibration_distribution1.dat" ] || { echo "GUARD: no distribution to warm start from"; exit 1; }
[ "$(tr -d ' ' < $SRC/calibration_distribution_shape.dat)" = "8564400" ] || { echo "GUARD: shape stamp is not two-class"; exit 1; }

rm -rf "$DIR" && mkdir -p "$DIR"
cp build2c/hftf_trace "$DIR/hftf"
cp "$SRC/calibration_state.dat" "$DIR/"
cp "$SRC/calibration_distribution1.dat" "$SRC/calibration_distribution2.dat" \
   "$SRC/calibration_distribution_shape.dat" "$DIR/"
cd "$DIR"

# THREE LINES. Anything more overrides a calibrated parameter.
printf 'weight_on_child %s\nomega_c_is_pinned 1\nfreeze_all_but_omega_c 1\n' "$OMEGA" > PARAM_HANDOVER.txt
cp PARAM_HANDOVER.txt PARAM_HANDOVER.relaunch.txt
[ "$(wc -l < PARAM_HANDOVER.txt)" -eq 3 ] || { echo "GUARD: the handover is not three lines"; exit 1; }
grep -qx "weight_on_child $OMEGA"   PARAM_HANDOVER.txt || { echo "GUARD: weight_on_child"; exit 1; }
grep -q  "addiction_scalar"         PARAM_HANDOVER.txt && { echo "GUARD: handover names a calibrated parameter"; exit 1; }

export OMP_NUM_THREADS=2
nohup ./hftf > run.log 2> run.err &
echo "$DIR launched pid $! at omega_c=$OMEGA"
echo "confirm:  grep -a 'resumed from calibration_state' $DIR/run.log   # must be present"
echo "          grep -a 'addiction_scalar_1=' $DIR/run.log | head -1     # must be the CONVERGED value, not 4.9191800065755218E-003"
echo "          grep -a 'omega_c is PINNED' $DIR/run.log"
