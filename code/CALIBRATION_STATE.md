# THE 20 SEPTEMBER T=30 IS VOID. THE FAIR-MARKET-RENT CAP WAS BROKEN

21 September. The archive disagrees with what this file said yesterday, and the
archive wins. Everything below the first two sections is what survives.

## WHAT WAS WRONG

The counterfactual's housing voucher is capped by a fair-market-rent standard.
The benchmark builds that standard from its own calibrated average rent times
its own calibrated average rental unit size. The counterfactual was rebuilding
it every period from `model_average_rent(t)*model_average_rental_unit_size(t)`
-- its OWN drifting product -- so the cap moved with the equilibrium it was
supposed to discipline, and in a transition it collapsed. Four defects, all
closed and each committed separately:

    a65b9dd4  median_income was never declared for the transition
    c463dd20  the eligibility cutoff's median income was computed off the
              wrong denominator
    cbc96395  the standard now reads the BENCHMARK's calibrated rent and
              calibrated unit size in every counterfactual
    f05451d5  the same two are pinned at the source, after the normalisation,
              so nothing downstream can re-derive a drifting one

The author's instruction was the whole of it: *"No, the formula has to be the
same as the benchmark... The rent is identical..."* and *"use the same model
average rental size as the benchmark. Pin it so the counterfactual uses the
same rule."*

## THE CONTROLLED PAIR, T=5, ONE SOURCE CHANGE

Same benchmark, same handover, same binary settings, controls stated before the
run:

                      pre-fix      post-fix
    vouchers t=1      0.63943      0.65572
    vouchers t=2      0.000000     0.66355
    lifetime t=1      790.873      792.194     (benchmark 791.39464)
    lifetime t=2         --        792.521
    CEV      t=1       -9.272%      +2.306%
    CEV      t=2          --        +3.273%    (long run +3.249%)
    budget residual     0.445       0.0327 / 0.0241 against a rule of 5e-2

    FMR standard, both periods: avg_rent 1.0000000
                                avg_unit_size 0.30208980094400001

At t=2 the pre-fix path paid NO vouchers at all. **Treatment First is welfare
improving at t=1 once the cap is fixed.** The -9.27 per cent that this file
reported yesterday, and that the grandfathering arm's entire rationale rested
on, was the collapsing cap and not the reform.

## WHAT THIS VOIDS

- The welfare column of the 20 September T=30 -- -9.272%, -11.46%, -12.15%,
  recovering to -2.223% at t=29 -- in full. There is no trough.
- The grandfathering brief. Its question has inverted from *how much of the t=1
  loss does it recover* to *how much of the t=1 gain does it forgo*, and the
  pre-fix evidence already had homelessness HIGHER under grandfathering
  (0.008747 against 0.007713 at t=1) because the exempt lose the deterrent.
  Its `CONTROL.md` acceptance numbers were measured on the broken cap and are
  stale.
- The quantity path -- h_1, b, lambda_d by period -- is not known to be wrong,
  but it is not verified either. At T=5 the quantities barely moved (h_1 +18.75%
  at t=1 post-fix against +19.4% pre-fix at T=30) while welfare inverted. Do not
  quote the 20 September quantity path as a result until the rerun lands.

## IN FLIGHT

**THE MODEL HAS CHANGED THREE TIMES SINCE THE 20 SEPTEMBER BENCHMARK.** The SMI
mortality double count is fixed; the model is one class with omega_c pinned at
zero; and SMI is exogenous, `iota_smi` and `mu_m` both at one. All of these are
DECLARED values in the Fortran, not vector entries, which is what makes a
resume come back as the same experiment.

**THE COMORBIDITY TARGET IS 7.30**, computed from the repo's own NSDUH file at
26+ on the same `svyrdudany` cut the level targets use, universe check passing
at 0.0890 and 0.0368. Full account and the whole verification trail in
`data/SMI_SUD_TARGET.md`. Data decomposes as entry 4.51 times persistence 1.62.

**WHERE THE RATIO HAS BEEN**, all measured, all on the benchmark switches:

    archive benchmark, two class                        0.596
    + mortality fix only, two class                     2.062
    + one class, iota_smi=1, mu_m=1, mid-calibration    1.656   loop 12 checkpoint
    same, the worker's block 1                          1.779
    TARGET                                              7.30

