# Unsecured borrowing breaks the budget identity for renters

Found 2 September 16:45, by running a borrowing-ON point locally and reading the
log rather than waiting on workers. It is why every ON arm has been slow, and it
matters far more than the slowness.

## What was measured

A borrowing-ON solve on the merged model, point `b083f765a0`:

    budget-not-clear lines, borrowing ON        250,039  and still climbing
    budget-not-clear lines, borrowing OFF             0  in all three OFF logs

The log reached 87 MB in about five minutes, which is itself most of the
slowness: the diagnostic prints ten lines per failing state.

The failures carry two shortfall magnitudes and they are not arbitrary:

    budget does not clear by                 -0.89828943890932111
    min(financial_grid(financial_index_used),0.d0) = -0.95587205886840820
    amortization_used        = 1
    years_left_on_mortgage_index = 1
    housing_status_index     = -1     (the street)
    housing_status_index_used = 2

THE SHORTFALL IS THE DEBT. The identity fails by very nearly the household's
own negative financial position.

## The cause, at line 24054

    budget_residual_1=after_tax_wealth_net_of_expenses_1-&
        ((frac_used*min(financial_grid(fin_index_frac_used),0.d0)+&
        (1-frac_used)*min(financial_grid(financial_index_used),0.d0))*&
        max(amortization_used-1,0)*housing_price(time_period)*&
        housing_size(housing_status_index_used)+ ...

The whole negative-asset term is multiplied by `max(amortization_used-1,0)`.
A renter has `amortization_used=1`, so that factor is ZERO and the term
vanishes: **a renter's debt does not appear in the budget identity at all.**

The structure was right while only owners could hold a negative position.
`min(financial_grid,0)` was mortgage debt, meaningful only when
`amortization_used>1`, and correctly scaled by `housing_price*housing_size`
because a mortgage is denominated against the house. Unsecured borrowing
introduces RENTERS with negative positions, and this identity has no term for
them -- it needs the unsecured branch, unscaled by housing and carrying
`unsecured_borrowing_rate` rather than `mortgage_interest_rate`.

THIS IS THE SAME BUG AS THE NET-WORTH ONE, in the same shape. Three net-worth
sites had a `min(financial_grid,0)*housing_price*housing_size` term that treated
every negative position as secured; they were fixed by gating on `has_house` and
adding a `(1-has_house)*financial_grid(financial_index)` branch. The budget
identity was not checked at the same time. It should have been.

## What is NOT yet established

Whether the OPTIMISER'S OWN resource constraint shares the defect, or whether
only this diagnostic is stale. The check recomputes an identity; it does not
prove which side of it the choice loop used. `after_tax_wealth_net_of_expenses_1`
is assembled across lines 21506-21931 and has not been traced yet.

The two possibilities are very different and must not be conflated:

- if the choice loop uses the same defective identity, a renter borrows and the
  resources never have to be repaid, so the ON economy is meaningless;
- if the choice loop is correct and only the check is stale, the ON economy is
  sound and this is a noisy diagnostic that costs 87 MB of log and a large part
  of the runtime.

TRACE IT BEFORE BELIEVING EITHER. A mechanism is not a measurement.

## What this invalidates right now

Every borrowing-ON measurement in flight, five arms, on both the pre-merge and
the merged model. None of them should be read until this is resolved. The
borrowing-OFF control `de322e4659` is untouched: zero budget failures, and its
finding stands -- w_bot is on target while the bottom tail is positive and
degenerate.
