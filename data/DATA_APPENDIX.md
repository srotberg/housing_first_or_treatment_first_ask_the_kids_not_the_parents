# Data appendix

Every number the calibration takes from outside the model, with the dataset it
comes from, its vintage, its universe, and the computation that turns it into the
figure reported in the paper. The paper's calibration section points here rather
than carrying this detail, so that any target can be reproduced from the public
microdata without reading the paper.

Two conventions hold throughout. **The unit is a household**, because the model's
agent is one, so counts of people are converted before use. And **the universe is
stated for every target**, because several of these numbers differ by a factor of
two depending on whether the denominator is people or households, adults or all
ages, renters or all occupants.

**Nothing here has to be downloaded.** The replication package carries the datasets
themselves, so every number below can be recomputed from the files already in this
folder. `raw/` holds the source exports exactly as they came from HUD, CDC WONDER, the
Federal Reserve, the Census, SSA, BLS and SAMHSA; `NSDUH_2024.dta` and `SCF_2022.dta`
are the two microdata extracts; and the scripts here turn all of it into the small
CSVs the Fortran reads. `README.md` lists
the regeneration commands and `FINDINGS.md` records what each source implied when
it arrived, including the targets it called into question.

---

## 1. Who uses drugs

**θ, the weight on drugs in utility — 35 percent of income spent on the drug,
averaged across users.** NSDUH 2024, adults 26 and over. The moment divides drug
spending by income over every household that buys any drug, not the subset
carrying a disorder. Users without a disorder spend about 11 percent of income on
the drug and users with one about 44 percent. The share of users carrying a
disorder is the disorder rate over the participation rate, 0.0368/0.0513 = 0.717,
so the weighted average is 0.717 × 0.44 + 0.283 × 0.11 = 0.347, reported as 35
percent. The weight comes from the two NSDUH rates the model already targets
rather than from the conversion rate; see the note under λ for why those two do not
agree with each other.

*The stylized model targets 20 percent, not 34.7, and the difference is not a data
disagreement.* A period there is thirty years, so every consequence of using arrives
once, at the end, rather than compounding annually. Buying the same spending share
therefore takes a larger weight on the drug, and past about θ = 0.22 the drug becomes
too valuable to be deterred by a distant death: at θ = 0.24 the average user earns
four times the population average and the income gradient the model exists to explain
has reversed. With the whole model recalibrated at each θ the share runs 15.2, 18.4,
20.2, 21.6 and 24.2 percent at θ from 0.18 to 0.23, and the mortality channel stops
reversing the gradient on its own somewhere between 0.22 and 0.23. Twenty percent is
what the two period model can carry with the mechanism intact.

**b, whether a household uses — 5.13 percent participation.** NSDUH 2024, past
year illicit drug use disorder module, adults 26 and over. Restricting to 26 and
over matters: including 12 to 25 year olds roughly doubles the rate, and the model
begins at 26.

**λ, the SUD hazard per unit used — a 3.68 percent adult disorder rate.** NSDUH
2024, adults 26 and over. This is the level, not the conversion rate from use to
disorder. The two published numbers are not mutually consistent: a conversion of
33.2 percent applied to a 5.13 percent participation rate implies a disorder rate
near 1.7 percent, not 3.68. The level is the better measured of the two, so it is
the one matched, and the conversion the model implies, 71.7 percent, is reported
rather than imposed. The stylized model is calibrated to the same 3.68 percent
level, having previously targeted the 33.2 percent conversion, so the two models no
longer carry inconsistent numbers for the same object.

**ℵ, the flow value of being alive — a value of a statistical life of \$7.5m.**
The range surveyed in Viscusi and Aldy (2003), converted to current dollars and
expressed as a multiple of mean household income.

---

## 2. What using and being homeless cost

**ρ_d, earnings lost to a disorder — a 50 percent employment rate among the
homeless.** HUD 2023. The moment is employment among literally homeless adults.

**κ_ued, the employment multiplier for a disorder — a 16.25 percent unemployment
rate given a disorder.** NSDUH 2024, adults 26 and over with a past year disorder.

**h₁, the service flow of homelessness — a 0.399 percent homelessness rate.** HUD
point in time count, 2023, **converted to households**: 467,020 homeless
individuals at one household each, plus 57,563 homeless family households, against
131,332,360 occupied units. The person rate is 0.195 percent and is the wrong
denominator for this model, since the agent is a household. `FINDINGS.md` section 1
records the full year by year series and why 2023 rather than 2024 is used.

