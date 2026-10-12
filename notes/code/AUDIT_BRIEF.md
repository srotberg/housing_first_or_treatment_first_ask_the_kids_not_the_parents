# The full-code audit, 31 August

The author asked for the whole model audited. 38,137 lines, 106 subroutines,
split across parallel auditors. Each writes `code/audit/AUDIT_<slice>.md` and
commits it. This file is the brief they share.

## WHAT TO LOOK FOR, in priority order

These are the classes that have actually produced bugs in this model, newest
first. A generic hunt produces noise; these produce findings.

### 1. The two-pass (two discount factor types) machinery

The benchmark chain runs ONCE PER TYPE. `accumulating_beta_types` is 0 on the
first pass and 1 on the second. Statistics accumulators must NOT reset on the
second pass, so their resets are written
`if (accumulating_beta_types==0) X(time_period)=0`. Four bugs today, all the
same shape: **a routine written for a single pass, called where the pass count
is no longer what it assumes.**

  - A DENOMINATOR is not an accumulator. Masses like `sum_of_distribution` are
    RECOMPUTED from `distribution_stationary`, which holds only the type just
    solved, so they hold one unit against numerators holding two. They are
    scaled by `mass_passes` at the recomputation. Find any that are not.
  - MODULE SCOPE LEAKS. A routine can be internally consistent and still leave
    a one-type value in a shared variable that nine later routines read. Ask who
    reads it AFTER, not whether the routine itself is consistent.
  - CALLED TWICE. A routine with guarded resets, called again outside the loop
    where `accumulating_beta_types` is 0, WIPES the pooled totals and refills
    from the last type solved. This is invisible at one type.
  - The nine routines in the loop, in order: stationary_equilibrium_statistics,
    stationary_equilibirum_homeownership_rate, govt_revenues_calc,
    calculate_aggregate_consumption, calculate_welfare,
    calculate_household_housing_spending, calculate_welfare_by_characteristics,
    calculate_homeownership_by_characteristics,
    stationary_equilibrium_wealth_distribution_of_old. Anything else that
    touches `distribution_stationary` runs OUTSIDE it.

### 2. Dead code that looks live

`adjusting_unemployment_probabilities_based_on_productivity` computes a profile
across the whole employment grid and then overwrites it with 1, so the
separation rate does not vary with productivity at all -- and the comment says
so. `stationary_equilibrium_income_distribution` is never called from anywhere.
`distance_money_cost_of_treatment` is declared and never used.
`distance_discount_factor_impatient` and `discount_factor_impatient_adjuster`
likewise. `beta_type_weight` is declared and never used.

REPORT: any parameter that is computed and then overwritten; any variable
declared and never read; any subroutine never called; any `distance_` with no
adjuster or `_adjuster` with no distance.

### 3. A moment that does not measure what its target measures

`h_2` was compared against a CEX expenditure share while the model computed an
income share; the two are not close, because a household at the bottom spends
more than it earns. For every `MOMENT` printed in `print_all_moments`, check the
UNIVERSE (all households? renters? working age?) and the DENOMINATOR (income?
expenditure? mass?) against what the target is a number for.

### 4. The ordinary Fortran hazards

Array bounds; a variable read before it is set; `intent(out)` arguments the
routine never assigns; implicit typing where a scope has no `implicit none`
(a misspelled name became an uninitialised real once and broke a transition
matrix row); integer division where real was meant; a loop index reused by an
inner loop.

## WHAT A FINDING MUST CONTAIN

  - the line number and the subroutine
  - what the code does, quoted
  - what it should do, and WHY you believe that
  - whether it is LIVE in the benchmark, live only in a counterfactual or the
    transition, or dead
  - what it would change if fixed: a number if you can, "unknown" if not

## WHAT NOT TO DO

Do not fix anything. This is a read-only audit; the author decides what gets
changed. Do not report style. Do not report a thing the comments already
explain as deliberate -- this file is heavily commented and most oddities are
documented decisions. Do not guess at a number you have not computed: three
diagnoses today were reasoned from the code and all three were wrong when
measured.

Say "I found nothing in this class" where that is true. A short honest audit is
worth more than a long speculative one.
