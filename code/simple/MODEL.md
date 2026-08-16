# The simplified model: what is written, and how it gets calibrated

Overview of `code/simple/`. The original `../housing_first_or_treatment_first_SR_v1.f90`
is untouched and remains the homeownership version for the appendix.

---

## 1. The model

### State — 6 variables, 4,320 points per age

| | Symbol | Points | Notes |
|---|---|---|---|
| Age | `j` | 60 | real age 26–85, retire at 66 |
| Assets | `a ≥ 0` | 60 | cubic spacing, dense near zero |
| Productivity | `y` | 9 | Rouwenhorst on AR(1), ρ=0.9, σ=0.2 |
| Employment | `e` | 2 | employed / unemployed |
| SUD status | `d` | 2 | clean / SUD |
| Voucher | `η` | 2 | held / not |

**Housing entered with is deliberately not a state.** Survival, employment transitions and
the recovery hazard all condition on the *chosen* `h'`, and renters face no adjustment cost,
so the unit you arrive in is payoff-irrelevant. Verified empirically: removing it left every
aggregate byte-identical while cutting the solve from 9.7 s to 1.5 s.

### Choices

`h'` ∈ {homeless, 3 rental sizes} × drug regime ∈ {abstain, light, heavy} ×
treatment ∈ {0,1} × `a'` on the full 60-point grid.

### What was dropped, and on whose authority

| Dropped | Requested by |
|---|---|
| Homeownership, tenure choice, mortgages, negative assets | AE |
| Housing-market GE — house prices *and* rents | AE |
| UI-expiration state | AE |
| Type-dependent bequests | AE |
| 4 of 7 housing sizes | R2 |
| Addiction-dependent Cobb-Douglas weights | R2, R3, AE |

### What was added

| Added | Requested by |
|---|---|
| Endogenous treatment take-up raising the recovery hazard | R1 1(b), AE — *the* damning gap |
| Imperfect sobriety detection + false positives | R1 4(a),(b) |
| Drug price as an equilibrium object | R1 1(c), R3, AE |
| Homelessness externality *inside* period utility | R2, replaces κ_cons |

### Preferences — fixed across SUD status

```
u = [ c^α · h^β · (v+b)^γ ]  with  α=(1-θ_h)(1-θ_v),  β=θ_h(1-θ_v),  γ=θ_v
```

A single `θ_v` for clean and SUD agents alike. This is the change that makes the
addict/experimenter expenditure gap a **prediction** rather than an assumption:

- An agent **with SUD** faces no further addiction risk (the recovery hazard depends on
  housing, not on `v`), so their drug choice is *static* — the unconstrained Cobb-Douglas
  optimum, expenditure share `θ_v`.
- A **clean** agent restrains, because crossing `v̄` jumps the hazard from `π_low` to
  `6.48 × π_low`. They bunch at or below `v̄`.

The 4× gap between the 44% and 11% expenditure moments then emerges from forward-looking
behaviour. It also kills R2's "bakes in an income-contingent gain/loss from becoming
addicted" and R3's "reducing addiction mechanically raises consumption utility" at once.

**The commitment this makes:** all private cost of SUD now runs through mortality,
unemployment and resource diversion. Absent those, becoming addicted would *relax* a
constraint. That is internally consistent with the paper's thesis but sharper than the
current specification — and it makes the mortality-shutdown arm decisive rather than
marginal.

### Equilibrium — three objects, no housing market

| Clears | How |
|---|---|
| `τ_ℓ` | government budget, closed form given the distribution |
| `p_v` | drug market, `p_v = ψ₁ · V^(ψ₂−1)` |
| bequests | assets of the deceased redistributed to survivors |
| `H_agg` | fixed point, since it enters utility (only when `κ_ext > 0`) |

**The drug supply is exactly as you specified it.** Cost `C(V) = ψ₁/ψ₂ · V^ψ₂`, so the
supply elasticity is `1/(ψ₂−1)`. `ψ₁` is normalised at the benchmark so `p_v = 1` there —
which preserves the existing normalisation and means nothing in the current calibration
shifts — and `ψ₂` is set from the empirical supply elasticity. Only counterfactuals move the
price. This answers R3's worry that endogenising `p_v` "requires suppressing this
normalization": it does not, because you normalise `ψ₁` instead.

Same functional form as the rental company being deleted, so it is a swap, not added
complexity.

---

## 2. How it is solved

Backward induction, one exact pass. Four things carry the speed:

1. **The expectation is precomputed once per age**, staged so `y'` integrates out first
   (independent of every choice), then `(e', d', η')`. The original rebuilds this *inside*
   the `a'` loop, so it is recomputed once per current asset gridpoint. Current assets enter
   the kernels only through the binary voucher-eligibility indicator, so two copies suffice
   rather than 60.

