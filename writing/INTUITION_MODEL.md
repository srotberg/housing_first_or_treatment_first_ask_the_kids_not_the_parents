# The intuition model

A small three-period model to sit in front of the quantitative one. **It has assets, income
risk and a borrowing constraint** — see §0 for why that is not optional.

---

## 0. Why assets have to be in it

The first draft of this plan dropped savings to keep the model hand-solvable. That was
wrong, for a reason that matters.

**R1's objection to the current Appendix A is exactly that it has no savings.** Comment 1(d):

> The paper emphasizes mortality risk as the key mechanism generating drug use concentrated
> among low-income individuals. However, **in a dynamic model with savings, borrowing
> constraints, and income risk, it seems possible that the labor-market and income-risk
> consequences of drug use could also generate a low-income concentration of drug use.** ...
> I would find this more intuitive than **a toy example that abstracts from dynamic savings
> decisions**.

R1 is not making a stylistic point. He is naming a **rival hypothesis**: income risk plus a
borrowing constraint might produce the same downward gradient with no mortality channel at
all. That rival operates *entirely through precautionary saving*. A model without assets
cannot distinguish the two hypotheses, because it has assumed away the alternative it is
supposed to rule out.

R2 points the same way in his "black box" comment:

> it would be useful to show and explain intuitively a plot of the drug use policy function
> for addicts and non-addicts as **their income and wealth vary**.

And R1 comment 1(e) asks for the appendix to be "reorganized and made more precise ...
described more clearly as intuition rather than as a general proof," while the AE asks for a
stylized model showing "key static **and dynamic** mechanisms."

**Consequence for the design:** "simple" here means *few moving parts and fully transparent*,
not *hand-solvable*. Three periods with assets does not have a closed form. It solves
numerically in milliseconds, which is all that matters — it can be plotted, perturbed, and
have channels switched off one at a time, in a setting small enough to reason about
completely.

---

## 1. Setup

Three periods, `t = 1, 2, 3` — the minimum that makes the value of life a real object and
lets the homelessness feedback loop appear.

**State:** assets `a ≥ 0` (borrowing constraint binds — this is what makes precautionary
saving operative), permanent income `y`, employment `e`, SUD status `d`.

**Preferences.** The quantitative model's period utility, unchanged, so the two models speak
the same language:

```
u(c, h, v) = ( c^(1-θ_h) h^θ_h )^(1-θ_v) (v + b)^θ_v    under CRRA,  plus ℵ
```

**Timing.**

- **t = 1.** Choose `v ≥ 0` and `a₂ ≥ 0`. Using leads to SUD at `t = 2` with probability `π`.
- **t = 2.** Employment shock. SUD raises mortality `δ_d`, raises unemployment risk (hence
  homelessness risk), and — under Treatment First — forfeits the voucher. Choose `a₃ ≥ 0`.
- **t = 3.** Continuation. Recovery with probability `ρ(h₂)`, *lower if homeless at t = 2*.

**Policy.** A voucher worth `W` in utility terms, received by eligible households with
probability `π_V`. Under HF receipt is independent of drug use; under TF it requires
sobriety. `π_V` is *generosity* (benchmark ≈ 0.27, universal = 1); HF/TF is *conditionality*.

---

## 2. Proposition 1 — mortality, not income risk, reverses the income gradient

### The analytical intuition (stated honestly as intuition)

Ignoring savings for a moment, a household uses iff `G(y) > π·Δ(y)`, where `G` is the
period-1 utility gain from using and `Δ` the expected loss in continuation value from SUD.

Under CRRA with `σ = 2`, flow utility is `−1/comp`, so

```
G(y) = 1/comp₀ − 1/comp₁ = (1/comp₀)·(1 − comp₀/comp₁)  ∝  y^(−α).
```

The *utility* gain from drugs shrinks as consumption rises, because marginal utility falls.
Meanwhile `Δ(y) ≈ V(y)`, which is increasing in `y`. So `π·Δ/G ∝ y^α·V(y)` is strictly
increasing: the rich have more to lose and less to gain, and there is a single crossing.

**This is intuition, not proof** — which is precisely how R1 asked for it to be labelled.
The proof obligation is discharged numerically, below and in the full model.

### The demonstration that actually answers R1

With assets in the model, run three variants and plot drug use against income in each:

| Variant | Mortality effect of SUD | Employment effect of SUD | Question it answers |
|---|---|---|---|
| A | on | on | baseline — is the gradient downward? |
| B | **off** | on | **can income risk alone produce it?** |
| C | on | off | is mortality sufficient on its own? |

**Variant B is the whole point.** It is R1's rival hypothesis, instantiated. If the gradient
survives with mortality switched off, the paper's headline framing is wrong and the mechanism
is really about the value of future *resources*, not the value of *life*. If it flattens or
inverts, R1's alternative is ruled out in the simplest setting where it can be posed.

Because the model has a borrowing constraint, variant B genuinely has the precautionary
channel operating — which is exactly what the current appendix cannot claim.

### What the quantitative model already tells us to expect

Scanning `ℵ` in the full model, drug use by income tercile:

