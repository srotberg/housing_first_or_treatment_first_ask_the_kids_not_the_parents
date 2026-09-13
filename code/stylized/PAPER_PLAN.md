# The stylized model's exposition, as the author laid it out

The author, 13 September 2026, in their own words:

> *"we start from the simple model without omega_c or delta_d. show that
> mortality is what reverses the gradient. then show how we measure the optimal
> degree of SUD by calibrating omega_c and delta_d and letting the reader know
> that omega_c does not affect the income gradient. then showing what the
> optimal SUD is, running HF and then showing TF and how it can actually improve
> newborn welfare even in the short run!"*

This file records that arc and, against each step, what is MEASURED, what is
NOT, and what still has to be done before it can be written. Nothing here has
been written into the paper. It is a plan, not prose.

## Step 1. The simple model: mortality reverses the income gradient

Turn `omega_c` and `delta_d` off and show the gradient.

**MEASURED AND STRONG.** At sigma = 2 the flow utility is `X^(1-sigma)/(1-sigma)
= -1/X`, so the goods part of value is NEGATIVE and `aleph` is what makes a life
worth living. For the poorest, `W2 < 0`: the cheapest rental costs 0.10 and the
poorest household earns 0.108, so it either pays the rent and consumes nothing
or takes the street. A negative continuation makes the mortality penalty a
BENEFIT -- multiplying a negative number by a smaller survival probability
RAISES it -- so those households buy the smallest sliver of drug the grid sells
purely to acquire the disorder and die sooner.

The calibrated model has 1.56 per cent of period-2 states in that condition, and
the quantitative model instruments the same thing at 0.45 per cent.

**THE CLEANEST DEMONSTRATION AVAILABLE, and it is already run.** Put an income
floor at 0.182, which is the smallest floor that clears the negative value of
life entirely, and the using population collapses:

    no floor      43 of 120 income nodes use, lowest user at y = 0.108
    floor 0.182    9 of 120 income nodes use, lowest user at y = 0.449

Thirty-four of the forty-three using income levels disappear and every one of
them is poor. The floor and the mechanism are the same object: the argument is
that the gradient reverses at the bottom because life is worth little there, and
a floor is an instrument for making life worth having at the bottom. That table
is the figure for this section.

## Step 2. Calibrate `omega_c` and `delta_d`

**DONE, and both are identified by their own moments** -- which was not true at
any earlier point. The calibrated vector is `calibrated_sep13.json`:

    moment                    model    target    gap
    housing spending         0.2668    0.2680   -0.5 %
    value of life           79.9997   80.0000   -0.0
    homelessness             0.0103    0.0100   +3.1     (quantised, see below)
    participation            0.0887    0.0890   -0.4
    unemployment             0.0485    0.0485   +0.0
    SUD rate of the homeless 0.2170    0.2170   +0.0
    child use gap            0.1839    0.1834   +0.3
    child SUD odds ratio     2.0212    2.0000   +1.1
    income of users          0.7338    0.7400   -0.8
    drug spending share      0.1413    0.1410   +0.2

Median 0.4 per cent, nine of ten inside 1.1.

`pi_base` is NOT calibrated and must not be described as though it were: onset is
a flat rate on anyone who buys, so `sud = part * pi_base` identically, and with
participation on target `pi_base = 0.0368/0.089 = 0.41348` exactly.

Homelessness is QUANTISED at this income grid -- across twenty-eight tables it
took exactly two values, 0.0096 and 0.0103, with the target of 0.0100 between
them -- so +3.1 per cent is the best attainable and it is not a calibration
failure. Say so rather than leaving a reader to wonder.

## Step 2a. "`omega_c` does not affect the income gradient"

**NOT YET MEASURED. This is load-bearing and it is the one gap in the arc.**

It is what lets the child channel be introduced without disturbing the mechanism
established in step 1, so it needs the same treatment `delta_d` already got:
hold the vector, sweep the parameter, show the adult block does not move.

For `delta_d` that test is done and it is clean -- drug share, income of users,
participation and the SUD rate are identical to four decimals from 0.308 to
0.700 while the child odds ratio runs 1.41 to 2.11. The equivalent sweep for
`omega_c` has not been run.

## Step 3. The optimal degree of SUD, at `omega_c = 1`

**MEASURED, AND THE HEADLINE IS NOT THE PARTICIPATION NUMBER.**

    omega_c   use rate    SUD    drug share   vs benchmark
     0.0152     0.0887   0.0367     0.1413       0.0 %
     0.0500     0.0709   0.0293     0.0000     -20.1 %
     0.2500     0.0723   0.0299     0.0000     -18.5 %
     1.0000     0.0746   0.0308     0.0000     -15.9 %

