#!/bin/sh
# FULL HOMELESSNESS INTERNALISATION at omega_c = 0.06.
#
#     ./remote_internalise_point.sh stage
#     ./remote_internalise_point.sh solve <kappa_x>
#
# A COPY of remote_scan_point.sh, not an edit of it: three other runs depend on
# that file unchanged.
#
# WHAT IS DIFFERENT FROM A SCAN POINT. A scan point moves omega_c only, and
# kappa_x there is inert -- it enters as -kappa_x*H with H the AGGREGATE, a
# constant inside every household's problem. Here
# internalise_homelessness_cost=1 turns it into a flat kappa_x levied on any
# household that CHOOSES the lowest housing grid point, so it MOVES POLICY
# FUNCTIONS. See the declaration at line 3688 and the application at line 28688.
#
# WHY TWO MODES. kappa_x is the one parameter this experiment turns on, and
# because it moves policy functions a provisional value wastes the entire run.
# `stage` does everything that does not depend on it -- build, decompress, guard
# -- and refuses to solve. `solve` writes the handover and launches.

# PEGGED DRUG PRICE -- THIS SCRIPT RUNS A COUNTERFACTUAL ON THE BENCHMARK BINARY.
# On is_counterfactual = 0, clear_drug_market re-normalises the supply shifter
# every block, so the drug price is pinned at 1 and drug_supply_elasticity does
# nothing. The old experiments cleared the market at 1.46, and so must every
# counterfactual reported in the paper (author, 24 September). Use
# remote_cf_clearing.sh. Set ALLOW_PEGGED_PRICE=1 only to reproduce an old
# pegged run deliberately.
[ "${ALLOW_PEGGED_PRICE:-0}" = 1 ] || { echo "GUARD: pegged drug price -- use remote_cf_clearing.sh (or ALLOW_PEGGED_PRICE=1 to reproduce a pegged run on purpose)"; exit 1; }
set -e
cd "$(dirname "$0")"

MODE="$1"
OMEGA=0.06
DIR=internalise_h_oc006
SEED=scan_seed

case "$MODE" in
  stage|solve) ;;
  *) echo "usage: $0 stage | $0 solve <kappa_x>"; exit 1 ;;
esac

# ---------------------------------------------------------------- stage ------
if [ "$MODE" = stage ]; then

[ -f "$SEED/PARAM_HANDOVER_base.txt" ] || { echo "GUARD: $SEED/PARAM_HANDOVER_base.txt is missing -- that file IS the converged vector; without it the unbanked names revert and the onset hazard is zero"; exit 1; }
[ -f "$SEED/calibration_state.dat" ] || { echo "GUARD: no $SEED/calibration_state.dat -- the benchmark vector has not been published yet"; exit 1; }
head -1 "$SEED/calibration_state.dat" | grep -qx 'calibration_state_v3' || { echo "GUARD: seed state is not v3; the model would ignore it and run the declarations"; exit 1; }

grep -q 'child_penalty_classes=2' housing_first_or_treatment_first_SR_v1.f90 || { echo "GUARD: source is not child_penalty_classes=2"; exit 1; }

# THE TWO SITES THIS EXPERIMENT TURNS ON. The model is frozen; if either has
# moved, stop rather than run something else under this name.
grep -q 'integer :: internalise_homelessness_cost=0' housing_first_or_treatment_first_SR_v1.f90 || { echo "GUARD: internalise_homelessness_cost is not declared, or no longer defaults to 0"; exit 1; }
grep -q 'case ("internalise_homelessness_cost")' housing_first_or_treatment_first_SR_v1.f90 || { echo "GUARD: internalise_homelessness_cost is not a handover name"; exit 1; }
grep -q 'case ("kappa_x")' housing_first_or_treatment_first_SR_v1.f90 || { echo "GUARD: kappa_x is not a handover name"; exit 1; }
grep -q 'flow_utility_1=flow_utility_1-kappa_x' housing_first_or_treatment_first_SR_v1.f90 || { echo "GUARD: the Pigouvian charge is not applied anywhere"; exit 1; }

