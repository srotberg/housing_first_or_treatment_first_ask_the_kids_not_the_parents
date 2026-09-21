# THE FIX WORKS ON THE GRANDFATHERED BUILD, AND MY "PURELY COSTLY" HYPOTHESIS IS RETRACTED

21 September, T=5 grandfathered probe on the fixed source (cbc9639 + f05451d),
seeded from the re-solved post-fix arm 3.

## THE PRECONDITION THIS PROBE EXISTED TO CHECK

    t=1   vouchers_2 = 0.66024643
    t=2   vouchers_2 = 0.67363200        pre-fix: EXACTLY 0.0

**The voucher programme survives past t=1 on the grandfathered build.** That
needed its own check rather than inheriting the coordinator's: the payment site is
one of the five where `voucher_index==1` had to be widened for the grandfathered
state, so the GF payment path is not the path their no-GF run validated.

Startup verification unchanged, as it should be -- it depends on the benchmark,
which the fix does not touch:

    TRANSITION GF: grandfathered= 3.6183336317475669  left in state 1= 0.0
    DRUG PRICE PATH seeded: t=0 1.0  t=1 0.92738703  t=T 0.83283631757376753
    0 HANDOVER IGNORED

## THE FIRST POST-FIX COMPARISON

Against the coordinator's post-fix no-grandfathering numbers at the same horizon:

                            my GF        their no-GF   GF - no-GF
    t=1 lifetime welfare    792.28206    792.194       +0.088
    t=2 lifetime welfare    792.59700    792.521       +0.076
    t=2 voucher spending    0.673632     0.66355       +1.5%

## I RETRACT "GRANDFATHERING MAY BE PURELY COSTLY"

`THE_QUESTION_HAS_INVERTED.md` called that the leading hypothesis on the
corrected baseline. **The first post-fix evidence does not support it.**
Grandfathering still adds about +0.09 utils at t=1 -- close to the +0.100 the
equivalent pre-fix cross-container pair gave, so the ABSOLUTE benefit is roughly
unchanged by the fix.

What died is the FRAMING, not the benefit. "Recovers 24.0 per cent of the total
t=1 loss" is meaningless because there is no loss. The defensible statement is:

**grandfathering makes an already-beneficial reform slightly better at t=1,
lifting a +0.799 utils gain by about eleven per cent.**

That is a much weaker claim for the policy than the brief's, and a much less
dramatic one than "purely costly". Both of my previous readings were too strong in
opposite directions, forty minutes apart, and each was drawn from a single
comparison.

## TWO CAVEATS, AND THEY ARE THE SAME CAVEAT

**The comparison crosses containers.** My GF against their no-GF. Measured on this
very quantity, the cross-container noise is about 0.025 utils: the pre-fix pair
gave +0.100 across containers where the brief's own within-container pair gave
+0.1252. That is a quarter of the effect being claimed.

**And the homelessness cost is not yet measurable.** It was grandfathering's main
cost pre-fix -- h_1 0.008747 against arm 3's 0.007713 at t=1, 0.012876 against
0.010648 at t=2. Post-fix my GF h_1 is 0.0087694 at t=1 and 0.0083786 at t=2,
far below the pre-fix 0.012873 at t=2, so the fix removed most of the transition's
homelessness. **But there is no post-fix no-GF h_1 to difference against**, so
whether grandfathering still RAISES homelessness is open, and that is the question
that decides whether the +0.09 utils is worth having.

Both reduce to one thing: **the GF-minus-no-GF difference needs both arms in one
container, off one benchmark.** The effect is ~0.09 utils on a base of 792, which
is 1.1e-4 relative -- the same order as the cross-container spread.

## WHAT I AM DOING ABOUT IT

Running the NO-GRANDFATHERING arm at T=5 in THIS container, off THIS benchmark,
before launching T=60. Forty-five minutes, and it converts the headline from a
cross-container difference into a controlled pair -- and it answers the
homelessness question, which the cross-container numbers cannot.

It is not duplicated work: the sibling's no-GF run is the production one at a
different horizon, and this is a CONTROL for this session's own measurement. It
also measures the cross-container bias directly, which is the only way to say
what the T=60 cross-container comparison is worth.

## THE PATH SO FAR, loop 0, for the record

    t   h_1         b           lambda_d    p_drug      vouchers_2
    1   0.0087694   0.056834    0.033885    0.927387    0.660246
    2   0.0083786   0.052043    0.032453    0.929318    0.673632

Against the pre-fix probe at the same periods: b was 0.059563 and 0.055854, so
participation is 4.6 and 6.8 per cent LOWER once vouchers are actually paid, and
h_1 at t=2 is 0.0084 against 0.0129. Nothing here is converged -- this is loop 0
of a probe that will be stopped after it, and no number in it is a result.
