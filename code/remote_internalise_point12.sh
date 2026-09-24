#!/bin/sh
# FULL HOMELESSNESS INTERNALISATION at omega_c = 0.06, kappa_x = 0.9329,
# FRESH FROM THE SEED with frozen_stop_after_blocks 12.
#
# WHY THIS FILE EXISTS. A frozen run never exits the calibration loop on its own
# (source 948), so it never reaches save_welfare_curve (52324) and writes no CEV.
# frozen_stop_after_blocks is a handover name (46569) used in the loop condition
# at 47401 as (loop_count<2*frozen_stop_after_blocks) -- loop_count advances
# TWICE per block, hence the factor of two. At 12 the run leaves the loop after
# twelve blocks and goes on to the statistics, the save and the welfare curve.
#
# IT DOES NOT TOUCH internalise_h_oc006. remote_internalise_point.sh stage does
# `rm -rf` on that directory and the first solve is still RUNNING in it.
set -e
cd "$(dirname "$0")"

OMEGA=0.06
KAPPA=0.9329
DIR=internalise_h_oc006_b12
SRC=internalise_h_oc006
SEED=scan_seed

[ -x "$SRC/hftf" ] || { echo "GUARD: no binary at $SRC/hftf"; exit 1; }
[ -f "$SEED/PARAM_HANDOVER_base.txt" ] || { echo "GUARD: seed handover missing"; exit 1; }
head -1 "$SEED/calibration_state.dat" | grep -qx 'calibration_state_v3' || { echo "GUARD: seed state is not v3"; exit 1; }
[ -e data ] || ln -s ../data data
[ -r data/us_mh_onset_shape.csv ] || { echo "GUARD: data/us_mh_onset_shape.csv does not resolve"; exit 1; }

rm -rf "$DIR" && mkdir -p "$DIR"
# THE SAME BINARY as the run this must reproduce to 1e-4: a rebuild is not the
# control it claims to be.
cp "$SRC/hftf" "$DIR/"
cp "$SEED/calibration_state.dat" "$DIR/"
gunzip -c "$SEED/calibration_distribution1.dat.gz" > "$DIR/calibration_distribution1.dat"
gunzip -c "$SEED/calibration_distribution2.dat.gz" > "$DIR/calibration_distribution2.dat"
cp "$SEED/calibration_distribution_shape.dat" "$DIR/"
[ "$(stat -c%s "$DIR/calibration_distribution1.dat")" = "265496400" ] || { echo "GUARD: distribution 1 wrong size"; exit 1; }
[ "$(tr -d ' ' < "$DIR/calibration_distribution_shape.dat")" = "8564400" ] || { echo "GUARD: shape stamp is not two-class"; exit 1; }

cd "$DIR"
[ -r ../data/us_mh_onset_shape.csv ] || { echo "GUARD: ../data CSV does not resolve from $DIR -- the empty-run.err trap"; exit 1; }
[ -r ../data/us_mortality_multipliers.csv ] || { echo "GUARD: ../data CSV does not resolve from $DIR"; exit 1; }

# THE FULL VECTOR. Three lines means the unbanked names revert and
# addiction_onset_base is declared 0.d0 -- a zero onset hazard.
cp ../$SEED/PARAM_HANDOVER_base.txt PARAM_HANDOVER.txt
sed -i "s|^weight_on_child .*|weight_on_child $OMEGA|" PARAM_HANDOVER.txt
sed -i "s|^kappa_x .*|kappa_x $KAPPA|" PARAM_HANDOVER.txt
grep -q '^internalise_homelessness_cost ' PARAM_HANDOVER.txt \
  && sed -i "s|^internalise_homelessness_cost .*|internalise_homelessness_cost 1|" PARAM_HANDOVER.txt \
  || echo "internalise_homelessness_cost 1" >> PARAM_HANDOVER.txt
# frozen_stop_after_blocks, NOT frozen_stop_tolerance: the tolerance stops on
# block_move, the metric this family does not trust.
grep -q '^frozen_stop_after_blocks ' PARAM_HANDOVER.txt \
  && sed -i "s|^frozen_stop_after_blocks .*|frozen_stop_after_blocks 12|" PARAM_HANDOVER.txt \
  || echo "frozen_stop_after_blocks 12" >> PARAM_HANDOVER.txt
cp PARAM_HANDOVER.txt PARAM_HANDOVER.relaunch.txt

n=$(wc -l < PARAM_HANDOVER.txt)
[ "$n" -gt 50 ] || { echo "GUARD: handover is only $n lines"; exit 1; }
ob=$(awk '$1=="addiction_onset_base"{print $2}' PARAM_HANDOVER.txt | tr 'Dd' 'Ee')
awk -v v="$ob" 'BEGIN{exit !(v+0>0)}' || { echo "GUARD: addiction_onset_base '$ob' not positive -- the collapse"; exit 1; }
grep -qx "weight_on_child $OMEGA"           PARAM_HANDOVER.txt || { echo "GUARD: weight_on_child"; exit 1; }
grep -qx "kappa_x $KAPPA"                   PARAM_HANDOVER.txt || { echo "GUARD: kappa_x did not land"; exit 1; }
grep -qx 'internalise_homelessness_cost 1'  PARAM_HANDOVER.txt || { echo "GUARD: not internalised"; exit 1; }
grep -qx 'frozen_stop_after_blocks 12'      PARAM_HANDOVER.txt || { echo "GUARD: block cap did not land BY VALUE"; exit 1; }
grep -qx 'freeze_all_but_omega_c 1'         PARAM_HANDOVER.txt || { echo "GUARD: must be FROZEN"; exit 1; }
grep -qx 'omega_c_is_pinned 1'              PARAM_HANDOVER.txt || { echo "GUARD: omega_c must be pinned"; exit 1; }
[ "$(grep -c '^kappa_x ' PARAM_HANDOVER.txt)" = 1 ] || { echo "GUARD: duplicate kappa_x"; exit 1; }
[ "$(grep -c '^frozen_stop_after_blocks ' PARAM_HANDOVER.txt)" = 1 ] || { echo "GUARD: duplicate block cap"; exit 1; }

echo "handover: $n lines, kappa_x $KAPPA, internalised, frozen_stop_after_blocks 12, omega_c $OMEGA"
export OMP_NUM_THREADS=2
date -u +'launched %Y-%m-%dT%H:%M:%SZ' > LAUNCHED.txt
./hftf > run.log 2> run.err
echo "=== 12-BLOCK RUN DONE ==="
ls -la welfare_curve* 2>/dev/null || echo "no welfare_curve file"
grep -ac "KAPPA_X PROBE" run.log
