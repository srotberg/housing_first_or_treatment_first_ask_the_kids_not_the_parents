# THE CHAIN IS VERIFIED END TO END. T=60 REMAINS HELD.

21 September. Everything upstream of the transition has been rebuilt in a fresh
container and scored against known numbers. This file is the evidence.

## THE FOUR LINKS, AND WHAT EACH WAS SCORED AGAINST

    1. gfortran 13.3.0, not in the image        3 builds clean each time
    2. benchmark, cold from resume_seed.dat     ECONOMY IS STILL, block 25
    3. arm 3, warm from 2                       simulation_ended, 9 blocks
    4. T=5 grandfathered probe                  the t=0 mapping, against counts

## LINK 2: THE BENCHMARK

`ECONOMY IS STILL` at block 25, `BLOCK MOVE` 9.4302e-5, against n90's block 27 at
8.646e-5. 213 `baseline_benchmark` files, the count the archive's README records,
at matching byte sizes.

                        this run      n90           miss
    b                   0.081812      0.081740      +0.088%
    lambda_d            0.033610      0.033625      -0.044%
    h_1                 0.006458      0.006458      -0.006%
    V                   0.494481      0.494427      +0.011%
    drug shifter        1.619894      1.620015      -0.007%

The four-series decomposition tracked n90's recorded one column by column AND
handed over from `y` to `lambda_d` as the binding series at block 7 in both, which
is the feature the recipe singles out as the one an estimate got wrong.

Nothing moved under the freeze: 3 of 96 names in the written `resume_seed.dat`
differ from n90's, and all three are the ones deliberately overridden.

## LINK 3: ARM 3

See `results/arm3_reproduction/RESULTS.md`. b -0.05%, lambda_d -0.25%, h_1 -0.32%,
price +0.09%, pi_v -1.13%, lifetime welfare -0.001%. It passed CONVERGED.md's own
acceptance test -- |db| monotone into the stop over four readings, b inside the
cycle band, all three live rules inside.

The CEV is +3.4337% against the archive's +3.249%, and that +0.185pp was
PREDICTED at +0.182pp before the run finished, from the welfare curve offset.
See `CEV_OFFSET.md`.

## LINK 4: THE T=5 GRANDFATHERED PROBE -- THE t=0 MAPPING AGAINST COUNTS

The startup verification the brief requires, and it passes:

    TRANSITION GF: holders before=                     3.6183336317475669
    TRANSITION GF: stationary slot-0 mass before/after= 0.0   3.6183336317475669
    TRANSITION GF: grandfathered= 3.6183336317475669  left in state 1= 0.0
    TRANSITION GF: terminal value for the grandfathered state filled from the
                   ordinary holder
    DRUG PRICE PATH seeded FROM FILE, entries read= 4 of 4

                            reference     this chain    miss
    grandfathered mass      3.6187        3.61833       -0.010%
    total population       50.8612       50.861572      +0.0007%
    grandfathered share     ~7.1%         7.116%
    left in state 1         0.0           0.0           exact
    h_1 at t=1              0.008747      0.0087462     -0.009%

**h_1 at t=1 is the strongest single check in this whole exercise.** It depends on
the re-solved benchmark, the re-solved arm 3 as the terminal condition, the
mapping into voucher state 4, the price seed, and a complete backward-then-forward
pass. It reproduces to nine parts in a hundred thousand, so nothing in that chain
is silently wrong.

The mass checks are COUNTS over the benchmark's own distribution, which is why
they are the right control: a compiler cannot move them, and the pending voucher
fix cannot either.

All three of the mapping's arrays show the move -- holders before 3.61833, state 1
left at exactly zero, the stationary slab carrying the mass -- so the fix of
20 September that maps every array holding the initial condition is working, with
the Aitken buffers correctly left alone.

## THE MEMORY MODEL IS CONFIRMED, AND THE LESSONS FILE'S FIT WOULD HAVE BEEN WRONG

    predicted at T=5 by 7.3 + 0.0967*T      7.78 GB
    MEASURED peak RSS at T=5                7.93 GB       +1.9%

So the grandfathered fit through the two points in `grandfather_voucher_states`'
declaration holds, and T=60 lands at 13.1 to 13.3 GB of 15. The lessons file's
three-state fit `2.91 + 0.079*T` predicts 9.1 GB at T=60 and would have been
wrong by four gigabytes on a box with no swap.

## TWO INCIDENTAL CORRECTIONS

- **The benchmark's drug price is exactly 1.0.** An earlier reconstruction in this
  session inferred 0.99486 by inverting the T=30 ramp arithmetic. That was wrong.
  It does not matter, because the T=60 path is seeded from the file rather than
  the ramp, but the seed file's t=0 anchor is 1.0.
- **A converged arm's last log line is `simulation_ended`, with an UNDERSCORE.**
  Grepping for "simulation ended" returns zero on a good run and reads as a crash.

## WHAT IS STILL HELD, AND WHY THE T=5 PRIOR IS NOT A FLOOR

The T=60 grandfathered transition is NOT launched. The coordinator's voucher
accounting bug is upstream of it and the run would inherit it; grandfathering is
an exemption from a condition, and with vouchers unpaid from t=2 there is no
condition to be exempt from.

Everything is staged and ready: `check_transition_inputs.py` accounts for all 79
required files in the staged directory, parsed out of the Fortran rather than
trusted from the staging script, which also settles that the 211-vs-213 gap
between `counter_TF` and `baseline_benchmark` files is harmless.

**One more reason the +24 per cent prior is not a floor.** The transition computes
its own welfare levels at kappa_x = 0.8139, but the T=5 test differenced them
against n90's benchmark value of 791.3946, written at 0.002. This chain
differences against a consistent 791.3236. That mechanically RAISES the fraction
of the t=1 loss that grandfathering recovers, because the same +0.1252 utils is
divided by a smaller total loss. The resulting percentage is deliberately NOT
quoted here: both sides of it still come from runs carrying the voucher bug, and a
number computed on a broken baseline is not worth recording.
