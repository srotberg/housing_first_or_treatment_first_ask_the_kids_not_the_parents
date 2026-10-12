# The secant's non-convergence warning costs a factor of 400

Found 1 September 2026 while measuring the three upward `addiction_scalar_1`
points of `code/DRUG_UP.txt`. It is not specific to those points: nothing has
completed a point on any source built since 20:37 on 31 August.

## What happens

`84c1ee5` ("Fix two undefined reads in the secant and a race in the
distribution sweep") changed the guard on the labor-supply secant's
non-convergence warning from `abs(MU_1-MU_1)`, identically zero and so unable
to fire, to `abs(MU_1-MU_2)`. The condition is correct. What it exposed is
that the secant leaves its loop non-converged constantly, and the warning it
then prints is **eleven `write(*,*)` statements** sitting in the household's
inner labor-supply solve, inside the OpenMP parallel region
(`housing_first_or_treatment_first_SR_v1.f90:20715-20730`).

Every one of those writes takes libgfortran's global I/O lock. With four
threads in `solve_value_function_and_policy_functions`, three sit blocked in
`___pthread_mutex_lock` while the fourth writes 32 bytes. The model stops
being a solver and becomes a log generator.

## The measured cost

One point, `addiction_scalar_1=0.028`, source `d08c67c178`, four cores. The
per-age timings the model prints itself:

    age 60 .. 51    wall_s = 0.35 .. 0.56     the warning is not firing
    age 25 .. 13    wall_s = ~190             the warning is firing

A factor of about 400 on the ages where it fires. The run reached age 13 of
the first value-function solve in 93 minutes; the same model measures a whole
point in 12 to 27 minutes when the warning cannot fire.

Output volume, sampled from `/proc/<pid>/io` at 91 minutes:

    total written      7.3 GB
    rate               1.4 MB/s   (~45,000 lines/s)

## Why the disk fix did not fix it

`84b26dc` ("Drop the labor-supply secant warning before it fills the disk")
did not remove the eleven writes. It pipes the model's stdout through a
`grep -Ev` that discards the lines downstream, and `f323b06` adds a 2 GB
`head -c` cap behind it. Both protect the disk and neither touches the cost:
the writes still execute, still take the lock, and still serialise the solve.
The log on disk stayed at 36 KB while the model wrote 7.3 GB into the pipe,
which is why the run looks idle from the outside -- `ls` on the log shows
nothing moving.

Two runs have now been lost to this. The first (`worker_727034dc25`, another
session, `discount_factor_impatient=0.91`) wrote 24 GB and nearly filled the
container; `f323b06` records that its cause was never identified because the
file was deleted for space before it was sampled. This is that cause.

## What it is not

It is not a deadlock, and `pos: 0` in `/proc/<pid>/fdinfo/1` is not evidence of
one -- a pipe's offset is always zero. The run progresses the whole time, just
400 times slower. I killed one at 93 minutes believing it was hung; it was
not, and it would probably have finished in about three hours.

## What would fix it

Removing the eleven writes, or throttling them to a counter with one summary
line at the end of the solve. The warning's *condition* is worth keeping --
it is telling the truth, the secant really is failing to converge across a
large part of the state space at these parameters, and that is a finding in
its own right that deserves its own look. It is the eleven unthrottled writes
inside a parallel region that are the defect, not the diagnosis.

The Fortran was not edited here: the standing instruction for this round is
not to touch it.
