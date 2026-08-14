# Housing First or Treatment First? — Revision Plan

RED-D-26-00078. Rejected, with an explicit invitation to resubmit "an almost new paper" to
the same AE and the same referees.

---

## 0. Compute: can this run here?

**Yes — but only after fixing the code, not by shrinking the model alone.** I compiled and
ran your model in this container. Findings are in `code/PERFORMANCE_NOTES.md`; the headline:

| Finding | Impact |
|---|---|
| **`readme.txt` compiles with no `-O` flag** — gfortran defaults to `-O0` | Likely **3–10×**, one-line fix |
| **Expectation recomputed inside the `a′` loop** (lines 9552–9705) | Plausibly **10–50×** |
| Model simplification (§2) | **15–25×** |
| `max_CPUs=40` hardcoded, overrides `OMP_NUM_THREADS` | Portability; 10:1 oversubscription here |
| **Coarse-grid mode has a real bug** — see below | Correctness |

These multiply. A solve currently measured in hours should land well under a minute, which
is the threshold where the entire revision runs interactively on 4 cores.

Measured baseline: compiles in 23 s; sustains ~360% CPU on 4 threads (parallelism is
healthy); 612 MB resident; roughly 4 *retirement-age* backward-induction steps in 3.5 min
wall / 12.5 min CPU. Retirement ages are the cheap ones.

### Why the coarse grid disagrees with the full grid

You were right that it is broken, and it is not a tolerance issue. `optimal_financial_1` is
initialized **once** (line 9471) outside both the addiction loop (9500) and the housing loop
(9519), but the refinement pass centres its search window on it. It is only updated on a new
**global** maximum (line 9715, inside the `largest_value` test), so for every branch after
the first, the refinement searches around *a different branch's optimum*. A branch whose
true optimum falls between coarse gridpoints and would have won is silently lost.

With `coarse_grid=0` the loop `do gsi=0,0` runs one exhaustive pass and the stale value is
never read — which is exactly why only coarse mode is wrong.

Separately, coarse-then-refine assumes unimodality in `a′`, and this model breaks it: voucher
eligibility is a step function of income (which includes `r·a`), the food-stamp rule kinks,
and housing is discrete. Those discontinuities sit precisely where your policy action is.

**Recommendation: fix the reset, but do not rely on coarse mode for anything reported.** Your
welfare margins are 0.1–1% and R1 already flagged them as narrow. Use **regime decomposition**
instead — within each regime (voucher eligible/not, food stamp binding/not, `v` ∈ {0, ≤v̄, >v̄})
the problem is concave, so solve each exactly and take the max. Exact *and* fast.

### On giving me access to your remote machine

Don't. Two better options:

1. **Run Claude Code on the remote box itself.** It is a Linux CLI — install it there and
   start a session inside your MobaXterm SSH shell. You authenticate as yourself, no
   credentials are shared, and the session has native access to all 40 cores. This is the
   right answer to what you asked.
2. **Git as the interface.** I commit here → you `git pull` and run there → you commit
   results into `output/` → I analyze and write.

I cannot usefully SSH out from this container: it is ephemeral, outbound goes through an
HTTPS proxy, and credentials would need re-entering every session. Option 1 gets you
everything you wanted from that idea, without the security problem.

---

## 1. Do this first, before anything else

The AE writes that Constantini (2025) finds HF reduces 3-year mortality by 4.6pp while TF
has no long-term health effect, *"in contrast with the model simulations of this paper."*

Your headline runs through mortality — universal TF only beats universal HF once mortality
spillovers are added. Your Experiment 1 has population *rising* 0.23% under TF. Your
addiction→mortality multiplier (6.9) is overwhelming your homelessness→mortality multiplier
(1.6), and those two came from separate literatures that were never reconciled.

**Re-target κ_{h,φ} and κ_{d,φ} on the existing code so Experiment 1 reproduces
Constantini's HF-vs-TF mortality difference.** This is a two-parameter recalibration, not a
rebuild. A week on your cluster.

- Ranking survives → your single strongest objection becomes a validation exercise.
- Ranking flips → you learned it in a week, and "generosity dominates conditionality" is
  still a publishable paper.

