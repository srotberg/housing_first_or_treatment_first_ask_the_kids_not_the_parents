# Why omega_c = 1 barely moves drug use in the quantitative model

The author, 10 September: *"we need to understand why in the quant model even
omega_c = 1 barely moves drug use.. I think it is the key to almost everything"*.

It is measured below, and it is a factor of ROUGHLY NINE against the stylized
model, decomposing into two factors that are both real and both structural.

## The two models, side by side

The comparable object is the deterrent a parent faces from transmitting the
penalty, expressed as a share of a life, because the two models' utility units
are not otherwise commensurable.

    STYLIZED, omega = 1
      child's loss DELTA                     0.332192 utils
      lifetime value at birth E[V1]          3.42834 utils
      DELTA / V1                             9.69 per cent
      weight it is applied with              1.00     (period 1, with certainty)
      DETERRENT                              9.69 per cent of a life

    QUANTITATIVE, omega_c = 1
      child's loss E[V_child(d=1)]-E[V_child(d=0)]
                                             -104.2 utils at the lowest
                                             productivity node, -69.4 at the
                                             highest; drug users are poor, so
                                             the margin sits near -104
      newborn lifetime value                 2195.0 utils
      ratio                                  4.75 per cent
      weight it is applied with              0.2333   (see below)
      DETERRENT                              1.11 per cent of a life

    RATIO                                    9.69 / 1.11 = 8.7   <- WITHDRAWN, see
                                             the aleph correction below; it is 2.1

## Factor one: WITHDRAWN -- IT IS TWICE THE SIZE, NOT HALF

**The section below is WRONG and is kept only so the error is legible. See
"THE ALEPH CORRECTION" at the end of this file.** It divides the child's loss by
a lifetime value that is dominated by an additive constant, which is not a
denominator any behavioural comparison can use.

## (superseded) Factor one: the child's loss is half the size, 4.75 against 9.69

This is despite the QUANTITATIVE model's income penalty being LARGER --
`penalty_child_addicted` is 0.36 against the stylized `DEL_D` of 0.24. The
quantitative child is insured against it: unemployment insurance, the
supplemental security income floor, the voucher, a savings decision, and a
progressive tax all absorb part of a productivity cut that a two-period model
with none of them passes straight through to utility. Factor 1.71 to 2.04.

## Factor two: the term is collected only when the parent DIES, factor 4.3

This is the larger half, and it is a direct consequence of the design rule in
`code/stylized/TRANSITION_LESSONS.md` -- the child's inherited penalty keys on
the period the parent dies in. In the Bellman the child term reads

    beta * (1 - survival(age,h,d,smi)) * omega_c * DeltaV_child

so it is multiplied by the probability of dying THIS PERIOD. Summing the
discounted hazard from age a, staying in one survival regime, gives the weight
the parent actually applies:

      age   data age   1-phi clean   1-phi SUD    W clean    W SUD
        1      25        0.00094      0.00754     0.0521    0.1934
        6      30        0.00106      0.00850     0.0674    0.2333
       11      35        0.00130      0.01042     0.0882    0.2854
       21      45        0.00293      0.02345     0.1510    0.4249
       31      55        0.00659      0.05272     0.2471    0.5763

W is the DISCOUNTED probability of dying; undiscounted it is 1 by construction,
and the whole of the gap between 1 and 0.23 is beta compounding over the decades
between the drug choice and the death that transmits it. The SUD column is the
relevant one because `kappa_phi_d_level = 8` multiplies the death hazard
eightfold, which pulls the transmission date forward and is the only reason the
weight reaches 0.23 rather than 0.07.

THE PERSISTENCE ASSUMPTION BEHIND W_SUD IS CHECKED, NOT ASSUMED. At the
benchmark the share of newborns born to a parent who died with the disorder is
0.045707 + 0.007395 = 5.310 per cent, against a population disorder rate of
3.702 per cent -- a ratio of 1.43, exactly the over-representation the eightfold
hazard predicts. The child class carries 5.19 per cent of the population, which
agrees. So a household that acquires the disorder usually still has it when it
dies, and the absorbing calculation is the right one.

## What this explains

At omega_c = 1 the parent's deterrent is 1.11 per cent of a life. It moved
`b` from 0.087846 to 0.073182, a fall of 20.04 per cent. That is not a small
response TO THE DETERRENT; it is a small deterrent. The stylized model applies a
deterrent nearly nine times larger and gets a collapse to zero.

SO THE EXTERNALITY IS NOT SMALL BECAUSE PARENTS DO NOT CARE. It is small because
the model routes the harm through a channel that is discounted by four and
damped by two before it reaches the choice.

## The question this raises, for the author to answer