**c̲, the food stamp consumption floor — food stamps at 0.42 percent of labour
income.** USDA SNAP average benefit against average labour income.

**π_V, the voucher lottery probability — 26.6 percent of eligible households
receiving one.** HUD Picture of Subsidized Households, 2023, **tenant based
voucher row only**. The all programmes summary averages over public housing and
project based assistance, which are not the model's voucher; using it would
overstate coverage.

---

## 3. The mental illness chain

**λ_m, the chance of recovering from mental illness — a 25 percent SMI share of
the homeless.** Gutwinski et al. (2021), a meta regression of prevalence among
homeless people in high income countries.

**ρ_m, earnings lost to mental illness — labour income of the homeless at 19.1
percent of average.** The moment is the ratio of mean labour income among the
homeless to the population mean. Note that this and ρ_d are both homeless
conditional moments, so the two penalties are identified jointly rather than
separately; the paper says so.

**κ_uem, the employment multiplier for mental illness — a 30 percent employment
rate given SMI.** NSDUH 2023, adults with serious mental illness, defined by
substantial functional impairment rather than any mental illness. The distinction
is load bearing: any mental illness covers roughly a quarter of adults, and a state
that halves productivity cannot sensibly cover a quarter of the population.

**p_m(j), the age profile of SMI prevalence — 5.5 percent overall.** NSDUH 2023.
The object matched is the profile by age; the 5.5 percent is the level it
integrates to. The onset hazard is not read off directly but backed out of the
profile and the exit rate, so the whole profile is reproduced by construction.

---

## 4. Recovery and treatment

**μ_H, the recovery multiplier when homeless — 1.473.** Milby et al. (2005), a
randomised trial on cocaine dependent homeless adults: 6.60 weeks abstinent in the
housed arm against 4.48 in the unhoused arm, so 6.60/4.48 = 1.473. This is the
causal estimate the paper leans on hardest, and the same trial supplies the
treatment effect on recovery.

**τ̄ᵘ, the utility cost of treatment — 24 percent treatment take up.** NSDUH 2023,
take up given a disorder.

---

## 5. Externalities

**ω, the weight on the child — an 18.3 percent rise in use when altruism is
switched off.** NSDUH 2024. Past month use among parents is 0.845 of use among non
parents, with parents reweighted to the non parents' joint distribution of age,
income, sex and marital status, so the gap is behaviour rather than composition.
The model's counterfactual raises use **from the parent level**, so the rise is
1/0.845 − 1 = 0.1834 rather than 1 − 0.845 = 0.155. Getting the denominator wrong
here understates the target by about fifteen percent.

**δ_d, the child's earnings penalty for a parent's disorder — a child disorder
ratio of 3.** McGovern et al. (2023) report children of a parent with a disorder
acquiring one at two to four times the rate of other children; the midpoint is the
target. The model counterpart contracts the newborn productivity distribution
conditional on the parent's disorder against the disorder rate at each productivity
node, at the same parental housing status, so the comparison isolates the disorder.

**δ_h, the child's earnings penalty for homelessness — 31 percent.** Chetty et al.
(2016): children who moved to a lower poverty neighbourhood before age thirteen
earned 31 percent more as adults. Set externally, not calibrated, and the asymmetry
with δ_d is deliberate. No study measures what a parent's SUD does to a child's
lifetime earnings, so δ_d has to be calibrated inside the model against a moment the
literature does measure. The housing-to-earnings link is measured directly, so δ_h
does not.

*What the model implies, and does not target.* At δ_h = 0.31 the child of a homeless
parent is 2.02 times as likely to be homeless itself, reported as a validation moment
rather than a target.

*What the model implies, and the direct measurement it is checked against.* At
δ_h = 0.31 the child of a homeless parent is 2.02 times as likely to be homeless itself
in the stylized model, reported as a validation moment rather than a target. (The
quantitative model carries its own δ_h and produces its own ratio.)

The measurement to check it against is Bassuk, Buckner, Weinreb, Browne, Bassuk, Dawson
and Perloff (1997), *American Journal of Public Health* 87(2), 241–248 — a case-control
study of 220 homeless mothers and 216 low-income housed mothers in Worcester,
Massachusetts. Both arms are poor, so the comparison isolates transmission from the
poverty that accompanies it, and no population base rate is needed:

