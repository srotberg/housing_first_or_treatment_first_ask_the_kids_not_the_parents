# Parameter audit: every parameter, its source or its target

The AE objected that the paper shows "no distinction between parameters that are
standard in the literature, versus those that are new to the paper." This is that
distinction, made explicitly, for every parameter in `params.f90`.

**Status key**
- **L** — standard in the literature, cited
- **D** — set directly from data
- **C** — internally calibrated, with the moment it is assigned to
- **E** — determined in equilibrium
- **⚠** — not yet credibly disciplined

---

## A. Preferences and prices

| Parameter | Value | Status | Source / target |
|---|---|---|---|
| `sigma` | 2.0 | **L** | CRRA, standard |
| `xi_tax` | 0.85 | **L** | HSV progressivity, Heathcote–Storesletten–Violante (2017) |
| `r` | 0.03 | **L** | Kaplan, Mitman and Violante (2020) |
| `beta` | 0.96 | **C** | → net worth / income. **Currently fixed; must be calibrated** (§D) |
| `theta_h` | — | **C** | → aggregate housing cost / income = 0.212 (SCF, all households) |
| `theta_v` | — | **C** | → drug spending / income given SUD = 44% |
| `b_dm(1,1)` | — | **C** | → drug participation |
| `b_dm(2,·)` | 1e-3 | **C** | → keeps the interior solution so `theta_v` pins the expenditure share |
| `aleph` | — | **C** | → **should target VSL = $7.5m** (the paper's own approach), not the SUD income ratio (§D) |
| `p_rent` | — | **C** | → share with housing cost > 50% of income = 17.5% |
| `psi1` | — | **E** | Normalisation so `p_v` = 1 at the benchmark |
| `tau_l` | — | **E** | Government budget balance |
| `bequest` | — | **E** | Assets of the deceased |

## B. Programme rules — all institutional, none free

| Parameter | Value | Status | Source |
|---|---|---|---|
| `kappa_V` | 0.5 | **D** | HUD rule: eligibility below 50% of area median income |
| `kappa_r` | 0.3 | **D** | HUD rule: 30% tenant contribution |
| `prob_ui` | 0.30 | **D** | Insured unemployment / total unemployment, FRED 2014–24 |
| `ui_replace` | 0.50 | **D** | Standard US replacement rate |
| `prob_V` | — | **C** | → voucher recipients / income-eligible = 26.6% (HUD) |
| `cfloor_share` | 0.10 | **C** | → **should target SNAP spending / GDP = 0.42%** (§D) |

## C. Transitions and hazards

| Parameter | Value | Status | Source / target |
|---|---|---|---|
| `pi_ue_base` | 0.55 | **L** | Annualised job finding, Krueger, Cramer and Cho (2014) |
| `pi_eu_base` | — | **C** | → unemployment rate = 4.9% |
| `kappa_ue_h` | 0.8 | **L** | Desmond and Gershenson (2016) |
| `kappa_ue_d` | — | **C** | → unemployment rate given SUD = 26.9% |
| `kappa_phi_h` | 1.6 | **D** | Meyer et al. (2025): 60% excess mortality for the unhoused |
| `kappa_phi_d` | 6.9 | **L/⚠** | Within Degenhardt et al. (2011) SMR range 2.5–9.8, but the paper calibrates it internally to the drug-price elasticity. **Should be calibrated, not fixed** (§D) |
| `heavy_ratio` | 6.48 | **D** | NSDUH: heavy users 6.48× more likely to have SUD |
| `pi_d_low` | — | **C** | → SUD rate |
| `vbar` | 0.05 | **C** | → **should target the light-experimenter share = 0.87** (§D) |
| `recover_housed` | 0.025 | **D/⚠** | Vaillant (1995) 10-year recovery. **The AE questions applying alcohol recovery rates to drug SUD** — see §D |
| `recover_mult_hl` | — | **C** | → SUD share of the homeless |

## D. Serious mental illness

Documented in full in `MENTAL_HEALTH.md`.

| Parameter | Value | Status | Source / target |
|---|---|---|---|
| `smi_prevalence` | 0.055 | **D** | SMI among US adults, NSDUH 2023 |
| `mh_onset` | derived | — | `mh_recover · p/(1−p)`, so prevalence is never disturbed |
| `mh_recover` | — | **C** | → SMI share of the homeless = 25% (Gutwinski et al. 2021) |
| `kappa_ue_m` | — | **C** | → employment rate given SMI = 30% |
| `prod_pen_m` | — | **C** | → homeless income / average = 19.1% |
| `kappa_phi_m` | 2.50 | **D** | Standardised mortality ratio for SMI, 2–3 |
| `disab_income` | 0.25 | **⚠** | Order of magnitude only. Should come from mean SSI/SSDI relative to mean income |
| `rec_mult_m` | 0.50 | **⚠** | Direction certain, magnitude invented |
| `mh_b_ratio` | 0.25 | **⚠** | Should target **co-occurring SUD among adults with SMI** (SAMHSA NSDUH detailed tables) |

## E. Policy and fiscal

| Parameter | Value | Status | Source / target |
|---|---|---|---|
| `chi_D` | 0.212 | **D** | CEA (2017): ~$30,000 per person per year |
| `chi_H` | 0.252 | **D/⚠** | National Alliance to End Homelessness. **R2 and R3 both judge it too high; the AE asks for comparison with Abramson and van Nieuwerburgh.** Run as sensitivity |
| `prod_pen_d` | 0.80 | **⚠→C** | See below. Reassign to → SUD income / average = 68.7% |
| `treat_cost` | 0.05 | **⚠** | Needs a treatment-cost source |
| `treat_gain` | 3.0 | **⚠** | **Almost certainly far too large — see below** |
| `detect_prob`, `false_pos` | 1.0, 0.0 | — | Policy-experiment parameters; report as sensitivity (R1 4a, 4b) |
| `drug_supply_elasticity` | 0.5 | **⚠** | No credible estimate exists. Report as a bounded sensitivity; perfectly elastic *is* the paper's current assumption |
| `kappa_ext` | 0.0 | **⚠** | Off. R2 noted introducing it "would require a new calibration moment" |

---

## The three that most need fixing

### 1. `treat_gain = 3.0` — this is the Treatment First mechanism

Tripling the recovery hazard is not supported. The evidence:

- Remission from SUD overall: **35.0–54.4%** at a mean 17-year follow-up
- Remission following specialty treatment: **47.6%** (50.3% in studies since 2000)
- Contingency management versus a comparison treatment: **OR = 1.22**

The first two are not a treatment effect — they are different populations with
different selection. The only clean randomised number is the third, and it implies
a *modest* effect, not a tripling.

**This parameter deserves special treatment because the paper's conclusion runs
through it.** R1 predicted that adding endogenous treatment would strengthen TF;
how much it strengthens it is exactly `treat_gain`. Set it from the RCT evidence
(~1.2–1.5) and **report the TF result across a range**, identifying the value at
which the ranking would change. That is the same discipline R1 forced on κ_cons.

### 2. `aleph` should target VSL, not the income ratio

The paper's own approach is to calibrate ℵ so the model-implied VSL equals $7.5m
(Viscusi and Aldy 2003; EPA 2010). That is an external target and it is better
than the internal one currently used. It also matters more than it looks: the
scan in `INTUITION_MODEL.md` shows the income gradient of drug use only inverts
once ℵ is large, so **the VSL target is what generates the paper's central
mechanism**, not a normalisation.

Requires computing model VSL — the marginal rate of substitution between
consumption and survival — and stating the income denominator used for the
dollar conversion explicitly.

That frees `prod_pen_d` to be calibrated to the SUD income ratio (68.7%).

### 3. `prod_pen_d` — the honest answer is that the wage effect is contested

The AE asks (A20) whether there are direct productivity effects of SUD. The
robust findings are on the **employment** margin — roughly 50% more unscheduled
absence and 44% higher turnover — while estimates of the wage penalty
*conditional on working* are mixed, with some of the older literature finding
positive effects for casual use.

So: set `prod_pen_d = 1.0` in the baseline (no direct wage effect, employment
channel only), calibrate a version to the SUD income ratio as the alternative,
and say plainly in the paper that the wage evidence is contested. That answers
A20 honestly rather than inventing a number.

---

## Still to reassign in code

| Parameter | Assign to |
|---|---|
| `beta` | net worth / income (SCF) |
| `vbar` | light-experimenter share = 0.87 (NSDUH) |
| `cfloor_share` | SNAP spending / GDP = 0.42% |
| `kappa_phi_d` | drug-price participation elasticity = −0.63 (the paper's approach) |
| `aleph` | VSL = $7.5m |
| `prod_pen_d` | SUD income / average = 68.7% |

Once these are wired, every parameter is either cited, taken from data, or
attached to a named moment — with four exceptions that should be reported as
sensitivities rather than calibrated: `treat_gain`, `drug_supply_elasticity`,
`chi_H`, and the detection parameters.

---

## Sources

- [Fleury et al. (2016), remission from substance use disorders: systematic review and meta-analysis](https://pubmed.ncbi.nlm.nih.gov/27614380/)
- [White (2012), recovery/remission from substance use disorders](https://www.naadac.org/assets/2416/whitewl2012_recoveryremission_from_substance_abuse_disorders.pdf)
- [Contingency management long-term abstinence meta-analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC8034391/)
- [Gutwinski et al. (2021), mental disorders among homeless people](https://journals.plos.org/plosmedicine/article?id=10.1371%2Fjournal.pmed.1003750)
- [İmrohoroğlu and Zhao (2022), "Homelessness"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4308222)
- [CEA (2017), the underestimated cost of the opioid crisis](https://trumpwhitehouse.archives.gov/sites/whitehouse.gov/files/images/The%20Underestimated%20Cost%20of%20the%20Opioid%20Crisis.pdf)
- [Brookings, the economic impact of the opioid epidemic](https://www.brookings.edu/articles/the-economic-impact-of-the-opioid-epidemic/)

Figures drawn from search-result summaries where the primary domain is blocked
from this environment; verify against the papers before they enter the draft.
