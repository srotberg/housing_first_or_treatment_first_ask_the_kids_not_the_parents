# ROUND 1, PASS 2, BATCH A -- pi_V and cbar, borrowing off

Three points, run in sequence on one economy without a rebase between them.
Line 1 is the anchor and the control; lines 2 and 3 each move ONE instrument
off it.

## All three points are on the same model

    point_f9c16d5308.r2a_anchor   MODEL b8dc1077ad   line 1, ANCHOR
    point_9724dc31eb              MODEL b8dc1077ad   line 2, pi_V arm
    point_531868d8bd              MODEL b8dc1077ad   line 3, cbar arm

**The three MODEL lines agree.** They were confirmed equal before any of the
numbers below were compared, so the arms are differences in the instrument and
not differences in the Fortran. `INVARIANTS: all PASS` on all three.

The anchor is committed as `point_f9c16d5308.r2a_anchor.txt` and not at the
plain tag path, because `point_f9c16d5308.txt` already holds RUN3 of the
determinism study and the two are byte-for-byte different runs. Read the last
section before using either.

Borrowing is off throughout (`include_unsecured_borrowing=0`).

## Arm 1 -- pi_V, instrument `probability_of_voucher_benchmark_used`

    instrument   anchor 0.024723   ->   arm 0.048000
    pi_V         anchor 0.179386   ->   arm 0.270715
    target                              0.266

**BRACKETS.** 0.179386 < 0.266 < 0.270715. The target lies between the two
measured points, close to the arm end.

Previous pass, for the record: 0.0247 -> 0.0388 gave 0.179 -> 0.241, short of
the target. Doubling the step to 0.048 carried pi_V past it.

## Arm 2 -- cbar, instrument `max_food_cost`

    instrument   anchor 0.0136     ->   arm 0.0080
    cbar         anchor 0.0085982  ->   arm 0.0045596
    target                              0.0042

**DOES NOT BRACKET. Both points fall ABOVE the target.** The lower of the two,
0.0045596 at `max_food_cost=0.0080`, is still above 0.0042.

The direction is now right. The previous pass moved the instrument UP
(0.0136 -> 0.0196) and got 0.00860 -> 0.01352, away from the target; this arm
moved it DOWN and cbar fell with it. It did not fall far enough to cross.

The gap remaining is small next to the step just taken -- the arm closed
0.00404 of distance and 0.00036 is left -- but **no instrument value is
projected here**. Extrapolating past the measured arms has been done on this
branch repeatedly and has been wrong every time. What is established is the
bracket side, not the root.

## aleph moved under both arms -- the previous pass's finding REPEATS, with one caveat

Neither instrument owns aleph. Both moved it.

    anchor            aleph = 50.6280
    pi_V arm          aleph = 51.4513     +0.8233
    cbar arm          aleph = 47.5789     -3.0490

The cbar arm moves aleph DOWN, the pi_V arm moves it UP, and the cbar arm is
much the larger disturbance. aleph's own target is 80, so both arms are moving
a moment that is already far short, and the cbar arm moves it further away.

**The arms are not orthogonal.** This is the second pass in a row to find it,
under the same two instruments.

**The caveat, and it is not small.** The noise floor these deltas should be
read against is NOT the 1.9e-05 that `DETERMINISM.md` documents for aleph. This
anchor sits 0.294 away from that study's three-run baseline on the identical
vector (last section). Against that 0.294:

- the cbar arm's **-3.049 is about ten times it and is solid**;
- the pi_V arm's **+0.823 is under three times it, and should not be leaned
  on** as an established movement until the anchor discrepancy is understood.

So the non-orthogonality repeats and is firm for cbar. For pi_V it is
suggestive only, on this batch's evidence.

## Other moments that moved

Recorded because an arm that is meant to own one moment moved several. Anchor,
then pi_V arm, then cbar arm.

    moment      anchor        pi_V arm      cbar arm
    h_1         0.082821      0.066765      0.083384
    h_2         0.106685      0.076977      0.106215
    h_3         0.479632      0.502320      0.443187
    beta        2.68832       2.61359       2.76133
    theta       0.331251      0.343489      0.326499
    w_bot       0.030199      0.025495      0.033641
    b           0.396755      0.400957      0.400308
    y_u         0.707466      0.698747      0.710794