| childhood factor | homeless | housed poor | odds ratio | 95% CI |
|---|---|---|---|---|
| primary female caretaker ever homeless | 14.2% | 8.3% | 1.80 | [0.98, 3.33] |
| primary male caretaker ever homeless | 10.3% | 4.4% | 2.41 | [1.12, 5.18] |
| ever in foster care | 19.6% | 8.3% | 2.67 | [1.49, 4.80] |

Odds ratios and intervals computed from the published percentages and the two sample
sizes; homelessness is rare in the population, so the odds ratio approximates the risk
ratio. The model's 2.02 sits between the two parental measures, at a δ_h taken from an
earnings estimate that knows nothing about homelessness transmission. It is US data,
matching the model's calibration.

*Why a general-population comparison is the wrong one.* Flatau, Conroy, Spooner, Eardley
and Forbes (2013) report that 43.0 percent of non-Indigenous Australian
homelessness-assistance clients had parents who had experienced homelessness (69.0
percent for Indigenous clients). Turning a conditional share into a ratio needs a
population base rate, and against one the implied ratio is 5 to 6 — but that credits the
housing penalty with everything else that differs between poor children. Cobb-Clark and
Zhu (2015) show the difference is substantial: among Journeys Home respondents, all on
income support, those first homeless at 15 or below were 2.6 times as likely to have
been in foster care (42.5 against 16.1 percent), and markedly more likely to have
suffered physical or sexual abuse or had a parent serve jail time. A case-control design
differences all of that out, which is why Bassuk is used and Flatau is not.

*Journeys Home.* Its microdata would give an independent poverty-held-fixed ratio, from
`HFHLAGE < 18` crossed with `JHSTRATA`, but access needs a DSS application and possibly
a fee, and it has no parental-homelessness question so it could not reproduce Flatau in
any case. The variables and the access route are recorded in
`data/journeys_home/README.md`.


What can be said is that δ_h is not asked to carry more than the earnings evidence
supports, and that if any of the observed gradient is selection rather than transmission
— which it must partly be — the model's value is the conservative one.

*Correction.* An earlier version of this appendix read the 5–6 figure as the model's
target and concluded the model understated the channel by two thirds. That compared a
selection-confounded data ratio with a pure income effect and was wrong.

An earlier version recorded δ_h as calibrated to a ratio of 2. That target had no
source; it was chosen because it reproduced Chetty. The dependence has been inverted
so the sourced number is the input.

The stylized model is calibrated to the same ratio of 3 and needs δ_d = 0.45 to reach
it. That is a larger penalty than the earnings literature measures directly, 24
percent in Nilsson (2017) and 31 in Chetty et al. (2016), because the model is being
asked to reproduce an epidemiological ratio rather than an earnings coefficient and
income is its only channel from parent to child. It should be read as the reduced
form of the whole childhood rather than as an estimate of a wage effect. It was
previously set at 0.30, which delivered a ratio of 2.1, the bottom of the McGovern et
al. range rather than its midpoint.

---

## 6. Preferences and the housing ladder

**γ, the Cobb-Douglas weight on housing — housing at 26.8 percent of expenditure
net of drugs.** Consumer Expenditure Survey 2024, shelter plus utilities over total
expenditure. This is an **expenditure** share and not a rent to income ratio: a
Cobb-Douglas weight equals the expenditure share exactly, and income and
expenditure differ by saving. It is the same moment and the same definition the
stylized model uses.

**β, the discount factor — wealth over output of 3.** BEA fixed assets against NIPA
output. Household wealth in the model is financial wealth alone, since the rental
stock sits on the rental companies' books, so the counterpart in the accounts is
the private capital stock rather than measured household net worth. Private
nonresidential fixed assets are roughly two years of output and all private fixed
assets roughly three; three is the figure used and the run reports if β pins at a
bound trying to reach it.

**h̲ and h̄, the two ends of the rental ladder — 13.2 and 62.7 percent.** ACS 2023,
table B25042, tenure by bedrooms, **universe occupied housing units**, N =
131,332,360. The six bedroom categories are collapsed to three: none or one, two,
and three or more, giving 13.2 / 24.1 / 62.7. Table B25041 covers all housing units
including about ten percent vacant and is the wrong universe; it is kept in `raw/`
only so the difference is checkable. Since the universe is occupied units, the model
counterpart conditions on being housed and the homeless are in neither denominator.

