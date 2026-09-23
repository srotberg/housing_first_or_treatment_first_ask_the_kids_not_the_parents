# b_smi sweep, point 0.05

23 September, 01:46 UTC. Run dir `code/b_smi_0p05/` (gitignored), source
5de3d99, `-O3` binary copied in. Benchmark, not Treatment First.

## NOT THE CORNER THAT WAS EXPECTED, BUT A CEILING

SMI participation is nowhere near one: `SUD | SMI` is **0.2093**. The moment is
not at the boundary the brief warned about.

It is at a different one. `SUD | SMI` sat in [0.2093, 0.2105] across all eight
blocks -- a range of 0.5 per cent -- while `lambda_d` moved 10 per cent and
`SUD | non-SMI` moved 11 per cent. Every bit of the ratio's movement over the
run came from the DENOMINATOR. Against the 1.7792 recorded at a multiple of
1.0, a twentyfold cut in the multiple bought a factor of 1.85 in the ratio and
stopped there.

So the response is real and correctly signed -- `r_smi` RISES as the multiple
FALLS -- but it is sublinear and appears to be running into a ceiling on the
SMI rate itself. If 0.01 also returns `SUD | SMI` near 0.21, the multiple
cannot reach 7.30 at any value and the distance has to come from somewhere
else.

## THE NUMBERS

    b_smi_multiple            0.05
    blocks completed          8, last BLOCK MOVE 9.3597e-3 (under the 1e-2 rule)
    MOMENT r_smi              3.2996        against 7.30
    SUD | SMI                 0.20931       derived, see below
    SUD | non-SMI             0.06343       derived, see below
    b                         0.17338       against 0.10502
    lambda_d                  0.070323      against 0.043424
    model_fraction_homeless   0.0074271     NOT at zero
    p_m                       0.047229      (input to the derivation)

`r_smi` by block: 3.6633, 3.5906, 3.5762, 3.3317, 3.2788, 3.2749, 3.2850,
3.2996. `BLOCK MOVE` halved each block from block 4: 0.2078, 0.0855, 0.0393,
0.0189, 0.00936.

## THE TWO RATES ARE DERIVED, NOT READ

The steady-state moment block prints `r_smi`, `lambda_d` and `p_m` but NOT the
two conditional rates; the four raw masses are printed only on the transition
path (`TRANSITION SMIDRUG`). Rather than add a diagnostic `write` and make this
binary differ from the other three points', both rates are recovered from

    lambda_d = p_m*(SUD|SMI) + (1-p_m)*(SUD|non-SMI)   with  r_smi = ratio

which is exact given those three. It assumes `model_fraction_addicted`'s
divisor and `model_smi_prevalence`'s base coincide with the `xtab_*` masses
`r_smi` is built from; they are accumulated in different subroutines. If a
sibling prints the rates directly, theirs supersede these. The three inputs are
above so the arithmetic can be redone.

## THE CONTROL NEEDS THE POINTS READ AT THE SAME CONVERGENCE

`SUD | non-SMI` is NOT stable within a point while the equilibrium settles: it
ran 0.05714, 0.05850, 0.05876, 0.06319, 0.06404, 0.06401, 0.06376, 0.06343
over the eight blocks, a rise of 11 per cent, and it was still drifting when
`BLOCK MOVE` reached 9.4e-3.

So comparing `SUD | non-SMI` across the four points only means something if the
four are read at a comparable `BLOCK MOVE`. A point stopped at six blocks
(`BLOCK MOVE` around 0.04) reports a control roughly 1 per cent lower than the
same point stopped at eight, for no reason connected to `b_smi_multiple`. Read
the control against the block count, or the sweep will manufacture a leak it
has not found -- or hide one it has. This point is quoted at `BLOCK MOVE`
9.4e-3.

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
