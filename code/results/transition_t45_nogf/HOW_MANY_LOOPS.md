# HOW MANY LOOPS. MEASURED ON A CONTROLLED PAIR, AND THREE WRONG ANSWERS FIRST.

21 September. The container restart at 09:46 produced, by accident, the cleanest
experiment available: two runs of the SAME loop, one loop of price walking apart,
same code, same everything. Run 1's loop 0 seeded from the constructed T=45 seed;
run 2's loop 0 seeded from run 1's own output.

## THE CAP BINDS EVERYWHERE. THIS IS A WALK, NOT A CONTRACTION.

    price step, run 1 -> run 2:  EXACTLY -0.500% in all 21 paired periods

Not approximately. `max_drug_price_move=0.005` is the binding constraint in every
period of every loop, so the loop count is set by how far the price must travel
divided by half a per cent, and nothing in the economics changes that.

## WHAT ONE LOOP BUYS

               run 1     run 2     fell    loops to the 0.0100 rule
    max       0.1818    0.1675   0.0143            11
    mean      0.1548    0.1379   0.0170             8
    min       0.1254    0.1092   0.0162             6

**The rule is a MAXIMUM over periods, so 11 is the number.** At 4.7 hours a loop
that is about 52 hours.

**And the fall is ACCELERATING, not slowing**: 0.0122 per loop over the first
half of the paired window against 0.0213 over the second. A path stalling short
of its root does the opposite.

## THREE WRONG ANSWERS, AND THE SAME MISTAKE EACH TIME

Told to the author before this one, all wrong:

    "about 3 loops"    from a pre-fix bracket that is not this economy's
    "17 loops"         from a period-by-period pairing
    "47 loops"         from the proportional reading of the same pairing

The pairing was the error, and the author found it by asking whether a drop at
t=6 was "because of pv or piv or stuff like that". It was the price, but not as a
defect. **Both runs' distance series are sawtooths, and they fall at DIFFERENT
periods** -- run 1 at t=7,10,17,18,19 and run 2 at t=6,9,16,17,21 -- so
differencing period by period subtracts a trough from a peak and reports a fall
five times too large at one period and too small at the rest. The sawtooth itself
is inherited: the price path carries bumps at t=2 and t=8 straight from the T=30
measured secant roots the seed was built from.

The statistic the stopping rule uses -- the maximum over all periods -- is immune
to the misalignment. It should have been the first thing computed.

## PI_V IS NOT IN ANY OF THIS, AND THAT IS THE REAL UNKNOWN

    pi_v: ONE distinct value in each run, frozen at 0.0768762

`start_updating_at_loop_number=0`, so pi_v first moves in **loop 1's forward
pass, period 1**. Everything above is the drug market alone, and the drug market
is the half that works.

**The only loop 1 in this project's history destroyed the solve**: pi_v collapsed
to its floor and took distance_drug_market from 0.017 to 0.680 in three periods
(`t30_loop1_pivcollapse.log`). The secant, the trust region and the
quarter-of-pi_v clip were written to stop exactly that and **have never been
exercised on a transition**. One observation of failure, zero of success.

So: **11 loops if pi_v behaves and barely perturbs the price path; more if it
perturbs it, since a moving pi_v moves incomes, demand and therefore the root the
price is walking toward; and no useful number if it collapses.**

The test is one period long and costs nothing extra.
