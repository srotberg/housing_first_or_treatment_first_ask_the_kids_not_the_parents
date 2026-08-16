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

Plus the chain itself, and **the onset rate is a profile, not a scalar.** The
model note is explicit that the scalar version was tried and is wrong: a flat
onset against a flat recovery drives prevalence towards its steady state from
below, so the model produces a prevalence profile that *rises* with age, where
NSDUH has it *falling* from 11.0 per cent at 26 to 29 to 1.4 per cent at 65 and
over, a factor of eight. It hit the 5.5 per cent average with the shape
backwards, which misplaces the channel and everything it feeds.

So onset is backed out of the observed prevalence profile and the recovery
hazard,

    lambda(a) = [ p(a+1) - p(a)(1 - mu) ] / (1 - p(a))

with prevalence fitted **log linearly**, R^2 = 0.977, and not interpolated
piecewise: differencing a piecewise linear curve turns every kink into a spike,
and the first attempt gave onset of 1.00 at 26, 0.01 at 32 and exactly zero at 56
and 68. Those zeros were artifacts. Entry is raised by `iota = 2.0` when `d = 1`,
exit is `lambda_m = 0.067`, the level stays calibrated to `p_m = 0.055`, and
newborns enter at the observed prevalence at 26 rather than at the ergodic of the
age one transition matrix, which would start them at 4.7 per cent against 11 to
13 observed.

The chain does **not** depend on housing, which is a result rather than an
omission: At Home / Chez Soi looked for that effect and did not find it.

## The index, and why m goes on the outside

`unemployment_grid_size = include_addiction*6 + (1-include_addiction)*3` already
carries employment crossed with the disorder: `1..3` clean, `4..6` with a SUD,
where within each block `1` is employed, `2` is unemployed without insurance and
`3` is unemployed in the first year of a spell. `threshold_addiction_index = 3`
is the divider.

**CORRECTED, and this is the opposite of what this plan first said.** Put the
**SUD** outermost and mental illness inside it:

    index = 3*n_smi*d + 3*m + e      e in 1..3,  m,d in 0..1,  n_smi in {1,2}

    n_smi = 1:  1..3 clean, 4..6 with a SUD      exactly today's layout
    n_smi = 2:  1..6 clean, 7..12 with a SUD

The first version of this plan put `m` outermost, which looked equivalent and is
not. Counting the patterns in the source shows why: there are 37 uses of
`threshold_addiction_index` that are not comparisons at all but **loop bounds**,
of the form `1 .. threshold` and `threshold+1 .. grid_size`, meaning "sweep the
clean block" or "sweep the SUD block". With `m` outermost the clean block is
`{1,2,3,7,8,9}` and neither range is contiguous, so all 37 break. With the SUD
outermost both blocks stay contiguous at either grid size, so all 37 are correct
untouched, and so are the 74 coarse tests of the form `index > threshold`, which
still mean exactly "has a SUD".

That leaves only the fine grained employment tests to rewrite, which is about
thirty sites rather than a hundred and fifty.

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
integer function emp_of(i)     ; emp_of = mod(i-1,3) + 1                    ; end function
integer function smi_of(i)     ; smi_of = mod((i-1)/3, number_of_smi_states) ; end function
integer function sud_of(i)     ; sud_of = (i-1)/(3*number_of_smi_states)     ; end function
integer function idx_of(e,m,d) ; idx_of = 3*number_of_smi_states*d + 3*m + e ; end function
```

Written against `number_of_smi_states` they are correct at **both** grid sizes,
with `threshold_addiction_index = 3*number_of_smi_states` and
`unemployment_grid_size = 6*number_of_smi_states`. That is what makes step 1
below a no-op by construction rather than by hope.

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

1. ~~**Add the four index functions and rewrite every test through them, with the
   grid still at 6.**~~ **DONE.** `number_of_smi_states = 1`, so the grid is
   still 6 and the layout is unchanged. 49 fine grained tests now go through
   `emp_of` and `sud_of`; the loop bounds and the coarse SUD tests were left
   alone because the SUD being outermost keeps them correct. Every rewritten
   form was checked to be identical to the one it replaced at every index in the
   grid, and `verify_index_map` re-checks that inside the model at startup and
   stops it if any pair disagrees. Two sites needed care: the original had
   `index == threshold - 1` and `index == grid_size - 1`, arithmetic rather than
   comparison, and a first pass left the `-1` dangling. The compiler caught
   both.
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
