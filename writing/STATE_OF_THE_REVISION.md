# Housing First or Treatment First — state of the revision

RED-D-26-00078. What the model now is, how it is calibrated in two stages, what it is
validated against, which referee comment each change answers, and what is still open.

Written to be read in one sitting and used to decide direction. Section 5 is the part
that decides direction: it lists what is *not* answered.

---

## 1. The model

The original model is untouched (`code/housing_first_or_treatment_first_SR_v1.f90`) and
remains the homeownership version for an appendix. Everything below refers to the rebuilt
model in `code/simple/`.

### 1.1 Environment

Overlapping generations. Model ages 1–60, real age 26–85; retirement at 66 (age index 41).
Households die stochastically; assets of the deceased are redistributed as a **uniform**
lump-sum bequest.

**State — 7 variables, 12,960 points per age**

| | Symbol | Points | Notes |
|---|---|---|---|
| Age | `j` | 60 | real age 26–85 |
| Financial assets | `a ≥ 0` | 60 | cubic spacing, dense near zero; no borrowing |
| Labour productivity | `y` | 9 | Rouwenhorst, AR(1) in logs, ρ = 0.90, σ = 0.20 |
| Employment | `e` | 3 | employed / unemployed with UI (year 1) / unemployed without UI |
| SUD status | `d` | 2 | clean / substance use disorder |
| Serious mental illness | `m` | 2 | absent / present |
| Housing voucher | `η` | 2 | held / not held |

Two deliberate absences.

**Housing entered with is not a state.** Survival, employment transitions and the recovery
hazard all condition on the *chosen* `h'`, and renters face no adjustment cost, so the unit
a household arrives in is payoff-irrelevant. Removing it left every aggregate identical
and cut the solve by 6.6×.

**Employment needs three states, not four.** UI is drawn on *entry* to unemployment with
probability 0.30 and lasts one year. A first-year non-recipient and a long-term unemployed
household have identical income (zero) and identical continuations, so those two states
merge *exactly* — this is a proof, not an approximation.

### 1.2 Choices

Housing `h' ∈ {homeless, 3 rental sizes}` × drug regime `∈ {abstain, use}` × treatment
`∈ {0,1}` × savings `a'` on the full 60-point grid × **hours worked, continuous on [0,1]**.

### 1.3 Preferences

```
u(c, h, v, ℓ) = [ c^α · h^β · (v+b_dm)^γ ]^(1−σ)/(1−σ)
                + ω_ℓ · (1−n)^(1−σ_ℓ)/(1−σ_ℓ)
                + ℵ − κ_ext·( H_agg + ω_ext·HD_agg )

α = (1−θ_h)(1−θ_v),  β = θ_h(1−θ_v),  γ = θ_v
```

The Cobb-Douglas **weights are invariant to SUD status**. Only the Stone-Geary shifter
`b` varies, by SUD status and by mental illness. This is the AE's A8 suggestion, and it is
what kills the "reducing addiction mechanically raises utility from c and h" objection.

A single `b` cannot match both the participation moment and the expenditure-share moment —
a `b` large enough to deter clean households pushes the unconstrained `v*` below zero,
which drives SUD drug spending to the corner. Two values of `b` (clean, SUD) separate them:
`b(clean)` pins participation, `b(SUD)` keeps the interior solution so `θ_v` pins the
expenditure share. Poor mental health *lowers* `b`, which raises the marginal utility of
the first units of use — the self-medication channel.

`ℵ` is the flow value of being alive; it is what makes mortality risk a deterrent to drug
use and therefore carries the paper's central mechanism.

### 1.4 Drug use and addiction

Two regimes: abstain (`v = 0`) or use (`v > 0`, chosen continuously). **A single addiction
hazard**: a clean household that uses becomes SUD next period with probability `π_d`,
regardless of how much it consumes. There is no light/heavy threshold and no
consumption-dependent hazard.

