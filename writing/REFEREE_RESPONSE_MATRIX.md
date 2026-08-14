# Referee response matrix — every comment, with a disposition

RED-D-26-00078. Numbering follows each report exactly, so this can become the response
letter.

**Cost key:** `W` writing only · `F` free from existing output · `C` cheap compute ·
`M` model change · `X` expensive

**Disposition key:** **Do** = implement · **Discuss** = argue in text, no code ·
**Defend** = push back with evidence · **Cut** = remove the thing being objected to

---

## Referee 1

R1 ranks importance as 2) > 1) > 4) > 3).

### 1. Model

| # | Comment | Disposition | Cost |
|---|---|---|---|
| 1a | Mental health absent; would "weaken TF dramatically" | **Do.** Persistent binary state raising drug propensity, lowering employment and recovery. Add **last** — it doubles the state space. Also fixes 2(c)(ii) | M |
| 1b | TF should encourage treatment; recovery is random | **Do.** *The most damning comment* — the policy is named Treatment First and there is no treatment. Binary treatment/effort choice raising the recovery hazard at a cost. R1 expects this to **strengthen** TF | M |
| 1c | Drug price fixed at 1, never adjusts | **Do.** Let `p_v` clear a simple supply curve. AE and R3 also ask. Replaces two GE prices you are deleting | M |
| 1d | Show the mortality channel is the quantitatively important one | **Do.** This is the channel-shutdown ladder — R1 *specifies the design* and says he prefers it to the appendix. See plan §6 | C |
| 1e | Appendix disorganized, static, claims overreach | **Do.** Tighten, demote, relabel as intuition. Replace with a *dynamic* stylized model in the body | W |

### 2. Calibration and quantification — *R1's top priority*

| # | Comment | Disposition | Cost |
|---|---|---|---|
| 2a | Model fit never reported in Table 2 | **Do.** Non-negotiable. Its absence is what made R1 distrust the whole quantification | F |
| 2b | Tables 3–4 misses framed too positively | **Do.** Rewrite the framing honestly; state which misses matter and why | W |
| 2c-i | Homeless 100% unemployed (data 40–52%), income ~0 (data 19.1%); users at 41% of average income (data 74%) | **Do.** Add a transitory expense/eviction shock so non-corner households become homeless. Fixed preferences (plan §4.2) also helps the user-income gap | M |
| 2c-ii | Homeless too young: 73.1% aged 26–44 (data 48.1%); 9.3% aged 55+ (data 27.1%) | **Do.** Comes free with mental health (1a) — chronic illness generates the persistent older homeless population | M |
| 2d | Should match policy-relevant elasticities from the RCT literature | **Do.** Drug use → voucher generosity/conditionality; homelessness → voucher access; recovery → housing status. This is the core ask across all four documents | C |
| 2e | Price-elasticity moment not replicable | **Do.** Appendix defining every moment's model counterpart | W |
| 2f | Show identification numerically (Jacobian / AGS / perturbation figure); and show robustness to the −0.36…−0.9 elasticity range | **Do.** R1 was complimentary about the verbal argument in §4.2 — he just wants it shown. Perturbation plots are the cheap version | C |

### 3. Policy analysis