There is a real partial defense either way: Constantini studies *rationed* HF vs TF, which
is your Experiment 1, where you already agree TF is worse. Your novel claim is about
*universal* TF, which he does not study. Say that explicitly regardless.

---

## 2. The new model, in one page

**States (7):** age `j`, assets `a ≥ 0`, productivity `x/z`, employment `e`, SUD status `d`,
housing `h` (homeless + 2–3 rental sizes), voucher receipt `η`. Mental health `m` makes 8.

**Gone:** homeownership, tenure choice, mortgages, the negative asset grid, house prices,
rents, the construction firm, the rental company, UI expiration, type-dependent bequests,
4 of 7 housing sizes.

**Equilibrium objects:** labor tax `τ_ℓ`, drug price `p_v`, bequests. That's it — no housing
market to clear.

**New mechanisms:** endogenous treatment, imperfect sobriety detection, a homelessness
externality, mental health.

**Preferences fixed across SUD status** (single θ_2) — see §4.

Everything above is requested by name in the AE letter or a referee report except mental
health (R1 asked for it) and fixed preferences (your call, and the right one).

### Implement homeownership as a switch, not a deletion

The code already separates renter (`i=1`) and owner (`i=2`) across 74 `do i=1,2` loops, with
bounds driven by `is_owner` at allocation. So:

```fortran
integer, parameter :: include_homeownership=0
integer, parameter :: tenure_grid_size=include_homeownership*2+(1-include_homeownership)*1
integer, parameter :: negative_financial_grid_size=include_homeownership*61+(1-include_homeownership)*1
integer, parameter :: housing_status_grid_size=include_homeownership*7+(1-include_homeownership)*4
```

These are `parameter` constants, so gfortran dead-code-eliminates the owner branches and the
arrays shrink at compile time. Zero runtime cost, and `=1` restores today's model exactly.
Verify the `financial_grid` constructor handles a negative block of length 1.

Speedup compounds: tenure ~2×, assets 151→91 ~1.7×, housing 8→4 ~2×, plus `p_h` leaving the
outer loop. **Roughly 15–25× fewer Bellman evaluations**, before algorithmic changes.

### Three algorithmic changes worth more than the state count

1. **Exploit the step structure of π_d(v).** It has one threshold v̄, so solve three *smooth*
   subproblems (v=0, v ≤ v̄, v > v̄) and take the max. Kills a non-concave search.
2. **Monotonicity of a'(a).** Carry the previous gridpoint's optimum as a bracket.
3. **Coarse-grained OpenMP** over the outer state loops (productivity × employment × SUD).
   With 4 cores, parallelize coarsely; with 40, this is where the scaling comes from.

**Target:** one stationary equilibrium in ≤ 60–90 seconds on 4 cores. If you hit that,
everything the referees want — transitions, sensitivity, identification — becomes routine.

---

## 3. Master table: every big item and its disposition

Grouped by theme, with the cheapest adequate response. "Discuss" means a paragraph, not code.

### A. The model is opaque *(AE, R1 1e, R2, R3)*

| Item | Response | Cost |
|---|---|---|
| Need a stylized model | Two-period model proving the **generosity × conditionality cross-partial** — see §5 | Analytical |
| Appendix A disorganized, static, overclaimed | Tighten, demote, relabel as intuition | Writing |
| Model is a black box | Numerical **channel-shutdown ladder** — see §6 | ~50–100 solves |
| Show drug-use policy functions | Plot v(a, income) by SUD status | 1 figure |
| Stylized facts on drug use by income/employment/housing | Report from baseline | Free |

### B. Quantification below bar *(AE, R1 2, R3)*

| Item | Response | Cost |
|---|---|---|
| **Model fit never shown** | Add model column to Table 2 for all 22 targets | Free — non-negotiable |
| Homeless: 100% unemployed, ~0 income (data: 40–52%, 19%) | Add a transitory expense/eviction shock so non-corner people become homeless | Model change |
| Homeless age distribution off (73% vs 48% aged 26–44) | Mental health state creates persistent older homeless | Comes free with §C |
| No numerical identification evidence | Local perturbation plots; AGS sensitivity if solve is fast | Cheap once fast |
| Price-elasticity moment not replicable | Appendix defining every moment's model counterpart | Writing |
| Calibration reads as a list | Rewrite around insights; separate standard vs novel parameters | Writing |
| Sources span decades, SCF waves unclear | Date everything | Writing |

