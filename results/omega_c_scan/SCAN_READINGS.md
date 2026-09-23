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
points across this transient. The readings below shrink as blocks settle,
which is the transient decaying, not the policy weakening.

**The control is the instrument.** At omega_c = 0 the same frozen path runs
with no policy change, so its distance from 0.098916 IS the transient. Only
the part of a raised point's move that exceeds the control's belongs to
omega_c. Nothing here is reportable until the control has blocks to compare.

## READINGS

    time   omega_c   block     b vs 0.098916   lambda_d vs 0.043579   source
    20:28  0.075     1         -28.4%          --                     session summary
    21:20  0.065     5 of ~9   ~-15%           ~-18%                  session summary
    22:21  0     ctrl 4         -4.0%           -5.9%                  session summary

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

What it does settle is the shape of the answer: the raw readings overstate
the reduction by several points, so the omega_c that delivers a true 18 per
cent is HIGHER than a naive reading of the raw table would suggest.

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