**Two renter cost shares, untargeted.** ACS 2023: 49.5 percent of renter households
spend more than thirty percent of income on housing and 26.5 percent more than half.
These are reported as checks rather than matched, because a cost share is a budget
consequence of the housing grid rather than the grid itself.

**ω_ℓ, the weight on leisure — average hours worked of 40 percent.** Guvenen et al.
(2023).

**σ_y, the dispersion of productivity — 0.20 in logs.** Storesletten et al. (2004).
Productivity is a permanent draw in the benchmark, so only the dispersion is
operative.

---

## 7. Employment and the fiscal side

**π̄ᵉᵘ, the job separation rate — a 4.85 percent unemployment rate.** BLS Current
Population Survey, 2014 to 2024 average, so that the target is not read off a single
year of the cycle.

**π̄ᵘᵉ, the job finding rate — 0.55 annually.** Krueger et al. (2014), exit rates
from matched CPS panels.

**τ_ℓ, the level of the labour income tax — an average labour income tax rate of
22.4 percent.** McDaniel (2007), which is also what Guvenen et al. (2023) use. The
parameter the code moves is the retention scale in the tax function, which is the
inverse of what its name suggests; raising it lowers the average effective rate.

**Set from statute rather than estimated.** ξ = 0.85 from Heathcote et al. (2017);
τ_k = 15 percent, the statutory US rate on long term capital gains and qualified
dividends (IRS Topic 409); ψ = 0.5 and ȳ = 1 times average income, from the
Department of Labor's comparison of state unemployment insurance laws; κ_V = half of
median income, HUD's very low income limit, and κ_r = 30 percent of income, the
tenant contribution under the Housing Choice Voucher programme.

**φ̄(j), baseline survival — SSA period life table 4.C6**, ages 26 to 85, sexes
combined by **survivor weight** rather than averaged. Averaging the two columns is
wrong because the surviving population is increasingly female with age.
`make_life_table.py` does the combining and writes `us_life_table.csv`.

---

## 8. The externally set parameters, one at a time

The sections above cover every target the model is calibrated *to*. This section
covers every parameter set *from* a source without a model counterpart, so that the
two tables in the paper are documented in full and nothing is left to be inferred.

### Mortality

**κ̄_φd, increased mortality with a disorder — 8, from a range of 6 to 10.**
Hjorthøj et al. (2023), a review of excess mortality among people with substance use
disorders; the midpoint of the reported range is used.

**κ_φH(j), increased mortality when homeless — 4.41 falling to 1.09 by age.**
Baggett et al. (2013), standardised mortality ratios for homeless adults in Boston,
which run 9.1 at the youngest ages to 1.1 at the oldest. The model applies the
profile scaled so that the aggregate excess matches; `FINDINGS.md` section 10 records
that an earlier placeholder understated this by a factor of five.

**κ_φm, mortality multiplier for mental illness — 2.50.** Olfson et al. (2015),
premature mortality among adults with schizophrenia and other serious mental illness.

### The mental illness chain

**ι, the multiplier a disorder puts on the onset of mental illness — 2.** Nielsen et
al. (2017), Danish population registers, which follow the whole population and so
identify the effect of a disorder on subsequent onset rather than the cross sectional
association.

**μ_m, the recovery multiplier under dual diagnosis — 0.82.** Bradizza et al. (2006),
a review of relapse among people carrying both a disorder and a mental illness.

**ζ_DI, the disability replacement rate for mental illness — 0.25.** SSA 2023, SSDI
and SSI award rates and benefit levels for beneficiaries qualifying on a mental
disorder.

### Recovery and treatment

**π̄_r, the baseline recovery rate — 0.025 a year.** Vaillant (1995), the ten year
remission rate from the natural history of alcoholism, annualised. This is
unassisted remission, which is what the baseline hazard is meant to be.

**g, the treatment effect on recovery — 1.35.** Milby et al. (2005), the odds ratio
from the same randomised trial that supplies μ_H, so the level and the housing
gradient come from one experiment rather than two.

### Externalities

**δ_h, the child's earnings penalty for homelessness — 0.31.** Chetty et al. (2016);
see section 5.

**κ_x, the disamenity of aggregate homelessness — 0.20 percent of annual earnings,
which enters as 0.002.** Loubière et al. (2020), a contingent valuation across
Europe: €57 a year among the 42 percent of respondents willing to pay anything,
against €23 averaged over all respondents. The higher figure is taken as the
baseline, because it is the one least kind to Treatment First: a larger disamenity
loads whichever policy houses more people. The lower figure, €23, is 0.08 percent
and enters as 0.0008; an earlier version of this file gave that number as the value
of the 0.20 percent baseline, which was wrong.

