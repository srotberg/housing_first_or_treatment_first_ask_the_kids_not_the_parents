# Moving the externality into the full model

Four changes. Two are already in the code and only need to be reported properly,
one is implemented here, one needs a decision before it can be written.

---

## 1. Transmission only, not the general disamenity

**Decision: drop `kappa_x` from the benchmark and keep it as an appendix
sensitivity at zero.**

The general disamenity is small and it is the weakest number in the paper.
Loubière et al. (2020) is the only credible source and, once the right mean is
used, it prices ending homelessness altogether at **€23 per adult per year, about
0.08% of average annual earnings** — the mean over all respondents, not the €57
mean among the 42.3% willing to pay anything. At the benchmark homelessness rate
that is a fraction of a percent of consumption, an order of magnitude below the
welfare differences the policy comparison turns on. It cannot move a ranking, and
carrying it forces a reference-rate normalisation (`H_ref`) that is the single
most consequential judgement in its own calibration.

The intergenerational channel is different: it is large, it has a clean target
(the transmission ratio), and it is the one that reverses the ranking in the
stylized model. So the benchmark carries `delta_d` and `delta_h` and sets
`kappa_x = 0`, with the disamenity reported as a sensitivity that can only
strengthen the case for whichever policy reduces homelessness more.

**Code.** `newborns_inherit_addiction` exists (line 68) but inherits *addiction
status*, which is the wrong channel — it has the wrong welfare sign for the same
reason a heritable taste does in the stylized model. What is needed is a shift in
the newborn's *productivity draw*:

```
x_child ~ Omega_x( x_parent ) shifted by (1-delta_d)^{1{parent was ever addicted}}
                                       * (1-delta_h)^{1{parent was ever homeless}}
```

Implemented as a shift in the newborn's draw **probabilities over the existing
productivity grid**, not as new grid points. Minting penalised types would
multiply the type space by four and give back the speed gained in §4.

This requires the parent's ever-addicted and ever-homeless indicators to be
carried into the newborn draw. They are not currently in the state, so they have
to be accumulated in the distribution rather than in the value function — which
is where they belong anyway, since the parent does not internalise them except
through altruism (§3).

---

## 2. Government budget and labour supply distortion

**Already in the model. No new work; the reporting changes.**

- `tau_l` is calibrated to an average labour income tax rate of 22.4%, and the
  budget already includes `omega_voucher`, `omega_food`, `chi_H` and `chi_D`.
- Labour supply is a choice with `omega_l = 8.5` targeting average time working
  of 40%.
- Experiments 1–4 already report `Average income tax (p.p. delta)` and
  `Labor supply (% delta)`.

What is missing is that these never appear in the welfare decomposition beside
the externality. The point of the full model over the stylized one is exactly
that conditionality is not free: it changes voucher outlay, which moves the tax
rate, which distorts hours and saving. Those terms need to sit in the same table
as the transmission gain so a reader can see the externality net of what paying
for it costs.

---

## 3. Parental altruism in the benchmark

### What it has to be

Not warm glow. A warm-glow bequest motive values the *transfer*, not the child's
situation, so a parent who becomes addicted and lowers its child's productivity
feels nothing. The term has to be **true altruism**: the newborn's expected
lifetime value enters the parent's objective at weight `omega`,

```
V_parent = ... + omega * E[ V_1( x_child ) ]
```

with `x_child` drawn from the shifted distribution of §1. Then the parent's drug
and housing choices carry an internal cost that rises with the probability of
addiction, exactly as in the stylized robustness check, and only `(1 - omega)` of
the damage is external.

### How to calibrate it credibly

**The identifying moment is the intergenerational transfer flow.** With
`include_bequest_motive = 0` today, bequests in this model are purely accidental.
Turning on altruism makes parents accumulate in order to pass wealth on, so
`omega` is identified by how large that flow is, given `beta`. This is the
standard approach in two-sided-altruism calibrations and it uses machinery the
model already has.

`beta` and `omega` are then jointly identified by two moments:

| parameter | moment | target |
|---|---|---|
| `beta` | net wealth / GDP | 3.25 (already used) |
| `omega` | intergenerational transfers / disposable income | **3% per year** |

The transfer target is from the Federal Reserve's SCF-based work: annual
inheritances plus inter vivos transfers averaged about **$350 billion (2016
dollars) per year over 1995–2016, roughly 3% of household disposable personal
income**. Since this model has bequests but no inter vivos margin, the model's
bequest flow is matched to the combined figure, which is the conservative
direction: it attributes the whole observed transfer flow to the one margin the
model has, so it cannot understate `omega`.

