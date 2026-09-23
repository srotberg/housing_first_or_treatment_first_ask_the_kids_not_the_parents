# b_smi sweep, point 0.5

    b_smi_multiple      0.5
    blocks completed    6, last BLOCK MOVE 1.3666e-2  (rule 1e-4)
    MOMENT r_smi        2.38354   against 7.30
    SUD | SMI           0.14356   derived, see below
    SUD | non-SMI       0.06023   derived, see below   <- THE CONTROL
    b                   0.154898  against 0.10502
    lambda_d            0.064195  against 0.043424
    model_fraction_homeless   0.0070342   NOT at zero

No corner. Participation 0.155 (not near zero, not near one), homelessness
0.0070, SMI share 0.0476, SMI share of the homeless 0.254. The moments are
measuring something.

At a multiple of 1.0 the ratio is about 1.78. Halving it to 0.5 buys 2.38, so
the channel moves the ratio the right way and reaches about a third of the 7.30
target. The response over this interval is roughly +0.6 in the ratio per halving
-- far too slow to reach 7.30 by halving alone if it stays log-linear, which is
exactly what the lower points exist to test.

## READ IT AT BLOCK 6, NOT BLOCK 1

The ratio DRIFTS DOWN as the equilibrium settles, and by a lot:

    block 1     r_smi 2.65697     block 6     r_smi 2.38354      -10.3 per cent

This is the effect ENGINE.md records -- a loop's moment print is one iterate,
not an equilibrium. Reading this point at block 1 would overstate the ratio by a
tenth. **The four points must be compared at the same block**, and block 1 is
the wrong one.

## THE CONTROL IS WHAT MOVES, AND THIS MATTERS FOR THE DESIGN

Decomposing the two rates across blocks:

    block 1     SUD|SMI 0.14312     SUD|non-SMI 0.05387
    block 6     SUD|SMI 0.14356     SUD|non-SMI 0.06023

SUD|SMI is FLAT to three decimals (+0.3 per cent). SUD|non-SMI rises 11.8 per
cent. So within this point the ratio falls entirely because the CONTROL moves,
not because the treated group does.

That is a settling effect, not a `b_smi_multiple` effect -- the multiple is held
(adjuster 0) and cannot move between blocks. But it means the control is NOT a
fixed quantity as the solve converges, so the cross-point test the sweep is for
-- "SUD|non-SMI should be near constant across the four points" -- is only
readable if all four points are read at the same block AND are equally
converged. A point stopped at a different BLOCK MOVE will show a different
control for reasons that have nothing to do with its multiple. Compare the four
at block 6, and compare their last BLOCK MOVE before believing the control.

## The two rates are DERIVED, not printed

The model prints only the ratio. `r_smi` is built at line 11127 from four
cross-tab masses (`xtab_sud_mass_smi`, `xtab_mass_smi`, `xtab_sud_mass_pop`,
`xtab_mass_pop`) and none of the four is ever written to the log, so the levels
cannot be read directly. They are backed out of

    lambda_d = p_m * (SUD|SMI) + (1 - p_m) * (SUD|non-SMI)
    SUD|SMI  = r_smi * (SUD|non-SMI)

with `MOMENT lambda_d` = 0.0641947 and `MOMENT p_m` = 0.0476047. It reproduces
lambda_d to 8 decimals by construction, so it is not a check on itself. It is
exact only if the cross-tab's population base is the same as
`model_fraction_addicted`'s, which was not verified. Giving those four masses a
print is a one-line source edit and would put the control on a firm footing for
all four points; it was not made here because the brief forbids changing the
design mid-sweep.

## Verification, in this run's own log

    HANDOVER b_smi_multiple:                1.0000000000000000  ->  0.50000000000000000
    HANDOVER b_smi_multiple_adjuster:       0.0000000000000000  ->  0.0000000000000000
    HANDOVER freeze_all_but_omega_c:                         0  ->           1
    HANDOVER voucher_conditional_on_clean:                   0  ->  0.0000000000000000
    survival: clean housed vs SMI homeless with SUD at age 40 =
        0.98719030618667603   0.88727469276301107

`HANDOVER IGNORED` count 0, `no calibration_state.dat` -- cold. Benchmark, not
Treatment First. Zero `budget does not clear` lines over the whole run.

## THE WARM RESUME IS BROKEN. DO NOT RESUME THIS MODEL -- RESTART IT COLD.

Paid for twice tonight, and it is the most useful thing this point found.

The container rebooted at 00:51:47 and again at 01:17:44, both times within a
second of a scheduled check-in firing. The first reboot killed the cold run
after block 1; it was relaunched warm from `calibration_state.dat` per the
ENGINE rule, which says not to restore PARAM_HANDOVER on a resume. **The warm
run came back as a different economy and said nothing about it:**

                    cold block 1        warm block 1
    b               0.145009            0.952517
    lambda_d        0.058016            0.000000
    r_smi           2.65652             0.000000     (the guarded corner)
    stopping rule   1.0000e-004         0.0000000    <- the tell
    budget lines    0                   416,517

`b ~ 0.95, lambda_d = 0` is the signature `launch_arm.sh`'s own comment names
for *"a naive restart silently runs the Fortran's declared values while looking
perfectly healthy"*. The log printed `resumed from calibration_state.dat,
written after loop 2` and the parameters did not come back with it. The
216,937-line `budget does not clear` burst that followed -- a constant
1.9999999552965164E-002, which is float32 `0.02` promoted to double, on street
households -- is a SYMPTOM of that wrecked economy, not a separate defect: the
cold run prints zero such lines from the same binary.

So the standing rule "on a resume do NOT restore PARAM_HANDOVER" is correct
about the handover and wrong about the outcome here: the state file did not
carry the run. The recovery is a genuinely cold restart -- delete
`calibration_state.dat`, `resume_seed.dat`, `newborn_parent_share.dat` and the
`calibration_distribution*.dat` set, restore `PARAM_HANDOVER.txt` from the
`.kept.txt` copy, and relaunch. That is what produced the numbers above, and its
block 1 reproduced the first cold run's block 1 to four significant figures
(r_smi 2.65697 vs 2.65652, b 0.145002 vs 0.145009), which is the evidence that
the cold path is sound and the warm path is not.

**The `.kept.txt` copy is what made this recoverable, twice.** It is not
ceremony.

## Cost and timing, for the other three points

    cold start -> block 1     ~5.5 minutes
    each block after          ~3 minutes
    six blocks                ~23 minutes total

Compute only survives while a turn is open. Both reboots landed on an idle
session at a check-in firing, so a 20-minute check-in is not a safety net here
-- it is the event that ends the run. Hold the turn and take the six blocks in
one sitting.
