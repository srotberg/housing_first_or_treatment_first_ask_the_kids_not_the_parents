# Calibration state — 3 September, 13:35

## THE ECONOMY IS STOCHASTIC PRODUCTIVITY NOW, on the author's instruction

*"Flip it to stochastic and calibrate everything there"*, 3 September.
`run_one_point.sh` defaults to `fixed_productivity=0` and `archive()` filters
the archive on the process, so nothing measured on the frozen grid pools with
anything measured now. That is why the usable archive is 68 points out of 614
and not a fault.

The process is `KKK_process(rho_fixed=0.5, sigma_fixed=0.309, rho_shock=0.9,
sigma_shock=0.2)` with `kkk_sigma_scale`, `kkk_s_deviation_bottom=3.35` and
`kkk_s_deviation_top=3.0`. Two components collapsed onto one age-varying grid.

## THE BEST POINT IS 71ab126acb AND THE LOSS IS BLIND TO ITS DISPERSION

    point_71ab126acb   MODEL ae10d02fc7   minimax 84.0%   median 32.0%
    inside ten per cent 5 of 21           worst: pi_V +84.0

**Read this before treating it as the base.** `sigma_y` is `not measured` at
every archived point, because its object changed this afternoon and the old
label is dropped. So the minimax cannot see dispersion — and 71ab126acb runs
`kkk_sigma_scale=1.0`, the UNSCALED process, whose bottom half share of
productivity was 0.329 against a 0.172 target. It is "best" partly because the
moment that would condemn it is invisible.

`point_c048025c98`, at `kkk_sigma_scale=2.20949` and
`bottom_productivity_level=0.004`, is the better economy on the housing block:

    moment        c048025c98      71ab126acb     target
    h_1           0.003827 (-4%)  0.000711 (-82%) 0.00399
    h_share1      0.2409   (-7%)  0.1007   (-61%) 0.26
    omega_l       0.2279  (-43%)  0.2408  (-40%)  0.40

**MEASURING sigma_y AT THE SCALED BASE IS THE NEXT THING THAT MATTERS.** Until
one point reports it on the new definition the gate is choosing between
economies on an incomplete loss.

## IN FLIGHT: the drug Jacobian step, 3 lines, 3 workers

`batch_drugfit_1330.txt`, launched 13:29. Full, half and quarter step off
`point_21b30a4de9` on `lambda_addiction` and `addiction_scalar_1`. Branches
`wip/drugfit-a-1330`, `-b-`, `-c-`.

The gate's own decision on the round: b is 31.6 per cent out at the best drug
point, inside four times the threshold, so **this round is the drug block ALONE
and no arms went out with it.** An arm measured off an unpinned base has to be
measured again.

## THE DRUG BLOCK HAS TO BE RE-PINNED, and the 2x2 that lets it is in

The block was closed to 7.7 per cent on the FROZEN grid and does not transfer:
b is +32.0 per cent on this economy. The 2x2 landed at 13:20 and straddles both
targets, which is what `restore.py` needed to fit at all:

    point         lambda_addiction  addiction_scalar_1   b        lambda_d
    dfda9c9942         2.69141           0.0282234    0.01388     0.00037
    4b6ca93a36         3.17586           0.033204     0.05831     0.01407
    a5e945af9b         2.2877            0.033204     0.12859     0.03389
    6f02506be3         2.69141           0.0391807    0.17918     0.05874
    target                                            0.08900     0.03680

`a5e945af9b` is already b +44.5, lambda_d -7.9.

## HOMELESSNESS IN THIS MODEL IS A TASTE MARGIN, AND THAT IS WHAT BLOCKS
## emp_homeless

Measured at `c048025c98`:

    DIAG homeless who could afford it on INCOME ALONE = 0.932
    DIAG homeless by choice, share of the homeless    = 0.940

Ninety-four per cent of the homeless are there by choice and ninety-three per
cent could rent the cheapest unit out of income. `bottom_productivity_level`
moved `emp_homeless` only 0.8598 -> 0.8247 across the whole move from 0 to
0.004 for that reason: the households the bottom node impoverishes are already
homeless, and the ones setting the employed share are choosers, who are
employed. **The bottom node cannot fix the composition while the choice margin
dominates the count.** This is the open question the author should decide on.

## `net_income_lowest` IS PRODUCTIVITY, NOT INCOME

    net_income_lowest = labor_income_tax_rate*employment_grid(1,1)**curvature

No labour supply, no age-efficiency profile. So the line every point prints,
`cheapest rental over lowest net income`, is rent over after-tax PRODUCTIVITY:
16.55 at `c048025c98`, where the honest hours-adjusted figure at the model's own
`omega_l` of 0.228 is about 73. The author raised this on 3 September: *"you
can't go off by productivity alone and the rent, you have to account for the
labor supply reducing the income below what the productivity itself reads"*.
The normalisation that used it is commented out, so it survives only as a
printed number -- but it is a printed number that has been informing exactly
this decision. NOT YET FIXED; it needs the author's call on whether to spend a
Fortran edit on a diagnostic.

## Three moments changed definition or wiring this afternoon

- **sigma_y** is the bottom half share of LABOUR INCOME, walked at the median of
  a new earnings histogram over working-age households in work, with hours and
  the age profile in it. Target unchanged at 0.172, which was always an earnings
  statistic. The old productivity share stays as a DIAG. Old label in
  `STALE_LABEL`, so archived points drop the row rather than mis-compare.
- **emp_homeless** was emitted as `UNTARGETED`; `score_points` reads `MOMENT`
  lines only, so its owner `bottom_productivity_level` had a target it could not
  see for a day. It is a `MOMENT` now, target 0.460.
- **h_share1** was scored in `gaps.py` and NOT in `next_batch.py`:
  `newborn_endowment_scale` had no entry in `OWN`, so the moment was outside
  `OWN.values() | GATE` and the gate neither counted nor stepped it. Mapped now,
  bound (0.0, 3.0). It does not close the gap -- the endowment only pushes
  h_share1 DOWN and is at its floor of 0.0 with h_share1 already below target.

Registered inert, `6c3b8a9a23 -> ae10d02fc7`; 64 of 581 points pooled before
the edit and 64 after. Both gate builds clean.

## Solve time, measured on this economy

3 to 4 minutes, median 3 over the stochastic points so far; the four drug
points took 3 minutes each on 4 cores. Not the 11 minutes the frozen
seventeen-node grid needed at two beta types.

## Not in the calibration

`code/points_pregrid/` is PRESERVED and never scored or seeded from.
`p_det`, `p_fp` and `c_test` do nothing in the benchmark and belong with the
experiment, not Table 5.