Cross-check, and it matters: **Altonji, Hayashi and Kotlikoff (1997)** reject
operative altruism at the margin. Redistributing a dollar from a recipient child
to a donor parent raises the transfer by **less than 13 cents**, against the
dollar full altruism implies. Note what this does and does not deliver. It is not
a point estimate of `omega` — in an interior altruistic transfer the derivative
is one for *any* `omega` — it is a rejection of the interior altruistic transfer
model itself. So it functions as a ceiling and a sanity check: a calibrated
`omega` anywhere near one would be inconsistent with it, and any calibration that
produces one should be treated as a failure of the calibration rather than a
finding.

A useful anchor for the order of magnitude is the pure generational discount: at
an annual `beta` of 0.99 over thirty years that is **0.29**, and the stylized
model's robustness check put the reversal threshold near 0.43. So the region that
matters is roughly 0 to 0.5, and the ranking has to be reported across it with
the threshold stated, the same discipline `kappa_cons` and `kappa_x` were held
to.

### What altruism does to the rest of the calibration

`delta_d` has to be **re-calibrated jointly with `omega`**, not held at its
current value. An altruistic parent uses less, so the transmission ratio the
model produces at a given `delta_d` falls. The pair `(delta_d, omega)` is
identified by the pair (transmission ratio, transfer flow).

---

## 4. Fixed permanent income, unemployment risk kept

**Implemented.** `fixed_productivity = 1` at line 68.

### What it does and does not do

The productivity dimension is **not removed**. It still carries the cross
sectional dispersion of permanent income and the intergenerational link, so
`employment_grid_size` stays at 9 and the value function is exactly the same
size. What changes is that the transition becomes the identity at every age
rather than only in retirement.

Two edits:

1. `GKKOC_intergenerational_employment_process` now runs the identity loop from
   age 1 instead of from retirement, and freezes `employment_grid` at its **mid
   working life** width. Freezing at the age-one width instead would quietly
   shrink income inequality and take the wealth targets with it; freezing at
   mid life keeps roughly the average cross sectional variance of log
   productivity and removes only the risk.

2. A zero-probability guard at the top of each of the five expectation nests in
   the Bellman loops:

   ```fortran
   if (employment_process(age_index,employment_index,future_employment_index)<=0.d0) cycle
   ```

   This is exact, not an approximation. With the identity transition eight of the
   nine branches carry zero mass, so the innermost nest shrinks by a factor of
   nine at every working age. It is also a free win when productivity is
   stochastic, since it prunes the near-zero tails of the Tauchen matrix.

### Expected gain, and the caveat

The innermost nest currently runs 9 (productivity) × addiction × unemployment ×
voucher branches per `a'` node, each doing a badly-strided read into a rank-7
array. Removing the factor of nine there should be worth **3 to 6× overall**.

The caveat is important and belongs in the paper: this is a **substitute for a
fix that is strictly better**. `PERFORMANCE_NOTES.md` §4 shows the expectation is
being recomputed inside the `a'` loop when it depends on neither current assets
nor `a'` except through the binary voucher-eligibility indicator. Hoisting it is
worth 10–50×, keeps the stochastic process, and makes the productivity collapse
worth almost nothing on top. **Do §4 first.** Fixed productivity should be
adopted because it makes the newborn externality tractable, not because it is the
cheapest way to buy speed.

### Why it makes §1 tractable

With a fixed type the child's penalty is a shift along a single scalar, so the
child's value is `V_1` evaluated at a different point of the same grid — exactly
the interpolation the stylized model does. With an AR(1) the parent's terminal
`z` is a random object reached by a whole history, the grid is age-varying
(`z_grid_by_age` widens with `variance_by_age`), and the penalty has to be
expressed as a shift across Tauchen nodes whose spacing changes with age. That is
the real reason to do it.

---

## 5. The disorder probability: open

`probability_of_becoming_addicted_if_experiment` and
`increased_probability_of_becoming_addicted_if_heavy_user` currently make the
addiction hazard a **step function of `v`** at the cutoff `v_bar`, with a
separate target (light experimenters / experimenters = 0.868) pinning the cutoff.

That step is one of the four sources of non-concavity in `a'` that
`PERFORMANCE_NOTES.md` §3 identifies as breaking the coarse-then-refine asset
search. Replacing it with a smooth hazard

```
pi_d(v) = 1 - exp(-lambda v)
```

would remove that non-concavity, retire `v_bar` and its target, and make the full
model's addiction technology identical to the stylized model's, which the note
now implicitly promises.

**This is my reading of the change and it is a guess.** Confirm before it is
written, since the alternative readings — smoothing the step but keeping the
light/heavy split, or changing the *level* of the hazard rather than its shape —
imply materially different work and different calibration targets.
