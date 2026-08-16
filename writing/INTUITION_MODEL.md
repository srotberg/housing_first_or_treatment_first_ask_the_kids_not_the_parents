# Intuition and mechanisms: one model, not two

**Decision: there is no separate computational toy model.** The analytical section proves what
can be proved on paper; everything numerical happens in the simplified calibrated model.

---

## 0. Why not a separate three-period model

An earlier version of this plan proposed a standalone three-period model with assets to
demonstrate the income gradient. That is redundant, for three reasons.

**R1 asked for it in the baseline model, explicitly.** Comment 1(d):

> A simple way to do this would be to compare the relationship between income and drug use in
> **the baseline model** to an otherwise similar version of the model in which mortality is
> not affected by drug use. **I would find this more intuitive than a toy example that
> abstracts from dynamic savings decisions.**

A toy model is the thing he said he would find *less* convincing.

**The simplified model already is the small model.** It solves in 1.4 s on four cores, and it
carries assets, income risk, a borrowing constraint, and the full policy structure. A separate
model would duplicate all of that and then invite the question of whether the two agree.

**Two models means two calibrations.** Every parameter would need a mapping, every result a
consistency check, and any disagreement between them becomes a referee's paragraph.

### What a toy model genuinely cannot be replaced by

One thing: a **proof**. Proposition 2 below is a theorem about expected voucher values. It is
established by two lines of algebra, needs no assets and no computation, and cannot be
"demonstrated" by simulation. That stays analytical — but it is half a page, not a model.

---

## 1. The analytical section (short)

Two results, derived in a stripped-down version of *the same* model with the simplifying
assumptions stated explicitly, and labelled as intuition rather than as general proof — which
is exactly what R1 comment 1(e) asks for.

### 1a. The drug-use threshold

A household uses iff `G(y) > π·Δ(y)`, where `G` is the period utility gain from using and `Δ`
the expected loss in continuation value from SUD. Under CRRA with `σ = 2`,

```
G(y) = 1/comp₀ − 1/comp₁ = (1/comp₀)·(1 − comp₀/comp₁)  ∝  y^(−α),
```

so the *utility* gain from drugs shrinks as consumption rises, while `Δ(y) ≈ V(y)` rises. The
ratio `π·Δ/G ∝ y^α·V(y)` is increasing: single crossing, use concentrated at the bottom, with
no ex-ante preference heterogeneity.

**State the two conditions under which this fails** — both are real and both are now
documented numerically:

- **`ℵ` must be large.** Under CRRA the flow term is bounded above, so with small `ℵ` the
  continuation value is nearly flat in income, `Δ` barely rises, and there is no reversal.
- **`b` must be small.** If `b` is large the interior optimum
  `v* = γ/(α+γ)·(y + p_v b)/p_v − b` is negative at low `y`, so poor households are
  *mechanically* barred from an interior solution and the gradient turns upward regardless of
  mortality.

### 1b. Proposition — the generosity × conditionality cross-partial

The deterrent conditionality creates is the gap in expected voucher value between abstaining
and using:

| | abstain | use |
|---|---|---|
| Housing First | `π_V · W` | `π_V · W` |
| Treatment First | `π_V · W` | `0` |

```
D(π_V, TF) = π_V · W · 1{TF},     ∂D/∂π_V = W · 1{TF} > 0
⟹  ∂²(drug use) / ∂π_V ∂(TF) < 0.
```

**A guaranteed voucher is a much bigger stick than a lottery ticket.** At `π_V ≈ 0.27` the
expected penalty for using is a quarter of `W`; universal, it is all of `W`.

**The cost does not scale the same way.** TF's cost is borne by non-compliant households:

```
cost ≈ π_V · W · μ(π_V),     μ = mass still using under TF,
```

and `μ` is decreasing in `π_V` by the proposition itself. **Generosity makes conditionality
both more effective and cheaper.** This explains the whole pattern that currently reads as
four disconnected experiments: rationed TF has a weak deterrent and a large non-compliant
group, so it loses; universal TF has a maximal deterrent and a small one, so it wins.

This result needs no assets and no calibration, so the paper's central contribution rests on
its most robust component — worth saying explicitly.