The channel transmits the parent's state AT THE INSTANT OF DEATH. A parent who
uses from 25 to 60 and is clean at 75 transmits nothing to its child. The
empirical literature the penalty is calibrated from -- Nilsson (2017) for
`DEL_D`, McGovern et al. (2023) for the disorder ratio -- measures the harm of
EXPOSURE DURING CHILDHOOD, which is a stock the parent accumulates while alive,
not a state read off at death.

Nothing has been built. Three options, and the choice is the author's:

1. LEAVE IT. The death-contingent form is the canonical dynastic one and it was
   settled deliberately; the finding is then that the externality is genuinely
   small in this model and Housing First's win survives.
2. RAISE omega_c. Reproducing the stylized deterrent needs omega_c near 9, which
   is inside `weight_on_child_cap = 25`. It is a defensible sensitivity but it
   is no longer "the weight on the child" in any interpretable sense.
3. CHANGE THE KEYING to accumulated exposure rather than the state at death.
   This is a model change and a large one.

## Reproduction

`scratchpad/omega_deterrent.py` (in the repo). `DeltaV_child` is read from the
`expected_child_value=` print in `code/variant_cf_20260910T161710Z.log`, which
is the near-benchmark run (b 0.0861, lambda_d 0.0370, h_1 0.0132); the survival
schedule is `actual_survival_probability` in the Fortran source; the newborn
lifetime value 2195.0 is that run's `average_welfare_of_youngest_cohort`, which
carries the 0.4 per cent inflation documented in `CEV_AUDIT.md` and is immaterial
at this precision.

## AND THE OTHER HALF OF THE ANSWER, measured the same hour

`arm0_utf_nofp` returned while this was being written. It is universal Treatment
First at omega_c = 0 with the false positive rate set to zero and detection left
at 0.9, so imperfect testing still lets a tenth of users through.

    universal Housing First,  omega_c = 0                    +29.973%
    universal Treatment First, omega_c = 0, p_fp = 0.005     +22.186%
    universal Treatment First, omega_c = 0, p_fp = 0         +30.770%

A HALF PER CENT FALSE POSITIVE RATE COSTS 8.58 CEV POINTS, which is more than
the whole 7.79 point gap between the two policies. With perfect testing
Treatment First WINS, by 0.80 points.

The magnitude is large but it is not a puzzle. It compounds: 0.005 per year is
1 - 0.995^40 = 18.2 per cent over a forty year working life and 26.0 per cent
over the full sixty period life, so a newborn behind the veil faces something
between a one in five and a one in four chance of being wrongly stripped of a
voucher at some point. And being stripped is not a one period event:
`voucher_exclusion_release = 1/3` bars the household for three years in
expectation and then returns it to the BACK OF THE QUEUE, not to the voucher.

## Putting the two together

The stylized model made Treatment First win by a wide margin. The quantitative
model reverses it, and the reversal is now fully accounted for by two channels,
neither of which the stylized model has:

    the externality Treatment First buys is 8.7x weaker    (this file, above)
    the false positive risk it carries costs 8.58 points   (absent entirely
                                                            from the stylized
                                                            model)

Remove the second and Treatment First wins even at omega_c = 0, where the
externality is at its maximum and the case for conditionality is at its
strongest in the bound the author asked for. So the ranking in this model is
NOT a statement about drug utility. It is a statement about TESTING, and it says
the policy comparison turns on enforcement accuracy rather than on how much the
externality is worth.

## IS 0.5 PER CENT A REASONABLE FALSE POSITIVE RATE?

The author asked, 10 September, and it is the right question to ask of a
parameter that has just turned out to carry 8.58 CEV points.

### Where the number came from

The author set it on 9 September, replacing 0.05, and the reasoning is in the
declaration: urine testing is two stage, an immunoassay screen then GC-MS or
LC-MS/MS confirmation, federal programmes require the confirmation before a
positive is reported, screens alone run false positives from the low single
digits to about ten per cent depending on the analyte, and confirmation drives
the reported rate well under one per cent. On that reading 0.005 IS REASONABLE
AND IF ANYTHING CONSERVATIVELY HIGH -- confirmed analytical false positives are
usually quoted below it.

### But the model's parameter is not analytical error

What `probability_of_false_positive` multiplies is the probability that a
household WHICH MEETS THE CONDITION loses the voucher anyway, and that has
routes a confirmatory assay never touches:

* a missed or refused test scored as a positive -- transport, work, illness,
  childcare -- which is plausibly the largest channel in a real programme and is
  not a test error at all;
* specimen mix-ups and chain of custody or clerical error, where confirmation
  correctly confirms the WRONG sample;
* a legitimate prescription with no Medical Review Officer step, which federal
  workplace testing has and public assistance programmes often do not;
* recertification and paperwork failures, to which a testing requirement adds a
  fresh occasion.

Read as a programme outcome rather than an assay statistic, 0.5 per cent per
year is more likely TOO LOW than too high. NO NUMBER IS ASSERTED HERE: the size
of those channels has not been pinned to a source and should be before anything
is claimed in print.

