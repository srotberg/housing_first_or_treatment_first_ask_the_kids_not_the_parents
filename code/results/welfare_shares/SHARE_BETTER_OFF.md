# THE SHARE BETTER OFF. WHAT EXISTS, WHAT IT MEASURES, AND WHAT IT LEAVES OUT.

21 September, on the author's question "what about the % of households who are
better off?" and then "when you show newborns do you include the children?".

## IT EXISTS, AND I SAID IT DID NOT

`frac_in_support` is not a common-support diagnostic despite the name. Its
accumulating block sits under

    if (value_function_used>value_function_benchamrk_used)

with `distribution_mass_used` drawn from `distribution_stationary_benchmark`, so
it counts the mass of households whose counterfactual value beats their OWN
benchmark value at the SAME state. That is the share better off. It is computed
on every period of every transition and was printed only under
`solve_transition_dynamics==0`, which is never true in one.

I read the name instead of the condition above it, told the author the statistic
did not exist, and offered to build it. The gate is now removed and all four
series print every period as `TRANSITION BETTER OFF`.

**The check that settles the interpretation**: the BENCHMARK's own dump reads
0.0000 on all four, because comparing the benchmark against itself gives V > V,
false everywhere.

## THE LONG-RUN NUMBERS

From `counter_TF.txt`, the Treatment First steady state:

    all households        95.81%
    age-1 cohort          80.35%
    households with SUD    0.19%
    age-1 with SUD         0.00%

**Broad gains, concentrated losses.** About 96 per cent of households are better
off and essentially nobody with substance use disorder is.

**These are PRE-FIX.** That dump is dated 19 September, before the voucher cap
fixes. The post-fix arm 3 re-solve moved b by 0.03 per cent, lambda_d by 0.19,
h_1 by 0.15 and the CEV by 0.017 points, so these shares should be close -- but
that is an inference. The session that re-solved arm 3 committed its log and not
its dump.

## WHAT THE AGE-1 SHARE DOES NOT INCLUDE, AND IT IS THE AUTHOR'S POINT

`frac_in_support_youngest` compares `value_function` at `age_index==1`. **The
value function is the ADULT object. Childhood is not in it.** The source says so:

> average_welfare_with_childhood adds the adult half discounted by twenty five
> periods. These are REPORTED and feed nothing: no moment is bracketed on them
> and no adjuster reads them.

So the CEV path already reported to the author DOES include childhood; the SHARE
does not. Calling that series "newborns" was wrong -- it is the adult lifetime
value of the cohort born at that date.

## WHY A CHILDHOOD-INCLUSIVE SHARE IS NOT A GATED PRINT

    own_childhood_1 = sum over child ages of
                      beta^(a-1) * ( utility_at_age_1/mass_at_age_1
                                     - kappa_x*model_fraction_homeless(t) )

It is a SCALAR accumulated across the whole cross-section, not a per-state
object, and there is **no benchmark counterpart stored anywhere** -- grepped,
nothing. Two things are therefore missing before a household-level comparison
can exist: childhood utility per state in the counterfactual, and the same in
the benchmark, which means re-solving and re-saving the benchmark.

**And there is a modelling question under the engineering one.** A child's flow
comes from what its PARENT's household consumes, so childhood is indexed by the
parent's state, not by the age-1 household's own state. Attaching it to an age-1
household needs a parent-to-child mapping to be chosen. That is very likely why
the existing code keeps it as an aggregate, and it is the author's call, not a
detail to settle while implementing.

## THE CHEAP MIDDLE OPTION

`average_childhood_utility` is already computed per period and is also not saved
to the dumps. Printing it gives the SIZE and DIRECTION of the childhood effect
across the two economies without a share, and it is another gated-print fix
rather than new economics. Not applied yet: the running solve is mid backward
pass, where no checkpoint is written, so a stop now costs the hour it has spent
rather than the three minutes a forward-pass stop costs.
