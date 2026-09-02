# Bottom-50%-by-wealth targets, computed from SCF 2022

For the author's restructuring: drop the patient type, model only the bottom half
of the wealth distribution, and re-target every moment to that subpopulation.
Computed from `data/SCF_2022.dta` with `wgt`, households ranked by `networth`,
cut at the weighted 50th percentile.

## What came out

| quantity | bottom 50% by WEALTH | bottom 50% by INCOME |
|---|---:|---:|
| share of all income | **0.2006** | 0.1319 |
| share of all net worth | 0.0220 | 0.1083 |
| **net worth / their own income** | **0.8216** | 6.1526 |
| **housing cost / their own income** | **0.2051** | 0.2299 |
| share spending >50% of income on housing | **0.1307** | -- |
| the same, renters only | 0.1919 | -- |

Both cuts are given because they are DIFFERENT POPULATIONS and the model already
contains a moment defined on the second one. `sigma_y` is the bottom half by
EARNINGS at 0.172; the design here is the bottom half by WEALTH at 0.2006. Using
one where the other belongs is a five per cent error in every income-normalised
target.

## The three replacements the author asked for

- **`beta` becomes net worth over the bottom half's own income: 0.8216.** The old
  target, wealth over GDP at 3.0, is meaningless once the top half is gone.
- **`gamma` becomes housing cost over the bottom half's own income: 0.2051.**
- **`w_bot` disappears.** It was the bottom half's share of total net wealth and
  is 1.0 by construction here. Worth recording that the SCF puts it at 0.0220
  against the model's standing target of 0.0250 -- an independent check that the
  old target was about right.

## The scaling rule for everything else

    headcount shares of population        x 2
    normalised by income                  / 0.2006, i.e. x 4.99
    conditional on homeless/addicted/SUD  unchanged

So homelessness 0.00399 -> 0.00798, and food stamps `cbar` 0.0042 -> **0.0209**.
NOT x2 for the second class: the bottom half earns a fifth of income, not a half.

## TWO THINGS THAT ARE NOT SETTLED

**The income tax is NOT in this file.** The SCF summary extract has 357 columns
and none of them is a tax measure. `tau_l`'s current 0.224 came from elsewhere,
and the bottom half's average rate has to come from that same source rather than
from here -- CBO average federal tax rates by quintile is the usual one, and it
matters that the bottom two quintiles are near zero or negative once refundable
credits are counted. Computing it from the model's own tax function applied to
the bottom half is possible but produces an OUTPUT, not an independent target.

**The housing-cost definition here is not the one behind `h_2`=0.101.** That
number is CEX severe cost burden. This is SCF, and housing cost here is
12*rent for renters plus 12*mortpay for owners -- no property tax, insurance or
utilities, and a payment rather than a user cost. The whole-population version of
the SCF measure is 0.0783 against the CEX 0.101, so the two are NOT
interchangeable. Either recompute the bottom-half burden in CEX, or change the
source deliberately and say so.

## The author's design decisions, 18:45

- **The rental market does not have to clear.** Rent is held at its benchmark;
  the bottom-half economy is partial equilibrium in housing.
- **The government budget is unchanged.** It funds half the economy as it stands.
- **The income distribution is tuned to the bottom half**, not inherited whole.
- **The unemployment rate is tuned to the bottom half** as well.

## The income distribution, and what identifies the productivity spread now

| | whole population | bottom 50% by wealth |
|---|---:|---:|
| mean income | 141,390 | 56,724 |
| **sd(log income)** | 1.0350 | **0.8112** |
| p10 / p50 / p90 | 20,537 / 70,259 / 248,610 | 15,133 / 44,317 / 113,496 |
| p90/p10 | 12.11 | 7.50 |

    bottom-half mean income / whole-population mean   0.4012
    bottom-half sd(log income) / whole-population sd  0.7837

`sd_permanent_productivity` currently targets `sigma_y`, the bottom half's share
of earnings -- which is meaningless once the model IS the bottom half. **Its new
target is the within-bottom-half income spread, sd(log income) = 0.8112.** State
it that way rather than as a parameter value: mechanically rescaling 0.9651185 by
0.7837 gives 0.7564, but that assumes the map from productivity dispersion to
income dispersion is linear and that unemployment, hours and transfers contribute
dispersion in the same proportion. The moment is the target; 0.7564 is only a
starting guess for the search.

## The unemployment rate

    SCF, whole population, lf==1 & occat1==4     0.0375
    SCF, bottom 50% by wealth                    0.0523
    ratio                                        1.3947

**The bottom-half target is 0.0683, not 0.0523.** The SCF's own whole-economy
rate is 3.75 per cent against the 4.9 the model targets, so taking the level
straight from the SCF would silently swap the source underneath the calibration.
Take only the RELATIVITY from the SCF and apply it to the official 4.9:
0.049 x 1.3947 = 0.0683.

## The income tax: the SCF cannot give it, and after-tax income is not in here

Asked directly whether the survey reports before- and after-tax income. It does
not, at least not in this extract. Every income column is a PRE-TAX component:

    income  wageinc  bussefarminc  intdivinc  kginc  ssretinc
    transfothinc  norminc  equitinc

There is no net-of-tax measure and no tax paid. So the bottom half's average
income tax rate has to come from wherever `tau_l`'s 0.224 came from -- CBO
average federal tax rates by quintile being the usual source, where the bottom
two quintiles are near zero or negative once refundable credits count. That
matters a lot here: a bottom-half economy taxed at 0.224 would be paying a rate
its own data says it does not.