Removing `mu_m` cost most of the rise. The fix-only 2.062 was entry 1.39 times
persistence 1.47; with `mu_m` at one the persistence contribution goes and the
ratio falls back towards entry alone. That was stated before the choice was
made and is recorded here because it sets the size of the job: `b_smi_multiple`
now carries the whole distance from about 1.7 to 7.30, a factor of four and a
third, where with `mu_m` kept it would have been about three.

**THE CHANNEL IS BUILT AND LIVE.** `b_smi_multiple`, an SMI-specific multiple on
`addiction_scalar_1`, with its moment `MOMENT r_smi`, its gaps row, its bracket
and its persistence in `calibration_state.dat`. Three things about it that are
easy to get wrong and are written at the code rather than only here:

  - **THE BRACKET'S SIGN IS REVERSED.** b enters as (b+q)^phi_q so the marginal
    value of the first unit goes like 1/b: a LARGER multiple means LESS use and
    a LOWER ratio. Parameter and moment move in opposite directions and the
    update ADDS the gap. Same trap as `kappa_phi_d_level`.
  - **IT READS `smi_of(unemployment_index)` RATHER THAN TAKING AN ARGUMENT**, to
    avoid forty silent hand edits. The cost is that `b_shifter` is no longer a
    pure function of its arguments. The gate is DIRECTIONAL, not a no-op: move
    the parameter and check SUD|SMI moves hard while SUD|non-SMI barely does.
  - **IT PERSISTS AT THE TAIL OF `calibration_state.dat`, WITH ITS ADJUSTER.**
    Without that every resume reset it to 1.0; without the adjuster a resume
    came back HELD while still looking like it was running.

**THE SWEEP WAS RUN AND IT SETTLES THE QUESTION: `b_smi` CANNOT REACH 7.30.**
Five points, every one of them with the other forty seven adjusters frozen, so
each is the single-parameter test ENGINE.md's phase 3 rule 1 asks for:

    b_smi_multiple   r_smi   SUD|SMI   SUD|non-SMI   read at
        1.00         1.779    0.0900      0.0506     block 1
        0.50         2.384    0.1436      0.0602     block 6, BLOCK MOVE 1.4e-2
        0.20         3.259    0.1809      0.0555     block 1
        0.05         3.300    0.2093      0.0634     block 8, BLOCK MOVE 9.4e-3
        0.01         3.886    0.2229      0.0574     block 1
                              TARGET 7.30

`SUD|SMI` SATURATES. A twentyfold cut in the multiple, 0.20 to 0.01, buys
twenty three per cent on it. A ratio of 7.30 against a non-SMI rate of 0.057
needs `SUD|SMI` at 0.42 and the SMI rate is levelling off near 0.22. The 1e-6
floor in the update is not what stops it.

THE MARGIN IS THE REASON. `b` enters as `(b+q)^phi_q`, so cutting it raises the
marginal value of the first unit and raises USE. Whether a user becomes
DISORDERED is the onset hazard, and at `iota_smi = 1` an SMI household faces the
population's. At a multiple of 0.20 the model already has
`model_experimenters/model_total_drug_users` at 0.604: the extra use `b_smi`
buys arrives as experimentation, which the ratio does not count.

**SO THE INSTRUCTION OF 22 SEPTEMBER CANNOT BE CARRIED OUT AS STATED** --
remove the higher SUD risk with SMI, remove the lower recovery with SMI, and
pick `b` to match 7.30. The first two removals are what make the third
impossible. Three ways forward are written out in
`results/smi_comorbidity/B_SMI_SWEEP.md` and the choice is the author's; nothing
has been changed pending it.

**THE 0.20 AND 0.01 RATES ARE READ, NOT DERIVED.** `code/smi_sud_xtab.py`
decodes `calibration_distribution1.dat` into the four masses `r_smi` is built
from. The 0.5 and 0.05 rows had to be backed out of `lambda_d`, `p_m` and
`r_smi`, which is exact only if the cross-tab's population base coincides with
`model_fraction_addicted`'s -- accumulated in different subroutines and never
checked. The decode is controlled against the model's own print: 3.2589 against
3.2588654628626594 at 0.20, and 3.8856 against 3.8855666636818813 at 0.01.

**READ A POINT AT ITS BLOCK COUNT.** The ratio drifts DOWN as the equilibrium
settles -- 2.657 at block 1 against 2.384 at block 6 on the 0.5 point -- and the
drift is entirely in the DENOMINATOR: `SUD|non-SMI` rose eleven per cent over
the 0.05 point's eight blocks while `SUD|SMI` sat inside half a per cent. It
does not touch the finding, because the saturation is in the column that does
not drift.