SUD households recover with a hazard that depends on housing (lower when homeless), mental
illness (lower with SMI), and **treatment take-up**, which is a choice with a resource cost.

Clean households may initiate only up to age index 30 (real age 55).

### 1.5 Labour supply — continuous, from the first-order condition

Hours are pinned by the intratemporal FOC, solved the way the original code solves it:
bracket on the sign of

```
u_c · d(resources)/d(hours)  −  ω_ℓ·(1−n)^(−σ_ℓ)
```

Two things the original does not do, both of which matter here.

**The residual is not monotone in hours.** The food-stamp floor claws back at 100% and the
voucher at `κ_r = 0.30`, so `d(resources)/d(hours)` jumps *up* where each transfer runs
out, and the residual can cross zero more than once. That is the **welfare trap**, not a
numerical artefact: "work a little and keep the transfer" and "work properly" are genuinely
distinct local optima, and the household has to compare them. A single bisection on [0,1]
would silently pick whichever one it happened to bracket. The interval is split at the
kinks and each piece solved exactly. Voucher eligibility is a step in the *continuation*
value rather than the budget, so the piece optimum is clamped to each side of it and both
are evaluated.

**The FOC is solved multiplied through by `(1−n)^σ_ℓ / u_c`.** Both factors are positive,
so no bracketing decision changes, but it removes the poles false position crawls on —
`u_c` blowing up as resources run out, and the marginal utility of leisure blowing up as
hours approach one. With Anderson–Björck rather than Illinois for the remaining asymmetry
at zero hours, a root takes 6.8 evaluations instead of 22.

`check_hours.f90` validates the solver against a 4,001-point brute-force scan of the
identical objective.

### 1.6 Housing, vouchers, and the two policies

Rent is a fixed price (no housing-market general equilibrium). Homelessness is the lowest
point of the housing grid, with a calibrated service flow `h_homeless`.

Voucher rules are institutional, not free: eligibility below 50% of median income (`κ_V`),
30% tenant contribution (`κ_r`), and a lottery probability `π_V` calibrated to HUD take-up
among the eligible. Vouchers pay only while renting, never while homeless.

| | Housing First | Treatment First |
|---|---|---|
| Voucher conditional on abstinence | no | yes |
| Detection probability | — | `p_detect ≤ 1` |
| False-positive rate | — | `p_false ≥ 0` |

Both detection parameters are policy-experiment objects reported as sensitivity, not
calibrated: the point is precisely that perfect enforcement is not credible.

### 1.7 Serious mental illness

Exogenous persistent binary state. It is **SMI**, not "any mental illness": AMI covers ~23%
of US adults including mild anxiety, while SMI is ~5.5% and is defined by substantial
functional impairment. Putting a quarter of the population in a state that halves
productivity would be indefensible.

This follows İmrohoroğlu and Zhao (2022) structurally, not just numerically: in their model
labour-market shocks generate *short* homeless spells while health shocks generate *chronic*
homelessness, and expanded disability income is the effective policy for the chronic group.
Homelessness driven purely by income risk is transitory; the persistent tail needs a
persistent state.

SMI affects six things: productivity conditional on working, job finding and separation,
mortality, the SUD recovery hazard, `b` (self-medication), and eligibility for disability
income when not employed. Onset is *derived* from the target prevalence and the recovery
rate, so calibrating persistence never disturbs prevalence.

### 1.8 Government and equilibrium

Three equilibrium objects, no housing market:

| Clears | How |
|---|---|
| `τ_ℓ` | government budget, closed form given the distribution |
| `p_v` | drug market: cost `C(V) = ψ₁/ψ₂ · V^ψ₂`, so supply elasticity `= 1/(ψ₂−1)` |
| bequests | assets of the deceased, redistributed uniformly |
| `H_agg`, `HD_agg` | fixed point, since they enter period utility (only when `κ_ext > 0`) |