2. **Exact regime decomposition** replaces coarse-then-refine. The objective is *not*
   single-peaked in `a'` — voucher eligibility is a step function of income (which includes
   `r·a`), the food-stamp floor kinks, housing is discrete. Within a regime the c/v split is
   closed-form Cobb-Douglas, so `a'` is searched exactly on the full grid and the max taken
   over regimes. **This is why the coarse-grid disagreement disappears rather than getting
   patched** — there is no unimodality assumption left to violate.

3. **Housing entered with is not a state** (above) — 6.6×.

4. **Powers hoisted** out of the inner loop; `σ = 2` special-cased to a reciprocal.

### Measured, 4 cores, gfortran 13.3 `-O2`

| | |
|---|---|
| One household solve | **1.42 s** |
| Distribution | 0.01 s |
| One full stationary equilibrium (44 iterations) | **67 s** |
| Thread scaling | 4.52 / 2.36 / 1.42 s on 1 / 2 / 4 |

For contrast, the original does not finish a single backward pass in four minutes here.

---

## 3. The calibration plan

### Structure

The parameter-to-moment map is close to triangular — each internally calibrated parameter
dominates one moment. So rather than a simplex search in 15 dimensions, sweep parameters one
at a time in the known direction of their own moment gap and repeat. This is the same
"adjuster" idiom the original code uses, reorganised so the whole set is one visible table
with the sign of `dM/dparam` declared explicitly. A wrong sign shows up immediately as a
moment walking away from its target.

### Current block — 8 parameters, 8 moments

| Parameter | Primary moment | Target | Sign |
|---|---|---|---|
| `b_sg` | drug participation | 4.0% | − |
| `pi_d_low` | SUD rate | 2.0% | + |
| `h_homeless` | homelessness rate | 0.3% | + |
| `pi_eu_base` | unemployment rate | 4.9% | + |
| `kappa_ue_d` | unemployment rate given SUD | 26.9% | − |
| `recover_mult_hl` | SUD share of the homeless | 37% | − |
| `prob_V` | voucher recipients / eligible | 26.6% | + |
| `theta_v` | drug spend / income given SUD | 44% | + |

Inner equilibria are solved loosely (tol 3e-3, ≤20 iterations) while parameters are still
moving by percent, then tightened once for the final report. Step size backs off
multiplicatively whenever a sweep fails to improve the worst gap.

### Still to add

- `beta` → wealth/income ratio
- `vbar`, and the light-experimenter share (0.87)
- `aleph` → VSL of $7.5m
- `theta_h` → rent-to-income 0.33
- `kappa_phi_d` → **the drug-price participation elasticity of −0.63**, which now requires
  perturbing `p_v` and re-solving — cheap at 1.4 s per solve, and it is the moment R1 said
  was not replicable
- **The elasticity of drug use with respect to housing access** — R2, R3 and the AE all name
  this as *the* key elasticity and it is currently untargeted. Milby et al. (2005) plus the
  HF RCT literature
- **Constantini's HF-vs-TF mortality difference**, which is the first thing to check and the
  one that could overturn the headline

### Honest cost estimate

At ~67 s per equilibrium, a 25-sweep calibration is roughly 25 minutes on 4 cores. Adding
the remaining 7 parameters and the two elasticity moments (each of which needs extra solves
at perturbed prices) puts a full calibration in the low hours — an overnight job here, well
under an hour on 40 cores. That is the whole point of the rebuild.

---

## 4. Status

**Working:** household problem, stationary distribution, aggregates, equilibrium loops,
calibration sweep framework.

**Not yet written:** the full parameter block, welfare (consumption-equivalent), the four
counterfactuals, the mechanism-decomposition arms (switches exist in `params.f90` but
nothing drives them), transition paths.

**Not yet meaningful:** every number the model currently prints. Parameters are placeholders
and the calibration has not converged. Do not read the aggregates as results.

---

## 5. Two Fortran traps, both hit here

**Fortran is case-insensitive, and this has now bitten four times.** `J`/`j`,
`M`/`mom`, `r`/`R` and `Phi`/`phi`. The `r`/`R` one is the instructive case: a
local `real(dp) :: R` in `solve_household` silently captured every `r*a_grid(ia)`
in that routine, so capital income was read from an uninitialised variable and
then from whatever the previous asset iteration left behind. It compiled, it ran,
and it produced plausible numbers. **Module-level names are now long enough that
nothing shadows them by accident** — `r_free`, `n_age`, `j_ret`, `j_exp`, `mom`,
`dist_t` — and any new one should follow.

**Module parameters collide with loop variables — Fortran is case-insensitive.** A local
`integer :: j` shadows a use-associated `J`, so `do j = J, 1, -1` silently starts from an
uninitialized value. Symptom: a solve returning in 0.000 s leaving `V = 0`, then a segfault
under OpenMP once the garbage index ran off the end of the array. Age parameters are now
`n_age`, `j_ret`, `j_exp`; the moment array is `mom`, not `M`, for the same reason.

**Never list collapsed loop variables in an OpenMP `private` clause.** They are private by
default; naming them explicitly is non-conforming and segfaults under gfortran.
