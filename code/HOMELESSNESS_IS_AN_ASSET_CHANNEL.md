# The model makes you homeless when you have no CASH, not when you have no INCOME

Diagnosed 2 September from point 39f903d92e, prompted by the author asking
whether h_2 is too small and h_1 too large to weed out the employed. Both are
right, and the diagnostics say something sharper.

## The homeless are too rich AND too employed

    income of the homeless        model 0.29340   observed 0.19100   +54%
    employed share of the homeless model 0.95471  observed 0.46000  +108%

Two independent readings of the same fault: the households the model makes
homeless are not poor.

## Nobody in the cheapest unit is cost-burdened

    unit 0 (cheapest)  41.8% of renters   0.0% paying over half their income
    unit 1             10.2% of renters   0.0% paying over half their income
    unit 2 (largest)   47.9% of renters  29.8% paying over half their income

At `smallest_rental_relative_to_lowest_income=0.039` the bottom rung is trivially
affordable to anyone with a job, so NO EMPLOYED HOUSEHOLD IS EVER PRICED OUT OF
HOUSING. That is the author's h_2 point, measured: the rung cannot select the
homeless on income because it never binds.

## So homelessness runs through ASSETS, and the age profile proves it

    age 26   5.45%      age 71   4.78%
    age 27   4.02%      age 72   4.82%
    age 28   1.06%      age 74   4.67%
    age 29-34 ~0.05%    age 80   6.02%   <- the single most homeless age

BIMODAL, and the two spikes are exactly the two moments a household holds no
assets: age 26, where `newborn_endowment_scale=0` hands everyone precisely zero
and the DIAG confirms `renter wealth = 0.00000`; and the late seventies, where
assets have been run down. In between, when households hold any buffer at all,
homelessness is essentially nil.

THAT IS WHY THE HOMELESS ARE EMPLOYED. They are young workers with no savings,
not low earners. `emp_homeless` at 0.955 is not a mis-set rung so much as a
statement that the model's homelessness is a liquidity event.

## Three levers, and the third is free

1. **Raise h_2** -- `smallest_rental_relative_to_lowest_income`, now 0.039.
   Prices low-income households out, so the homeless become selected on income.
   The gate has arms at 0.02535 and 0.06045, both close in; getting from 0.955 to
   0.460 may need far more than a +/-35 per cent bracket.
2. **Shrink the street** -- `size_homelessness`, now 0.149. Makes homelessness a
   worse outcome that only the destitute accept. NOTE the coupling recorded in
   ENGINE.md: the street is a RATIO of the rung, so raising h_2 drags the street
   up with it unless size_homelessness falls more than proportionally.
3. **Endow newborns** -- `newborn_endowment_scale`, at 0.0 in ALL 40 points, with
   a bound of (0, 3.0). Zero assets at 26 manufactures the young spike directly.
   The parameter has never taken a second value and the model is sitting on the
   corner of its range.

## One thing nothing scores

**Age 80 is the most homeless age in the model, at 6.02 per cent.** No target
touches the old-age tail. US homelessness peaks in middle age and the elderly
have Social Security, so this looks wrong on its face and is worth checking
before the counterfactuals lean on it.