`ψ₁` is normalised so `p_v = 1` at the benchmark. This is what answers R3's worry that
endogenising `p_v` "requires suppressing this normalization": it does not, because the
normalisation moves to `ψ₁`. Only counterfactuals move the price.

The externality enters **period utility**, taken as given by households — that is what makes
it a spillover rather than a private cost — but the aggregates are equilibrium objects, so
policy moves them and the movement feeds back into the value of life and hence into drug
decisions. This is the property `κ_cons` lacked.

---

## 2. Calibration

Two stages, and they are different exercises.

### 2.1 First stage — the stationary equilibrium

Parameters set outside the model, then internally calibrated parameters each attached to
one moment of the stationary distribution.

#### Externally set

| Parameter | Value | Source |
|---|---|---|
| `σ` (CRRA) | 2.0 | standard |
| `σ_ℓ` (leisure curvature) | 3.0 | Frisch elasticity 0.5, Chetty (2012) |
| `ξ` (tax progressivity) | 0.85 | Heathcote, Storesletten and Violante (2017) |
| `r` | 0.03 | Kaplan, Mitman and Violante (2020) |
| `κ_V` (voucher eligibility) | 0.50 of median | HUD rule |
| `κ_r` (tenant contribution) | 0.30 | HUD rule |
| `π_UI` (share of entrants drawing UI) | 0.30 | insured unemployment / total unemployment, FRED 2014–24 |
| UI replacement rate | 0.50 | standard US |
| `π_ue` (job finding, annual) | 0.55 | Krueger, Cramer and Cho (2014) |
| `κ_ue,h` (homeless job-finding multiplier) | 0.80 | Desmond and Gershenson (2016) |
| `κ_φ,h` (homeless mortality multiplier) | 1.60 | Meyer et al. (2025), 60% excess mortality |
| `κ_φ,m` (SMI mortality multiplier) | 2.50 | standardised mortality ratios for SMI, 2–3 |
| SMI prevalence | 5.5% | NSDUH 2023, adults |
| SMI recovery hazard | 0.067/yr | İmrohoroğlu–Zhao's own moment: ~50% improve enough to work within 10 years |
| `χ_D` (fiscal cost per SUD) | 0.212 | CEA (2017), ~$30,000 per person-year |
| `χ_H` (fiscal cost per homeless) | 0.252 | National Alliance to End Homelessness — **reported as sensitivity**, R2/R3 both judge it high |
| `ρ_pen,d` (SUD wage penalty) | 1.00 | **no direct effect in the baseline** — see A20 below |

#### Internally calibrated — 19 parameters, 19 moments

Each parameter is assigned the moment it dominates, and the sign of `dM/dparam` is declared
in code so a wrong sign shows up immediately as a moment walking away from its target.

| Parameter | Moment | Target | Source |
|---|---|---|---|
| `b`(clean) | drug participation | 5.13% | NSDUH 2024, ages 26+ |
| `π_d` | SUD rate | 3.68% | NSDUH 2024, ages 26+ |
| `h_homeless` | homelessness rate | 0.30% | HUD PIT |
| `π_eu` | unemployment rate | 4.90% | BLS |
| `κ_ue,d` | unemployment rate given SUD | 26.90% | NSDUH |
| `recover_mult_hl` | drug UD share of the homeless | 21.70% | Gutwinski et al. (2021) |
| `π_V` | voucher recipients / income-eligible | 26.60% | HUD |
| `θ_v` | drug spending / income given SUD | 44.00% | paper's existing moment |
| `θ_h` | aggregate housing cost / income | 21.20% | SCF 2022, **all** households |
| `p_rent` | share with housing cost > 50% of income | 17.49% | SCF 2022, all households |
| `ℵ` | SUD income / average income | 68.70% | NSDUH 2024 |
| `di_coverage` | SMI share of the homeless | 25.00% | Gutwinski et al. (2021) |
| `κ_ue,m` | unemployment rate given SMI | 7.10% | NSDUH Table 6.5B, via Bayes |
| `ρ_pen,m` | homeless income / average | 19.10% | Meyer et al., linked administrative data |
| **`β`** | **wealth / GDP** | **3.00** | standard US capital-output ratio |
| `cfloor_share` | food stamps / labour income | 0.42% | SNAP outlays, FY2023 |
| `mh_b_ratio` | SUD rate given SMI | 9.75% | NSDUH 2023 detailed tables, Bayes on Tables 6.13B / 6.4B / 5.10B |
| `ω_ℓ` | average hours worked | 40% of time | Guvenen et al. (2023) |
| `b`(SUD) | keeps the drug choice interior so `θ_v` identifies the expenditure share | — | — |

