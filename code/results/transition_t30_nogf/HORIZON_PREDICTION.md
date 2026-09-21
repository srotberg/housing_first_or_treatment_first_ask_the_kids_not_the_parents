# IS T=30 TOO SHORT? THE PREDICTION, WRITTEN BEFORE THE RUN'S FORWARD PASS LANDS

21 September 02:40. `hftf_t30b` is in its backward pass; no period of loop 0 has
printed yet. This is stated now so it cannot be fitted afterwards.

## THE CLAIM ON RECORD, AND WHY I NO LONGER BELIEVE IT

`CALIBRATION_STATE.md` said, on the 20 September run: *"T=30 IS TOO SHORT, AND
THE RIGHT RUN NOW SAYS SO... h_1 is 0.010585, +63.9 per cent on the benchmark
where the terminal steady state is +1.3 per cent."* That run was pre-fix. Its
loop-0 path:

    t=1    h_1 +19.4%   b -27.0%   lambda_d 0.033610
    t=4    h_1 +76.5%   b -27.0%   lambda_d 0.031300      <- the peak
    t=20   h_1 +63.3%   b -34.5%   lambda_d 0.023524
    t=29   h_1 +63.9%   b -41.9%   lambda_d 0.020800
    T      h_1  +1.3%   b -44.6%   lambda_d 0.018460      <- terminal steady state

**Read the three columns against the terminal, not against each other.** b ends
2.7 points from its terminal value and lambda_d 12.7 per cent from its, both
still moving in the right direction at a rate that would close them. h_1 ends
**sixty-two points** from its terminal value, having stopped falling around t=20
and ticked back UP at t=28 and t=29.

A path that is merely short is still visibly travelling at its last free period,
in every variable. This one has b and lambda_d nearly continuous with the
terminal and h_1 discontinuous by a factor of fifty. **That is not a horizon
signature. That is one variable being driven by something the terminal steady
state does not share** -- and h_1 is exactly the variable the fair-market-rent
cap controls, because a voucher is what keeps a household housed.

The cap collapsed ALONG the path and not in the steady state. That is the
whole shape: h_1 climbs while the cap falls, stalls high, and never rejoins a
terminal that was solved with an intact cap.

## THE PREDICTION

**If the bug caused it**, the post-fix T=30 shows h_1 at t=29 far below +63.9 per
cent and still visibly DECLINING into the terminal, with the peak lower than
+76.5 per cent and earlier than t=4.

**If the horizon really is too short**, h_1 still stalls somewhere near +60 per
cent with b and lambda_d close to terminal, and the answer is T=60 or more.

**What would falsify BOTH and mean something else is wrong**: h_1 rising
monotonically to t=29, or b and lambda_d moving further from terminal than they
did pre-fix.

## WHY IT MATTERS BEYOND THE HORIZON

If the bug caused it, the reported horizon can stay at T=30 and every run gets
about three times cheaper than the T=75 the state file was heading toward. If
the horizon caused it, T=30 is a diagnostic only and the paper's transition
costs five hours a loop instead of 2.7.

---

# AND A SECOND PREDICTION, ON THE t=1 WELFARE GAIN, SAME RULE

Added 02:50, still before the forward pass. The author's hope is stated plainly:
*"ideally we find a welfare gain in t=1 and dont need a grandfathered
simulation"*. The gain already exists at T=5 -- **CEV +2.306 per cent at t=1** on
the corrected source. What follows is why I expect the T=30 number to be LOWER,
written now so it is not explained away later.

## WHY A LONGER HORIZON SHOULD SHRINK THE t=1 GAIN

The terminal steady state is the BEST state in the problem: +3.249 per cent,
h_1 back to +1.3, lambda_d at 0.018460. Every period of the transition is worse
than it -- homelessness elevated, the stock of disorder still turning over.

A cohort alive at t=1 lives about 61 periods. The horizon decides how many of
those it spends in the transition and how many in the terminal steady state:

    T=5    4 transition periods,  57 in the terminal steady state
    T=30  29 transition periods,  32 in the terminal steady state

**T=5 hands the t=1 cohort the good news twenty-five periods early.** It is not a
truncation that merely shortens the path; it replaces the bad middle with the
good end. So +2.306 per cent is an OPTIMISTIC reading of the t=1 gain, and the
honest expectation is that T=30 comes in below it.

