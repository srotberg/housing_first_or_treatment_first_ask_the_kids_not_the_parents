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

Files live in this folder. `raw/` holds the source exports exactly as downloaded;
the scripts here turn them into the small CSVs the Fortran reads. `README.md` lists
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
rather than imposed.

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
earned 31 percent more as adults.

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
which enters as 0.0008.** Loubière et al. (2020), a contingent valuation across
Europe: €57 a year among the 42 percent of respondents willing to pay anything,
against €23 averaged over all respondents. The higher figure is taken as the
baseline, because it is the one least kind to Treatment First: a larger disamenity
loads whichever policy houses more people.

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

## What is not here yet

The Model column of the paper's two calibration tables reports what the model
produces against each of these targets. Those numbers are filled from a converged
run, and the run is not converged at the time of writing, so this file documents the
data side only. When the calibration lands, the model side is added here alongside
each target rather than left only in the paper.
