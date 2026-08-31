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
    # ONE DISCOUNT FACTOR BY DEFAULT. Two is reachable by passing 2 here, but
    # the two-pass path does not yet reproduce the one-pass economy at equal
    # betas, so anything measured at 2 is provisional.
    # THE FLAT EXCESS DEATH RISK FROM THE STREET, per period. Default is
    # Baggett's implied excess at age 26, so only the age gradient is removed.
    # 0 Baggett ratios, 1 flat excess risk, 2 flat 1.6 multiplier.
    [homeless_death_risk_flat_in_age]=0
    [homeless_excess_death_risk]=0.00396
    [number_of_beta_types]=1
    [utility_cost_of_treatment]=0.0908753
    # THE PRICE OF TREATMENT, HELD AT ZERO. It replaced the utility cost on 31
    # August and was switched back the same day on the author's instruction, so
    # treatment is charged in utility again and not on resources.
    [money_cost_of_treatment]=0
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
    # THE SUD MORTALITY LEVEL, ADDED 30 AUGUST. It was settable in the Fortran
    # and not handable, so every point so far solved at its declared 8.0 --
    # which is why 8.0 is the default here and why next_batch.py fills it in
    # for a point whose VECTOR line predates it. Adding a name changes the md5
    # of every future vector, so a point measured before today will not be
    # recognised as already measured and will re-run once if it is asked for.
    # That is the price of the name, and it is paid once.
    [kappa_phi_d_level]=8.0
    # THE IMPATIENT DISCOUNT FACTOR, ADDED WITH THE TWO-TYPE MODEL. The commit
    # that split households into a patient and an impatient type taught the
    # Fortran's PARAM_HANDOVER and next_batch.py the name and did NOT teach it
    # to this script, so TWOBETA.txt line 1 -- the equal-beta validation the
    # whole two-type change rests on -- died at the argument loop with "unknown
    # parameter" before a single point was solved.
    #
    # The default is the Fortran's DECLARED value, 0.900 at
    # perceived_probability_lower=0, not a search centre: nothing has calibrated
    # it yet, and matching the declaration means handing it over explicitly
    # changes nothing. It is not added to LEGACY_DEFAULT below, deliberately.
    # Every point in points/ was measured on the ONE-type model under a
    # different MODEL hash, and the already-measured check does not compare
    # model hashes -- so a legacy tag here would let a stale one-type point be
    # served in place of a two-type run. The new name changing every tag is what
    # keeps that from happening, and it also keeps this script in step with
    # next_batch.py's IMPLICIT table, which the same commit left alone.
    [discount_factor_impatient]=0.900
)
for a in "$@"; do
    k=${a%%=*}; v=${a#*=}
    [ -n "${P[$k]+x}" ] || { echo "unknown parameter: $k" >&2; exit 2; }
    P[$k]=$v
done

# THE HOUSING GRID INVERTS IF THE SMALLEST UNIT IS NOT SMALLER THAN THE LARGEST.
#
# housing_size(0)=smallest_rental..., housing_size(n-1)=largest_house_size, and
# the interior points are laid out by
#
#   housing_status_grid_distance(i) = i*(largest-smallest)^(1/expander)/(n-1)
#   housing_size = smallest + distance^expander
#
# so at smallest>largest the grid runs DOWNWARD and index n-1, which every
# moment calls "the largest unit", is the CHEAPEST one. Nothing in the Fortran
# notices: the run completes and prints a share in the largest unit that is
# really the share in the smallest.
#
# This happened. The ladder point at smallest_rental=0.15 was solved against
# largest_house_size=0.1118 and reported h_3 = 0.295 against a target of 0.627,
# which reads as a large miss and is not a measurement of anything. Fail here
# instead, and leave the FAILED file so it is visible.
# THE MODEL HASH, COMPUTED HERE because the script cd'd to its own directory at
# the top, which made an earlier "$(dirname "$0")" resolve to code/code and
# stamp an EMPTY hash on two points before it was caught. An empty stamp is
# nearly as bad as none, so fail loudly rather than write one.
#
# IT MUST BE COMPUTED AT TOP LEVEL. This block was pasted INSIDE the inverted
# grid failure branch below, which is the one path that never reaches the point
# file, so MODEL_HASH was set only when the grid inverted and was unset on every
# run that actually solved. Under set -u the "MODEL ${MODEL_HASH}" line then
# killed the script AFTER the solve, mid-write, leaving a point file holding a
# header and no moments -- twenty minutes of compute recorded as a truncated
# file. Keep this above the first exit path.
MODEL_HASH=$(md5sum ./housing_first_or_treatment_first_SR_v1.f90 | cut -c1-10)
if [ -z "$MODEL_HASH" ]; then
    echo "FATAL: could not hash the source; refusing to write an unidentifiable point" >&2
    exit 1
fi

if awk -v a="${P[smallest_rental_relative_to_lowest_income]}" \
       -v b="${P[largest_house_size]}" 'BEGIN{exit !(a+0 >= b+0)}'; then
    echo "run_one_point: smallest_rental_relative_to_lowest_income=${P[smallest_rental_relative_to_lowest_income]}" >&2
    echo "run_one_point: is not below largest_house_size=${P[largest_house_size]}; the housing" >&2
    echo "run_one_point: grid would invert and every unit share would be reversed." >&2
    mkdir -p points
    printf 'point FAILED: inverted housing grid, smallest=%s largest=%s\n' \
        "${P[smallest_rental_relative_to_lowest_income]}" "${P[largest_house_size]}" \
        > "points/point_inverted_grid_$$.FAILED.txt"
    exit 2
fi

TAG=$(for k in "${!P[@]}"; do echo "$k=${P[$k]}"; done | sort | md5sum | cut -c1-10)

# THE TAG OF THE SAME ECONOMICS BEFORE A NAME WAS ADDED TO THE VECTOR.
#
# Adding kappa_phi_d_level changed the md5 of every vector, so an arm measured
# yesterday no longer matches its own file and would be solved a second time to
# produce a byte-identical answer. Five of the eight arms of one batch were in
# exactly that position, which is two and a half hours of compute for nothing.
#
# So a name whose value is still the default it had when it was introduced is
# dropped, and the resulting LEGACY_TAG is checked as well. A point that moved
# the parameter has a different value, does not qualify, and is measured -- which
# is right, because it IS a different point. This mirrors next_batch.py's
# IMPLICIT table and the two must be kept in step.
declare -A LEGACY_DEFAULT=( [kappa_phi_d_level]=8.0 )
LEGACY_TAG=$(for k in "${!P[@]}"; do
    if [ -n "${LEGACY_DEFAULT[$k]+x}" ] && [ "${P[$k]}" = "${LEGACY_DEFAULT[$k]}" ]; then continue; fi
    echo "$k=${P[$k]}"
done | sort | md5sum | cut -c1-10)

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
if [ "$LEGACY_TAG" != "$TAG" ] && [ -f "points/point_${LEGACY_TAG}.txt" ] &&
   grep -q "END OF MOMENTS" "points/point_${LEGACY_TAG}.txt"; then
    echo "run_one_point: $TAG was measured as $LEGACY_TAG before the vector"
    echo "run_one_point: gained a name it is still at the default of, skipping"
    exit 0
fi

# ONE POINT AT A TIME PER CHECKOUT. Everything below this line is shared state
# in the working directory -- the hftf binary, PARAM_HANDOVER.txt,
# B_SWEEP_GRID.txt, calibration_state.dat -- and none of it is keyed to the tag.
# Two runs started in the SAME directory therefore race, and the race is silent:
# the handover is consumed as it is read, so a second run that rewrites
# PARAM_HANDOVER.txt between the first run's write and the first run's read
# hands the model the WRONG VECTOR. The count assertion below cannot catch it,
# because it counts HANDOVER lines and the wrong vector has just as many. The
# point is then archived under the md5 of the vector it was ASKED for while
# holding the moments of the vector it was GIVEN -- a mislabelled point, which
# is worse than a missing one, because nothing downstream can tell.
#
# This was reached on 31 August by running a batch through local subagents,
# which share one checkout, instead of one container per worker. Four runs were
# live in this directory at once; B_SWEEP_GRID.txt held a different point's
# addiction_scalar_1 and PARAM_HANDOVER.txt had already been consumed. No point
# was archived from it and the archive was verified clean afterwards, but only
# because the runs were stopped before they finished.
#
# The lock makes the failure impossible rather than unlikely. Parallelism across
# CONTAINERS is untouched -- each has its own directory and its own lock -- and
# parallelism within one container was never real anyway: the solver takes every
# core it can get, so two runs sharing four cores take longer than the same two
# runs one after another.
if command -v flock >/dev/null 2>&1; then
    exec 9>".run_one_point.lock"
    if ! flock -n 9; then
        echo "run_one_point: another point is running in this checkout, waiting for it"
        flock 9
    fi
else
    echo "run_one_point: flock absent, cannot serialise; do not run two points here at once" >&2
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
    # WHICH MODEL MEASURED THIS POINT. The tag is the md5 of the PARAMETER
    # vector alone, so re-measuring the same vector on a changed model
    # reproduces the tag and silently replaces a real measurement. That hazard
    # is in the standing rules and has no detector; this is the detector. A
    # worker that pulls a source change mid-round and rebuilds now stamps the
    # new hash, so the point can be identified and discarded instead of trusted.
    echo "MODEL ${MODEL_HASH}"
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
