# The homelessness externality

R2's first missing margin, and the one he said to build:

> a large homeless population, **especially if many are addicted to drugs**,
> creates a negative externality beyond the fiscal burden of providing services
> ... the externality seems very easy to introduce into the current model
> (though would require a new calibration moment)

---

## 1. Is it endogenous? Yes — in the sense that matters

```
disutility = kappa_ext * ( H_agg + omega_ext * HD_agg )
```

`H_agg` is the homelessness rate; `HD_agg` is the share of the population both
homeless and with SUD. Households take both as given.

**Taking them as given is what makes it an externality.** If a household
internalised its own contribution it would be a private cost, not a spillover,
and the wedge between private and social returns to policy would vanish — which
is the entire reason for including it.

But the aggregates are equilibrium objects:

- they are determined by behaviour and solved as a fixed point, alongside
  bequests and the drug price;
- they enter **period utility**, so they enter the value function, so they change
  the value of life, so they change drug-use decisions;
- policy moves them, and that feeds back into behaviour, not only into welfare
  arithmetic.

**This is the property κ_cons lacked.** R1 comment 3(a) objected that the
loss-of-consortium adjustment "is not formally integrated into the model... these
losses should in principle affect the value of life and agents' decisions."
Here they do. The objection does not apply.

## 2. Composition, not just level

R2's phrasing is specific — "especially if many are addicted to drugs" — so the
disamenity is weighted by composition through `omega_ext`, rather than depending
on the headcount alone. This matters for the policy comparison: TF and HF change
the *composition* of the homeless population, not only its size, so a
level-only externality would miss part of the welfare difference between them.

## 3. Calibration: there is no credible point estimate, and pretending otherwise
would repeat the κ_cons mistake

What exists, and why none of it is clean:

**Hedonic property-value studies.** The National Association of Realtors has
suggested a shelter in a residential neighbourhood can lower nearby property
values by around 12.7%, and there is evidence of negative effects in Manhattan.
Three problems: these measure the local disamenity of a *specific facility*, not
the economy-wide *rate*; siting is endogenous, so the estimates are confounded;
and results vary widely, with some jurisdictions finding no discernible effect.
A model without geography cannot map a local hedonic gradient onto an aggregate
rate without a strong and unstated assumption.

**Voted spending and ballot measures.** Large approved bonds and levies reveal
aggregate willingness to pay. But voted spending mixes altruism toward the
homeless, disamenity avoidance, and beliefs about fiscal cost — and the model
already carries the fiscal cost separately as `chi_H`, so using the total would
double-count.

**Stated-preference surveys** on willingness to pay for Housing First exist but
are weak evidence for a welfare parameter that moves a policy ranking.

### So: report it as a bounded sensitivity

1. **`kappa_ext = 0` is the conservative baseline.** Critically, **zero is
   defensible here** — it simply means no externality — whereas `κ_cons = 0` was
   the value R1 pointed out reversed the paper's conclusion. The externality can
   only *strengthen* the case for policies that reduce homelessness, so the
   baseline results are a lower bound.
2. **Report the policy ranking across a range** of `kappa_ext`, and state the
   threshold at which any conclusion changes — the same discipline R1 forced onto
   κ_cons ("the ranking is preserved as long as...").
3. **Anchor the range** by reporting, for each value, the implied
   consumption-equivalent cost of the benchmark homelessness rate. That converts
   an opaque parameter into a number a reader can judge: "at this value,
   households would give up X% of consumption to eliminate homelessness." A
   referee can then decide whether X is plausible without needing an estimate of
   `kappa_ext` itself.

Point 3 is the substantive move. It does not manufacture an estimate that does
not exist; it makes the assumption legible.

## 4. Why this is a better answer than κ_cons on every count

| | κ_cons | this externality |
|---|---|---|
| Requested by a referee | no | **yes** (R2) |
| Has a literature | no | yes (Corbae, Glover and Nattinger) |
| Internalised in the value function | **no** — R1 3(a) | yes |
| Affects behaviour | no | yes |
| Zero is defensible | **no** — reverses the conclusion | yes — it is the lower bound |
| Free parameters | 1, unbounded | 2, reported as a range |

---

## Sources

- [Corbae, Glover and Nattinger, *Equilibrium Evictions*, NBER WP 32898](https://www.nber.org/papers/w32898) ([KC Fed version](https://www.kansascityfed.org/documents/9505/rwp23-03corbaeglovernattinger.pdf))
- [Sitti, Horn and Berrens, *The Effect of Homeless Shelters on Property Values*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5239331)
- [Willingness-to-pay for Housing First across 8 European countries — survey protocol](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6260705/)

The Corbae et al. specification could not be read directly — nber.org,
econ.rutgers.edu and the KC Fed PDF are all blocked from this environment. **It
is worth checking how they specify and discipline their housing externality
before settling this**, since R2 named that paper as the reference.
