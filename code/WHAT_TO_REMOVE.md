# What can come out, ranked by what it is worth

Measured baseline: one working age of the backward induction takes **71 s** on
four cores, one full pass **51 minutes**. Everything below is a multiplier on
that. Nothing on this list costs the model as written anything, because most of
it is machinery the revision already removed on paper and not yet in the code.

## 1. Housing entered with is still a state. Worth 6.6x

`do housing_status_index=lowest_housing_grid_point,housing_status_grid_size-1`
is an outer loop over the unit the household **arrives in**, eight values for a
renter. The model as written does not have it:

> Survival, employment transitions and the recovery hazard all condition on the
> *chosen* housing, and renters face no adjustment cost, so the unit a household
> arrives in is payoff-irrelevant. Carrying it would replicate the whole problem
> N_h times; removing it leaves every aggregate unchanged and cuts the solve by
> a factor of 6.6.

That is the model note's own arithmetic, and it is the single largest item
available. It is not an approximation: with no moving costs the value function
is genuinely constant across that index, so removing it changes no aggregate at
all. It would have to come back if moving costs were ever added.

**This is the one to do first.** It is worth more than everything else here put
together.

## 2. The owner branch is still solved. Worth about 2x

`max_amortization_years=2` and the loop
`do years_left_on_mortgage_index=1,...,max_amortization_years` runs twice, with
`years_left_on_mortgage_index>1` setting `has_house=1`. So the owner problem is
still being solved on every pass, along with its buy, sell and move branches,
even though the revision removes homeownership, tenure, mortgages and negative
assets.

It also drags the asset grid with it. `financial_grid_size` is
`negative_financial_grid_size=61` plus `positive_financial_grid_size=90`. The 61
negative points are mortgage debt: renters already run 61 to 151, so those points
exist only to serve a tenure the model no longer has.

Removing the owner branch is worth roughly 2x directly, plus whatever the dead
allocations cost in memory traffic.

## 3. The income grid, 9 points. Worth 1.8x at 5 points, and it is the one to be careful with

With `fixed_productivity=1` the transition is the identity, so productivity is a
pure type: the model decouples into nine independent problems and cost is
**linear** in the number of points. Nine to five is a straight 1.8x.

But this is the one place where the saving is paid for. The paper's headline
result is who uses drugs **by income**, and the stylized model's whole argument
is about where a threshold in income sits. Five points across a lognormal with a
standard deviation near 0.5 in logs is a coarse instrument for locating a
threshold, and the participation moment is a near cliff in `b`, so a coarse
income grid makes the moment itself jumpier to hit.

Suggested: **seven, not five**, worth 1.3x, and only after items 1 and 2. If the
gradient moments come out unchanged at seven, five can be tried.

## 4. The housing choice grid, 4 points to 3. Worth 1.33x

The model as written has one homelessness state and three rental sizes, from two
parameters, the level and the geometric spread. Dropping to two rentals is worth
1.33x on the choice loop.

It is defensible but not free. Two rented sizes is the fewest that lets a
household economise on housing rather than lose it, and the stylized model shows
what happens without that margin: with a single rental size homelessness comes
out at **3.48 per cent against a target of 0.40**, and no value of the street's
service flow brings it back. Going to **three total** keeps two rentals and is
safe. Going to two total is the failure case.

Note the code still has `housing_status_grid_size=7`, so getting to four is
itself a saving before any of this.

## 5. What is NOT worth removing

**The asset grid.** It is the largest single factor, since the `a'` search is
quadratic in it, and halving it would be worth 4x. But the objective is not
single peaked in `a'` precisely because voucher eligibility is a step function of
income, the food stamp floor kinks, and housing is discrete. Those notches are
where this paper's action is. A coarse asset grid degrades exactly the region
the welfare comparison turns on, and the welfare margins are tenths of a per
cent.

**The expectation hoist.** Implemented, verified bit identical, measured at one
per cent. See TIMING.md.

## What it adds up to

Items 1, 2 and 4 together are `6.6 x 2 x 1.33` which is about **17x**, and none
of them costs the model as specified anything at all. That takes a working age
from 71 s to roughly 4 s, a backward pass from 51 minutes to about 3, and a
stationary equilibrium from 5 to 10 hours to well under an hour. A first stage
calibration then moves from weeks on four cores to a day or two, which is the
threshold at which the calibration can actually be iterated rather than launched
and hoped for.

Adding item 3 at seven points takes it to roughly 22x.