**On `β` and wealth/GDP = 3.** GDP is measured as *all factor income* — labour earnings
plus the return on the capital stock — with transfers (social security, UI, disability,
food stamps, vouchers) excluded, because transfers are redistribution, not output. Three is
the standard US private-capital-to-output ratio and is what a life-cycle discount factor is
normally pinned by. It is the right target here rather than the SCF's ~7.3 net-worth-to-
*household-income* ratio, whose numerator is mostly housing equity a model without
homeownership cannot hold and whose denominator is a household income concept, not output.

Note the arithmetic this implies: with `A = 3·GDP` and `GDP = labour income + rA`, capital
income is 9% of GDP. That is low relative to a one-third capital share, and it is a
consequence of holding `r` fixed at 3% in a model with no production function. It should be
stated in the paper rather than left for a referee to find.

**Method.** Coordinate descent. Participation is a near-threshold function of `b` — below a
cutoff everyone uses, above it nobody does, and in the dead zone every drug moment reads
zero — so the level is pinned by bisection on `log b` *before* composition is touched, in
partial equilibrium.

**Status: the first-stage calibration has not converged.** Every number the model currently
prints is a placeholder. This is the single largest piece of work outstanding.

### 2.2 Second stage — short-run experimental moments

The first stage matches a cross-section. It says nothing about the *responses* the paper's
conclusion depends on, and that is exactly what R2, R3 and the AE all identified as the
crux. The second stage targets those responses directly.

These are **short-run** objects. They are computed by holding the stationary distribution
fixed at the benchmark, applying the experimental treatment, and simulating forward the same
number of periods as the study — not by comparing two stationary equilibria. That is a
different computation from stage one and requires the transition machinery (§5, R1 3d).

| Moment | Value | Source | Use |
|---|---|---|---|
| Abstinence, no housing → housing (unconditional) | 4.48 → 6.60 weeks of 24 | Milby et al. (2005), NH vs NACH, P = .058 | **Target** |
| Abstinence, no housing → housing (best housed arm) | 4.48 → ~7.5 weeks | Milby et al. (2005) | **Target** |
| Adding a sobriety condition | 6.60 → 8.32 weeks, **P = .091** | Milby et al. (2005), NACH vs ACH | **Validation only — sign, not level** |
| Housing First vs *usual services*, substance use | ≈ 0 | accommodation-based interventions systematic review | **Validation** |
| Drug-price participation elasticity | −0.63 | paper's existing approach, now computable because `p_v` is an equilibrium object | **Target**, via `κ_φ,d` |
| Treatment effect on the recovery hazard | OR ≈ 1.22 → `treat_gain` ≈ 1.35 | contingency-management meta-analysis | **Target, reported as a range** |
| Model-implied VSL | $7.5m | Viscusi and Aldy (2003); EPA (2010) | **Target**, via `ℵ` |

**Why the conditionality effect is a validation check and not a target.** Milby's abstract
reports that the abstinence-contingent arm beat the unconditional arm, but that holds only
*after controlling for treatment attendance*. In the raw randomised comparison, NACH vs ACH
gives P = .091 and the GEE models state the two housed groups "did not differ from one
another." Calibrating to a point estimate the source paper reports as insignificant would be
exactly the sin R1 attacked `κ_cons` for.