command -v gfortran >/dev/null 2>&1 || {
  echo "gfortran is missing -- installing it (a rebuilt container loses it)"
  apt-get update -qq >/dev/null 2>&1
  apt-get install -y -qq gfortran >/dev/null 2>&1
  command -v gfortran >/dev/null 2>&1 || { echo "GUARD: gfortran could not be installed; nothing can be built"; exit 1; }
  echo "gfortran installed: $(gfortran --version | head -1)"
}

# code/data MUST EXIST, and it is a symlink to ../data. Do not delete it.
#
# The Fortran opens "../data/us_mh_onset_shape.csv" and
# "../data/us_mortality_multipliers.csv", paths relative to the WORKING
# DIRECTORY. This run solves from code/internalise_h_oc006/, where ../data is
# code/data -- so without the symlink the path does not resolve.
#
# IT LOOKS EXACTLY LIKE TRAP 4. The model inquires, falls back to the working
# directory, and if neither exists prints "not found. stopping." and STOPS,
# leaving an EMPTY run.err with no backtrace -- which is the container-rebuild
# and OOM signature. The omega_c = 0.07 point died this way two minutes in. The
# symlink is committed now; this guard is here so a container that somehow lacks
# it repairs itself rather than halting.
[ -e data ] || ln -s ../data data
[ -r data/us_mh_onset_shape.csv ] || { echo "GUARD: data/us_mh_onset_shape.csv does not resolve"; exit 1; }
[ -r data/us_mortality_multipliers.csv ] || { echo "GUARD: data/us_mortality_multipliers.csv does not resolve"; exit 1; }

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

echo "STAGED. Binary, seed state and both distributions are in $DIR/."
echo "No handover has been written: kappa_x is not known yet."
echo "Run: $0 solve <kappa_x>"
exit 0
fi

# ---------------------------------------------------------------- solve ------
KAPPA="$2"
[ -n "$KAPPA" ] || { echo "usage: $0 solve <kappa_x>"; exit 1; }
# A NUMBER, AND NOT A PLACEHOLDER. Exponent-safe, and non-negative because the
# model clamps it non-negative on the way in and would silently run a different
# point than the one this file is named for.
echo "$KAPPA" | grep -qE '^[-+]?[0-9]*\.?[0-9]+([EDed][-+]?[0-9]+)?$' || { echo "GUARD: kappa_x '$KAPPA' is not a number"; exit 1; }
awk -v v="$(echo "$KAPPA" | tr 'Dd' 'Ee')" 'BEGIN{exit !(v+0>=0)}' || { echo "GUARD: kappa_x is negative; the model clamps it to 0 and the run would be mislabelled"; exit 1; }

[ -x "$DIR/hftf" ] || { echo "GUARD: $DIR/hftf is not built -- run '$0 stage' first"; exit 1; }
[ -f "$DIR/calibration_state.dat" ] || { echo "GUARD: $DIR/calibration_state.dat is missing -- run '$0 stage' first"; exit 1; }
[ "$(stat -c%s "$DIR/calibration_distribution1.dat" 2>/dev/null)" = "265496400" ] || { echo "GUARD: distribution 1 is missing or the wrong size -- run '$0 stage' first"; exit 1; }