**κ_x is not yet in the Fortran.** It appears in the household's problem in the
paper and `grep -ci kappa_x` over the source returns zero. Because the headcount is
aggregate and taken as given, its absence cannot move any policy function, so no
calibrated moment depends on it; what it changes is the welfare comparison across
steady states, which is where the paper uses it.

### Employment and labour supply

**κ_ueH, the employment multiplier when homeless — 0.80.** Desmond and Gershenson
(2016), on job loss following involuntary housing loss.

**σ_ℓ, the curvature on leisure — 3.00, chosen to produce a Frisch elasticity of
0.5.** Chetty (2012). The Data column of the paper's table reports the elasticity
being targeted, 0.5, and the Value column the curvature that delivers it.

**ε(j), the age profile of efficiency.** The exponential of a quadratic used by
Greenwood et al. (2025), exp{−(j−1)²/1800 + (j−1)/30} with j = 1 at age 26. It peaks
at age 56 having risen 65 percent, then falls 4 percent to the last working age.

### Preferences and the grid

**σ, risk aversion — 2.** Attanasio and Weber (2010).

**ς, the curvature of the rental ladder — 1.8.** Set rather than estimated. With
three rental sizes the size distribution carries two free numbers and the two ends
take them, so a third parameter chasing the same shares would not be identified. The
curvature places the middle rung a fraction (1/2)^ς of the way from the smallest size
to the largest, so 1.8 puts it 28.7 percent of the way up rather than the 50 percent a
uniform ladder gives. At the calibrated ends the three sizes stand at 1 : 1.46 : 2.59.

### The drug market

**ν_2, the drug supply elasticity — 1.46, which implies a curvature of
1 + 1/1.46 = 1.68.** Mace et al. (2020), estimated on Washington State
administrative data. No direct estimate exists for an illicit drug; cannabis is the
closest market because it remains a Schedule I substance federally, so even a
licensed producer works without interstate trade, without ordinary banking and under
prohibition. Cigarettes and gasoline share none of those frictions and are not used.

**ν_1, the supply shifter, and p_v, the drug price.** ν_1 is a pure normalisation,
chosen so that supply equals demand at p_v = 1 in the benchmark; it fixes units and
not behaviour. p_v is one at the benchmark by that normalisation and free in every
counterfactual, where it is an equilibrium object rather than a parameter.

**J_E, the last age at which use can begin — 55 in model terms, which is age 80.**
A restriction rather than an estimate. The model imposes certain mortality by age 85
to keep the age dimension manageable, so a household near the end knows death is
coming and a disorder costs it almost nothing; at the final age a disorder acquired
carries no consequence at all, only the flow benefit of using. The cap keeps use out
of that region. Sensitivity to raising it is reported once the model is calibrated.

### Statute