**Why the extensive/intensive distinction is the sharper test.** Milby's counterfactual is
*literally no housing*, and the effect is large. The HF RCTs compare HF to "usual services",
which already include shelter or transitional housing, and the effect is small or null. So
the elasticity of drug use with respect to housing access is **large at the extensive margin
and near zero at the intensive margin**. A model that reproduces both is far better
identified than one that matches either number alone. This is the moment R2 called the crux.

**Status: the second stage is specified but not built.** It needs the transition-path solver.

---

## 3. Validation — untargeted moments and their sources

What the model should be scored on *after* calibration, none of it targeted.

### 3.1 Distributional

| Untargeted moment | Data | Source |
|---|---|---|
| Full CDF of housing cost / income (12 thresholds) | 95.4 / 89.3 / 77.2 / 63.6 / 50.9 / 40.6 / 32.5 / 26.0 / 17.5 / 12.6 / 7.1 / 4.6 % above 5–100% | SCF 2022, ages 26–85, owner housing at imputed rent 8.3% of value (`data/scf_housing_burden.py`) |
| Drug **user** income / average | 95.1% | NSDUH 2024, ages 26+ (`data/nsduh_gradients.py`) |
| Share of the homeless who are **employed** | 40–52% | R1 comment 2(c)(i) |
| Age distribution of the homeless | 48.1% aged 26–44; 27.1% aged 55+ | R1 comment 2(c)(ii) |
| Drug use by age (U-shaped) | NSDUH | `data/drug_use_age_distribution.xlsx` |
| Homelessness by age | California PIT | `data/homelessness_by_age_california.xlsx` |
| Wealth distribution by age | SCF 2022 | `data/SCF_*` |

Two of these deserve emphasis because R1 used them to distrust the whole quantification.
The paper reported that drug users earn 41% of average income against "roughly 74%" in
the data — but the 74% is computed over people with a use *disorder*, not people who use.
For ages 26+, NSDUH gives **0.951 for users** and **0.687 for moderate/severe UD**.
Targeting the disorder ratio and validating on the use ratio is the sharper test, and it
makes the economics explicit: *use* is close to income-neutral, and it is **progression to
disorder** that concentrates at the bottom.

### 3.2 Policy responses

| Untargeted response | Data | Source |
|---|---|---|
| HF effect on 3-year mortality | **−4.6 pp**, s.e. 1.7 | Costantini (2025), ~300,000 VA veterans, IV |
| TF effect on long-run health | **≈ 0** | Costantini (2025) |
| Housing stability under HF | sustained | HF RCT literature |
| Housing stability under TF | declining | HF RCT literature |
| Permanent supportive housing vs emergency shelter, property values | PSH raises, emergency shelter lowers | shelter-siting hedonic literature |

**The Costantini result is the paper's biggest single risk and should be confronted in the
introduction, not buried.** The best available quasi-experimental evidence says the
mortality benefit runs through *housing*, and that conditioning on treatment adds nothing
detectable. The paper concludes universal TF dominates.

The defensible position after the revision is the **generosity** result — expanding coverage
dominates, and conditionality is second-order and uncertain — which is consistent with all
of the evidence above and is still a paper. Getting there requires reporting welfare and
mortality as two separate dimensions (AE A9) rather than one collapsed ranking.

### 3.3 Full source list

