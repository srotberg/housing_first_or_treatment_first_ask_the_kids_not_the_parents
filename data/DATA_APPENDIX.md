# Data appendix

Every number the calibration takes from outside the model, with the dataset it comes from, its vintage, its
universe, and the computation that turns it into the figure the paper reports. The paper's calibration sections
(3.2 and 5) and Appendix A point here rather than carrying this detail. Brought up to date with the paper on
10 October 2026, with a second pass the same day that closed most of the open provenance
(`DATA_APPENDIX_CHANGES_2026-10-10.md` lists what changed). Web sources are cited with their URL and were accessed on
10 October 2026.

The entries follow the paper. Part I is the quantitative model, block by block: Blocks 1 to 6 are the twenty-five
parameters of Section 5.1 and Table 3, Blocks 7 to 13 the thirty-three standard parameters of Appendix A and
Table A1. Part II is the Treatment First experiment of Section 6: the three screen parameters, what clears in each
run, the columns of Table 5 and the welfare criterion. Part III is the validation of Section 5.2 and Table 4,
including the deterrence comparison with the US military, and the other data facts the text quotes. Part IV is the
stylized model of Section 3 (Tables 1 and 2), where it differs from Part I. Part V is what is not yet documented or
not in the package; Part VI what earlier versions of this appendix carried and the paper no longer uses.

Each entry gives the parameter as the paper writes it, whether it is set outside the model (Ext.) or calibrated
inside it (Int.), the data value, the model's value of the moment where there is one, and the parameter's value,
all as in Tables 3 and A1, which `code/paper/calib_tables.py` generates from the benchmark
(`results/reference/hf_2c_omega_0.085/`) and whose cells it also exports as `c_*` in `code/paper/calib_numbers.json`
for the prose. Where the prose rounds a table cell (θ = 0.165 prints as 0.17, π_V = 0.0675 as 0.068, the SSI
floor 0.177 as 0.18) the entry says so. The Fortran name follows where it helps a reader find the number.
(`code/paper/params_numbers.json`, the older `q_*` export, is stale and no longer quoted by the paper.)

Two conventions hold throughout. **The unit is a household**, because the model's agent is one; where a target is
a share of people that is said. And **the universe is stated for every target**, because several of these numbers
move by a factor of two between people and households, adults and all ages, renters and all occupants.

**The package carries most of the data.** `raw/` holds the source exports as downloaded (HUD, CDC WONDER, the
Federal Reserve, the Census, SSA, BLS, SAMHSA, NSFG); `NSDUH_2024.dta` and `SCF_2022.dta` are microdata extracts,
and the 2024 NSDUH public use file is in `raw/` for the variables the extract lacks. A few inputs are not in the
package; Part V lists them. `README.md` lists the files and the regeneration commands.

---

# Part I. The quantitative model

Blocks 1 to 6 are Section 5.1 and Table 3; Blocks 7 to 13 are Appendix A and Table A1.

## Block 1: Who uses drugs

**θ, the weight on drugs in utility — drug spending of users over their income, 16.0 percent.** Int.; θ = 0.165
(the prose prints 0.17) and the benchmark's aggregate share is 14.8 percent. The target is declared as `drug_spending_share_data = 0.16`
in the Fortran, and the stylized model reads it from there. It is built from two sources, because no single one
carries both halves.

*The numerator.* Midgette et al. (2019), "What America's Users Spend on Illegal Drugs, 2006–2016", put 2016
retail expenditure on cannabis, cocaine, heroin and methamphetamine at 146 billion dollars (52 + 24 + 43 + 27).
136 billion of it is used here, which counts cannabis at its daily and near-daily users' share and the other three
in full. CPI-U (BLS CUUR0000SA0, 240.007 to 313.689) carries 136 billion of 2016 dollars to 177.8 billion in 2024.

*The denominator.* NSDUH 2024, adults 26 and over (`AGE3` ≥ 7), any drug use disorder (`svyrdudany` in 1, 2, 3):
8.90 percent of 227.3 million adults, or 20.2 million people, with mean FAMILY income of 54,216 dollars, 1,097
billion in all. Family income, not personal, because the model's income is what a household pays its rent and
buys its consumption out of.

*The one assumption, and the target.* NSDUH reports income in bands with the top one open at 75,000 and over. With
its midpoint at 100,000 the construction gives 177.8/1097 = 16.2 percent; at 75,000 it gives 19.0 and at 125,000
14.1. The target, 16.0, lies inside that range. (`make_drug_spending_target.py` writes `drug_spending_target.csv`
with the 125,000 midpoint, 14.1 percent; neither model reads its headline.)

**b, whether a household uses at all — 8.90 percent of adults with a drug use disorder of any severity.** Int.;
b = 0.0054 and the benchmark gives 8.96 percent. NSDUH 2024, past-year drug use disorder module, `svyrdudany` in
(1, 2, 3), adults 26 and over (`AGE3` ≥ 7), weighted: 8.90 percent. The universe matters twice over: including 12 to
25 year olds raises the rate, and the model begins at 26; the eighteen-and-over rate is 10.13. The value is written
to `drug_spending_target.csv` (`participation`, 0.08901) by `make_drug_spending_target.py`. A user in the model is
therefore a household whose use amounts to a disorder, mild included, of any illicit drug, marijuana among them
(the paper's footnote to this item). *How the Fortran reaches it.* The parameters of Block 1 were calibrated with
the child's weight at zero, against targets 18 percent above the data (`participation_rate_data = 0.10502` =
8.90 × 1.18, 10.50 percent, and `sud_rate_data = 0.043424`, 4.34 percent), because switching the weight on to
ω_c = 0.085 lowers use by about that much (`calib_tables.py`, `UPLIFT`; `c_uplift_pc`, `c_b_target_pc`,
`c_sud_target_pc`): with the weight off the benchmark's use is 10.54 percent, and switching it on lowers it by 15.0
percent (`c_b_off_pc`, `c_b_fall_pc`), the 17.7 percent rise of ω_c's moment read the other way. The benchmark with
the child's weight in place is the one reported, at 8.96 against 8.90.

**π_d, the chance that a year of use leads to a SUD — 41.3 percent of users carrying a SUD.** Int.; π_d = 0.0345 and
the benchmark gives 42.6 percent. NSDUH 2024, adults 26 and over: 3.68 percent carry a moderate or severe drug use
disorder (`svyrdudany` in 2, 3) against 8.90 percent with one of any severity, so 3.68/8.90 = 41.3 percent of
users carry a SUD. Both come from one variable on one universe; the eighteen-and-over pair, 4.54 and 10.13, is not
used. The benchmark's disorder rate is 3.81 percent.

**κ_φd, increased mortality with a SUD — users' income at 74 percent of the average.** Int.; κ_φd = 4.00 and the
benchmark gives 62 percent (a miss of twelve points the table shows as it is). NSDUH 2024, mean personal income of adults 18 and over with a past-year drug use
disorder of any severity over the mean of all adults, income bands at their midpoints with the top band at
90,000: 0.740 (`drug_user_income_data`). On the model's 26-and-over universe the same computation gives 0.761, and
on family income 0.815. The paper places the value within the range of the mortality rate ratios of a SUD it
cites: 3.91 in the Danish registers (Plana-Ripoll et al., 2019) and 6.6 among Norwegians in specialist care
(Heiberg et al., 2018). The Fortran declares `kappa_phi_d_level = 8` as a starting value only.

**ℵ, the flow value of being alive — a value of a statistical life of 80 times mean household income.** Int.;
ℵ = 87.6 and the benchmark gives 81. Nine million dollars, the range surveyed in Viscusi and Aldy (2003) in current
dollars, against a mean household income of 113,000 dollars (CPS ASEC, `MEAN_HH_INCOME_USD` in
`code/stylized/gradient.py`; the year is Part V), is 80 times it (`vsl_data = 80`). The model's counterpart is its
value of life over average labour income. The income elasticities in the item's footnote, 0.5 to 0.6 across people
(Viscusi and Aldy, 2003) and 1.5 to 1.7 over time (Costa and Kahn, 2004), are in `lit_numbers.py`
(`va_el_*`, `ck_el_*`).

## Block 2: Costs of homelessness and vouchers

**κ^ue_d, how much harder it is to regain employment with a SUD — a 21.7 percent SUD share of the homeless.** Int.;
κ^ue_d = 3.78 divides the job-finding rate of a household with a SUD (`multiple_find_if_addicted`), and the
benchmark gives 20.2 percent. Gutwinski, Schreiter, Deutscher and Fazel (2021), meta-analysis of the prevalence of
mental disorders among homeless people in high-income countries, drug use disorders: 21.7 percent
(`sud_share_of_homeless`). A household with a SUD that stays out of work longer runs down its savings and is more
likely to end up homeless. The SUD does not raise separations.

**h₁, the service flow of homelessness — a homelessness rate within 0.40 to 1.00 percent of households.** Int.;
h₁ = 0.0216 and the benchmark gives 0.62 percent. The floor is HUD's point in time count, 2023, converted to
households: 467,020 homeless individuals at one household each plus 57,563 homeless family households, against
131,332,360 occupied units (ACS 2023 one-year, B25042), 0.399 percent. A one-night count misses households homeless
at other times of the year, so the ceiling is the share homeless at some point over a year, from Burt, Aron and Lee
(2001) (`h1_band_hi = 0.010`). Their estimate is from the 1996 National Survey of Homeless Assistance Providers and
Clients (NSHAPC): at least 2.3 million adults and children, "nearly 1 percent of the U.S. population", were likely to
experience a spell of homelessness at least once during a year, and perhaps as many as 3.5 million (Urban Institute,
"Millions Still Face Homelessness in a Booming Economy", 2000, https://webarchive.urban.org/publications/900050.html,
and "A New Look at Homelessness in America", https://webarchive.urban.org/publications/900302.html; read from the
search record of those pages, as the pages themselves could not be fetched from this environment). The ceiling is
therefore a share of **people**, all ages, in 1996, while the floor is a share of households in 2023; on households
the annual rate would be lower, since a homeless family is one household and several people. The band's 1.00 is the
author's rounding of "nearly 1 percent" (the Fortran comment at `h1_band_hi` calls it "the author's approved 0.4 to
1.0 per cent"). The calibrated h₁ is 53 percent of the smallest rental, h₂ (`c_h1_of_h2_pc`),
which the item quotes.

