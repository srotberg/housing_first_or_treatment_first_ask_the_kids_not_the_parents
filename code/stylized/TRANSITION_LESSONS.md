# What the stylized transition got wrong, and what the full model's must not

The stylized transition was written, reviewed and found to be materially
incomplete. The full model's transition has the same shape and will hit the same
traps, so they are written down here before it is coded.

## 1. A cohort path is not a transition

The first version plotted expected lifetime value for each newborn cohort after
the reform, and every cohort in it lived its whole life under one policy. That
made Treatment First look nearly free: the cohort born at the switch loses
0.08 percentage points, because it simply declines to use and keeps its voucher.

The households the reform actually falls on were **not in the figure at all**.
They are the ones already mid life when the rule changes: they chose whether to
use under the old rule, a disorder cannot be recovered from once the last period
is terminal, and conditionality now withdraws their voucher for a decision taken
before the rule existed. They lose **8.7 per cent of consumption**, and 0.64 per
cent of them are put on the street by the revocation itself. Two orders of
magnitude more than the cohort path showed. (Those two figures were computed
under the old period 2 rule and have not been restated; the point they make is
about the size of the gap, which the fix does not close.)

**For the full model.** There is no single "caught" generation there, there are
fifty four of them, one per age. Every household alive at the reform has a
history under the old rule, and the ones deepest into a disorder have the least
time left to recover from it. The transition must integrate over the whole age
distribution alive at the switch, not just follow newborns. Expect the cost to
be concentrated in middle age: old enough to have acquired the disorder, too
close to the end to benefit from the treatment the policy is buying.

## 2. Check whether the deterred margin is empty before believing a small cost

Under Treatment First at universal cover the stylized model USED TO HAVE
participation of exactly zero at every income. Nobody used, so nobody was
revoked, so nobody was made homeless, so no child inherited the homelessness
penalty. The policy's cost was the loss of an OPTION rather than a realised
penalty, which is why it looked small.

**That turned out to be a symptom of the revocation bug, not a property of the
model.** The period 2 condition was testing a history of use rather than the
current period, so any household that used in period 1 lost its period 2
voucher whatever happened to it, and the deterrent was strong enough to empty
the margin completely. With the condition testing the current period, as the
quantitative model's does, participation under Treatment First at universal
cover is small but positive and the revocation actually fires.

The lesson stands and is now better evidenced: **before reporting that a
conditional policy is cheap, check whether anyone is actually subject to the
condition in equilibrium.** An answer of exactly nobody is worth treating as a
bug report and not as a result until it has been chased down.

## 3. Watch which period an inherited penalty keys on

The child's penalty is tied to the parent's PERIOD 1 use and PERIOD 1
homelessness. For use that is defensible, since v is only chosen in period 1.
For homelessness it is not obviously right: homelessness happens in both
periods, and under this convention the homelessness that Treatment First CAUSES,
by revoking vouchers from households that already have a disorder, can never
reach a child. The mechanism is switched off by a timing assumption rather than
by economics.

**For the full model.** The same question, with more room to get it wrong: a
child born at parental age j inherits the parent's state at j, so the convention
has to say which ages count. A revocation at age 50 that makes a household
homeless should reach a child born at 50, and must not silently fail to.

## 4. Show the mechanism next to the welfare

One welfare panel invites the reading that nothing is happening. Homelessness
and disorder rates by cohort, on the same axis, show what the welfare number is
made of and make an empty deterred margin visible immediately.

## 5. Mechanical traps, all of which bit

- **Sign of a compensating variation.** `cev(par, dv)` where `dv` is the value
  the household loses is the compensation it needs; `cev(par, -dv)` is the
  negative of it and reads as a gain. The first version reported the caught
  generation GAINING 8 per cent.
- **Editing a function by slicing between two anchors** deleted `numbers()`
  entirely, because the slice ran from one function to the module's main block
  and swallowed everything between.
- **Tuple width.** Adding a field to what `period1` returns broke three unpack
  sites, one of which (`value1`) was only reached by the welfare routines and
  would have failed hours later.
- **Assets matter for the size of the answer.** The caught generation's loss is
  32.6 per cent computed at zero assets and 8.7 per cent integrating over the
  assets they actually saved. Never quote the zero asset figure.

---

## 6. THE FULL MODEL'S TRANSITION MUST BE REDONE TO MATCH THIS ONE

Standing instruction, not a suggestion. Everything above was found by writing
the stylized model's transition, getting it wrong, and being corrected. The
full model's transition has to end up aligned with the stylized one on every
point, and it is easier to build it that way than to retrofit it:

1. **Integrate over the whole age distribution alive at the reform**, not just
   newborn cohorts. In the stylized model this was the difference between a cost
   of 0.08 percentage points and one of 8.7 per cent of consumption. In the full
   model there is a caught generation at every age, and the worst hit will be in
   middle age: old enough to carry a disorder, too near the end to gain from the
   treatment the policy buys.
2. **Key the child's inherited penalty on the period the parent DIES in**, which
   is also the period conditionality acts in. This was got wrong twice, once in
   each direction, and both errors were invisible in the output.

   Keyed on the FIRST period alone, the homelessness conditionality causes by
   revoking vouchers never reaches a child at all: the voucher is withdrawn at
   the transition into period 2, so the mechanism is switched off by a timing
   assumption rather than by economics.

   Keyed on EITHER period, which was the overcorrection, a parent transmits a
   penalty it picked up under the OLD regime even when the new programme housed
   it for the whole of its final period. In the transition that produced
   nonsense: under universal Housing First, where nobody is unhoused, 0.73 per
   cent of the second cohort of newborns was still being born behind an unhoused
   parent, because their parents had been unhoused years earlier under the old
   rationed programme. The author caught this by asking the obvious question,
   which is that under universal Housing First the initial old must be housed.

   Period 2 is right on both counts, and equation (11) already said so: the
   penalty is keyed on a parent "unhoused when it died". With it, Housing First
   transmits nothing at the reform and the entire difference between the two
   policies is conditionality's own revocations, 0.33 per cent against 0.00.
