# THE COLD-START PATH WORKS. What it takes, measured 20 September.

This container had no `.dat` files at all -- the 79 transition inputs are 4.71 GB
and gitignored -- so the whole chain had to be rebuilt from the repository. The
cold start had never been exercised. It works, and this is the recipe that did
it, written down because the next container will need it too.

## 0. THE COMPILER IS NOT IN THE IMAGE

`gfortran` is absent from a fresh container; only gcc/g++ are there. Every build
script calls `gfortran` by that name, so:

    apt-get install -y gfortran-13
    ln -sf /usr/bin/gfortran-13 /usr/local/bin/gfortran

GNU Fortran 13.3.0. **A different compiler than the archive's runs used**, which
matters only against the standing rule that the model is not bit-reproducible
and a no-op control scores at 1e-4 relative, never on equality.

Build times on 4 cores: 30 s at `-O1 -fcheck=bounds,pointer`, 50 s at `-O3`.
All three standing builds clean; the only warnings are the pre-existing
`transition_length-25` out-of-bounds notices the recipe already documents,
which fire because `transition_length` is 1 in a steady state.

## 1. WHAT "COLD" MEANS, AND WHY THE HANDOVER IS THE WHOLE STATE

`calibration_state.dat` is written POSITIONALLY and does not carry every
calibrated parameter, so a cold run must be seeded from `resume_seed.dat`
instead -- which the Fortran's own comment calls a deliberate superset, applied
AFTER the state file. The log's first two lines are the confirmation:

    no calibration_state.dat, starting from the declared values
    HANDOVER addiction_onset_base: 0.0000000000000000 -> 3.3600679648463409E-002

and `grep -c "HANDOVER IGNORED" run.log` returned **0** over all 96 names. A
misspelt name is not an error; it prints `HANDOVER IGNORED, unknown name` and
the run continues against a model nobody chose.

The committed `code/calibration_state.dat` is NOT used. It belongs to a
different vector, and `run_one_point.sh` deletes the state file at the head of
every run -- that deletion is what "cold" means in the standing rule.

## 2. THE BENCHMARK'S HANDOVER IS THE SEED PLUS SEVEN NAMES

`code/seeds/PARAM_HANDOVER_trans_bench.txt` is the TREATMENT FIRST
configuration and must not be used for the benchmark. Diffed against
`code/results/n90_benchmark/resume_seed.dat`, arm 3 adds ten policy overrides
on top of it; the benchmark keeps the seed's own values for all of them --

    voucher_conditional_on_clean                        0
    include_voucher_exclusion                           0
    increased_prob_of_voucher_if_homeless_and_addicted   1
    probability_of_voucher_benchmark_used               0.067533863
    adjust_taxes                                        0
    probability_of_detection / _false_positive          inert at conditionality 0

-- and overrides only these seven, none of which is a policy:

    penalty_child_addicted   0.24     delta_d, Nilsson, pinned
    weight_on_child          0.055    omega_c, pinned by the author
    kappa_x                  0.8139   the n90 probe's value; the arms and the
                                      transition all run under it, and the seed
                                      carries the coded 0.002 instead
    omega_c_is_pinned        1
    freeze_all_but_omega_c   1        the log prints FROZEN to confirm
    frozen_stop_tolerance    1e-4
    frozen_stop_after_blocks 25

`kappa_x` is the one to watch. It enters flow utility as `kappa_x*H` with H the
AGGREGATE homelessness rate, so it is choice-independent and shifts welfare
levels without moving a single policy -- which is why the recipe computes it
after the benchmark rather than before. But a benchmark solved at 0.002 has a
lifetime welfare that is not comparable with arm 3's at 0.8139, and the
benchmark-to-arm-3 welfare difference is the entire object of the transition.

## 3. THE RUN DIRECTORY MUST SIT ONE LEVEL UNDER A `data/`

The model opens `../data/us_mortality_multipliers.csv` and
`../data/us_mh_onset_shape.csv` RELATIVE TO THE RUN DIRECTORY. So a run in
`code/<name>/` needs `code/data/`, which does not exist in a fresh checkout and
has to be populated from the repository's top-level `data/`. It fails AFTER the
binary has eaten `PARAM_HANDOVER.txt`, so a naive restart then silently runs the
declared values. `launch_arm.sh` already does this; a hand-staged benchmark run
must too.

Keep a copy of the handover beside the run: the binary deletes the original with
`close(79,status='delete')`.

## 4. ON A COLD START THE COMMITTED `newborn_parent_share.dat` IS DEAD

Measured, not read off the source: neither `newborn_parent_share resumed:` nor
`no banked newborn parent shares` appears anywhere in the benchmark's log, so
that read never executed.

The reason is that the read is NESTED inside the `calibration_state.dat` reader's
own `if (state_ios_1==0)` chain (unit 72). No state file, no read -- even though
`newborn_parent_share.dat` has its own unit and its own `iostat`, and even though
it is deliberately un-gitignored precisely so a rebuilt container can have it.
The `.gitignore`'s comment says two container rebuilds cost a loop each before
that exception was added; on a COLD start the exception buys nothing, because the
only path that opens the file is the resume path.

So a cold run's first distribution is built with every parent clean and housed --
the print confirms it, `newborn_parent_share (clean housed, ...) = 1.0 0 0 0` --
and the intergenerational channel is switched off until the aggregation rebuilds
it. **That costs a block, not correctness**, and the frozen stopping test is a
move BETWEEN CONSECUTIVE BLOCKS over b, lambda_d, h_1 and average labour income,
so a block-1 transient cannot satisfy it and cannot be mistaken for convergence.

It is written down rather than fixed: the model is frozen, and this is a block of
wall clock, not a wrong number. What it does mean is that **copying
`newborn_parent_share.dat` into a cold run directory is a no-op** and should not
be counted as having warm started anything.
