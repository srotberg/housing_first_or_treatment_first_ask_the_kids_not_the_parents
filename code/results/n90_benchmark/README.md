# The n90 benchmark, saved

This is the converged benchmark every arm and the transition read from:
delta_d = 0.24, omega_c = 0.055, kappa_x = 0.8139. It is the first benchmark in
this project that converged AND saved -- `ECONOMY IS STILL` at block 27, block
move 8.646e-5.

## Why these files are in git

The run that produced it wrote 213 `*baseline_benchmark.*` files totalling
2.2 GB, in a container that is reclaimed after a period of inactivity. Losing
it means redoing the whole calibration.

An arm does not need all 2.2 GB of it, but it needs more than is here, and the
next section says exactly what.

## CORRECTION, 19 September: THIS DIRECTORY IS NOT SUFFICIENT TO RUN AN ARM

An earlier version of this file said the 29 large files are "written for the
transition and for diagnostics" and that "no arm opens them", so their absence
"costs SPEED, not correctness". **That is false.** A cloud session running arm 1
hit it within four minutes:

    block 1 solved            CF MOMENTS distance= 1.6282888
    loop_count= 1
    Fortran runtime error: Cannot open file 'value_function1baseline_benchmark.dat'
    Error termination.

`frac_of_households_in_support_of_policy` reads, for i = 1 and 2,
`value_function<i>baseline_benchmark.dat` (line 23895) and
`distribution_stationary<i>baseline_benchmark.dat` (23898). It is called
UNCONDITIONALLY in the counterfactual loop at 51689, with no flag guarding it.
Their absence costs CORRECTNESS: no arm gets past its first loop.

**HOW THE WRONG CLAIM WAS MADE, because the method was sound and the timing was
not.** It was measured by access time against a running arm -- which is the
right instrument -- but the snapshot was taken while that arm was still in
block 1, and the routine sits after the moment block, so it had not yet been
reached. The arm being measured had the files in its container, so it never
failed and never revealed the dependency. Re-measured against the same arm an
hour later, all four files show as READ at 12:26:36 to 12:26:42, about seven
minutes in. An early reading taken for a settled one, which is the error this
project keeps paying for.

## WHAT IS MISSING, AND WHY IT CANNOT BE FIXED BY COMMITTING MORE

Four files, 596 MB:

    value_function1baseline_benchmark.dat            294 MB
    value_function2baseline_benchmark.dat             26 MB
    distribution_stationary1baseline_benchmark.dat   253 MB
    distribution_stationary2baseline_benchmark.dat    22 MB

That is past what belongs in git, and there is no LFS here. **So an arm cannot
be run from a fresh checkout of this repository**, and a container that has only
this directory cannot run one either. An arm has to run where a converged
benchmark's full output is on disk, or after re-running the benchmark -- and
re-running it gives a benchmark that is NOT the one the other arms read, which
breaks the cross-arm comparisons the questions are built on.

What this directory IS still good for: the 54 small scalars an arm reads, the
parameter seed, and reading the benchmark's numbers without a run.

## What is NOT here, and what it costs

The 29 large files, and the two warm-start distributions
(`calibration_distribution1.dat` is 265 MB). Their absence costs SPEED, not
correctness: the stationary distribution is re-solved each block, so an arm
started without them solves block 1 from cold and takes a few more blocks to
settle. It does not change the answer.

If the transition needs the large files, the benchmark must be re-run. The
procedure is `code/CALIBRATION_RECIPE.md`, and `resume_seed.dat` here is the
seed it starts from.

## Using it

    code/launch_arm.sh <arm> <kappa_x> code/results/n90_benchmark [price] [pi_v]

The launcher refuses if fewer than 60 benchmark files arrive, which is the
guard against pointing it at a directory that does not have them.
