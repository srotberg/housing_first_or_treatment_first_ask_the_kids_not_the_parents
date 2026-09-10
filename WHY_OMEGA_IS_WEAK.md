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