### C. Key mechanisms missing *(R1 1a/1b, AE)*

| Item | Response | Cost |
|---|---|---|
| **No treatment in "Treatment First"** | Binary treatment/effort choice raising the recovery hazard at a cost; TF subsidizes or mandates it | One binary choice, no new state. **R1 expects this to strengthen TF** |
| TF assumes perfect detection | Detection probability p < 1 + false-positive rate | Modifies the voucher kernel only |
| Mental health absent | Persistent binary state: raises drug propensity, lowers employment, lowers recovery | Doubles state space — add **last** |
| Drug price fixed at 1 | Let `p_v` clear a simple supply curve | One scalar, replaces two you deleted |
| Admin/compliance costs ignored | Sensitivity row | Cheap |

### D. Elasticities untargeted *(R2, R3, AE — this is the core one)*

| Item | Response |
|---|---|
| **Elasticity of drug use to housing access** | Target it. Milby et al. (2005) + the HF RCT literature you already cite |
| Elasticity of homelessness to SUD | Target it |
| Match Constantini's mortality effects | §1 — do this first |
| Robustness to the −0.36/−0.9 price elasticity range | Sensitivity ladder |

### E. Welfare machinery is ad hoc *(R1 3, R2, R3, AE)* — see §4

### F. Model too large *(AE)* — see §2

### G. Policy analysis presentation *(R1 3d, R3, AE)*

| Item | Response | Cost |
|---|---|---|
| No proper transition paths | Solve them — feasible once there's no housing market to clear | Only viable post-§2 |
| Too many counterfactuals in body | Keep 2, appendix the rest | Writing |
| Voucher probability varies discretely | Continuous sweep of π_V — is there a Laffer curve? | Cheap sweep, good figure |
| Tables should show levels + % changes | Add columns | Free |
| Language too strong ("debate is resolved") | Soften — see §4 | Writing |

### H. Literature and writing

| Item | Response |
|---|---|
| Connect to Constantini, Cohen, Brounstein-Wieselthier, Abramson, Humphries | Cite and engage |
| χ_H = 25.2% too high *(R2, R3)* | Compare to Abramson–van Nieuwerburgh; sensitivity |
| "37% of homeless have SUD" unsourced | Source it, state your homelessness definition |
| Intergenerational discussion without linkages *(AE)* | See §4.3 |
| "Addicted" → "substance use disorder" | Global find-replace |
| Why a max experimentation age? *(R1)* | Justify or drop |
| Typos *(R1, items 3–10)* | Fix |

---

## 4. The welfare rebuild — the highest-leverage section

Four separate complaints all land here, and one restructuring answers all of them.

### 4.1 Kill κ_cons; build the homelessness externality instead

R1 called κ_cons "plucked out of thin air," noted a truly conservative value is zero, and
observed it flips your ranking. R1 also objected that it is "not formally integrated into
the model" and "should in principle affect the value of life and agents' decisions."

R2 hands you the replacement: *"a large homeless population, especially if many are addicted
to drugs, creates a negative externality beyond the fiscal burden"* — citing Corbae, Glover
and Nattinger (2024), and calling it *"very easy to introduce."*

**Add −κ_ext · H_agg to period utility**, where H_agg is the aggregate homelessness rate that
agents take as given. This is strictly better than κ_cons on five counts:

1. A referee **asked for it**.
2. It has a citation and a literature, rather than being picked from air.
3. It is **internalized** — it enters V, so it affects the value of life and drug decisions.
   R1's consistency objection dies completely.
4. It **amplifies** the universal-policy result, since those policies cut homelessness ~93%.
5. It costs one scalar and an aggregate you already compute.

Then follow the AE's presentational fix: report **welfare and mortality as two separate
columns** rather than folding deaths into a single number. Let the reader weigh them.