### Why it very nearly does not matter

Housing First does no testing, so its welfare is FLAT in this parameter. Treatment
First is not, and the two measured points bracket the crossing:

    p_fp = 0.000    universal TF  +30.770%     TF ahead by 0.797
    p_fp = 0.005    universal TF  +22.186%     TF behind by 7.787
    Housing First   +29.973%, at every p_fp

    chord slope        -1716.8 CEV points per unit p_fp
    CROSSING           p_fp = 0.000464, i.e. 0.046 per cent per year,
                       about ONE IN TWO THOUSAND

The crossing sits 9.3 per cent of the way along a chord between two measured
points, so it is an INTERPOLATION, not an extrapolation. And the curve is
strongly concave -- the older vintage's slope over [0.005, 0.05] is -657.6
against -1716.8 here -- so the true crossing is if anything BELOW the linear one.

SO TREATMENT FIRST WINS ONLY IF WRONGFUL EXCLUSION IS HELD BELOW ROUGHLY ONE IN
TWO THOUSAND PER YEAR, which is an order of magnitude tighter than the author's
already conservative calibration and tighter than any real programme plausibly
achieves. The interesting object for the paper is therefore the THRESHOLD, not a
point value: the ranking is a statement about enforcement accuracy, and the
threshold is small enough that the answer is robust to the whole plausible range
of the parameter.

### The one solve that would settle it

An arm at `probability_of_false_positive = 0.0005` -- just above the implied
crossing -- would confirm the threshold directly rather than by interpolation.
Not run, and not queued without the author, because it is an experiment rather
than a fix.

## "What about two false positives? Maybe the government can do two tests?"

The author, 10 September. The arithmetic is below, but the first thing to say is
that THE SECOND TEST IS ALREADY SPENT.

### 0.005 is already the two-test number

Urine testing is two stage and the calibration already reflects it: the
immunoassay screen is the 0.05 that was in the file before 9 September, and
GC-MS or LC-MS/MS confirmation is what took it to 0.005. So "run a second test"
is not an unused lever; it is the lever that has already been pulled, and the
question is what a THIRD stage would add.

### If a third stage were independent, Treatment First wins

    p^2 = 2.50e-05   ->  universal TF ~ 30.727%   against HF 29.973%
                         TF ahead by 0.754, and 19x below the crossing

### But the residual is exactly the part that is NOT independent

Confirmation has already removed the random analytical error. What survives it
is systematic, and systematic errors RECUR ON A RETEST:

* a legitimate prescription produces a TRUE analytical positive every time, and
  only a Medical Review Officer step catches it, not another assay;
* chronic cross-reactivity from a daily medication recurs by construction;
* a household that missed the first appointment for want of transport, or
  because its shift could not be moved, is disproportionately likely to miss the
  second -- and a missed test scored as a positive is not a test error at all;
* specimen mix-up is the one channel a genuinely fresh draw does catch.

Let rho be the share of residual false positives that are systematic. Then two
tests give p_2 = p (rho + (1 - rho) p), and

       rho        p_2         TF        vs HF
      0.00%    2.50e-05    30.727%     +0.754
      5.00%    2.74e-04    30.300%     +0.327
      8.83%    4.64e-04    29.974%     +0.001   <- BREAK EVEN
     10.00%    5.23e-04    29.873%     -0.100
     25.00%    1.27e-03    28.592%     -1.381
    100.00%    5.00e-03    22.186%     -7.787

IF MORE THAN ABOUT NINE PER CENT OF THE RESIDUAL FALSE POSITIVES RECUR ON A
RETEST, TWO TESTS STILL LEAVE HOUSING FIRST AHEAD. rho is not measured here and
no value is asserted; the break-even is the object, and it is low.

### And testing twice cuts deterrence, unless it is done the right way

If exclusion requires BOTH tests positive, a user escapes when either misses:
detection goes from 0.95 to 0.9025, a five per cent loss of deterrence, which
pushes the other way. The design that avoids it is to RETEST ONLY THE POSITIVES
-- which is, again, exactly what the confirmatory stage already is.

So the lever that would actually move rho is not a further assay. It is a
Medical Review Officer step and an appeals process, because those are what
address prescriptions and missed appointments, and those are the channels
another test cannot see.

### One caveat, and it runs against Treatment First

Every TF figure in this section is a LINEAR reading of a chord that is strongly
concave near zero, so the true values are if anything lower and the break-even
rho lower still.

## THE ALEPH CORRECTION, and it answers both of the author's questions at once

The author, 10 September: *"I just don't see why the fp is so large in its
effect. And I also don't understand why the omega_c effect even at 1 is so
small"*. Both are the same fact about the value function, measured below.

### What the value function is actually made of

