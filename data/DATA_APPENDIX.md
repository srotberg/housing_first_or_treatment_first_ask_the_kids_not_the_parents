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

**θ, the weight on drugs in utility — 16.2 percent of income spent on the drug,
across users.** RAND/ONDCP for the numerator and NSDUH 2024 for the denominator,
because no single source carries both halves. `make_drug_spending_target.py`
computes it and writes `drug_spending_target.csv`; both models read that file.

*The numerator.* Midgette et al. (2019), "What America's Users Spend on Illegal
Drugs, 2006–2016", put 2016 retail expenditure on cannabis, cocaine, heroin and
methamphetamine at 146 billion dollars, of which 136 billion is done by the daily
and near-daily users who account for almost all of it. That is 2016 dollars, and
CPI-U (BLS CUUR0000SA0, 240.007 → 313.689) carries it to 177.8 billion in 2024.

*The denominator.* NSDUH 2024, AGE3 ≥ 7 for adults 26 and over, `svyrdudany` in
(1,2,3) for any drug use disorder: 8.90 percent of 227.3 million adults, or 20.2
million people, with mean FAMILY income of 54,216 dollars — 1,097 billion in all.
Family income, not personal, because the model's *y* is what a household pays its
rent and buys its consumption out of. 177.8/1097 = **16.2 percent**.

*Two corrections, and they pull opposite ways.* The earlier figure divided 2016
spending by 2024 PERSONAL income and got 18.4 percent. Correcting the denominator
alone gives 12.4 and correcting the price level alone gives 24.0, which is why
the uncorrected number looked plausible. Neither correction is a choice between
defensible alternatives: 2016 spending cannot be divided by 2024 income, and a
household model cannot be fed personal income.

*The one assumption.* NSDUH reports income in seven bands with the top one open
at 75,000 and over. Its midpoint is set at 100,000, the convention behind the
personal income figures quoted above; at 75,000 the share is 19.0 percent and at
125,000 it is 14.1.

*What the earlier 35 percent was.* It was built as a weighted average of 11
percent for users without a disorder and 44 with one, and attributed to NSDUH.
NSDUH does not collect expenditure, so that citation was wrong whatever the
numbers were. The construction above replaces it.

*The stylized model.* θ is not bracketed there, because the spending share is
discontinuous in θ: it climbs to about 19 percent and jumps to 29, so a bisection
aimed between the branches narrows onto the jump. θ is found by scanning instead,
at 0.2350, where the model spends 15.2 percent. Past about θ = 0.245 the
mortality channel stops reversing the income gradient on its own, and the
calibrated value sits well below that.

**b, whether a household uses — 8.90 percent participation.** NSDUH 2024, past
year illicit drug use disorder module, `svyrdudany` in (1,2,3), AGE3 ≥ 7 for
adults 26 and over. The universe matters twice over. Including 12 to 25 year olds
raises the rate, and the model begins at 26. And the figure in use until recently,
10.13 percent, was the EIGHTEEN and over rate while this appendix and the note
both said 26 and over throughout; on the model's own universe it is 8.90.

**λ, the SUD hazard per unit used — a 3.68 percent adult disorder rate.** NSDUH
2024, `svyrdudany` in (2,3) for moderate or severe, AGE3 ≥ 7 for adults 26 and
over. This and participation now come from one variable and one universe, which
two earlier pairs did not: 5.13 and 3.68 matched no single cut, and 10.13 and
4.54 were both the eighteen and over figures. This is the level, not the conversion rate from use to
disorder. The two published numbers are not mutually consistent: a conversion of
33.2 percent applied to the 8.90 percent participation rate implies a disorder
rate near 2.95 percent, not 3.68. The level is the better measured of the two, so
it is the one matched, and the conversion the model implies, 3.68/8.90 = 41.3
percent, is reported rather than imposed. The stylized model is calibrated to the same 3.68 percent
level, having previously targeted the 33.2 percent conversion, so the two models no
longer carry inconsistent numbers for the same object.

**ℵ, the flow value of being alive — a value of a statistical life of \$9m, which is
80 times mean household income.** The range surveyed in Viscusi and Aldy (2003),
converted to current dollars, against a mean household income of \$113,000. The
stylized model targets the same 80.