3. **Report the mechanism beside the welfare.** Homelessness and disorder rates
   by cohort, on the same figure. One welfare panel invites the reading that
   nothing is happening.
4. **Check whether anyone is actually subject to the condition** before
   reporting that conditionality is cheap. In the stylized model nobody uses
   under Treatment First at universal cover, so nobody is ever revoked and the
   cost is the loss of an option rather than a realised penalty. Say so.
5. **Aggregate off the true distribution, not the grid's geometry.** Where a
   decision threshold falls inside a cell, the share of that cell inside the
   region is a CDF difference, and the threshold can lie BELOW the cell's node
   as well as above it. Missing the second case cost three and a half points of
   participation in one step here.
6. **A hump is not a bug.** Participation should rise then fall in generosity as
   moral hazard gives way to the value of life. Test for a single turning point,
   not for monotonicity; testing the wrong property sent me chasing real
   economics as if it were an artefact.


---

## 7. WHEN A BUG IS FOUND HERE, CHECK THE FULL MODEL FOR IT

Standing instruction. The stylized model is small enough that its mistakes are
found; the quantitative model is not. Every fix here gets carried across, or is
recorded as not applying, with the reason.

The audit as of the revocation fix:

| bug found in the stylized model | does the quantitative model have it? |
|---|---|
| Period 2 revoked the voucher on a HISTORY of use, when there is no period 2 drug choice and only the disorder can fail the condition | **No.** `calculate_housing_voucher` zeroes the voucher when the household is addicted NOW, or is choosing to use NOW (`future_addiction_index_1 >= 1`). Both are current-period tests; nothing there looks at a history. The stylized model was the one out of line, and the fix brought it into line. |
| The child's inherited penalty keyed on the parent's PERIOD 1 only, so homelessness that conditionality itself causes could never reach a child | **No.** `expected_child_value(addiction_index, is_homeless_1)` enters the continuation at EVERY age, weighted by the chance the parent does not survive it, so the parent's state at whatever age it dies is what the child inherits. A revocation at 50 that puts the household on the street does reach a child born at 50. **SUPERSEDED, 13 September.** The author's child-timing rule replaced "every age" with a gate: the child is in the home from 26 to 50, so the term carries the death probability up to 49, arrives with weight ONE at 50 because the child leaves for certain, and is zero after 50. The verdict above still holds for the period the child exists -- the parent's state at whatever age it dies inside that window is what the child inherits -- but the term no longer runs to age 85. |
| The income grid was placed by TRUNCATING log income and spacing nodes uniformly, and the truncation point rather than the model was what set how many households could not afford to rent. Replaced by nodes at the conditional mean of equal-mass intervals, packed toward the bottom at `GRID_KAPPA = 2`, 120 of them, because the drug, housing and homelessness margins all sit there. Sigma fell from 1.1854 to 0.9633 and the median moved from 0.518 of the mean to 0.636, against roughly 0.65 in the data | **YES, AND IT IS LIVE.** `employment_grid` is nine nodes spaced uniformly in logs over plus and minus three standard deviations of a permanent draw, which is the truncated uniform placement this row records fixing. At the calibrated `sd_permanent_productivity` of 0.97 neighbouring nodes differ by a factor of 2.07 in income, and the bottom of the distribution is three mass points: 0.43 per cent at 0.034 of mean income, 2.61 at 0.070, 9.99 at 0.145. The homelessness target is 0.399 per cent of households, which is SMALLER THAN THE BOTTOM NODE'S ENTIRE MASS, so the attainable rates near it are roughly zero, 0.43 and 3.04 per cent and the target falls between the first two. That is the step function the h_1 bracket has been failing to land inside: measured, 6.2e-06, 6.7e-05, 4.2e-04, 2.3e-03, 1.5e-02, 3.1e-02, 3.4e-02, with the last three the second node arriving. Not yet fixed, because the grid multiplies the state space and the stylized model's own note warns which way it can go: resolved finely, every household below the affordability floor is FORCED onto the street, and there the margin sits at the eleventh percentile rather than in the tail. The quantitative model has a consumption floor the stylized model tried and removed, so it may hold where the stylized model could not, but that is a measurement rather than a deduction. `productivity_below_which_to_reduce_ss` is an index into this grid and must move with it. |
| Aggregating a decision threshold off the grid's geometry rather than off the true CDF | **Does not arise.** The quantitative model carries a distribution over grid points and evaluates the drug choice at each point, so there is no cell for a threshold to fall inside. |