`flow_utility_1 = flow_utility_goods_only + value_of_life`, the goods term is
CRRA at sigma = 2, and `value_of_life` -- aleph -- is 177.77, added EVERY period.
The model's own diagnostics give the scale:

    aleph                                       177.77
    average period of life, non-users           161.11    -> u_goods = -16.66
    worst cell, Treatment First                  10.39    -> u_goods = -167.38
    worst cell, universal Housing First          73.62    -> u_goods = -104.15
    share with a NEGATIVE value of life           0.0000  -- the pathology the
                                                             declaration warns
                                                             about does NOT fire

So CONSUMPTION IS ONLY 9.4 PER CENT OF THE VALUE OF A PERIOD OF LIFE, and
marginal utility at the worst cell is TEN TIMES the average, because at sigma = 2
u_goods = -1/c is unbounded below.

### Why the false positives cost so much: sigma = 2 at the bottom

The consumption-equivalent metric divides by dV/dx = 98.3 utils per unit, so one
util is 1.02 per cent of lifetime consumption. That leverage is not special to
the false positives -- the whole universal programme is 43.3 utils, and it reads
as 44 per cent on the same scale -- so it inflates every welfare number equally
and CANCELS in a Housing First against Treatment First comparison. It is not the
explanation, it is only the reason the headline reads 8.58 rather than 0.385 per
cent of lifetime UTILITY.

The explanation is the tail. The earlier risk-neutral envelope, 0.63 to 1.58
utils, valued the lost voucher-years at the AVERAGE. At sigma = 2 the loss lands
on households whose marginal utility is up to ten times the mean, which puts the
envelope at 6.3 to 15.9 utils. THE MEASURED 8.44 SITS INSIDE THAT BRACKET. The
cost is not the expected loss; it is the expected loss weighted by a marginal
utility that explodes at the bottom, and wrongful exclusion is precisely the
event that sends a household there.

### Why omega_c = 1 is weak: the timing, and ONLY the timing

FACTOR ONE ABOVE IS WITHDRAWN. It divided the child's loss by V, and V is nine
tenths aleph. On the denominator a behavioural comparison can actually use:

    quantitative   104.2 utils / 98.3 = 106.0 per cent of lifetime consumption
    stylized       per_case            =  50.86 per cent

THE QUANTITATIVE MODEL'S CHILD PENALTY IS TWICE THE STYLIZED MODEL'S, NOT HALF.
The insurance story told above for why it might be smaller is not needed and is
not supported. What remains is the death-contingent weight alone:

    quantitative deterrent, omega_c = 1   106.0% x W_SUD 0.2333 = 24.7%
    stylized deterrent,     omega   = 1    50.86% x 1.0         = 50.86%
    RATIO                                                          2.06

not the 8.7 reported earlier. So the ONE structural difference between the two
models is that the quantitative parent collects the child's loss only when it
dies, and that is worth a factor of four; the child's loss itself is twice as
big here, which claws half of it back.

### Which leaves a real question, sharper than before

A deterrent worth a quarter of lifetime consumption moves drug use by only 20
per cent. The only direct evidence on what it is up against is the same
diagnostic: under Housing First a drug user's period of life is worth 165.48
against 161.26 for everyone else, a surplus of 4.22 utils per period, or roughly
55 utils over a discounted life, against a deterrent of 24 utils. That is the
right order to explain a partial response. IT IS CROSS-SECTIONAL AND THEREFORE
SELECTION, NOT A TREATMENT EFFECT, and it is offered as a scale check and
nothing more.

## THE DECOMPOSITION, closed with measured terms

`arm0_utf_nochild` returned +22.262 per cent, which is the term that lets the
account close on measurement rather than on a residual assumption.

    MEASURED, universal, omega_c = 0
      Housing First                       29.973%
      HF, no child penalty                36.826%   -> externality under HF  +6.852
      Treatment First                     22.186%
      TF, no child penalty                22.262%   -> externality under TF  +0.076
      TF, no false positives              30.770%   -> false positives       -8.584
      TF, no treatment cost               21.526%   -> treatment cost        +0.659

THE EXTERNALITY UNDER TREATMENT FIRST IS 0.076 POINTS, essentially zero, which is
what it has to be: its disorder rate is 0.03 per cent, so there is almost no
child harm left for the counterfactual to remove. That confirms the earlier
derivation rather than assuming it.

    THE ACCOUNT, Treatment First against Housing First
      externality Treatment First removes      +6.776
      drug utility and everything else         -5.979   (the only derived term)
      --------------------------------------------------
      net at perfect testing                   +0.797   = TF(no fp) - HF
      false positives                          -8.584
      --------------------------------------------------
      TOTAL                                    -7.788   = TF - HF

THE TWO LARGE TERMS VERY NEARLY CANCEL. Treatment First buys back 6.776 points of
externality and pays 5.979 for it in drug utility, netting +0.797. The false
positives, at 1.27 times the externality they buy back, are what turn that into
a 7.788 point loss.