Expect the headline to soften to: *"universal TF dominates on addiction, homelessness,
mortality and fiscal cost; universal HF wins narrowly on direct newborn welfare."* That is
defensible. "The debate is resolved in favor of universal TF" is not — R1 said so directly.

### 4.2 Fix preferences across SUD status

Adopt θ_{1,2} = θ_{0,2} = θ_2 as **the specification**, and run the old addiction-dependent
version as a robustness arm. This is cleaner than the AE's own proposal (vary `b` by
addiction status), because with Cobb-Douglas the asymptotic expenditure share is θ_2
regardless of `b`, and `b` is calibrated tiny — so varying `b` moves behavior at very low `v`
but will not reproduce the 44%-vs-11% expenditure gap.

**Fixed preferences reproduce that gap endogenously.** With identical preferences, an addict
and an experimenter in the same state differ in exactly one respect: the addict faces no
further addiction risk, since the recovery hazard depends on housing, not on `v`. So the
addict's drug choice is *static* — expenditure share θ_2. The experimenter restrains,
because crossing v̄ jumps them to π_{d,high} = 6.48 × π_{d,low}, so they bunch at or below v̄.

The 4× gap stops being an assumption and becomes a **prediction**. That is a materially
stronger paper, and it kills R2's "bakes in an income-contingent gain/loss from becoming
addicted" and R3's "reducing addiction mechanically raises consumption utility" at once.

Three things to work through:

1. **Recheck identification.** θ_{1,2} is gone, so the 44%, 11% and 0.87 moments now rest on
   θ_2, v̄ and π_{d,low}. The mapping is intuitive but the last two both key off v̄ — verify.
2. **All private cost of SUD now runs through mortality, unemployment and resource
   diversion.** Absent those, becoming addicted *relaxes* a constraint and would be weakly
   desirable. Internally consistent with your thesis, but a sharper commitment.
3. **It makes the mortality shutdown a cleaner test**, since R2's rival explanation for the
   income gradient is gone — but there is no fallback mechanism if the gradient fails to flip.

**Computational bonus:** for d = 1 the drug choice is static and, given discrete h', the
(c, v) split is closed-form Cobb-Douglas. No search over `v` for the addicted half of the
state space; combined with the three-regime trick, none anywhere.

### 4.3 Parental anxiety: discuss it, mostly

R2's exact framing matters. Of his two welfare additions he says the externality is *"very
easy to introduce"* but the dynastic element *"seems like more of a stretch, **but could be
discussed** (I think it would only amplify the welfare gains from reducing addiction)."*

R2 is not asking you to build a dynastic model. He is asking you to acknowledge it and note
the direction — which is in your favor. Three tiers:

**Tier 1 — discuss (recommended default).** A paragraph: parental altruism is an omitted
welfare channel; since universal TF reduces both SUD and homelessness among the next
generation, incorporating it would amplify the measured gains. Cite Corbae et al. Zero cost,
and it is literally what R2 asked for.

**Tier 2 — warm glow (cheap, and it fixes an AE complaint).** The AE separately asks: *"Why
is there a discussion on intergenerational transmission in Section 4.1.3, without
intergenerational linkages?"* The AE is right — §4.1.3 specifies log x' = 0.5 log x + ε, but
§3.12 draws newborns from the *unconditional* Ω_x, so ρ_x is decorative.

Make it load-bearing. At a single parental age j_p, add ν · E_{x'|x}[V_1(0, x', ...)] to the
Bellman. You do **not** need to match parents to actual children — the conditional
distribution of x' given x is already specified, and in a stationary equilibrium the
unconditional newborn distribution is unchanged, so nothing else breaks. One extra term at
one age, using objects you already compute (V_1 is needed for the welfare measure anyway).

Because the parent cannot influence x', this shifts welfare *levels* but not decisions —
which is exactly what R2 predicts ("only amplify the welfare gains"). It changes the *policy
comparison* because V_1 differs across regimes. One new parameter ν, disciplined by
willingness-to-pay evidence, reported as a welfare robustness row.

**Tier 3 — behavioral dynastic link.** Make the child's initial state depend on the parent's
`d` or `h`; the `newborns_inherit_addiction` switch (line 68) already exists. This creates a
genuine "I shouldn't use drugs because my child will suffer" channel and would strengthen TF
further. **Don't.** It is a different paper, it needs its own calibration target, and R2
explicitly did not ask for it.

