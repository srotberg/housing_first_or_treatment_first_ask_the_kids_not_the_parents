#!/usr/bin/env bash
# STEP 3's TWO RUNS, each at the vector in step3_vector.txt.
#
#   bash code/step3_run.sh calib1    the calibration loop
#   bash code/step3_run.sh point1    the measurement, at whatever vector file is named
#   bash code/step3_run.sh point1 some_other_vector.txt
#
# WHY A DRIVER AND NOT A TYPED COMMAND LINE. ENGINE.md's rule, after the
# coordinator hand-typed value_of_life=42.0 into a brief built from a point that
# had 34: a command line with eighty parameters in it must never be retyped. The
# vector is read from the file, so the run and the record cannot disagree.
set -uo pipefail
cd "$(dirname "$0")"
VARIANT=${1:?"usage: step3_run.sh calib1|point1 [vector file]"}
VEC=${2:-step3_vector.txt}
[ -f "$VEC" ] || { echo "no vector file $VEC" >&2; exit 1; }
read -r -a ARGS < "$VEC"
[ "${#ARGS[@]}" -gt 40 ] || { echo "only ${#ARGS[@]} parameters in $VEC" >&2; exit 1; }
echo "step3_run: $VARIANT at ${#ARGS[@]} parameters from $VEC"
exec bash run_variant.sh "$VARIANT" "${ARGS[@]}"