*Correction.* The quantitative model's target was 7.5, the dollar figure in millions,
compared against a model quantity that is a sum of V/MU_c and so carries the model's
own numeraire. On the first iteration the model produced 392 times average labour
income and the block was driving it at 7.5, which is a tenth of one multiple of
average income. The target is now the multiple, 80, and the comparison is taken on
the model's value of life over average labour income so that nothing in the block
depends on what a unit of the model is worth.

---

## 2. What using and being homeless cost

**ρ_d, earnings lost to a disorder — no moment; set to one.** The 50 percent
employment rate among the homeless (HUD 2023, employment among literally homeless
adults) is now h_2's moment, in section 6 below, because the price of the cheapest
dwelling is what prices a working household onto the street. ρ_d is switched off in
the benchmark (`include_rho_d = 0`) and κ_ued carries the disorder into poverty.

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

**ρ_m, earnings lost to mental illness — no moment; set to one.** It is switched
off in the benchmark (`include_rho_m = 0`) for two reasons. Its moment would have
been homeless conditional, like ρ_d's, so the two were identified jointly rather
than separately and neither cleanly. And it inverted the return to work: pinned at
its floor of 0.05 an employed household with SMI kept five percent of its wage while
a non-employed one draws disability insurance at ζ_DI = 0.25, so the SMI households
the model put on the street were the ones with jobs. κ_uem carries the illness into
poverty instead, on the extensive margin, and it is calibrated and live.

*A moment ρ_m does not carry, reported untargeted.* Income of the homeless at 19.1
percent of average. Meyer, Wyse, Meyer, Grunwaldt and Wu (2024), NBER Working Paper
32323, from the 2010 Census linked to restricted use tax and administrative records.
The attribution is inferred rather than quoted: Referee 1's comment 2(c)(i) gives the
19.1 percent alongside an employment rate of 40 to 52 percent among the homeless,
and that pair is verbatim the headline of that paper, 52 percent of the sheltered
and 40 percent of the unsheltered in formal employment. The paper itself could not
be opened from the machine this was written on, so the table number behind the 19.1
still needs checking. It is reported with the untargeted moments.

**κ_uem, the employment multiplier for mental illness — a 30 percent employment
rate given SMI.** Not an NSDUH number. It is the
midpoint of the employment range for high disability diagnoses in the clinical
literature: roughly a fifth of people with schizophrenia are in work, 12 percent
full time, against 48 to 73 percent for any mental illness. The source needs
naming.

*What NSDUH actually says.* In the 2024 public use file, among adults 26 and over,
58.0 percent of those with SMI are employed against 57.5 percent of those without,
and 45.8 percent against 47.2 percent are employed full time. On NSDUH's own
definition of SMI there is almost no employment gap.