**κ_φH, mortality when homeless — 1.60 at every age.** Ext. Meyer, Wyse and Logani (2023), NBER Working Paper
31843: the death rate of homeless adults against housed adults who are also poor, about 60 percent higher, applied
as a flat multiplier on baseline mortality (`increased_risk_of_death_homeless = 0.6`, the multiplier less one, with
`homeless_death_risk_flat_in_age = 2`). Against all housed adults their headline ratio is about 3.5 for the
non-elderly, highest at prime ages; holding one ratio fixed across ages is the model's simplification.

**κ_H, the employment penalty of homelessness — 0.20.** Ext. Desmond and Gershenson (2016), *Social Problems*
63(1), on job loss after involuntary housing loss (`increased_prob_if_homeless = 0.2`). In a shelter separations are
1 + κ_H = 1.2 times as frequent and job finding 1 − κ_H = 0.8 times as fast; applying the estimate to finding as
well as to loss is the model's assumption.

**c̲, the food stamp maximum allotment — SNAP outlays at 0.42 percent of output.** Int.; c̲ = 0.0879 and the
benchmark gives 0.43 percent. Fiscal year 2023 (October 2022 to September 2023): SNAP outlays of about 113 billion
dollars against nominal GDP of about 27.0 trillion, 113/27,000 = 0.42 percent, declared as
`food_stamps_share_data = 0.0042`. The construction is the one in the paper's first draft (`writing/`, commit
dc5b53f8, 14 August: "In fiscal year 2023, total ... SNAP benefit payments were approximately \$113 billion ...
Nominal U.S. GDP in the same year was about \$27.0 trillion", citing USDA ERS, *Trends in SNAP Participation and
Costs*, and BEA, *Gross Domestic Product, 2023*). The numerator checks: USDA ERS puts federal SNAP spending in FY 2023
at 112.8 billion dollars (https://www.ers.usda.gov/data-products/charts-of-note/109300). The denominator does not
check against calendar 2023: the Fortran comment at the moment's print (`SR_v1.f90`, "SNAP outlays near 113 billion
against a GDP near 27.7 trillion is 0.0041") uses calendar-year GDP, which gives 0.41. 27.0 trillion is closer to
GDP over the fiscal year; the BEA table it was read from is not recorded (Part V). The model's counterpart is aggregate food
assistance over output, which in this model is labour income.

**π_V, the chance of drawing a voucher — 26.6 percent of the income-eligible population holding one.** Int.;
π_V = 0.0675 a year (the prose prints 0.068) and the benchmark gives 27.5 percent (`voucher_coverage_data = 0.266`).
*Where 26.6 comes from.* HUD, *Worst Case Housing Needs: 2023 Report to Congress*
(https://www.huduser.gov/portal/publications/Worst-Case-Housing-Needs-2023.html), on the 2021 American Housing
Survey: 19.3 million very low-income renter households, income at or below half of area median income, of whom 5.14
million received federal rental assistance of any kind (vouchers, public housing and project-based assistance);
5.14/19.3 = 26.6 percent. The construction is the paper's first draft's (commit dc5b53f8, 14 August), and the
target has been 0.266 since it entered the Fortran (commit 0d5e4bcf, 16 August). The 19.3 million is confirmed by
the report's summaries (https://housingmatters.urban.org/research-summary/worst-case-housing-needs-reach-new-high);
the 5.14 million is the draft's and could not be checked against the report from this environment. So the
denominator is very low-income **renters** in 2021, and the numerator is **all** federal rental assistance, not
the voucher alone. The paper and Table 3 attribute the figure to HUD's Picture of Subsidized Households 2023; that
file (`raw/HUD_picture_subsidized_households_2023_by_program_US.xlsx`) supplies the voucher checks of Part III,
Block 3, but not 26.6: its tenant-based voucher row has 1,965,742 occupied units of 2,364,622, which would need a
denominator of 7.4 million to give 26.6. The changes file lists the attribution.

**T₀, the endowment at entry to adulthood — 26.0 percent of the homeless aged 25 to 34.** Int.; T₀ = 0.111 times
average earnings and the benchmark gives 26.4 percent. HUD point in time count 2024 (`raw/HUD_PIT_counts_by_state_2007_2024.xlsb`,
sheet 2024, Total row): 146,859 homeless people aged 25 to 34 out of 565,602 aged 25 and over. A share of people,
not of households; `make_homeless_age.py` writes the bands to `us_homeless_by_age.csv` (Part III, Block 1, for the
other four).

## Block 3: SMI chain

**ι, the SUD multiplier on SMI onset — 2.00.** Ext. (`iota_smi = 2.0`). Two Danish register studies bracket it, as
the paper now cites them: Hjorthøj, Albert and Nordentoft (2018), *JAMA Psychiatry* 75(7), a hazard ratio of 1.34
for any SUD in the conversion from schizotypal disorder to schizophrenia; and Nielsen, Toftdahl, Nordentoft and
Hjorthøj (2017), *Psychological Medicine* 47(9), 6.04 for any substance abuse in the onset of schizophrenia. 2.00
lies between. (The comment at the Fortran declaration still gives the older pair, 1.34 for any SUD and 2.74 for
opioid use disorder; the changes file lists it.)

**λ_m, the annual chance of recovering from SMI — 50 percent recovered within ten years.** Ext.; λ_m = 0.066.
Åsbø et al. (2022), *Schizophrenia Bulletin* 48(4), a ten-year follow-up of a first-episode psychosis cohort:
clinical recovery of 50.0 percent for bipolar disorder, 31.7 percent overall and 22.9 for schizophrenia spectrum
disorders. The model uses the bipolar rate (`smi_ten_year_recovery_data = 0.50`): 1 − (1 − λ_m)^10 = 0.50 gives
an annual hazard of 0.067 (the Fortran declaration, `lambda_m = 0.067`), which the benchmark carries as 0.066, the
value Table 3 and the prose print.

**ω_m, the level of the SMI onset profile — 4.82 percent of the population with SMI.** Int.; ω_m = 0.0037 and the
benchmark gives 4.83 percent. NSDUH 2024 past-year SMI prevalence by age (`SMIPY`), weighted by the model's own age
distribution over 26 to 85 (`model_smi_prevalence_target`). On NSDUH's own weights the 26-and-over rate is 5.01
percent; the model's age distribution has more older households, among whom SMI is rarer.

**κ^ue_m, how much harder it is to regain employment with SMI — a 25 percent SMI share of the homeless.** Int.;
κ^ue_m = 7.71 divides the job-finding rate of a household with SMI (`kappa_find_smi`), and the benchmark gives 24.7
percent. Gutwinski et al. (2021), the same meta-analysis as κ^ue_d (`smi_share_of_homeless_data = 0.25`): the
pooled prevalence of schizophrenia spectrum disorders, 12.4 percent (95 percent interval 9.5 to 15.7), plus that of
major depression, 12.6 percent, is 25.0 (https://journals.plos.org/plosmedicine/article?id=10.1371%2Fjournal.pmed.1003750;
the pair and the sum are recorded in the commits that introduced the target, 29b4400d and 36688011, 14 August).
Bipolar disorder is not added, and the two are summed as if no one had both, so 25 is an upper bound on the share
with either diagnosis. SMI does not raise separations or cut earnings on the job.

**μ_m, the SUD recovery multiplier for SMI — 0.82.** Ext. Bradizza, Stasiewicz and Paas (2006), a review of relapse
among people carrying both a SUD and a mood, anxiety, schizophrenia-spectrum or personality disorder: dual-diagnosis
cohorts relapse at 39.8 percent against 26.4 without a co-occurring disorder, so sustained remission is 0.602
against 0.736, and 0.602/0.736 = 0.82 (the odds ratio is 1.84).

*Corroborated on a population sample.* McCabe, West, Strobbe and Boyd (2018), *Journal of Substance Abuse Treatment*,
run the comparison on NESARC-III: 8,503 adults with a prior-to-past-year DSM-5 SUD, by past-year outcome. Inverting
their Table 1 against the outcome prevalences in their abstract (abstinence 14.2, asymptomatic use 36.9, partial
remission 10.9, persistent 38.1 percent):

| comorbidity | remission, none | remission, comorbid | ratio |
|---|---:|---:|---:|
| mood disorder, abstinent or asymptomatic | 52.2% | 41.4% | **0.79** |
| mood disorder, not persistent/recurrent | 64.2% | 50.1% | **0.78** |
| anxiety disorder, abstinent or asymptomatic | 51.5% | 47.8% | 0.93 |
| anxiety disorder, not persistent/recurrent | 62.9% | 56.9% | 0.90 |

The mood disorders (bipolar, dysthymia, major depression) are the closer analogue of the model's SMI, and 0.82
sits next to them. `nesarc_mu_m.py` reproduces the table.

**κ_φm, the mortality multiplier for SMI — 2.50.** Ext. Olfson et al. (2015), *JAMA Psychiatry*, standardised
mortality ratios for adults with schizophrenia in the United States; 2.50 is the middle of them.

## Block 4: Recovery and treatment

**π̄_r, the baseline SUD recovery rate — 22 percent recovered within ten years.** Ext.; π̄_r = 0.025 a year.
Vaillant (1995), the ten-year remission rate of an untreated cohort; 1 − (1 − 0.025)^10 = 0.224.

**μ_H, SUD recovery when homeless — a housed-to-homeless abstinence ratio of 1.473.** Int.; μ_H = 0.696 multiplies
the recovery hazard in a shelter, and the benchmark's ratio of the average recovery hazard of housed to homeless
households with a SUD is 1.45. Milby, Schumacher, Wallace, Freedman and Vuchinich (2005), *American Journal of
Public Health* 95(7), randomised 196 cocaine-dependent homeless adults, all in day treatment, to no housing,
housing not conditional on abstinence, and abstinence-contingent housing. The ratio is the unconditional housing arm
against no housing, unadjusted: 6.60 weeks of consecutive abstinence against 4.48, 6.60/4.48 = 1.473. The
abstinence-contingent arm did best, and once treatment attendance is controlled for the unconditional arm is not
ahead of no housing; the calibration takes the unadjusted contrast of housing against none.

**g, the treatment effect on recovery — 2.00.** Ext. (`treatment_effect_on_recovery`). Medication for opioid use
disorder roughly doubles remission: 18.8 percent with buprenorphine-naloxone against 10.4 without, an odds ratio of
(0.188/0.812)/(0.104/0.896) = 1.99 (Paul et al. 2024, Western Journal of Emergency Medicine 25(6), 869-874: TriNetX
records 2017-2022, propensity-matched, remission within a year of diagnosis), and randomised trials of agonist
medication against placebo at least double abstinence (Fudala et al. 2003, NEJM 349(10), 949-958: 17.8 percent of
urine samples free of opiates with buprenorphine-naloxone against 5.8 with placebo). It replaced 1.35, from an odds ratio of 1.22 for contingency management, which is
a behavioural adjunct rather than the treatment a Treatment First programme delivers.

**τ̄ᵘ, the utility cost of treatment — 24.5 percent treatment take-up.** Int.; τ̄ᵘ = 4.49 and the benchmark gives
24.9 percent. NSDUH 2024 public use file, adults 26 and over with an illicit drug use disorder other than marijuana
(`UD5IEMANY`), receiving any substance use treatment in the past year (`SUTRTPY2`, alcohol treatment included),
weighted by `ANALWT2_C` (`treatment_take_up_data`). This universe is not the model's SUD state, a moderate or severe
disorder for any drug including marijuana (`svyrdudany` in 2, 3); the two cover similar shares of adults, 3.71 and
3.68 percent, but not the same people.

## Block 5: Externalities

**ω_c, the parent's weight on its child — unmarried two-adult households use 17.5 percent more than lone parents.**
Int.; ω_c = 0.085 and the benchmark gives 17.7 percent (`child_use_gap_data = 0.1748`; target changed on 8 October,
see Part VI). *The model moment* is a counterfactual: with every other parameter unchanged, drug use with the child
given no weight against drug use at ω_c, less one (`drug_users_without_child/model_total_drug_users − 1` in the
Fortran), so it is the proportional rise in the model's own users. *The data moment holds the household fixed as
well.* NSDUH 2024 public use file (`raw/NSDUH_2024_public_use_file_tab_delimited.zip`), adults 26 and over
(`AGE3` ≥ 7), two-person households (`IRHHSIZ2` = 2), not married (`IRMARIT` ≠ 1): lone parents living with one child
under 18 (`IRKI17_2` = 2; 573 respondents) against adults living with one other adult and no child (`IRKI17_2` = 1;
3,698 respondents; partner, roommate or relative, since the public file has no cohabitation flag). The outcome is
any illicit drug use in the past year (`ILLYR`), weighted by `ANALWT2_C`. The lone parents are reweighted to the
other group's cells of age band (`AGE3`), sex (`IRSEX`), kind of unmarried (`IRMARIT`: never married, divorced or
separated, widowed) and family income band (`IRFAMIN3`); with two members in each household, equal family income
is equal income per person. The cells common to both groups hold 70 percent of the non-parents' weight. On those
cells the lone parents use at 34.2 percent and the non-parents at 40.2, so the non-parents use 17.48 percent more
(`make_altruism_moment_loneparent.py` → `code/paper/nsduh_loneparent.json`, `nsduh_lp_id_value = 0.1748`,
`nsduh_lp_id_pc = 17.5`; reproduced 10 October). Past-year use matches the model's annual period; past-month use
(`ILLMON`) gives 19.5 percent. On any drug use disorder (`UD5ILLANY`) the same cells give 59.3 percent, but only 76
lone parents have one, too few for a reliable comparison, so, as the item's footnote says, the broader measure is
used and matched only as a proportional response, not as a level. The same script prints the comparison against
married couples without children and with other cell definitions; the paper quotes none of them.

**δ_d, earnings the child loses because of a parent's SUD — 0.24.** Ext. Nilsson (2017), *Journal of Political Economy*
125(4), Table 4, Panel A, column 1 (the PDF is in related_lit/): children born to mothers under 21 in the two
experiment regions and conceived July-October 1967, so exposed from early pregnancy to the policy that let grocery
stores sell strong beer, have average log earnings at age 32 lower by exp(b)-1 = -0.244 (SE 0.090) than the
surrounding cohorts and the same cohorts elsewhere (a triple difference); men -0.241 (SE 0.113), women -0.174
(SE 0.138, insignificant); the abstract rounds it to 'around 20 percent'. Footnote 40: at age 37, or in cumulative
earnings over ages 26-37, the effect is similar for men and smaller for women; Linnros and Nilsson (2025) follow
the cohort to 47, cumulative earnings 16 percent lower. The mean effect is driven by the part of the distribution
below the 40th percentile, with about -14 percent from the 40th to the 80th; years of schooling -0.32 (men -0.52),
high school completion -6.7 points, welfare receipt +3.5 points. It is an intention-to-treat average over every
such child, drinkers' and non-drinkers' alike (`penalty_child_addicted = 0.24`). A child whose parent had the SUD at
any point while it lived at home, before J_K or the parent's death, enters with its productivity lowered by that
proportion for life. Transmission of the SUD is then untargeted (Part III, Block 6).

κ_x, the disamenity of homelessness, is no longer a parameter of the paper (Part VI). Loubière et al. (2020) survive
only in a footnote to Section 2: Europeans would pay about 0.2 percent of average earnings a year to end
homelessness (`f_kappa_x_pc`, from the Fortran's `kappa_x`), and solving the model with such a disamenity barely
changes the results.

## Block 6: Drug market

**ε_s, the price elasticity of drug supply — 1.46.** Ext. Mace, Patel and Seegert (2020), *National Tax Journal*
73(2), on Washington State administrative data for cannabis, which remains a Schedule I substance federally, so even
a licensed producer works without interstate trade, ordinary banking or federal protection; the paper uses it
because it knows of no direct estimate for an illicit drug. The inverse supply is
p_v = ν₁ S_v^{1/ε_s}, an exponent of 0.68; the code's `drug_supply_curvature` is the cost function's, 1 + 1/1.46 =
1.68. It is at the lower end of the elasticities used in the drug-supply literature (Rhodes et al., 2002).

*Appendix A: the standard parameters (Table A1).*

## Block 7: Preferences

**σ, risk aversion — 2.** Ext. Attanasio and Weber (2010).

**γ, the weight on housing services — shelter plus utilities at 26.8 percent of expenditure.** Int.; γ = 0.536 and
the benchmark gives 26.2 percent. BLS Consumer Expenditure Survey 2024, table 2500, all consumer units: (16,316.79 +
4,736.50)/78,535.21 = 26.8 percent (`cex_housing_share.py`). It is an expenditure share, not a rent-to-income ratio,
and the CEX excludes illicit drug spending. γ is calibrated to it rather than read off: with four housing points,
the street among them, and a voucher paying part of the rent, the Cobb-Douglas identity between weight and share
does not hold. Owners enter the CEX at outlay rather than imputed rent, so the true share is somewhat higher.

**β, the discount factor — wealth over output of 3.** Int.; β = 0.946 and the benchmark gives 2.95. BEA fixed asset
tables against NIPA output, 2023 vintage, the last year the fixed asset tables cover (`wealth_to_output_data`).
No ratio was computed from a table: the Fortran comment at the declaration says that BEA fixed assets over NIPA
output puts all private fixed assets at "roughly three" years of GDP and private nonresidential fixed assets at
"roughly two", and the target was set back to 3.0 on the author's instruction (2 September); the first draft
(commit dc5b53f8) sets 3 "as in" Guvenen, Kambourov, Kuruscu, Ocampo and Chen (2023). So 3 is a round figure and
there is no extract to name (Part V).

**ξ_j, the equivalence scale — √2 = 1.41 while the child is at home, 1 after.** Ext. The square-root scale (OECD,
2013), applied while the parent is 26 to 50.

## Block 8: Rental ladder

**h₂, the smallest rental size — renters paying over half of income, 19.2 percent.** Int.; h₂ = 0.0407 and the
benchmark gives 25.8 percent. SCF 2022 (`SCF_cost_burdened_renters_code.txt`), every non-owner (`hhouses` ≠ 1) with
positive income and positive rent, weighted by `wgt`, no income band and no age cut, rent to income annualised as
12 × `rent`/`income` (`renter_burden_50_data`). The same universe gives 43.2 percent above thirty percent, reported
as a check (Part III). On the model's 26 to 85 the pair would be 16.2 and 40.5. The Fortran's update rule for h₂
still brackets on the thirty percent cut, and h₂ was held in the benchmark.

**h₃/h₂ and h₄/h₂, the spacing of the ladder — 4 and 8.** Ext., set (`rung_ratio_h3`, `rung_ratio_h4`); no moment.

## Block 9: Earnings and employment

**J, J_K and J_R — 60, 25 and 41, with j = 1 at age 26.** Ext. The last age is 85; the
child is at home while its parent is 26 to 50; retirement begins at 66, the full retirement age for those born 1943
to 1954 (`life_span = 60`, `child_at_home_last_index = 25`, `retirement_span = 20`).

**ε(j), the age profile of efficiency.** Ext. The exponential of a quadratic in age used by Greenwood, Guner and
Kopecky (2025), ε(j) = exp{−(j−1)²/1800 + (j−1)/30} with j = 1 at 26. It peaks at age 56, 65 percent above age 26,
and is 4 percent below the peak at 65, the last working age.

**ρ_y and σ_ζ, the productivity process — persistence 0.90, set; the shock's standard deviation calibrated to the
bottom half's share of earnings, 17.2 percent.** ρ_y Ext., σ_ζ Int.; σ_ζ = 0.413 and the benchmark gives 16.2
percent. Log productivity follows log y' = ρ_y log y + ζ over working life and is frozen in retirement; ρ_y = 0.90 is the
persistence in Guvenen, Kambourov, Kuruscu, Ocampo and Chen (2023). In the code the instrument is `kkk_sigma_scale`
(2.0635), which scales both the shock's 0.20 and the entry component's 0.309, so the spread of log productivity at
entry is 0.84.

*The target.* SCF 2022 (`SCF_2022.dta`), households aged 26 to 65 with positive wage and salary income
(`wageinc` > 0), weighted by `wgt`: 13,070 implicate records (about 2,614 households, five implicates each), 85.2
percent of the age band by weight. The bottom half holds 17.2 percent of earnings (`bottom_half_earnings_share_data`).
For reference: the top tenth holds 41.1, the bottom tenth 1.00, p90/p10 is 10.0, the sd of log earnings 1.036 and
1.019 net of single-age effects.

*Why the share and not the sd.* The productivity grid has thirteen nodes running from 2.69 standard deviations below
the mean to 3.00 above (`c_nodes`, `c_kkk_lo`, `c_kkk_hi`), so it cannot reproduce a continuous sd, and the sd of log earnings mixes the persistent
component with a transitory one. A share of the bottom half is a property of where the mass sits rather than of the
tails. The universe is households with positive earnings, so the extensive margin, which the model produces through
unemployment, is held out, and the age profile is removed separately through ε(j).

**ρ, the persistence of productivity across generations — 0.50.** Ext. Between the intergenerational elasticities of
earnings of about 0.4 in Solon (1992) and about 0.6 in Mazumder (2005).

**π̄ᵉᵘ, the job separation rate — a 4.9 percent unemployment rate.** Int.; π̄ᵉᵘ = 0.0268 and the benchmark gives 5.6
percent. The mean of the monthly CPS unemployment rate (FRED `UNRATE`, ages 16 and over, seasonally adjusted) from
January 2014 to May 2024, the last month in `raw/FRED_UNRATE_monthly_1948_2024.xlsx`: 4.852, declared as
`unemployment_rate_data = 0.049` (the paper's "2014 to 2024"). Over
January 2014 to December 2023 it is 4.89. π̄ᵉᵘ is scaled across productivity by ϖ(y).

**ϖ(y), separations by productivity.** Ext. Each productivity node takes the unemployment odds of the education
group it falls in, from the BLS 2019 annual averages of unemployment by educational attainment for ages 25 and over,
with education ordering productivity by median earnings, and the profile is normalised to average one so that π̄ᵉᵘ
alone sets the aggregate rate. `UNEMPLOYMENT_BY_PRODUCTIVITY.md` sets out the mapping. The table is the CPS annual
averages for 2019, Table 7, "Employment status of the civilian noninstitutional population 25 years and over by
educational attainment" (https://www.bls.gov/cps/aa2019/cpsaat07.pdf). The values the Fortran carries
(`edu_share_1`, `edu_rate_1`) are, as shares of the population 25 and over and unemployment rates: less than high
school 9.6 and 5.4 percent, high school and no college 27.4 and 3.7, some college or associate degree 26.4 and 3.3,
bachelor's degree and higher 36.6 and 2.1. The 5.4 is confirmed by BLS
(https://www.bls.gov/careeroutlook/2020/data-on-display/education-pays.htm); the table itself could not be opened
from this environment, so the other seven values are as the 3 September note records them, and that note asks for
them to be checked before publication (Part V).

**π̄ᵘᵉ, the annual job-finding rate — 0.55.** Ext. Krueger, Cramer and Cho (2014), annual exit rates from
unemployment on matched CPS panels.

**p_ui, the share of separations that receive UI — 0.30.** Ext. BLS, the 2022 supplement to the CPS on
unemployment insurance (USDL-23-0586): about seven in ten unemployed people who worked in the past year had not
applied for UI since their last job.

## Block 10: Baseline survival and SMI onset

**φ̄_j, baseline survival by age.** Ext. Arias (2014), *United States Life Tables, 2010*, National Vital Statistics
Reports 63(7) (`raw/NCHS_US_life_tables_2010_nvsr63_07.pdf`), Table 1, the total population: one minus the probability of dying, q_x, at ages 26 to 84, with death
certain after 85. The quantitative model carries it as the vector `actual_survival_probability`, in place since the
repository's first commit; it reproduces Table 1's q_x at every age to within 0.05 percent (q₂₆ = 0.000943, q₈₄ =
0.075818), against 11 percent or more if the table is shifted a year either way. The SSA period life table, Table 4.C6,
is also in the package (`raw/SSA_period_life_table_table4c6.xlsx`, written to `us_life_table.csv` by
`make_life_table.py`); the quantitative model does not use it for baseline survival, but it reaches the model through
`make_mortality_multipliers.py`. The stylized model's survival comes from the Arias table too (Part IV).

**ς_m(j), the age profile of SMI onset.** Ext. NSDUH 2024, SMI prevalence by `AGE3` band (10.15, 8.98, 6.30, 4.32 and
1.27 percent at 26–29, 30–34, 35–49, 50–64 and 65+), fitted log-linearly in age. Onset is backed out of the fitted
prevalence and a recovery hazard of 0.067, clamped at zero, and normalised to one at age 26 (`make_mh_onset.py`,
`us_mh_onset_shape.csv`). The inversion ignores differential mortality and ι, so the profile is matched
approximately; the level is ω_m's.

## Block 11: Interest and taxes

**r, the risk-free rate — 0.03 a year.** Ext. Kaplan, Mitman and Violante (2020), *Journal of Political Economy*
128(9). β is calibrated given r.

**φ, tax progressivity — 0.85.** Ext. The paper says "in line with Heathcote et al. (2017)". The exponent in y^n = min{Y, τ_ℓ Y^φ}, a progressivity 1 − φ = 0.15
(`curvature_of_labor_income_taxes`). Heathcote, Storesletten and Violante (2017) estimate 1 − φ = 0.181 for the
United States on federal taxes and transfers, so 0.85 is somewhat less progressive than their estimate. *What 0.85
is attributed to.* No single study: the first draft (commit dc5b53f8) set the parameter at 0.85 "based on estimates
from" Heathcote et al. (2017); the author, 6 and 7 October (`code/CALIBRATION_STATE.md`, rounds r206 and r207):
"many papers use 0.85", with the paper saying only "in line with Heathcote et al. (2017)" and quoting no number. The
0.845 in Heathcote, Storesletten and Violante's 2014 *American Economic Review* paper, once taken for this value, is
the labour-supply factor under their equation (34), not the tax term; that paper's progressivity is 0.185.

**τ_ℓ, the scale of after-tax labour income — an average labour income tax rate of 22.4 percent.** Int.; τ_ℓ = 0.894
and the benchmark gives 20.9 percent. McDaniel (2007), "Average Tax Rates on Consumption, Investment, Labor and
Capital in the OECD 1950–2003", working paper, Arizona State University: the average tax rate on labour in the
United States, the value Guvenen et al. (2023) use. The target has been 22.4 since the first draft (commit
dc5b53f8, "commonly used in macro calibration"); which year or average of years of McDaniel's series gives it is not
recorded (Part V). Raising τ_ℓ raises after-tax income, so it lowers the tax.

**τ_k, the capital income tax — 0.15.** Ext. The statutory rate on long-term capital gains and qualified dividends
for the middle of the income distribution (IRS Topic 409).

## Block 12: Social security benefits and programmes' rules

**S(y) and S̲, social security and its floor — the statutory primary insurance amount.** Ext. SSA 2024: 90 percent
of the first 1,174 dollars of monthly average indexed earnings, 32 percent up to 7,078, 15 percent above, up to the
168,600-dollar taxable maximum. Divided by the 2024 average wage index of 63,795 dollars these are k₁ = 14,088/63,795
= 0.22, k₂ = 84,936/63,795 = 1.33 and y^max = 168,600/63,795 = 2.64 (`ss_bend_1 = 0.2208`, `ss_bend_2 = 1.3314`,
`ss_taxable_max = 2.6428`), in units of average labour income, applied to
productivity at the last working age. The floor is the 2024 SSI federal benefit rate, 943 dollars a month, or
11,316/63,795 = 0.177 of average labour income (the prose prints 0.18), at full take-up (`use_pia_formula = 1`; the flat 0.40 replacement
rate still declared as `ss_replacement_rate` is unused).

**ψ_ui and ȳ, unemployment insurance — 0.50 and one times average labour income.** Ext. The statutory replacement
rates and state benefit maxima in the Department of Labor's comparison of state UI laws (U.S. Department of Labor,
2024).

**κ_V and κ_r, the voucher rules — half of median income and thirty percent of income.** Ext. HUD's very low-income
limit for eligibility, and the tenant's contribution under the Housing Choice Voucher programme, the voucher paying
the rest of the rent up to the payment standard.

**ϱ, the food stamp clawback rate — 0.30.** Ext. SNAP statute, 7 CFR 273.10: a household's allotment is the maximum
for its size less thirty percent of its net monthly income. The model applies the 0.30 to gross income Y + ra, with
no SNAP deductions.

## Block 13: Drug market

**J_E, the last age at which use can begin — 55 in model terms, age 80.** Ext. (`max_age_to_choose_addiction = 55`;
the paper explains it in a footnote to Section 4).
Without it use would begin in the last years of life, where almost no continuation value remains to be lost: the
model imposes certain death after age 85, so a household near the end knows death is coming and a disorder costs it
almost nothing.

**ν₁, the supply shifter.** A normalisation, chosen so that supply equals demand at p_v = 1 in the benchmark and held
fixed across experiments, in which the price is free.

---

# Part II. The Treatment First experiment (Section 6, Table 5)

## The screen: three parameters set with the experiment

These three parameters do nothing in the benchmark, where `voucher_conditional_on_clean = 0`, so they are set with
the experiment (paper Section 6, "The screen") rather than calibrated, and are not in Tables 3 or A1. The values the
experiment ran at are in the arm's handover, `results/counterfactuals_2c/tf85_c35/tf/PARAM_HANDOVER.arm.txt`, which
`code/paper/export_results.py` reads. The Fortran declarations of the first two differ from what was run
(`probability_of_detection = 0.95`, `probability_of_false_positive = 0.005`); the handover overrides them, and
the paper quotes the handover.

**p_det, the detection rate — 85 percent.** A household that uses or carries the disorder is detected with
probability 0.85 (`probability_of_detection 0.85` in the handover; `x_tf_pdet_pc`). The paper sets it below the
evidence to be conservative, since a lower rate weakens the case for Treatment First: office urine screens detected
92.5 percent of opioid use against confirmation by liquid chromatography and tandem mass spectrometry in a blinded
study of 1,000 pain patients (Manchikanti et al., 2011), and laboratory screens 96 to 100 percent across five opioid
assays (Walsh et al., 2025); the paper quotes the pair as 92.5 to 100 percent. The sentence's direction words
(`x_tf_pdet_where`, `x_tf_pdet_so`) turn if the rate is ever set at or above 92.5. There are no false positives
(`probability_of_false_positive 0` in the handover): a household that neither uses nor has the disorder is never
flagged, since a positive screen is confirmed in a laboratory before it has consequences. A footnote reports that
the qualitative results hold with a detection rate of 70 percent and with a more elastic supply of the drug; the
only runs behind it are on the earlier benchmark, in `results/counterfactuals_cf_fix2/` (`tf70_cycle`,
`tf70_damp_partial`, `tf70_remote_damp_cycle`, `tf70_remote_partial` for 70 percent; `elast5_85`, a supply elasticity
of 5), and were not re-run on the current one (the author, 2 October: "dont run the sensitivity analysis"). None
of the 70 percent runs converged; the supply run did. The 70 is typed in the footnote, not generated; Part V.

**ψ_x, the release rate from exclusion — 1/3 a year.** A detected household is excluded and returns to the lottery
with probability 1/3 a year (`voucher_exclusion_release = 1/3`, a Fortran parameter; `x_psi_x`, `x_ban_years`), an
expected three years, the period for which the Housing Choice Voucher programme already bars a household evicted
from federally assisted housing for drug-related criminal activity (24 CFR 982.553).

**c_test, the cost of one screen — 0.031 percent of average earnings, 35 dollars.** The Texas Legislative Budget
Board's fiscal note for Senate Bill 11 (83rd Legislature, 2013) puts a test at 35 dollars, the upper end of the
per-test estimates, which loads the experiment against Treatment First. The model charges
`cost_per_drug_test = 0.00049461` (the Fortran declaration and the handover agree) against the benchmark's average
labour income of 1.5898 (`results/reference/hf_2c_omega_0.085/files/average_labor_incomebaseline_benchmark.dat.gz`),
0.031 percent (`x_ctest_earn_pc`). In dollars, average labour income is the value of a statistical life over its
multiple, 9 million / 80 = 112,500 dollars (Block 1), so a test costs 0.00049461/1.5898 × 112,500 = 35 dollars
(`x_ctest_usd`). The tests cost 0.036 percent of net government revenue under Treatment First (`x_ctest_budget_pc`,
not quoted).

## What responds in each run, and the columns of Table 5

Every experiment replaces Housing First with Treatment First and keeps the programme rationed and the tax system as
in the benchmark. Two objects can respond: the drug price, by clearing the drug market, and π_V, by holding net
government revenue at its benchmark level, so that what the screen saves is spent on vouchers for others. When π_V
is held, the revenue the screen frees goes unspent. No data enter here beyond Part I and the three parameters
above; the entries record where each column is read from (`code/paper/export_longrun.py`, which writes
`writing/tables/tab_longrun.tex` and the `x_lr_*` names; `export_results.py` and `export_pe_noext.py` write the
`x_*` names the prose quotes).

| column of Table 5 | externalities | drug price | π_V | run |
|---|---|---|---|---|
| 1 Housing First | off | clears | benchmark's | `results/pe_noext/arm_A` |
| 2 Treatment First, both held | off | held at column 1 | held at column 1 | `results/pe_noext/arm_B` |
| 3 Treatment First, π_V clears | off | held at column 1 | clears against column 1's net revenue | `results/noext_fixp/arm_D` |
| 4 Housing First (the benchmark) | on | clears | benchmark's | `results/counterfactuals_2c/nulltf/null` |
| 5 Treatment First, both held | on | held | held | `results/decomp_2c_both/arm_fixboth` |
| 6 Treatment First, π_V clears | on | held | clears | `results/decomp_2c/arm_fixp` |
| 7 Treatment First, both clear (the main experiment) | on | clears | clears | `results/counterfactuals_2c/tf85_c35/tf` |

"Without the externalities" means the parent puts no weight on its child, the child's productivity does not depend
on what its parent did (`weight_on_child`, `penalty_child_addicted` and `penalty_child_homeless` at zero), and
childhood is not counted in welfare; the model is recalibrated in that configuration (Arm A). Two runs are in
footnotes rather than columns. The no-externality run with both objects clearing, in which a newborn gains 0.39
percent as an adult, is `results/noext_clear/arm_C`. The run with the externalities in which only the drug price
clears and π_V is held (price −13 percent, drug use −27, homelessness +13, a newborn's CEV 0.18 percent;
`x_dc_pv_*`) is `results/decomp_2c/arm_fixpv`; it was a column until 9 to 10 October and is now a footnote to the
main experiment's welfare paragraph.

The main experiment's levels: π_V rises from 6.75 to 9.62 percent, the drug price falls by 14 percent (0.86 of the
benchmark's), drug use falls from 8.96 to 6.09 percent of households and the SUD from 3.81 to 2.54, and a newborn
gains 4.33 percent of lifetime consumption, 57 percent of it in childhood (Table 5's last column; `x_tf_*`,
`x_lr_*`).

## The welfare criterion (Section 6.1)

Every welfare number is a consumption-equivalent variation: the proportional change in non-housing, non-drug
consumption, at every date and in every state, that makes a newborn under the benchmark as well off as under the
counterfactual. Both values are taken at birth, before any of the newborn's draws are realised, including the
household it is born into, and each under its own policy's distribution of newborns (the ex-ante newborn criterion
of Conesa et al., 2009, and Guvenen et al., 2023). Welfare includes childhood in the parent's household, at weight
one rather than at the parent's ω_c, and adult life from the year the child leaves home. In the no-externality
columns of Table 5 the CEV is the newborn's value at 26 against column 1, since childhood is not counted there. The
shares better off compare each state's value under Treatment First with the same state's under Housing First, on
the Housing First distribution. The computation is the Fortran's `calculate_childhood_utility` and the CEV's
`childhood_comparison`, and `cohort_cev.py` for the transition's cohorts. The paper itself flags (an `\upd` note at
"Whose welfare") that every CEV is still computed with each child at home for the full J_K years, without the
parent's death that the newborn-welfare equation now states; the changes file lists it.

## The transition (Section 6.3)

The paper's numbers come from loop 1_r5 of the sixty-year run (`results/transition_2c/loop1_r5`, saved 9 October
21:51), which has converged against loop 0_r5: the budget residual has a median of 9.3 × 10⁻⁴ across the 59 years
(worst 2.1 × 10⁻³) and the drug market's gap a median of 0.08 percent (worst 1.60); the cohort born at the reform
gains 2.68 percent and the one born in year 59 4.34 (`code/CALIBRATION_STATE.md`, 9 October 21:51). A run with
T = 70 (`results/transition_2c_t70`, started 9 October from loop 0_r5's price and π_V paths) is in progress and
will replace every number and Figure 2; until it does, the text's "seventy years" is highlighted (`\tocheck`), and
the paper's own note (`\upd` at Section 6.3) says the welfare numbers are to be recomputed with the parent's death
in childhood after it. No data enter beyond Part I and Part II.

---

# Part III. Validation (Section 5.2, Table 4)

None of these is fitted. Each is produced by the model and is a place it can be caught, so the derivation of the
data side matters as much as for a target. They follow Table 4 ("Untargeted moments", `writing/tables/tab_untargeted.tex`,
written by `code/paper/calib_tables.py`, whose cells it exports as `u_*` in `calib_numbers.json`), block by block.

## Block 1: Homelessness

**Share of the homeless by age, 25–34, 35–44, 45–54, 55–64 and 65+ — 26.0, 27.2, 21.0, 18.4 and 7.5 percent.**
HUD point in time count 2024 (`raw/HUD_PIT_counts_by_state_2007_2024.xlsb`, sheet 2024, Total row): 146,859, 153,849,
118,740, 104,007 and 42,147 out of 565,602 homeless people aged 25 and over (`make_homeless_age.py`,
`us_homeless_by_age.csv`). The 25–34 share is T₀'s target, so only the other four are checks; the prose quotes 35–44,
27.2, and 55 and over, 25.9 = 18.4 + 7.5 (`u_hl_3544_d`, `u_hl_55p_d`); pooled, 74.2 percent are 25 to 54
(`u_hl_2554_d`, not quoted). These are shares of people. HUD's "over 64" also counts the few homeless over 85.

**Employed share of the homeless — 46 percent.** Meyer, Wyse, Meyer, Grunwaldt and Wu (2024), NBER Working Paper 32323,
from the 2010 Census linked to tax and administrative records: 52 percent of the sheltered and 40 percent of the
unsheltered homeless in formal employment; 46 is the unweighted midpoint (`employed_share_of_homeless_data`).
Weighted by the 2023 point in time count, 396,494 sheltered and 256,610 unsheltered, the pair gives 47.3.

**Income of the homeless over average — 19.1 percent.** Meyer et al. (2024), the same linkage
(`homeless_income_share_data = 0.191`). The figure goes back to the submitted paper's table of untargeted moments
("Avg. income of homeless ... 0.191 × avg. income", citing Meyer, Wyse, Meyer, Grunwaldt and Wu, 2024; first draft,
commit dc5b53f8), whose text read "average cash income among homeless individuals is approximately 19 percent of
average population income", and Referee 1 quotes it (comment 2(c)(i), `HF_or_TF_RED_reviews/reviewer1_R1.pdf`). The table
of Meyer et al. it was read from is not recorded and the paper could not be opened from this environment (Part V).
The model's counterpart includes food stamps, as the data do.

## Block 2: Who uses and who has a SUD

**Share of users by age, 34 or less, 35–44, 45–54, 55–64 and 65+ — 45, 19, 14, 12 and 10 percent; mean age 39.6.**
NSDUH 2023 detailed tables (`raw/NSDUH_2023_detailed_tables.zip`), Table 5.3A, column "Substance Use Disorder (2023)",
in thousands, ages 12 and over, pooled in `drug_use_age_distribution.xlsx` (sheet `own_calcuations`, column B): over
48,464, ages 12 to 34 hold 21,941, 35–44 9,281, 45–54 6,582, 55–64 6,048 and 65 and over 4,610. The mean age takes band
midpoints and 70 for the open band. Three things about this universe: the youngest band starts at 12, because the
model's first cohort stands in for everyone who began earlier; the object is a substance use disorder with alcohol
included; and the year is 2023, as Table 4 says. (Table 4 labels the first band 26–34, and the prose says "67 percent
of them are 26 to 34, against 45".) On the drug use
disorder column of the same table the shares are 51.1, 17.4, 12.5, 10.8 and 8.2 and the mean age 37.5; restricted to
26 and over they are 31.0, 24.6, 17.7, 15.2 and 11.6, mean 44.6.

**Unemployment given a SUD — 16.2 percent.** NSDUH 2024 public use file (`raw/NSDUH_2024_public_use_file_tab_delimited.zip`;
`NSDUH_2024.dta` lacks `IRWRKSTAT`), adults 26 and over, moderate or severe drug use disorder (`SVYRDUDANY` in 2, 3),
unemployed (`IRWRKSTAT` = 3) over the labour force (`IRWRKSTAT` in 1–3), weighted by `ANALWT2_C`: 16.25. Any disorder
gives 12.72, none 6.04, everyone 6.65.

**Drug use with SMI over without — 2.44.** NSDUH 2024 public use file, adults 26 and over, any illicit drug use in the
past year (`ILLYR` = 1), by past-year SMI (`SMIPY`), weighted by `ANALWT2_C`: 56.40 percent with SMI against 23.09
without (`code/paper/smi_use_ratio.json`; `SMI_SUD_TARGET.md` sets out the eight cuts considered). The universe is
past-year use of any illicit drug, marijuana included; on the model's cut, any drug use disorder, the ratio is 4.51.

**Drug poisonings as a share of deaths, 25 to 44 — 20.8 percent.** CDC WONDER provisional mortality, deaths in 2024
(`raw/CDCWONDER_provisional_mortality_drug_alcohol_induced_by_5yr_age.txt`), grouped by MCD – Drug/Alcohol Induced
Cause, summing the four drug poisoning rows: X40–X44 unintentional, X60–X64 suicide, X85 homicide and Y10–Y14
undetermined, 36,330 deaths at 25 to 44 (`make_overdose.py`, `us_overdose_mortality.csv`). The export carries no
all-cause count, so each band's poisoning death probability is divided by the SSA all-cause probability averaged over
the same ages (26 to 29 for the first band, where the life table starts): 19.7 percent at 25–29, 23.3 at 30–34, 22.2
at 35–39 and 18.5 at 40–44, and 20.8 pooled with the bands weighted by population. The model's
counterpart counts every death its SUD adds at 26 to 44, not only poisonings. (Table 4 and the prose print 20.0,
`u_deaths_d`, the value typed into the Fortran as `observed=0.20`, and name no year; the 2024 computation here gives
20.8. The changes file lists the discrepancy.) The ICD-10 113 Cause List export kept
in `raw/` as SUPERSEDED has only accidental poisoning, X40–X49, which runs 1 to 3 percent below the four drug rows at
these ages.

## Block 3: Housing and vouchers

**Renters paying over 30 percent of income — 43.2 percent.** SCF 2022, the universe of h₂'s target (Block 8): every
non-owner with positive income and rent, weighted, no income band, 12 × rent/income (`renter_burden_30_data = 0.432`,
`SCF_cost_burdened_renters_code.txt`). The model's counterpart is housed households, 58.7 percent. Keeping the 40 renters with no
income and the 345 who pay no rent gives 40.9. The SCF universe is renters, while every household in the model rents.

**Rent over income, voucher holders — 31.2 percent.** HUD Picture of Subsidized Households 2023, tenant-based voucher
row: 503 dollars monthly tenant rent against 19,368 dollars annual income, 503 × 12/19,368 = 31.2. The all-programmes
figure is 29.3 and the project-based 27.9; the model's κ_r is 0.30 and this is the check on it.

**Voucher holders living on wages — 28 percent.** Same source and row: wages are the main source of income for 28
percent of tenant-based voucher households.

## Block 4: Distribution

**Income, bottom 1, 5, 10 and 20 percent — 0.01, 0.31, 0.92 and 2.71 percent.** SCF 2022, all households, no age
restriction, total household income `income` weighted by `wgt`, sorted and cumulated with the household that straddles
each cut split, as the Fortran walks its own histogram: 0.00012, 0.00311, 0.00915 and 0.02705.

**Net worth, bottom 1, 5, 10, 20 and 50 percent — −0.16, −0.28, −0.29, −0.23 and 2.2 percent.** SCF 2022, all
households, `networth` weighted by `wgt`, with the same straddle split: −0.00158, −0.00279, −0.00287, −0.00226 and
0.02202 (`SCF_wealth_shares.txt`, which `calib_tables.py` reads for the bottom half; the prose quotes the bottom fifth,
−0.23, and the bottom half, 2.2). For comparison, the Federal
Reserve's Distributional Financial Accounts (`raw/FRB_DFA_net_worth_levels_by_percentile_1989_2026.csv`) put the
bottom half at 2.52 percent averaged over 2022:Q1 to 2026:Q1 and 2.45 in 2026:Q1 (`make_wealth_shares.py --from-year
2022`, `us_wealth_shares.csv`); the Fortran's `bottom_half_wealth_share_data = 0.025` is that figure, and the paper no
longer uses it.

## Block 5: Drug price elasticities

**Participation about −0.3 to −0.9, intensive margin about −0.3 to −0.8.** No dataset behind either: both are ranges
from the literature in Section 2 of the paper, and the check is where the model lands against them. Participation,
whether a household uses at all: Saffer and Chaloupka (1999) and Grossman and Chaloupka (1998), whose long-run
decomposition has a permanent ten percent price fall raising the number of cocaine users by a little over eight
percent. Intensive margin, how much a user buys: the same decomposition raises frequency among users by a little over
three percent, and Olmstead et al. (2015) put the conditional elasticity for heroin at −0.80 on two designs sharing a
sample of regular users but not an identification strategy. The model's figures, −1.32 for participation and −0.63
per user, average twenty price moves, up by 10, 20, ..., 100 percent and down by 10, 20, ..., 90 and 95 percent, with
the distribution of households held fixed (`results/elast_grid/w0.txt` and `w1.txt`, two workers that each re-solved
the benchmark; every step also measured in an earlier run reproduces to under 0.001). Neither is targeted.

## Block 6: Transmission

**A child of a parent with a SUD acquires one — odds ratios of 1.44 and 2.51.** Mellentin et al. (2016), 398,881
offspring in the Danish registers, and Yoon et al. (2013), a United States population-based sample; one affected
parent against none. Both measure a parent's alcohol use disorder, and Yoon's outcome is the child's alcohol use
disorder, so the range is for the transmission of substance use disorders broadly rather than of the drug use
disorder the model carries. The model's 1.46 follows from δ_d and is not targeted.

**A homeless adult had a homeless parent — odds ratios of 1.8 to 2.4.** Bassuk, Buckner, Weinreb, Browne, Bassuk,
Dawson and Perloff (1997), *American Journal of Public Health* 87(2), 241–248, a case-control study of 220 homeless
mothers and 216 low-income housed mothers in Worcester, Massachusetts:

| childhood factor | homeless | housed poor | odds ratio | 95% CI |
|---|---|---|---|---|
| primary female caretaker ever homeless | 14.2% | 8.3% | 1.80 | [0.98, 3.33] |
| primary male caretaker ever homeless | 10.3% | 4.4% | 2.41 | [1.12, 5.18] |
| ever in foster care | 19.6% | 8.3% | 2.67 | [1.49, 4.80] |

Odds ratios and intervals computed from the published percentages and the two sample sizes. Both arms are poor, so
the comparison separates transmission from the poverty that accompanies it. There is no earnings penalty for a
parent's homelessness in the model, so its odds ratio, 6.23 against the general population of homeless adults, comes
from the persistence of productivity across generations alone.

*Why a general-population comparison would be wrong* (appendix only; the paper cites neither study below). Flatau, Conroy, Spooner, Eardley and Forbes (2013) report that
43.0 percent of non-Indigenous Australian homelessness-assistance clients had parents who had experienced
homelessness. Converting a conditional share to a ratio needs a population base rate, and against one the implied
ratio is 5 to 6, but that credits the housing penalty with everything else that differs between poor children.
Cobb-Clark and Zhu (2015) show the difference is substantial: among Journeys Home respondents, all on income support,
those first homeless at 15 or below were 2.6 times as likely to have been in foster care (42.5 against 16.1 percent).

**Children living with a parent who has a SUD — 4.6 percent.** NSDUH 2024 public use file, respondents aged 26 and
over (`AGE3` 7 to 11), each weighted by `ANALWT2_C` times `NRCH17_2`, their own children under 18 in the household
(three or more counted as three), so the unit is a child. The share of those children whose parent has a moderate or
severe drug use disorder (`SVYRDUDANY` in 2, 3, the model's SUD) is 3.2 percent for the surveyed parent; counting
either parent, with the other parent of a married respondent assigned the child-weighted rate of married parents of
the other sex, independently, it is 4.6 percent, the figure Table 4 and the prose quote (`nsduh_kids_sud_hh_pc`). The
independence makes it an upper bound if partners' disorders go together. On any severity the pair is 8.0 and 12.1.
`make_children_with_sud_parent.py` → `code/paper/nsduh_kids_sud.json` (reproduced 10 October). The model's 5.81
percent (Table 4 prints 5.8) is the share of children, households aged 26 to 50, living with a parent who has a SUD.

## Block 7: Losing a voucher

**Three-year mortality of households with SMI put on the street — 4.6 percentage points.** Costantini (2025),
"Housing First or Treatment First? Evidence from the VA's homelessness programs" (`related_lit/Costantini_2025_*.pdf`,
abstract, page 1): among nearly 300,000 unhoused veterans with mental illness, enrolling in the Department of
Veterans Affairs' Housing First programme lowers three-year mortality by 4.6 percentage points against a
no-programme counterfactual, an instrumental-variables estimate (`COSTANTINI_PP` in `code/paper/export_revoked.py`;
`x_rv_costantini_pp`). The model's counterpart, 3.6 points (`x_rv_street_smi_pp`), is the three-year mortality gap
between the households with SMI at revocation whose first housing choice after Treatment First revokes their voucher
is the street, 10.20 percent, and the same households followed with their voucher kept, 6.63
(`x_rv_street_smi_dead_tf`, `x_rv_street_smi_dead_hf`), the direct gap with no Wald rescaling, the drug price and
π_V held, pooled over the holders revoked in years 1 to 3 (the row "SMI, on the street" of
`results/revoked_2c_street`'s tables, read by `code/paper/export_revoked.py`, which refuses unless the run's guard
summary passed).

## Block 8: Deterrence

**Mehay and Pacula's own estimates of the policy's effect — 4 to 16 percentage points, 11 to 45 percent** (`mp_lo_pp`,
`mp_hi_pp`, `mp_lo_rel_pc`, `mp_hi_rel_pc`). Their regression estimates of the testing policy's effect on the probability of
past-year use, which allow for who left the military, run from 4 to 16 percentage points; against the 35.7 percent of
service members using in 1980 (`mp_mil_py80_pc`) that is a fall of 4/35.7 = 11 to 16/35.7 = 45 percent. The model's
response among all tested users (`x_ws_tested_all_pc`) is compared with this range in Block 8; the 61 percent below is
the raw comparison among those who stayed.

**The Family Options Study** (`fo_families` 2,282, `fo_children` 5,397, `fo_sites` 12, `fo_cost_pc` 9). Gubits et al.
(2016), *Family Options Study: 3-Year Impacts of Housing and Services Interventions for Homeless Families*, HUD, and
Gubits et al. (2018), *Journal of Policy Analysis and Management* 37(4), 835-866: 2,282 families with 5,397 children
enrolled from emergency shelters in 12 communities, September 2010 to January 2012, randomised to priority access to a
long-term subsidy, rapid re-housing, transitional housing or usual care; at 37 months the subsidy group had fewer than
half as many later episodes of homelessness, fewer child separations, school absences and child behaviour problems,
less food insecurity, adult psychological distress and partner violence, at about 9 percent more cost than usual care
over the three years. Read from HUD's summary and the JPAM abstract (11 October); the report's PDF is not yet in
related_lit.

**Users without a SUD who stop when tested — 61 percent.** Mehay and Pacula (1999), "The effectiveness of workplace
drug prevention policies: does 'zero tolerance' work?", NBER Working Paper 7383 (the author's copy). The US military
began random testing in 1981 and dismissed those who failed; Navy and Marine Corps commanders had to test 10 to 20
percent of their commands every month (p. 6). On the NLSY, past-year marijuana use among those who stayed in the
military fell from 48.5 to 13.2 percent between 1980 and 1984, and among those who stayed civilians from 45.8 to 32.0
(Table 6, p. 30). The testing therefore cut use among those subject to it by 1 − (13.2/48.5)/(32.0/45.8) = 61 percent
of what it would otherwise have been (`data/lit_numbers.py` → `code/paper/lit_numbers.json`, `mp_stay_rel_pc`; the
inputs are `mp_stay_*`, `mp_test_lo`, `mp_test_hi`). Section 2 quotes the same numbers. The measure is any
past-year use of marijuana, broader than the model's, so the two are compared as proportional responses.
The model's counterpart, 59 percent (`x_ws_tested_nosud_pc`), applies Treatment First to the benchmark's households
with the distribution, the drug price and π_V held at Housing First's, and follows each user subject to the screen
(every voucher holder, and every eligible household offered a voucher, weighted by its offer rate): of those that
used under Housing First and have no SUD, 59 percent stop and none starts. Those with a SUD are 67 percent of the
users subject to the screen (`x_ws_tested_sud_share_pc`) and cannot stop on impact; counting them, 19 percent stop
(`x_ws_tested_all_pc`), about a third of the military's response. `code/paper/export_whostops.py` reads the
`DIAG who stops` line of `results/whostops_2c/cfarm_tf_imp_ws850/cf.log.gz` (`code/deter_2c/run_whostops.sh`). The
long-run fall in the footnote, 64 percent, is Table 5's fifth column (8.96 to 3.20 percent).

## Other data the text quotes

Not in Table 4, but stated as data in Sections 1, 2 and 7:

- **771,480 people homeless in the January 2024 point in time count** (Section 1): HUD PiT 2024
  (`raw/HUD_PIT_counts_by_state_2007_2024.xlsb`, sheet 2024, Total row, column "Overall Homeless"; checked 10 October).
  The number is typed in the source, not generated.
- **Users are nearly as likely to be parents** (Section 7): in the National Survey of Family Growth 2017–2019, 75
  percent of adults aged 40 to 49 who used hard drugs in the past year had a child, against 81 percent of those who
  used none (`nsfg_all_anybirth_hard_4049_pc`, `nsfg_all_anybirth_nouse_4049_pc`). Female and male respondent files
  (`raw/NSFG_2017_2019_*`), ages 15 to 49, weighted by `WGT2017_2019`, children ever born (`PARITY`) or fathered
  (`BIOKIDS`); hard drugs are cocaine, crack, crystal meth or injecting in the last twelve months
  (`nsfg_births_by_drug_use.py` → `code/paper/nsfg_births.json`).
- **A child at home** (Section 7): among adults aged 26 to 49, 40 percent of those with a drug use disorder of any
  severity have a child under 18 at home, against 48 percent of comparable adults who used no illicit drug, the
  non-users reweighted to the users' cells of age, sex, personal income and marital status (NSDUH 2024;
  `make_children_at_home_reweighted.py` → `code/paper/nsduh_kids_home.json`, `nsduh_kh_sud_pc`,
  `nsduh_kh_sud_like_pc`).
- **The users' income, 0.74 of the average** (Sections 1 and 3) is κ_φd's target (Block 1), and **17.5 percent** (Sections
  1, 2 and 7) is ω_c's (Block 5).

---

# Part IV. The stylized model (Section 3, Tables 1 and 2)

The stylized model is `code/stylized/gradient.py` (8 October; `gradient.json` holds the calibration,
`gradient_numbers.json` the `g_*` names the prose quotes, and the script writes Tables 1 and 2,
`writing/tables/tab_external.tex` and `tab_internal.tex`, and Figure 1): two periods of thirty years, productivity
fixed for life, drugs bought only in the first period, saving at zero interest, a SUD that raises the risks of dying
and of being out of work in the second period, and food assistance. There is no housing, no government budget, no
child and no unemployment insurance. Its targets are the quantitative model's wherever the two share a moment, read
from the same Fortran declarations or data files, so the two models aim at one number. What differs is this.

- **Periods and survival.** β = 0.86 per period is 0.995 a year compounded over thirty years (`g_beta`,
  `g_beta_ann`; the annual factor is set high on purpose, as the paper's footnote explains). σ = 2. φ̄ = 0.93
  (0.9293 in `gradient.json`) is survival from 26 through 55 in the quantitative model's own life table, Arias (2014)
  (Block 10): the product of the first thirty entries of `actual_survival_probability`, read from the Fortran.
- **Productivity** is lognormal, log y ~ N(−σ_y²/2, σ_y²), with σ_y = 0.95 (0.946) set outside the model so that
  the poorer half of the lognormal holds 17.2 percent of income, Φ(−σ_y) = 0.172 (`BOT50_TARGET`, the SCF 2022 share
  of Block 9). The code also **truncates the distribution below at y_min = 0.24 of mean income**, the survivors
  renormalised to mean one (`Y_FLOOR`; `g_yfloor`). The paper does not state the bound (the author, 8 October: "You
  don't need to explain the income floor to the reader"), so it is documented here: with σ = 2 the value of being
  alive is negative at a low enough consumption, and a household for which it is negative would use drugs for the
  mortality they bring; the bound keeps every household's period-1 value positive (`gradient.py` asserts it), and
  being alive is worth nothing at a consumption of about 0.17 at the calibrated parameters (`gradient.y_zero`). It
  cuts 20.1 percent of the lognormal, so the model's poorer half holds 21.5 percent rather than 17.2
  (`g_bot50_model`; computed 10 October from `gradient.moments`). At the calibration the users are one band of
  incomes from 0.68 to 0.81 of the mean.
- **π_d = 0.41, set externally** as the SUD rate over participation, 0.0368/0.08901 = 0.413
  (`data/drug_spending_target.csv`, rows `sud_rate` and `participation`; NSDUH 2024, 26 and over), since use and the
  SUD are separated by cohort.
- **u₀ = 4.9 percent and u₁ = 16.25 percent** are the quantitative model's targets (`unemployment_rate_data`,
  `unemployment_rate_sud_data`; Table 1 prints u₁ as 0.16), set here rather than fitted. A household out of work in
  the second period earns nothing and consumes its savings plus c̄.
- **Food assistance** F(ye) = max(0, c̄ − ϱye) on each period's earnings, with ϱ = 0.30, SNAP's benefit reduction
  rate; c̄ = 0.098 (Table 2 prints 0.10) is fitted to the same 0.42 percent of labour income as the quantitative
  model's c̲ (`food_stamps_share_data`). There is no unemployment insurance.
- **p_v = 1** is a normalisation.
- **The five internal parameters** are fitted jointly and every moment is matched exactly (`gradient.py` asserts a
  relative error below 10⁻⁶): **ℵ = 8.64** to a VSL of 80 times average income (9 million dollars against a CPS ASEC
  mean household income of 113,000, `g_vsl_musd`, `g_mean_hh_usd`; Part V for the year); **b = 0.032** to
  participation of 8.90 percent (0.08901, `drug_spending_target.csv`), solved inside the fit; **θ = 0.22** to drug
  spending of 16.0 percent of users' income (`drug_spending_share_data`, Block 1); **κ_φd = 3.56** to users' income of
  0.74 of the mean (`drug_user_income_data`, Block 1); **c̄ = 0.098** as above.
- **The log-utility footnote** ("All the qualitative results of this section hold with log utility as well, with the
  model recalibrated to the same targets"). The recalibration is `code/stylized/referee_item7/log_utility/`
  (`calibrate_log.py`, `tests_log.py`, `single_band_search.py`, `kappa_fine_scan.py`, `knife_edge.py`), with
  `gradient.py` unmodified and σ = 1, outputs in `results/referee_item7/log_utility/` and the write-up in
  `results/referee_item7/LOG_UTILITY.md`. All five targets are hit (maximum relative error 8.5 × 10⁻¹³ in
  `log_calibration.json`) at ℵ = 3.69, b = 0.0030, θ = 0.165, κ_φd = 11.95 and c̄ = 0.0995. **That write-up does not
  support the footnote as worded**: at log the users are two bands, the bottom 8.44 percent and the top 0.46 percent,
  rather than one middle band; κ_φd = 11.95 lies above the 3.91 to 6.6 the paper cites; in Figure 1's scan the
  mortality channel alone leaves the average user at 3.51 times the mean up to its calibrated strength and reverses
  the gradient only at 110 to 120 percent of it; and the unemployment channel alone never moves users off the top,
  with saving or without (`figure1_scans_main_session.txt`), so the no-saving demonstration of the right panel does
  not survive log. The changes file lists it.
- **The footnote on a version with housing** (Section 3.1: 3.54, 0.52 at twice the calibrated mortality strength,
  and 0.56 without saving) reads the older staged model: `code/stylized/stage_numbers.json` (`s1_r_none`,
  `s1_r_mort_hi`, `s1_r_unemp_hi`, from `stage_results.py`) and `oldmodel_nosave_numbers.json` (`g_old_ns_u200`, from
  `oldmodel_nosave.py`). No data enter beyond what is above.

---

# Part V. Open provenance

What the package does not yet document, or does not carry. Each item says what was checked on 10 October (the
repository, its git history from the first commit, and the web; from this environment the web could be searched but
not fetched, so a source that only exists as a PDF table could not be read).

1. **The year of the 113,000-dollar mean household income** behind the VSL multiple (Block 1, Part IV). It is a
   constant, `MEAN_HH_INCOME_USD` in `code/stylized/gradient.py`, labelled CPS ASEC; it first appears in the paper's
   text on 15 August (commit acef0219) and in code on 30 September (2c89f233), never with a year or table. The
   Census reports that would carry it (P60-282, *Income in the United States: 2023*, and table HINC-01) were found
   but their mean could not be read. The test's dollar cost uses 9 million / 80 = 112,500 instead (Part II).
2. **The BEA table behind GDP of 27.0 trillion** in the SNAP target (Block 2). The fiscal year (2023), the outlays
   (113 billion; ERS 112.8) and the arithmetic are closed; the GDP figure is the first draft's, cited to BEA without a
   table, and it is below calendar-2023 GDP.
3. **Meyer et al. (2024)**: the table behind the 19.1 percent income of the homeless (Part III, Block 1). Traced back
   to the submitted paper's table and Referee 1's quotation, but not to a table of the working paper.
4. **McDaniel (2007)**: the year, or average of years, of the series that gives 22.4 percent (Block 11).
5. **The BLS 2019 education table** (Block 9): the table is named (CPS annual averages 2019, Table 7) and its
   less-than-high-school rate, 5.4, confirmed; the other three rates and the four population shares are as the
   3 September note records them, unchecked against the table, and the table is not in the package.
6. **Wealth over output of 3** (Block 7): no BEA or NIPA extract was ever computed; the target is a round figure
   (see the entry). Nothing to add to the package unless the author wants the ratio computed.
7. **The 5.14 million assisted renters** behind π_V's 26.6 percent (Block 2): from the first draft; the report's
   19.3 million is confirmed, the 5.14 million could not be read from the report.
8. **The detection-rate robustness at 70 percent and the more elastic supply** (Part II): typed in a footnote, and
   only earlier-benchmark runs exist, in `results/counterfactuals_cf_fix2/`, and none has been run on the current
   benchmark (the author, 2 October: "dont run the sensitivity analysis"). Their notes record that **no 70 percent
   run converged**: `tf70_cycle` stopped in a two-pass cycle, `tf70_damp_partial` was lost at pass 7 to a container
   restart, `tf70_remote_damp_cycle` stopped at pass 12 when the cycle returned, and `tf70_remote_partial` reached
   pass 8 with the same behaviour (`NOTE.md` in each). Every pass of the four has drug use 28 to 29 percent below
   Housing First and a newborn's CEV between +1.43 and +1.76 percent (`passes.txt`), so the sign the footnote
   claims holds on every pass, but there is no equilibrium. `elast5_85`, a supply elasticity of 5, converged
   (`RESULT.md`), with a CEV of +2.77 percent at its last pass.
9. **Mehay and Pacula (1999)** is cited from the author's copy and is not in `related_lit/`; Costantini (2025) is.

Resolved: g's study (Paul et al., 2024, and Fudala et al., 2003, 6 October). On 10 October, second pass: the ceiling
of h₁'s band (Burt, Aron and Lee, 2001: NSHAPC 1996, people, nearly 1 percent; Block 2); π_V's denominator (HUD's
*Worst Case Housing Needs 2023*, 19.3 million very low-income renters in 2021; Block 2); the SNAP year (fiscal 2023,
113 billion over 27.0 trillion; Block 2); the 25 percent SMI share (12.4 schizophrenia spectrum plus 12.6 major
depression in Gutwinski et al., 2021; Block 3); what φ = 0.85 is attributed to (Block 11); the BLS table's name
(Block 9).

---

# Part VI. Retired

Earlier versions of this appendix documented parameters, targets and checks that the model or the paper no longer
has. They are listed so that a reader of an older draft can find what happened to them.

- **ρ_d and ρ_m**, earnings lost to a SUD and to SMI: the SUD and SMI do not cut earnings on the job (both set to one).
- **ζ_DI**, a disability replacement rate: the model has no disability insurance.
- **δ_h**, an earnings penalty for a parent's homelessness: removed; Bassuk et al. (1997) is now a check (Part III).
- **δ_d calibrated to a child disorder ratio of 3** (McGovern et al.): δ_d is now set from Nilsson (2017).
- **λ_m calibrated to the SMI share of the homeless**: λ_m is now set from Åsbø et al. (2022), and the share is
  κ^ue_m's target.
- **κ^ue_d calibrated to unemployment given a SUD, 16.25 percent**: now a check; κ^ue_d targets the SUD share of the
  homeless.
- **κ_uem and a 30 percent employment rate with SMI**: SMI raises no separations; κ^ue_m targets the SMI share of the
  homeless.
- **κ_φd = 8, external**: now calibrated, 4.00.
- **κ_φH falling from 4.41 to 1.09 with age** (Baggett et al., 2013): now a flat 1.60 from Meyer et al. (2023).
- **g = 1.35** from contingency management: now 2.00.
- **κ_x entering as 0.002**: later solved inside the model, 0.93, and now dropped (above).
- **A leisure weight ω_ℓ and curvature σ_ℓ**: labour is supplied inelastically.
- **A flat social security replacement rate ψ_R = 0.40**: the statutory primary insurance amount replaced it.
- **The ACS bedroom shares and a ladder curvature ς**: the rungs are set at 4 and 8 times the smallest.
- **h₂ targeted on a 50 percent employment rate among the homeless**: h₂ targets the over-half burden.
- **False positives, p_fp = 0.05, and p_det = 0.90**: the experiment has none and detects 85 percent.
- **A permanent productivity draw σ_y in the quantitative model**: replaced by the persistent process ρ_z, σ_ζ.
- **ω_c targeted on parents against non-parents**, past-month use (`ILLMON`), 1/0.845 − 1 = 18.3 percent
  (`make_altruism_moment.py`): replaced on 8 October by unmarried two-adult households against lone parents, which
  holds the household fixed as the model's counterfactual does, first on past-month use (19.5 percent) and later the
  same day on past-year use, 17.5 percent, which matches the model's annual period (Block 5).
- **κ_x, the disamenity of homelessness, solved inside the model at 0.93** to a willingness to pay of 0.20 percent of
  income (Loubière et al., 2020): no longer a parameter of the paper; it survives only as a footnote in Section 2
  saying a disamenity of that size barely changes the results (Block 5).
- **ι's sources as Nielsen et al. (2017), 1.34 for any SUD and 2.74 for opioid use disorder**: the paper now brackets
  2.00 between Hjorthøj et al. (2018), 1.34, and Nielsen et al. (2017), 6.04 (Block 3).
- **κ_φd's wider literature range**, Walker et al. (2017) and Degenhardt et al. (2011): the paper now cites only
  Plana-Ripoll et al. (2019) and Heiberg et al. (2018) (Block 1).
- **The price-clears-only run as a column of Table 5**: a footnote since 9 to 10 October (Part II).
- **The stylized model's income floor y_min as income out of work**: out of work the household now lives on its
  savings plus food assistance; y_min only truncates the productivity distribution (Part IV).
- **Checks no longer reported**: returns to homelessness within 24 months, standardised mortality ratios of the homeless
  (Baggett et al.), earnings shares of the bottom and top tenth, the income and labour force participation of adults
  with a SUD, and the three treatment-admission figures from TEDS-A.