So false positives are DECISIVE WITHOUT BEING DOMINANT. An earlier note in this
file said the ranking is a statement about testing accuracy rather than about the
size of the externality. THAT IS WITHDRAWN: the three terms are 8.584, 6.852 and
5.979, all the same order, and the result is a near cancellation broken by the
smallest well understood of them.

Which is also why the ranking is fragile in three directions at once. Raise
omega_c, or re-key the child transmission off the instant of death, and the
externality term grows. Value drug utility less and the second term shrinks.
Lower the false positive rate and the third shrinks. Any one of them flips it.

## CORRECTION: the omega_c response is 16.69 per cent, not 20.04

The author, 10 September: *"it might be that you analyzed the data wrong for the
change in drug use of parents? Maybe it is a smaller difference and you made a
mistake in the computations?"*

THEY ARE RIGHT. Re-derived from the logs, taking only POST-FROZEN prints and only
runs that report `FROZEN CONVERGED`:

    omega_c = 0      b = 0.087845639  and  0.087846607   two runs, agreeing to 6 digits
    omega_c = 0.17   b = 0.085920614
    omega_c = 1.0    b = 0.073181764
    omega_c = 0.6    EXCLUDED -- FROZEN CONVERGED = 0, its only print is pre-frozen

    omega_c = 0.17   fall from the omega_c = 0 base   2.192%   (I said 2.24)
    omega_c = 1.0    fall from the omega_c = 0 base  16.694%   (I said 20.04)

The error was the DENOMINATOR: I divided the difference by the omega_c level
instead of by the omega_c = 0 base, which measures the RISE from internalised to
not, not the FALL the sentence claimed. Every earlier statement of "20 per cent"
in this file and in chat is wrong by that amount and is corrected here.

## AND THE PUZZLE DISSOLVES THE OTHER WAY: the stylized model is the degenerate one

Sweeping omega finely in the stylized model, with `b` held, shows its response is
not strong -- it is SATURATED almost immediately:

    UNIVERSAL pi_V = 1.0            RATIONED pi_V = 0.266
      omega   use      fall           omega   use      fall
       0.00   7.1076%    0.0%          0.00   8.9010%    0.0%
       0.05   1.6615%   76.6%          0.05   5.2914%   40.6%
       0.10   1.6475%   76.8%          0.10   4.1824%   53.0%
       0.20   1.0191%   85.7%          0.20   3.1744%   64.3%
       0.25   0.0154%   99.8%          0.30   0.8794%   90.1%
       0.30   0.0000%  100.0%          0.50   0.0000%  100.0%
       1.00   0.0000%  100.0%          1.00   0.0000%  100.0%

AT UNIVERSAL COVER A WEIGHT OF 0.05 ALREADY REMOVES THREE QUARTERS OF DRUG USE,
and everything from 0.30 up is a flat corner. The flat steps in between -- 1.6615
to 1.6475 to 1.6399 across omega 0.05 to 0.15 -- are the means test notch: a
discrete margin, not a distribution being eaten into.

So "100 per cent against 16.7 per cent" is not a strong response against a weak
one. It is a CORNER, reached at omega around 0.3, against an INTERIOR response
that is still moving at omega = 1. The stylized model has one continuous choice
and essentially one margin, so a small deterrent flips nearly everyone at once.
The quantitative model has sixty periods, a productivity grid, assets, employment
and health states, so a deterrent moves the fraction of the distribution that
lies within it, and 16.7 per cent of users quitting when the child is fully
internalised is a SUBSTANTIAL interior response rather than a puzzle.

WHAT NEEDS EXPLAINING IS THEREFORE THE STYLIZED MODEL, not the quantitative one:
a deterrent one twentieth the size wipes out three quarters of use there. That is
the number to distrust.

## THE DECISIVE ARM: arm0_utf_lowfp at p_fp = 0.0005 returns +29.8176

Run because the 8.584 point false positive term rested on an interpolation across
[0, 0.005] in a region where the curve's slope is steeper than it is further out.
It was the test of whether the threshold framing survives. IT DOES, and it comes
out slightly tighter than the interpolation said.

    HF is FLAT in p_fp (it does no testing)      29.9734%
    p_fp = 0        universal TF   30.7701%      TF ahead by  +0.797
    p_fp = 0.0005   universal TF   29.8176%      TF behind by -0.156
    p_fp = 0.005    universal TF   22.1857%      TF behind by -7.788

    slope [0, 0.0005]        -1905.0 points per unit p_fp
    slope [0.0005, 0.005]    -1696.0     CONCAVE, steepest at zero, as predicted

    MEASURED CROSSING   p_fp = 0.000418 = 0.0418 per cent a year, about 1 in 2391

