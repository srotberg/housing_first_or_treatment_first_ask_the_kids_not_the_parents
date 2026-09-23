# omega_c SCAN -- RUNNING READINGS

The benchmark, calibrated once at omega_c = 0 and published under
`code/scan_seed/`:

    b        0.098916    (total drug-user share)
    lambda_d 0.043579    (disorder rate)

Every point HOLDS that vector and only raises omega_c
(`freeze_all_but_omega_c 1`, `omega_c_is_pinned 1`), so the fall in b is the
reduction. The author is looking for the omega_c that gives 18 per cent.

## HOW TO READ THIS TABLE

**An early block is not an answer.** A scan point is a restart, and
`bequest_residual` is a model output that `calibration_state.dat` cannot bank,
so it re-converges from scratch and drags newborn assets, the wealth
distribution and hence drug use with it. The benchmark itself swung thirty
points across this transient.

**WHICH WAY AN EARLY BLOCK IS WRONG IS NOT KNOWN, and an earlier version of
this file asserted it was.** That version said the readings shrink as blocks
settle, so every early reading overstates the reduction. It was inferred from
0.075's block 1 at -28 per cent against 0.065's block 5 at -15, which is a
comparison of TWO DIFFERENT POINTS and says nothing about a trajectory. Inside
a single point the movement runs the other way so far:

    0.065   block 5   b ~ -15%
    0.065   block 9   b = 0.0808, -18.3%

The reduction GREW by three points between those blocks. So a raw early
reading is untrustworthy in size, not reliably biased in a known direction,
and the correction has to come from the control rather than from a rule of
thumb about early blocks.

**The control is the instrument.** At omega_c = 0 the same frozen path runs
with no policy change, so its distance from 0.098916 IS the transient. Only
the part of a raised point's move that exceeds the control's belongs to
omega_c. Nothing here is reportable until the control has blocks to compare.

## READINGS

    time   omega_c   block     b vs 0.098916   lambda_d vs 0.043579   source
    20:28  0.075     1         -28.4%          --                     session summary
    21:20  0.065     5 of ~9   ~-15%           ~-18%                  session summary
    22:21  0     ctrl 4         -4.0%           -5.9%                  session summary
    22:25  0.065     9 of ~11  -18.3%          --                     b=0.0808, MOVE 3.0e-3
    22:41  0     ctrl 5         -5.0%           --                     b=0.094, deviation GROWING
    22:46  0.075     7         -20.6%          --                     b=0.0785, metric stalled then rose

## THE STOP RULE, FIXED FOR EVERY POINT SO THEY STAY COMPARABLE

The 0.075 point asked for one at 22:46, having hit the benchmark's own
stall-then-rise (its metric fell to 0.0254 and turned). The rule given to it,
and to be given to every point:

    Stop when |b(k) - b(k-1)| / b(k-1) < 0.5 per cent for TWO CONSECUTIVE
    blocks, or at block 12, whichever comes first.
    Never stop on block_move alone, in either direction.
    When stopping, report the last THREE blocks' b so the wander is visible.

Two consecutive blocks, because one quiet block is not arrival. Block 12 as a
cap, because the benchmark never fired the 0.001 rule at all.

## MONOTONICITY HOLDS SO FAR

    omega_c 0.065   block 9   b = 0.0808
    omega_c 0.075   block 7   b = 0.0785

b falls as omega_c rises, which is the direction the mechanism predicts. The
0.08 point has reported ten convergence distances and no moment at all, so it
cannot extend this yet; it has been asked for b.

## THE BENCHMARK IS A HAND-STOPPED SNAPSHOT, NOT A RESTING POINT

The control's deviation is GROWING, not decaying:

    control  block 4   b = 0.095   -4.0%
    control  block 5   b = 0.094   -5.0%