Heathcote, Storesletten and Violante (2017) · Kaplan, Mitman and Violante (2020) ·
Chetty (2012) · Guvenen et al. (2023) · Krueger, Cramer and Cho (2014) ·
Desmond and Gershenson (2016) · Meyer et al. (2025) · Degenhardt et al. (2011) ·
Vaillant (1995) · Fleury et al. (2016) · contingency-management meta-analysis
(PMC8034391) · Gutwinski et al. (2021, *PLOS Medicine*) · İmrohoroğlu and Zhao (2022) ·
Corbae, Glover and Nattinger (2024, NBER w32898) · Autor, Palmer and Pathak (2014, via
Corbae et al.) · Milby et al. (2005, *AJPH* 95(7):1259–65) · accommodation-based
interventions systematic review (PMC8356295) · Costantini (2025) · CEA (2017) ·
Viscusi and Aldy (2003) / EPA (2010) · SAMHSA NSDUH 2024 microdata and 2023 detailed
tables · SCF 2022 · HUD programme rules and take-up · FRED insured unemployment ·
National Alliance to End Homelessness · Sitti, Horn and Berrens; Ridgeway (shelter siting).

---

## 4. Every model change, and the comments it answers

| # | Change | Comments answered |
|---|---|---|
| 1 | **Homeownership, tenure, mortgages and negative assets removed** | AE **A4**; R2 **D1** (the 7-point housing grid with 4 uncalibrated values disappears) |
| 2 | **Housing-market GE removed** — house prices and rents no longer clear | AE **A5** |
| 3 | **Drug price `p_v` made an equilibrium object**, with `ψ₁` normalised so `p_v = 1` at the benchmark | R1 **1(c)**; R3 **M2d**; AE **A5** |
| 4 | **Cobb-Douglas weights fixed across SUD status; only `b` varies** | R2 **C5**; R3 **M2a**; AE **A8** |
| 5 | **`κ_cons` deleted; homelessness externality built into period utility**, weighted by composition (`H_agg + ω_ext·HD_agg`) | R1 **3(a)**, **3(b)**; R2 **C2**; R3 **M2c**; AE **A9** |
| 6 | **Endogenous treatment take-up** raising the recovery hazard at a resource cost | R1 **1(b)**; AE **A10** — the most damning gap: the policy is named Treatment First and there was no treatment |
| 7 | **Imperfect detection and false positives** under TF | R1 **4(a)**, **4(b)**; AE **A11** |
| 8 | **Serious mental illness** added: productivity, employment, mortality, recovery hazard, `b`, and disability income | R1 **1(a)**; R1 **2(c)(ii)** (chronic illness generates the older homeless population) |
| 9 | **SUD productivity penalty set to 1.0 in the baseline**, with the employment-margin evidence carrying the effect and the contested wage evidence stated plainly | AE **A20** |
| 10 | **UI restructured**: drawn on entry with probability 0.30, lasting one year; four states collapse to three by an exact merge | AE **A2** |
| 11 | **Uniform lump-sum bequests** replacing type-dependent transfers | AE **A7** |
| 12 | **Single addiction hazard** — no light/heavy threshold, no consumption-dependent hazard | simplification; removes the `v̄` and 6.48 heavy-ratio parameters R3 **M2b** asked to justify |
| 13 | **Continuous labour supply from the FOC**, replacing the grid, with the welfare-trap non-convexity handled exactly | R3 **m1** (labour supply kept and made precise); AE **A3** (its role is now visible) |
| 14 | **`β` retargeted to wealth/GDP = 3** | AE **A17** (a parameter that was previously fixed by assertion now has an external target) |
| 15 | **Homeless SUD target corrected from 37% to 21.7%** — the 37% sits on Gutwinski's *alcohol* figure; the model is about drugs | AE **A16** |
| 16 | **Drug-user income target split** into users (95.1%) and SUD (68.7%) | R1 **2(c)(i)** — the "74%" measured a different population |
| 17 | **Housing-burden target moved to all households** at 21.2% aggregate, with the full 12-point CDF as validation | R1 **2(a)**; AE **A12** |
| 18 | **Mental-illness productivity penalty generating employed-but-poor households** | R1 **2(c)(i)** — an unemployment effect alone cannot produce employed homeless households |
| 19 | **Every parameter assigned a source or a target**, with a standard/novel status key (`code/simple/CALIBRATION.md`) | AE **A17** |
| 20 | **Channel-shutdown ladder** built (`mechanism.f90`): shut one channel, recalibrate `b` to hold participation fixed, report *who* uses in each arm | R1 **1(d)**, **1(e)**; R2 **C4**; R3 **M2b**, **M2c**; AE **A1** — *code exists, not yet run* |

