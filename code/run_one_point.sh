#!/usr/bin/env bash
# Run ONE model point at an ARBITRARY parameter vector and record its moments.
#
#   bash code/run_one_point.sh name=value name=value ...
#
# Any name the Fortran's PARAM_HANDOVER select case knows may be given; anything
# not given keeps the default below. Example:
#
#   bash code/run_one_point.sh addiction_scalar_1=0.005 value_of_life=31 \
#                              lambda_addiction=2.2 size_homelessness=0.5
#
# WHY key=value AND NOT POSITIONAL. The first version took b and aleph and three
# optional extras, which meant a secant could only ever be taken on those five.
# Twenty four parameters are calibrated, every one of them owns a moment, and a
# search that can only move five of them is not a search of the space. Naming
# them makes every parameter a candidate and costs nothing.
#
# gamma is NOT settable: it is tied to theta inside the model as 0.28*(1-theta),
# and setting it by hand breaks the tie.
#
# The point file records the vector on a VECTOR line, machine readable, so the
# coordinator reads what was actually run rather than parsing a filename.
set -euo pipefail
cd "$(dirname "$0")"

# THE DEFAULTS ARE THE CENTRE OF THE CURRENT GENERATION, so an arm of the search
# is one name=value pair and nothing else, and every arm is a matched pair with
# the centre. b and the value of life are where the users ridge and the value of
# life ridge cross (code/ridge_solve.py); the rest is the vector generation one
# held fixed.
declare -A P=(
    [addiction_scalar_1]=0.0275022
    [value_of_life]=34.8331
    [lambda_addiction]=1.5
    [relative_share_of_addiction_1]=0.38
    [size_homelessness]=0.68259
    [discount_factor]=0.993881
    [relative_share_of_leisure]=2.55924
    [labor_income_tax_rate]=0.753746
    [sd_permanent_productivity]=0.953396
    [kappa_uem]=1
    [lambda_m]=0.067
    [multiple_of_probabilities_of_employment_if_addicted]=2.59294
    [penalty_child_addicted]=0.3
    [penalty_child_homeless]=0.31
    [probability_becoming_unemployed]=0.0294178
    [probability_of_voucher_benchmark_used]=0.012136
    [utility_cost_of_treatment]=0.02
    [smallest_rental_relative_to_lowest_income]=0.0412373
    [largest_house_size]=0.0830253
    [weight_on_child]=0.5
    [max_food_cost]=0.0042
    [mu_homeless]=0.6788
)
for a in "$@"; do
    k=${a%%=*}; v=${a#*=}
    [ -n "${P[$k]+x}" ] || { echo "unknown parameter: $k" >&2; exit 2; }
    P[$k]=$v
done

TAG=$(for k in "${!P[@]}"; do echo "$k=${P[$k]}"; done | sort | md5sum | cut -c1-10)

if [ ! -x hftf ] || [ housing_first_or_treatment_first_SR_v1.f90 -nt hftf ]; then
    echo "building..."
    gfortran housing_first_or_treatment_first_SR_v1.f90 -mcmodel=medium -fopenmp \
        -O3 -funroll-loops -ffree-line-length-none -g -fbacktrace -o hftf
fi

# b reaches the model through the sweep grid; everything else through the handover.
printf '%s\n' "${P[addiction_scalar_1]}" > B_SWEEP_GRID.txt
: > PARAM_HANDOVER.txt
for k in "${!P[@]}"; do
    [ "$k" = addiction_scalar_1 ] && continue
    printf '"%s" %s\n' "$k" "${P[$k]}" >> PARAM_HANDOVER.txt
done

ulimit -s unlimited
echo "running $TAG on $(nproc) cores"
START=$(date +%s)
OMP_NUM_THREADS=$(nproc) OMP_STACKSIZE=512M GFORTRAN_UNBUFFERED_ALL=1 \
    ./hftf > "worker_${TAG}.log" 2>&1 || true
MINS=$(( ($(date +%s) - START) / 60 ))

mkdir -p points
{
    echo "point $TAG solved in ${MINS} min on $(nproc) cores"
    echo -n "VECTOR"
    for k in $(echo "${!P[@]}" | tr ' ' '\n' | sort); do printf ' %s=%s' "$k" "${P[$k]}"; done
    echo
    awk '/===== ALL TARGETED MOMENTS =====/{f=1} f{print} /===== END OF MOMENTS =====/{if(f)exit}' \
        "worker_${TAG}.log"
} > "points/point_${TAG}.txt"

grep -q "END OF MOMENTS" "points/point_${TAG}.txt" || {
    echo "NO MOMENTS BLOCK; tail of the log follows" >> "points/point_${TAG}.txt"
    tail -30 "worker_${TAG}.log" >> "points/point_${TAG}.txt"; }

cat "points/point_${TAG}.txt"
