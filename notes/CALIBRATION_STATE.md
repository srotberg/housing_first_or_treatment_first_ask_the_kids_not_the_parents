
## THE LABOUR SECANT WARNING COST THE WHOLE EVENING, AND IT WAS MINE

**No point was ever measured on any source at or after `84c1ee5`.** Nine worker
sessions across four batches produced nothing between 23:28 and 01:20. The cause
was not the fleet, not the rate limit, and not the vectors.

`84c1ee5` changed the labour-supply loop's convergence test from `abs(MU_1-MU_2)`,
the gap in marginal utility, to `abs(x_0-x_2)`, the width of the bracket. In the
same commit it gave the warning BELOW that loop a real condition, having found it
written as `abs(MU_1-MU_1)` and so unable to fire. Each change was right alone.
Together they are inconsistent: the loop exits on the BRACKET, the warning still
tested the MARGINAL UTILITIES, and both against 1e-8. A bisection on [0,1]
reaches a bracket of 1e-8 in about twenty seven steps; the marginal utility gap
there is whatever the slope makes it and is essentially never that small. **So
the warning fired on converged solves, at essentially every working-age state.**

The measurements, from the worker that found it:

    AGE_TIME age=  41  wall_s=      0.37     retired, no labour solve
    AGE_TIME age=  40  wall_s=    191.52     first working age
    AGE_TIME age=  18  wall_s=    186.49

A factor of about 500, and a clean step at the retirement boundary rather than a
gradual slowdown. Eleven unbuffered writes per occurrence, with
`GFORTRAN_UNBUFFERED_ALL=1` set by `run_one_point.sh`, serialise all four OpenMP
threads on stdout: 1.42 MB/s measured, 6.3 GB in 73 minutes, and the process at
117 per cent of a core rather than near 400. Two independent sessions confirmed
it -- one at 70 minutes still on age 9 of 42, another with the same emission rate
at two different values of the parameter it was supposedly testing, 0.4 per cent
apart, which is what ruled the parameter out.

It also explains the 24 GB log that nearly filled the coordinator's disk at
23:54. Same cause, different symptom, and the log cap added then treated the
symptom without finding it.

**THE FIX.** Leaving the loop without converging means hitting the iteration cap,
which is what the warning is for and what it now tests. It cannot fire on a solve
that converged, whatever the marginal utilities do. It is throttled to twenty
occurrences regardless -- eleven writes inside a parallel region is a hazard even
when the condition is right -- and the total prints once beside the invariants as
`DIAG labour secant hit its iteration cap`. **Zero is the expected reading. A
large number there is a real solver problem and the twenty printed occurrences
are the evidence for it.**

### THE RULE THIS BUYS, AND IT IS THE ONE THAT WAS MISSING ALL EVENING

**Prove a source change on ONE point before fanning out to workers.** Nine
containers, four batches and two hours went into a build whose first completed
point would have exposed the fault in twenty minutes. `-fsyntax-only` cannot see
this class at all, and neither can reading the diff: both halves of the change
were individually correct.

The coordinator's own container is the right place for that one point. It has
gfortran, so it skips the fifteen minute install; its output is visible; and a
failure there costs one run instead of nine.

Corollary, learned the same way: **a change that alters a convergence test and a
diagnostic that reads the same quantities is one change, not two.** Check them
together or the inconsistency lives in the gap between them.