| Calibrating an ABSOLUTE unit size against an income grid whose truncation floor is built from that same size, ONCE, at import | **No.** The quantitative model's smallest rental is `smallest_rental_relative_to_lowest_income`, a RATIO to the lowest income on the grid rather than an absolute size, so the unit moves with the grid by construction and cannot outrun it. The stylized model's `h_sm` is an absolute number and `_grid` truncates below `TRUNC_FLOOR * pr * P().h_sm` from the CLASS value, so any trial above it prices the poorest households out of the only unit they could afford: they cannot rent at all, and homelessness ran 0.4 per cent at `h_sm = 0.10`, 3.0 at 0.15 and 20 at 0.39, none of it an answer about unit sizes. Fixed by capping the bracket at the floor. The ratio parameterisation is the better design and is worth copying if the stylized grid is ever rebuilt. |
| Collapsing the ACS three-way size split to two rentals by taking the SMALL BIN rather than the small and medium bins together | **Does not arise.** The quantitative model has three housed sizes and targets `housing_size_dist_data` bin for bin, so there is no collapse to get wrong. The stylized model has two, so its `h_2` is everything below the standard family unit, 37.3 per cent, and not the studio-and-one-bedroom bin's 13.2. Aimed at 13.2 the bracket could not converge at all: the share is INCREASING in `h_sm` across the admissible range and bottoms out near 24 per cent, so the target sat below anything the model can produce and the bisection ran to its lower bound. A target outside the attainable range looks exactly like a broken adjuster, which is how it presented. |
| `threshold()` wrote the boundary cells PER CROSSING, which is correct only while no cell is the boundary of two of them. The use region is not always an interval: at some parameter values it is the top block PLUS one isolated cell in the middle of the income distribution, where a household sits on a housing rung boundary and using tips which rung it takes. That cell has a crossing on each side, both wrote it, and the second write won, so its share was one of the two halves rather than their overlap and never shrank to zero as the region closed. The whole cell then left at once, a 1.25 point step in participation as a function of `b`, and it is what put two points of the channel scan out of reach: the 8.90 per cent target sat strictly inside the jump | **Does not arise, for the reason already recorded two rows above.** The quantitative model carries a distribution over grid points and picks the drug quantity by comparing values AT each point, so there is no threshold, no boundary cell and nothing to split. The class is worth stating anyway because it is not really about cells: it is about code that assumes a choice set is an INTERVAL when the model does not guarantee one. The Fortran's exposure to that assumption is `frac_mov_optimal_1`, the asset lottery, which splits between two adjacent nodes; it is a lottery over a CHOSEN point rather than a partition of a region, so a disconnected region cannot arise there either. Checked and clear. |

Two differences between the models are DELIBERATE and are not bugs: the
quantitative model exempts a household in treatment from the condition, and it
enforces the condition imperfectly, with a detection rate and a false positive
rate. The stylized model has neither, and says so.

The rule runs the other way too, and the calibration of the quantitative model
turned up eight bugs that had to be checked back against the stylized model:

