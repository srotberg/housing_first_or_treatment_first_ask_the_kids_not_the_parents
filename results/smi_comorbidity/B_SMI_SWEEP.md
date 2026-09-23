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

---

# CORRECTION, 02:00: "CANNOT REACH 7.30" IS TOO STRONG. THE MARGIN IS NOT SPENT

The heading above was written on the RATIO alone, and the ratio is confounded by
its denominator. The author pushed back twice -- *"are you saying we cant get
r_smi higher? maybe you need to do 0.001?"* and *"or 0.00001?"* -- and the
decomposition they prompted says they are right.

## THE DRUG STATE SPLIT, READ OFF THE DISTRIBUTIONS

                        multiple 0.20            multiple 0.01
                     non-SMI      SMI         non-SMI      SMI
    clean             0.9070    0.7724         0.8757    0.7208
    experimenter      0.0375    0.0467         0.0605    0.0527
    SUD               0.0555    0.1809         0.0638    0.2264
    any use           0.0930    0.2276         0.1243    0.2792

**SEVENTY TWO PER CENT OF SMI HOUSEHOLDS ARE STILL COMPLETELY CLEAN.** There is
no exhausted margin and no ceiling of the kind claimed above.

## WHAT THE TARGET ACTUALLY REQUIRES

Among SMI households that use anything, 81 per cent carry a SUD
(0.2264/0.2792). If `b_smi` pulled every SMI household into use, `SUD | SMI`
would approach 0.81 and the ratio 12.6. A ratio of 7.30 needs `SUD | SMI` at
0.419, which is the SMI USING share at 0.52 against 0.28 now. Inside the
channel's reach.

The 0.81 is an upper estimate rather than a measurement: it is the steady state
among today's users, and households pulled in later are less disadvantaged and
may recover faster.

## WHY IT MOVES SLOWLY WITHOUT CAPPING

`lambda_addiction` is ZERO, so

    addiction_onset_hazard = min(base + (1-exp(-lambda*q)), 1) = base = 0.0336

for ANY positive quantity, and exactly zero at q = 0. Quantity does not enter
the onset at all. So `b_smi` cannot work through how much a household uses --
only through WHETHER it uses -- and it moves that solely through the utility of
ABSTAINING: a clean household's index goes as `b^phi_q`, so `u = -1/X` goes as
`-b^-0.27` and each decade of `b_smi` multiplies the cost of staying clean by
10^0.27 = 1.86. That grows without bound. It is slow, not blocked.

Measured, the SMI using share rose 0.052 over the 1.3 decades from 0.20 to
0.01, about 0.04 a decade. Straight-lining, the 0.24 still wanted is six more
decades, near a multiple of 1e-8. The push is CONVEX in 1/b, so expect it
sooner than the straight line -- and that is an extrapolation, which is why
0.001 and 1e-5 are being measured rather than argued.

**THE FLOOR IS 1e-6.** The state read clamps the multiple to [1e-6, 10], so the
ladder runs 1e-3, 1e-4, 1e-5, 1e-6 and no lower without a source change.

## THE INTERNAL CHECK ON THE DECODE

The 18 unemployment states decode as `drug = (i-1)/6` and
`smi = mod((i-1)/3, 2)`. With onset flat at 0.0336, the steady state SUD share
among users is `onset/(onset+exit)`, and the measured 0.2264/0.2792 = 0.811
implies an exit hazard of 0.0079 -- consistent across both points and with the
`r_smi` the Fortran itself prints. The split is not an artefact of the decode.


---

# SETTLED, 02:16: THE RATIO ASYMPTOTES AT ABOUT 4.01. THE CORRECTION ABOVE WAS
# RIGHT ABOUT THE CLEAN SHARE AND WRONG ABOUT WHAT IT IMPLIED

The author asked for 0.001 and then 1e-5. Both were run cold and frozen, read at
block 1, everything else identical:

    b_smi_multiple      r_smi     SMI clean   SMI SUD   SMI any use
        0.20           3.2589      0.7724     0.1809      0.2276
        0.01           3.5506      0.7208     0.2264      0.2792
        0.001          4.0057      0.7245     0.2276      0.2755
        1e-5           4.0094      0.7244     0.2278      0.2756
                       TARGET 7.30

**A HUNDREDFOLD CUT FROM 0.001 TO 1e-5 CHANGES EVERY CELL BY LESS THAN 0.0003.**
That pair is the clean comparison -- same configuration, both cold, both block 1
-- and it is flat. The ratio asymptotes near 4.01 and `b_smi` cannot deliver
7.30. The heading of the section above stands; the correction under it was right
that 72 per cent of SMI households are still clean, and wrong to read an open
margin off it.

The floor in the update is 1e-6, one decade below the last point, and two
decades bought 0.0037 on the ratio, so the floor is not what binds either.

## AND A PUZZLE THAT IS WORTH ONE CHEAP TEST BEFORE THIS IS QUOTED

At `b_smi_multiple = 1e-5` the SMI shifter is 4.9e-8. Flow utility is
Cobb-Douglas in `(b+v)`, so an abstaining household's index carries a factor
`b^phi_q`, and at `phi_q = 0.165` that factor is 0.062 against 0.47 for a
household spending five per cent of consumption on the drug. With `u = -1/X` the
abstainer should be many times worse off, and essentially every SMI household
should use SOMETHING. Seventy two per cent abstain, and the share does not move
across two decades of `b`.

So one of these is true and the sweep does not distinguish them:

  - the drug STATE is a slow Markov chain rather than a period choice, and the
    clean stock empties only through a transition whose hazard `b` does not
    touch -- `lambda_addiction` is zero, so onset is a flat 0.0336 for any
    positive quantity;
  - or the abstaining branch of the value function does not see the SMI `b`.

The second was checked as far as the source allows and looks sound:
`b_shifter` ignores its arguments and reads `smi_of(unemployment_index)`, the
abstain branches at 28524, 28534, 28549 and 28557 call it like every other
branch, and `unemployment_index` is safe under OpenMP -- the loop over it at
25265 is SERIAL and the `!$omp parallel do` inside runs over the financial
index with `unemployment_index` correctly in the `shared` clause, so every
thread in a region sees the same household state. There is no race.

That leaves the first, which would mean `b` moves who WANTS to use while the
stock of users is governed by hazards `b` does not enter. It is consistent with
everything measured and it has not been demonstrated.