**`b_smi_multiple` HAS A GAPS ROW NOW**, which it did not before: its distance
is RELATIVE so `pairs()` never discovered it, its adjuster is DECLARED zero and
turned on from the handover so the held test dropped it, and it prints on the
same line as its own distance so its value column was empty. All three are
closed in `code/paper/calibration_report.py`, each with a before-and-after
control on a frozen log and a joint log.

**THE CONTAINERS REBOOT, BUT NOT AT THE FIRING TIMES** -- that reading was
measured false and corrected at the top of ENGINE.md. This container booted at
01:28 and has carried two solves through several turn boundaries since. Nothing survives a kernel reboot, so every solve
runs in a worker session and this one coordinates only. See the entry at the top
of ENGINE.md.

## THE HORIZON IS NOT SETTLED. T=45 IS NOT ENOUGH, AND I SAID IT WAS.

This section said, at 08:11, that "everything is at or past its terminal value
by the early twenties", that T=45 had twenty periods to spare and that post-fix
even T=30 would have sufficed. **That was wrong.** The completed 43-period path
says so plainly:

                  t=44        terminal      gap    closing at    needs
    h_1         -0.39%        +1.31%       1.70    0.155/period   ~11 more
    b          -47.65%       -44.65%       3.00    0.095/period   ~32 more
    lambda_d   -51.23%       -45.20%       6.03    0.260/period   ~23 more

**None of the three has arrived at the last free period.** They CROSS their
terminal values in the early twenties, overshoot by several points, and then
crawl back. I read the crossing as the arrival. Crossing is the start of the
approach, not the end of it.

On those rates participation binds and wants about **T=76**; lambda_d wants ~67
and homelessness ~55.

**So `CALIBRATION_STATE.md`'s original instinct -- "the reported result should be
T=75" -- was right, and I overturned it on a misreading.** What was genuinely
wrong in the old section was the explanation of h_1's +63.9 per cent stall,
which WAS the fair-market-rent cap; the horizon conclusion was not.

The T=30 run was still correctly killed at 02:44 on the author's instruction
(*"i suggest to just go to T=45"*): T=30 is further from enough, not closer.

Caveat: loop 0 of an unconverged run, so the rates may shift as the price path
settles. The overshoot-and-slow-return shape should be robust, since it is
cohort turnover rather than prices.

**The horizon is an open scope question for the author.** T=76 is about 8 hours
a loop against 4.7, so roughly 40 hours for five loops against 24. Whether it is
worth it depends on whether the paper reports a converged lambda_d or a welfare
path over the first few decades; the second is unaffected by a tail still
settling.

## WHAT THE AUTHOR ESTABLISHED ABOUT THE MODEL, 21 September

**The transition solves for TWO objects, not five.** *"rent and housing price
and lump sum transfer are not equilibrium objects, they are constant"*, and
*"i can only think of 2: pi_v and p_v"*. `peg_prices_in_counterfactual=1` pins
the house price and rent and ZEROES their distances, so two of the four stopping
rules never bind; lump_sum_transfer is never assigned inside the loop. I had
claimed three of four rules belonged to them. See
`results/transition_t30_nogf/TWO_OBJECTS_NOT_FIVE.md`.

**And homelessness is not one either.** *"once pi_v and p_v converge,
homelessness is what it is and is applied to the welfare"*. The code already
does this: h_1 is written every loop as a reference and never read back.

## WHAT SURVIVES FROM THE 20 SEPTEMBER RUN

**The secant seed.** `distance_drug_market` at t=1 came in at 0.031346 against a
test of 0.21730, and the mean across 29 periods was 0.01351 -- fifteen times
better than the ramp's 0.2027 and the supply curve's 0.4878. The cap stopped
binding, so no fourth reseed was needed. This is a property of the seeding, not
of the voucher, and the fix does not touch it.

**The control on the drug price, which is a result in itself.** h_1 at t=1 was
0.0077265 at p=0.777 and 0.0077137 at p=0.927: a 0.17 per cent move in
homelessness across a 19 per cent move in the price. Homelessness at
implementation is conditionality revoking housing from people still using, and
the price is not a competing explanation. Participation is the opposite --
b went 0.092053 to 0.059749 over the same price move, a 35 per cent fall for a
19 per cent rise, an implied demand elasticity near -1.8 against the -2.3 slope
measured on the supply side. **This model's drug market clears through
participation, not through homelessness.**

