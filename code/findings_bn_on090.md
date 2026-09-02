# bn_on090 — the ON arm at the higher impatient discount did not produce a measurement

Point `a2778b36aa`, from `code/batch_bn_on090.txt`, run verbatim and unmodified:
`include_unsecured_borrowing=1`, `discount_factor_impatient=0.90`,
`unsecured_borrowing_rate=0.055`, `unsecured_borrowing_limit=1.50`.

**No point file was written.** The run does not terminate. It was stopped after
4h06m; no scored moment exists, so none of the questions the batch was meant to
answer can be answered from it. What follows is why, established from the live
process, and what it implies for the arm.

## Every question asked, and its status

| Question | Answer |
| --- | --- |
| `w_bot` against the 0.0250 target | **not measured** — no point file |
| every bottom-percentile wealth share, and is ANY negative | **not measured** |
| are the bottom shares still exact multiples of one another | **not measured** |
| `beta` against the 3.0–4.5 band | **not measured** |
| every other scored moment with its per-cent gap | **not measured** |
| where `w_bot` and `beta` land against the OFF control `de322e4659` | **cannot be stated** |

The comparison against the borrowing-OFF control at 0.75 is therefore still open.
Nothing here revises the control's own numbers (`w_bot` 0.0247429, −1.03% off
target, no negative bottom share, the three shares exactly 1x/5x/10x).

## What actually happened

The solve itself finished, and quickly. Both beta types' value functions solved
at about 5 s per age over 60 ages, the distribution converged in 55 sweeps to
`final_distance = 5.79e-04`, and the moment block printed through the SMI and
homeless-income diagnostics. All of that took roughly eight minutes, from 15:39
to 15:47.

From 15:47 onward the process consumed exactly one core, the three OpenMP worker
threads asleep, and wrote not one further byte for 3h58m (`wchar` frozen at
445,397,245 across the whole period).

`gdb`, attached read-only and detached cleanly:

```
#0  _gfortran_mminloc0_4_r8 () from libgfortran.so.5
#1  stationary_equilibrium_wealth_distribution_of_old (time_period=1)
        at housing_first_or_treatment_first_SR_v1.f90:11871
#2  calibrating_model ()  at housing_first_or_treatment_first_SR_v1.f90:36246
#3  main_program ()       at housing_first_or_treatment_first_SR_v1.f90:7540
```

with `wealth_of_top_x_perc_index = 1` — still the **first** of three brackets,
four hours in.

## Why it cannot terminate

The walk at line 11861 retires one cell per pass and exits only when accumulated
mass clears its target:

```fortran
do while ((distance_pop_of_top_wealth_x_perc(i)+10.d0**(-6)) <= &
          stopping_rule_wealth_dist_of_old(i))
    min_wealth_index = minloc(wealth_matrix(time_period,:,:,:), &
        mask = wealth_matrix(time_period,:,:,:) > &
               -housing_price(time_period)*housing_size(housing_status_grid_size-1))
    ...
```

There is **no iteration bound**. Its sibling walk in
`stationary_equilibirum_homeownership_rate` (line ~11062) is safe precisely
because its final bracket is capped by `wealth_counter_2 <= wealth_counter`;
this one has no such cap.

Read from the live process:

- `housing_price(1) = 12.048193`, `housing_size(2) = 0.039`, so the mask floor is
  **−0.4698795**;
- the seven negative financial grid points are
  −0.9558721, −0.7022733, **−0.4876898**, −0.3121215, −0.1755683, −0.0780304, −0.0195076;
- a renter's net wealth is `financial_grid(financial_index)` outright
  (`has_house = 0` kills the other three terms), so the **three most negative
  points sit below the floor** and their cells fail the mask `> floor` from the
  outset;
- `wealth_matrix` holds `32 x 4 x 1 = 128` cells in total.

So the mass parked at the deepest borrowing points never accrues to
`pop_of_top_wealth_x_perc`. Once the mask-eligible cells are exhausted — at most
128 passes — `minloc` over an all-false mask returns 0 in every position, the
code reads `distribution_stationary(0)%vector_transition_real(...,0,:,:,-2,:)`
(out of bounds twice over: the amortization dimension starts at 1, the housing
dimension at −1), `sum_distribution_used` contributes nothing, `pop` stops
growing, `distance` is pinned, and the `do while` never turns false. It then
re-runs `minval`/`minloc` over the 128 cells forever, which is exactly the frame
gdb caught.

The borrowing-OFF control never reaches this: with no cell below the floor, `pop`
clears its target and the loop exits. **This is a bug that `include_unsecured_borrowing=1`
exposes, not a property of `discount_factor_impatient=0.90`.** Any ON point whose
equilibrium puts mass below `-housing_price*housing_size(housing_status_grid_size-1)`
will hang the same way, at any impatient discount.

## One further observation from the log

The worker log reached **425 MB**, against 200–300 KB for a normal point. The bulk
is a single diagnostic repeated 1,016,518 times:

```
budget does not clear by -0.89828943890932111
min(financial_grid(fin_index_frac_used),0.d0)= -0.95587205886840820
min(financial_grid(financial_index_used),0.d0)= -0.95587205886840820
amortization_used=  1
housing_status_index= -1
```

always at the most negative grid point. It did not stop the solve, but a million
non-clearing budgets at the deepest borrowing node is worth a look on its own,
independently of the hang.

## Not done, deliberately

No source was modified, no vector was changed, no retry was attempted, and
`supervise_calibration.py` was not run. Fixing the walk — bounding the loop as its
sibling is bounded, and deciding whether the mask floor should follow the
borrowing limit rather than the largest house — is a code change the ON arm needs
before it can be measured, and it is the author's call.

Evidence is in `code/logs_bn_on090/`: `head.log`, `tail.log`, `gdb_backtrace.txt`.
The full 425 MB log was left uncommitted.
