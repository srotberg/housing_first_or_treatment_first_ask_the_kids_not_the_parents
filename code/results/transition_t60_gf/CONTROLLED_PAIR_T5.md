# GRANDFATHERING, MEASURED AGAINST ITS OWN CONTROL IN ONE CONTAINER

21 September. Post-fix (cbc9639 + f05451d), T=5, loop 0, both arms off THIS
session's benchmark and THIS session's re-solved arm 3, both reading a seed
verified byte-identical by `cmp`, both under the same handover. One source switch
differs: `grandfather_voucher_states`.

Nothing here is converged. This is loop 0 of a pair of probes and no number in it
is a result. What it establishes is signs, orders of magnitude, and which periods
can be read at all.

## THE PAIR

     t | h_1 GF-noGF | b GF-noGF | lambda_d | welfare GF-noGF | noGF gain | GF gain
     1 |     +14.4%  |   +23.6%  |  +0.82%  |    +0.08416     | +0.87434  | +0.95850
     2 |      +9.1%  |   +16.2%  |  +0.19%  |    +0.06769     | +1.20575  | +1.27344
     3 |      +5.3%  |   +12.0%  |  +0.07%  |    +0.13114     | +1.01043  | +1.14157
     4 |     -11.4%  |    +8.1%  |  -0.15%  |    +0.36280     | +1.05298  | +1.41578

Gains are against this session's benchmark lifetime welfare of 791.32356.

## ONLY t=1 AND t=2 ARE READABLE, AND THE SOURCE SAYS SO IN ADVANCE

The terminal value function has **no grandfathered slab**, and at a short horizon
it is filled from the ordinary holder. The declaration is explicit that this is a
modelling choice, taken because a zero continuation "would make exemption look
catastrophic and the test worthless":

> The terminal steady state has no grandfathered mass -- by T>=60 the exempt
> cohort is dead -- so the file carries no such slab [...] At a SHORT horizon the
> cohort is still alive at T and would read a zero continuation.

At T=5 the exempt are alive at the terminal date, so at t=4 they are pricing their
future against a continuation that is not theirs. h_1 flipping sign at t=4, from
+5.3 per cent to -11.4, is that boundary and not economics. **This is exactly the
defect T=60 removes**: by t=59 the exempt are dead, nothing reads the slab, and
the same comparison becomes readable across the whole path.

t=3 is marginal for the same reason, one period further from the boundary.

## WHAT THE READABLE PERIODS SAY

**Grandfathering is welfare-improving, and smaller than the brief implied.**
+0.08416 utils at t=1 -- a 9.6 per cent larger gain than the reform alone, which
delivers +0.87434 on its own.

**Its costs are real and they are not artefacts of the cap bug.** +14.4 per cent
homelessness and +23.6 per cent participation at t=1, against +13.4 and +21.7
measured PRE-fix. The costs reproduce on a working baseline almost unchanged,
where the benefit's whole framing did not.

**Both decay monotonically**, +14.4 -> +9.1 -> +5.3 on homelessness and +23.6 ->
+16.2 -> +12.0 on participation. That is the exempt cohort thinning, and it is the
one clean pattern in the table. An earlier reading of this session claimed the
BENEFIT decays with them; t=3 contradicted it, and two points were never a trend.

**lambda_d barely moves** -- +0.82 per cent at t=1, +0.19 at t=2. Grandfathering
changes who USES, not who has the disorder, over five periods. That is the same
shape CALIBRATION_STATE.md found for the reform itself: participation responds at
once, the stock of disorder turns over only with the cohort.

## THE MECHANISM, WHICH RESOLVES AN APPARENT PARADOX

Grandfathering raises homelessness AND raises welfare. Both, at once, and it is
not a contradiction.

The welfare measure is the t=1 cohort's LIFETIME welfare including childhood, and
**newborns are not grandfathered -- their parents are.** So the gain arrives
through the childhood term, as parents keep housing they would otherwise lose to
revocation. The brief said the same of the pre-fix T=5 test: "ALL of it in the
childhood term, since newborns are not grandfathered, their parents are."

Meanwhile the exempt keep using, which raises the drug price for everyone. The
measured t=1 implied price on the grandfathered arm is 1.019 against 0.927 faced,
a gap of +0.0917, where the no-GF arm faces the same seed. A dearer drug worsens
outcomes for the NON-exempt, who are still subject to conditionality -- which is a
plausible route by which aggregate homelessness rises while the exempt themselves
are housed.

**So grandfathering looks like a transfer to the caught generation's children with
real efficiency costs attached, not a free mitigation.** On five periods of loop 0.

## THE CROSS-CONTAINER NOISE IS THOUSANDTHS, NOT HUNDREDTHS

This session repeatedly warned that the GF-minus-noGF difference is 1e-4 relative
and could drown in cross-container spread. Now measured:

    this session's no-GF t=1 welfare   792.19790
    the coordinator's                  792.194      0.0039 apart
    this session's no-GF t=2           792.52931
    the coordinator's                  792.521      0.0083 apart

Against an effect of +0.084. So the cross-container comparison was worth about
five per cent of the effect, not the twenty-five per cent this session assumed
from the w_bot figure. **The earlier warnings were too pessimistic**, and the
"both arms need one benchmark" argument is weaker than argued -- though still
correct in principle, and free to honour when one container holds both.

## WHAT THIS DOES NOT SETTLE

The horizon. At T=5 the terminal steady state sits one to four periods away and
every period inherits most of the long-run gain: the no-GF gain reaches +1.206 by
t=2 against a long-run +3.249 per cent CEV. The coordinator's own note on the
sign flip makes the same point -- the sign is real, the magnitude is not the
transition's true t=1 cost.

T=60 is the run that answers it, and for this arm it is not a preference: the
exempt cohort must be dead before arm 3 is a valid terminal condition, and a
household aged 26 at the reform reaches 85 at t=59.
