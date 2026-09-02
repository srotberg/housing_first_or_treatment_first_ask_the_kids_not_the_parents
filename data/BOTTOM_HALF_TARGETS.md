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