The pi_V arm is the one to note: it cut h_1 from 0.0828 to 0.0668 and h_2 from
0.1067 to 0.0770 while doing its job on pi_V. h_2's target is 0.101, so the
anchor sat on it and the arm knocked it off.

The cbar arm leaves pi_V alone (0.179386 -> 0.179244), so the cross-contamination
between these two runs in one direction only.

## THE ANCHOR DOES NOT REPRODUCE THE DETERMINISM BASELINE

This is the finding of the batch that was not asked for, and it bears on
everything above.

`DETERMINISM.md` measured this exact vector three times and returned a verdict
of REPRODUCIBLE: worst relative spread over the 23 targeted moments 5.13e-05,
median 8.80e-06. This batch's anchor is the same vector -- the `VECTOR` line
md5 is `96657e26d534200c25d17a7c8ac8d727` in all four files -- run against the
same source, md5 `b8dc1077adc90fe0d9b497289e93e7c5`, the very build that study
certifies. `nproc` is 4 here, as it was there.

It does not land in the same place. Deviation of this anchor from the mean of
RUN1-RUN3, against that triple's own spread:

    moment      RUN1-3 mean      this anchor     rel dev   triple spread   ratio
    w_bot         0.0294871         0.030199    2.41e-02        1.54e-05    1566
    h_1           0.0841772         0.082821    1.61e-02        1.65e-05     977
    lambda_m       0.025974         0.026345    1.43e-02        1.09e-06   13129
    lambda_d       0.294579          0.29177    9.53e-03        3.48e-05     274
    b              0.399889         0.396755    7.84e-03        2.45e-05     320
    aleph           50.3339           50.628    5.84e-03        1.92e-05     304
    p_m           0.0505164        0.0507276    4.18e-03        8.80e-06     475
    y_u            0.710117         0.707466    3.73e-03        1.43e-05     260
    tau_l          0.234374         0.233623    3.20e-03        3.47e-06     924
    cbar         0.00861663       0.00859817    2.14e-03        2.57e-05      83
    pi_V           0.179213         0.179386    9.62e-04        6.51e-06     148

**22 of the 23 targeted moments sit outside the documented spread, by factors
of 25 to 13,000.** The exception is `sigma_y`, identical to every digit, which
is what `DETERMINISM.md` predicts for it: it is a function of the exogenous
productivity process and sits outside the solved equilibrium.

The shape is the one that study already named. Its `w_bot` section records the
pre-fix economy as **bimodal rather than scattered**, with a low attractor at
0.029486 and a high one at 0.030324 / 0.030328, and attributes it to an
execution-path difference rather than to rounding. This anchor's `w_bot` is
**0.030199** -- near the high attractor, while the certified triple sits at the
low one:

    post-fix triple    0.0294872  0.0294868  0.0294872
    pre-fix low        0.0294860
    pre-fix high       0.0303242  0.0303281
    THIS ANCHOR        0.0301990

That bimodality was supposed to have been closed by `d9ff1a8`, the unset
`age_index` fix, and the source here is the post-fix source. So either the fix
does not close the path difference in every case, or something outside the
`.f90` md5 selects between the two attractors.

**What this does and does not damage.** All three points of this batch ran
back-to-back in one container off one binary with nothing pulled between them,
which is exactly what the anchor is for, so the arms remain matched pairs and
the bracket findings above stand on their own control. What it damages is any
comparison of these numbers against points measured in another container, and
the aleph noise floor, as flagged above.

**What it needs.** A repeat of this vector in a fresh container, and the four
`DIST_DONE` sweep counts and `final_distance` values compared against the
triple's -- those are printed before the `ALL TARGETED MOMENTS` block that
`run_one_point.sh` keeps, so they must be captured from the worker log while
the run is live. `DETERMINISM.md` found them bit-identical across its three
runs; if they differ here, the execution path differs and that localises it.
Not done in this batch, which was three points and no spare run.
