# THE SECOND SEED FAILED ITS OWN TEST, AND THE THIRD IS A REAL SECANT

20 September, later. The supply-curve reseed was launched with a stated test:
`distance_drug_market` at t=1 must fall from 0.21730 toward zero. **It rose to
0.48885 and the gap changed sign.** The seed was worse than the ramp it
replaced.

    run A (ramp)    t=1   p_faced 0.98929   p_implied 0.77695   gap -0.21233
    run B (reseed)  t=1   p_faced 0.77695   p_implied 1.26580   gap +0.48885

## THE ERROR, WHICH IS THE ONE THE STANDING RULE NAMES

I claimed the fixed-point map was a contraction and called that measured. It
was not measured. I compared implied prices ACROSS PERIODS inside a single
loop -- different distributions, different economies -- and read the near
flatness as a price response. **It is not a price experiment at all.**

From two prices in the SAME period the slope is d(implied)/dp = -2.25 at t=1,
steepening to -7.8 by t=28. The map is EXPANSIVE in every period, so the
undamped step I took was the worst move available. My estimate had been -0.19,
off by more than a factor of ten, and it implied a drug demand elasticity near
-0.2 where the truth is nearer -2.8.

**PREFER A MEASURED BRACKET TO AN ELASTICITY** is in the standing rules. I
wrote the rule into the commit message of the change that broke it.

## WHAT RUN B BOUGHT, WHICH IS NOT NOTHING

Two genuine (price, implied) pairs in all 29 periods, hence a real secant.
**Every one of the 29 roots lies strictly inside its own bracket -- none
clamped** -- which is the check that the two prices really straddle the
crossing rather than sitting on one side of it.

    t=1  0.92739    t=10 0.90769    t=20 0.87289    t=28 0.83402
                                                    t=29 0.83349 (pinned)

## THE SHAPE IS AN OVERSHOOT, NOT AN UNDERSHOOT

The price starts near 0.927 and decays to the terminal 0.83349. It does not
dip below and climb back. The earlier note in this file said the opposite and
was written from run A alone, where the implied price sat below the terminal
for a reason that is NOT the equilibrium price being low: quantity was low
because the price faced was high.

The ramp was closer to the truth than the reseed that replaced it. 0.98929 is
7.0 per cent above p*(1) and on the correct side; 0.77695 is 16.0 per cent
below and on the wrong side. The ramp was converging, slowly and from the
right direction, and the "about forty loops" arithmetic that justified
replacing it assumed a target of 0.78 that does not exist.

## WHAT IS NOW KNOWN ABOUT THE ECONOMICS

The mechanism print earns its place immediately. At t=1, under run B's cheap
price:

    h_1 = 0.0077265   (+19.6% on the benchmark)
    b   = 0.0920529   (+12.6% on the benchmark)
    lambda_d = 0.0336098  (flat)

Two results follow, and they matter for the paper.

**Homelessness at implementation is not price-driven.** t=1 homelessness is
+19.6 per cent at p=0.777 and +19.2 per cent at p=0.989 -- the same number
across a twenty-one per cent price swing. It is the conditionality revoking
housing from people who are still using. The author's hypothesis of 19
September stands, and the drug price is not a competing explanation.

**A cheap drug raises participation sharply at implementation.** b is 12.6 per
cent ABOVE the benchmark at p=0.777, against 44.6 per cent below it in the
terminal steady state. That is why the implied price shot to 1.266, and why
lifetime welfare was WORSE under the cheap seed (786.281, CEV -13.19%) than
under the dear one (788.151, CEV -8.66%).

## THE TEST FOR THE THIRD SEED, SET BEFORE IT RUNS

`distance_drug_market` at t=1 must fall well below 0.21730, the better of the
two runs so far. The root is a LINEAR secant on a curve that is not linear, so
it will not be zero. **At or above 0.21730 the secant is not locating the
crossing, and the next move is bisection on [0.77695, 0.98929], which cannot
fail but costs a loop per halving.**

## STILL OPEN

- No loop has converged. Nothing here is a result.
- T=30 still looks short: t=29 homelessness was 60 per cent above benchmark
  where the terminal steady state is 1.3 per cent above it.
- The windowing has not been compared bit-for-bit against an unwindowed run.
- The child's inherited penalty must key on the period the parent DIES in.
  Read, not verified.
- Arms 1 and 2 were run under the loose stopping rules and not re-checked.

