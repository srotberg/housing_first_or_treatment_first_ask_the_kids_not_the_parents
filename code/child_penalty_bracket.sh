#!/usr/bin/env bash
# MEASURE what penalty_child_addicted has to be for the child SUD odds ratio to
# reach 2.0. A BRACKET, NOT AN ELASTICITY.
#
# The source carries an elasticity of SUD risk to log productivity of 0.73 and
# an inference from it that a ratio of 2 needs a 61 per cent earnings cut. That
# number does not survive contact with the model: at the calibrated 0.24 the
# elasticity predicts a ratio of 1.22 and the model returns 1.094, because the
# seven-node productivity grid absorbs most of a 24 per cent shift before it
# can move any mass across a node boundary. An elasticity that is wrong by a
# factor of two at the calibrated point is not a basis for extrapolating four
# times as far.
#
# The ratio is an UNTARGETED moment in the benchmark's own moments block, so
# each point is a two-minute benchmark solve, not a counterfactual.
#
# DO NOT RUN THIS WHILE A COUNTERFACTUAL IS PENDING. A benchmark point run takes
# the is_counterfactual==0 branch of clear_drug_market, which RE-NORMALISES the
# supply shifter and writes drug_supply_shifterbaseline_benchmark.dat -- the
# file every counterfactual imports. Interleaving would price the remaining
# arms against a supply curve belonging to a different economy, and they would
# converge and produce numbers. The script refuses rather than relying on that
# being remembered.
set -uo pipefail
cd /home/user/housing_first_or_treatment_first

if pgrep -c -f "hftf_cf" >/dev/null 2>&1 && ps -eo args= | grep -q "^\./hftf_cf"; then
    echo "REFUSING: a counterfactual is running. It imports the benchmark's drug"
    echo "supply shifter, and a benchmark point run rewrites that file."
    exit 1
fi
if ps -eo args= | grep -q "run_phase1.sh"; then
    echo "REFUSING: run_phase1.sh is still going; wait for PHASE1 COMPLETE."
    exit 1
fi

VEC=$(grep -a "^VECTOR " code/benchmark_of_record.txt | head -1 | sed 's/^VECTOR //')
[ -n "$VEC" ] || { echo "no benchmark vector in benchmark_of_record.txt"; exit 1; }

# BOTH RATIOS, AND THEY RUN IN OPPOSITE DIRECTIONS.
#
#   delta_d, penalty_child_addicted = 0.24 -> ratio 1.0945, target 2.00  (raise)
#   delta_h, penalty_child_homeless = 0.31 -> ratio 3.4477, target 2.10  (LOWER)
#
# Same channel and the same contraction of the newborn draw against the rate at
# each node, so the fact that one overshoots by 64 per cent while the other
# undershoots by 45 is a statement about the model, not about the penalties: a
# child's homelessness is far steeper in productivity than a child's disorder.
#
# BOTH PENALTIES ARE EXTERNALLY SET, so neither number is free -- 0.24 is
# Nilsson (2017) and 0.31 is Chetty, Hendren and Katz (2016). What the bracket
# measures is how far the model's mapping is from the external estimate, which
# is a diagnostic and not a calibration.
#
# EACH IS SWEPT WITH THE OTHER HELD AT ITS CALIBRATED VALUE. They are not
# independent: a parent can be both disordered and homeless, so each penalty
# moves the other's ratio a little. Sweeping one at a time is the right first
# cut and the cross term is worth checking before either number is used.
run_sweep () {
    NAME=$1; PARAM=$2; ROW=$3; shift 3
    echo
    echo "$NAME: $ROW against $PARAM"
    printf '%-10s %-14s %s\n' "penalty" "ratio" "point"
    for PEN in "$@"; do
        LINE=$(echo "$VEC" | sed -E "s/(^| )$PARAM=[^ ]*/\1$PARAM=$PEN/")
        bash code/run_one_point.sh $LINE > "code/bracket_${PARAM}_${PEN}.log" 2>&1
        TAG=$(ls -t code/points/point_*.txt | head -1)
        R=$(grep -a "$ROW" "$TAG" | sed 's/.*model=//' | awk '{print $1}')
        printf '%-10s %-14s %s\n' "$PEN" "${R:-FAILED}" "$(basename "$TAG" .txt)"
    done
}

run_sweep "SUD, target 2.00" penalty_child_addicted \
    "delta_d child SUD ratio" 0.24 0.45 0.65 0.85

run_sweep "HOMELESSNESS, target 2.10" penalty_child_homeless \
    "delta_h child homelessness ratio" 0.31 0.22 0.14 0.07

echo
echo "Interpolate on the measured curve; do not extrapolate off either end."
