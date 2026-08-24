#!/usr/bin/env bash
# Run ONE model point and leave its moments in code/points/.
#
# WHY THIS EXISTS. Sweep points are independent, so they parallelise across
# containers: each worker session gets its own four cores and runs one point.
# Putting the recipe here rather than in every worker's prompt means a worker
# prompt is two lines, the recipe is version controlled, and a fix to it
# reaches every future worker instead of the ones spawned after it.
#
#   bash code/run_one_point.sh <b> <aleph> [lambda] [theta] [h1]
#
# gamma is NOT set: it is tied to theta inside the model as 0.28*(1-theta), and
# setting it by hand breaks the tie.
set -euo pipefail

B=${1:?b required}
ALEPH=${2:?aleph required}
LAM=${3:-1.5}
THETA=${4:-0.38}
H1=${5:-0.42}
TAG="b${B}_aleph${ALEPH}_lam${LAM}_th${THETA}_h${H1}"

cd "$(dirname "$0")"

if [ ! -x hftf ] || [ housing_first_or_treatment_first_SR_v1.f90 -nt hftf ]; then
    echo "building..."
    gfortran housing_first_or_treatment_first_SR_v1.f90 -mcmodel=medium -fopenmp \
        -O3 -funroll-loops -ffree-line-length-none -g -fbacktrace -o hftf
fi

printf '%s\n' "$B" > B_SWEEP_GRID.txt
cat > PARAM_HANDOVER.txt <<EOF
"lambda_addiction" $LAM
"relative_share_of_addiction_1" $THETA
"size_homelessness" $H1
"value_of_life" $ALEPH
"discount_factor" 0.99
"relative_share_of_leisure" 2.4
"labor_income_tax_rate" 0.753746
"sd_permanent_productivity" 0.953396
"kappa_uem" 1
"lambda_m" 0.067
"multiple_of_probabilities_of_employment_if_addicted" 2.7
"penalty_child_addicted" 0.3
"probability_becoming_unemployed" 0.0155
"probability_of_voucher_benchmark_used" 0.06
"utility_cost_of_treatment" 0.02
EOF

ulimit -s unlimited
echo "running $TAG on $(nproc) cores"
START=$(date +%s)
OMP_NUM_THREADS=$(nproc) OMP_STACKSIZE=512M GFORTRAN_UNBUFFERED_ALL=1 \
    ./hftf > "worker_${TAG}.log" 2>&1 || true
MINS=$(( ($(date +%s) - START) / 60 ))

mkdir -p points
{
    echo "point $TAG   solved in ${MINS} min on $(nproc) cores"
    awk '/===== ALL TARGETED MOMENTS =====/{f=1} f{print} /===== END OF MOMENTS =====/{if(f)exit}' \
        "worker_${TAG}.log"
} > "points/point_${TAG}.txt"

if ! grep -q "END OF MOMENTS" "points/point_${TAG}.txt"; then
    echo "NO MOMENTS BLOCK; tail of the log follows" >> "points/point_${TAG}.txt"
    tail -30 "worker_${TAG}.log" >> "points/point_${TAG}.txt"
fi

cat "points/point_${TAG}.txt"
