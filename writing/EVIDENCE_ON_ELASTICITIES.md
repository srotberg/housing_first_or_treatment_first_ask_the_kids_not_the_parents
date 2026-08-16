# The two key elasticities: what the evidence actually says

R2: "all of the welfare results rest on whether the model has an accurate elasticity
of drug use to housing access." R3 and the AE agree. Here is what the uploaded
evidence supports, and where it cuts against the paper.

---

## 1. Milby et al. (2005) — read the results, not the abstract

196 cocaine-dependent homeless adults in Birmingham, randomised to three arms, all
receiving identical day treatment:

| Arm | n | Meaning in this paper's terms |
|---|---|---|
| NH — no housing | 66 | no assistance |
| NACH — housing, no abstinence condition | 67 | **Housing First** |
| ACH — housing contingent on abstinence | 63 | **Treatment First** |

**Mean consecutive weeks abstinent, out of 24:**

| NH | NACH | ACH |
|---|---|---|
| **4.48** (SD 4.98) | **6.60** (SD 6.32) | **8.32** (SD 6.79) |

ANOVA group effect P = .0020. Pairwise:

- NH vs ACH — **P = .0004**, strong
- NH vs NACH — **P = .058**, marginal
- **NACH vs ACH — P = .091, not significant**

The GEE models tell the same story: both housed groups significantly exceed NH in
phases 1 and 2, and **"the ACH and NACH groups did not differ from one another."**
ACH exceeded NACH in 22 of 24 weeks, but the authors state the difference "was
small and not statistically significant."

**The abstract's claim that ACH beat NACH holds only "after control for treatment
attendance."** In the raw randomised comparison it does not.

Treatment attendance, days over both phases: NH 32.0, NACH 56.6, ACH 50.1. Both
housed arms far exceed NH; NACH and ACH do not differ (P = .21).

### What this licenses as a calibration target

**Target the housing-access elasticity. Do not target the conditionality effect.**

- Housing access: 4.48 → ~7.5 weeks abstinent, roughly **+65%**, well identified.
  This is the moment R2, R3 and the AE all asked for.
- Conditionality: 6.60 → 8.32 weeks, **+26%, P = .091.** Positive, imprecise. Use it
  as a validation check with the confidence band shown, not as a target.

Calibrating to a point estimate that the source paper reports as insignificant
would be exactly the sin R1 attacked elsewhere.

---

## 2. This reconciles the apparent contradiction in the literature

The Accommodation-based interventions review finds "no clear differences between
the Housing First group and the control group on outcomes related to mental
health, quality of life and substance use." That looks like it contradicts Milby.
It does not:

- **Milby's counterfactual is literally no housing.** Large effect.
- **HF RCTs compare HF to "usual services"**, which typically already include
  shelter or transitional housing. Small or null effect.

So the elasticity of drug use with respect to housing access is **large at the
extensive margin (nothing → something)** and **near zero at the intensive margin
(some housing → permanent housing)**. The model should reproduce both, and that
is a much sharper test than either number alone.

---

## 3. Where the evidence cuts against the paper's headline

Stated plainly, because a referee will:

| Question | Evidence |
|---|---|
| Does housing reduce drug use? | Yes, versus no housing (Milby) |
| Does conditioning on sobriety add to that? | Positive point estimate, **not significant** (Milby, P = .091) |
| Does TF improve long-run health? | **No effect** (Costantini, ~300,000 veterans, IV) |
| Does HF improve long-run mortality? | **−4.6pp over 3 years**, s.e. 1.7 (Costantini) |

The paper concludes universal TF dominates. The best available evidence says the
conditionality benefit is imprecisely estimated and the housing benefit is large
and well identified. **The revision has to confront this directly rather than cite
Milby's abstract as support.**

The defensible position remains the generosity result: expanding coverage
dominates, and conditionality is second-order and uncertain. That is consistent
with everything above, and it is still a paper.

---

## 4. Adapting Corbae et al. to a homelessness externality

Their externality is **not** about homelessness. `U_h = q · E(Q)`: housed utility
scales with aggregate neighbourhood housing *quality*, and they say explicitly
that it "operates through the quality of neighboring units, not the income or
employment of the residents of those units." Unhoused utility is normalised to
zero. Identification comes from Autor, Palmer and Pathak's Cambridge rent
decontrol: when control was lifted, *uncontrolled* units appreciated more in
neighbourhoods with many controlled units, and that differential pins the spillover.

**The transferable part is the identification logic, not the functional form:**
use a shock that changes local exposure, then read the externality off the
differential response of *unaffected* units. Applied to homelessness, that is the
shelter-siting hedonic literature — which exists and has moved past naive
correlations.

### What that literature shows, and why it is better than a single number

- Naive estimates: shelters reduce nearby property values by about **6.33%**
- **Spatial difference-in-differences accounting for endogenous siting: no
  significant overall effect**
- Effects are local — concentrated within about 400 m, dissipating beyond
- **Heterogeneity is the useful part: temporary emergency shelters reduce property
  values, while permanent supportive housing raises them**

That last finding maps directly onto this paper's policy margin. **Permanent
supportive housing is HF-like; temporary transitional shelter is TF-like.** So the
externality is not a single parameter multiplying a headcount — it plausibly
differs in *sign* between the two policies being compared. That is a substantive
modelling point, and it cuts in favour of HF for a third independent reason.

### The caveat that must be stated

Hedonic capitalisation measures **local, avoidable** disamenity: what people pay to
live further away. This model has no geography, so nobody can avoid anything, and
a capitalisation estimate does not map cleanly onto an aggregate public bad.
Porting a hedonic coefficient into a non-spatial model is an assumption, not a
calibration.

**Recommendation:** keep `kappa_ext = 0` in the baseline, report the sensitivity
range, and use the PSH-versus-emergency-shelter heterogeneity as the *qualitative*
argument — that the sign of the externality differs by policy type — rather than
pretending to a point estimate the spatial literature does not deliver.

---

## Sources

- Milby, Schumacher, Wallace, Freedman and Vuchinich (2005), *To House or Not to
  House*, [AJPH 95(7):1259–65](https://ajph.aphapublications.org/doi/full/10.2105/AJPH.2004.039743)
- Costantini (2025), *Housing First or Treatment First? Evidence from the VA's
  homelessness programs*
- [Accommodation-based interventions for people experiencing homelessness — systematic review](https://pmc.ncbi.nlm.nih.gov/articles/PMC8356295/)
- Corbae, Glover and Nattinger, [*Equilibrium Evictions*](https://www.nber.org/papers/w32898)
- [Sitti, Horn and Berrens, *The Effect of Homeless Shelters on Property Values*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5239331)
- [Ridgeway, *Effect of Emergency Winter Homeless Shelters on Property Values*](https://crim.sas.upenn.edu/sites/default/files/Ridgeway_Effect%20of%20Emergency%20Shelters-v5_1.2.2018.pdf)
