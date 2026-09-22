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

**THE 22 SEPTEMBER MORTALITY DIAGNOSTIC IS VOID. It solved Treatment First.**
Seeded from the TRANSITION's handover, which sets
`voucher_conditional_on_clean=1`; that switch is set by the handover alone and
nothing resets it per phase. Every model number it produced is withdrawn --
the ratios 1.928 through 2.244, the aggregate drug-use fall, and the inference
that adopting the fix forces a drug-block recalibration. Full account in
`results/smi_comorbidity/MORTALITY_FIX_RUN.md`. The author caught it from the
arithmetic: a patch that lowers death risk for SMI households with a SUD, and
touches nothing else, cannot cut aggregate drug use by a third in a population
95 per cent of which it cannot reach.

**A HANDOVER IS NOT A CALIBRATION.** `PARAM_HANDOVER*` files carry policy
switches as well as parameters. Print the switch lines before using one. The
benchmark vector is `seeds/PARAM_HANDOVER_bm_n90repro.txt`, which agrees with
the transition's on every calibrated parameter and differs only on the seven
switches; the Fortran settles the ambiguous one: *"a zero here is written out as
TF, a one is written as HF. Default 1 is the benchmark."*

**THE MODEL HAS CHANGED.** The SMI mortality double count is now fixed in
`code/housing_first_or_treatment_first_SR_v1.f90` (1f8e7110), on the author's
instruction to refit. What survives from the diagnostic is only the survival
table itself, which is read at build time and no switch can touch:

    clean housed, age 40         0.98719030618667603  both, to the last digit
    SMI homeless w/ SUD, age 40  0.79504489593274741 -> 0.88727469276301107
    cells clipped to zero           2 of 472  ->  0 of 472

This invalidates the calibration, the benchmark, and every counterfactual and
transition in the archive, because survival feeds the value of life, saving and
labour supply.

**THE COMORBIDITY TARGET IS 7.30, COMPUTED 21:05.** From the repo's own
`data/raw/NSDUH_2024_public_use_file_tab_delimited.zip`, adults 26+, weighted,
SMI from `SMIPY`, drug involvement from `SVYRDUDANY` -- the variable both model
targets are built from. The universe check passes exactly, 0.0890 and 0.0368.
Full account in `data/SMI_SUD_TARGET.md`.

                                      SMI    non-SMI   ratio
    use  (any DUD incl. mild)       0.34126   0.07570   4.51
    SUD  (moderate or severe)       0.20426   0.02797   7.30
    SUD among USERS                 0.59854   0.36940   1.62

The "about 2" carried through this session was wrong by a factor of 3.6: it came
from secondary summaries on a broad, alcohol-inclusive definition at 18+.

**RUNNING: the fix-only test, NOT a calibration.** The author: *"Before you do
any refit I want to see if it is even needed."* `code/bench_fixonly/`, pid
32050, launched 20:44:16, warm started from the archive benchmark and running
`seeds/PARAM_HANDOVER_bm_n90repro.txt` with the benchmark switches VERIFIED IN
ITS OWN LOG. No parameter moves.

                    ref      blk 1     blk 2     target
    aggregate SUD  0.03361   0.04359   0.05110   0.04342
    ratio          0.596     2.162     2.043     7.30
    BLOCK MOVE       --      1.0000    0.2048    1e-4

**THE FIX IS WORTH KEEPING AND IS NOT ENOUGH.** It corrects an arithmetic error
at no parameter cost and takes the comorbidity from the wrong sign to about a
quarter of the way. It also OVERSHOOTS the level: lambda_d is now 18 per cent
above target and still climbing, so a refit is needed for the level. "lambda_d
lands on its target" was reported at block 1 and is withdrawn -- the path
crossed the target, it did not settle on it.

**THE REMAINING GAP IS AT ENTRY, AND THE INSTRUMENT IS `b`.** The ratios
multiply exactly:

                      entry  x  persistence  =  SUD ratio
        data           4.51        1.62           7.30
        model, fixed   0.78        2.78           2.16

The model has SMI households STARTING to use less than everyone else when the
data says they start 4.5 times more, and compensates with too much stickiness.
`addiction_scalar_1` is bracketed on participation, which is exactly the missing
margin, so an SMI-specific `b` answers to the use ratio 4.51. The recovery-side
routes in `results/smi_comorbidity/WHAT_TO_ADD.md` push on persistence, which is
already OVERDONE at 2.78 against 1.62 -- so does `mu_m=0.82`.

**THE FULL JOINT CALIBRATION IS PREPARED BUT NOT RUNNING.** Launched 20:38:48
and stopped at 20:43:28 because `run_one_point.sh` deletes the warm start by
design, so it was cold: 41 minutes to a first block that means nothing, against
~13 minutes a block warm. Its 88-argument vector is built and verified at
`/tmp/claude-0/refit_args.txt`, the switches checked.

**STOPPED: the T=45 no-grandfathering transition.** Killed 20:25 and its session
archived, because it is a transition of a model that no longer exists. Loop 1's
paths are committed as `seeds/*_t45_nogf_afterloop1.txt`, including the first
pi_v vector in the project that carries a shape. Loop 0 closed 21 September
07:58; loop 1 closed 22 September 16:45 with the budget at 0.0738 -> 0.046182 ->
0.032962 against a rule of 5e-2, so the budget cleared and the drug market did
not.

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
