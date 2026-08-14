# The intuition model

A three-period model to sit in front of the quantitative one. Solvable by hand, dynamic
rather than static, and it delivers the paper's three claims as propositions.

R1's objection to the current Appendix A is precisely that it "derived results in very
specific static settings, while the main model is dynamic," so a second static model would
not answer it. Three periods is the minimum that makes the value of life a real object and
lets the homelessness feedback loop appear.

---

## Setup

Three periods, `t = 1, 2, 3`. A household has permanent income `y`, distributed on
`[y_low, y_high]`. No savings — the point is the drug/housing/mortality interaction, not
consumption smoothing, and dropping assets is what keeps it closed-form.

**Preferences.** Within a period, over non-drug consumption `c`, housing `h` and drugs `v`:

```
u(c, h, v) = ( c^(1-θ_h) h^θ_h )^(1-θ_v) (v + b)^θ_v  ,  transformed by CRRA
```

plus a flow value of being alive `ℵ`. This is the quantitative model's period utility,
unchanged, so the two models speak the same language.

**Timing.**

- **t = 1.** The household chooses `v ≥ 0`. Using leads to substance use disorder (SUD) at
  `t = 2` with probability `π`.
- **t = 2.** SUD carries three penalties: mortality `δ_d`, elevated unemployment (hence
  elevated homelessness risk), and — under Treatment First — loss of the housing voucher.
- **t = 3.** Continuation. Recovery from SUD happens with probability `ρ(h₂)`, which is
  *lower if homeless at t = 2*. This is the channel that makes t = 3 necessary.

**Policy.** A voucher worth `W` in utility terms (housing stability). It is rationed: an
eligible household receives it with probability `π_V`.

- **Housing First:** receipt is independent of drug use.
- **Treatment First:** receipt requires sobriety.

`π_V` is *generosity* — the benchmark has `π_V ≈ 0.27`, universal provision is `π_V = 1`.
Conditionality is the HF/TF switch. **The paper's contribution is that these two are
separate dimensions, and that they interact.**

---

## Proposition 1 — mortality reverses the income gradient of drug use

Let `G(y)` be the period-1 utility gain from choosing `v` optimally rather than abstaining,
and let `Δ(y)` be the expected loss in continuation value from becoming addicted. A
household uses iff

```
G(y)  >  π · Δ(y).
```

**Claim.** `G(y)` is decreasing in `y` while `Δ(y)` is increasing in `y`, so there is a
single crossing `ŷ`: households use iff `y < ŷ`. Drug use concentrates at the *bottom*.

**Why `G` falls with income.** Under CRRA with `σ = 2` the flow utility is `-1/comp`, and
the gain from adding drugs is

```
G(y) = 1/comp₀ − 1/comp₁ = (1/comp₀)·(1 − comp₀/comp₁).
```

`1/comp₀ ∝ y^(-α)`, and the bracket tends to a constant. So `G(y) ∝ y^(-α)` — the *utility*
gain from drugs shrinks as consumption rises, because marginal utility is falling.

**Why `Δ` rises with income.** The loss from a truncated life is the continuation value
itself, `V(y) ≈ ℵ·E[remaining life] + w(y)`, which is increasing in `y`.

The ratio `π·Δ(y)/G(y) ∝ y^α · V(y)` is therefore strictly increasing: rich households have
more to lose and less to gain. **This is the reversal the paper claims, and it holds without
any ex-ante preference heterogeneity.**

### The proposition tells you when it fails, and that is the useful part

The reversal needs `Δ(y)` to rise fast enough. If `ℵ` is small, `V(y)` is dominated by the
flow term, which is *bounded above* under CRRA — so `V` is nearly flat in income, `Δ` barely
rises, and the gradient does **not** invert.

This is not hypothetical. Scanning `ℵ` in the quantitative model:

| ℵ | participation | use, low | use, mid | use, high |
|---|---|---|---|---|
| 1 | 90.9% | 96.8% | 96.8% | 96.8% |
| 40 | 78.8% | 91.5% | 91.5% | 91.4% |
| 150 | 59.7% | 80.0% | 80.0% | 80.0% |
| **600** | **26.1%** | **54.6%** | **35.3%** | **19.1%** |