| ℵ | participation | low | mid | high |
|---|---|---|---|---|
| 1 | 90.9% | 96.8% | 96.8% | 96.8% |
| 40 | 78.8% | 91.5% | 91.5% | 91.4% |
| 150 | 59.7% | 80.0% | 80.0% | 80.0% |
| **600** | **26.1%** | **54.6%** | **35.3%** | **19.1%** |

The gradient only inverts once `ℵ` is large. Under CRRA the flow term is bounded above, so
with small `ℵ` the continuation value is nearly flat in income, `Δ(y)` barely rises, and
there is no reversal.

**So the $7.5m VSL target is not a normalisation — it is the parameter that generates the
paper's central mechanism.** That is worth stating plainly. It answers R3's request to
"explain how [drug-use patterns] depend on model parameters, notably `b` ... and `ℵ`," and it
turns an innocuous-looking calibration choice into a headline modelling result.

**Second failure mode.** If `b` is large, the interior optimum
`v* = γ/(α+γ)·(y + p_v b)/p_v − b` is negative at low `y`: poor households are *mechanically*
barred from an interior solution and the gradient turns upward whatever mortality does. `b`
must be small for Proposition 1 to have force. This is why the paper calibrates `b` "very
small," and it deserves a sentence saying so — it is a substantive restriction, not a
numerical convenience.

### And the figure R2 asked for

The same model produces it directly: the drug-use policy function over `(a, y)`, plotted
separately for `d = 0` and `d = 1`. That is R2's request verbatim, and it is far more legible
in a three-period model than in the full one.

---

## 3. Proposition 2 — the cross-partial. This is the paper.

The deterrent conditionality creates is the difference in expected voucher value between
abstaining and using:

| | abstain | use |
|---|---|---|
| Housing First | `π_V · W` | `π_V · W` |
| Treatment First | `π_V · W` | `0` |

```
D(π_V, TF) = π_V · W · 1{TF},        ∂D/∂π_V = W · 1{TF} > 0
⟹  ∂²(drug use) / ∂π_V ∂(TF) < 0.
```

**A guaranteed voucher is a much bigger stick than a lottery ticket.** At `π_V ≈ 0.27` the
expected penalty for using is about a quarter of `W`, so TF barely bites; universal, it is
all of `W`.

**This one survives without savings, and that is a feature.** `D` is a comparison of expected
voucher values; adding assets changes the *level* of `W` but not the linearity in `π_V`. So
the paper's central contribution rests on the most robust part of the argument — worth saying
explicitly, because it means the headline does not depend on the modelling choices R1 is
most sceptical of.

### Why the cost does not scale the same way

The obvious objection is that TF's cost — non-compliant households losing housing — must
also rise with `π_V`. It does not:

```
cost ≈ π_V · W · μ(π_V),      μ = mass still using under TF,
```

and `μ` is *decreasing* in `π_V` by Proposition 2 itself. **Generosity makes conditionality
both more effective and cheaper.** That single mechanism explains the whole pattern that
currently reads as four disconnected experiments:

- rationed TF vs rationed HF → weak deterrent, cost falls on a large non-compliant group →
  TF loses (Experiment 1)
- universal TF vs rationed HF → maximal deterrent, small non-compliant group → TF wins
  (Experiment 4)

---

## 4. Proposition 3 — the feedback loop amplifies both

Recovery at `t = 3` occurs with probability `ρ(h₂)`, lower when homeless. Then

```
SUD at t=2 → unemployment ↑ → homeless at t=2 → ρ ↓ → SUD persists at t=3.
```

Expected SUD duration exceeds `1/ρ`, so `Δ(y)` in Proposition 1 is larger than a one-period
penalty implies. Two corollaries: the gradient reversal is stronger than a two-period model
predicts, and the deterrent in Proposition 2 is stronger because what is being deterred is
more costly. **Conditionality and the feedback loop are complements.**

It also delivers the answer to the RCT literature for free: housing responds within one
period, SUD only over two, so a short-horizon experiment detects the housing effect and
misses the addiction effect regardless of the true long-run treatment effect.

---

## 5. How this reframes the paper

Currently the contribution reads as "a large model, four experiments." With this section:

> a general principle about conditional transfers — *the deterrent value of conditionality is
> increasing in the generosity of the benefit being conditioned* — proved transparently,
> measured in a calibrated model, applied to a live policy debate.

Say explicitly that the quantitative model measures **magnitudes** and the fiscal and
equilibrium feedbacks; the **signs** come from here. That answers the AE's central complaint
that "the economic messages of the paper are lost within long-lists of model features," and
R2's "black box."

**What stays in the appendix:** the tightened static derivation, relabelled as intuition
rather than as a general proof of the model's mechanism — exactly R1 comment 1(e). Do not
delete it; demote it.

**Division of labour on Proposition 1.** The three-period model with assets shows the
mechanism cleanly and rules out the precautionary rival in a transparent setting. The full
channel-shutdown ladder in the quantitative model then does it at the calibrated
parameterisation — which is what R1 actually asked for in 1(d). The small model motivates;
the big model demonstrates.
