# b_smi sweep, point 0.05

23 September, 01:46 UTC. Run dir `code/b_smi_0p05/` (gitignored), source
5de3d99, `-O3` binary copied in. Benchmark, not Treatment First.

## NO CORNER, AND NO CEILING EITHER

SMI participation is nowhere near one: `SUD | SMI` is 0.2093. The moment is not
at the boundary this point was expected to hit, and the ceiling `1/(SUD |
non-SMI)` is 17.5 at block 1, well above 7.30. Nothing here is a boundary.

## THE READING ONLY MEANS SOMETHING AT A MATCHED BLOCK

This is the first thing to take from this point, because it changes what the
sweep's own table says.

`r_smi` is NOT monotone in the block count. It runs 3.6633, 3.5906, 3.5762,
3.3317, 3.2788, 3.2749, 3.2850, 3.2996 -- it FALLS by 10 per cent as the
equilibrium settles, then flattens. `SUD | non-SMI` rises 11 per cent over the
same blocks, 0.05714 to 0.06343, and was still drifting at `BLOCK MOVE` 9.4e-3.
So a point read at block 1 and a point read at block 8 are not comparable, in
the ratio OR in the control.

`B_SMI_SWEEP.md` lists `sw_02` at 0.20 as a block-1 number. Set beside it:

    multiple   SUD|SMI   SUD|non-SMI   r_smi
    0.20       0.1809    0.0555        3.2589   sw_02, block 1
    0.05       0.2093    0.0571        3.6633   this point, block 1
    0.05       0.2093    0.0634        3.2996   this point, block 8, converged

Compared like with like, 0.20 to 0.05 moves `SUD | SMI` by 15.7 per cent and
`SUD | non-SMI` by 2.9 per cent. **The directional gate passes**: the SMI rate
moves more than five times what the control does, which is what the channel
had to show.

Compare sw_02's block 1 against this point's block 8 instead and the same
interval reads +1.25 per cent -- a tenth of the real response, and it would
look like the channel had died. Every point in the table needs its block count
recorded, and the three earlier rows re-read at a matched one before any slope
is taken off them.

## THE ELASTICITY IS STILL COLLAPSING

On the matched block-1 comparison the log slope over [0.05, 0.20] is **-0.084**,
after -0.579 over [0.50, 1.00] and -0.223 over [0.20, 0.50]. The collapse
`B_SMI_SWEEP.md` identified continues and is not flattening out.

Extrapolating -0.084 from 3.6633 puts 7.30 near `b_smi_multiple` = 1e-5, five
thousand times below this point. As that note says, a falling slope makes any
such figure a lower bound on the distance rather than an estimate. The useful
statement is the qualitative one: on the evidence of four points the multiple
does not reach 7.30 at any value anyone would want to run.

## THE NUMBERS

    b_smi_multiple            0.05
    blocks completed          8, last BLOCK MOVE 9.3597e-3 (under the 1e-2 rule)
    MOMENT r_smi              3.2996        against 7.30      (3.6633 at block 1)
    SUD | SMI                 0.20931       derived, see below
    SUD | non-SMI             0.06343       derived, see below (0.05714 at block 1)
    b                         0.17338       against 0.10502
    lambda_d                  0.070323      against 0.043424
    model_fraction_homeless   0.0074271     NOT at zero
    p_m                       0.047229      (input to the derivation)

`BLOCK MOVE` halved each block from block 4: 0.2078, 0.0855, 0.0393, 0.0189,
0.00936.

## THE TWO RATES ARE DERIVED, NOT READ -- AND THE METHOD IS CHECKED

The steady-state moment block prints `r_smi`, `lambda_d` and `p_m` but NOT the
two conditional rates; the four raw masses are printed only on the transition
path (`TRANSITION SMIDRUG`). Rather than add a diagnostic `write` and make this
binary differ from the other three points', both rates are recovered from

    lambda_d = p_m*(SUD|SMI) + (1-p_m)*(SUD|non-SMI)   with  r_smi = ratio

which is exact given those three. The method reproduces `sw_02`'s numbers,
which `code/smi_sud_xtab.py` decoded independently from
`calibration_distribution1.dat`: 0.0462*0.1809 + 0.9538*0.0555 = 0.061293
against the 0.0613 that run reported. The three inputs are above so the
arithmetic can be redone.

## freeze_all_but_omega_c DOES NOT SURVIVE A RESUME

`b_smi_multiple` and its adjuster persist in `calibration_state.dat` as of
7ce5626, but `freeze_all_but_omega_c` is DECLARED 0 (line 946) and is written
by the handover only. A bare resume therefore comes back with all 47 adjusters
live and reports itself as normal -- the failure ENGINE.md describes as coming
back "a different experiment" saying nothing. Measured here, in the resumed
log:

    HANDOVER b_smi_multiple:            5.0E-002 -> 5.0E-002    state carried it
    HANDOVER freeze_all_but_omega_c:           0 ->        1    state did NOT

So on every relaunch of a FROZEN point, `PARAM_HANDOVER.txt` must be re-placed
from `PARAM_HANDOVER.kept.txt`, against the standing "do not restore it" rule.
That rule guards against throwing away calibrated loops, and here there are
none to throw: the freeze zeroes every calibration adjuster AFTER the state
file and the handover are read, so no calibrated parameter had moved, and
`omega_c` is not a handover name. Confirm `0 -> 1` in the log after each
relaunch. This applies to all four sweep points.

## THE CONTAINER SUSPENDS WHEN THE SESSION GOES IDLE

Two solves died, at 00:53:27 and 01:17:48 by `uptime -s`. Both times the log
stopped 4 to 7 minutes after this session's last activity and the reboot
followed while it waited on a 20-minute `send_later`. Holding the session busy
instead -- a foreground poll loop -- carried the run through 25 minutes and six
blocks with no reboot at all.

`setsid` does not help, as ENGINE.md already says. What helps is not going
idle: hold the session with foreground waits and check in far more often than
20 minutes. The checkpoint is still what saves the run -- each segment above
resumed warm and lost only the block in flight.