**ξ = 0.85**, tax progressivity, Heathcote et al. (2017). **τ_k = 0.15**, the
statutory US rate on long term capital gains and qualified dividends, IRS Topic 409
(https://www.irs.gov/taxtopics/tc409). **ψ = 0.50** and **ȳ = 1** times average
income, from the Department of Labor's comparison of state unemployment insurance
laws (https://oui.doleta.gov/unemploy/statelaws.asp). **κ_V = 0.50** of median
income, HUD's very low income limit
(https://www.huduser.gov/portal/datasets/il.html), and **κ_r = 0.30** of income, the
tenant contribution under the Housing Choice Voucher programme
(https://www.hud.gov/helping-americans/housing-choice-vouchers).

---

### The dispersion of permanent productivity

**sigma_y — the target is the bottom half's share of earnings, 17.2 percent.**
SCF 2022 (`SCF_2022.dta`), households aged 26 to 65 with positive wage and salary
income (`wageinc > 0`), weighted by `wgt`. That is 13,070 observations, 85.2 percent
of the age band by weight.

| moment | SCF 2022 |
|---|---:|
| bottom half's share of earnings | **17.2%** (the target) |
| top tenth's share | 41.1% |
| bottom tenth's share | 0.99% |
| p90/p10 | 10.0 |
| sd of log earnings | 1.036 |
| sd net of age effects | 1.019 |

sigma_y is **internally calibrated** in both models, against the first row. The share
falls monotonically in sigma_y, so one number identifies it, and both models are
calibrated to the same moment, which is what makes their income dispersion the same
object rather than two numbers that happen to be close.

**Why the share and not the sd.** The sd is the obvious moment and it is the wrong
one here, for two reasons. Discretisation: the life cycle model's productivity grid
has nine nodes spanning six standard deviations, so it cannot reproduce a continuous
sd, and the stylized model's grid is truncated at [0.12, 5.0], which costs dispersion
at both ends. Universe: the sd of log earnings mixes the permanent draw with a
transitory component the models do not have, so matching it directly would overstate
permanent inequality. A distributional share is robust to both. It is a property of
where the mass sits rather than of the tails the grid cannot represent.

For reference, the two adjustments that would take the raw sd to a comparable number:
the **age profile** comes out first, because the life cycle model carries it
separately in ε(j), and regressing log earnings on single age dummies leaves 1.019;
the **transitory variance** comes out next, and Storesletten et al. (2004) put it at
0.063, so √(1.036² − 0.063) = 1.005.

The universe is the household, per the convention above, so `wageinc` is household
wage and salary income rather than an individual's. **The universe matters here:**
restricting to positive earnings excludes the 14.8 percent of the age band with none,
which is the margin the model produces endogenously through unemployment rather than
through the productivity draw.

**What the models deliver.** The stylized model lands at sigma_y = 1.147 and hits
17.2 percent exactly; untargeted, its p90/p10 is 11.7 against 10.0 and its top tenth
share 39.3 against 41.1. The life cycle model's sigma_y is still converging at the
time of writing; at 1.00 its bottom half share is 16.5 percent and its top tenth
share 38.5 and its bottom tenth share 1.10 against 0.99. Its p90/p10 is not a useful
check, because nine nodes over six standard deviations put the tenth and ninetieth
percentiles on the second and eighth nodes: the shares are the moments to read.

**Productivity is not earnings in the life cycle model, and the gap is reported
rather than assumed away.** The distinction applies to the life cycle model only. In
the stylized model income *is* the draw, with no labour supply choice between them, so
its sigma_y matches this moment exactly. In the life cycle model what sigma_y governs
is the spread of *productivity*, while the moment measures the spread of *earnings*,
which is productivity times hours times whether the household works at all. Three things keep the mapping tight enough to use the moment. The
universe is households with positive earnings, so the extensive margin the model
produces through unemployment is held out rather than loaded onto sigma_y. The age
profile is removed separately, since the model carries eps(j) of its own. And what
is left, the dispersion of hours among the employed, is small against a spread of log
earnings above one. What remains shows up in the validation section: the model's own
earnings distribution, with hours and employment in it, is checked at the two tails,
the bottom tenth's share of 0.99 percent and the top tenth's of 41.1. The bottom
half's share is not a check, because it is the target.

---

## 9. The validation moments

None of these is fitted. Each is produced endogenously by the model and is a place
the model can be caught, so the derivation of the data side matters as much as for a
target. They are listed in the order the paper's validation section lists them.

**Homelessness rate for 25-34, 35-44, 45-54, 55-64 and 65+, and the shares of the homeless across those bands.** HUD point
in time count 2024, by age band, against Census population for the same bands.

| band | homeless | population | rate | share of homeless |
|---|---:|---:|---:|---:|
| 25–34 | 146,859 | 46,453,864 | 0.3161% | 26.0% |
| 35–44 | 153,849 | 45,539,224 | 0.3378% | 27.2% |
| 45–54 | 118,740 | 40,780,356 | 0.2912% | 21.0% |
| 55–64 | 104,007 | 41,661,725 | 0.2496% | 18.4% |
| 65–84 | 42,147 | 54,744,775 | 0.0770% | 7.5% |
| total | 565,602 | 229,179,944 | 0.2468% | 100% |

Two cautions. The 65+ column in the HUD file is named **"Over 64"**, and a first pass
that searched for "65" stopped at 64 and lost the band. And these are **person**
rates, unlike the household rate that h₁ is calibrated to, because the age
distribution is only published for people; the level therefore differs from the 0.399
percent target by construction and it is the **profile** that is the check.

**Returns to homelessness within 24 months — 17.4 percent.** HUD System Performance
Measures, national summary, 2024 (`raw/HUD_system_performance_measures_national_summary_2020_2024.pdf`).
The series runs 19.7 in 2020 and 16.6 in 2022, so 2024 is not an outlier. Nothing in
the calibration disciplines exit and reentry, so the model produces this from the
recovery and homelessness hazards alone.

**Drug poisonings as a share of deaths, 25 to 44 — about 20 percent.** CDC WONDER
provisional mortality, grouped by **MCD – Drug/Alcohol Induced Cause**, summing the
four drug poisoning rows: X40–X44 unintentional, X60–X64 suicide, X85 homicide,
Y10–Y14 undetermined. That is 81,834 deaths at ages 25–84. Dividing by the SSA
all cause probability at the same ages gives 20.4 percent at 25–29, 23.2 at 30–34,
22.3 at 35–39 and 18.6 at 40–44. **The grouping matters:** the ICD-10 113 Cause List
offers only unintentional poisoning, X40–X44, which understates the total by 7 to 10
percent at prime ages; that export is kept in `raw/` marked SUPERSEDED so the
difference is checkable.

**Bottom half's share of net worth — 2.52 percent.** Federal Reserve Distributional
Financial Accounts (`raw/FRB_DFA_net_worth_levels_by_percentile_1989_2026.csv`), most
recent quarter, bottom 50 percent share of household net worth.

**Housing costs above 30 and 50 percent of income — 40.6 and 17.5 percent.**
SCF 2022, computed by `SCF_cost_burdened_renters_code.txt`. The universe is renters
with positive income and positive rent, dropped of homeowners, and restricted to the
80th to 100th percentile band of the income CDF used in that script; rent to income is
annualised as 12 × rent / income. This is a different universe from the ACS 49.5 and
26.5 percent quoted with the rental ladder, which is why the two pairs of numbers
differ, and both are reported rather than reconciled.

**Standardised mortality ratio, homeless — 9.1, 4.5, 1.1 by band** (age weighted). Baggett et
al. (2013), ages 25–44, 45–64 and 65–84. This is the profile the age varying
homelessness multiplier is built from, so the check is that the model reproduces the
**shape**: the collapse by a factor of eight from the youngest band to the oldest is
selection, not protection.

**Tenant contribution rate — 31.2 percent.** HUD Picture of Subsidized Households
2023, **tenant based voucher row**: \$503 monthly tenant rent against \$19,368 annual
income. The all programmes figure is 29.3 percent and the project based figure 27.9,
so using the wrong row moves this by three points; the model's κ_r is set to 0.30 and
this is the check on it.

**Voucher holders with wages as main income — 28 percent.** Same source and
same row. It is a check on the model's employment composition among voucher holders,
which nothing targets.

**Income, moderate or severe SUD over average — 71.1 percent**, and
**labour force participation, SUD against clean — 65.8 against 61.5 percent.**
NSDUH 2024 public use file, computed by `NSDUH_2024_income_code.txt` and
`NSDUH_2024_probability_SUD_code.txt`, adults 26 and over, severity from the
DSM-5 based moderate or severe classification. The participation pair is the
informative one: participation is **higher** among those with a disorder, so the
earnings penalty in the model has to run through unemployment conditional on
participating rather than through dropping out of the labour force.

**Homeless at treatment admission — 14.5 percent**, **psychiatric problem
alongside SUD at admission — 43.1 percent**, and **working at all, homeless in treatment — 6.6
percent.** TEDS-A 2022 admissions public use file, 999,619 admissions aged 25 and
over. The sample is selected on entering publicly funded treatment, so it is useful
for **ratios and not levels**. The psychiatric figure is a share of those answering
the item. The last of the three is the sharpest check in this list: among people
entering treatment who are homeless, only 6.6 percent work at all, which is far more
severe than the disorder penalty alone and is a direct test of the homelessness to
employment channel.

**Drug use disorder share of the homeless — 21.7 percent.** Gutwinski et al. (2021),
the same meta regression that supplies the SMI share λ_m is calibrated to, so the
disorder share is the untargeted half of the same study.

**Drug price participation elasticity — −0.63.** Saffer and Chaloupka (1999). The
model's participation response to the drug price is not targeted anywhere; it comes
out of the drug market and the utility weight, so this is a check on both at once.
This is the **extensive** margin, whether a household uses at all. The intensive
margin, how much a user buys once using, is a separate elasticity and the model
produces it separately; it is not yet reported here because the source for the data
side has not been settled.