My interpolation predicted 29.9117 at this point against a measured 29.8176, an
error of 0.094 points and OPTIMISTIC FOR TREATMENT FIRST -- which is exactly the
sign concavity implies, so the curve is behaving as described rather than doing
something unexplained near zero. The earlier estimate of the crossing, 0.0464 per
cent, becomes 0.0418.

### What that means for the author's HIV question

Reading the accuracy off the measured slope near zero:

    p_fp = 4e-6    HIV-grade full algorithm, order 1 in 250,000   TF +0.789
    p_fp = 1e-4    1 in 10,000                                    TF +0.606
    p_fp = 4.18e-4 THE CROSSING, 1 in 2,391                        dead heat
    p_fp = 5e-4    1 in 2,000                                     HF +0.156
    p_fp = 5e-3    the calibrated value                           HF +7.788

SO THE AUTHOR'S POINT CARRIES. If a confirmed programme can reach anything like
the specificity of the HIV testing algorithm, or even one wrongful exclusion in
ten thousand household-years, TREATMENT FIRST WINS. The requirement is stringent
but it is not absurd: better than one in roughly two thousand four hundred a
year.

That is the form the result should take in the paper. Not "Housing First wins",
and not a point value of `probability_of_false_positive`, but a THRESHOLD ON
ENFORCEMENT ACCURACY with the policy ranking on either side of it -- because the
calibrated 0.005 is itself a round conservative stand-in rather than a measured
post-confirmation rate, and the answer moves either side of 1 in 2,400.

STILL UNRESOLVED, and it should not be forgotten because the threshold is now
sharp: `probability_of_false_positive` in this model is not assay error. It is
the chance a COMPLIANT household loses the voucher, which includes a missed
appointment scored as a positive. No improvement in the assay touches that
channel, and nothing here has pinned its size.

## WHY omega HAS TO BE NEAR ONE HERE AND NEAR 0.05 THERE

The author, 10 September: *"we need to understand why omega needs to be so high
in the quant model and not in the stylized model? Did you try to compute the data
again to make sure it is correct?"*

### First, the re-computation they asked for

Re-derived from the raw `OMEGA_DIAG` counts in the logs rather than from any
earlier summary. The moment is (users with the child term off) / (users with it
on) - 1, at the same omega_c:

    omega_c = 0     on 0.087846607   off 0.087862326   ->  0.000179
    omega_c = 0.17  on 0.085920614   off 0.087660630   ->  0.020251
    omega_c = 1.0   on 0.073181764   off 0.085833231   ->  0.172877
    target                                                 0.183432
    linear in omega_c, the target needs                    omega_c = 1.057

TWO INDEPENDENT COMPUTATIONS AGREE. The internal moment is a PARTIAL equilibrium
object, 17.29 per cent at omega_c = 1; the ladder across fully re-solved
equilibria gives 16.69 per cent. They differ only by the general equilibrium
terms and land within 0.6 points of each other, which is the cross-check that
matters.

### And the answer: THE DETERRENTS ARE THE SAME SIZE, THE MARGINS ARE NOT

Putting both models on the one comparable scale, the deterrent as a share of
lifetime consumption, against the fall in drug use it produces:

          model    omega    deterrent    fall in use
          quant     0.17        4.20%          2.19%
          quant     1.00       24.73%         16.69%
       stylized     0.05        2.72%         40.55%
       stylized     0.10        5.43%         53.01%
       stylized     0.20       10.87%         64.34%
       stylized     0.30       16.30%         90.12%

AT A DETERRENT NEAR FOUR OR FIVE PER CENT OF LIFETIME CONSUMPTION THE STYLIZED
MODEL REMOVES ABOUT HALF OF ALL DRUG USE AND THE QUANTITATIVE MODEL REMOVES 2.2
PER CENT. That is a factor of about twenty, and it is NOT a difference in how
much the parent is made to care -- the two deterrents are the same size in the
same units. It is the elasticity of the drug-use margin.

So omega_c does not have to be near one here because the child is worth little.
At omega_c = 1.057 the deterrent is a QUARTER OF LIFETIME CONSUMPTION, which is
enormous. It has to be near one because the distribution of the gap between using
and not using is WIDE in a model with sixty periods, a productivity grid, assets,
employment and health states, so a deterrent moves only the households lying
within it. In the stylized model that distribution is close to a point mass: two
periods, one continuous choice, one margin, so almost everyone crosses at once
and the response saturates by omega = 0.3.

### What has NOT been measured, and what would settle it

The dispersion of V(use) - V(do not use) across the state space is INFERRED here
from the response, not measured. A diagnostic that accumulates that gap over the
distribution at the benchmark would give it directly, and would say whether the
implied density near indifference is what the response requires. It is a small
addition to the Fortran and cannot go in while a solve is running.

## THE 18 PER CENT TARGET, RE-DERIVED FROM THE MICRODATA

