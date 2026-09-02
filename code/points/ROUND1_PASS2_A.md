# ROUND 1, PASS 2, BATCH A -- pi_V and cbar, borrowing off

Three points, run in sequence on one economy without a rebase between them.
Line 1 is the anchor and the control; lines 2 and 3 each move ONE instrument
off it.

## All three points are on the same model

    point_f9c16d5308   MODEL b8dc1077ad   line 1, ANCHOR
    point_9724dc31eb   MODEL b8dc1077ad   line 2, pi_V arm
    point_531868d8bd   MODEL b8dc1077ad   line 3, cbar arm

**The three MODEL lines agree.** They were confirmed equal before any of the
numbers below were compared, so the arms are differences in the instrument and
not differences in the Fortran. `INVARIANTS: all PASS` on all three.

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

## aleph moved under both arms -- the previous pass's finding REPEATS

Neither instrument owns aleph. Both moved it.

    anchor            aleph = 50.6280
    pi_V arm          aleph = 51.4513     +0.8233
    cbar arm          aleph = 47.5789     -3.0490

The cbar arm is the larger disturbance, and it moves aleph DOWN while pi_V
moves it UP. aleph's own target is 80, so both arms are moving a moment that is
already far short, and the cbar arm is moving it the wrong way and by a lot
more than the pi_V arm is moving it the right way.

**The arms are not orthogonal.** This is the second pass in a row to find it,
under the same two instruments.

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
