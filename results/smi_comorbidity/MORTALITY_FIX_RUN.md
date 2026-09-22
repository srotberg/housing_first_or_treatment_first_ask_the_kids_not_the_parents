# VOID: THIS RUN SOLVED TREATMENT FIRST, NOT THE BENCHMARK

22 September 20:37. Everything below the line that reports a MODEL number is
wrong and must not be quoted. The run was seeded with
`t45_nogf/PARAM_HANDOVER.kept.txt`, which is the TRANSITION's vector, and that
file sets the policy switches:

    voucher_conditional_on_clean                        0 -> 1
    include_voucher_exclusion                           0 -> 1
    increased_prob_of_voucher_if_homeless_and_addicted  1 -> 0
    adjust_taxes                                        0 -> 1

`voucher_conditional_on_clean` is not gated on `is_counterfactual` -- the
handover is the ONLY thing that sets it, and nothing resets it per phase. So the
solve was a Treatment First economy, compared against a benchmark, and the
comparison confounds the mortality fix with the whole of the policy.

**THE AUTHOR CAUGHT IT BY ARITHMETIC, NOT BY READING THE LOG**: *"why would such
a small change alter the equilibrium so much? It should just raise drug use...
Not lower it."* That is right and it is decisive. The patch lowers the death
probability for SMI households carrying a SUD and touches nothing else; the
control in this very file shows the clean housed cell identical to the last
digit. A fall of a third in AGGREGATE drug use, in a population 95 per cent of
which the patch cannot reach, had no mechanism. Treatment First has exactly that
mechanism, and it is what Treatment First is for.

## VOID

    ratios 1.928 / 2.028 / 2.207 / 2.244
    "the fix flips the sign of the comorbidity"
    SUD rate 0.033609 -> 0.019036 and participation 0.10502 -> 0.046343
    the user-state ratio 0.419 -> 0.810
    every conclusion drawn from them, including the claim that adopting the fix
    forces a drug-block recalibration -- that inference was drawn from TF's
    own effect on the drug block

## NOT VOID

The survival table is read off at build time and no policy switch can touch it:

    clean housed, age 40         0.98719030618667603 both, to the last digit
    SMI homeless w/ SUD, age 40  0.79504489593274741 -> 0.88727469276301107
    cells clipped to zero           2 of 472 -> 0 of 472

The patch itself, the three standing builds, `SMI_BY_SUD_UNIVERSE.md` and
`SMI_SUD_COMORBIDITY_EVIDENCE.md` are all independent of this run and stand.

## HOW IT HAPPENED, SO IT DOES NOT AGAIN

The seeding note below says `PARAM_HANDOVER.kept.txt` is *"the 102-line vector
the reference benchmark was actually solved at"*. That is false. The reference
benchmark was never solved in the T=45 run: it was LOADED from
`seeds/benchmark_dat/`, which the md5 `c35f79f5...` proves -- and that md5 was
checked later, in this same session, without going back to correct the earlier
claim it contradicted.

**A HANDOVER IS NOT A CALIBRATION. IT CARRIES POLICY SWITCHES TOO.** Before
using any `PARAM_HANDOVER*` file, print the switch lines. The benchmark vector
is `seeds/PARAM_HANDOVER_bm_n90repro.txt`; it agrees with the transition's on
every calibrated parameter and differs only on the seven switches. The Fortran
settles the ambiguous one outright: *"a zero here is written out as TF, a one is
written as HF. Default 1 is the benchmark."*

---

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

## BLOCK 2, 19:58. THE RATIO HOLDS; THE LEVEL IS THE NEW PROBLEM

                   mass      SMI share  SUD rate | SUD|SMI  SUD|non   ratio
    REFERENCE    50.861207    0.048291  0.033609 | 0.02043  0.03428   0.596
    PATCHED b1   50.868662    0.048209  0.030655 | 0.05657  0.02934   1.928
    PATCHED b2   50.968664    0.047988  0.023042 | 0.04453  0.02196   2.028

    BLOCK MOVE   1.0000  ->  0.2483     against a rule of 1e-4

The ratio is stable across two blocks while the block move falls by a factor of
four, which is weak evidence that it is converging to something near 2 rather
than passing through it. Both conditional rates are falling; the non-SMI rate
falls faster, so the ratio keeps rising.

**THE LEVEL IS WHAT NEEDS SAYING NOW.** The aggregate SUD rate has gone

    0.033609  ->  0.030655  ->  0.023042      against sud_rate_data = 0.043424

so the fix does not merely redistribute drug use towards the SMI, it cuts the
total by a third and takes lambda_d from 23 per cent below its target to 47 per
cent below. The same is true of participation: b is 0.055967 against a
participation target of 0.10502.

This is not a defect of the fix and it is not a reason to reverse it. The
benchmark was calibrated with the double count IN, so some of what the drug
block's parameters were doing was offsetting an excess hazard that should never
have been charged. Removing it leaves those parameters over-tuned in the other
direction. But it has a consequence for the work the author is weighing:

**ADOPTING THE FIX MEANS RECALIBRATING THE DRUG BLOCK, AND THAT RECALIBRATION
MOVES THE SAME DIAL THE SMI CHANNEL WOULD USE.** Restoring lambda_d and b to
target pushes `addiction_scalar_1` -- the Stone-Geary shifter, the model's `b`
-- DOWN for everyone, because participation is a decreasing function of it. The
proposed SMI channel is a lower `b` for SMI households specifically. The two are
the same instrument at different margins, so the SMI-specific value cannot be
sized against the CURRENT calibration; it has to be sized against the
recalibrated one, or it will be fitted to close a gap the recalibration was
going to close anyway.

Order of work that follows from this, and it is the opposite of the intuitive one:

    1. let this converge                      the ratio and the level
    2. pull the NSDUH SMI x SUD extract       the target the channel answers to
    3. recalibrate the drug block WITH the fix and WITHOUT an SMI channel
    4. read the residual comorbidity gap off THAT benchmark
    5. size b_SMI against the residual, if there is one

Step 3 is a full calibration and is the expensive one. Skipping it is what
produces a self-medication parameter that exists to cancel an arithmetic error,
which is the failure `WHAT_TO_ADD.md` already warned about for the double count
itself.
