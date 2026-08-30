# The two period model: what to build

Design settled, not yet built. This is the spec, not a summary of work done.

## Why this and not the three period model

The reason drug spending comes out at 1.8 per cent of a user's income rather
than 11 is that the marginal cost of using is `lambda * exp(-lambda v) * dV`,
where `dV` is what the disorder destroys. In the three period model `dV` is two
periods of continuation and the survival penalty applies at BOTH transitions.
Cutting to one period and one transition takes `dV` down by something like a
factor of four, so the optimal `v` rises and `lambda` can be far smaller while
still hitting the progression target.

The earlier two period test in `two_period.py` collapsed, moral hazard from
+2.55 to +0.24, and it does **not** count against this design. There the disorder
was realised *in* the final period, so death cost nothing. Here it is realised in
the **transition**, with the mortality penalty applied on the way into period 2.
That is the fix.

The income gradient survives in structure. It works because `aleph`, the income
independent part of the continuation, does not shrink when consumption does, so
the rich lose proportionally more by dying. Halving the continuation scales the
income dependent and income independent parts together, so the ratio that drives
the gradient is untouched. Weaker in level, same in structure.

## The environment

**Period 1.** Household of permanent productivity `y`, clean. Employment
`e in {0,1}` is realised with the unemployment probability `u_0`; if unemployed it
receives income support. A voucher arrives with probability `pi_V` if income
eligible. It then chooses consumption, housing, drug use `v >= 0` and saving.

**The transition.** With probability `pi(v) = 1 - exp(-lambda v)` the household
acquires the disorder. Survival into period 2 is `phi(d) = phi_0 (1 - kappa d)`,
so the mortality penalty applies here and only here.

**Period 2.** Terminal. Employment is realised with `u_0` if clean and the higher
`u_1` if `d = 1`. The voucher is drawn again, subject to the policy rule. The
household chooses consumption and housing, runs assets down, bequeaths nothing.

Two changes from Section 2 of the note, both the author's: unemployment and the
voucher now operate in period 1 as well, not only later.

## What retires

`rho`, the recovery probability, stops meaning anything: there is no period to
recover into. Drop it from `P` and from the external table. It belongs in the
quantitative model, where treatment is a choice, and its absence here is easier
to defend than the current three period structure.

The whole "why there are three periods" paragraph in the note goes with it, and
is replaced by something better: the disorder is realised in the transition, so
mortality has something to destroy without needing a third period.

## Value functions

    W_2(a, y, e, eta, d) = max_j  { (1-gam-th) log c + gam log h_j + aleph }
                            s.t.  c = R a + y_e(y,e) - r_j(eta)

    W_2(a, y, d)         = E[ W_2(a,y,e,eta,d) | y, d ]      over e and eta

    V_1(y) = max_{j, v>=0, a'>=0}
             { (1-gam-th) log c + gam log h_j + th[log(b+v) - log b] + aleph
               + beta * phi(d') * E_{d'} W_2(a', y, d') }
             s.t.  c = R a + y_e(y,e) - r_j(eta) - p_v v - a'

with `d' = 1` with probability `pi(v)`. Note `phi` is inside the expectation over
`d'`, since survival depends on the realised disorder: the continuation is
`E_{d'} [ phi(d') W_2(a', y, d') ]`, not `phi * E W_2`. Getting that wrong is the
value of life pathology all over again.

Period 1 now integrates over `e` and `eta` too, so `V_1(y)` is itself an
expectation over the period 1 employment and voucher draws.

## Code changes

`stylized.py`

* `solve_late` becomes `solve_period2`, returning the period 2 value, street
  share, rent and voucher outlay on the asset grid, indexed by `d`. Delete the
  period 3 block entirely.
* `use_choice` and `value1` gain the period 1 employment and voucher draws, which
  means looping over `_states(par, 0, policy, y)` in period 1 rather than
  assuming employed, clean and uncovered.
* The continuation becomes `sum over d' of pi_d' * phi(d') * W_2(a', d')`.
* `aggregates` loses the period 3 accounting.
* Drop `rho`.

`calibrate.py`

* Targets unchanged except that `prog` now refers to the single transition, so
  the 33.2 per cent is the share of users who acquire the disorder at that
  transition, which is the same object.
* `lambda` should calibrate an order of magnitude lower than 131. If it does not,
  something is wrong with the continuation.
* Widen the `lambda` bracket downward to 0.05 and leave `theta` at 0.11
  initially. Do **not** free `gamma`: it collapses, twice tried.

## What to check first, before anything else

**Section 4, the channel decomposition.** Scale the mortality channel alone from
zero to its calibrated value with `b` refitted at every point, and the same for
unemployment. The result the model exists to demonstrate is that mortality
reverses the income gradient and a resource penalty does not. If both channels
end in the same place, the two period model has bought a spending share at the
cost of the paper's first result, and it should be abandoned exactly as the
`theta = 0.20` calibration was.

Only if that passes, look at the drug spending share.

Expected: `r_use` below one with mortality at full strength, above two with
unemployment at full strength, and a drug spending share somewhere between 5 and
15 per cent. Prior on it holding: about 60 per cent.

## What changes in the note

Section 1.2 timing, three paragraphs become two. The mortality paragraph loses
the three period justification and gains the transition argument. Section 1.4
Figure 1 numbers, Section 1.5 the policy experiment, Section 1.6 welfare and the
externality, all regenerate from `fill.py`. The external table loses `rho`.

Section 2, the quantitative model, is unaffected: it has sixty periods and the
comparisons in it are to the stylized model's mechanisms, not to its horizon.

## The wealth to income ratio, measured but not targeted

Asked for on 30 August and parked, so it is written down rather than recomputed.

The benchmark implies aggregate end-of-period-1 assets of 0.05943 against
aggregate period-1 income of 0.96683, a ratio of **0.0615 per period**. A period
is thirty years, so against an ANNUAL income flow that is **1.84**. The
quantitative model targets 3.0 for its own wealth-over-output and is banded
(3.0, 4.5), so the stylized model sits well below it.

Nothing targets this. It falls out of the saving policy, which is why it is low.
Two things would have to be settled before it could be calibrated to match:

- the annualisation is a CONVENTION applied here, not something the model
  states, and the raw model number is the per-period 0.0615;
- period 2 is terminal, assets are run down and nothing is bequeathed, so this
  is one cohort's peak saving and not a stationary stock. It is not the same
  object as the quantitative model's wealth over output even after annualising.

Recovered from `threshold()`, whose branch arrays carry a' in slot 0:
aggregate over income weights and state probabilities, mixing the use and
no-use branches by the cell's `frac`.
