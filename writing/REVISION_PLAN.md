# Housing First or Treatment First? — Assessment and Revision Plan

Notes on the RED R&R decision (RED-D-26-00078, reject with door left open) and a
proposed rebuild of the quantitative model.

---

## 1. Read of the decision

Karabarbounis rejected but explicitly invited "an almost new paper," with a promise to
return it to the same AE and the same referees. That is a real option, not a polite
brush-off. Three signals support taking it:

- The AE letter is a **roadmap**, not a dismissal. It is unusually specific about what a
  successful revision looks like, and it leads with "the main contribution of this paper
  would be to provide a detailed model-based evaluation ... This is the major selling
  point." The AE likes the question.
- R3 recommends revision. R2 is on the fence but calls the model "very rich" and its
  exposition clearer than İmrohoroğlu–Zhao. Only R1 recommends rejection, and R1's
  report is the most detailed and constructive of the three — that is an engaged referee,
  not a hostile one.
- Nobody attacked the question, the framing, or the contribution claim. Every objection is
  about *execution*: identification, model fit, policy modeling, and complexity.

**The one-line diagnosis, on which all three referees and the AE agree:** the paper is a
large model carrying a small amount of identification. The fix is not to add more
machinery. It is to cut ruthlessly, and spend the freed budget disciplining the three or
four elasticities the policy conclusion actually turns on.

That is exactly the direction of the "simplify the model" instinct. The plan below goes
somewhat further than dropping homeownership, because the AE explicitly licenses more.

---

## 2. The one thing to resolve before investing months

The AE writes:

> Constantini (2025) finds for a sample of 300,000 Veterans that Housing First reduces
> three-year mortality by 4.6 percentage points while Treatment First has no long-term
> health effects, **in contrast with the model simulations of this paper**.

This is the most dangerous sentence in the whole file, because the paper's headline result
runs *through mortality*. Universal TF only beats universal HF once loss-of-consortium
mortality spillovers are added (Table 9). If the best quasi-experimental evidence says HF
saves lives and TF does not, the central welfare ranking is contradicted by the evidence
the model should be matching.

There is a good defense, and it should be made loudly and early — but it is only a partial
defense:

- **What Constantini studies is Experiment 1**, i.e. HF vs TF holding rationing fixed. In
  that comparison the paper *already agrees* with the evidence on the housing and welfare
  margins: TF raises homelessness ~17% and lowers welfare ~0.4%. The paper's novel claim
  is about *universal* TF, which Constantini does not study. Say this explicitly.
- **But the mortality sign still conflicts.** In Experiment 1 the model has population
  *rising* 0.23% under TF (fewer deaths, via less addiction), whereas Constantini has HF
  reducing mortality. The model's addiction→mortality multiplier (κ_{d,φ} = 6.9) is doing
  far more work than its homelessness→mortality multiplier (κ_{h,φ} = 1.6). The relative
  strength of those two channels is precisely what determines the paper's answer, and it is
  currently disciplined by two separate literatures that were never reconciled.

**Action, and do this first:** re-target the model so that Experiment 1 reproduces
Constantini's 3-year mortality difference between HF and TF. This is a cheap experiment on
the *existing* code — it is a re-calibration of two multipliers, not a rebuild. Two
outcomes:

- The universal-TF ranking survives → the paper is now *validated against* the AE's own
  cited evidence, and the single strongest objection becomes a selling point.
- The ranking flips → far better to learn this in a week than after a six-month rebuild,
  and the paper becomes "generosity dominates conditionality," which is still publishable
  and arguably a more interesting result.

Do not start the rebuild before running this check.

---

## 3. What to cut