The gradient only inverts once `ℵ` is large. **So the VSL target of $7.5m is not a
normalisation — it is the parameter that generates the paper's central mechanism.** That is
worth saying out loud in the paper: it answers R3's request to "explain how [drug-use
patterns] depend on model parameters, notably `b`, the Stone-Geary parameter, and `ℵ`," and
it converts an innocuous-looking calibration choice into a headline modelling result.

**Second failure mode, also worth stating.** If `b` is large, the interior optimum
`v* = γ/(α+γ)·(y + p_v b)/p_v − b` is negative for low `y`: poor households are *mechanically*
excluded from an interior solution, and the gradient turns upward regardless of mortality.
`b` must be small for Proposition 1 to have any force. This is why the paper calibrates `b`
"very small," and it deserves a sentence explaining that it is a substantive restriction
rather than a numerical convenience.

---

## Proposition 2 — the cross-partial. This is the paper.

Consider the deterrent that conditionality creates: the difference in expected voucher value
between abstaining and using.

| | abstain | use |
|---|---|---|
| Housing First | `π_V · W` | `π_V · W` |
| Treatment First | `π_V · W` | `0` |

So

```
D(π_V, TF)  =  π_V · W · 1{TF},        ∂D/∂π_V = W · 1{TF} > 0.
```

**The deterrent from conditioning on sobriety is linear in the generosity of the benefit
being conditioned.** Equivalently

```
∂² (drug use) / ∂π_V ∂(TF)  <  0.
```

**In words: a guaranteed voucher is a much bigger stick than a lottery ticket.** Under
rationing at `π_V ≈ 0.27`, the expected penalty for using is about a quarter of `W`, so TF
barely bites. Under universal provision the penalty is the whole of `W`.

### Why the cost does not scale the same way

The obvious objection is that the *cost* of TF — non-compliant households losing housing —
should also rise with `π_V`. It does not, and the asymmetry is the result:

```
cost  ≈  π_V · W · μ(π_V),     where μ = mass still using under TF.
```

`μ` is *decreasing* in `π_V`, by Proposition 2 itself. Generosity strengthens the deterrent,
which shrinks the population that bears the cost. **Generosity makes conditionality both
more effective and cheaper.**

That single mechanism explains the whole pattern in the quantitative results, which
currently reads as four disconnected experiments:

- rationed TF vs rationed HF → weak deterrent, cost falls on a large non-compliant group →
  TF loses (Experiment 1)
- universal TF vs rationed HF → maximal deterrent, small non-compliant group → TF wins
  (Experiment 4)

---

## Proposition 3 — the feedback loop amplifies both

This is why the model needs a third period. Let recovery at `t = 3` occur with probability
`ρ(h₂)`, lower when homeless. Then

```
SUD at t=2  →  unemployment ↑  →  homeless at t=2  →  ρ ↓  →  SUD persists at t=3.
```

The expected duration of SUD is therefore longer than `1/ρ` would suggest, so `Δ(y)` in
Proposition 1 is *larger* than the one-period penalty implies. Two corollaries:

1. The income-gradient reversal is stronger than a two-period model would predict.
2. The deterrent in Proposition 2 is stronger, because the thing being deterred is more
   costly. **Conditionality and the feedback loop are complements.**

It also delivers the paper's answer to the RCT literature for free: housing responds within
one period, SUD only over two, so a short-horizon experiment detects the housing effect and
misses the addiction effect regardless of the true long-run treatment effect.

---

## How this reframes the paper

Currently the contribution reads as "a large model, four experiments." With this section it
becomes:

> a general principle about conditional transfers — *the deterrent value of conditionality is
> increasing in the generosity of the benefit being conditioned* — proved in a transparent
> model, measured in a calibrated one, and applied to a live policy debate.

Say explicitly that the quantitative model exists to measure **magnitudes** and the fiscal and
equilibrium feedbacks. The **signs** come from here. That directly answers the AE's central
complaint that "the economic messages of the paper are lost within long-lists of model
features," and R2's "black box."

### Optional, cheap, and persuasive

Calibrate the three-period model roughly and show it reproduces the sign pattern of the
quantitative model — including the `ℵ` threshold in Proposition 1. It costs almost nothing
and it demonstrates that the big model is doing what the small one says it should.

### What stays in the appendix

The tightened static derivation, relabelled as intuition rather than as a general proof of
the model's mechanism — which is exactly what R1 asked for in comment 1(e). Do not delete it.