**The horizon problem.** At t=29 the price was already the boundary condition,
0.83349, and yet h_1 sat at +63.9 per cent on the benchmark where the terminal
steady state is +1.3. Whether that survives the fix is exactly what the rerun
answers; if it does, the reported result needs a longer horizon and that is a
scope decision for the author.

## CLOSED SINCE THIS FILE LAST SAID OTHERWISE

- **The windowing was compared bit for bit**: 6.075e-05 relative against a rule
  of 1e-4. Windowing the policies to one slot is a no-op on the path.
- **pi_v's update is no longer a fixed damped step.** It carries per-period
  secant state, falls back to a damped 0.05 of the residual, abandons the
  secant when the gap grows, holds a four-step trust region, and applies the
  existing quarter-of-pi_v clip last.
- **The transition's stopping rules were loosened by the author's instruction**
  (*"the convergence rule can be less tight than the long run"*): a factor of
  two on all four, applied only when `solve_transition_dynamics` is on.
- **Paths save and restore**, in Fortran and in `code/save_transition_paths.py`,
  and both refuse a path carrying NaN or a pi_v on a bound.
- **The benchmark `.dat` set is shared**, 90 files, 2.06 GB compressed to 124 MB
  in `code/seeds/benchmark_dat/`, retiring the four-and-a-half-hour cold start.

## THE RUNNING T=30 CARRIES A PRE-FIX TERMINAL CONDITION. QUANTIFIED, NOT FATAL

Found 21 September 02:05, by reading the file the run actually loads. The
transition does not solve its terminal steady state -- it reads `counter_TF`,
and the set in `trans_bench_to_tf/` is dated 19 September 19:21, before any of
the five voucher fixes:

    counter_TF.txt  probability_of_voucher          0.0763466554594919
                    govt_spending_on_housing_vouchers_2  0.68483690499099070

The post-fix arm 3 re-solve gives 0.0768762 and 0.67956504, so the terminal
pi_v this run is anchored to is **0.69 per cent low** and the terminal voucher
spending 0.77 per cent high.

**Why the run continues anyway.** The same controlled re-solve moves the
terminal quantities the backward pass actually needs by almost nothing: b
+0.031 per cent, h_1 +0.153, lambda_d -0.190, and **lifetime welfare by 0.001
per cent** -- four orders of magnitude inside anything that could change a t=1
CEV. A 0.69 per cent error in one instrument's terminal level sits far inside
the transition's own stopping rules and inside the noise of a first,
unconverged loop, and re-solving arm 3 here first would cost hours before the
diagnostic the author asked for could even start.

**What it does mean.** The pi_v panel's last periods inherit a slightly low
anchor, so read the END of that panel as approximate.

**The anchor is now fixed for the NEXT run, 02:11.** A sibling committed
`seeds/PARAM_HANDOVER_trans_postfix.txt` and made `stage_transition.sh` default
to it: `probability_of_voucher_benchmark_used` 0.076876159888350143 against the
old 0.076347, and `drug_price_start` 0.83283631757376753 against 0.83349. Those
two scalars ARE the terminal pin, so a run staged from here carries the
corrected one without needing the `counter_TF` `.dat` set rebuilt.

**The running job was NOT restarted for it, and that is a decision, not an
oversight.** It is thirty minutes into a three-hour loop; the change is 0.69 per
cent on one instrument and 0.079 per cent on the price; and nothing the author
asked this loop to show -- whether homelessness rises, whether use falls,
whether the CEV is positive, whether the path flattens by t=30 -- turns on
either. Paying thirty minutes to move a tail anchor by two thirds of a per cent
in a loop that will not have converged anyway is churn. The next T=30 stages
from the post-fix handover.

## STILL OPEN

- Nothing has converged. No number in the "in flight" section is a result yet.
- pi_v's budget update switches on at loop 1 and has still never run to
  convergence on a path.
- Whether the t=1 gain is the right SIZE. A recipient's voucher is about 67 per
  cent of their income and recipients are 6.3 per cent of the population, so
  abolishing the programme outright is worth roughly 3 per cent of population
  average consumption -- that is the bound the t=1 number has to sit inside.
- The grandfathered arm's voucher code has not been run since any of the five
  fixes.
- `penalty_child_homeless` is 0, so the "children on the street" channel
  transmits no inherited penalty at all. Whether that is intended is the
  author's call and it is not a bug to fix unasked.
- The child's inherited penalty must key on the period the parent DIES in.
  Read, not verified.
- Arms 1 and 2 were run under the loose stopping rules and not re-checked.
