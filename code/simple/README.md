# Simplified HF/TF model

A clean solver for the reduced model described in `writing/REVISION_PLAN.md`. The original
`../housing_first_or_treatment_first_SR_v1.f90` is untouched and remains the version with
homeownership, for the appendix.

```
make          # build
make run      # build and run on 4 threads
make debug    # -O0 -g -fcheck=all, for when something segfaults
make clean
```

## Status

**Working:** household problem, stationary distribution, aggregate reporting.
**Not yet written:** the equilibrium loops (τ_ℓ, p_v, bequests), calibration, counterfactuals,
welfare. Parameter values in `params.f90` are placeholders — the aggregates the model
currently prints are not meaningful.

## Measured performance (4 cores, gfortran 13.3, `-O2`)

| | |
|---|---|
| Household solve | **1.42 s** |
| Distribution | 0.01 s |
| **Total per equilibrium** | **~1.45 s** |
| Bellman evaluations | 373,248,000 |
| Thread scaling | 4.52 s (1) → 2.36 s (2) → 1.42 s (4) — 3.2×, ~80% efficient |

For comparison, the original model does not complete a single backward-induction pass in
four minutes on the same machine.

## What makes it fast

**1. Housing entered with is not a state.** Survival, employment transitions and the
recovery hazard all condition on the *chosen* `h'`, and renters face no adjustment cost, so
the unit a household arrives in is payoff-irrelevant. Carrying it replicated the entire
problem `NH` times. Removing it took the solve from 9.7 s to 1.5 s with **byte-identical**
aggregates — SUD rate and drug participation matched to all printed digits, which is the
check that it was genuinely redundant. Reinstate it if moving costs are ever added.

**2. The expectation is precomputed once per age.** In the original the next-period
expectation is rebuilt inside the `a'` loop (lines 9552–9705), so it is recomputed once per
current asset gridpoint. The transition kernels do not depend on current assets except
through the binary voucher-eligibility indicator, so two copies suffice rather than `NA`.
The build is staged: integrate over `y'` first (independent of every choice), then over
`(e', d', η')`.

**3. Exact regime decomposition replaces the coarse-then-refine search.** The objective is
not single-peaked in `a'` — voucher eligibility is a step function of income (which includes
`r·a`), the food-stamp floor kinks, and housing is discrete. Within a regime (drug regime ×
treatment × housing) the c/v split is closed-form Cobb-Douglas, so `a'` is searched exactly
on the full grid and the max is taken over the handful of regimes. No unimodality
assumption, so none of the basin-hopping failure that makes `coarse_grid=1` disagree with
the full grid in the original.

**4. Powers hoisted out of the inner loop.** The nested Cobb-Douglas collapses to
`c**α · h**β · (v+b)**γ`; the housing and Stone-Geary powers are precomputed, and `σ = 2`
is special-cased so the CRRA transform is a reciprocal rather than a `pow()`.

## Two Fortran traps worth knowing about

Both cost real debugging time here.

**Module parameters named `J` collide with loop variables named `j`.** Fortran is
case-insensitive, so a local `integer :: j` *shadows* a use-associated `J`, and
`do j = J, 1, -1` silently starts from an uninitialized value. The symptom was a solve that
returned in 0.000 s leaving `V = 0`, and a segfault under OpenMP when the garbage index ran
off the end of `V`. Age parameters are now `n_age`, `j_ret`, `j_exp`.

**Do not list collapsed loop variables in an OpenMP `private` clause.** They are private by
default; naming them explicitly is non-conforming and segfaults under gfortran.

## Model summary

State `(j, a ≥ 0, y, e, d, η)` — 4,320 per age, 259,200 total.

Relative to the original: no homeownership, tenure choice, mortgages or negative assets; no
housing-market GE (rent is a fixed price); no UI-expiration state. Added: endogenous
treatment take-up, imperfect sobriety detection with false positives, an internalised
homelessness externality, and a drug price that is an equilibrium object.

Preferences do **not** depend on SUD status (single `theta_v`). The addict/experimenter
expenditure gap is therefore a prediction rather than an assumption: an agent with SUD faces
no further addiction risk, so their drug choice is static at the Cobb-Douglas optimum, while
a clean agent restrains to stay below `vbar` and avoid the jump to `pi_d_high`.

Switches for the mechanism-decomposition arms are `on_mortality_d`, `on_employment_d` and
`on_homeless_fb` in `params.f90`.

## Next

1. Equilibrium loops: τ_ℓ from the government budget, `p_v` from drug-market clearing,
   bequests. With ~1.5 s per solve, 30 outer iterations is under a minute.
2. Calibration.
3. Counterfactuals and welfare.
