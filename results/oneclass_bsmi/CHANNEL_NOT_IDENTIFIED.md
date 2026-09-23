# RETRACTED: "THE b_smi CHANNEL MOVES THE RATIO THE WRONG WAY"
# THE TRACE WAS CONTAMINATED. THE CHANNEL IS NOT IDENTIFIED EITHER WAY.

23 September 01:35 UTC. This file previously asserted, on two blocks, that the
channel had the wrong sign, that its bracket diverged, and that it leaked into
non-SMI households. **A third block inverts the first two and none of those
three claims survives.** The earlier text is replaced rather than appended to,
because it was wrong and a reader should not have to get to the bottom to learn
that. A push notification carrying the wrong conclusion was sent at 01:32 and
is corrected by the one that follows this.

## THE THREE-POINT TRACE

    b_smi     r_smi        b    lambda_d    SUD|SMI   SUD|non-SMI
    1.0000  1.77924  0.13006    0.052442   0.090042      0.050607
    0.9500  1.72495  0.15570    0.061267   0.102158      0.059224
    0.9025  1.79850  0.13829    0.058818   0.101903      0.056660

    net 1.0000 -> 0.9025:   r_smi +1.08%,  b +6.32%

Every column is NON-MONOTONIC. r_smi falls then rises; `b` rises 19.7 per cent
then falls 11.2; lambda_d rises then falls. Read on the first two points the
ratio moves against the channel's premise, read on the last two it moves with
it, and read end to end it moves with it by about one per cent.

## WHY THE FIRST READING WAS WRONG, AND IT IS A DOCUMENTED MISTAKE

This is a JOINT calibration. Roughly twenty other brackets step every block
alongside `b_smi_multiple`, and the drug block's own instruments are visibly
fighting: `b` oscillating 0.13006 -> 0.15570 -> 0.13829 is other instruments
correcting, not the SMI multiple acting. The `b` moment moved 19.7 per cent in
one block while `b_smi_multiple` moved 5, so the confound is several times the
size of the effect being read.

ENGINE.md's phase 3 rule 1 says exactly this, and says it was already paid for:

    ONE PARAMETER PER DIAGNOSTIC POINT, AND READ IT AT LOOP 0. Three
    conclusions were drawn and retracted in one night because a multi-parameter
    trace was read as though it isolated one parameter... THE WIDE,
    SINGLE-PARAMETER TEST COMES FIRST, NOT AFTER THE THEORY.

That rule was read at the start of this session and then broken anyway, in the
form it warns about most precisely -- a two-point trace, a confident mechanism
to explain it, and a recommendation attached.

## WHAT IS AND IS NOT ESTABLISHED NOW

NOT ESTABLISHED, all three previously asserted:

  - the SIGN of the channel. +1.08 per cent end to end, against a swing of
    -3.05 then +3.68, is not a direction;
  - that the bracket DIVERGES. The distance went 0.75627 -> 0.76371 -> 0.75363,
    up then back down. Two points made a trend out of a wobble;
  - that it LEAKS. The SUD|non-SMI move was computed across a pair in which
    every other instrument had also stepped, so it measures the whole block's
    work, not this parameter's.

STILL ESTABLISHED, and independent of the trace:

  - the wiring IS SMI-conditional, at 12668, checked in the source;
  - the resume divergence and the 1e-12 corner guard, in RESUME_DIVERGENCE.md.
    Those rest on within-block structure and on the source, not on this trace;
  - the cold start reproduces to a relative 3e-5.

## THE TEST THAT WOULD ACTUALLY SETTLE IT

A one-parameter diagnostic, which is what should have been run before any
conclusion was offered: two COLD points identical in every respect except
`b_smi_multiple` -- 1.0 against something wide, 0.5 or lower, since 5 per cent
is inside the confound -- each read at its FIRST moment block, before the other
brackets have taken a step. A cold point costs about five and a half minutes,
so the pair is a quarter of an hour.

It needs the four cores, which the calibration currently owns. That is the
author's call, and it is the open question put to them: pause the calibration
for fifteen minutes to identify the channel, or let it keep running and accept
that the b_smi row cannot be interpreted meanwhile.

## WHAT IS NOT BEING DONE

No Fortran edited, the adjuster untouched, the run left going. The earlier
recommendation to HOLD the channel is WITHDRAWN -- it rested on the divergence
claim, which is retracted.