**Cross-cutting count.** Six model changes plus one table cover roughly two-thirds of the
substantive comments.

---

## 5. What is still unanswered

Grouped by what it would take. This is the section that should drive the decision about
direction.

### 5.1 Blocked on the first-stage calibration converging

Nothing here is conceptually open; it is all waiting on numbers.

| Comment | What is needed |
|---|---|
| R1 **2(a)**, AE **A12** — model fit never reported | The fit table. Exists in code, needs a converged calibration |
| R1 **2(b)** — Tables 3–4 misses framed too positively | Rewrite once the misses are known |
| R1 **1(d)**, R2 **C4**, R3 **M2b/M2c**, AE **A1** — mechanisms | `mechanism.f90` is written but has never been run against a calibrated model |
| R1 **2(c)(i)** — share of the homeless employed (40–52%) | Currently **not a targeted moment**. Should be added or explicitly validated |
| R1 **2(c)(ii)** — age distribution of the homeless | Not yet computed as a model moment |

### 5.2 Blocked on the transition-path solver — the largest single gap

| Comment | What is needed |
|---|---|
| R1 **3(d)** — "solve proper transition paths; the several-period PE is a half-measure" | A transition solver. With no housing market, a path iterates on `τ_ℓ` and `p_v` alone, which is far cheaper than in the original model, but it does not exist yet |
| R1 **2(d)**, R2 **C1**, R3, AE **A13** — match the RCT elasticities | **The whole of §2.2.** These are short-run objects and cannot be computed from a comparison of stationary equilibria |
| R1 **2(e)** — the price-elasticity moment is not replicable | Needs the perturbation experiment plus an appendix defining each moment's model counterpart |

This is the critical path. Everything R2, R3 and the AE call the crux sits behind it.

### 5.3 Not started, cheap once the solve is fast

| Comment | What is needed |
|---|---|
| R1 **2(f)** — show identification numerically | Jacobian or perturbation figure. One solve per parameter |
| R1 **4(c)** — compliance, stigma and administrative costs of testing | A real admin cost in the government budget plus sensitivity. The current dismissive footnote must go |
| R1 **4(d)** — sensitivity ladder over addiction, recovery, mortality and employment parameters | Doubles as 2(f) |
| R2 **C6**, R3 **m3** — continuous sweep over voucher generosity; is there a Laffer curve? | One sweep of `π_V` from benchmark to 1 |
| R3 **m2** — present sensitivity as graphs, not tables | Plotting only |
| R3 **M1c** — show the empirical income–drug-use relationship | Microdata already extracted in `data/nsduh_gradients.py`; needs a figure |
| AE **A15** — compare `χ_H` to Abramson and van Nieuwerburgh | Sensitivity run plus a paragraph |
| R3 **m1** — welfare decomposition showing the role of labour supply | Now that hours are continuous, this is a decomposition of the tax-financing welfare cost |

### 5.4 Genuinely open modelling questions

