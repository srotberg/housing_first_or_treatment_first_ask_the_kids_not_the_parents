# ARM 3 DOES NOT CONVERGE AT drug_market_adjuster = 0.2. IT CYCLES.

19 September. Measured, not inferred, after two runs of the same arm with the
same parameters and the same seed both reported `CONVERGED: YES` on all three
live rules and disagreed by 4 per cent on every moment and by a factor of two
on the CEV.

## THE CYCLE

Six loops at `drug_market_adjuster=0.2`, `frozen_stop_tolerance=1e-6`, seeded
at the 8-loop run's stopping point. Loop 1 is the cold-value-function block and
is not part of the cycle.

    loop   CF distance      b              price       pi_v
      1    1.628 (cold)     0.046416       0.834351    0.069870
      2    1.0966e-03       0.047512       0.838523    0.070668
      3    6.3885e-04       0.046908       0.840248    0.073103
      4    1.0985e-03       0.045810       0.839166    0.075695
      5    9.6377e-04       0.045092       0.835899    0.076997
      6    1.0085e-03       0.045290       0.833897    0.076972

b oscillates with amplitude about +-0.0012 around **0.046122**, period five to
six loops, **with no decay over five observations**. The CF distance sits flat
at about 1e-3 -- ABOVE its own 5e-4 rule -- rather than falling.

## WHAT IT EXPLAINS

    original arm 3, 22 loops   b = 0.047121   ~ the cycle's PEAK   (0.047512)
    re-solve, 8 loops          b = 0.045209   ~ the cycle's TROUGH (0.045092)
    cycle mean, loops 2-6      b = 0.046122

The two "converged" answers are the peak and the trough of one oscillation.
pi_v is the same story: 0.070288 and 0.076023 straddle the observed 0.0699 to
0.0770 range. That is why both passed every rule and disagreed by 4 per cent.

**No tolerance on loop-to-loop movement can converge a limit cycle.** Lowering
`frozen_stop_tolerance` only makes a run grind to its block cap and stop at an
arbitrary phase. 1e-6 was unreachable by three orders of magnitude and setting
it without first measuring the movement was a mistake.

## THE CAUSE, AND THE FIX THE AUTHOR AUTHORISED

`drug_market_adjuster` was 0.2. The drug market's own stability bound was
measured earlier at a < 0.270 -- from the demand elasticity of -9.23, giving
d(gap)/dp = -7.41 -- but that is the drug market ALONE. pi_v adjusts on the
government budget inside the same loop, and the two are coupled: pi_v up ->
more vouchers -> housing changes -> drug demand changes -> price moves ->
budget moves -> pi_v moves. The joint bound is tighter than the single-market
one, and 0.2 is outside it.

Halved to **0.1** on the author's instruction, 19 September. It is a HANDOVER
parameter, so this needs no change to the Fortran and the frozen model is not
touched.

Re-run seeded at the CYCLE MEAN (price 0.8375, pi_v 0.074687) rather than at a
phase extreme, with `frozen_stop_tolerance=1e-5` -- ten times looser than the
unreachable 1e-6, ten times tighter than the 1e-4 that allowed the 4 per cent
disagreement, and meaningful only because damping should make the movement
actually decay.

**CONTROL, STATED BEFORE THE RUN.** Damping changes the path, not the fixed
point. If the damped run converges, b must land inside the measured cycle band
**0.046122 +- 0.0012 = [0.04492, 0.04732]**. Outside that band means the
adjuster changed something it should not have.

## THE STANDING RULE THIS WANTS

An arm that has been solved once has not been shown to be solved. A converged
flag on a single run is not evidence; the same arm from a different seed, or
the trajectory of the last several loops, is.
