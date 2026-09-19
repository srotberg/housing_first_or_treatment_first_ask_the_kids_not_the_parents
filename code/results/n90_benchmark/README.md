# The n90 benchmark, saved

This is the converged benchmark every arm and the transition read from:
delta_d = 0.24, omega_c = 0.055, kappa_x = 0.8139. It is the first benchmark in
this project that converged AND saved -- `ECONOMY IS STILL` at block 27, block
move 8.646e-5.

## Why these files are in git

The run that produced it wrote 213 `*baseline_benchmark.*` files totalling
2.2 GB, in a container that is reclaimed after a period of inactivity. Losing
it means redoing the whole calibration.

An arm does not need 2.2 GB of it. Measured by access time against a running
arm, a counterfactual READS 54 of those files and the largest is 1944 bytes.
The 29 large ones -- value functions, stationary distributions, policy
functions -- are written for the transition and for diagnostics, and no arm
opens them. So everything an arm depends on is about 6 KB, and there was never
a reason for it to be perishable.

What is here: all 184 benchmark files under 100 KB (a deliberately generous cut
-- it avoids guessing which 54 matter), plus the three that sit between 100 KB
and 2 MB, plus `resume_seed.dat`, the named parameter seed the calibration
resumes from. About 4 MB in total.

The three mid-size ones -- `baseline_benchmark.txt` and the two
`policy_function_*2` arrays -- are almost certainly not read by an arm either.
They are here because a cloud session, given the 100 KB cut, decided on its own
to RE-RUN the whole benchmark rather than use this directory, which is hours of
work and produces a benchmark that is not the one the other arms read. Four
megabytes is a cheap way to remove the temptation.

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