| # | Comment | Disposition | Cost |
|---|---|---|---|
| 3a | Loss of consortium not integrated into the model — internally inconsistent | **Cut + replace.** Drop κ_cons; build R2's homelessness externality into period utility instead, where it *is* internalized. See plan §4.1 | M |
| 3b | κ_cons ad hoc; truly conservative value is zero | **Cut.** Same fix — the parameter disappears | — |
| 3c | Tone down; universal TF is not unambiguously preferred | **Do.** Report welfare and mortality as two columns (AE's suggestion). Headline softens to "generosity dominates; conditionality pays once the benefit is guaranteed" | W |
| 3d | Solve proper transition paths; the several-period PE is "a half-measure" | **Do.** Only feasible after the cuts — with no housing market to clear, a path iterates on τ_ℓ and p_v alone | X |

### 4. Sensitivity

| # | Comment | Disposition | Cost |
|---|---|---|---|
| 4a | TF assumes perfect observation and enforcement | **Do.** Detection probability p < 1. Modifies the voucher kernel only — no new state | M |
| 4b | False positives — non-users losing access | **Do.** Same mechanism, second parameter | M |
| 4c | Compliance costs, stigma, admin burden; the $1–2bn testing estimate is too low to ignore *and* probably understated | **Do.** Put a real administrative cost in the government budget and run sensitivity. **Do not** keep the current dismissive footnote | C |
| 4d | Sensitivity to addiction transitions, recovery, addiction/homelessness mortality, employment consequences | **Do.** A sensitivity ladder — cheap once the solve is fast, and it doubles as 2(f) | C |

### Smaller comments

| # | Comment | Disposition |
|---|---|---|
| 1 | Why a maximum experimentation age? Inconsistent with U-shaped drug use by age in Table 4(a) | **Do** — either justify from NSDUH initiation data or drop J_A. Note R1 has caught a real internal tension |
| 2 | Tables should show levels *and* percentage changes | **Do** |
| 3 | p.5 "well-aware" → "well aware" | **Do** |
| 4 | Eq. (9) ends with a period, should be a comma | **Do** |
| 5 | p.25 target 19 — remove comma after citation | **Do** |
| 6 | p.28 fn.7 "our calibration" → singular (single-authored) | **Do** |
| 7 | Abramson citation lists "forthcoming" twice | **Do** |
| 8 | Karlman et al. — "Kinneruda", "Kragh-Sørensena" have spurious trailing 'a' | **Do** |
| 9 | Goering et al. — "Guido. Powell ," → "Guido Powell," | **Do** |
| 10 | Degenhardt et al. — "Hamamd Ali" → "Hammad" | **Do** |

---

## Referee 2

### Conceptual

| # | Comment | Disposition | Cost |
|---|---|---|---|
| C1 | All welfare results rest on the elasticity of drug use to housing access; only a *price* elasticity is targeted | **Do.** Target it — Milby et al. (2005) plus the HF RCT literature. R2 calls this the crux, and R3 + AE agree | C |
| C2 | Negative externality from a large homeless population (Corbae, Glover, Nattinger 2024); "very easy to introduce" | **Do.** −κ_ext·H_agg in period utility. **This replaces κ_cons** and turns R1's strongest objection into a referee-requested feature. Amplifies the universal-policy result | M |
| C3 | Parents suffer anxiety their children become addicted/homeless | **Discuss** (R2 says "more of a stretch, but could be discussed", and predicts it "would only amplify the welfare gains"). Optional cheap tier: warm glow at one parental age using the ρ_x = 0.5 process you already specify — which also fixes the AE's complaint that the intergenerational language is decorative. See plan §4.3 | W or C |
| C4 | Rich model is a black box; show the drug-use policy function by income and wealth for addicts and non-addicts | **Do.** One figure, straight from existing output | F |
| C5 | Utility spec (13) bakes in an income-contingent gain/loss from becoming addicted | **Cut the cause.** Fix preferences across SUD status (single θ_2). The 44%/11% gap then emerges endogenously from forward-looking restraint. See plan §4.2 | M |
| C6 | Optimal voucher design — χ_H = 25% of average income looks high; would broadening eligibility or coverage give more gains? | **Do.** Continuous sweep over generosity (also R3's Laffer point), plus sensitivity on χ_H against Abramson–van Nieuwerburgh | C |

### Detail

| # | Comment | Disposition | Cost |
|---|---|---|---|
| D1 | Housing grid: 7 values, only 3 calibrated, listed in footnote 4, not uniformly spaced. How were they chosen? Does it matter? Should they be calibration parameters? | **Cut the problem.** Dropping homeownership takes the grid to homeless + 2–3 rental sizes, all calibrated, reported in the table. Answers the objection by removing it | M |

---

## Referee 3

### Major concern 1 — connection to evidence and stylized facts

| # | Comment | Disposition | Cost |
|---|---|---|---|
| M1a | Present stylized facts on correlations between drug use, voucher receipt, and homelessness | **Do.** Empirical table up front. Also serves the AE's "align with a few stylized facts" | W |
| M1b | Survival and unemployment probabilities are central but their empirical basis is not transparent — especially unemployment transitions | **Do.** Dedicated subsection sourcing each hazard and multiplier | W |
| M1c | The income–drug use relationship is key to calibrating `b` and the income-dependent penalties, but its empirical counterpart is not shown | **Do.** Plot the joint distribution from NSDUH — you already have the microdata in `data/` | C |

### Major concern 2 — modelling of the addiction process

| # | Comment | Disposition | Cost |
|---|---|---|---|
| M2a | Reducing addiction lowers θ_d and mechanically raises utility from c and h, making addiction-reduction and housing-expansion complements "even absent incentive effects" | **Cut the cause.** Same fix as R2's C5 — fixed preferences removes the mechanical complementarity entirely | M |
| M2b | Stone-Geary is clever, but what drug-consumption patterns does it actually generate? Where does heterogeneity in `v` come from? Show model stylized facts by income, employment, housing, assets, and their dependence on `b`, the Stone-Geary parameter, and ℵ | **Do.** This *is* the channel-shutdown ladder plus the policy-function figure. One exercise serves R1 1(d), R2 C4, and this | C |
| M2c | Since drug use is rational and forward-looking, where do the externalities justifying intervention arise? Make them analytic or numerical; show how optimal policy changes when channels are shut off | **Do.** Enumerate them explicitly — fiscal (homelessness cost, addiction cost, foregone taxes) and non-fiscal (the C2 externality). The shutdown ladder quantifies each. **This is the sharpest theoretical question in any of the reports** and deserves its own subsection | C |
| M2d | How is the price elasticity targeted when p_v is normalized to 1? | **Do.** Resolved by making p_v an equilibrium object (R1 1c). Then explain the identification cleanly | M |

### Minor concerns

| # | Comment | Disposition | Cost |
|---|---|---|---|
| m1 | Surprised labor supply elasticity does not matter more for the welfare cost of tax financing | **Defend + show.** Note the tension with the AE, who questions whether labor supply is needed at all. Keep it, coarsen the grid, and report the welfare decomposition so its role is visible | C |
| m2 | Present counterfactual sensitivity as graphs, not tables (loss of consortium, ℵ) | **Do.** Moot for κ_cons once it is cut; do it for ℵ and the other key parameters | F |
| m3 | Vary the voucher receipt probability continuously — is there a Laffer curve of generosity, or is the corner optimal? | **Do.** Sweep π_V from the benchmark to 1. Same exercise as R2's C6, and it is a genuinely good figure — it would show whether "universal" is optimal or just a corner | C |

---

## Associate Editor

| # | Comment | Disposition | Cost |
|---|---|---|---|
| A1 | Provide a stylized model section; the number of moving parts obscures the economics | **Do.** *Dynamic*, not static — see plan §5. Prove the generosity × conditionality cross-partial | W |
| A2 | Is modelling UI expiration important? | **Cut** the κ state | M |
| A3 | What is the role of labor supply? | **Defend, coarsen.** R3 wants it kept — see m1 | C |
| A4 | Why homeownership rather than just homeless vs housed? | **Cut**, behind a compile-time switch; keep an appendix version | M |
| A5 | Why full GE? PE and GE outcomes look nearly identical. Keep government; add drug prices; drop housing prices and rents | **Cut** the housing-market GE; **add** p_v. Two prices out, one in | M |
| A6 | Intergenerational transmission discussed in §4.1.3 without intergenerational linkages | **Do.** Either delete the decorative language or make ρ_x load-bearing via the warm-glow term (C3) | W or C |
| A7 | How are lump-sum transfers determined by type? Why type-dependent bequests? | **Cut.** Uniform lump sum | M |
| A8 | Preferences: keep Cobb-Douglas weights invariant to addiction; vary `b` instead | **Do, but better.** Fully fixed preferences — see plan §4.2 for why varying `b` will not reproduce the 44%/11% gap | M |
| A9 | Loss-of-consortium modelling is ad hoc and drives the ranking; present welfare and mortality as two dimensions | **Do.** Cut κ_cons, two columns, plus the C2 externality | M |
| A10 | TF-as-voucher-conditionality omits that the program actively treats SUD before housing | **Do.** Same as R1 1(b) | M |
| A11 | The policy is unlikely to be perfectly enforceable | **Do.** Same as R1 4(a)/(b) | M |
| A12 | Model fit never shown; non-targeted moments missed | **Do.** Same as R1 2(a)–2(c) | F/M |
| A13 | Key elasticities: drug use → housing access; homelessness → addiction. Match them | **Do.** The core ask | C |
| A14 | Connect to Constantini (2025), Cohen (2024), Brounstein & Wieselthier (2026), Abramson (2026), Humphries et al. (2026) | **Do**, and **note the Constantini conflict is the paper's biggest risk** — resolve it first. See plan §1 | C |
| A15 | Fiscal cost of homelessness appears high; compare to Abramson & van Nieuwerburgh | **Do.** Sensitivity on χ_H | C |
| A16 | Where does "37% of homeless have SUD" come from? Depends heavily on the homelessness definition | **Do.** Source it; state explicitly that you target *literal* homelessness and exclude doubling-up; flag the sensitivity | W |
| A17 | Calibration reads as a monotonous long-list; sources span decades; SCF waves unclear; no distinction between standard and novel parameters | **Do.** Full rewrite of the section, with a standard/novel column | W |
| A18 | Fewer counterfactuals in the body — experiments 1 and 3 are the most relevant | **Do.** Two in the body, rest to appendix | W |
| A19 | "Addicted" → "suffering from substance use disorder" | **Do.** Global replace | W |
| A20 | Are there direct productivity effects of SUD on productivity? | **Do (small).** Currently SUD affects employment *transitions* but not productivity conditional on working. Either add a wage penalty or justify the omission — evidence exists | M |

---

## Cross-cutting: what one change answers the most

| Change | Comments resolved |
|---|---|
| **Fixed preferences across SUD status** | R2 C5, R3 M2a, AE A8 — and strengthens R1 1(d) |
| **Homelessness externality replacing κ_cons** | R1 3(a), 3(b), 3(c), R2 C2, R3 M2c, AE A9 |
| **Channel-shutdown ladder** | R1 1(d), 1(e), R2 C4, R3 M2b, M2c, AE A1 |
| **Drop homeownership + housing GE** | AE A4, A5, R2 D1 — and buys the compute for everything else |
| **Endogenous treatment** | R1 1(b), AE A10 — the single most damning gap |
| **Mental health** | R1 1(a), R1 2(c)(ii) |
| **Make p_v an equilibrium object** | R1 1(c), R3 M2d, AE A5 |
| **Model fit table** | R1 2(a), 2(b), AE A12 |

Six model changes and one table cover roughly two-thirds of the substantive comments. The
remainder is writing, plus the elasticity-targeting work that all four documents converge on.
