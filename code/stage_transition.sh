#!/bin/bash
# stage_transition.sh <run dir> <binary> <benchmark run dir> <arm 3 run dir> <price path seed>
#
# Stages a TRANSITION run. The transition reads TWO steady states: the benchmark
# as its initial condition and arm 3 as its terminal condition, the second
# because set_files_names points long_run_simulation at the reform's own arm when
# solve_transition_dynamics==1 (TRANSITION_LESSONS.md section 13, defect 1 --
# before that fix it named the benchmark and the path was solved from the
# benchmark TO the benchmark, converging on a reform that does nothing).
#
# Nothing here is optional except the warm-start distributions. The script ends
# by running check_transition_inputs.py, which parses the required list out of
# the Fortran rather than trusting this one, and REFUSES if anything is missing
# -- the binary deletes PARAM_HANDOVER.txt as it starts, so a run that dies on a
# missing input has already eaten its seed.
set -e
N=$1; BIN=$2; BM=$3; ARM=$4; SEED=$5
S=$(cd "$(dirname "$0")" && pwd)
[ -n "$N" ] && [ -n "$BIN" ] && [ -n "$BM" ] && [ -n "$ARM" ] && [ -n "$SEED" ] || {
    echo "usage: stage_transition.sh <run dir> <binary> <benchmark dir> <arm3 dir> <price seed>"; exit 1; }
[ -x "$BIN" ] || { echo "REFUSING: no binary at $BIN"; exit 1; }
[ -f "$SEED" ] || { echo "REFUSING: no price path seed at $SEED"; exit 1; }

mkdir -p "$N"
cp "$BIN" "$N/hftf"; chmod +x "$N/hftf"

# THE INITIAL STEADY STATE.
cp $BM/*baseline_benchmark.dat $BM/*baseline_benchmark.txt "$N/" 2>/dev/null || true
nb=$(ls $N/*baseline_benchmark.* 2>/dev/null | wc -l)
echo "benchmark files : $nb from $BM"
[ "$nb" -lt 60 ] && { echo "REFUSING: expected at least 60 baseline_benchmark files, got $nb"; exit 1; }

# THE TERMINAL STEADY STATE. Arm 3's own output, file_number 'counter_TF'.
cp $ARM/*counter_TF.dat $ARM/*counter_TF.txt "$N/" 2>/dev/null || true
na=$(ls $N/*counter_TF.* 2>/dev/null | wc -l)
echo "counter_TF files: $na from $ARM"
[ "$na" -lt 10 ] && { echo "REFUSING: arm 3 wrote almost nothing named counter_TF ($na files)."; \
                      echo "  An arm that misses every file_number branch runs blank (commit 80949ad)."; exit 1; }

# The warm start. Optional: it shortens nothing and changes nothing, but the
# newborn shares are the intergenerational channel's own state and starting
# without them switches it off for a block.
for f in calibration_distribution1.dat calibration_distribution2.dat \
         calibration_distribution_shape.dat newborn_parent_share.dat; do
  [ -f "$BM/$f" ] && cp "$BM/$f" "$N/$f"
done
true

# THE PARAMETER VECTOR. The transition runs under the REFORM's configuration --
# it is a path to Treatment First -- so this is arm 3's handover, not the
# benchmark's, and the two must be one file rather than two believed to match.
# THE HANDOVER, AND WHICH ONE. PARAM_HANDOVER_trans_bench.txt carries the
# ARCHIVE's terminal condition -- pi_v 0.076347 and price 0.833490 -- which
# predates the voucher cap fixes (cbc9639, f05451d). A transition seeded there
# warm starts its fiscal instrument and its drug price at values the terminal
# steady state no longer has. _trans_postfix.txt carries the re-solved arm 3's:
# pi_v 0.076876159888350143 and price 0.83283631757376753.
#
# Override with HANDOVER=<path> to pin a specific one.
HANDOVER=${HANDOVER:-$S/seeds/PARAM_HANDOVER_trans_postfix.txt}
[ -f "$HANDOVER" ] || { echo "REFUSING: no handover at $HANDOVER"; exit 1; }
cp "$HANDOVER" "$N/PARAM_HANDOVER.txt"
echo "handover        : $HANDOVER"
cp "$N/PARAM_HANDOVER.txt" "$N/PARAM_HANDOVER.kept.txt"   # the binary deletes the original

# THE PRICE PATH SEED. Absent or SHORT, the code silently keeps the linear ramp
# for the periods it could not read and says so in one line, so the count in the
# log is the only check.
cp "$SEED" "$N/drug_price_path_seed.txt"
echo "price seed      : $(wc -l < $N/drug_price_path_seed.txt) entries from $SEED"

# THE TWO CSVs, opened as ../data/<f>.csv RELATIVE TO THE RUN DIRECTORY.
mkdir -p "$(dirname "$N")/data"
for f in us_mortality_multipliers.csv us_mh_onset_shape.csv; do
  [ -f "$(dirname "$N")/data/$f" ] || cp "$(cd "$S/.." && pwd)/data/$f" "$(dirname "$N")/data/$f"
done

date +%s > "$N/START_EPOCH"
echo
python3 "$S/check_transition_inputs.py" "$N"
echo
echo "staged at $N -- start with: cd $N && ./hftf > run.log 2>&1"