| bug found in the quantitative model | does the stylized model have it? |
|---|---|
| The disorder rate by productivity, which delta_d is calibrated on, was the mass with the disorder AND EMPLOYED over the mass with the disorder, so it was an employment rate that read about 0.87 wherever anyone stood and zero elsewhere | **Does not arise.** The stylized model has no productivity grid to condition a disorder rate on; the child's outcome is `terminal_homeless_prob` evaluated at the child's own income, which is a rate over the whole population at that income by construction. |
| The newborn productivity draw ignored the parent, so `newborn_employment_probability` and therefore delta_d reached the parent's continuation value and the cross section not at all | **No.** `children.py` draws the child's income from the penalised distribution and solves the child's problem at that income, so the penalty is in the child's outcome and not only in the parent's valuation of it. This is the one place the stylized model was right and the quantitative model was not. |
| Newborns were seeded without the age-one SMI prevalence, so mental illness was built up by onset from age two alone and came out three times too small | **Does not apply.** The stylized model has no mental illness state. |
| The drug first order condition scaled both marginal utilities by `(1-sigma)*utility_1`, but `calculate_flow_utility` appends `aleph` and `bar_tau^u` before returning, so the scale was `X^(1-sigma) - aleph` and came out NEGATIVE. The condition was then negative at every point of its bracket, the bisection never saw a sign change, and every household the risk term applied to abstained completely | **No, and it is immune twice over.** Flow utility is logarithmic, so there is no `(1-sigma)` factor anywhere for `aleph` to contaminate: `par.aleph` is a pure additive constant in `_branch` and `solve_period2` and never multiplies a derivative. And the drug quantity is chosen by `np.argmax` over the value on `vg`, which compares LEVELS of the objective rather than solving a marginal condition, so a mis-scaled derivative has nothing to act on. |
| A moment was attributed to a parameter that no longer carried it, and a second parameter chased a share the first was thought to own. `rho_d` had the employed share of the homeless in Tables 5 and 6 and in the prose, but `include_rho_d = 0`: the penalty is off, and the price of the cheapest dwelling `h_2` is what the code brackets on that moment. The ladder's curvature then ran on the SMALLEST size share, which is not `h_2`'s moment either, so no parameter owned the middle rung by name | **No, but only because it has fewer moving parts.** The stylized model has two rentals and targets one share, `hsmall`, so there is no third rung and no second instrument to double book. There is no employment state to generate an employed share of the homeless. The class of bug is live in it, though, and its own instance was `theta`: Table 2 listed it as internally calibrated while the calibration held it fixed, which is the same failure of the table to say what the code does. The check that closes it in both models is the same one: read the Set column against the code, parameter by parameter, and make each row name the moment the code actually brackets on. |
| A restart file carried no record of the shape of what it held. `read_calibration_distribution` loaded `calibration_distribution{1,2}.dat` on nothing but their existence, and the files are a bare list of numbers. A build at a different asset grid read them anyway: cut from 40 positive points to 25, the array goes from 101 to 86 and the read SUCCEEDS, having taken the first 86/101 of each slice of another distribution. The log reported `sum= 45.718` where the file was written at 51.362. The 25 point build then took 2445 distribution sweeps against 340 and reported average net wealth 10.7 per cent low, and both numbers were read as evidence about the grid | **Does not arise, and the reason is a design difference worth keeping.** Everything the stylized model persists is keyed by NAME: `calibrated.json` is seven named parameters, and `numbers_prev.json`, `params_prev.json` and `tables_prev.json` are name to value maps for the red marking. A name keyed file cannot be silently misread into a different layout -- a missing key raises and an extra key is ignored -- so the failure mode needs a positional file to exist at all, and the stylized model has none. The class is still worth naming, because it is not really about arrays: a cached artefact that does not record the configuration it was produced under will be reused under another one. The stylized model's own exposure of that shape is `calibrated.json` being loaded by a build whose income grid has changed, where the keys still match and the values are no longer the calibration. Nothing in it says which grid it was calibrated at. |
| The aggregation normalised the drug-spending histogram through `index_drug_1`, a local integer that is assigned only inside the branch a household with positive drug spending enters. A draw that leaves no drug spending anywhere in the distribution never enters that branch, so the normalisation indexed a 100001-element array with an uninitialised integer and wrote outside it. The crash carries no message of its own, it sits ahead of every moment print, and a loop that hit it therefore scored nothing, which is why four consecutive loops produced no gap table | **No, and the reason is a habit worth keeping.** Every conditional statistic in `aggregates` divides by `max(denominator, 1e-12)`: `prog` and `r_use` by `part`, `homeless` by `mass`, `sud_of_homeless` by `hl`, `dshare` by `uinc`, `housing_share` by `hinc`. An empty subpopulation is a defined number in all of them rather than an exception. The deeper protection is that the stylized model normalises whole arrays and never carries an index out of the accumulating loop into the normalising statement, so it has no variable whose value depends on the loop having entered a branch. Fixed in the Fortran by normalising the whole array, which is what the bin counts needed in any case, and only when there is a mass to divide by. |
| The parameter handover was read at the foot of `read_calibration_state`, BELOW two early returns. `calibration_state.dat` is not in the repository, so a container that had never run the model returned before `PARAM_HANDOVER.txt` was opened, solved at the values in the Fortran declarations, and printed a complete moments block saying nothing about the vector it had discarded. It bites only the FIRST run in such a container, because that run's own loop then writes the state file, which is why it hid: a worker measuring six points lost its first and honoured the other five, and it cost one archived point in 423. What made it expensive was not the bug but the diagnosis: three re-runs agreeing to four decimals were read as evidence the whole archive was invalid, when all three were first runs in one container and the agreement was the bug's signature | **No, and the design is why.** The stylized model takes its parameters as function ARGUMENTS -- `calibrate(seed, ...)`, `with_(P(), **kw)` -- so there is no side channel through which a caller's vector can be dropped. `calibrated.json` is a seed and not a specification: its absence means a cold start from the class defaults, which is a slower calibration rather than a different experiment, and `calibrate.py` says so where it loads it. The class generalises past handover files, though, and this is the form to carry: **a parameter that arrives by a channel the run can skip must leave a receipt, and the caller must refuse the measurement when the receipt is missing.** The Fortran echoes one `HANDOVER` line per parameter it applies, which was already the receipt; nothing was reading it. `run_one_point.sh` now counts them and fails the point unless every parameter it handed was echoed. |
| An aggregation array was declared from 0 while the state dimension it sums over starts at `lowest_housing_grid_point=-1`, homelessness. The filling loop correctly ran over the dimension's own bounds, so `dist_housing_1(-1)` read-modify-wrote the 8 bytes below the array on every 100th distribution sweep of every run, and the homeless column of the DIST_MOM diagnostic never received its mass. Found by `-fcheck=bounds` the first time the diagnostic fired; invisible before because the victim of the write is whatever the compiler placed there | **The class is LIVE in principle and MORE dangerous here, and was checked.** numpy does not fault a negative index: `arr[-1]` silently wraps to the LAST element, so the same off-by-one would add homeless mass to the top housing bin and no tool would ever object. Checked: the stylized model's states are dict keys and 0-based tuple positions (`(par.na, 2)` arrays indexed by explicit 0/1), with no state code that can go negative, so no instance exists today. The rule to carry: any accumulator indexed by a STATE CODE must be declared over the code's own range, and in Python a state code that can be negative must never index an array directly. |
| **The child's inherited penalty was written out in ONE of the six housing branches.** `weight_on_child*expected_child_value(...)` sat in `renter_to_renter_problem` alone; `renter_to_owner_problem`, `owner_owner_stay_problem`, `owner_owner_move_problem` and `owner_renter_problem` did not carry it at all. `expected_child_value` is zero for a clean housed parent and negative otherwise, so a parent with the disorder paid the child's penalty when it rented and did not pay it when it owned, bought or moved between houses. The rent-versus-own margin was tilted towards owning by the whole size of the externality, for exactly the households the paper is about, and `omega_c`'s own moment was measured on an economy in which five of six branches ignored `omega_c` | **No, and the reason is worth keeping rather than a lucky escape.** The stylized model's penalty is `par.beta * par.omega * _chdmg_at(par, y) * _pid(par, vg)`: it depends on income and on the drug quantity and NOT on which dwelling the household takes. `_branch` maximises over the housing options internally and `pen` is subtracted from the result, which is exact precisely because the penalty is flat across the options -- a constant cannot move an argmax. The quantitative model's `expected_child_value(e, d, h)` carries the housing status as its third index, because there the street is a state the child can inherit, so the term MUST sit inside the housing comparison and not after it. **The rule to carry: a term may be hoisted out of a maximisation only while it is constant across what is being maximised over, and adding an argument to such a term silently invalidates every hoist of it.** The homelessness index was added to `expected_child_value` at some point after the term was written, and that is what turned a correct hoist into a wrong one. Fixed by routing all six branches through `child_continuation_value`. |

