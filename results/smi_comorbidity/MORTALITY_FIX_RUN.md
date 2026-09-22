# The mortality double count fix, run at the calibrated point

22 September. The author: *"run the calibrated model with it, and see how much
it changes about the SMI and drug use and SUD"*, *"no need to recalibrate, let's
just see how it affects the model with the parameters we already fixed"*, and
then *"you should run the benchmark with the change without the transition"*.

## The first attempt was wrong and produced nothing, which is why it is recorded

`code/bench_mortfix/` was created empty and the patched binary started in it.
The binary printed

    no calibration_state.dat, starting from the declared values
    no warm start distribution, initialising from the age one cross section

and both lines are fatal to the exercise, for different reasons.

**THE DECLARED VALUES ARE NOT THE CALIBRATED POINT.** They are the declaration's
starting guesses, and they are far from it:

    relative_share_of_housing   declared 0.278    calibrated 0.53560465
    labor_income_tax_rate       declared ~0.69-0.75  calibrated 0.89353149
    discount_factor             declared 0.944    calibrated 0.94653324
    kappa_find_smi              declared 1.0      calibrated 10.791363
    addiction_onset_base        declared 0.0      calibrated 0.03360068

A run from there measures the declared point, not the mortality fix. Forty-one
minutes of it were thrown away; it had reached its first moment block, which
printed `model_fraction_addicted= 0.0`, and that zero is the declared point's
own, not a result. The log is kept as `bm_run_coldstart_discarded.log`.

**A BENCHMARK DIAGNOSTIC MUST BE SEEDED, AND THE SEED IS NOT THE ONE IN
`code/`.** `code/calibration_state.dat` is 15 September and is also not the
calibrated point. The calibrated point is `code/t45_nogf/PARAM_HANDOVER.kept.txt`,
the 102-line vector the reference benchmark was actually solved at, kept because
the binary deletes `PARAM_HANDOVER.txt` as it reads it.

## How it is seeded, and why this makes it a control rather than a comparison

    cp ../t45_nogf/PARAM_HANDOVER.kept.txt PARAM_HANDOVER.txt
    cp ../t45_nogf/calibration_distribution{1,2}.dat .
    cp ../t45_nogf/calibration_distribution_shape.dat .
    rm -f calibration_state.dat resume_seed.dat

The warm start is not merely *a* benchmark distribution. It is byte identical to
the one the 0.596 / 0.126 / 0.317 were read off:

    md5  c35f79f594346bd45b55d741bdd8acbd  t45_nogf/calibration_distribution1.dat
    md5  c35f79f594346bd45b55d741bdd8acbd  t45_nogf/distribution_stationary1baseline_benchmark.dat

and the binary confirmed it on load:

    warm start distribution loaded, sum=   50.861206888360229

against the reference's 50.861206888360229. Same parameters, same starting
distribution, one line of the survival table different. Anything that moves is
the fix.

## The control that must not move, stated before the run

ENGINE.md's corollary for controls: re-measure the vector the change should not
touch and state the reference BEFORE the run. The survival print gives it for
free, and it is exact.

                                      unpatched      patched
    clean housed, age 40         0.98719030618667603  0.98719030618667603
    SMI homeless w/ SUD, age 40  0.79504489593274741  0.88727469276301107
    cells clipped to zero           2 of 472             0 of 472
    smallest probability            0.00000              0.33280

The clean-housed cell is identical to the last digit, which is the no-op control
passing on equality rather than at 1e-4. The comorbid cell's DEATH probability
falls from 0.20496 to 0.11273, down 45 per cent: that is the double count -- the
SMI multiplier had been charged on the addiction and homelessness excesses as
well as on the baseline hazard, and now is charged only on the baseline.

## What is being measured

    ratio of SMI rate to non-SMI rate     reference (unpatched)
    SUD                                   0.596
    uses, no SUD                          0.126
    uses at all                           0.317

The question is whether removing the artificial mortality penalty raises them.
It cannot be expected to close them: the fix removes a suppressor, it does not
add a channel, and the gaps are large. If they move a few per cent, the
self-medication work in `WHAT_TO_ADD.md` is sized against what is left, which is
the sequencing that file already argues for.

## Run record

    launched  19:31:43 UTC, pid 28587, detached (setsid, ppid 1, own pgid)
    binary    hftf_bm, md5 473c983e4054a543cc18ab973aec3efb
    source    bm.f90, patched by code/patch_mortality_smi.py
    log       code/bench_mortfix/bm_run.log

## FIRST BLOCK, 19:45. THE SIGN FLIPS. NOT CONVERGED -- READ THE CAVEAT.

The run writes `calibration_distribution{1,2}.dat` at the end of each block, and
those decode exactly as the stationary files do. Block 1's, against the
reference's own checkpoint, by the same script on both sides:

                   mass      SMI share  SUD rate | SUD|SMI  SUD|non   ratio
    REFERENCE    50.861207    0.048291  0.033609 | 0.02043  0.03428   0.596
    PATCHED b1   50.868662    0.048209  0.030655 | 0.05657  0.02934   1.928

The reference row reproduces the four published numbers to every digit shown,
which is the check that the script is the same one that produced 0.596.

**SMI households go from carrying SUD at 60 per cent of the population rate to
carrying it at 193 per cent.** `SUD|SMI` nearly triples, 0.02043 -> 0.05657.
The sign of the model's comorbidity is no longer the opposite of the data's.

**THE CAVEAT, AND IT IS NOT SMALL.** This is block 1 of a warm start. The block
printed `BLOCK MOVE 1.0000 against a rule of 1.0000E-004`, so the economy is one
pass from the reference and nowhere near a fixed point; the drug price has not
re-cleared and neither has the budget. The DIRECTION is established -- a 45 per
cent cut in the comorbid cell's death probability is not a subtle intervention
and it moves this ratio hard -- but the MAGNITUDE is not, and 1.928 should not
be quoted anywhere until the solve converges.

Two things in the row are worth flagging before then.

**Total mass rises, 50.861207 -> 50.868662.** Tiny, and the right sign: fewer
deaths in the comorbid cells means slightly more people alive. It is a check
that the patch did what it says rather than a result.

**The NON-SMI SUD rate falls, 0.03428 -> 0.02934, and the patch does not touch
non-SMI survival.** So this is either a general-equilibrium channel -- a
non-SMI household's continuation value includes the SMI states it may transit
into, those states got less deadly, its value of life rose and its drug use
fell -- or it is simply block 1 being far from converged. `mu_m=0.82` makes the
first mechanism real rather than hypothetical, but a 14 per cent fall is large
for it, and the aggregate SUD rate falling while the SMI rate triples is exactly
what an unconverged block looks like. DO NOT explain this until it converges;
it was explained wrongly once already in this file's parent.

The `uses, no SUD` and `uses at all` ratios -- 0.126 and 0.317 -- need the
policy function, which is only written when the solve finishes.
