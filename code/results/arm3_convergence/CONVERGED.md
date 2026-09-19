# ARM 3, PROPERLY CONVERGED. THE ORIGINAL RUN WAS THE OUTLIER.

19 September. `drug_market_adjuster=0.1`, `frozen_stop_tolerance=1e-4`, seeded
at the cycle mean. Eight loops, 36 minutes, `simulation_ended`, all files saved.

## IT CONVERGED, AND THIS TIME THAT WAS CHECKED RATHER THAN READ OFF A FLAG

The acceptance test was set BEFORE the run: the movement must DECAY
monotonically into the stop, and b must land inside the measured cycle band
[0.04492, 0.04732]. Both hold.

    |db|  5->6  2.116e-04
          6->7  9.383e-05
          7->8  2.693e-05        monotone, three readings, into the stop

    CF distance  1.09e-3 -> 9.97e-4 -> 6.11e-4 -> 2.03e-4     decaying
    b = 0.045287                                              inside the band

No earlier arm 3 run met that test. Both of the previous ones stopped at a
phase of an undamped oscillation.

## THE THREE LIVE RULES

    CF moments   2.0303e-04   (rule 5e-4)     ok
    budget       8.8351e-03   (rule 2.5e-2)   ok
    drug gap    -4.9903e-03   (rule 5e-3)     ok, BUT SEE THE CAVEAT

Rental, housing and inheritance are identically zero every loop and are not
checks.

## THE RESULT, AND WHAT IT CORRECTS

                              b        db%    lambda_d    dlam%      h_1      dh1%
    original, 22 loops     0.047121   -42.4%   0.019133   -43.1%   0.006790   +5.1%
    8-loop, loose          0.045209   -44.7%   0.018363   -45.4%   0.006505   +0.7%
    CONVERGED              0.045287   -44.6%   0.018460   -45.1%   0.006542   +1.3%

                              pi_v       price      CEV
    original, 22 loops      0.070288   0.842217    +1.646%
    8-loop, loose           0.076023   0.830199    +3.291%
    CONVERGED               0.076347   0.833490    +3.249%

**The converged point sits with the 8-loop run, not with the original.** The
original -- the run whose numbers were reported -- is the one that was wrong.

Two headline numbers move materially:

- **homelessness rises by 1.3 per cent, not 5.1 per cent.** Predicted: the
  CF-moments rule is 5e-4 ABSOLUTE and h_1 is about 0.0065, so that rule is 7.7
  per cent of h_1 and pins it least. h_1 was always the number most exposed.
- **the CEV is +3.25 per cent, not +1.65 per cent.** The welfare gain from
  Treatment First is about double what was reported.

## THE CAVEAT, WHICH IS REAL

The drug gap finished at -4.9903e-03 against a rule of 5.0e-03 -- **99.8 per
cent of tolerance** -- and its path is not decaying:

    -0.01223 +0.00307 +0.00405 +0.00107 -0.00481 -0.00545 -0.00556 -0.00499

It is hovering near -0.005 rather than closing. Halving `drug_market_adjuster`
pinned the price (0.02 to 0.06 per cent a loop) at the cost of it no longer
being able to walk to the clearing price inside eight loops. The run stopped on
the MOMENT tolerance, which tests b, lambda_d, h_1 and income -- not the drug
gap.

A negative gap means the implied price is below the posted one, so the price
should still be falling, and a lower price means more drug use. **b of 0.045287
is therefore likely a slight UNDERSTATEMENT.** Closing it needs more loops at
the halved adjuster, not a different adjuster.

## WHICH CHANNEL WAS OSCILLATING, MEASURED

Halving `drug_market_adjuster` did what it was meant to: the drug price moved
0.02 to 0.06 per cent a loop and was effectively pinned. It was not the
oscillator. pi_v was -- moving 1 to 4 per cent a loop.

The pi_v update is `pi_v += 0.05*(net_govt_revenues - constraint)`, with the
gain HARD-CODED at 0.05. Its own comment records that it was cut from 0.3 after
measuring dResidual/dpi_v = -16.9 on the omega_c=1 arm with the drug price
pinned, and ends "The gain was tuned in a region the optimal policy arms
leave."

Measured here, by pairing each pi_v step with the printed distance_govt_budget
that drove it -- the inferred residual reproduces the printed distance exactly,
one loop offset:

    dR/dpi_v = +34.2, +10.3, -6.1, -15.2

The two positive readings are the cold value function, not a derivative. On the
trustworthy late readings the multiplier 1 + 0.05*dR/dpi_v is +0.70 and +0.24 --
inside the unit circle. **So the 0.05 gain is adequate in this region and no
change to the frozen Fortran was needed.** What looked like a pi_v instability
was the cold-start hump: the residual peaked at 0.0573 on loop 3 and decayed
0.0398, 0.0096, 0.0050 thereafter.
