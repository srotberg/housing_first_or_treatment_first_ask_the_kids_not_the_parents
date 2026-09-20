# THE SECANT SEED WORKED. FIRST TRANSITION LOOP NEAR AN EQUILIBRIUM

20 September. T=30, third seed, one complete loop. The test set before the run
was that `distance_drug_market` at t=1 fall well below 0.21730. It came in at
**0.031346**, and across all 29 periods:

    mean distance_drug_market    ramp 0.2027   supply curve 0.4878   SECANT 0.01351

**Fifteen times better than the ramp**, with seven of 29 periods already inside
the 5e-3 rule (0.00029 at t=20, 0.00107 at t=23, 0.00258 at t=16).

## NO FOURTH RESEED. THE CAP IS NO LONGER BINDING

Three points in period 1 put the root at 0.9183 (bracketing pair) and 0.9167
(two nearest) against a seed of 0.92739 -- about 1.2 per cent, which is three
loops at the half-a-per-cent cap rather than forty. The reseeding was only ever
justified by the cap being the binding constraint. It is not any more, so the
run walks in on its own machinery.

## THE MECHANISM, WHICH IS NOW READABLE PERIOD BY PERIOD

                  benchmark      t=1           t=29          TF steady state
    h_1            0.006458   0.007714 +19.4%  0.010585 +63.9%  0.006542 +1.3%
    b              0.081740   0.059749 -26.9%  0.047540 -41.8%  0.045287 -44.6%
    lambda_d       0.033625   0.033610  flat   0.020800         0.018460
    lifetime       791.3946   787.9067         790.6010         792.5130
    CEV                  --    -9.272%          -2.223%           +3.249%

**Participation falls at once; disorder does not.** b drops 26.9 per cent in
the FIRST period and grinds to -41.8 per cent by t=29. lambda_d is completely
unmoved at t=1 -- 0.033610 against the benchmark's 0.033625 -- and only decays
later. That is the right shape: a household can stop USING the day the policy
starts, but the stock of people WITH disorder turns over only as the cohort
does. The author's reading of 19 September, that drug use would stop
immediately for many, is confirmed; what is slow is recovery from disorder.

**The welfare trough is at t=3 and shallow**: -9.27%, -11.46%, -12.15%, then
monotone recovery to -2.22% at t=29. A dip and a slow climb, not exponential
decay -- again the author's reading rather than mine.

**Homelessness rises and stays up.** +19.4 per cent at t=1, peaking at +76.5
per cent, still +63.9 per cent at t=29 against +1.3 per cent in the long run.
That is where the welfare loss is.

## THE CONTROL HELD, AND IT IS A RESULT IN ITSELF

h_1 at t=1 was 0.0077265 at p=0.777 and 0.0077137 at p=0.927: **a 0.17 per cent
move in homelessness across a 19 per cent move in the drug price.** Homelessness
at implementation is the conditionality revoking housing from people still
using, and the price is not a competing explanation.

Participation is the opposite -- violently price-sensitive. b was 0.092053 at
p=0.777 and 0.059749 at p=0.927, a 35 per cent fall for a 19 per cent price
rise, an implied demand elasticity near -1.8 consistent with the -2.3 slope
measured on the supply side. **This model's drug market clears through
participation, not through homelessness.**

## T=30 IS TOO SHORT, AND THE RIGHT RUN NOW SAYS SO

At t=29 the price IS the boundary condition, 0.83349, so the seed can no longer
be blamed. And yet h_1 is 0.010585, **+63.9 per cent on the benchmark where the
terminal steady state is +1.3 per cent**, and lambda_d is 0.0208 against
0.0185. The terminal condition is being imposed on a period nowhere near the
terminal steady state.

The reported result should be T=75, which fits memory at about 10.5 GB of 15
since the windowing. That is a scope decision and it is the author's. The T=30
run continues meanwhile: it is close on the drug market and will show how pi_v
behaves as the fiscal instrument, which no transition has yet exercised.

## STILL OPEN

- Nothing has converged. No number here is a result.
- pi_v's budget update switches on at loop 1 and has never run on a path.
- The windowing has not been compared bit-for-bit against an unwindowed run.
- The child's inherited penalty must key on the period the parent DIES in.
  Read, not verified.
- Arms 1 and 2 were run under the loose stopping rules and not re-checked.

