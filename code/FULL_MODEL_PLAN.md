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

**The identifying moment is the drug use gap between adults with and without a
child in the household.** This is the exact margin `omega` operates on in this
model: the only thing the weight does is make a parent use less than an otherwise
identical household without a child, because using raises the chance of a
disorder and the disorder lowers the child's permanent income. It is a revealed
behavioural moment from the survey the paper already uses for the participation
rate and for `u_1`.

Measured in NSDUH 2024 (`data/make_altruism_moment.py`), adults 26 and over,
weighted:

| | with a child | without | ratio |
|---|---|---|---|
| past month illicit use, raw | 16.34% | 16.63% | 0.983 |
| **past month, reweighted** | **14.11%** | **16.71%** | **0.845** |
| past year, reweighted | 20.34% | 25.14% | 0.809 |

The raw comparison shows nothing, and that is composition: parents are older,
richer and far more likely to be married. Reweighting parents to the non parents'
*joint* distribution over age, income, sex and marital status opens a gap of 2.6
percentage points. The age pattern is what makes it credible rather than
mechanical: the gap is widest at 35 to 49 (ratio 0.60) and 30 to 34 (0.71), the
child rearing window, and narrows at 50 to 64 (0.855) when children have left.

**The calibration condition.** Every household in the model has a child, so there
is no parent and non parent comparison to run directly. `omega` is the entire
reason a household here uses less than it otherwise would, so at the calibrated
parameters, switching altruism off must raise drug use by `1/0.845 - 1 = 18.4`
per cent.

**Run through the stylized model first, it gives `omega = 0.0137`** on the past
month moment and `0.0169` on the past year one (`code/stylized/altruism.py`).
That is a useful check on the whole strategy: the moment identifies `omega`
sharply, the answer is small, and the stylized model's ranking reverses back to
Housing First only near `omega = 0.43`, so the calibrated weight sits a factor of
thirty inside the region where the externality still decides the comparison.

**The caveat, which makes this an upper bound.** Selection runs the wrong way and
cannot be signed away: heavy users lose custody, so part of the gap is children
being absent from users' households rather than users cutting down for their
children. The measured gap is therefore an upper bound on what altruism explains
and zero is the lower bound, so the ranking is reported across that range with
the threshold stated.

**Why not the transfer flow, which was the earlier proposal.** It does not work
here. Estates in this model accrue to the government rather than to children
(change 11 in the revision list), so `omega` does not move saving at all and the
transfer flow cannot identify it. Restoring bequests to children only to identify
`omega` would undo a change made for a different reason.

Cross-check, and it matters: **Altonji, Hayashi and Kotlikoff (1997)** reject
operative altruism at the margin. Redistributing a dollar from a recipient child
to a donor parent raises the transfer by **less than 13 cents**, against the
dollar full altruism implies. It is not a point estimate of `omega` — in an
interior altruistic transfer the derivative is one for *any* `omega` — it is a
rejection of the interior altruistic transfer model itself, so it functions as a
ceiling. A calibrated `omega` near one would mean the moment is picking up
something other than altruism. At 0.014 it is nowhere near.

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

## 5. The disorder probability: smooth hazard, split dropped

**Decision taken: replace the light/heavy step with a hazard that is smooth in
`v`, and retire the split.** Two steps, and only the first is implemented.

### Step 1, done: the regimes are collapsed

`include_heavy_vs_light_use_transitions = 0`. The use decision
`future_addiction_index` now runs over {0, 1} rather than {0, 1, 2}, and the
`v_bar` truncation in the drug quantity block is guarded so it applies only while
the split exists. Without that guard the collapsed model would silently cap every
experimenter's drug spending at the retired threshold.

Retired with it: `v_bar` itself and its target, light experimenters over
experimenters = 0.868.

### Step 2, not done: make the hazard rise with `v`

`pi_d(v) = 1 - exp(-lambda v)`, with `lambda` calibrated to the moment the two
old probabilities jointly hit, experimenters over addicts = 1.

This is **not a one line change**, and the reason is worth being precise about.
`addiction_probabilities` is a precomputed rank-4 array indexed by
(current `d`, future `d`, **use regime**, homeless). Indexing by regime is exactly
what makes it precomputable. Once the hazard depends on the *quantity* chosen it
becomes state dependent, so it has to be evaluated inside the Bellman loop, where
the drug quantity is known but the array lookup currently is not. The five
expectation nests at lines 9694, 10086, 10636, 11045 and 11390, plus the
distribution at 13964, all read it by index.

### The speed claim needs a correction

I said this change removes a non-concavity and speeds the solver up. Removing the
step does remove one of the four non-concavities in `a'`. But there is a cost on
the other side that I had not checked and that changes the sign of the net
effect.

Drug spending is currently chosen in **closed form** from the static Stone-Geary
first order condition and then clipped to the regime. The household internalises
the addiction hazard only at the *regime* margin, never at the intensive one. A
hazard that rises with `v` puts the continuation value into the first order
condition,

```
theta / (b + v)  =  (1-gamma-theta)/c  +  lambda exp(-lambda v) [V(d=1) - V(d=0)] / u_c
```

which has no closed form and needs a numerical solve at every `(state, a', h')`
node. The bisection branch already in the code can carry it, but this is a real
cost, and it is plausibly larger than the gain from the removed step.

So: **do this for the economics, not for the speed.** It makes the full model's
addiction technology identical to the stylized model's, and it restores the
property the stylized note leans on, that the intensive and extensive margins are
not separate decisions. The speed comes from fixed productivity (section 4) and,
much more, from hoisting the expectation out of the `a'` loop
(`PERFORMANCE_NOTES.md` section 4).

There is a cheaper intermediate worth considering if the solve time bites: keep
`v` static optimal as it is today and let the realised hazard be
`1 - exp(-lambda v*)` at that quantity. That removes the step, retires `v_bar`,
keeps the closed form, and keeps the extensive margin internalised. What it gives
up is intensive margin internalisation, which the model does not have today
either. It is strictly closer to the stylized model than the status quo and costs
nothing.
