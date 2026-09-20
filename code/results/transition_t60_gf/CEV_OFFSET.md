# ARM 3'S CEV SHOULD COME OUT ABOUT +3.46%, NOT +3.249%, AND THAT IS NOT A FAILURE

Written BEFORE arm 3 finished, because the brief says to STOP and report if arm 3
does not land near the archive's numbers, and one of those numbers is going to
move for a reason that has nothing to do with arm 3.

## WHAT WAS MEASURED

The benchmark re-solve reproduces n90 on every equilibrium object:

    b        +0.088%     lambda_d  -0.044%     h_1   -0.006%
    V        +0.011%     shifter   -0.007%

but its saved welfare curve sits a near-CONSTANT 0.0711 utils BELOW n90's at all
21 points -- from -0.070430 at x=-0.5 to -0.071390 at x=+0.5, so the difference
itself varies by 1.4 per cent across a 100 per cent range of x.

A difference that flat is an ADDITIVE, CHOICE-INDEPENDENT term. It is not a
different equilibrium: a different equilibrium would move the moments, and the
moments agree to better than a tenth of a per cent.

## WHY THE CURVES DIFFER: kappa_x, AND THE ORDER THE RECIPE PRESCRIBES

`kappa_x` enters flow utility as `kappa_x*H` with H the AGGREGATE homelessness
rate, so it is independent of every household's own choice and shifts welfare
levels while moving no policy and no moment. That is exactly the shape observed,
and it is why CALIBRATION_RECIPE.md section 9 can put the benchmark at step 2 and
"pin kappa_x from the probe" at step 3: the benchmark does not need to know it.

**So the n90 benchmark ran at kappa_x = 0.002, the coded default.** Its own
`resume_seed.dat` says so -- that file writes the LIVE value of every handover
parameter on each save -- and the step order explains why. The 0.8139 the probe
then produced was applied to the ARMS and to the transition. This session's
benchmark was run at 0.8139 from the start, because the arms and the transition
all run there and a benchmark whose welfare cannot be differenced against theirs
is useless.

**The kappa_x accounting does not fully close, and that is stated rather than
papered over.** Using this run's own probe, `H*(D_child + beta^25*D_adult) =
0.118174` measured at H = 6.4576e-3, a change of 0.8139 - 0.002 predicts a shift
of -0.0960. The observed shift is -0.0711, which is 74 per cent of it. So either
n90's curve was written at some kappa_x other than the coded default, or a second
additive term contributes. **The prediction below does not depend on resolving
that**, because it uses the MEASURED curve shift and not the model of it.

## WHY IT REACHES THE CEV, AND BY HOW MUCH

`calculate_welfare_gains` hard-codes `vf_simulation='baseline_benchmark'` (22641)
and reads `welfare_curvebaseline_benchmark.dat` (22643). Every arm's CEV and the
transition's whole welfare path are obtained by INVERTING the benchmark's saved
curve at the arm's own lifetime welfare. So the curve's level is not a diagnostic,
it is the measuring stick.

    the archive:  arm 3 ran at kappa_x=0.8139 and inverted a curve written at the
                  coded default. Measuring stick and object not on the same
                  kappa_x, so the reported CEV carries the offset.
    this chain:   benchmark, arm 3 and the transition are all at 0.8139. The
                  inconsistency is removed.

The curve's local slope at arm 3's welfare, off the saved points themselves --
791.3946 at x=0 and 793.0949 at x=0.05, and arm 3's lifetime welfare of 792.5130
sits between them -- is 34.0 utils per unit x. A measuring stick 0.0711 utils
lower returns a HIGHER x for the same welfare:

    0.0711 / 34.0 = 0.00209   ->   CEV higher by 0.209 percentage points

## THE PREDICTION, AND THE TEST

**If arm 3 reproduces the archive in every other respect, its CEV here should be
about +3.46%, not +3.249%.** The direction is firm: the shift is measured, its
sign is known, and the inversion is monotone. The size carries the 26 per cent of
the shift that the kappa_x accounting does not explain.

So the acceptance test on arm 3 splits in two, and only the first half is a test
of arm 3:

    b 0.045287   lambda_d 0.018460   h_1 0.006542   pi_v 0.076347
    price 0.833490                          -- these must reproduce
    CEV +3.249%                             -- this must reproduce +3.249% PLUS
                                               0.21pp, i.e. about +3.46%

**A CEV of +3.249% here would be the surprise**, not a confirmation: it would mean
the curve shift did not propagate, and the first thing to check would be whether
arm 3 read a stale `welfare_curvebaseline_benchmark.dat`.

## WHAT IT MEANS FOR THE TRANSITION, WHICH IS THE POINT

The transition reports a welfare PATH and a CEV per period through the same
inversion, so the same 0.21pp offset sits on every period of it. That is:

- **harmless for the shape**, the trough, the recovery and the comparison of the
  grandfathered arm against the non-grandfathered one, because it is one additive
  constant applied to both;
- **material for any level quoted against the archive**, including the T=5 prior's
  790.9978 / 790.8726 / 791.3946 triple, which was measured on the archive's
  measuring stick;
- **a reason both transition arms must be inverted against the SAME curve.** If
  the two sessions' benchmarks differ in their curve level the way this one
  differs from n90's, the grandfathered-minus-not difference -- +0.1252 utils at
  T=5 -- would be contaminated by a constant of comparable size. The two arms
  agreeing on b and h_1 to 0.1 per cent is NOT sufficient; they have to agree on
  the curve.

That last point strengthens the decision already put to the coordinator in
HOLD.md, and changes its basis: the case for one benchmark is not the
cross-container spread on the moments, which turns out to be tiny. It is the
welfare curve, which is an additive level that the moments cannot detect.
