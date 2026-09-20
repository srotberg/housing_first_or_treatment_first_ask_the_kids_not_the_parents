# The third seed: the two-point secant, and the test the second one FAILED

## The second seed was wrong, and wrong in the direction I did not predict

I seeded the price path at the supply curve read off run A's allocation and
predicted `distance_drug_market` at t=1 would collapse from 0.21730 toward
zero. It went to 0.48885 and the gap CHANGED SIGN.

    run A (ramp)      t=1   p_faced 0.98929   p_implied 0.77695   gap -0.21233
    run B (reseed)    t=1   p_faced 0.77695   p_implied 1.26580   gap +0.48885

## Why: I asserted a contraction from a number that was not a price experiment

I read the near-flatness of the implied price ACROSS PERIODS within run A as
a price response and called it measured. It is not. Different periods are
different distributions; nothing about it is a price experiment. The real
slope, from two prices in the SAME period, is d(implied)/dp = -2.25 at t=1,
falling to -7.8 by t=28. The map is EXPANSIVE everywhere, so an undamped
fixed-point step was the worst available move. My estimate was -0.19.

## What run B bought: a genuine secant in all 29 periods

Two real (price, implied) pairs per period now pin the root, and **every one
of the 29 roots falls strictly inside its own bracket -- none was clamped**,
which is the check that the two points really do straddle the crossing.

    t=1  0.92739     t=10 0.90769     t=20 0.87289     t=28 0.83402
                                                       t=29 0.83349 (pinned)

The path OVERSHOOTS and decays to the terminal. It does not undershoot and
recover, which is what I told the author, and the original ramp was closer
to the truth than my reseed: 0.98929 is 7.0 per cent above p*(1) and on the
correct side, while 0.77695 is 16.0 per cent below it and on the wrong side.

## The test for THIS seed

`distance_drug_market` at t=1 must fall well below 0.21730, the best of the
two runs so far. The seed is a linear-secant root and the true curve is not
linear, so it will not be zero; **anything at or above 0.21730 means the
secant is not locating the crossing and the next step is bisection on the
bracket [0.77695, 0.98929], which cannot fail but costs a loop per halving.**

## MUST NOT MOVE

- `price_of_addictive_good_path(29)` stays 0.83349, the boundary condition.
- `pi_v` stays 0.076347 in every period of loop 0; its update is gated
  behind loop_count>0.
- h_1 at t=1 was 0.0077265 under run B's cheap price and +19.2 per cent on
  the mass measure under run A's dear one -- the same number either way.
  **Homelessness is not price-driven here**, so a third price should leave
  it near 0.0077 again. If it moves materially, something other than the
  price changed and the run is not comparable.