## WHAT TO WATCH, AND WHAT WOULD BE BAD NEWS

**The sign, not the level.** If t=1 stays positive at T=30, the finding holds and
grandfathering has no loss left to recover. If it crosses zero, the T=5 result
was a horizon artefact and the whole question reopens.

**The falsifier for this prediction** is t=1 at T=30 coming in at or ABOVE
+2.306 per cent. That would mean the transition periods are not worse than the
terminal for the t=1 cohort, which would contradict the h_1 and lambda_d paths,
and I would want to know why before believing the welfare number.

## ON WHETHER THE GRANDFATHERED ARM IS STILL NEEDED

If t=1 is a gain, grandfathering has nothing to recover and the arm is not
needed to rescue the policy. It may still be worth ONE paragraph as a result
rather than an arm: the pre-fix T=5 test found homelessness HIGHER under
grandfathering (0.008747 against 0.007713 at t=1) because the exempt lose the
deterrent and b rose 21.7 per cent. "Exempting the caught generation makes
things worse" is a finding, not an absence of one. That is a scope call for the
author and no work is being done on it.

---

# VERDICT, 05:25. THE FIRST PREDICTION HELD. THE SECOND DID NOT.

Measured on `t45_nogf/t45_run.log`, loop 0, T=45, six periods -- the same window
the prediction named.

## PREDICTION ONE: h_1's STALL WAS THE BUG, NOT THE HORIZON. CONFIRMED.

               t=1    t=2    t=3    t=4    t=5    t=6
    pre-fix  +19.4  +65.6  +73.4  +76.5  +76.4  +76.0   peak t=4, then +63% forever
    post-fix +18.7  +18.9  +18.4  +17.6  +17.2  +16.7   peak t=2, monotone decline

The prediction asked for "a lower peak, earlier than t=4, still visibly
DECLINING". It got +18.9 at t=2 against +76.5 at t=4, and a monotone fall
after. The stated falsifier -- "h_1 still stalls somewhere near +60 per cent" --
is not close to happening.

**So `CALIBRATION_STATE.md`'s "T=30 IS TOO SHORT, AND THE RIGHT RUN NOW SAYS SO"
was the fair-market-rent cap collapsing along the path.** Every clause of that
section rested on h_1 sitting 62 points from its terminal at the last free
period. It sits 15 points from it at t=6 and is still moving.

## PREDICTION TWO: THE t=1 GAIN WOULD SHRINK AT A LONGER HORIZON. FALSIFIED.

    T=5  post-fix   CEV t=1  +2.306%
    T=45 post-fix   CEV t=1  +2.318%

The reasoning was that the terminal steady state is the best state in the
problem and a longer horizon gives the t=1 cohort less of it -- 57 of its 61
periods at T=5 against 32 at T=45. The stated falsifier was "t=1 at T=45 coming
in at or ABOVE +2.306 per cent". It came in above, by 0.012 points.

**Why the reasoning failed.** It treated the cohort's lifetime as a weighted
average over which steady state it sits in. It is not: discounting puts the
weight on the near periods, and those are nearly identical under both horizons.
A nine-fold change in horizon moved t=1 by twelve thousandths of a point, which
is the real finding and is stronger than the prediction would have been.

## AND THE HORIZON ARITHMETIC I GAVE THE AUTHOR WAS WRONG BY A FACTOR OF FOUR

At 05:02 I said lambda_d decays 1.70 per cent a period and reaches terminal
about t=36, making it the variable that sets the horizon. That rate was measured
on the PRE-FIX path. Post-fix it decays **4.13 per cent a period** and projects
to about **t=15**.

    measured t=1..6, post-fix        reaches terminal about
    lambda_d   -4.13%/period         t=15
    h_1        -0.47%/period         t=36

**Homelessness is the slow variable, not SUD** -- the reverse of what I told the
author an hour earlier, and for the same reason the horizon claim was wrong: the
bug slowed the thing I was measuring the rate on. Both still arrive inside 45.

Six periods is a direction, not a number, and decay rates slow near the target.
The path itself answers it by about t=20.
