#!/bin/sh
# ONE POINT OF THE omega_c SCAN, self-contained, for a session of its own.
#
#     ./remote_scan_point.sh 0.065
#
# WHAT THE EXPERIMENT IS. The benchmark is calibrated ONCE at omega_c = 0. Each
# scan point HOLDS that entire vector and only raises omega_c; the fall in b is
# the reduction. That is why the point is FROZEN:
#     freeze_all_but_omega_c 1   zeroes every adjuster but omega_c's
#     omega_c_is_pinned 1        and pinning kills that one too
# A JOINT run at omega_c > 0 refits b back to its target and measures a
# reduction of ZERO by construction.
#
# WHAT IT INHERITS, all committed under scan_seed/:
#     calibration_state.dat          the converged benchmark vector, ~5 KB
#     calibration_distribution1.dat.gz  253 MB of mostly-zero text -> 12.6 MB
#     calibration_distribution2.dat.gz   24 MB -> 58 KB
#     calibration_distribution_shape.dat
# The handover is written here and is THREE LINES: anything more would override
# a calibrated parameter and measure the wrong model. See ENGINE.md.
set -e
cd "$(dirname "$0")"
OMEGA="$1"
[ -n "$OMEGA" ] || { echo "usage: $0 <omega_c>"; exit 1; }
DIR="scan_$(echo "$OMEGA" | tr -d '.')"
SEED=scan_seed

[ -f "$SEED/PARAM_HANDOVER_base.txt" ] || { echo "GUARD: $SEED/PARAM_HANDOVER_base.txt is missing -- that file IS the converged vector; without it the unbanked names revert and the onset hazard is zero"; exit 1; }
[ -f "$SEED/calibration_state.dat" ] || { echo "GUARD: no $SEED/calibration_state.dat -- the benchmark vector has not been published yet"; exit 1; }
head -1 "$SEED/calibration_state.dat" | grep -qx 'calibration_state_v3' || { echo "GUARD: seed state is not v3; the model would ignore it and run the declarations"; exit 1; }

# the source must be TWO classes for this experiment to mean anything
grep -q 'child_penalty_classes=2' housing_first_or_treatment_first_SR_v1.f90 || { echo "GUARD: source is not child_penalty_classes=2"; exit 1; }

rm -rf "$DIR" && mkdir -p "$DIR"
echo "building (-O3 with -g -fbacktrace, so a fault prints a stack)..."
gfortran -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium \
         -O3 -funroll-loops -g -fbacktrace \
         -o "$DIR/hftf" housing_first_or_treatment_first_SR_v1.f90 2>build_$DIR.log
echo "built: $(grep -c Warning build_$DIR.log) warnings, $(grep -ci error build_$DIR.log) errors  (expect 7 and 0)"

cp "$SEED/calibration_state.dat" "$DIR/"
gunzip -c "$SEED/calibration_distribution1.dat.gz" > "$DIR/calibration_distribution1.dat"
gunzip -c "$SEED/calibration_distribution2.dat.gz" > "$DIR/calibration_distribution2.dat"
cp "$SEED/calibration_distribution_shape.dat" "$DIR/"
[ "$(stat -c%s "$DIR/calibration_distribution1.dat")" = "265496400" ] || { echo "GUARD: distribution 1 is the wrong size after decompression"; exit 1; }
[ "$(tr -d ' ' < "$DIR/calibration_distribution_shape.dat")" = "8564400" ] || { echo "GUARD: shape stamp is not two-class"; exit 1; }

cd "$DIR"
# THE HANDOVER IS THE FULL CONVERGED VECTOR, NOT THREE LINES.
#
# A first version of this script wrote three lines -- weight_on_child,
# omega_c_is_pinned, freeze_all_but_omega_c -- on the reasoning that
# calibration_state.dat carries everything else. It carries the 108 BANKED
# names. It does NOT carry the 69 unbanked ones, which revert to their Fortran
# declarations, and addiction_onset_base is declared 0.d0. With lambda_addiction
# pinned, a zero base means NOBODY EVER DEVELOPS A DISORDER.
#
# Measured on the omega_c = 0 control before this was fixed: three HANDOVER
# lines read, and "budget does not clear" printed NINETY-ONE THOUSAND times in
# the first 40 MB of log, with housing_status_index = -1. The same trap had
# already been diagnosed and written up for the RESUME path that morning, and
# then contradicted here.
cp ../scan_seed/PARAM_HANDOVER_base.txt PARAM_HANDOVER.txt
sed -i "s|^weight_on_child .*|weight_on_child $OMEGA|" PARAM_HANDOVER.txt
cp PARAM_HANDOVER.txt PARAM_HANDOVER.relaunch.txt
n=$(wc -l < PARAM_HANDOVER.txt)
[ "$n" -gt 50 ] || { echo "GUARD: handover is only $n lines -- the unbanked names would revert and the model would run with a ZERO onset hazard"; exit 1; }
ob=$(awk '$1=="addiction_onset_base"{print $2}' PARAM_HANDOVER.txt | tr 'Dd' 'Ee')
awk -v v="$ob" 'BEGIN{exit !(v+0>0)}' || { echo "GUARD: addiction_onset_base is '$ob', not positive -- that is the collapse"; exit 1; }
grep -qx "weight_on_child $OMEGA"    PARAM_HANDOVER.txt || { echo "GUARD: weight_on_child"; exit 1; }
grep -qx 'freeze_all_but_omega_c 1'  PARAM_HANDOVER.txt || { echo "GUARD: must be FROZEN"; exit 1; }
grep -qx 'omega_c_is_pinned 1'       PARAM_HANDOVER.txt || { echo "GUARD: omega_c must be pinned"; exit 1; }

export OMP_NUM_THREADS=2
echo "solving omega_c=$OMEGA ..."
./hftf > run.log 2> run.err

echo "=== RESULT omega_c=$OMEGA ==="
grep -a "resumed from calibration_state" run.log | head -1
grep -a "^ addiction_scalar_1=" run.log | head -1
grep -a "MOMENT b \|MOMENT lambda_d" run.log | tail -2
grep -a "BLOCK MOVE" run.log | tail -1 | cut -c1-140