If Tier 2 is more than you want, do Tier 1 and simply delete the decorative
intergenerational language from §4.1.3. That alone closes the AE's complaint.

---

## 5. The intuition section — a *dynamic* stylized model

The paper structure to aim for: **intuition model → quantitative model → homeownership in
the appendix.** That is the right shape, and it maps onto what the referees asked for.

The intuition model must be **dynamic, not static**. That is the whole content of R1's
comment 1(e): the current Appendix A derives results "in very specific static settings,
while the main model is dynamic," so "some claims around the appendix are more general than
what the appendix actually establishes." A second static model would not fix this.

### Proposed setup — three periods, no assets, binary drug choice

Keep only what is needed for the channels to be visible:

- **Income** `y`, either two types or a continuum. No savings — this is what makes it
  tractable, and R1's objection to the current appendix is about *dynamics*, not assets.
- **Period 1:** choose `v ∈ {0,1}` (experiment or not). Utility gain `g(y)` from using.
- **Transition:** experimenting leads to SUD with probability π.
- **Period 2:** SUD carries mortality risk δ, unemployment risk, and — under TF — loss of the
  voucher. Recovery probability depends on housing status.
- **Period 3:** continuation value, so the value of life is an actual object rather than a
  reduced-form penalty.

Three periods rather than two buys you the feedback loop: SUD in period 2 → homeless in
period 2 → lower recovery → still SUD in period 3. That is the mechanism the abstract calls
central, and it cannot appear in two periods.

### The three results it should deliver

**Result 1 — the income gradient reverses.** There is a threshold ŷ above which agents
abstain, and drug use is decreasing in `y` iff the mortality penalty scales with the
continuation value faster than the utility gain `g(y)` scales with income. This is the
current Appendix A result, but now with a genuine continuation value — which is exactly what
R1 said the static version could not establish.

**Result 2 — the cross-partial, and this is the paper.** Under TF the penalty for using is
losing the voucher. If vouchers are rationed with probability π_V, the *expected* penalty is
π_V × (voucher value). So deterrence is **linear in π_V**:

> ∂(deterrence)/∂π_V > 0, hence ∂²(deterrence)/∂(generosity)∂(conditionality) > 0.

A guaranteed voucher is a strictly bigger stick than a lottery ticket. That single line
explains why rationed TF loses to rationed HF while universal TF beats both — the result
currently buried in Table 8. It is nearly trivial to prove and it is the paper's actual
contribution.

**Result 3 — the feedback loop amplifies.** With recovery depending on housing, SUD +
homelessness is close to absorbing, so the period-2 penalty compounds into period 3. Show
that this raises the deterrent in Result 2 — i.e. the loop and the conditionality reinforce
each other.

### Why this reframes the whole paper

It moves you from "here is a big model and four experiments" to "here is a general principle
about conditional transfers, verified quantitatively, applied to a live debate." That
directly answers the AE's central complaint — *"the economic messages of the paper are lost
within long-lists of model features"* — and R2's "black box" objection.

Say explicitly that the quantitative model exists to measure **magnitudes** and fiscal and
equilibrium feedbacks. It does not establish the **signs**; the intuition model does.

**Optional and cheap:** calibrate the three-period model roughly and show it reproduces the
sign pattern of the quantitative model. It costs almost nothing and it is persuasive.

### Homeownership in the appendix

Exactly right, and the compile-time switch in §2 is what makes it nearly free: run the
appendix version with `include_homeownership=1` and report that the policy conclusions are
unchanged. This converts the AE's objection ("why do we need homeownership?") into a
robustness result rather than a concession — and because it is one parameter, the appendix
version stays in sync with the main model automatically instead of rotting.

---

## 6. The mechanism section: channel shutdowns

R1 asked for this **by name** in comment 1(d), and stated a preference for it over the
appendix: *"compare the relationship between income and drug use in the baseline model to an
otherwise similar version of the model in which mortality is not affected by drug use. I
would find this more intuitive than a toy example that abstracts from dynamic savings
decisions."*

