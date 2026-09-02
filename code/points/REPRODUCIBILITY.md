# Two runs of one tag do not agree exactly

A tag is the md5 of the parameter vector, and `run_one_point.sh` treats it as
identifying a measurement: if `points/point_<tag>.txt` exists with an
`END OF MOMENTS`, the run is skipped. The script works hard to earn that --
it deletes `calibration_state.dat` and `calibration_distribution*.dat` before
every solve so that "a point is a function of its vector and nothing else",
and it asserts the handover count so a run that silently ignored its vector
cannot be recorded.

It is a function of its vector to a tolerance, not to the bit. Recording the
size of that tolerance, because it is not visible from any single point file.

## The observation

Tag `6aadbe9c3d` (`batch_s2_02.txt` line 1) was measured twice, in two
sessions, concurrently and independently. Both landed; the second was
resolved away in favour of the first, which is what this note is about.

Held identical, and checked rather than assumed:

    MODEL b75ae0454f          both      (so the same source, comments stripped)
    VECTOR ...                byte-identical
    cores                     4         both
    warm start                none      both (the script deletes it)
    HANDOVER                  42 of 42  both

Divergence over the 667 numbers the two files share:

    numbers differing            219 of 667  (33%)
    median relative difference   4.5e-06
    worst targeted moment        2.8e-04     tau_u, treatment take up
    largest single difference    1.3e-02     DIAG age 84, SUD rate

The shape is what matters. The targeted moments are the tight end: the worst
of them moves by 2.8e-04 relative, and most move far less. The large relative
differences are all on quantities that are themselves small, where a tiny
absolute wobble is a large relative one. The worst is the whole of that story:

    mine    DIAG age  84  homeless= 0.098553 ... sud= 0.007021  mass= 0.884298
    theirs  DIAG age  84  homeless= 0.098560 ... sud= 0.006933  mass= 0.884218

The SUD rate at age 84 moves by 9e-05 in absolute terms, which is 1.3% of
0.007. Everything else on that line -- the homeless share, the mass -- agrees
to five significant figures. It is the smallness of the quantity, not an
unstable cell: the mass at age 84 is 0.88.

## What it is not

- Not a source difference. The `MODEL` hash is equal, so the two binaries came
  from the same semantic source.
- Not a warm start. `run_one_point.sh` removes `calibration_state.dat` and
  `calibration_distribution*.dat` before the solve, deliberately.
- Not a thread-count difference. Both ran `OMP_NUM_THREADS=$(nproc)` on 4-core
  containers, and both recorded "on 4 cores".
- Not a handover difference. Both applied 42 of 42, and the `VECTOR` lines are
  byte-identical.

## What it is

Not determined here, and stated as such rather than guessed. The distribution
region at 24528 carries no `atomic`, `critical` or `reduction`; it accumulates
into per-thread slices indexed by `omp_get_thread_num()`, which is summed
afterwards. Static scheduling over a fixed thread count should make that
reproducible, so the residual is more likely the equilibrium loop stopping on
a convergence tolerance from a slightly different iterate than a race. The
source itself flags one known unsynchronised write in that loop
(`is_addicted_1`, argued benign in the comment at 24543 because every thread
writes the same value), which is worth re-reading if anyone chases this.

## Why it is worth knowing

- **Re-running a point to check it will not reproduce it.** Diffing two runs
  of one tag shows ~33% of numbers differing. That is this, not a bug.
- **A tag identifies a vector, not a byte stream.** Two files under one tag
  are both valid measurements; there is no basis in the artifacts for
  preferring either.
- **It bounds what a moment is worth.** Quoting a targeted moment past about
  four significant figures is quoting the solver's tolerance. The calibration
  loss is compared to four decimals, which sits just inside this.