| Comment | Status |
|---|---|
| R2 **C2** — externality calibration | Implemented but **`κ_ext = 0` in the baseline**. There is no credible point estimate: hedonic shelter-siting studies measure a *local, avoidable* disamenity, and this model has no geography. Corbae et al.'s externality is about neighbourhood housing *quality*, not homelessness, so only their *identification logic* transfers, not the functional form. Recommendation: keep zero as the conservative baseline, report a bounded sensitivity, and use the qualitative finding that **PSH raises property values while emergency shelter lowers them** — i.e. the externality plausibly differs in *sign* between HF and TF. That is a substantive point in HF's favour and it is more honest than inventing a number |
| R2 **C3**, AE **A6** — parental anxiety / intergenerational transmission | R2 lists it as a margin the paper misses but writes that it "could be discussed" and predicts it "would only amplify the welfare gains." The AE's A6 is a separate and simpler complaint: §4.1.3 uses intergenerational language without any intergenerational linkage. **Decision needed**: either delete the decorative language (cheap, fully answers A6) or add a warm-glow term at one parental age using the `ρ_x = 0.5` process already specified (cheap, answers both). Recommendation: the warm-glow version, because it costs one term and converts a criticism into a feature |
| R1 smaller comment **1** — why a maximum experimentation age? | Still present (`j_exp`, real age 55) and **still unjustified**. R1 caught a real internal tension with the U-shaped age profile of drug use in Table 4(a). Either justify it from NSDUH initiation data or drop it |
| AE **A16** — homelessness definition | The SUD target has been corrected, but the paper must still state explicitly that it targets *literal* homelessness and excludes doubling-up, and flag the sensitivity |
| R2 **D1** — how were the rental sizes chosen? | The grid is now 4 points instead of 7, and `h_homeless` is calibrated, but the three rental sizes are still set rather than calibrated. Either calibrate them or say plainly how they were chosen |

### 5.5 Writing only

R1 **1(e)** (reorganise the appendix, relabel as intuition), **3(c)** (tone down; universal
TF is not unambiguously preferred), smaller comments 2–10 (levels *and* percentage changes
in tables; eight typographical and citation fixes) · R3 **M1a** (stylised facts up front),
**M1b** (transparent empirical basis for the survival and unemployment hazards) ·
AE **A1** (stylised model section — the plan is now to use the *calibrated* model with the
shutdown ladder rather than a separate static toy), **A14** (connect to Costantini, Cohen,
Brounstein and Wieselthier, Abramson, Humphries et al.), **A17** (rewrite the calibration
section — §2 of this note is the raw material), **A18** (two counterfactuals in the body),
**A19** (global replace "addicted" → "suffering from substance use disorder").

---

## 6. Where the compute stands

4-core container, gfortran 13.3, `-O3 -march=native -funroll-loops -flto`.

| | |
|---|---|
| One household solve, 4-point hours grid | 6.2 s |
| One household solve, continuous hours from the FOC | **19.2 s** |
| Distribution | ~0.01 s |

Continuous hours cost 3.1×. That is the price of exactness on the labour-supply margin and
of handling the welfare-trap non-convexity correctly, and it is bounded: the FOC solve
itself is now 6.8 residual evaluations per root, down from 22 before the rescaling.

**Implication for the plan.** A stationary equilibrium is roughly 25–40 household solves, so
8–13 minutes. A full coordinate-descent calibration is an overnight job here and under an
hour on 40 cores. Counterfactuals, once calibrated, are minutes. The transition solver
(§5.2) will be the expensive object and is the thing to build next.

---

## 7. Recommended order

1. **Converge the first-stage calibration.** Everything in §5.1 unblocks at once, including
   the model-fit table whose absence is what made R1 distrust the quantification.
2. **Build the transition-path solver.** It is the critical path: it unblocks R1 3(d) *and*
   the whole of §2.2, which is what R2, R3 and the AE independently identified as the crux.
3. **Run the second-stage calibration** against Milby and the HF RCT literature, reporting
   the extensive/intensive contrast.
4. **Run the shutdown ladder** and the sensitivity/identification figures (§5.3) — cheap
   once 1–3 are done.
5. **Decide the two open modelling questions** (§5.4): the parental warm-glow term and the
   maximum experimentation age.
6. **Rewrite**, leading with the generosity result and reporting welfare and mortality as
   two dimensions, with the Costantini evidence confronted in the introduction.