cd "$DIR"
# RE-ASSERTED FROM INSIDE THE RUN DIRECTORY, because that is the path the model
# actually walks and a missing CSV costs the whole run with an empty run.err.
[ -r ../data/us_mh_onset_shape.csv ] || { echo "GUARD: ../data/us_mh_onset_shape.csv does not resolve from $DIR -- this is the empty-run.err trap, not a rebuild"; exit 1; }
[ -r ../data/us_mortality_multipliers.csv ] || { echo "GUARD: ../data/us_mortality_multipliers.csv does not resolve from $DIR -- this is the empty-run.err trap, not a rebuild"; exit 1; }
# THE HANDOVER IS THE FULL CONVERGED VECTOR, NOT THREE LINES. Three HANDOVER
# lines means the 69 unbanked names revert to their Fortran declarations, and
# addiction_onset_base is declared 0.d0 -- with lambda_addiction pinned, a zero
# base means NOBODY EVER DEVELOPS A DISORDER.
cp ../scan_seed/PARAM_HANDOVER_base.txt PARAM_HANDOVER.txt
sed -i "s|^weight_on_child .*|weight_on_child $OMEGA|" PARAM_HANDOVER.txt
# REPLACED IN PLACE, NOT APPENDED. The seed vector already carries a kappa_x
# line (0.8139). The parser is a sequential read with last-wins, so appending
# would work but would leave two kappa_x lines and a file that does not say what
# it ran.
sed -i "s|^kappa_x .*|kappa_x $KAPPA|" PARAM_HANDOVER.txt
# internalise_homelessness_cost is NOT in the seed vector, so it is appended.
grep -q '^internalise_homelessness_cost ' PARAM_HANDOVER.txt \
  && sed -i "s|^internalise_homelessness_cost .*|internalise_homelessness_cost 1|" PARAM_HANDOVER.txt \
  || echo "internalise_homelessness_cost 1" >> PARAM_HANDOVER.txt
cp PARAM_HANDOVER.txt PARAM_HANDOVER.relaunch.txt

n=$(wc -l < PARAM_HANDOVER.txt)
[ "$n" -gt 50 ] || { echo "GUARD: handover is only $n lines -- the unbanked names would revert and the model would run with a ZERO onset hazard"; exit 1; }
ob=$(awk '$1=="addiction_onset_base"{print $2}' PARAM_HANDOVER.txt | tr 'Dd' 'Ee')
awk -v v="$ob" 'BEGIN{exit !(v+0>0)}' || { echo "GUARD: addiction_onset_base is '$ob', not positive -- that is the collapse"; exit 1; }
grep -qx "weight_on_child $OMEGA"           PARAM_HANDOVER.txt || { echo "GUARD: weight_on_child"; exit 1; }
grep -qx 'freeze_all_but_omega_c 1'         PARAM_HANDOVER.txt || { echo "GUARD: must be FROZEN"; exit 1; }
grep -qx 'omega_c_is_pinned 1'              PARAM_HANDOVER.txt || { echo "GUARD: omega_c must be pinned"; exit 1; }
grep -qx 'internalise_homelessness_cost 1'  PARAM_HANDOVER.txt || { echo "GUARD: the externality is not being internalised -- this is a plain scan point"; exit 1; }
grep -qx "kappa_x $KAPPA"                   PARAM_HANDOVER.txt || { echo "GUARD: kappa_x did not land"; exit 1; }
[ "$(grep -c '^kappa_x ' PARAM_HANDOVER.txt)" = 1 ] || { echo "GUARD: more than one kappa_x line"; exit 1; }
[ "$(grep -c '^internalise_homelessness_cost ' PARAM_HANDOVER.txt)" = 1 ] || { echo "GUARD: more than one internalise_homelessness_cost line"; exit 1; }

echo "handover written: $n lines, kappa_x $KAPPA, internalise_homelessness_cost 1, omega_c $OMEGA"

# SIX THREADS ON FOUR CORES LIVELOCKS THE DISTRIBUTION LOOP.
export OMP_NUM_THREADS=2
echo "solving omega_c=$OMEGA kappa_x=$KAPPA (internalised) ..."
date -u +'launched %Y-%m-%dT%H:%M:%SZ' > LAUNCHED.txt
./hftf > run.log 2> run.err

echo "=== RESULT omega_c=$OMEGA kappa_x=$KAPPA ==="
grep -a "resumed from calibration_state" run.log | head -1
grep -a "^ addiction_scalar_1=" run.log | head -1
grep -a "BLOCK MOVE" run.log | tail -3 | cut -c1-200
