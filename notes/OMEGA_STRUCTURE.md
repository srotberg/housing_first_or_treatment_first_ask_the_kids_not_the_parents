# Why omega_c cannot reach its moment

## The moment

    child_use_gap_data = 1/0.845 - 1 = 0.18343

Parents use 84.5 per cent of what non-parents use, so use with the child term
off is 18.3 per cent higher than with it on. The model computes exactly that:
`drug_users_without_child / model_total_drug_users(1) - 1`. The DEFINITION is
right; the mechanism cannot produce the number.

MEASURED: 0.0209 at four classes and 0.0203 at two, both at omega_c = 0.17. One
ninth of the target. The claim that it saturates near 0.037 at omega_c = 1 is an
EXTRAPOLATION off an elasticity of 0.32 and has not been measured.

## The structure

    future_utility_vector = ... +
        discount_factor *
        (1 - survival_probability(age_index, is_homeless_1, ...)) *
        weight_on_child * expected_child_value(...)

Multiplied by the probability of DYING THIS PERIOD, which for a working age
parent is a fraction of a per cent. omega_c scales a term already multiplied by
about 0.01.

## The level and the difference

`expected_child_value` is differenced against the clean housed slice, which is
then zeroed, at lines 29927-29930. The design comment at 4986 specifies the
LEVEL -- `beta*phi*EV + beta*(1-phi)*omega*E V_1` -- so the code contradicts its
own spec, and the level is also what Barro-Becker and the altruistic OLG papers
use. The author raised both points and both are right.

The decomposition of the child term's effect on the cost of using:

    omega * [ (phi_using - phi_clean) * V_child          <- the mortality channel
            + (1 - phi_using) * (V_clean - V_penalised) ] <- the penalty channel

At phi_clean = 0.99, phi_using = 0.98, V_child = 2200, penalty gap 100:

    mortality channel  -22
    penalty channel     +2

The mortality channel swamps the penalty channel about ELEVEN TO ONE. The
differencing zeroes V_clean and with it the whole first bracket, which is why it
gets the sign the moment needs and keeps only a ninth of the size.

Neither version can deliver 18 per cent. The level gives a large effect pointing
the WRONG way -- the child's value becomes a payout on death, so raising omega
makes dying less bad and using cheaper. The difference gives a small effect
pointing the right way. This is an argument for the child entering the parent's
payoff WHILE ALIVE, which is the thing neither formulation has.

TO BE MEASURED, NOT ARGUED: drop the four differencing lines, keep everything
else, read omega's sign. Negative confirms the analysis; positive and large
means the level is the answer and the omega problem is solved.

## Two avenues that are closed

BEQUESTS CANNOT IDENTIFY IT. `expected_child_value` is dimensioned
`(employment_grid_size,0:1,1:2)` -- the parent's productivity class, disorder and
homelessness. NO FINANCIAL DIMENSION. The child's value does not depend on how
much the parent leaves, so omega_c cannot move bequests. Inheritance still flows
(0.306 per period) but no altruism responds to it.

And there is no bequest moment anyway: `bequests_to_net_wealth_data = 0.012`
appears EXACTLY ONCE in the file, at its own declaration, the same scar the file
records for `child_homeless_ratio_data`.

MEASURED, for whoever builds that moment: bequests are 0.828 per cent of net
worth against 1.2 in the data, 31 per cent low. Aggregate net worth is 82.55 two
ways that agree to 0.07 per cent -- 3.5182 x 23.4628 via wealth over output, and
1.6454 x 50.135 via average net wealth times population mass -- against a
bequest flow of 0.68323.

## What omega_c does and does not touch

It governs BEHAVIOUR, not the welfare accounting. The child's cost is counted
through the newborn distribution: a newborn of a parent with the disorder is
placed in the penalised class and carries a lower value function for life,
whatever omega_c is. So a small omega_c means the externality is almost entirely
EXTERNAL, which is what the paper's argument wants. Failing this moment is a
calibration blemish, not a threat to the result.

## CORRECTION, 10 September evening: the elasticity was never measured

Everything above that rests on an elasticity of 0.32 is withdrawn, including the
claim that reaching 0.18343 would need omega_c of order 166. That elasticity was
fitted to a saturation point that had been INFERRED rather than run. It is the
same extrapolation method that failed on the delta_h floor, on the rho frontier
and on the consumption equivalent, and it should have been discarded hours
earlier.

TWO MEASURED POINTS, on the author's cleaner cross-run statistic -- b at
omega_c = 0 against b at omega_c = X, rather than the model's internal moment:

    omega_c = 0      b = 0.087846     difference  0
    omega_c = 0.17   b = 0.085921     difference  2.24 per cent

(The model's own internal moment read 2.03 per cent at omega_c = 0.17. The two
differ because the internal version holds some general equilibrium objects fixed
while separate runs re-solve everything. The cross-run statistic is the cleaner
one and is what the ladder reports.)

A straight line through those two has slope 13.2 per cent per unit of omega_c,
so the 18.34 per cent target sits at

    omega_c  ~  1.39

just above the cap of 1 that was standing in the way. The linear reading is an
UPPER bound on the response -- at small omega the child term is a first order
perturbation, and it must flatten as the marginal households run out -- so 1.39
is a LOWER bound on the omega_c required.

## The cap of one had no reason behind it

The author, *"wait, why cant omega_c be larger than 1?"*. In the specification
the model runs, the child term is ADDED:

    V = u + beta*[ phi*V' + (1-phi)*omega*X ]

so omega is a MULTIPLIER, not a share, and nothing makes it improper above one.
The bound belongs to a weighted average form, which this is not. It was capping
the parameter at a tenth of the range needed.

What does bound it is the recursion: X is proportional to the value function,
about 0.045 of it, so a fixed point exists only while omega*0.045*E[beta^T] < 1,
of the order of fifty. The cap is now a named parameter set at 25.

THE LADDER: 0, 0.17, 1 measured, then 5 and 20 if needed. Reported as
b(0)/b(omega) - 1 against the 18.34 per cent target.
