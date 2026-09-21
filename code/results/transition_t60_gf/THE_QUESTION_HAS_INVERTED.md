# GRANDFATHERING'S QUESTION HAS INVERTED. There is no t=1 loss left to recover.

21 September, after the coordinator's 52cee58. Written before this session's T=60
run, because the brief it was given no longer describes what the run measures.

## WHAT THE BRIEF SAID THIS ARM WAS FOR

> grandfathering improved t=1 lifetime welfare by +0.1252 utils over arm 3
> (790.9978 vs 790.8726, benchmark 791.3946), **recovering 24.0 per cent of the
> total t=1 loss** and 33.4 per cent of the childhood loss [...] The open question
> your run answers: over a full horizon, does the avoided revocation outweigh the
> extra use? T=5 truncates the benefit while letting the cost run in full, so
> +24 per cent is a FLOOR.

Every clause of that rests on Treatment First imposing a t=1 LOSS. The policy
motive was the one in `grandfather_voucher_states`' own declaration: *"so the
policy never puts the caught generation's children on the street."*

## WHAT THE FIX DID TO THAT PREMISE

The coordinator's controlled before/after at T=5, one source change:

                    pre-fix     post-fix    vs benchmark 791.39464
    lifetime t=1    790.873     792.194     +0.799
    CEV t=1         -9.272%     +2.306%

**Treatment First is welfare-improving at t=1.** The -9.272 per cent that the
whole grandfathering rationale was built on was the collapsing fair-market-rent
cap, not the reform.

## SO THE QUESTION IS NOT THE ONE IN THE BRIEF

It is no longer *how much of the t=1 loss does grandfathering recover.* There is
no loss. It is:

**how much of the t=1 GAIN does grandfathering forgo, and does the avoided
revocation buy anything at all?**

And the pre-fix evidence, read under the new baseline, points somewhere
uncomfortable. The T=5 grandfathered test found homelessness HIGHER than arm 3's
transition, not lower -- 0.008747 against 0.007713 at t=1, 0.012876 against
0.010648 at t=2 -- because the exempt lose their deterrent and b rose 21.7 per
cent. Those costs do not depend on the sign of the baseline. What has vanished is
the benefit they were being traded against.

    pre-fix framing   TF inflicts a large t=1 loss; grandfathering recovers 24
                      per cent of it. A partial remedy for a real harm, and the
                      humane instinct is also the efficient one.
    post-fix framing   TF is a t=1 gain. Grandfathering exempts 7.1 per cent of
                      the population from a policy that is already improving
                      welfare, raises homelessness and use while it does so, and
                      delays convergence to the +3.249 per cent long run.

**On the corrected baseline grandfathering may be purely costly.** That is not
established -- it is what the run has to measure -- but it is now the leading
hypothesis, where before the run was expected to confirm a floor under a benefit.

## WHY THAT MAKES THE T=60 RUN MORE VALUABLE, NOT LESS

Because the policymaker's instinct -- protect the generation the reform catches --
may be exactly wrong, and a result that says so is worth more than one confirming
it. The exempt cohort's children are not obviously helped by an exemption from a
reform that raises their parents' welfare; they are exposed to a parent who keeps
using.

And the horizon is now the binding uncertainty rather than a detail. The
coordinator says so in the same commit:

> T=5 puts the terminal steady state four periods away, so t=1 inherits much of
> the long-run gain. The horizon contaminates both sides equally, so the SIGN FLIP
> is real while +2.306 per cent is not the transition's true t=1 cost.

At T=5 the terminal steady state sits four periods from t=1, so t=1 is reading
mostly the long-run gain. **T=60 is the only horizon in this project that is
defensible for the grandfathered arm at all**, for the reason the brief gives: a
household aged 26 at the reform reaches 85 at t=59, so at any shorter horizon the
exempt are still alive at the terminal date and arm 3 is not a valid terminal
condition.

## WHAT THIS DOES NOT CHANGE

The design is not reopened. Grandfathering keys on voucher-holding status at
implementation because the government cannot observe SUD, and that status is
observable, fixed before announcement and impossible to game. That reasoning is
untouched by the sign of the baseline.

Nor does it change what has been verified: the benchmark, arm 3, the t=0 mapping
and the memory model all stand, and arm 3 is re-solving on the fixed source now.

## THE PRIOR IS WITHDRAWN, NOT ADJUSTED

The brief's +0.1252 utils and 24 per cent were measured on two runs that both
lost the voucher programme after one period. This session already withdrew "24
per cent is a FLOOR" on the grounds that the bug truncated the benefit on both
sides. **The stronger statement is now available: the quantity that 24 per cent
was a fraction OF does not exist.** Neither the magnitude nor the sign carries
over, and no number from the pre-fix grandfathered test should be quoted again.
