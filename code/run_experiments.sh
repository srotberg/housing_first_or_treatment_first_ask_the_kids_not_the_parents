#!/usr/bin/env bash
# PHASE 1: the long-run-equilibrium counterfactuals, as vector lines.
#
# Every experiment is a one-line change off a FROZEN benchmark vector and runs
# through run_one_point.sh like any calibration point, so each lands as an
# md5-tagged point file with the HANDOVER assertion behind it. The provenance of
# a counterfactual then lives in the archive rather than in which binary happened
# to be built that day, which is what the paper needs in order to say what
# produced each number.
#
#   usage:  bash code/run_experiments.sh <benchmark_point_file> [name ...]
#           bash code/run_experiments.sh code/points/point_abc123.txt tf_benchmark
#           bash code/run_experiments.sh code/points/point_abc123.txt   # all
#
# THE SWITCHES, and what the source says each one is:
#
#   probability_of_voucher_benchmark_used
#       the voucher rate. 1 is universal. The naming block at line 8848 keys
#       "universal" off exactly this.
#
#   increased_prob_of_voucher_if_homeless_and_addicted
#       whether the addicted homeless get preferential access. 1 in the
#       benchmark. The source's own naming calls 0 "TF" and 1 "HF", at 8850 and
#       8867, and it has real economic uses at 25906, 25949, 29922, 29945, 29971.
#
#   voucher_conditional_on_clean
#       whether KEEPING the voucher requires passing a test, with
#       probability_of_detection, probability_of_false_positive and
#       cost_per_drug_test live. The cost already reaches the government budget
#       at 15508.
#
# AN AMBIGUITY THE AUTHOR MUST SETTLE, AND IT IS NOT GUESSED AT HERE.
# "Treatment First" has two readings in this codebase and they are not the same
# experiment:
#   (a) the source's own naming: TF is increased_prob = 0, vouchers not steered
#       to the addicted homeless. Nothing is tested and nothing is revoked.
#   (b) the author's phase 1a: "TF with cost of testing all eligibles and false
#       positive and false negative", which is voucher_conditional_on_clean = 1.
# The definitions below apply BOTH, since 1a names the testing explicitly and the
# source names the steering. If the author means only one, change the line.
set -u
cd /home/user/housing_first_or_treatment_first || exit 1

BASE=${1:?usage: run_experiments.sh <benchmark_point_file> [name ...]}
[ -f "$BASE" ] || { echo "no such point file: $BASE" >&2; exit 1; }
shift

VECTOR=$(grep -a "^VECTOR " "$BASE" | head -1 | sed 's/^VECTOR //')
[ -n "$VECTOR" ] || { echo "no VECTOR line in $BASE" >&2; exit 1; }

# name -> overrides. One line each, so the diff from the benchmark is readable.
declare -A EXP=(
  [benchmark_rerun]=""
  [tf_benchmark]="increased_prob_of_voucher_if_homeless_and_addicted=0 voucher_conditional_on_clean=1"
  [universal_hf]="probability_of_voucher_benchmark_used=1 increased_prob_of_voucher_if_homeless_and_addicted=1 voucher_conditional_on_clean=0"
  [universal_tf]="probability_of_voucher_benchmark_used=1 increased_prob_of_voucher_if_homeless_and_addicted=0 voucher_conditional_on_clean=1"
)

NAMES=${*:-benchmark_rerun tf_benchmark universal_hf universal_tf}

echo "benchmark: $(basename "$BASE")"
for n in $NAMES; do
    [ -n "${EXP[$n]+x}" ] || { echo "unknown experiment: $n" >&2; exit 1; }
done

for n in $NAMES; do
    OV=${EXP[$n]}
    echo
    echo "=== $n ==="
    echo "    overrides: ${OV:-none, this is the benchmark re-run for provenance}"
    LINE="$VECTOR"
    for kv in $OV; do
        k=${kv%%=*}
        if echo "$LINE" | grep -q "(^| )$k="; then
            LINE=$(echo "$LINE" | sed -E "s/(^| )$k=[^ ]*/\1$kv/")
        else
            LINE="$LINE $kv"
        fi
    done
    echo "    running, serialised on the checkout flock..."
    bash code/run_one_point.sh $LINE >> code/batch_run.log 2>&1
    TAG=$(ls -t code/points/point_*.txt 2>/dev/null | head -1)
    echo "    -> $(basename "$TAG" .txt)"
    echo "$n $(basename "$TAG" .txt) ${OV:-benchmark}" >> code/experiment_index.txt
done

echo
echo "index written to code/experiment_index.txt"