The instinct to remove homeownership is right, and the AE explicitly asks for it ("Why do
we need the role of homeownership, and not simply the difference between homelessness and
houses?"). But the AE licenses considerably more cutting than that, and each cut below is
requested by name in one of the four documents.

| # | Cut | Requested by | What it buys |
|---|-----|--------------|--------------|
| 1 | **Homeownership and tenure choice** | AE | Deletes state `o`, the entire owner branch, the 61-point negative asset grid, LTV constraint, selling costs, depreciation, and house price `p_h` |
| 2 | **Housing-market GE (`p_h` *and* `p_r`)** | AE | Deletes construction firm, rental company, γ₁, γ₂, two market-clearing conditions, and two targets (rental supply elasticity, rent-to-price ratio) |
| 3 | **UI expiration (state `κ`)** | AE | Collapses the (e, κ, d) grid from 6 to 4 |
| 4 | **Type-dependent bequests ϑ(x,z)** | AE | Replace with uniform lump sum; removes a GE fixed point |
| 5 | **Housing grid 7 sizes → 2–3** | R2 (grid is unjustified, only 3 of 7 calibrated) | Cuts the choice set ~2× |
| 6 | **Loss-of-consortium adjustment κ_cons** | AE, R1 3(a)(b)(c) | See below — this is the highest-value cut in the table |
| 7 | **Counterfactuals in the body: 4 → 2** | AE ("first and third experiment ... most relevant") | Pure writing win |

Cut #2 deserves emphasis because it is counterintuitive. The AE writes: *"Why does the
policy analysis require a full general equilibrium model? Many long-run partial equilibrium
outcomes appear nearly identical to the general equilibrium ones. Do account for the changes
in the government, and ideally for the adjustment in drug prices ... not necessarily in
terms of housing prices and rents."* The AE is asking to trade two equilibrium prices you
currently solve for (p_h, p_r) for one you do not (p_v). That is a strict computational win
*and* a responsiveness win.

Cut #6 also deserves emphasis. R1 called κ_cons "plucked out of thin air," noted that a
genuinely conservative value would be zero, and observed that it flips the policy ranking —
which is fatal for a headline claim. The AE offers the escape hatch: *"present the policy
consequences along two different dimensions, the welfare consequences of equation (30) and
the mortality consequences."* Report CE and lives saved as two separate columns and let the
reader weigh them. This costs nothing computationally, removes a free parameter, kills three
of R1's numbered objections at once, and forces the honest statement that the conclusion
softens to *"universal TF dominates on addiction, homelessness, mortality, and fiscal cost;
universal HF wins narrowly on direct newborn welfare."* That is a defensible claim. The
current one ("the debate is resolved in favor of universal TF") is not — R1 said so directly.

---

## 4. What must be added

These are not optional. Each is flagged by at least two of the four documents.

**1. Endogenous treatment / recovery.** This is the single most damning critique and it is
essentially unanswerable in the current setup: the policy is called *Treatment First* and
the model contains no treatment. Recovery is exogenous and random, so TF operates only
through the eligibility margin, never through the recovery margin. R1: *"One of the goals of
TF as a policy is to encourage addicts to seek treatment ... this mechanism is ruled out in
the model."* The AE: *"The policy itself has a direct role in impacting the transition out of
addiction."* Note R1 expects this to **strengthen** TF — so this addition works in the
paper's favor. Minimum viable version: a binary treatment/effort choice for those with SUD
that raises the recovery hazard at a utility or resource cost, which TF subsidizes or
mandates. Adds one binary choice, not a state variable.

**2. Drug price p_v adjusts in counterfactuals.** R1 1(c), R3, AE. Currently p_v ≡ 1 and
never moves, yet the calibration targets a *price* elasticity — R3 flags the internal
tension directly. One scalar in the outer loop, replacing two you deleted. Price feedback
plausibly *offsets* TF's reduction in drug use, so this is a real robustness risk worth
knowing about.

**3. Imperfect detection of drug use.** R1 4(a),(b). TF currently assumes sobriety is
perfectly observed and perfectly enforced. Add a detection probability p < 1 and a false
positive rate. This is a modification of the voucher transition kernel only — no new state,
no new cost — and it is the kind of realism that converts a referee.

**4. Mental health.** R1 1(a), and R1 is explicit that its absence is not neutral: *"mental
health contributing to drug use and addiction as well as homelessness would weaken TF
dramatically as a policy."* A referee who believes an omitted mechanism biases the result
toward the paper's conclusion will not clear it. Add it as a persistent binary state that
raises drug-use propensity, lowers employment, and lowers the recovery hazard.

Two notes. First, this doubles the state space — add it **only after** the simplified core
is fast, exactly as sequenced below. Second, there is a bonus: a chronically mentally ill
group that does not age out of homelessness is the natural fix for R1 2(c)(ii), the finding
that the model puts 73.1% of the homeless in ages 26–44 against 48.1% in the data. One
addition, two objections answered.

**5. Model fit column in Table 2.** R1 2(a). Trivial, and non-negotiable — its absence is
what caused R1 to lose confidence in the entire quantification. Report model moments beside
data moments for all 22 targets.

**6. Target the elasticity of drug use with respect to housing access.** R2, R3, and the AE
all name this as *the* key elasticity, and it is currently untargeted. R2: *"all of the
welfare results rest on whether the model has an accurate elasticity of drug use to housing
access."* Sources: Milby et al. (2005), plus the HF RCT literature already cited in the
intro. Pair it with the elasticity of homelessness with respect to addiction (AE).

**7. Numerical identification evidence.** R1 2(f), which was complimentary about the
existing verbal argument in Section 4.2 and just wants it shown numerically. Cheapest
credible option: perturb each parameter locally and plot the moment responses. The
Andrews–Gentzkow–Shapiro sensitivity matrix is the fuller answer if the solve is fast.

**8. Proper transition paths.** R1 3(d) calls the current several-period PE adjustment "a
half-measure." This is only feasible because of the cuts in §3 — with no housing market to
clear along the path, a transition requires iterating on τ_ℓ and p_v alone.

**9. A stylized model in Section 2.** R1 1(e), R3, and the AE all ask. See §6 — this is
more valuable than it sounds.

**10. Connect to the recent empirical and structural literature.** Constantini (2025),
Cohen (2024), Brounstein and Wieselthier (2026), Abramson (2026), Humphries et al. (2026),
Abramson and van Nieuwerburgh (forthcoming) on fiscal costs of homelessness. Also revisit
the χ_H = 25.2% of average income figure, which both R2 and R3 independently judged too
high, and source the "37% of homeless have SUD" figure precisely with an explicit
homelessness definition (AE).

**11. Terminology.** Replace "addicted" with "suffering from substance use disorder"
throughout (AE). Mechanical, and signals responsiveness at zero cost.

---

## 5. The proposed state space, and whether it will run on 4 cores

The proposed minimal state — age, non-negative assets, labor productivity, SUD status,
unemployment — is close to right but is missing two states that cannot go:

- **Housing status `h`** must stay. Mortality, employment transitions, and the recovery
  hazard all condition on it, and `h'` is the central choice. But it shrinks from 8 points
  (homeless + 7 sizes) to 3–4 (homeless + 2–3 rental sizes).
- **Voucher receipt `η`** must stay, because receipt is persistent and that persistence is
  the entire mechanism by which TF's threat operates.

So the minimal state is **(j, a ≥ 0, x/z, e, d, h, η)** — seven, of which age is trivially
sequential. Mental health makes eight.

Worth noting: renters in the current code already carry only non-negative assets (indices
61–151 of the 151-point grid). Dropping ownership therefore deletes the 1–60 range and the
entire owner block outright, rather than requiring any redesign of the asset grid.

### Indicative state counts, per age

| Version | Per-age states | vs. current |
|---|---|---|
| Current (renters 91×6×9×8×2, owners 151×6×9×2) | ≈ 95,000 | 1× |
| Simplified core (45 × 9 × 4 × 4 × 2) | ≈ 13,000 | 7× smaller |
| + mental health | ≈ 26,000 | 3.7× smaller |
| + treatment state (d ∈ {clean, SUD, SUD-in-treatment}) | ≈ 39,000 | 2.4× smaller |

The state count is not the real constraint, though — the **choice set** is. It falls from
a'(151) × h'(8) × o'(2) × v × ℓ to a'(45) × h'(4) × v × ℓ, and the tenure choice with all
its buy/sell/mortgage branching disappears entirely.

### Implement it as a compile-time switch, not a deletion

Homeownership should be gated behind a flag rather than stripped out, so it can be turned
back on for a robustness appendix or if a referee insists. The code already uses exactly
this idiom — `include_addiction`, `include_vouchers`, `only_LTV`, `coarse_grid` — and, more
usefully, the renter/owner split is *already* structurally separated: 74 `do i=1,2` loops
where `i=1` is the renter branch and `i=2` the owner branch, with array bounds already
driven by an `is_owner` flag at allocation.

So the change is small and mechanical:

```fortran
integer, parameter :: include_homeownership=0

! 1. Tenure: collapses all 74 owner/renter loops. `do i=1,2` -> `do i=1,tenure_grid_size`
integer, parameter :: tenure_grid_size=include_homeownership*2+(1-include_homeownership)*1

! 2. Mortgage grid: renters already index negative_financial_grid_size:financial_grid_size,
!    so setting the negative block to 1 leaves 91 non-negative points with index 1 = zero
integer, parameter :: negative_financial_grid_size=include_homeownership*61+(1-include_homeownership)*1

! 3. Housing sizes: homeless + 3 rental sizes instead of homeless + 7
integer, parameter :: housing_status_grid_size=include_homeownership*7+(1-include_homeownership)*4
```

Because these are `parameter` (compile-time) constants, gfortran dead-code-eliminates the
owner branches and the arrays physically shrink at compile time — there is no runtime cost
to carrying the switch, and setting `include_homeownership=1` restores the current model
exactly. This is strictly better than deleting the code. The one thing to verify is that
the `financial_grid` construction routine behaves when the negative block has length 1.

Turning it off also removes, for free: the LTV constraint, mortgage amortization and
insurance, `cost_of_selling`, owner-occupied depreciation, the buy/sell branching in the
Bellman operator, the construction firm, and `p_h` from the outer equilibrium loop.

### Where the speedup actually comes from

The intuition that "a lot of stuff gets faster" is right, and it compounds multiplicatively
because each cut hits a different nested loop:

| Source | Factor |
|---|---|
| Tenure choice `o'` gone (74 loops halve; no buy/sell branch) | ~2× |
| Asset grid 151 → 91 (mortgage block gone) | ~1.7× |
| Housing grid 8 → 4 points | ~2× |
| Per-age states 95k → 39k | (already counted above) |
| `p_h` out of the outer GE loop | ~1.3–2× on the equilibrium solve |

Compounded, that is roughly **15–25× fewer Bellman evaluations per equilibrium**, before
any of the algorithmic changes below. Those changes are what take it the rest of the way.

### Three algorithmic changes that matter more than the state count

1. **Exploit the step structure of addiction risk.** π_d(v) is a step function with a single
   threshold v̄. So solve three *smooth* subproblems — v = 0, v ∈ (0, v̄], v > v̄ — and take
   the max. This converts a non-concave search over v into three well-behaved problems and
   is likely the largest single win available.
2. **Use monotonicity of a'(a).** In finite-horizon VFI the savings policy is monotone in
   assets; carrying the previous gridpoint's optimum as a lower bracket turns an O(N²)
   search into roughly O(N). Consider EGM for the c/a' margin conditional on discrete
   (h', v-regime).
3. **Coarse-grained OpenMP.** With only 4 cores, parallelize the outer state loops
   (productivity × employment × SUD), not the inner ones. The `-fopenmp` flag is already in
   the build line.

On labor supply, there is a genuine conflict: the AE asks what role it plays, while R3 is
*surprised* it does not matter more for the welfare cost of financing via labor taxes.
Recommendation: keep it, since taxes are the financing margin and R3 will notice if it
vanishes, but put it on a coarse 3–5 point grid.

### Targets to aim for

| | Target on 4 cores |
|---|---|
| One stationary equilibrium | ≤ 60–90 seconds |
| Full calibration (~12–15 internal parameters) | overnight |
| One transition path (~150 periods, clearing τ_ℓ and p_v only) | ≤ 1 hour |

If a single equilibrium solve lands inside ~90 seconds, everything the referees asked for —
transitions, sensitivity analysis, the AGS matrix, robustness on imprecisely measured
targets (R1 2(f) flags the −0.36 to −0.9 price elasticity range specifically) — becomes
routine rather than heroic. That, not elegance, is the reason to simplify.

---

## 6. The stylized model is the highest-value addition

R1, R3, and the AE all ask for it, and the existing Appendix A does not satisfy them —
R1 calls it "disorganized and narrower than the surrounding discussion suggests," deriving
results in static settings while the main model is dynamic.

But there is a much better reason to write it than referee compliance. **The paper's actual
contribution is a proposition, and it is currently buried in Table 8.** The headline finding
is not "TF good" or "HF good" — it is that *the deterrent value of conditionality is
increasing in the generosity of the benefit being conditioned*. A guaranteed voucher is a
much bigger stick than a lottery ticket, which is why universal TF beats rationed TF on
addiction while rationed TF loses to rationed HF. That is a cross-partial:
∂²(deterrence)/∂(generosity)∂(conditionality) > 0.

That is provable in a two-period model with no computation at all. It reframes the entire
paper from "here is a big model, here are four experiments" to "here is a general principle
about conditional transfers, verified quantitatively in a calibrated model, applied to a
live policy debate." It also directly answers the AE's core complaint that "the economic
messages of the paper are lost within long-lists of model features."

Suggested Section 2: a two-period model delivering (i) the income gradient of drug use
requires the mortality penalty to scale with continuation value — this is the current
Appendix A result, tightened; and (ii) the generosity × conditionality cross-partial. Then
state clearly that the quantitative model exists to measure the magnitudes and the fiscal
and equilibrium feedbacks, not to establish the sign.

---

## 7. Two fit problems that the rebuild should be designed around

R1's Table 3 objections are the ones most likely to sink a resubmission, because they
concern exactly the states that discipline the mechanism.

**All homeless are unemployed with ~zero income in the model, against 40–52% unemployed and
19% of average income in the data.** Homelessness is currently a pure corner of the income
distribution. The fix is a shock that puts non-corner people on the street: a transitory
expense/eviction shock, or a rent shock. Without it, as R1 puts it, the model "may evaluate
HF and TF at the wrong margins" — and since voucher eligibility, tax payments, and the
fiscal gains from employment all key off income, this is not cosmetic.

**Model puts 73.1% of the homeless in ages 26–44 vs 48.1% in the data, with only 9.3% aged
55+ vs 27.1%.** Agents age out of homelessness too readily. As noted in §4, the mental
health state is the natural fix, since chronic mental illness generates exactly the
persistent, older homeless population the model is missing.

Design the simplified model to hit these two from the start rather than patching afterward.

---

## 8. Suggested sequencing

1. **Week 1 — the Constantini check.** Re-target κ_{h,φ} and κ_{d,φ} on the existing code so
   Experiment 1 reproduces the HF-vs-TF 3-year mortality difference. Decide whether the
   headline survives. *Everything downstream depends on this.*
2. **Weeks 2–3 — the two-period model.** Prove the generosity × conditionality cross-partial.
   Cheap, and it determines how the whole paper is framed.
3. **Weeks 3–6 — strip the model.** Execute all seven cuts in §3. Verify the income gradient
   of drug use survives the loss of homeownership — this doubles as R1's requested 1(d)
   exercise (compare against a version with no mortality effect of drug use to show the
   value-of-life channel is the quantitatively important one).
4. **Weeks 6–9 — add back.** Endogenous treatment, p_v adjustment, imperfect detection. Then
   mental health, last, once the solve time is known.
5. **Weeks 9–12 — recalibrate and discipline.** Full fit table, the housing-access elasticity,
   numerical identification, sensitivity to the imprecisely measured targets.
6. **Weeks 12+ — transitions, two body experiments, rewrite.**

The rewrite is not a residual. The AE was blunt: *"One would have to rewrite this paper to
reflect insights rather than providing 5 pages describing 22 moments and parameters."*

---

## 9. Bottom line

Resubmit — but only after step 1 confirms the mortality ranking survives contact with
Constantini. The question is good, the AE wants the paper to exist, and the referee pool is
already invested. The cost is a genuine rebuild of roughly a quarter's work, which is what
"an almost new paper" means.

The simplification instinct is correct and should be pushed further than planned: drop the
housing-market GE along with homeownership, because the AE asked for it and it buys back
the compute needed to deliver the transitions, sensitivity analysis, and identification
evidence that the referees actually want. The model is not too complex for its own sake —
it is too complex to be *disciplined*, and that is the thing every one of these four
documents is really saying.

One expectation to set now: the headline will likely have to soften from "the debate is
resolved in favor of universal TF" to something like "generosity matters more than
conditionality, and conditionality only pays once the benefit is guaranteed." R1 asked for
exactly this softening. It is a better paper's thesis anyway, and it is the one the
two-period model actually proves.
