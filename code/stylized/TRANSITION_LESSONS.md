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
2. **Key the child's inherited penalty on the parent's WHOLE life**, not on one
   period. Keyed on the first period alone, the homelessness that conditionality
   causes by revoking vouchers never reaches a child, and the mechanism is
   switched off by a timing assumption rather than by economics. This was
   corrected in the stylized model, and it doubled the share of children born to
   an ever unhoused parent, from 0.49 to 1.13 per cent.
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