## The income tax, computed from the model's own schedule

The SCF cannot give it directly, so the next best thing: apply the MODEL'S tax
function to the SCF income distributions and take the relativity.

The schedule is Heathcote-Storesletten-Violante, `T(y) = y - lambda*y^tau`, with
`lambda`=0.7522432 and `tau`=0.85, and BOTH the personal exemption and the
standard deduction are zero in this calibration, so there is nothing else in it.

    average rate, whole population (SCF income distribution)   0.3317
    average rate, bottom 50% by wealth                         0.1691
    ratio                                                      0.5098

    model's standing tau_l target                              0.2240
    BOTTOM-HALF TARGET, scaled by that ratio                   0.1142

**THE PROPORTIONAL SCALING THE AUTHOR SUGGESTED IS TOO LOW.** 0.224 x 0.4012 =
0.0899 assumes a flat tax. The schedule is progressive -- tau=0.85 is below one
-- so an average rate falls with income LESS than proportionally: a household at
40 per cent of mean income pays about 51 per cent of the mean household's
average rate, not 40. The right number is 0.1142, a quarter higher than the
naive one.

Only the RATIO is taken from this calculation, for the same reason as with
unemployment: the level the SCF distribution implies under this schedule, 0.3317,
does not agree with the model's 0.224 target, because the model's units and the
survey's are not the same object. Taking the level would silently swap the
source; taking the relativity does not.

## CORRECTION, 19:00: both of the derived numbers above were wrong

The author asked how each was computed. Showing the working broke both.

### The tax: 0.1142 was more than double the right answer. It is 0.0546.

`sd` and the tax were both derived by "take the ratio from the SCF and apply it
to the model's standing target". For the tax THAT METHOD IS NOT SOUND, because
the schedule is nonlinear and the ratio is not invariant to how income is
normalised. Varying the normalisation:

    scale        whole   bottom   ratio    implied target
    0.25x mean   0.4568  0.3231   0.7075   0.1585
    0.50x mean   0.3973  0.2492   0.6273   0.1405
    1.00x mean   0.3317  0.1691   0.5098   0.1142   <- what was reported
    2.00x mean   0.2614  0.0900   0.3443   0.0771
    4.00x mean   0.1919  0.0301   0.1568   0.0351

The reported 0.1142 was an artefact of normalising by mean income, a choice made
without justification.

THE PRINCIPLED NORMALISATION is the one under which the model's OWN whole-economy
target holds. Solving for it: **scale = 2.886 x mean income**, at which the
whole-population rate is 0.2240 by construction and

    BOTTOM-HALF AVERAGE INCOME TAX RATE = 0.0546

AND THE AUTHOR'S PROPORTIONAL SCALING WAS CLOSER THAN THE "CORRECTION" TO IT.
0.224 x 0.4012 = 0.0899 was called a quarter too low; it is in fact too HIGH,
against 0.0546. The reason is that `T(y)=y-lambda*y^tau` with lambda=0.75 has a
ZERO-TAX REGION at low income -- `max(y-lambda*y^tau, 0)` binds -- so at the
bottom the schedule is far more progressive than any proportional rule, not less.

### sd(log income): 0.8112 was the wrong variable. Use 0.8791.

`sd_permanent_productivity` governs the dispersion of PRODUCTIVITY, so the
sample should be earners, and the variable should be earnings:

    variable   sample                         whole    bottom 50%
    income     all households, y>0            1.0350   0.8112   <- reported
    wageinc    positive earnings, age<65      1.0445   0.8791   <- correct

`income` is total household income and includes capital income and transfers,
which are not productivity, and it retains retirees who have no productivity draw
in the model at all. The earnings restriction keeps 68 per cent of the bottom
half's weight.

**Revised targets: tau_l 0.0546, sd(log earnings) 0.8791.**

## Applying the tax function to the average income: it returns exactly zero

The author's suggestion -- take the bottom half's average income and put it
through the tax function -- is worth doing, and what it returns is the finding.

The schedule `T(y) = max(y - lambda*y^tau, 0)` has a ZERO-TAX THRESHOLD where
`y - lambda*y^tau = 0`, that is `y* = lambda^(1/(1-tau))`:

    y* = 0.7522432^(1/0.15) = 0.149872 in model units
       = 0.4325 of whole-population mean income

    whole-population mean income   0.3465 = 2.312 x y*
    bottom-half mean income        0.1390 = 0.927 x y*   BELOW THE THRESHOLD

So T(ybar_bot)/ybar_bot = **0.0000 exactly**. The average household in the bottom
half of the wealth distribution pays no labour income tax at all under this
schedule, and the bottom half's aggregate rate of 0.0546 is paid ENTIRELY BY ITS
UPPER TAIL.

WHICH NUMBER IS THE TARGET. `tau_l` is defined in the model at line 14196 as
`govt_revenues_from_labour_income / (model_total_efficiency_units + financial
income)` -- an AGGREGATE, revenue over income, not a rate evaluated at a mean.
So the target is **0.0546**, the aggregate. The rate-at-the-mean is the wrong
object for it, and the gap between the two is large even for the whole
population: 0.1181 at the mean against 0.2240 in aggregate.

THE ECONOMIC POINT IS WORTH KEEPING. A bottom-half economy is one where the
representative household is just below the income-tax threshold. That is a
substantive feature of the population being modelled, not an artefact, and it is
worth a sentence in the paper: the fiscal burden of these households is
essentially all consumption tax and payroll, not income tax.
