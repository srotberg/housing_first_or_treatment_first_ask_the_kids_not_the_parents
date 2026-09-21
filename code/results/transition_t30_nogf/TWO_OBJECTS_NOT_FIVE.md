# THE TRANSITION SOLVES FOR TWO OBJECTS. I SAID FIVE AND WAS WRONG.

21 September, 03:00. Correcting commit e09329e7, pushed twenty minutes earlier.

## WHAT I CLAIMED

> The transition iterates five objects per period. [...] housing_price, rent and
> lump_sum_transfer were not [saved], and their guess was rebuilt from a
> level-and-slope ramp on every restart. **Three of the four stopping rules are
> theirs**, so a restart inherited the two paths it had earned and threw away the
> housing and rental clearing, which at four hours a loop is the expensive half.

## WHAT IS ACTUALLY THERE

    integer, parameter :: peg_prices_in_counterfactual=1

and inside the loop, in every period:

    if (peg_prices_in_counterfactual==1) then
        housing_price(time_index)=calibrated_stationary_housing_price
        distance_housing_market(time_index)=0
        largest_housing_market_distance=0
    ...
        rent(time_index,:)=rent_calibrated(:)
        distance_rental_market(time_index)=0
        largest_rental_market_distance=0

The peg is the author's instruction of 8 September -- *"I also want to keep
constant the housing price and rent in a transition computation"* -- and the
reason is in the comment beside it: homeownership is off, so P prices rental
units and nothing else, and a reform that houses more people would bid it up
period by period and drag the rent along, making the path incomparable with the
long-run counterfactual it is supposed to converge to.

`lump_sum_transfer` is never assigned inside the loop at all. It is built once
in the prologue and thereafter only written to a file.

**So the objects are two, and the binding stopping rules are two:**

    price_of_addictive_good_path(t)   drug market      rule 1e-2
    probability_of_voucher_path(t)    budget residual  rule 5e-2

The housing and rental clauses of the four-way exit test are satisfied by
construction, not by convergence. There was no housing or rental clearing for a
restart to throw away.

## HOW I GOT IT WRONG

I read the `elseif (loop_count>start_updating_at_loop_number)` branch -- which
does update housing_price and rent off their excess demands -- and did not check
the `if` above it, which the compile-time peg makes the only live branch. A
parameter set to 1 at declaration makes an entire arm of the code dead, and
grepping for assignments finds the dead arm exactly as readily as the live one.

The author caught it in one line: *"rent and housing price and lump sum transfer
are not equilibrium objects, they are constant"*, and before that *"i can only
think of 2: pi_v and p_v"*.

## AND HOMELESSNESS IS NOT ONE EITHER

The author, same exchange: *"even the aggregate homelessness should not be
something to converge on, once pi_v and p_v converge, homelessness is what it is
and is applied to the welfare"*. That is right and the code already does it --
`model_fraction_homeless` appears nowhere in the transition's do-while except in
the comments of the path writer, which says so itself: it is written every loop
as a reference to score a restart against and is never read back.

## WHAT WAS CHANGED, AND WHAT IS STILL OWED

`restart_transition.sh` now promotes the TWO instrument paths only. Promoting a
constant is noise, and feeding it back through a reader is worse than noise:
loop 0's BACKWARD pass would use the file's value before the peg is re-imposed
inside the loop.

**Still owed.** The three extra readers and writers added to the Fortran in
e09329e7 are dead weight and the three readers are the hazard just described.
They must come out. They were NOT removed today because `hftf` T=45 has been
running since 02:49 and the standing rule is that code/*.f90 is not edited while
a solve is running. The running binary is unaffected either way -- it compiled
its own copy, and its log records `HOUSE PRICE PATH: no seed file, ramp stands`
for all three, so nothing was read. Remove them at the next build.