The drug first order condition row is the sharpest methodological difference
between the two models found so far, and it is worth stating as a rule. **The stylized model picks the
drug quantity by searching the objective; the quantitative model picks it by
solving a first order condition.** Only the second can be silently inverted,
because only the second depends on the derivative being assembled correctly. The
Fortran's own comment argued the bisection was safe because "the objective rises
then falls across it" -- which is true of the CORRECT condition, and the scale
error broke that premise without breaking anything the compiler or the solver
could see. The bisection ran to convergence every time and returned a corner.

The practical form of the rule: where the quantitative model replaces a search
with a first order condition for speed, the two must be checked against each
other at least once at a real state, because a sign error in the condition
produces a converged answer rather than a failure.

The second row is worth stating as a general point rather than an entry: a
penalty that enters only the parent's continuation value and not the child's
realised state will still let its own moment converge, because the moment is
computed off the penalty's own array. Nothing fails; the mechanism is simply
absent from the model. Both models now put the penalty in the child.

The warm start row generalises, and this is the form to carry: **a persisted
artefact that does not record the configuration it was produced under will be
reused under another one, and whether that is loud or silent is an accident of
which direction the configuration moved.** Growing the array hit end of file and
killed the run, which is the good case. Shrinking it succeeded and produced a
distribution missing an eighth of its mass, which then propagated into a
comparison between two builds and was read as a fact about asset grids. The
guard is cheap in both models: stamp what the artefact was made from, and refuse
it when the stamp does not match or is absent.

### Carried forward: newborn_parent_share needs a time index before the transition runs

Not a bug in the steady state and a bug in the transition, recorded here rather
than found later, which is the whole point of this file.

The newborn productivity draw is now a mixture of
`newborn_employment_probability` over the parents being replaced, and those
weights live in `newborn_parent_share`, accumulated by the statistics sweep as
the mass dying in each disorder and housing cell. The array has no time
dimension. In the stationary solve that is correct and cheap, because there is
one period and one distribution. In a transition it is wrong in the way that is
hardest to see: period t's newborns would be drawn against whichever period's
statistics ran last, so the composition of the parents would lag or lead the
distribution it is supposed to describe, and it would do so silently, since
every number involved stays a well formed probability.

The fix is a time index, `newborn_parent_share(transition_length,0:1,1:2)`,
written by the sweep at the period it just measured and read by the distribution
iteration at the period it is building. It has to go in BEFORE the transition is
turned on, not after: the symptom is a composition that is slightly off in a
model where the composition is the mechanism, and nothing about it looks wrong
on inspection.

This matters more here than it would in most models. Under `fixed_productivity`
the newborn draw is the household's productivity for life, so the parent
composition at the reform date is what the whole cohort carries through the
transition, and getting it from the wrong period misdates the reform's effect on
the generation the paper is about.

## 8. The transition horizon is not the display horizon

A transition must be COMPUTED over a horizon long enough that convergence is a
finding, and DISPLAYED over one short enough to read. These are different
numbers and conflating them turns an assumption into a result.

The failure is quiet. A settling test measures each cohort against the last one
computed, so a path still drifting at the end of a short run reports the end and
reads as converged. The stylized model ran five cohorts and asserted it had
settled in two or three; five could never have shown otherwise.

**The stylized model** now runs `GENERATIONS_LONG = 20` and draws
`max(GENERATIONS_SHOW, settle + 2)`, so a path that turns out to be slow extends
the figure rather than being clipped into looking fast. It also exports
`tr_horizon`, what was computed, and `tr_drift`, the gap between the last two
cohorts, so the claim can be checked rather than trusted.

**The quantitative model needs far more: fifty to a hundred periods.** It is a
sequence of general equilibrium prices rather than a Markov chain on four
penalty types; nothing is redrawn every generation, the capital stock and the
distribution both carry state, and the speed of convergence is not known in
advance. Run it long, verify the tail is flat, then truncate for display only
after seeing that it is. Never pick the horizon first.

## 9. The generation the reform catches parents the SECOND new cohort

The child's penalty keys on the parent's WHOLE life. That was fixed once, for
the rest points, and it survived in one more place: the first steps off them.

`path()` gave every cohort after the reform the mixture the previous cohort
produced under the NEW policy, so the initial old
never parented anybody. Its extra homelessness, which under Treatment First is
caused by the revocations themselves, was computed for the welfare marker and
then dropped on the floor. The two policies were identical on inheritance
forever, by construction rather than as a finding.

THE TIMING IS THE WHOLE CONTENT, and it is easy to get one generation wrong in
either direction:

- **The initial newborns inherit nothing from the reform, and should not.** Its income draw
  was settled by a parent who completed BOTH periods before the condition
  existed. The two policies hand cohort 1 the same mixture, and its welfare gap
  is the private loss alone.
- **The second cohort is the first that inherits the reform.** Its parent is the caught
  generation: young under the old rule, old when the reform landed, stripped of
  the voucher under Treatment First for a disorder acquired before the condition
  existed.
- **From the third cohort the parents are the second cohort of old, who lived
  their whole lives under the new rule,** and the
  chain is stationary in the policy.

