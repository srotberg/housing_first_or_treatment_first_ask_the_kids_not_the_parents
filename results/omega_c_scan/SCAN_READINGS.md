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

## IN FLIGHT

    omega_c   session                             state at 21:21
    0         session_016NSzSjqdS8bkRsa51S5fbk    solving, launched 21:07, no block yet
    0.055     session_016XoU7o6mG64ktEiJ8y1da3    block 3, BLOCK MOVE 0.085258
    0.06      session_01L9UR4QYx4b8S6CXqZS8JQ7    computing distances off its log
    0.065     session_013vxekwRecnZLSY6nyycP2T    block 5 of ~9
    0.07      session_01WtwzuCmJ6Ko5fro63GAXvc    block 1, converging to block 2
    0.075     session_01X8T8hReZpctbPNBCLLCWCE    solving, reporting at exit
    0.08      session_01Kdtds1VF5DyzFY8F4BsZbA    block 3, distance 0.0854 vs a 1e-3 rule
