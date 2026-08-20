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
| The child's inherited penalty keyed on the parent's PERIOD 1 only, so homelessness that conditionality itself causes could never reach a child | **No.** `expected_child_value(addiction_index, is_homeless_1)` enters the continuation at EVERY age, weighted by the chance the parent does not survive it, so the parent's state at whatever age it dies is what the child inherits. A revocation at 50 that puts the household on the street does reach a child born at 50. |
| Aggregating a decision threshold off the grid's geometry rather than off the true CDF | **Does not arise.** The quantitative model carries a distribution over grid points and evaluates the drug choice at each point, so there is no cell for a threshold to fall inside. |

Two differences between the models are DELIBERATE and are not bugs: the
quantitative model exempts a household in treatment from the condition, and it
enforces the condition imperfectly, with a detection rate and a false positive
rate. The stylized model has neither, and says so.

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