Wired up this way the stylized model puts 0.983 per cent of cohort 2 behind an
unhoused parent under Treatment First against 0.732 under Housing First, the
welfare gap widens from 0.074 to 0.110 points, and the ranking flips at cohort 3.

**The tests that the bridge is in the right place, both of which must pass.**
Cohort 1's inherited mixture must be IDENTICAL under the two policies; if it is
not, the bridge is a generation too early. Cohort 2's must DIFFER, and differ
only in the housing margin, since the initial old's disorder was settled
before the reform; if it does not, the bridge is missing.

**For the quantitative model:** the first periods of the transition are parented
by households whose lives straddle the reform. Build that bridge explicitly and
decide which cohort it lands on before writing any of it down.

## 10. The stylized model's early losses are a THEOREM, the full model's are not

In the stylized model the sign of each group's welfare change at the reform is
settled before any number is computed, and only the magnitude is open:

- **initial newborns** — weakly worse off. An option is removed and nothing is
  given back. This is the dominance argument of Section 3.6.1 on one cohort.
- **second cohort of newborns** — strictly worse off. Their parents, the initial
  old, were more likely to be unhoused, so they inherit worse draws.
- **initial old** — strictly worse off. The voucher is revoked for some of them
  and nothing is added for anybody.

So a stylized transition MUST open with welfare losses. That is a property of
the environment, not a result about housing policy, and neither the paper nor
the code should present it as one.

**The quantitative model is not bound this way, and its transition must not be
built as though it were.** Two channels absent from the stylized model push the
other way:

1. **The government budget clears in EVERY period of the transition**, not just
   at the endpoints. Treatment First covers fewer tenants, spends less, and so
   taxes less from the period the reform lands. The early cohorts pay those
   lower taxes over their whole lives. A transition that balances the budget
   only in the long run, or that holds taxes fixed on the path, throws this away
   and will reproduce the stylized model's losses as an artefact.
2. **Altruism is calibrated rather than zero.** A parent partly internalises the
   gain its own abstinence hands its child, so the private loss is strictly
   smaller than the same calculation gives here.

Either can outweigh the option loss and the inherited penalty. If the
quantitative transition comes out with the stylized model's sign pattern,
CHECK THE TAX PATH FIRST: the most likely explanation is that the budget was not
being cleared period by period.

## 11. Audit of the late stylized bugs against the Fortran

Section 7 says a bug found in the stylized model is checked against the
quantitative model before it is closed, and the answer written down whether it
carried across or not. Three bugs were found after that table was last filled.
All three were checked; **none of them is present in the Fortran.** A fourth
was found on 12 September and **it DID carry across**, which makes it the first
row of this table to come back positive. The table is the reason it was looked
for at all. A fifth, the corner branch, carries only as a CLASS -- the
mechanism cannot exist in the Fortran -- and its Fortran instance had already
been found by another route.

