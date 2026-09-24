#!/bin/sh
# WELFARE PASS for the omega_c=0.06 FULL INTERNALISATION point.
#
# The solve run dies inside the frozen calibration loop, so it never reaches
# save_vars_and_functions and never writes the welfare curve (source 52324,
# guarded by the loop condition at 47401). This pass resumes from the CONVERGED
# state of that run with frozen_stop_after_blocks=2, so the loop exits after two
# blocks and the run goes on to the statistics, the save, and save_welfare_curve.
#
# Two blocks, not one, so the pass carries its own control.
set -e
cd "$(dirname "$0")"

SRC=internalise_h_oc006
DIR=internalise_h_oc006_welfare
OMEGA=0.06
KAPPA=0.9329

[ -x "$SRC/hftf" ] || { echo "GUARD: $SRC/hftf missing"; exit 1; }
[ -f "$SRC/calibration_state.dat" ] || { echo "GUARD: no converged state in $SRC"; exit 1; }
[ -f "$SRC/PARAM_HANDOVER.relaunch.txt" ] || { echo "GUARD: no relaunch handover in $SRC"; exit 1; }
head -1 "$SRC/calibration_state.dat" | grep -qx 'calibration_state_v3' || { echo "GUARD: state is not v3"; exit 1; }

rm -rf "$DIR" && mkdir -p "$DIR"
cp "$SRC/hftf" "$DIR/"
cp "$SRC/calibration_state.dat" "$DIR/"
cp "$SRC/calibration_distribution1.dat" "$DIR/"
cp "$SRC/calibration_distribution2.dat" "$DIR/"
cp "$SRC/calibration_distribution_shape.dat" "$DIR/"
[ "$(stat -c%s "$DIR/calibration_distribution1.dat")" = "265496400" ] || { echo "GUARD: distribution 1 wrong size"; exit 1; }

# THE FULL VECTOR, NOT THREE LINES. calibration_state.dat banks only 108 names;
# the unbanked ones revert to their declarations and addiction_onset_base is
# declared 0.d0 -- a zero onset hazard and a collapsed economy.
cp "$SRC/PARAM_HANDOVER.relaunch.txt" "$DIR/PARAM_HANDOVER.txt"
cd "$DIR"

# frozen_stop_after_blocks, NOT frozen_stop_tolerance: the tolerance stops on
# block_move, which is the metric this family does not trust.
grep -q '^frozen_stop_after_blocks ' PARAM_HANDOVER.txt \
  && sed -i "s|^frozen_stop_after_blocks .*|frozen_stop_after_blocks 2|" PARAM_HANDOVER.txt \
  || echo "frozen_stop_after_blocks 2" >> PARAM_HANDOVER.txt
cp PARAM_HANDOVER.txt PARAM_HANDOVER.relaunch.txt

n=$(wc -l < PARAM_HANDOVER.txt)
[ "$n" -gt 50 ] || { echo "GUARD: handover is only $n lines"; exit 1; }
ob=$(awk '$1=="addiction_onset_base"{print $2}' PARAM_HANDOVER.txt | tr 'Dd' 'Ee')
awk -v v="$ob" 'BEGIN{exit !(v+0>0)}' || { echo "GUARD: addiction_onset_base '$ob' not positive -- the collapse"; exit 1; }
grep -qx "weight_on_child $OMEGA"          PARAM_HANDOVER.txt || { echo "GUARD: weight_on_child"; exit 1; }
grep -qx "kappa_x $KAPPA"                  PARAM_HANDOVER.txt || { echo "GUARD: kappa_x"; exit 1; }
grep -qx 'internalise_homelessness_cost 1' PARAM_HANDOVER.txt || { echo "GUARD: not internalised"; exit 1; }
grep -qx 'frozen_stop_after_blocks 2'      PARAM_HANDOVER.txt || { echo "GUARD: block cap did not land"; exit 1; }
[ "$(grep -c '^frozen_stop_after_blocks ' PARAM_HANDOVER.txt)" = 1 ] || { echo "GUARD: duplicate block-cap line"; exit 1; }

[ -r ../data/us_mh_onset_shape.csv ] || { echo "GUARD: ../data/us_mh_onset_shape.csv does not resolve"; exit 1; }
[ -r ../data/us_mortality_multipliers.csv ] || { echo "GUARD: ../data/us_mortality_multipliers.csv does not resolve"; exit 1; }

echo "welfare handover: $n lines, kappa_x $KAPPA, internalised, frozen_stop_after_blocks 2"
export OMP_NUM_THREADS=2
date -u +'launched %Y-%m-%dT%H:%M:%SZ' > LAUNCHED.txt
./hftf > run.log 2> run.err
echo "=== WELFARE PASS DONE ==="
grep -ac CEV run.log
