# b_smi against the SUD comorbidity ratio: THE MULTIPLE CANNOT REACH 7.30

The economy is the ONE CLASS configuration the author asked for on 22 September:
`child_penalty_classes = 1`, `weight_on_child = 0`, `omega_c` pinned, and SMI
exogenous -- `iota_smi = 1` and `mu_m = 1`, so SMI carries NEITHER a higher SUD
onset risk NOR a lower recovery rate. Every remaining SMI-to-SUD link is
endogenous, through employment and income, plus the Stone-Geary shifter
`b_smi = addiction_scalar_1 * b_smi_multiple` that this sweep moves.

Target: `sud_smi_ratio_data = 7.30`, the SUD rate given SMI over the SUD rate
given no SMI, computed from the repo's own NSDUH 2024 file in
`data/SMI_SUD_TARGET.md`.

## THE FINDING

    b_smi_multiple   r_smi    SUD|SMI   SUD|non-SMI   read at
        1.00         1.779     0.0900      0.0506     block 1
        0.50         2.384     0.1436      0.0602     block 6, BLOCK MOVE 1.4e-2
        0.20         3.259     0.1809      0.0555     block 1
        0.05         3.300     0.2093      0.0634     block 8, BLOCK MOVE 9.4e-3
        0.01         3.886     0.2229      0.0574     block 1

                                                      target 7.30

**`SUD | SMI` saturates.** Cutting the multiple twentyfold, from 0.20 to 0.01,
moves it from 0.1809 to 0.2229 -- twenty three per cent for a factor of twenty.
Reaching a ratio of 7.30 against a non-SMI rate of 0.057 needs `SUD | SMI` at
0.42, and the SMI rate is levelling off near 0.22. The multiple is bounded below
by 1e-6 in the update and the bound is not what stops it; the flow utility is.

**The mechanism is the onset margin, not the use margin.** `b` enters as
`(b+q)^phi_q`, so lowering it raises the marginal value of the first unit and
raises USE. Whether a user becomes DISORDERED is the onset hazard, and with
`iota_smi = 1` an SMI household faces the population's hazard. At a multiple of
0.20 the model already has `model_experimenters/model_total_drug_users` at
0.604: the extra use `b_smi` buys arrives mostly as experimentation, which the
ratio does not count.

## WHAT THIS MEANS FOR THE AUTHOR'S INSTRUCTION

The instruction of 22 September was to remove the higher SUD risk with SMI and
the lower recovery rate with SMI, and to pick `b` so that the model matches
7.30. **The first two removals make the third impossible.** `b_smi` alone tops
out at a ratio near 3.3 to 3.9 depending on how far the equilibrium has settled.

Three ways forward, and the choice is the author's:

1. **Put ONE of the two channels back and calibrate IT on 7.30**, keeping `b`
   common. `iota_smi` acts directly on the onset hazard, which is the margin
   that binds; `mu_m` acts on recovery, which is the other side of the same
   steady state. Either has the reach the multiple lacks.
2. **Move the target.** 3.3 is already above the 2.06 the two class benchmark
   produces with the SMI channels ON, so the endogenous income route delivers a
   real comorbidity gradient -- just not seven.
3. **Bring the non-SMI rate down to the data's.** These points are OFF the
   calibration: `lambda_d` runs 0.065 against its 0.043424 target because every
   other parameter is frozen while `b_smi` is cut. A recalibrated economy puts
   the non-SMI rate near 0.041 instead of 0.057, which alone lifts the ratio to
   about 5.4 at the same SMI ceiling. Closer, still short.

## HOW THE RATES WERE MEASURED

`code/smi_sud_xtab.py` decodes `calibration_distribution1.dat` into the four
masses `r_smi` is built from. The model prints only the ratio, so the 0.5 and
0.05 points had to BACK the two rates out of `lambda_d`, `p_m` and `r_smi`,
which is exact only if the cross-tab's population base coincides with
`model_fraction_addicted`'s -- they are accumulated in different subroutines and
that was never checked. The 0.20 and 0.01 rows above are READ, not derived.

The decode is controlled against the model's own print: at 0.20 the Fortran
printed `MOMENT r_smi` = 3.2588654628626594 and the decoder printed 3.2589; at
0.01, 3.8855666636818813 against 3.8856.

## READ A POINT AT ITS BLOCK COUNT

The ratio DRIFTS DOWN as the equilibrium settles -- the 0.5 point printed 2.657
at block 1 and 2.384 at block 6, ten per cent -- and the drift is entirely in
the DENOMINATOR: `SUD | non-SMI` rose eleven per cent over the 0.05 point's
eight blocks while `SUD | SMI` sat inside half a per cent. So the block 1 rows
above overstate their ratio and the comparison across points is only safe at a
comparable `BLOCK MOVE`. It does not touch the finding: the saturation is in
`SUD | SMI`, which is the column that does NOT drift.