Shut channels off one at a time, **recalibrating `b` in each arm to hold drug participation
at its baseline value**, and report *who* uses drugs. The recalibration is what makes it
work — without it, removing the mortality penalty just raises drug use everywhere and the
level change swamps the compositional one.

| Arm | Shut off | Isolates |
|---|---|---|
| 0 | baseline (fixed preferences) | Reference |
| 1 | κ_{d,φ} = 1 | Value-of-life — **the headline claim** |
| 2 | κ_{d,ue} = κ_{d,eu} = 1 | R1's rival hypothesis (income risk) |
| 3 | κ_{h,φ}, κ_{h,ue}, κ_{H,d} = 1 | The feedback loop the abstract calls central |
| R | restore θ_{1,2} > θ_{0,2} | Robustness vs the old preference spec |

**The money figure:** drug-use rate by income decile, one line per arm. Baseline slopes
down; if your claim holds, Arm 1 flips it upward. That single panel *is* your central
theoretical claim, shown dynamically, and it retires Appendix A as the load-bearing argument.

Alongside it, per arm: mean user income relative to average (the statistic R1 attacked —
41% model vs 74% data), share unemployed, share homeless, mean age, mean assets.

**Report experimenters and addicts separately.** Experimentation is the decision margin —
the clean test. Addiction is a stock that also reflects differential mortality and recovery,
so shutting off addiction-mortality changes its composition partly mechanically. Conflating
them invites exactly the objection R1 raised about your untargeted moments.

**Caveat on `b` as normalizer.** By your own argument `b` governs the *no-penalty* gradient,
which slopes upward, and penalties reverse it — so recalibrating `b` adjusts the very object
determining the counterfactual gradient. Handle it openly: report both un-normalized (gives
a headline level effect) and normalized (gives composition), and confirm the flip survives a
second normalizer. π_{d,low} is the good candidate, since it shifts the transition rather
than preferences.

**Risk:** if Arm 1 does not flip the gradient, the central claim is wrong. But R1's rival
hypothesis is that Arm 2 does the work — in which case the framing shifts from *value of
life* to *value of future resources*, which is more general and more robust. The paper
survives either result. What it cannot survive is a referee running this in his head and not
believing you.

---

## 7. Sequence

Ordering, not schedule — calibrate the durations to your own pace.

| Phase | Work | Where |
|---|---|---|
| **1** | **Constantini mortality check** on existing code | 40-core |
| **2** | Two-period model: the cross-partial | Paper |
| **3** | Strip the model (§2): homeownership switch, housing GE, UI, bequests, grid | Here → verify coarse |
| **4** | Fixed preferences; recheck identification of θ_2, v̄, π_{d,low} | Here → calibrate there |
| **5** | Add: treatment, imperfect detection, `p_v`, homelessness externality | Here |
| **6** | Add mental health **last** (doubles the state space) | Here → there |
| **7** | Full recalibration + fit table + housing-access elasticity + identification evidence | 40-core |
| **8** | Mechanism ladder (§6) | 40-core |
| **9** | Transitions, π_V sweep, sensitivity ladders | 40-core |
| **10** | Rewrite | Paper |

Phase 1 gates everything. Phases 3–5 are where I can do the most for you directly: the
Fortran edits are mechanical, verifiable coarse, and independent of the cluster.

The rewrite is not a residual. The AE was blunt: *"One would have to rewrite this paper to
reflect insights rather than providing 5 pages describing 22 moments and parameters."*

---

## 8. Bottom line

The door is genuinely open: R3 says revise, R2 is on the fence and calls the model "very
rich," and only R1 says reject — with the most constructive report of the three. Nobody
attacked the question. Every objection is about execution.

The single diagnosis all four documents share: **the paper is a large model carrying a small
amount of identification.** The fix is not more machinery. It is to cut hard, and spend the
freed compute disciplining the three or four elasticities the conclusion actually turns on.

Two structural moves do most of the work. Replacing κ_cons with a modeled homelessness
externality converts your weakest link into a referee-requested feature. Fixing preferences
across SUD status converts a calibrated assumption into a prediction. Both simplify the
model *and* strengthen it, which is the rare kind of revision that is worth the quarter it
will cost.
