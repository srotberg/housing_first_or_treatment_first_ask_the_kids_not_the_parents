# Putting serious mental illness into the Fortran

Decided: mental illness stays in the model, so the code has to gain it. This is
how, in the order it should be done, with the count of touch points measured
rather than guessed.

## What has to be true at the end

Six channels, all of them already written into Section 2.6 of the note:

| Channel | Object | Where it acts |
|---|---|---|
| productivity conditional on working | `rho_m` | `calculate_income` |
| both employment margins | `kappa_uem` | the job finding and separation rates |
| mortality | `kappa_phi_m` | `survival_probability` |
| the recovery hazard | `mu_m` | `probability_of_stopping_addiction` |
| the Stone-Geary shifter | `rho^b_m` | `calculate_flow_utility` |
| disability eligibility | `zeta_DI` | `calculate_income`, a branch that does not exist yet |

Plus the chain itself: onset derived from prevalence and the recovery rate, so
that calibrating persistence never disturbs prevalence,

    onset_m = lambda_m * p_m / (1 - p_m),   entry raised by iota when d = 1
    exit    = lambda_m

with `p_m = 0.055`, `lambda_m = 0.067`, `iota = 2.0` from the note's tables. The
chain does **not** depend on housing, which is a result rather than an omission:
At Home / Chez Soi looked for that effect and did not find it.

## The index, and why m goes on the outside

`unemployment_grid_size = include_addiction*6 + (1-include_addiction)*3` already
carries employment crossed with the disorder: `1..3` clean, `4..6` with a SUD,
where within each block `1` is employed, `2` is unemployed without insurance and
`3` is unemployed in the first year of a spell. `threshold_addiction_index = 3`
is the divider.

Make it `12`, with **mental illness as the outermost factor**:

    index = 6*m + 3*d + e        m in {0,1},  d in {0,1},  e in {1,2,3}

    1 .. 6    exactly what they mean today
    7 .. 12   the same six states, with mental illness

That ordering is the whole trick. Every existing test of the form
`unemployment_index <= threshold_addiction_index` stays correct for the first
block, so nothing that works today breaks; what is needed is that the tests
become block aware rather than being rewritten one by one.

The measured size of that job:

| Pattern | Occurrences |
|---|---|
| `threshold_addiction_index` | 156 |
| `unemployment_grid_size` | 124 |
| `do unemployment_index=1,unemployment_grid_size` | 27 |
| `future_unemployment_index` | 48 |
| `addiction_index` in any form | 356 |

Rewriting 156 index tests by hand is where the bugs come from. Do it with four
pure functions instead, added once near the head of `Global_Vars`:

```fortran
integer function emp_of(i)   ; emp_of = mod(i-1,3) + 1        ; end function
integer function sud_of(i)   ; sud_of = mod((i-1)/3, 2)       ; end function
integer function smi_of(i)   ; smi_of = (i-1)/6               ; end function
integer function idx_of(e,d,m) ; idx_of = 6*m + 3*d + e       ; end function
```

Then the rewrite is mechanical and checkable:

    unemployment_index <= threshold_addiction_index    ->  sud_of(i) == 0
    unemployment_index == threshold_addiction_index    ->  sud_of(i) == 0 .and. emp_of(i) == 3
    unemployment_index == threshold_addiction_index+1  ->  sud_of(i) == 1 .and. emp_of(i) == 1
    unemployment_index == unemployment_grid_size       ->  sud_of(i) == 1 .and. emp_of(i) == 3

That last line is the one to watch: `== unemployment_grid_size` currently means
"unemployed with insurance and with a SUD" and would silently come to mean
"...and mentally ill" the moment the grid grows. It appears in
`calculate_income` among other places, and it is the single most likely source
of a wrong answer that still runs.

## Order of work

1. **Add the four index functions and rewrite every test through them, with the
   grid still at 6.** The model must reproduce the current benchmark bit for bit
   before the grid grows. This is the step that makes the rest safe, and it is
   the one to spend the time on.
2. **Grow the grid to 12** and build the transition, with all six channel
   parameters set to their neutral values, `rho_m = kappa_uem = kappa_phi_m =
   mu_m = rho^b_m = 1`, `zeta_DI = 0`, `iota = 1`. Prevalence then moves but
   nothing else does, so the targeted moments must be unchanged to within the
   solver tolerances. If they are not, the transition is wrong.
3. **Switch the channels on one at a time**, checking the moment each is meant to
   move: `kappa_uem` against unemployment given mental illness, `kappa_phi_m`
   against the mortality multiplier, `mu_m` against recovery, `rho^b_m` against
   the SUD rate given mental illness, `zeta_DI` against the mental illness share
   of the homeless.
4. **Add the disability branch to `calculate_income`.** It is the fourth case of
   the note's income equation and the only genuinely new economics in the list.
5. **Recalibrate.** Four new internal parameters and one new target.

## What it costs

The state space doubles, so the backward pass doubles: **30 hours on four cores,
about 3 on forty**, against the 15 and 1.5 in `CALIBRATION_BUDGET.md`.

Cutting the asset grid from fifty points to thirty five buys that back exactly,
since the `a'` search is quadratic: `(50/35)^2 = 2.04`. Thirty points would buy
more than back. But the asset grid is the one cut the budget document says not to
make casually, because the objective is not single peaked in `a'`: voucher
eligibility is a step function of income including `ra`, the food stamp floor
kinks, and housing is discrete, so coarsening the grid coarsens exactly the
dimension that carries the notches. Validate it the way the budget already
demands for the ninety to fifty cut, by solving the benchmark at both and
comparing the targeted moments and both counterfactuals. That run is cheap once
homeownership is out.

## What this does not cover

Removing homeownership comes first in the audit's order of work and is worth 38x
on its own. Doing mental illness before it means every test run costs the full
51 minute pass rather than 80 seconds, so the sequence matters more than usual:
**cut the model down, then grow it.**
