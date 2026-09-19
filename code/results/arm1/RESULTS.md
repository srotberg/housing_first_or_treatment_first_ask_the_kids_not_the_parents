# ARM 1, THE OPTIMAL DRUG USE RATE -- NOT RUN. BLOCKED.

**Arm 1 did NOT converge. It did not reach loop 2.** No equilibrium is reported
below, and the block-1 numbers in the last section are NOT results -- block 1
solves from a cold value function and the brief says to judge nothing from it.

The blocker is an input that is not in the repository and cannot be
reconstructed without re-running the benchmark.

## WHAT HAPPENED

    block 1 solved            CF MOMENTS distance= 1.6282888  (the documented cold-start value)
    loop_count= 1
    Fortran runtime error: Cannot open file 'value_function1baseline_benchmark.dat'
    Error termination.

Wall time to failure: about four minutes.

## THE CAUSE, AND IT CONTRADICTS THE BENCHMARK'S README

`code/results/n90_benchmark/README.md` says, of the 29 large files it excludes:

> The 29 large ones -- value functions, stationary distributions, policy
> functions -- are written for the transition and for diagnostics, and **no arm
> opens them.** [...] Their absence costs SPEED, not correctness.

**That is false, and this run is the counter-example.** An arm opens them every
loop. The read is in `frac_of_households_in_support_of_policy`, which reads, for
i = 1,2:

    value_function<i>baseline_benchmark.dat          (cf.f90:23895)
    distribution_stationary<i>baseline_benchmark.dat (cf.f90:23898)

and it is called UNCONDITIONALLY in the counterfactual loop at cf.f90:51689,
immediately after `calculate_welfare` and `calculate_childhood_utility` and
before `distance_govt_budget` is formed. There is no flag guarding it.

**Why the README's measurement missed it.** The claim was established "by access
time against a running arm". The routine sits *after* the moment block in the
loop body, so it is first reached only once block 1 has finished. An access-time
snapshot taken while block 1 was still solving -- which is most of an arm's
first few minutes -- shows those files untouched. The arm that was measured had
the files present in its container, so it never failed and never revealed the
dependency. This is the same shape as the errors recorded elsewhere in this
project: an early reading taken for a settled one.

The consequence is the opposite of the README's: their absence costs
CORRECTNESS, not speed. No arm can run past its first loop without them.

## WHAT IS ACTUALLY MISSING

Present in `code/results/n90_benchmark/`: 191 files, about 4 MB, including
`resume_seed.dat` (the launcher staged 184 at the commit this ran against,
comfortably over its 60-file guard; three mid-size files were added in 37e528f
and do not affect this).

Absent from the repository entirely -- `find` over the whole tree returns no
`value_function*`, and there is no git-lfs:

    value_function1baseline_benchmark.dat
    value_function2baseline_benchmark.dat
    distribution_stationary1baseline_benchmark.dat
    distribution_stationary2baseline_benchmark.dat

Only a converged benchmark run writes these. They cannot be synthesised.

## A SECOND, SEPARATE DEFECT FOUND ON THE WAY

`code/launch_arm.sh` stages the benchmark files but NOT the two CSVs the model
reads (`us_mortality_multipliers.csv`, `us_mh_onset_shape.csv`). The Fortran
opens `"../data/<f>.csv"`, which from `code/arm1/` resolves to `code/data/`,
which does not exist.

This is nastier than it looks, and CALIBRATION_STATE.md already records why:
**the binary reads and DELETES `PARAM_HANDOVER.txt` before it checks for the
data file.** So the failed run eats the seed, and a naive restart runs the
Fortran's declared values (b ~ 0.95, lambda_d = 0) while looking healthy.

Worked around here by symlinking `code/data -> ../data` (one level above the run
directory, per the documented remedy) and re-staging. The symlink is a
container-local fixup and is deliberately NOT committed. A one-line
`cp "$S/../data"/*.csv "$N"/` in the launcher would close it permanently --
the source has a cwd fallback for exactly this -- but that is a `code/` change
outside this session's remit, so it is reported rather than made.

## SETUP, ALL VERIFIED BEFORE THE RUN

    branch            claude/two-period-addiction-hazard-d7gb61  (repointed; origin had moved twice)
    source sentinel   1
    builds            bounds, snan and -O3 all clean
    HANDOVER IGNORED  0
    kappa_x                        0.8139
    weight_on_child                1.0
    adjust_taxes                   1
    drug_price_start               0.89
    penalty_child_addicted         0.24
    internalise_homelessness_cost  0      (source default, not overridden)
    voucher_conditional_on_clean   0
    drug_market_adjuster           0.2    untouched
    max_drug_price_move            0.005  untouched

gfortran was absent from the image and was installed (13.3.0) and smoke-tested.

## BLOCK-1 DIAGNOSTICS -- NOT RESULTS, DO NOT QUOTE AS AN EQUILIBRIUM

Recorded only because the run exists. Block 1's value function is cold and its
V is meaningless; the brief is explicit that nothing is to be judged before
about block 5.

    price_of_addictive_good   0.89 -> 0.88555   (moved on the 0.5% clip, as expected)
    drug quantity V           0.38103716
    implied = 1.6200147899 * V**(1/1.46)        0.836585
    SIGNED gap = implied - price                -0.053415
    |gap| printed by the Fortran                 0.053415   <- reconstruction agrees to 6 digits
    CF MOMENTS distance       1.6282888          (documented cold-start value is 1.628)
    b                         0.050739
    lambda_d                  0.020103
    h_1                       0.005310
    average_welfare_with_childhood  781.183      (block 1, cold)

The gap reconstruction was validated against the Fortran's own printed distance
before the crash, so the method is confirmed working for whoever runs this next.

One observation, offered as an observation and nothing more: at p = 0.89 the
block-1 gap is NEGATIVE, i.e. it points the price DOWN, whereas the brief
expected a large POSITIVE gap in block 1 and a converged arm-1 price somewhat
ABOVE arm 2's 0.872. Block 1 is not evidence about either, and the pinned-price
probe in CALIBRATION_RECIPE 6a is the instrument that would settle it. It is
flagged only so it is not a surprise later.

## WHAT IS NEEDED TO RUN THIS ARM

**Run the arm where a converged benchmark's full output already exists** -- the
container arm 2 is running in, or any box that still holds the 2.2 GB n90 run.
The four files must sit in the arm's run directory beside the staged small ones.

**Re-running the benchmark here is the wrong fix, and the README now says so in
its own words.** The paragraph added in 37e528f records that a cloud session,
given the 100 KB cut, "decided on its own to RE-RUN the whole benchmark rather
than use this directory, which is hours of work and produces a benchmark that is
not the one the other arms read." An arm 1 built on a freshly re-run benchmark
would not be comparable with arm 2 or arm 3, which is the whole point of the
three arms. So it was not started here, and it should not be: this needs the
n90 files themselves, not an equivalent benchmark.

That also means the arm cannot be completed in this container. Per the brief's
own precedent for environment blockers, stopping and saying so is the useful
answer.

Whichever route is taken, `README.md` in `code/results/n90_benchmark/` should be
corrected: "no arm opens them" is what caused this, and the claim that their
absence "costs SPEED, not correctness" is the opposite of what happens. If the
four files are too large for git, the README should say plainly that an arm
cannot be run from a fresh checkout alone -- the current text promises that it
can.
