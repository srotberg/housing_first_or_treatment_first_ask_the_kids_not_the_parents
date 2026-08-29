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
    [addiction_scalar_1]=0.0224532
    [value_of_life]=35.1001
    [lambda_addiction]=5.0554
    [relative_share_of_addiction_1]=0.530445
    [size_homelessness]=0.104242
    [discount_factor]=0.993881
    [relative_share_of_leisure]=2.76316
    [labor_income_tax_rate]=0.720039
    [sd_permanent_productivity]=0.953392
    [kappa_uem]=1.01931
    [lambda_m]=0.067
    [zeta_DI]=0.0
    [smi_onset_level]=0.003306
    [multiple_of_probabilities_of_employment_if_addicted]=2.43741
    [penalty_child_addicted]=0.24
    [penalty_child_homeless]=0.31
    [probability_becoming_unemployed]=0.0294178
    [probability_of_voucher_benchmark_used]=0.0121367
    [utility_cost_of_treatment]=0.0908753
    [smallest_rental_relative_to_lowest_income]=0.0244763
    [largest_house_size]=0.121252
    [weight_on_child]=0.007
    [max_food_cost]=0.00498294
    [mu_homeless]=0.708003
    # THE TWO THAT MADE A POINT UNDER-SPECIFIED. Both are internally calibrated,
    # both are handover cases the model has accepted all along, and neither was
    # in the vector, so their values rode in on whatever calibration_state.dat
    # the container carried -- which is bug two of REPRODUCIBILITY_INVESTIGATION.
    # relative_share_of_housing owns gamma and is searched; the grid expander's
    # adjuster is declared zero, so it is pinned here at its declared value and
    # every point now states it explicitly.
    [relative_share_of_housing]=0.1483356
    [housing_status_grid_expander]=1.0
)
for a in "$@"; do
    k=${a%%=*}; v=${a#*=}
    [ -n "${P[$k]+x}" ] || { echo "unknown parameter: $k" >&2; exit 2; }
    P[$k]=$v
done

TAG=$(for k in "${!P[@]}"; do echo "$k=${P[$k]}"; done | sort | md5sum | cut -c1-10)

# A FAILURE THAT WRITES NOTHING IS INDISTINGUISHABLE FROM NOT HAVING STARTED.
# Worker 2 of the first automated round ended its turn four minutes after firing
# with no file in points/ and a status of SUCCEEDED. From outside there was no
# way to tell whether it had skipped its line, failed to build, or never run --
# and the health check's "has the point count moved" test reads a silent failure
# as a point still solving. Every exit below now leaves a file behind.
fail () {
    mkdir -p points
    {
        echo "point $TAG FAILED: $1"
        echo "FAILEDVECTOR (deliberately not a VECTOR line, so nothing treats"
        echo "this as a measured point and skips re-running it)"
        for k in $(echo "${!P[@]}" | tr ' ' '\n' | sort); do printf '  %s=%s\n' "$k" "${P[$k]}"; done
    } > "points/point_${TAG}.FAILED.txt"
    echo "run_one_point: $1" >&2
    exit 1
}

# ALREADY MEASURED? THE SCRIPT DECIDES, NOT THE WORKER. The worker prompt used
# to ask each worker to compare the parameter vector on its ROUND.txt line with
# the VECTOR line of every file in points/ and skip on a match. Those two lists
# are formatted differently and the round line carries 19 names against the
# vector's 24, so the comparison was a judgement call, and a worker that judged
# it wrong silently ran nothing. TAG is the md5 of the full sorted vector, which
# is the same comparison done exactly, so the check belongs here.
if [ -f "points/point_${TAG}.txt" ] && grep -q "END OF MOMENTS" "points/point_${TAG}.txt"; then
    echo "run_one_point: $TAG is already measured, skipping"
    exit 0
fi

if [ ! -x hftf ] || [ housing_first_or_treatment_first_SR_v1.f90 -nt hftf ]; then
    echo "building..."
    # THE COMPILER IS NOT ALWAYS THERE. Worker containers built from the
    # 2.1.245 image arrived without gfortran and the run died at the build step
    # with nothing measured; earlier images had it. Install it rather than fail,
    # and say which happened, because a silent reinstall on every point would
    # hide an image regression worth knowing about.
    if ! command -v gfortran >/dev/null 2>&1; then
        echo "run_one_point: gfortran absent from this container, installing"
        (apt-get update -qq && apt-get install -y -qq gfortran) >/dev/null 2>&1 \
            || (sudo apt-get update -qq && sudo apt-get install -y -qq gfortran) >/dev/null 2>&1
        if ! command -v gfortran >/dev/null 2>&1; then
            fail "gfortran absent and could not be installed"
        fi
        echo "run_one_point: gfortran installed, $(gfortran --version | head -1)"
    fi

    # -fimplicit-none IS NOT COSMETIC AND IT IS NOT OPTIONAL.
    # On 29 August create_unemployment_process was found reading
    # probability_becoming_employed1, with a trailing 1, declared nowhere in the
    # file. That subroutine has no implicit none of its own -- the module it
    # uses has one, but that does not reach a scope that merely uses it -- so
    # the misspelling was accepted as an uninitialised implicit real and an
    # unemployment transition row summed to about 1.46 instead of 1. The model
    # had been creating households inside unemployment for as long as anyone
    # can tell, and pi_eu was never within 45 per cent of its target.
    # This flag turns exactly that into a compile error. Verified both ways:
    # reintroducing the typo gives "Symbol 'probability_becoming_employed1' has
    # no IMPLICIT type; did you mean 'probability_becoming_employed'?", and the
    # corrected file compiles with ZERO such errors, so the typo was the only
    # instance of its class in the whole 35,000 lines. It costs nothing at run
    # time and it makes this bug unrepeatable.
    gfortran housing_first_or_treatment_first_SR_v1.f90 -mcmodel=medium -fopenmp \
        -fimplicit-none -O3 -funroll-loops -ffree-line-length-none -g -fbacktrace -o hftf \
        2> build_${TAG}.log || {
            tail -20 "build_${TAG}.log" >&2
            fail "the build failed; see build_${TAG}.log"
        }
fi

# EVERY POINT STARTS FROM THE DECLARATIONS PLUS ITS OWN HANDOVER, so a point is
# a function of its vector and nothing else. Left in place, calibration_state.dat
# carries the PREVIOUS point's parameters and its adjusters, its trust regions
# and its loop counter into this one, and the handover -- which consumes itself
# as it is read -- is gone by the second run, so the second point would silently
# re-measure the first. The warm start goes with it for the same reason: it is
# keyed to the distribution the previous vector produced.
rm -f calibration_state.dat calibration_distribution*.dat

# b reaches the model through the sweep grid; everything else through the handover.
printf '%s\n' "${P[addiction_scalar_1]}" > B_SWEEP_GRID.txt
: > PARAM_HANDOVER.txt
for k in "${!P[@]}"; do
    [ "$k" = addiction_scalar_1 ] && continue
    printf '"%s" %s\n' "$k" "${P[$k]}" >> PARAM_HANDOVER.txt
done
WANT=$(wc -l < PARAM_HANDOVER.txt)

ulimit -s unlimited
echo "running $TAG on $(nproc) cores"
START=$(date +%s)
OMP_NUM_THREADS=$(nproc) OMP_STACKSIZE=512M GFORTRAN_UNBUFFERED_ALL=1 \
    ./hftf > "worker_${TAG}.log" 2>&1 || true
MINS=$(( ($(date +%s) - START) / 60 ))

# DID THE PARAMETERS ACTUALLY REACH THE MODEL? This is the check that was
# missing, and its absence cost a night and an archive. The handover used to be
# read at the foot of read_calibration_state, below two early returns, so on a
# freshly cloned container -- which has no calibration_state.dat, because that
# file is not in the repository -- it was never reached. The run then solved at
# the values written in the Fortran declarations and printed a complete moments
# block. Nothing anywhere said the vector had been discarded: three archived
# points with different vectors re-ran to the same loss to four decimals before
# anyone thought to count the HANDOVER lines, and there were none. The model
# prints one line per parameter it applies, so the count is the proof, and a run
# that cannot prove it must not be recorded as a point.
GOT=$(grep -c "HANDOVER " "worker_${TAG}.log" 2>/dev/null || true)
IGNORED=$(grep -c "HANDOVER IGNORED" "worker_${TAG}.log" 2>/dev/null || true)
GOT=$((GOT - IGNORED))
if [ "$IGNORED" -ne 0 ]; then
    grep "HANDOVER IGNORED" "worker_${TAG}.log" >&2 || true
    fail "the model did not recognise $IGNORED of the names it was handed"
fi
if [ "$GOT" -ne "$WANT" ]; then
    fail "handover applied $GOT of $WANT parameters; this run did not measure the vector it was given"
fi

mkdir -p points
{
    echo "point $TAG solved in ${MINS} min on $(nproc) cores"
    echo "HANDOVER OK: $GOT of $WANT parameters applied"
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
