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
magnitude more than the cohort path showed.

**For the full model.** There is no single "caught" generation there, there are
fifty four of them, one per age. Every household alive at the reform has a
history under the old rule, and the ones deepest into a disorder have the least
time left to recover from it. The transition must integrate over the whole age
distribution alive at the switch, not just follow newborns. Expect the cost to
be concentrated in middle age: old enough to have acquired the disorder, too
close to the end to benefit from the treatment the policy is buying.

## 2. Check whether the deterred margin is empty before believing a small cost

Under Treatment First at universal cover the stylized model has participation of
exactly zero at every income. Nobody uses, so nobody is revoked, so nobody is
made homeless, so no child inherits the homelessness penalty. The policy's cost
is the loss of an OPTION, not a realised penalty, which is why it looks small.

That is a real result but it is knife edge in a specific way: it holds at
universal cover and need not hold at lower generosity, where some households
still use and the revocation actually fires. **Before reporting that a
conditional policy is cheap, check whether anyone is actually subject to the
condition in equilibrium.** If the answer is nobody, say so, because the reader
will otherwise assume the number prices a revocation that never happens.

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