---

## 2. The mechanism section: the shutdown ladder, in the calibrated model

Shut channels off one at a time, **recalibrate `b` in each arm to hold drug participation at
its baseline value**, and report both what `b` had to become and who uses drugs.

| Arm | Shut off | Isolates |
|---|---|---|
| 0 | — | baseline |
| 1 | `κ_φd = 1` | SUD → mortality: the value-of-life channel, the headline claim |
| 2 | `κ_ue,d = 1` | SUD → employment: **R1's rival hypothesis** |
| 3 | `κ_φh, κ_ue,h, ρ_homeless = 1` | the homelessness feedback loop |
| R | restore `θ₁,₂ > θ₀,₂` | robustness against the old preference spec |

Arm 2 is the one that matters most. R1's alternative is that "the labor-market and income-risk
consequences of drug use could also generate a low-income concentration of drug use." That
channel operates through precautionary saving against a borrowing constraint — both of which
the simplified model has. So the arm is a genuine test, not a strawman.

### Two numbers per arm, and the first one is new

**How far `b` had to move** measures *how much* deterrence the channel was providing. If
removing mortality forces `b` up by an order of magnitude to restore 4% participation,
mortality was carrying the deterrence. If `b` barely moves, it was not.

**The income gradient** measures *whom* it deterred — drug-use rate by income decile, one line
per arm.

Level and composition, separately identified. The recalibration is what makes the composition
comparison meaningful at all: without it, removing the mortality penalty just raises drug use
everywhere and the level change swamps any compositional change.

### Reporting

- Drug-use rate by income decile, one line per arm — **the money figure**. Baseline slopes
  down; if the claim holds, Arm 1 flips it upward and Arm 2 does not.
- Per arm: recalibrated `b`, mean user income relative to average (the statistic R1 attacked —
  41% model vs 74% data), share unemployed, share homeless, mean age, mean assets.
- **Experimenters and those with SUD reported separately.** Experimentation is the decision
  margin and the clean test; SUD is a stock that also reflects differential mortality and
  recovery, so shutting off SUD-mortality changes its composition partly mechanically.
- Drug-use policy functions over `(assets, income)`, separately for `d = 0` and `d = 1` —
  R2's request, verbatim.

### On `b` as the normaliser

`b` is not neutral: by the paper's own argument it governs the no-penalty gradient, which
slopes *upward*, and the penalties reverse it. So recalibrating `b` adjusts the very object
that determines the counterfactual gradient. Handle it openly:

1. Report both un-normalised (headline level effect: "removing mortality raises participation
   from 4% to X%") and normalised (composition). The pair is more informative than either.
2. Confirm the gradient flip survives a second normaliser. `π_d,low` is the candidate, since
   it shifts the transition rather than preferences and so does not mechanically re-rank who
   wants drugs.

### Risk

If Arm 1 does not flip the gradient, the central claim is wrong. But if Arm 2 turns out to do
the work, the framing shifts from *value of life* to *value of future resources* — more
general and more robust. The paper survives either result. What it cannot survive is a referee
running the experiment in his head and not believing the answer.

---

## 3. Robustness arm worth adding: a usage-independent addiction hazard

Replace the step function `π_d(v)` with a single probability of developing SUD conditional on
any use. This is cheap (collapses `NREG` from 3 to 2) and directly answers R1 comment 4(d) on
sensitivity to the addiction transition.

**Run it as robustness, not baseline**, because it costs something specific: the bunching at
`v̄` is what currently generates the experimenter expenditure share endogenously, so that
moment would need to be targeted another way.

---

## 4. How this reframes the paper

> a general principle about conditional transfers — *the deterrent value of conditionality is
> increasing in the generosity of the benefit being conditioned* — proved in half a page,
> measured in a calibrated model, applied to a live policy debate.

The quantitative model measures **magnitudes** and the fiscal and equilibrium feedbacks; the
**signs** come from §1. That answers the AE's complaint that "the economic messages of the
paper are lost within long-lists of model features," and R2's "black box."

**Appendix A:** tightened, relabelled as intuition rather than as a general proof of the
model's mechanism — R1 comment 1(e). Demote it, do not delete it.