The author, 10 September: *"I also want you to double check whether the 18%
change in use is correct from the data... Maybe your data point is wrong"*.

`data/make_altruism_moment.py` was re-run against the full NSDUH 2024 public use
file, 390 MB, not against any summary. IT REPRODUCES EXACTLY:

    past month illicit use, ages 26+, weighted
      raw          with a child 16.34%   without 16.63%   ratio 0.983
      reweighted   with a child 14.11%   without 16.71%   ratio 0.845
      implied rise with altruism off                      18.4%
      234 cells, 97.2% of non parent weight

So the number is right and the conversion is right: the model's moment is
(users with the term off)/(users with it on) - 1, based on use WITH the term on,
and 1/0.845 - 1 = 0.1834 is the same gap on the same base. That denominator was
already caught and fixed once in the declaration, and it is the mirror image of
the error I made in the ladder.

### But three things the re-run makes visible

**THE RAW GAP IS NOTHING: 0.983.** All of the moment is created by the
reweighting. That is legitimate rather than artefactual -- it is Simpson's
paradox, and every within-age-band ratio is far below the pooled one -- but the
moment is entirely a composition-adjusted object, and it inherits whatever the
adjustment gets wrong.

**THE WINDOW MATTERS AS MUCH AS THE ADJUSTMENT.** Past year gives 0.809 and a
23.6 per cent rise, not 18.4. There is no stated reason in the file for
preferring past month.

    reading                          ratio   target   implied omega_c
    past month, reweighted           0.845   0.1834       1.057
    past year, reweighted            0.809   0.2361       1.344
    past month, RAW                  0.983   0.0177       0.156

**THE FILE'S OWN CREDIBILITY ARGUMENT DOES NOT SURVIVE ITS OWN TABLE.** It says
the age pattern makes the gap credible because it is widest in the child rearing
window and "narrows at 50 to 64 when children have left". The table:

      26-29  0.805     30-34  0.713     35-49  0.600
      50-64  0.855     65+    0.478

65+ IS THE WIDEST RATIO OF ALL, wider than 35 to 49, in the group where a
concern for a child's inherited productivity is least plausible and where the
children in the household are as likely to be grandchildren. The rates there are
small, 7.93 against 3.79 per cent, so the ratio is noisy. But the stated pattern
is not the pattern, and that weakens the case that the gap is altruism rather
than household structure.

### What this does to omega_c

The source file already says the measured gap is an UPPER BOUND, because heavy
users lose custody and so their children are absent from the household rather
than their use being lower. The model's channel is narrower still: it is only the
parent's valuation of a child's inherited productivity penalty, realised at the
parent's death, where a real parent's lower use also reflects custody risk,
supervision, a child in the house, and time and money constraints.

omega_c is close to PROPORTIONAL to whatever share of the gap is attributed to
the model's channel:

      share attributed    1.00    0.75    0.50    0.33    0.25    0.10
      implied omega_c     1.06    0.81    0.56    0.39    0.31    0.16

SO omega_c = 1.06 IS NOT A MEASUREMENT, it is the top of a range whose bottom is
zero, and the file itself prescribes the discipline: report omega_c across the
range with the threshold at which a conclusion changes. That has not been done
yet and it should be, because the false positive threshold is now sharp enough
that the two ranges have to be read together.

## THE MOMENT BY AGE SUBSET: it is not stable, and 65+ is not the problem

The author, 10 September: *"Maybe you are not looking at the right ages in the
computations?"* Recomputed on the microdata, past-month use, reweighting redone
WITHIN each subset:

    sample                           raw  reweighted    rise   omega_c  cells  cover
    26+   (the moment in use)      0.983       0.845   18.4%     1.060    234  97.2%
    26-64 (drop 65+)               0.787       0.859   16.4%     0.950    190  99.0%
    26-49 (child-rearing)          0.639       0.845   18.4%     1.061    138  99.8%
    26-34                          0.735       0.900   11.1%     0.662     84  99.7%
    35-49 alone                    0.600       0.792   26.3%     1.490     54  99.9%
    65+ alone                      0.478       0.771   29.7%     1.673     44  94.3%

**DROPPING 65+ BARELY MATTERS.** omega_c goes 1.060 to 0.950. The suspicion in
the section above -- that grandparents were contaminating the moment -- is mostly
WRONG, because that group carries little weight in the pooled figure. To the
extent the earlier note read the file's credibility argument against its own RAW
table, it should be softened: reweighted, 35-49 gives 0.792 and 65+ gives 0.771,
which are close, and the anomaly is much milder than the raw ratios suggested.

**WHAT DOES MATTER IS THAT THE MOMENT IS NOT STABLE.** Across sensible windows
the implied omega_c runs from 0.66 at 26-34 to 1.49 at 35-49, a factor of 2.3,
and 26-34 is the window where a young parent's concern for a child is most
plausible. There is no age range on which this moment settles down.

