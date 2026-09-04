# Calibration state — 4 September, 01:30

## THE METHOD CHANGED AT 01:27: sequential Nelder-Mead, all stages at once

The author, this morning: *"you claimed this method was better than nelder mead,
and faster....but we have been stuck on it for like 12 hr"*, then *"we are better
off trying nelder mead sequentially"*, *"since each iteration is just 2.5 minutes,
we are better off doing that"*, and *"you can do all the stages combined"*.

**The parallel firing sequence in ENGINE.md is SUSPENDED while `nm_loop.sh` is
alive.** Do not run `next_batch.py` and do not launch a worker round: the serial
loop owns `code/points/` for the duration, and a parallel round would fill the
archive with points from a different search while the simplex is mid-reflection.
Steps 0, 1 and 2 of the firing sequence (checkout, no supervisor, archive has
points on the live model) still apply at every firing and are still worth doing.

### Why Newton was abandoned

Three Jacobians, fifteen model solves each. **Every step landed above its own
base**: base SSR 0.9603, full step 2.2025, quarter step 1.7283. The cause is the
drug block — a finite-difference nudge of 0.35 per cent in `addiction_scalar_1`
moves `lambda_d` from −4.5 per cent to −96.5 per cent, so that column is a secant
across a cliff rather than a derivative, and being much the largest column it
dominates the normal equations and drags every other instrument with it. A
truncated SVD does not help, because the direction is strongly identified; it is
simply not linear. Nelder-Mead forms no derivative at all, so the cliff costs it
one reflection instead of a whole step.

### The objective moved from minimax to the sum of squared residuals

On the author's instruction of 4 September. `gaps.py`, `newton.best()` and
`nelder.py` all rank on it, so the report cannot print a gap table for one
equilibrium and an age profile for another.

## THE CONFIGURATION, unchanged

    number_of_beta_types  1          one beta for everyone
    fixed_productivity    0          the KKK stochastic process
    use_pia_formula       1          the US statute, with the SSI floor live
    ssi_floor_level       0.1774     the 2024 federal benefit rate
    ssi_floor_takeup      1.0        HELD, so the level is the effective floor
    newborn_endowment_scale  0.0     HELD at zero by the author
    homeless_death_risk_flat_in_age  0   the Baggett age profile

Model hash **b2530947f0**, 117 points. The 22:00 cap patch (`4df7be4132`, the
street barred at `max_age_to_choose_addiction`) was **REVERTED** on the author's
instruction — *"You should revert to allow the 80 year olds to be homeless
again"* — and its points are orphaned. Any earlier section of this file that
describes that economy as live is out of date.

## THE SEARCH

**Twenty instruments**, all stages unioned. Of the 23 parameter/moment pairs in
`next_batch.OWN`, three are out and each for a different reason:

| parameter | moment | why it is out |
|---|---|---|
| `weight_on_child` | `omega_c` | needs `measure_child_gap=1`, which costs a second full solve and converge |
| `newborn_endowment_scale` | `h_share1` | the author holds it at 0 |
| `ssi_floor_level` | `h_share5` | the author holds the floor to the 2024 federal rate |

`sud_homeless` WAS out and should not have been: the model prints
`UNTARGETED SUD share of the homeless` on every point ever solved and `gaps.py`
had no pattern for it, so its instrument looked like a parameter with no moment.
It sits at 0.1166 against Gutwinski's 0.217 on all 155 archived points. Fixed
4 September; costs no model time and applies retroactively.

The simplex was seeded from the archive: eighteen affinely independent vertices
out of 155 solved points, for **zero model solves**. Three directions remain, the
instruments nothing ever moved; `--ask` fills them one solve at a time.

    best      827aa52172   SSR 2.1441
    worst vertex           SSR 9.8159

The best rose from 1.9299 when `sud_homeless` joined the objective. That is a
moment 46 per cent adrift being counted for the first time, not a regression.

**Combining the stages changed the standing.** On stage 0 alone the best was
0.9603; the two moments stage 0 never scored are far off and were free to drift
the whole time:

    utility_cost_of_treatment   tau_u      0.45441   0.24500   +85.5%
    kappa_uem                   lambda_m   0.12859   0.25000   −48.6%

## PARKED BY THE AUTHOR

- **Young and old homelessness.** *"Ignore young and old homelessness for now. We
  will fix that later."* `h_share1` and `h_share5` are UNSCORED. The best stage-0
  point puts 87.0 per cent of the homeless in retirement against 25.5 per cent of
  the population, spiking at age 80.
- **The flat 1.6× mortality multiplier** (`homeless_death_risk_flat_in_age=2`) was
  measured as a matched pair, `047afb7487` → `d2e58e6afb`: retired share 0.8 → 0.0
  per cent, SSR 3.0511 → 3.0636. **That test does not answer the question it was
  set**, because at that vector the spike was already at age 26, not 80. It would
  have to be rerun at `9a9c749a75` to learn anything.
- **The morbidity state.** *"keep calibrating the rest and we'll deal with
  morbidity later"*. Evidence scan is in `data/MORBIDITY_EVIDENCE.md`.
- **The newborn endowment double count**, two options offered, no decision taken.

## OPEN WITH THE AUTHOR

Nothing is blocking. The loop runs to 400 iterations and commits every twelfth.
