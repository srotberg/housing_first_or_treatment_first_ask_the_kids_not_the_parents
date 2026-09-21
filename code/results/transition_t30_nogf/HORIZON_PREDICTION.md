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