It is not returning to 0.098916, and the reason is in this project's own
record. The two-class benchmark was STOPPED BY HAND at block 11, deliberately,
because `block_move` had collapsed to 0.00513 and then risen again (0.016,
0.036) so the 0.001 rule would never fire -- and b was still wandering when it
was stopped, -0.7 then -2.3 then -5.8 per cent across the last three blocks.

So b = 0.098916 is a SNAPSHOT of a run that had not settled. The control,
allowed to run on, is walking to wherever the frozen system actually rests.
The gap between the two is not a transient decaying to zero; it is the
distance between a hand-stopped reading and the system's resting point.

**The consequence is the whole reason the control exists.** A scan point must
be measured against the CONTROL AT THE SAME DEPTH, never against 0.098916:

    0.065 at b = 0.0808, against the snapshot 0.098916     -18.3%
    against a control that settles at 0.095                -15.0%
    against a control that settles at 0.094                -14.0%
    against a control that settles at 0.093                -13.1%

Both numbers are still moving, so none of those is the answer. But the
correction is large -- four to five points -- and it runs one way: measured
properly, the reduction at a given omega_c is SMALLER than the raw table says,
so the omega_c delivering a true 18 per cent is HIGHER than 0.065.

That is the same conclusion an earlier version of this file drew and then
withdrew. It was withdrawn because it rested on comparing two different
points' early blocks, which was not evidence. It is restated here on the
control's own trajectory, which is.

## THE CONTROL HAS A NUMBER, AND IT IS NOT ZERO

At 22:21 the control reported block 4 at b -> 0.095 and lambda_d -> 0.041,
which is -4.0 and -5.9 per cent from the benchmark WITH NO POLICY CHANGE AT
ALL. Both figures come from a summary that rounded to three digits, so treat
them as approximate, and the control is still moving (block move 0.039).

That is the restart transient, measured rather than assumed, and it is the
reason no raw point reading should be quoted as a reduction. Subtracting it
from the one comparable point:

    0.065 at block 5     raw -15%     control at block 4  -4%     net ~ -11%

PROVISIONAL, and not to be reported to the author as a result, for three
reasons. The control has not settled, so -4 per cent is itself a moving
number and should go to zero. The two readings are one block apart rather
than matched. And a difference of rounded numbers carries the rounding of
both.

The claim first written here -- that the correction makes the answering
omega_c HIGHER -- rests on the control's -4 per cent surviving to its own
settled block, and that is exactly what is not yet known. State the two
outcomes instead, and wait:

    if the control settles at 0%, 0.065's -18.3% is all policy and 0.065 IS
    the answer to the author's question;
    if it settles near -4%, 0.065 nets about -14% and the answer lies above
    0.065.

Both hinge on the control, which is four blocks behind the point it has to be
compared with. Match the block depth before subtracting.

## IN FLIGHT

    omega_c   session                             state at 21:21
    0         session_016NSzSjqdS8bkRsa51S5fbk    block 4, b 0.095, move 0.039
    0.055     session_016XoU7o6mG64ktEiJ8y1da3    block 6, move 0.0231
    0.06      session_01L9UR4QYx4b8S6CXqZS8JQ7    block 9 of ~12
    0.065     session_013vxekwRecnZLSY6nyycP2T    block 5 of ~9
    0.07      session_01WtwzuCmJ6Ko5fro63GAXvc    block 2, bequest_residual 1.63
    0.075     session_01X8T8hReZpctbPNBCLLCWCE    block 5 complete
    0.08      session_01Kdtds1VF5DyzFY8F4BsZbA    block 8 of ~12, distance 5.82e-3

## bequest_residual IS THE SETTLE INDICATOR

The 0.07 point reported 1.63 at 22:13. The benchmark settles at 1.4771 and,
after a restart, walked back 2.1528, 1.8655, 1.6459. A point whose residual
is still well above about 1.48 has a b that is still moving for reasons that
have nothing to do with omega_c, whatever its block count says. Ask for it
alongside b.
