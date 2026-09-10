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

    RATIO                                    9.69 / 1.11 = 8.7

## Factor one: the child's loss is half the size, 4.75 against 9.69

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

The magnitude is large but it is not a puzzle: 0.005 per period compounds over a
sixty period life to 1 - 0.995^60 = 26.0 per cent, so a newborn behind the veil
faces roughly a one in four chance of being wrongly stripped of a voucher at
some point, and `include_voucher_exclusion = 1` means being stripped is not a
one period event.

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
