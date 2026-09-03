# The productivity process, and how it differs from the original

Written 3 September, answering the author: *"Can you explain to me how you did
it relative to the code I originally gave you? Because I had some process there.
I know you pick the dispersion to match the share of income of the bottom 50% of
the income dist. But how do you do the productivity transmission across
generations and the persistence for the household itself?"*

## What the code does now

`KKK_process` and `get_probabilities_KKK_process` take four numbers, all handed
in on every point:

    persistence_fixed_employment_newborn   rho_alpha = 0.5    intergenerational
    sd_fixed_employment_newborn            sd_alpha  = 0.309
    persistence_employment_surviving       rho_eta   = 0.9    within a life
    sd_employment_surviving                sd_eta    = 0.2

and build ONE log-productivity dimension whose variance evolves with age:

    var_fix    = sd_alpha^2 / (1 - rho_alpha^2)     = 0.12731
    var(1)     = sd_eta^2 + var_fix                 = 0.16731
    var(a)     = rho_eta^2 * var(a-1) + sd_eta^2

The grid runs +/- s_deviation * sd(a) at each age, so it FANS OUT with age, and
`kkk_sigma_scale` multiplies the whole thing -- that is the dispersion
instrument, pointed at sigma_y, the bottom half's share of labour income.

## THE TWO THINGS THE AUTHOR IS ASKING ABOUT, AND BOTH ARE WEAKER THAN THEY LOOK

### 1. There is NO intergenerational transmission of productivity

`rho_alpha = 0.5` appears in exactly one place: sizing `var_fix`, the stationary
variance of an AR(1) in the fixed effect ACROSS generations. It sets how
DISPERSED newborns are. It never correlates a child's draw with its parent's.

A newborn's node is drawn from `unconditional_employment_probability` -- the
unconditional distribution -- with no conditioning on the parent at all. The
model does track `newborn_parent_share(employment_index, addicted, homeless)`,
but that is used only for the child's ADDICTION and HOMELESSNESS penalties,
never for productivity.

So if the original code passed the parent's fixed effect to the child with
persistence 0.5, that link is gone.

### 2. The "fixed" effect is not fixed. It decays at 0.9 a year.

Collapsing the two components to one dimension folds the fixed effect into the
AGE-1 VARIANCE and then lets the single AR(1) govern everything after. So the
initial draw is forgotten:

    rho_eta^39 = 0.0164

**1.6 per cent of a household's initial condition survives to the last working
age.** The variance converges to sd_eta^2/(1-rho_eta^2) = 0.21053 and var(40) is
0.21051 -- fully converged, which is the same statement.

A genuine fixed effect persists for life by definition. This one does not, so
permanent inequality in the model is carried entirely by the AR(1)'s own
stationary variance and not by any household-specific permanent component.

## What this costs, concretely

- **Lifetime earnings inequality is understated relative to a fixed-effect
  process**, because a household that starts poor does not stay poor.
- **Social security is computed from `employment_grid` at the LAST working
  age** -- the type retired as -- so with the initial draw forgotten, a
  household's pension is nearly independent of where it started.
- **The child's penalty channel is the only intergenerational link in the
  model**, and it runs through addiction and homelessness, not income.

## What would restore it

Two separable changes, both the author's call:

1. **Draw the newborn's node conditional on the parent's**, with persistence
   `rho_alpha`. The machinery to know the parent's node already exists --
   `newborn_parent_share` is accumulated at every point.
2. **Keep the fixed effect as a second dimension** rather than folding it into
   the age-1 variance, so it persists for life. That is a state-space change and
   is much the more expensive of the two.

The first is cheap and restores intergenerational transmission. The second is
what makes "fixed" mean fixed.