Use falls about a sixth and stops, which is NOT "close to zero" and the author
expected it might be. But the DRUG SHARE is 0.0000 at every `omega_c` above the
calibrated one: the quantity bought collapses entirely and what survives is the
extensive margin on the corner branch -- households buying the grid's smallest
sliver for the mortality lottery of step 1.

So the honest statement is that optimal SUD is essentially zero in quantity
terms, and the residual participation is the same negative-value-of-life
mechanism the paper has just established. That is a better sentence than the
one the -15.9 per cent alone would support.

## Step 4. Housing First, then Treatment First

Voucher coverage is 26.60 per cent of ELIGIBLE households under every policy,
with the eligible population identical at 0.2309 -- eligibility being income
below half the median. `pV = 0.266` is HUD 2023, recipients over the income
eligible population.

**RATIONED TF IS IDENTICAL TO PLAIN TF and the reallocation factor is exactly
1.0000.** Conditionality in this model works as a DETERRENT, not as a rationing
device: use falls from 8.87 to 1.79 per cent, so almost nobody is disqualified
in equilibrium and no vouchers are freed to reissue. The budgets are already
equal at an outlay of 0.012977, so there is nothing for a higher `pV` to absorb.
That is worth stating plainly -- a reader will expect a rationing trade-off and
there is not one to report.

## Step 4a. "TF can improve newborn welfare even in the short run"

**THE MEASUREMENT DOES NOT SUPPORT THIS AS WRITTEN, and it is the one place the
arc and the numbers disagree.**

Lifetime welfare = childhood + adult, with the timing the author specified:
cohort 1 is the children alive when the policy changes, so its childhood is
lived under the NEW policy while its parents' disorder status is still the
pre-reform one it was born into.

    cohort        TF       HF null     TF net of the null
        1     -0.223 %     0.000 %        -0.223 %     <- clean
        2     +3.082 %    +3.303 %        -0.22        <- artefact, see below
        3     +4.441 %    +0.351 %        +4.09
     long     +4.489 %    +0.001 %        +4.49        <- clean

Cohort 1 LOSES 0.223 per cent of lifetime consumption. Including childhood makes
the loss smaller than the adult-only figure would suggest, but it does not flip
the sign. The gains begin at cohort 3 and reach +4.489 per cent in the long run.

The author's hypothesis for why it might have been positive was right in its
mechanism and wrong in its size:

> *"when you remove vouchers for parents with Sud, it hurts some of them and
> their kids, but it helps other kids since their parents don't use and they
> have better life prospects"*

Both halves are there. Measured, at each household's realised allocation:

    policy         childhood    kid c     kid h    street    users
    Housing First   1.433488   0.66747   0.26338  0.01341   0.08695
    Treatment First 1.430496   0.66756   0.26326  0.01472   0.01540

Consumption DOES rise as five sixths of users stop buying -- but by 0.013 per
cent, because the drug was a small share of a small group's spending. Housing
falls and childhood street exposure rises ten per cent, and housing carries
`phi_h = 0.373` in the child's bundle. The channel that hurts children under
Treatment First is HOUSING, not drugs, and the drug improvement is far too small
to offset it. That is the paper's own thesis and it should be said in those
terms.

## WHAT MUST BE FIXED BEFORE ANY OF THIS IS WRITTEN

1. **The transition's null is clean at the ends and not in the middle.** Running
   Housing First as the reform must leave every cohort at zero. Cohort 1 is now
   exactly 0.000 and the long run 0.001, after passing `par` to the baseline --
   `_welfare(p0, v1b)` without it falls back to the module constant `DEL_D`, a
   FRACTIONAL cut, while the path passes `par.delta_d`, a LOG shift. But cohort
   2 reads +3.303 per cent under the null. Cohorts 2 and 3 must not be quoted
   until that is zero.

   The suspected cause is that `_rest_point` and `_step` are not the same map,
   but that diagnosis is NOT confirmed: the test that produced it passed
   `ev_s0`, the fourth return of `_policy_grids`, where the real path uses
   `_hl_by_shift`. Recheck before concluding the code is wrong.

2. **The `omega_c` gradient sweep of step 2a**, which has not been run.

3. **`aleph_for_child` is a judgement, not an identity.** The child's own life is
   valued at `(xi-1) * aleph` on top of the parent's, and the switch is ON in
   every number above. Off, a childhood is worth its goods alone. Whichever way
   the paper goes, it has to say which.