| stylized bug | Fortran counterpart | verdict |
|---|---|---|
| Boundary cell split against the wrong cell's edges | `compute_asset_lottery` | **Clear.** Two point lottery whose weight sets the lottery's MEAN to the parabola vertex. Refuses rather than extrapolating at either end of the range, on a non concave fit, and when the vertex leaves the bracket. Documented as effectively inert: 12 of 177,120 calls fire. |
| Interpolating a step function at a shifted income | `create_newborn_employment_probability` | **Clear, and built the right way round.** It shifts the productivity DISTRIBUTION across nodes and then evaluates policies at real grid points, rather than evaluating a policy at a shifted income. The split preserves the mean of log productivity; mass below the bottom node piles onto it, which is conservative. |
| A CDF and a set of grid masses measured on different bases | `rent_to_income_cdf` | **Clear.** The histogram is cumulated and then divided by `total_renters_to_consider`, which is accumulated in the same loop off the same mass. Same measure both sides. |
| Child's penalty keyed on the wrong period | `newborn_employment_probability(:, is_addicted_1, is_homeless_2)` | **Clear, and it was the STYLIZED model that had to move.** `is_homeless_2` is the housing status the household chose for the period in which it may die, so the penalty conditions on the parent's state at death, which is what equation (11) says. The stylized model keyed on period 1, then on either period, and was corrected to death timing to match this. |
| **The child gap was measured between two solves that are not comparable.** In the stylized model the baseline and the `omega_c = 0` counterfactual settled on DIFFERENT BRANCHES -- drug share 0.1028 against 0.2177, participation 0.0956 against 0.2390 -- and the ratio of the two reported a gap of 1.4984 against a target of 0.1834. It was measuring which branch each solve landed on, not what the parent internalises | `weight_on_child` update, and the counterfactual that feeds it | **PRESENT, and by a shorter route: the counterfactual need not have settled at all.** The counterfactual re-solves the distribution from the baseline's under `max_distribution_sweeps = 200`, and the code ALREADY computed whether it left on that cap, printed it beside the moment, and said in its own comment that such a solve "has moved part of the way to the counterfactual and the gap it reports is a partial adjustment rather than the moment". It was then never tested: `loop_count_dist` appeared in that one write statement and nowhere else in the update, so a capped counterfactual stepped `weight_on_child` exactly as if it were converged, by an amount depending on the sweep cap. The only conditions on the counterfactual were `drug_users_without_child > 0` and a baseline floor at a tenth of target participation. **This also closes the one unexplained observation in the block.** Its comment records that at loop 3 of a cold run, removing the penalty CUT use by 75 per cent where the mechanism says it must RAISE it, considers the capped-distribution explanation, and rejects it by exhibiting a DIFFERENT loop that converged in 61 sweeps with the right sign -- which shows the block CAN work, not that loop 3 was converged. The flag from loop 3 would have settled it and was never read. Fixed by carrying the flag in `omega_counterfactual_capped`, gating the update on it, and routing a capped loop into the existing HELD branch, which leaves `distance_weight_on_child` at one so the bracket stays live rather than retiring on a loop whose moment could not be measured. The diagnostic copy of the same counterfactual printed its `MOMENT omega` line with NO convergence information at all, so a moment read out of a diagnostic run could not be judged either; it now prints sweeps, reached and capped like the calibration path. **The comparability half is NOT fixed and is deliberately left open:** a window on the counterfactual-to-baseline ratio would catch the stylized failure, which was a factor of 2.5 on participation, but this block has a RECORDED legitimate reading of +0.93, a factor of 1.93, so any window tight enough to be useful sits close enough to a real measurement to risk rejecting it. That is a threshold to MEASURE rather than to pick. The ratio is now printed beside the gap so it can be. |
| **The "corner branch": users piling onto the smallest positive point of the drug grid.** Every run of the stylized model alternates between an interior equilibrium at a drug share near 0.21 and a "corner" where the share collapses. The corner has NO economic content: sweeping the grid's smallest positive point over three orders of magnitude gives `dshare / v_lo = 1.000` at every one of them, so in the corner every user sits exactly on the floor and the reported drug share is a property of the grid. Raising the floor makes participation collapse -- 0.0763, 0.0732, 0.0214, 0.0072 as the floor goes 1e-5 to 3e-2 -- which is what choosing a dominated infinitesimal looks like, since the onset hazard is FLAT and a household buying 1.8e-6 of income pays the entire addiction risk for a vanishing amount of drug | the drug choice in `owner_renter_problem`, via the drug first order condition | **The MECHANISM does not carry: the quantitative model has no grid over drug quantity.** The split is solved from a MARGINAL CONDITION -- the marginal utility of the drug against `drug_risk_value`, `EV(a',clean) - EV(a',disorder)` at the node -- so there is no discrete ladder of quantities, no smallest positive rung, and nothing for households to pile onto. The stylized model's corner needs `argmax` over a grid to exist at all. **The CLASS carries, and the Fortran's instance of it was already found and fixed.** A choice pinned at the edge of its feasible set by arithmetic rather than by economics is exactly what the drug first order condition did: `calculate_flow_utility` appends `aleph` before returning, so scaling by `(1-sigma)` gave `S/X - aleph` against a true scale of `S/X`, the two agree in sign only while `S/X` exceeds `aleph`, and above that crossover the condition was negative at every point of the bracket -- the bisection never saw a sign change and walked the consumption share to one, driving richer households to complete abstention. Same shape, different route: the stylized model reaches the edge through a grid, the Fortran reached it through a bracket with no interior root. Both are the arithmetic manufacturing a gradient rather than the model deriving one. **Evidence level: the Fortran side is read off the code's own documentation of the choice and the fixed defect, not off a re-derivation of the bisection.** |
| **A downstream module solved its own parameter vector, loaded from disk at import, and every number it produced was at THAT vector rather than the caller's.** `children.py` line 315 opens `calibrated.json` and builds `_BASE` at module level; `transition.py` imports `children.py`, so the whole cohort chain inherits it. The file is dated 27 August and is a DIFFERENT MODEL: it carries `lam = 106.8`, the addiction-susceptibility parameter from before the hazard was flattened -- which `children.py`'s own docstring records as a rejected channel -- with `aleph` at 2.86 against the current 10.62, and no `pi_base`, `omega`, `kap`, `u0` or `u1` at all, because it predates the flat onset hazard, the child in the flow utility and the mortality channel. It is also gitignored, so what it contains is not in the repository. The same module hardcodes `DEL_D = 0.24` and `DEL_H = 0.31` and `transition.py` imports those instead of reading `par.delta_d`, so the transition's penalty mixture does not move when the calibration moves the penalty: measured, the cohort CEV read 1.773 per cent at `delta_d` of 0.24, 0.40, 0.57 AND 0.75 while the child SUD odds ratio moved 1.36 to 2.47. A transition table was reported to the author and had to be withdrawn | `run_one_point.sh`'s parameter table, `PARAM_HANDOVER`, and the HANDOVER receipt | **PRESENT IN CLASS, AND THE FORTRAN ALREADY BUILT THE DEFENCES THIS MODEL LACKS -- the one row in this table where the quantitative model is ahead.** It treats "which vector is this actually running" as a first-class hazard and guards it three ways. `run_one_point.sh` carries a defaults table that MUST be added in the same commit as the Fortran's `PARAM_HANDOVER` case, with the comments recording what happened when they drifted: an overnight run "solved twenty-one vertices in twenty-one seconds and promoted through all three stages without measuring anything", because every vector setting the new name was rejected at the argument loop. There is a RECEIPT -- the Fortran echoes one `HANDOVER` line per parameter it applies and the script fails the point unless every parameter handed over is echoed back -- and there is the standing rule that a structural parameter set in the SOURCE is worthless if the vector also names it, which cost a two-and-a-half-hour run that silently relaunched a different model. The stylized model has none of these: nothing states which vector produced a number, nothing refuses a stale one, and a module can substitute its own parameters for the caller's in silence. **The lesson travels the other way for once** -- normally the stylized model finds the bug and the quantitative model inherits the search; here the quantitative model learned it expensively first and the stylized model never did. Not yet fixed: routing `DEL_D`/`DEL_H` to `par` and removing the import-time solve changes `children.py`, `transition.py` and everything importing them, so it is the author's call. |
| the child's inherited penalty ran to a 90 per cent cut of productivity | quantitative only | The full model transmits the penalty as a multiplier on the child's permanent productivity, so a 0.9 penalty puts every child of a parent with the disorder in the bottom nodes of the grid: it manufactures very low productivity households who work and cannot afford the cheapest room, and it drives its own moment backwards, since the bottom of the grid has essentially no drug use. The stylized model transmits the penalty as a UTILITY cost, `omega * chdmg`, not as a productivity shift, so it has no counterpart to cap and the error cannot arise there. Capped at 0.4 in the Fortran, with a clamp on the state file so a banked 0.9 cannot survive a loop. |

### Two configuration findings, which are not bugs

**The transition is switched off.** `solve_transition_dynamics` is written
`is_counterfactual*0+(1-is_counterfactual)*0`, which is identically zero however
`is_counterfactual` is set, so `transition_length` collapses to 1. The machinery
is all present and has never run in this configuration.

When it is switched on, two things the stylized model had to learn are already
right here: the horizon is 75 periods, and the government budget distance is
computed in EVERY period of the path with the maximum driving the convergence
loop, not merely at the endpoints. `adjust_taxes` is 1 and
`clear_only_vouchers_govt_budget` is 0, so the whole budget clears rather than
the voucher line alone. Lesson 10's diagnostic is therefore already satisfied.

**`calibrate_only_rental_management_costs` is dead.** It is declared and written
to the output file but never read anywhere, so it restricts nothing. It reads
like a switch that would confine the calibration to one parameter, and it does
not.

## The quantitative model's transition is thirty periods

The author's decision of 24 August. The Fortran currently declares

    transition_length = (1-solve_transition_dynamics)*1 + solve_transition_dynamics*75

so the constant says seventy five and the plan says thirty. Change it when the
transition is actually turned on, not before: it sizes several allocatable
arrays and there is no reason to carry the cost while the calibration is still
moving.

WHAT IT WILL COST, so nobody is surprised. A steady state solves in nine to
eighteen minutes on four cores, and that is already a fixed point over the age
loop. A transition adds a second fixed point, over the whole PATH of prices, so
the cost is the period count times one age pass times the number of path
iterations. On the measured numbers that is eight to fifteen hours on four cores
for thirty periods, and the width comes from the path iterations rather than the
periods.

AND IT DOES NOT PARALLELISE THE WAY THE CALIBRATION DOES. A transition is one
sequential fixed point in time, so a fleet of containers cannot be thrown at it;
only the OpenMP loop over ages helps, which is about three and a half times.
Thirty points every twenty five minutes is a calibration number and does not
carry over.

Before committing an overnight run, set transition_length to three or five and
time one solve. The passes are near linear in the period count, so it
extrapolates, and it costs half an hour on a spare container.

## 12. p_v MUST CLEAR ALONG THE PATH, AND IT CANNOT UNTIL IT IS TIME-INDEXED

The author asked on 8 September for the drug market to be cleared in the
counterfactuals "and also the transition when we run it". The long-run
counterfactual was done that day: `clear_drug_market` is called inside
`long_run_counter_factual`'s loop and `distance_drug_market` is in its
convergence test. **The transition was NOT, and it is not a one-line
addition.**

`price_of_addictive_good` is declared a SCALAR (line ~2951). Every other
market in the transition carries a time index -- `rent(time_period,:)`,
`housing_price(time_period)`, `lump_sum_transfer(time_period)`,
`net_govt_revenues(time_period)` -- and the drug price does not. So a
transition path cannot hold a different p_v in period 3 from period 30, and a
per-period call to `clear_drug_market(time_index)` inside
`transition_simulation`'s loop would simply leave the LAST period's price
standing for every period, which is worse than not clearing at all: the log
would report `largest_distance_drug_market` converged while every period but
one faced a price that does not clear its own quantity.

What building it actually requires, in order:

1. Dimension the price like every other transition price:
   `real(8), dimension(1-solve_transition_dynamics:transition_length) :: price_of_addictive_good`,
   initialised across the range from the benchmark's normalisation.
2. Index all ~100 read sites. Most are in household loops where
   `time_period` is already in scope. The ones that are NOT are the trap:
   `calculate_utility` takes the price through a local
   `price_of_addictive_good_to_use` (~22391) and has no time argument, and
   the elasticity test at 7424--7517 saves and restores the scalar. Both need
   the period passed in rather than reaching for a global.
3. Check the OpenMP clauses. `price_of_addictive_good` appears in the private
   and shared lists of the parallel regions; an array is shared, and a copy
   of a scalar that used to be private is not the same thing.
4. Only then add `largest_distance_drug_market` to `transition_simulation`'s
   do-while, on the pattern of `largest_distance_govt_budget`: zero it before
   the per-period sweep, call `clear_drug_market(time_index)` inside it, and
   keep the maximum.

The supply shifter itself needs no change. It is the BENCHMARK's, read once
from `drug_supply_shifterbaseline_benchmark.dat` and held fixed, which is
already what makes the price rather than the quantity the endogenous object.

The lesson this belongs to is section 7's: a market that is present in the
model but has no caller is invisible in the output. `clear_drug_market`'s
`is_counterfactual` branch existed, was correct, and had NO CALLER for as
long as it had existed, and no log line said so, because
`distance_drug_market` sits at its declared zero and zero is what a cleared
market also reports.
