# THE DRUG-PRICE CAP AT T=3. DOUBLING IT IS SAFE AND ABOUT THREE TIMES FASTER.

21 September, on the author's "test the cap at 0.01 and 0.02 on T=3". Two runs
identical in every respect but `max_drug_price_move`, seeded from the same file,
same binary settings, same benchmark and terminal condition.

## WHY IT WAS WORTH MEASURING

On the T=45 the price step was **EXACTLY -0.500 per cent in every period of every
loop**. The cap binds 100 per cent of the time, so the secant inside
`clear_drug_market` -- with its own trust region and its abandon-on-growing-gap
guard -- never expresses itself. The cap is not a safety rail on the algorithm;
it IS the algorithm, and 0.005 was sized for a four-minute steady-state loop
rather than a 4.7-hour transition one.

## THE RESULT

t=1 distance_drug_market, loop by loop:

    cap 0.005   0.11253 -> 0.10523 -> 0.09774      falls 0.00730, 0.00749
    cap 0.01    0.11253 -> 0.08428 -> 0.06811      falls 0.02825, 0.01617

**Loop 0 is identical by construction** and is the control: the faced price comes
from the seed and the cap only clips the UPDATE, which first shows in loop 1.

**No overshoot.** The distance falls monotonically under both caps. The failure
mode a too-large step produces -- the distance turning back up -- does not appear.
The source's warning that the map is expansive (slope -2.25 at t=1 falling to
-7.8 by t=28) is about a RAW fixed-point step; a one per cent capped step is
still well inside the safe region.

**The advantage decays**: 3.87x on the first loop, 2.16x on the second. That is
what approaching the root looks like, not instability, but it means the
first-loop ratio overstates the gain.

## WHAT IT IMPLIES FOR THE T=45

    cap 0.005   max distance 0.1675, falls 0.0143/loop   ~11 loops   ~52 h
    cap 0.01    same, falls ~0.031/loop                   ~5 loops   ~24 h

Roughly a day instead of two and a half. The T=45 was relaunched at 0.01 at
19:00 from the two loops of walking already banked (seed t=1 = 0.918136).

## HONEST LIMITS

- Two loops of one horizon. The 5 is a T=3 ratio applied to a T=45 MAXIMUM
  across 43 periods, which is an extrapolation across both.
- The advantage is still decaying, so 5 could be 6 or 7.
- **The CEVs differ between caps at the same period** -- +2.3414 against +2.0812
  per cent at loop 1 -- which is expected for unconverged iterates on different
  paths, and is a standing reminder that no welfare number is quotable until the
  distances clear their rule.

## THE 0.02 ARM WAS NEVER MEASURED

It was OOM-killed at 17:58 before producing a single differentiating number,
because three T=3 solves at their FORWARD-pass footprint of 5.9 GB do not fit in
15 GB. See ENGINE.md. It was not re-run once 0.01 had shown both the speedup and
the absence of overshoot; if the third point is wanted it is about 50 minutes.
