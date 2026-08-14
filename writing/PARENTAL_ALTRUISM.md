# Parental anxiety about children: how to make it endogenous

R2's second welfare channel:

> parents suffer anxiety that their children may become drug addicts and/or
> homeless in adulthood... as soon as parents value the well being of their
> children this additional welfare consideration would arise... the dynastic
> element seems like more of a stretch, but could be discussed (I think it would
> only amplify the welfare gains from reducing addiction).

---

## 1. The distinction that matters

**A warm-glow term is not endogenous.** Adding `ν · E[V₁(child)]` to the parent's
value, where the child's type is drawn from an exogenous distribution, changes
welfare *levels* and changes the *policy comparison* (because V₁ differs across
regimes) — but it does not change any parent's decision, because no parent can
influence the draw. It is welfare accounting.

**For the channel to be endogenous, the parent's own choices must move the
child's outcome.** Then a parent contemplating drug use internalises the harm to
their child, and the anxiety becomes a deterrent rather than a bookkeeping entry.

That is the version worth building, because it is the version that changes the
paper's mechanism rather than just its welfare arithmetic.

---

## 2. The cheap way to do it — no new state variable

The obvious implementation is to give the child a "parent had SUD" tag. That is a
new binary state, doubling the state space (12,960 → 25,920 per age) and roughly
doubling solve time. Avoidable.

**Route the transmission through the mental-health state the model already has.**

```
parent has SUD at the child-bearing age
        ↓
child's INITIAL probability of serious mental illness is higher
        ↓
child has lower b (more tempted), lower SUD recovery hazard,
worse employment, lower income
        ↓
child is more likely to develop SUD and to become homeless
```

Every link after the first already exists and is already calibrated. The only
new object is the initial condition: the newborn distribution over mental health
becomes a function of the parent generation's SUD rate rather than a constant.

**Cost: zero extra state space, one new equilibrium fixed point** — and the model
already has three of those (bequests, `p_v`, `H_agg`), so the machinery is there.

### Why the mechanism is defensible, not just convenient

The epidemiological pathway is the documented one: parental SUD → childhood
adversity → mental illness → offspring SUD. The search evidence notes each
childhood adversity carries roughly 34% higher odds of developing a disorder,
and parental SUD is associated with offspring mental health problems
independently of offspring SUD. So transmitting through mental health is closer
to the actual mechanism than a direct SUD-to-SUD tag would be.

---

## 3. What disciplines it

**The transmission strength has a real target.** Adult children of parents with
severe alcohol use disorder have roughly **twice** the hazard of SUD after full
adjustment for confounders. Unadjusted hazards are much larger — 4.6 for opioid,
5.0 for volatile solvent, 5.3 for other stimulant use disorders — but the
adjusted figure near 2 is the right one for a model that already contains the
income and employment channels those adjustments control for.

So: **calibrate the elevation in the child's initial SMI probability so the model
reproduces an offspring SUD hazard ratio of ≈ 2.** One parameter, one moment,
and the moment is a published estimate rather than something invented.

**The altruism weight ν has no clean target, so do not pretend otherwise.**
Report it as a bound instead:

- **ν = 0 recovers the current model exactly.** So every welfare result the
  paper reports is a *lower bound* on the gain from reducing addiction.
- Any ν > 0 strengthens the case for policies that reduce SUD.

That is precisely R2's own prediction — "it would only amplify the welfare gains
from reducing addiction" — turned into a formal statement rather than a
conjecture. It is the same bounding logic that R1 forced onto κ_cons, applied
before a referee has to ask.

---

## 4. What it buys the paper

**It amplifies the headline result, and it does so through a new channel.**
Universal TF cuts SUD by a large margin; with transmission, that reduction
propagates to the next generation's mental health, and thence to their SUD and
homelessness. The welfare gain compounds across generations rather than
accruing once.

**It fixes the AE's complaint A6** — that §4.1.3 discusses intergenerational
transmission while the model has no intergenerational linkage. Right now ρ_x =
0.5 is specified and then never used, because newborns draw productivity from
the unconditional distribution. This makes an intergenerational link
load-bearing.

**It gives the deterrent an extra term.** The private cost of drug use becomes
mortality + unemployment + resource diversion + *harm to one's child*. That
raises Δ(y) in the income-gradient argument and strengthens the conditionality
deterrent — both propositions in `INTUITION_MODEL.md` get stronger.

---

## 5. Implementation sketch

1. **Child-bearing age** `j_kid` — a single model age, say 30.
2. **Newborn mental-health distribution** becomes
   `P(SMI at birth) = smi_prevalence · (1 + λ · SUD_rate(j_kid))`,
   normalised so the unconditional prevalence still matches NSDUH. `λ` is the
   transmission parameter, calibrated to the offspring hazard ratio of 2.
3. **Parent's Bellman at `j_kid`** gains `ν · E[V₁(child state)]`.
4. **New fixed point:** the newborn SMI share depends on the SUD rate at `j_kid`,
   which depends on behaviour, which depends on the newborn distribution. Solve
   it alongside bequests — same damped iteration.
5. **Report** the policy results at ν = 0 (the bound) and at one or two positive
   values, showing the direction and rough magnitude.

---

## 6. Recommendation

**Build it, but keep it in its place.** R2 called the dynastic element "a
stretch" and asked only that it be discussed. What makes it worth more than a
paragraph here is that the cheap implementation costs no state space and the
transmission strength has a published target — so it is not the parameter-fishing
exercise that a full dynastic model would be.

Present it as: baseline results at ν = 0, an explicit statement that these are a
lower bound on the welfare gain, and one robustness row with ν > 0. That answers
R2 fully, converts his conjecture into a result, and closes the AE's A6 — without
turning the paper into a dynastic-altruism paper.

**Do not** build a full altruistic bequest model. That would change savings
behaviour at every age, require its own calibration target, and put the paper's
core mechanism at the mercy of a literature it does not otherwise engage.

---

## Sources

- [Risk of substance use disorders in the adult children of parents with severe alcohol use disorder: a nationwide cohort study](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12723945/)
- [Parental and own substance use disorder: the intersection of gender and early adversity](https://pmc.ncbi.nlm.nih.gov/articles/PMC9018609/)
- [Parent-child separation and intergenerational transmission of substance use and disorder across three generations](https://pmc.ncbi.nlm.nih.gov/articles/PMC10368792/)

Figures are from search-result summaries; the primary domains are blocked from
this environment, so verify before the numbers enter the draft.