*Resolved: keep the high disability target.* The state in the model is not NSDUH's
SMI. It is an illness severe enough to raise the
chance of losing work, which is the high disability end of the distribution rather
than the whole of it. (This read "severe enough to cut productivity by ρ_m and to
raise the chance of losing work"; with ρ_m off, losing the work is the whole of it.) The clinical range for that end is what 30 percent is the
midpoint of, and it is the closest measurement available for the population the state
represents. A survey number for a population the state is not would be worse. The
paper carries this as a footnote on κ_uem rather than leaving the reader to find it. The distinction
is load bearing: any mental illness covers roughly a quarter of adults, and a state
that halves productivity cannot sensibly cover a quarter of the population.

**s_m(j), the age profile of SMI prevalence — 5.6 percent overall.** NSDUH 2024.
The object matched is the profile by age; the 5.6 percent is the level it
integrates to. The onset hazard is not read off directly but backed out of the
profile and the exit rate, so the whole profile is reproduced by construction.

---

## 4. Recovery and treatment

**μ_H, the recovery multiplier when homeless — 1.473.** Milby et al. (2005), a
randomised trial on cocaine dependent homeless adults: 6.60 weeks abstinent in the
housed arm against 4.48 in the unhoused arm, so 6.60/4.48 = 1.473. This is the
causal estimate the paper leans on hardest, and the same trial supplies the
treatment effect on recovery.

**τ̄ᵘ, the utility cost of treatment — 24.5 percent treatment take up.** NSDUH 2024,
adults 26 and over with an illicit drug use disorder other than marijuana,
receiving any substance use treatment in the past year (`SUTRTPY2` over
`UD5IEMANY`, weighted by `ANALWT2_C`). It was 24 percent from the 2023 detailed
tables; the vintage now matches every other NSDUH moment. The same universe gives a
disorder rate of 3.71 percent, against the 3.68 the calibration targets, which is
the difference between the public use file and the published table.

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

**δ_h, the child's earnings penalty for homelessness — a child homelessness ratio of
2.1.** Calibrated internally, on the transmission of its own condition, exactly as δ_d
is. Bassuk, Buckner, Weinreb, Browne, Bassuk, Dawson and Perloff (1997), *American
Journal of Public Health* 87(2), 241–248, is a case-control study of 220 homeless
mothers and 216 low-income housed mothers in Worcester, Massachusetts:

| childhood factor | homeless | housed poor | odds ratio | 95% CI |
|---|---|---|---|---|
| primary female caretaker ever homeless | 14.2% | 8.3% | 1.80 | [0.98, 3.33] |
| primary male caretaker ever homeless | 10.3% | 4.4% | 2.41 | [1.12, 5.18] |
| ever in foster care | 19.6% | 8.3% | 2.67 | [1.49, 4.80] |

Odds ratios and intervals computed from the published percentages and the two sample
sizes; homelessness is rare in the population, so the odds ratio approximates the risk
ratio. The target is the midpoint of the two parental measures, 2.1. Both arms are
poor, so the comparison isolates transmission from the poverty that accompanies it and
needs no population base rate. It is US data, matching the model's calibration.

*Chetty et al. (2016) is the check, not the source.* Children moved to a lower poverty
neighbourhood before age thirteen earn 31 percent more as adults. The penalty that
matches Bassuk is δ_h = 0.327, so an earnings estimate the calibration never saw
reproduces one it did, to within two points. This ordering was reversed in an earlier
version, with Chetty as the target and the ratio as the check; that had the dependence
backwards, since δ_h exists to price transmission and Chetty measures a neighbourhood
effect that only stands in for it. The honest caveat is that Bassuk is observational
and single-city where Chetty is quasi-experimental, so the target is the weaker design
and the check the stronger.

*Why a general-population comparison would be wrong.* Flatau, Conroy, Spooner, Eardley
and Forbes (2013) report that 43.0 percent of non-Indigenous Australian
homelessness-assistance clients had parents who had experienced homelessness (69.0
percent for Indigenous clients). Converting a conditional share to a ratio needs a
population base rate, and against one the implied ratio is 5 to 6 — but that credits
the housing penalty with everything else that differs between poor children.
Cobb-Clark and Zhu (2015) show the difference is substantial: among Journeys Home
respondents, all on income support, those first homeless at 15 or below were 2.6 times
as likely to have been in foster care (42.5 against 16.1 percent), and markedly more
likely to have suffered physical or sexual abuse or had a parent serve jail time. A
case-control design differences all of that out, which is why Bassuk is used and Flatau
is not.

*Journeys Home.* The panel is documented in Scutella, Johnson, Moschion, Tseng and
Wooden (2012), the Wave 1 findings report. Its microdata would give an independent
poverty-held-fixed ratio, from
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
output, 2023 vintage, the last year the fixed asset tables cover. The target is a
round number rather than a single year's reading; the paper names the vintage. Household wealth in the model is financial wealth alone, since the rental
stock sits on the rental companies' books, so the counterpart in the accounts is
the private capital stock rather than measured household net worth. Private
nonresidential fixed assets are roughly two years of output and all private fixed
assets roughly three; three is the figure used and the run reports if β pins at a
bound trying to reach it.

**κ_V, the voucher eligibility cutoff — half of median income.** HUD's Housing Choice
Voucher programme sets eligibility at the *very low income* limit, 50 percent of area
median income, adjusted for family size. Two simplifications: the model has one
national income distribution rather than area limits, and it applies the cutoff to
income rather than to family-size-adjusted income. One thing the model does not carry
is HUD's targeting rule, that at least 75 percent of new vouchers go to households at
or below 30 percent of area median income, so the model's recipients are drawn from
the eligible population in proportion rather than skewed to the bottom of it. π_V
picks up the level of coverage, not its slope.

**The rental ladder — 24.1 and 62.7 percent, for h_3 and h_4.** ACS 2023,
table B25042, tenure by bedrooms, **universe occupied housing units**, N =
131,332,360. The six bedroom categories are collapsed to three: none or one, two,
and three or more, giving 13.2 / 24.1 / 62.7. The model's four housing states are
h_1 for the street and h_2 < h_3 < h_4 for the three rentals. Only two of the three
shares are targets, because three shares carry two free numbers: ς places h_3 and
matches the middle share, h_4 matches the top share, and the smallest category
follows by complementarity. h_2 is not identified by a size share at all — see the
entry immediately below. Table B25041 covers all housing units
including about ten percent vacant and is the wrong universe; it is kept in `raw/`
only so the difference is checkable. Since the universe is occupied units, the model
counterpart conditions on being housed and the homeless are in neither denominator.

**h_2, the smallest rental size — a 50 percent employment rate among the homeless.**
HUD's 2023 point-in-time count for the level of homelessness and TEDS-A 2022 for the
composition; `employed_share_of_homeless_data` in the declaration. The moment is not
a size share, because the price of the cheapest dwelling is what decides whether a
household with a job can be housed at all, and nothing else in the model prices a
working household onto the street. Raise h_2 and the bottom rung is dearer, so more
of homelessness is employed homelessness.

*This moment used to be ρ_d's.* Two instruments cannot chase one moment, and the
proportional earnings penalties ρ_d and ρ_m are both switched off in the benchmark
(`include_rho_d = include_rho_m = 0`), so neither is calibrated on anything. What
carries a disorder or an illness into poverty is the extensive margin, κ_ued and
κ_uem, both of which are calibrated and live.

**ς, the curvature of the rental ladder — the 24.1 percent middle share.** It is
calibrated, not set. The curvature places the middle rung a fraction (1/2)^ς of the
way from the smallest size to the largest, so it is what moves the share of the
housed living in the middle unit, and that share is its moment. At 1.8 the middle
rung sits 28.7 percent of the way up rather than the 50 percent a uniform ladder
gives, and the three sizes stand at 1 : 1.46 : 2.59.

*Why the middle share and not the smallest.* With h_4 holding the top share the two
are the same fixed point, because the three shares add to one, so the calibrated
ladder is the same either way. The attribution is not: the smallest share is h_2's,
so aiming the curvature at it would point a rung at a share the rung below owns. The
update's sign follows the moment, since a larger ς takes mass out of the smallest
category and into the middle one.

**Two renter cost shares, untargeted.** ACS 2023: 49.5 percent of renter households
spend more than thirty percent of income on housing and 26.5 percent more than half.
These are reported as checks rather than matched, because a cost share is a budget
consequence of the housing grid rather than the grid itself.

**ω_ℓ, the weight on leisure — average hours worked of 40 percent.** Guvenen et al.
(2023).

**σ_y, the dispersion of productivity — the bottom half's share of earnings, 17.2
percent.** SCF 2022. Productivity is a permanent draw in the benchmark, so only the
dispersion is operative. It is calibrated inside the model on that share, and
Section 8 below sets out why the share and not the standard deviation.

**ψ_R, the social security replacement rate — 0.40.** SSA. Retirement income is
0.40 times the productivity state, not 0.40 times current earnings, because there
is no work in retirement for the age profile ε(j) to apply to. This replaced the US
PIA bend point schedule (0.9 below 0.3 of average, then 0.27+0.32(x−0.3) to 2,
0.81+0.15(x−2) to 4.1, flat 1.13 above), which is progressive and capped where the
note describes a linear rate, so a reader working from equation (13) had the wrong
retirement income at every node and badly wrong at the ends.

**p_det and p_fp, how well conditionality is enforced — 0.90 and 0.05.**
*Counterfactual parameters, not calibration ones.* `voucher_conditional_on_clean`
is zero in the benchmark, so neither binds there and neither belongs in Table 5;
they are set with the Treatment First experiment and reported with it. Set, not
measured. These are what separate the quantitative model's conditionality from the
stylized model's, where the condition is perfectly enforced and perfectly met: here
some households fail it because they cannot get clean and some fail it because the
test is wrong, and those two groups are the empirical case for Housing First. No
programme publishes a detection rate for a drug screen in a housing programme, so
both are set at plausible values and the counterfactuals report the range.

**c_test, the cost of running one test — 0.031 percent of average earnings.**
*Counterfactual parameter, like the two rates above: nothing is screened in the
benchmark.* The
Texas fiscal note puts a test at about $35 and Oklahoma at $20 for the screen plus
$141 for confirming a positive; against average household income near $113,000 the
screen alone is 0.031 percent. It is a **lower bound on the administrative burden
and is meant as one**: the programme level figures are far larger once staffing is
counted, and Arkansas spent $32,507 to run five tests in 2017. The counterfactual
reports the range rather than resting on the assay cost.

**r, the risk free rate — 0.03 annually.** Kaplan, Moll and Violante (2018/2020),
the standard annual real return used in this class of life-cycle models. β is set
against it so that the two are mutually consistent rather than chosen
independently.

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

**ϱ, the food stamp clawback rate — 0.30.** SNAP statute rather than an estimate: a
household's monthly allotment is the maximum allotment for its size reduced by
thirty percent of its net monthly income (7 CFR 273.10). The same rule and the same
rate are used in the stylized model. It matters beyond the level of the transfer,
because it is the implicit marginal tax the programme puts on earnings for exactly
the households this paper is about; a transfer withdrawn one for one would give
every household below the floor the same resources and so the same behaviour.

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
a review of relapse among people carrying both a substance use disorder and a mood,
anxiety, schizophrenia-spectrum or personality disorder.

*The arithmetic.* Dual diagnosis cohorts relapse at
39.8 percent against 26.4 percent without a co-occurring disorder, an odds ratio of
1.85 for difficulty maintaining abstinence. Sustained remission is therefore 1 −
0.398 = 0.602 against 1 − 0.264 = 0.736, and 0.602 / 0.736 = 0.82. Converting the
odds ratio to a risk ratio at that base rate gives the same figure.

*Corroborated on a population sample, which is the better universe.* Bradizza et al.
is a review of treatment samples, and μ_m applies to the whole disordered population
rather than to people entering treatment. McCabe, West, Strobbe and Boyd (2018),
*Journal of Substance Abuse Treatment*, run the same comparison on NESARC-III: 8,503
US adults with a prior-to-past-year DSM-5 SUD, classified by past-year outcome into
abstinence, asymptomatic use, partial remission and persistent/recurrent SUD
(`related_lit/McCabe_West_Strobbe_Boyd_2018_Persistence_Remission_DSM5_SUD_NESARC_III_JSAT.pdf`).

Their Table 1 gives the composition of each outcome group by comorbidity, so the
rate BY comorbidity comes from inverting it against the weighted outcome
prevalences in their abstract (abstinence 14.2, asymptomatic 36.9, partial 10.9,
persistent 38.1 percent):

| comorbidity | remission, none | remission, comorbid | ratio |
|---|---:|---:|---:|
| mood disorder, abstinent or asymptomatic | 52.2% | 41.4% | **0.79** |
| mood disorder, not persistent/recurrent | 64.2% | 50.1% | **0.78** |
| anxiety disorder, abstinent or asymptomatic | 51.5% | 47.8% | 0.93 |
| anxiety disorder, not persistent/recurrent | 62.9% | 56.9% | 0.90 |

DSM-5 mood disorders there are bipolar, dysthymia and major depressive disorder,
which is the closer analogue of this model's SMI state — an illness severe enough
to raise the chance of losing work — than the anxiety group is. **0.82 sits inside
what the better source supports and next to its mood-disorder figure**, so the value
stands and is now sourced on a population sample as well as a treatment one.
`nesarc_mu_m.py` in `data/` reproduces the table.

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

**κ_x, the disamenity of aggregate homelessness — 0.20 percent of annual earnings,
which enters as 0.002.** Loubière et al. (2020), a contingent valuation across
Europe: €57 a year among the 42 percent of respondents willing to pay anything,
against €23 averaged over all respondents. The higher figure is taken as the
baseline, because it is the one least kind to Treatment First: a larger disamenity
loads whichever policy houses more people. The lower figure, €23, is 0.08 percent
and enters as 0.0008.

**κ_x is in the Fortran.** It is declared at `kappa_x=0.002d0` and enters flow
utility as `-kappa_x*model_fraction_homeless(1)`. Because the headcount is
aggregate and taken as given by every household, `kappa_x*H` is a constant inside
the household's problem and cannot move any policy function, so no calibrated
moment depends on it; what it changes is the welfare comparison across steady
states, which is where the paper uses it.

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
target. They are listed in the order the paper's validation section lists them. Two are
derived elsewhere in this file rather than repeated here:
the **earnings shares of the bottom and top tenths**, 0.99 and 41.1 percent from
SCF 2022, come out alongside the share σ_y is calibrated on and are derived in
section 8 with it; and the **odds that a homeless adult had a homeless caretaker**,
1.8 and 2.4 from Bassuk et al. (1997), are derived in section 5 with δ_h, which is
calibrated on the same study.

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

The band is **65 and over**, not 64 and over: "Over 64" means over the age of 64.
The model's band 5 is `age_index` 40 to 60, data ages 65 to 85, so the two line up
exactly and there is no off-by-one between the data and the model here. The
off-by-one that does exist is inside the model: `rr_homeless_hold_age=65` replaces
the mortality profile above age 65, and every old homeless household the model
produces sits at age 65 itself.

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

**Housing costs above 30 and 50 percent of income — 43.2 and 19.2 percent.**
SCF 2022, computed by `SCF_cost_burdened_renters_code.txt`. The universe is every renter
with positive income and positive rent, weighted by `wgt`, with no income band; rent to
income is annualised as 12 × rent / income. *Correction, 1 October:* the script carried
a leftover restriction to the 80th to 100th percentile of the income distribution, under
which no renter is burdened at all, so it cannot have produced the 40.6 and 17.5 percent
that stood here before; the band is removed. Keeping also the 40 renters with no income
and the 345 who pay no rent gives 40.9 and 18.3. This is a different universe from the
ACS 49.5 and 26.5 percent quoted with the rental ladder, which is why the two pairs of
numbers differ, and both are reported rather than reconciled.

**Earnings shares, bottom tenth and top tenth — 0.99 and 41.1 percent.** SCF 2022
(`SCF_2022.dta`), the same universe and the same weights as the bottom half's share
sigma_y is calibrated on in Section 4: households aged 26 to 65 with positive wage
and salary income (`wageinc > 0`), weighted by `wgt`. Rank that universe by wage and
salary income and take each decile's share of total earnings. The two tenths come out
of the same computation as the target and are not themselves targeted, which is why
they belong here: sigma_y is identified by the bottom half alone, so the tails are
free to miss.

**Price elasticity of demand, intensive margin — −0.55.** The one moment here with no
dataset behind it, and it is the midpoint of a published range rather than an
estimate: the intensive margin runs between about −0.3 and −0.8 across the literature
set out in Section 2 of the paper, with Olmstead et al. (2015) at −0.80 for heroin
among regular users at the far end. The check on the model is therefore that it lands
inside the range, not that it reproduces the midpoint. The participation elasticity
beside it is a single estimate, Saffer and Chaloupka (1999), and is treated the usual
way.

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
produces it separately.

Both margins are now validation moments. The table in the validation section carries
the participation elasticity at −0.63, from Saffer and Chaloupka (1999), and the
intensive margin at −0.55, the midpoint of the −0.3 to −0.8 range rather than either
end of it; the model produces each and neither is targeted.

The data side of both margins is now settled. Participation estimates run from about
−0.3 to −0.9: Saffer and Chaloupka (1999) and Grossman and Chaloupka (1998), whose
long run decomposition has a permanent ten percent price fall raising the number of
cocaine users by a little over eight percent. The intensive margin is smaller, about
−0.3 to −0.8: the same decomposition raises frequency among users by a little over
three percent, and Olmstead et al. (2015) put the conditional elasticity for heroin at
−0.80 on two designs sharing a sample of regular users but not an identification
strategy.

*Correction.* An earlier version gave the participation range as −0.3 to −1.1 and
cited Olmstead et al. (2015) for it. The −1.1 endpoint had no traceable source, and
Olmstead's −0.80 is a conditional elasticity, so it belonged on the other margin.