**AND THE REWEIGHTING PULLS IN OPPOSITE DIRECTIONS IN DIFFERENT SAMPLES.** Over
26+ the raw pooled gap is nothing, 0.983, and reweighting OPENS it to 0.845. Over
26-49 the raw gap is wide, 0.639, and reweighting NARROWS it to 0.845. So within
narrow age bands most of the parent against non-parent difference is income, sex
and marital composition, which the adjustment strips out; across the full age
range it is age composition, which the adjustment restores. The two effects
happen to land on the same 0.845, which is a coincidence of this sample rather
than a sign of robustness.

**THE ARGUABLY RIGHT SAMPLE FOR THIS MODEL IS 26-64**, since the model's
households choose over drugs through working life and
`max_age_to_choose_homelessness` is 58. That gives 0.859, a 16.4 per cent rise,
and omega_c = 0.950.

None of this changes the conclusion already recorded: omega_c is the top of a
range, not a point, and the range is now bracketed by the data itself at roughly
0.66 to 1.49 before any allowance for the selection the source file warns about
or for the narrowness of the model's channel, both of which push the honest
number DOWN from there.

## THE MOMENT IS COMPUTED ON A DIFFERENT POPULATION FROM THE ONE b MEASURES

The author, 10 September: *"When you consider use I think you should remove those
with Sud... They are addicted already."* Following that leads somewhere larger
than the suggestion.

### First, the suggestion as put: it widens the gap

    sample                                     raw   rewtd    rise   omega_c
    26+   ALL (the moment in use)            0.983   0.845   18.4%     1.060
    26+   EXCLUDING any drug use disorder    0.972   0.819   22.0%     1.258
    26-64 ALL                                0.787   0.859   16.4%     0.950
    26-64 EXCLUDING any drug use disorder    0.811   0.823   21.6%     1.232

Removing the already-dependent RAISES omega_c, because among people with a
disorder parents and non-parents use at similar rates -- they cannot respond,
exactly as the author's reasoning says -- so including them pulls the ratio
toward one. The mechanism is the one described; it just runs the other way.

### But the model has no non-disordered users at all

Verified against the extract, ages 26 and over, weighted:

    svyrdudany in (1,2,3)  ANY disorder incl. mild   0.0890  = participation_rate_data
    svyrdudany in (2,3)    MODERATE or SEVERE        0.0368  = sud_rate_data
    svyrdudany == 3        SEVERE only               0.0170

BOTH TARGETS REPRODUCE EXACTLY. So `b` IS the any-disorder population and
`lambda_d` is the moderate-or-severe subset of it. In this model "uses" and "has
at least a mild disorder" are THE SAME EVENT, and there is no non-disordered user
to remove.

That also means the note's own description of `b` -- "the share who use at all,
with or without a SUD" -- does not match its target. The share who use at all is
16.5 per cent past month and 24.5 past year; 8.90 per cent is the share with a
disorder.

### So the altruism moment is on the wrong variable, and it matters by a factor of six

The model's moment is a proportional change in `model_total_drug_users`, which
targets 0.0890. Its empirical counterpart is the parent against non-parent gap in
THAT variable, not in past-month use:

    outcome                                       level    raw   rewtd    rise  omega_c
    ILLMON past-month use (the moment in use)    0.1654  0.983   0.845   18.4%    1.060
    ANYSUD  = what b is calibrated to            0.0890  0.944   0.978    2.2%    0.181
    MODSEV  = what lambda_d targets              0.0368  0.918   0.843   18.6%    1.071
    ANYSUD, ages 26-64                           0.1076  0.723   0.909   10.0%    0.605

PUT THE MOMENT ON THE POPULATION THE MODEL ACTUALLY MEASURES AND omega_c FALLS
FROM 1.06 TO 0.18.

### The caveat, and it is a real one

The answer is not robust across cuts of the same variable: moderate or severe
alone gives 0.843 and omega_c = 1.07, almost exactly what past-month use gives.
Any-disorder nets two offsetting components -- backing them out, parents are
about 7 per cent MORE likely to carry a mild-only disorder and 16 per cent less
likely to carry a moderate or severe one. Whether the model's user is the mild
group, the severe group or both is a modelling question, not a data one, and it
is the author's to settle. What is not in doubt is that the moment currently in
use is computed on a population three times larger than the one `b` measures.

### A side finding in the declaration

`sud_rate_data`'s comment says the right value is 0.0454 and that 0.0368
"matched no cut of that variable", and `AUDIT_A_declarations.md` repeats it. BOTH
ARE WRONG. 0.0368 is exactly `svyrdudany in (2,3)` at ages 26 and over; 0.0443 is
the same cut at ALL ages, which is presumably where 0.0454 came from. The
declaration is right and its comment is wrong.
