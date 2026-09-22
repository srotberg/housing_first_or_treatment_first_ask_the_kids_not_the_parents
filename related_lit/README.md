# Related literature

Papers cited in the note or used to set a parameter. Filenames are
`Author_Year_ShortTitle`.

## Quantitative models this paper sits beside

| file | what it is | why it is here |
|---|---|---|
| `Imrohoroglu_Zhao_2022_Homelessness_SSRN_4308222.pdf` | İmrohoroğlu & Zhao, *Homelessness* | The closest quantitative antecedent: a dynamic GE model of homelessness policy. Source of the disability-coverage parameter ζ_DI that `di_coverage` corresponds to. The AE asks how this paper differs. |
| `Corbae_Glover_Nattinger_2024_Equilibrium_Evictions_NBER_w32898.pdf` | Corbae, Glover & Nattinger, *Equilibrium Evictions* | Their externality is about neighbourhood housing **quality**, not homelessness, and is identified off rent decontrol. What transfers is the identification logic, not the functional form — see the disamenity discussion in the note. |
| `Abramson_VanNieuwerburgh_2024_Rent_Guarantee_Insurance_NBER_w32582.pdf` | Abramson & Van Nieuwerburgh, *Rent Guarantee Insurance* | Source of χ_H. **p.30**: \$2,500 per household per month for the literally homeless (0.6% of population), half that for the doubled-up (0.83%), blended to \$1,775. Footnote 11 lists the components. Note it is an assumption inside their calibration, not an independent estimate. AE A15. |

## The empirical paper the AE asks about

| file | what it is |
|---|---|
| `Costantini_2025_Housing_First_or_Treatment_First_VA.pdf` | Costantini, *Housing First or Treatment First? Evidence from the VA's homelessness programs* (Nov 2025). Shares this paper's question, and the title this paper used before, with quasi-experimental VA evidence. AE A14. |

## Mortality, used to set the hazard multipliers

| file | what it is | what it set |
|---|---|---|
| `Baggett_et_al_2013_Mortality_among_homeless_adults_Boston_JAMA_IntMed.odt` | Boston Health Care for the Homeless cohort, race adjusted all cause mortality rate ratios | **`kappa_phi_h`**. 8.6 men and 9.6 women at 25-44, 4.5 at 45-64, 1.1 at 65-84. Replaced a flat 1.6. Also: overdose is 35% of deaths at 25-44, opioids in 81% of them |
| `Olfson_et_al_2015_Premature_Mortality_Schizophrenia_US_Medicaid_JAMA_Psychiatry.odt` | US Medicaid schizophrenia cohort, SMRs by age band | **`kappa_phi_m`**. All cause SMR 3.6 at 20-34, 3.4 at 35-54, 4.0 at 55-64 — flat, so the parameter stays constant |
| `Walker_McGee_Druss_2015_Mortality_in_Mental_Disorders_metaanalysis_JAMA_Psychiatry.pdf` | Meta analysis, 148 studies, any mental disorder | Level check on `kappa_phi_m`. Pooled RR 2.22; 1.80 natural causes, 7.22 unnatural |
| `Colton_Manderscheid_2006_Mortality_public_mental_health_clients_8_states_PCD.pdf` | Eight state public mental health clients; the "decades of life lost" study | Level check on `kappa_phi_m`. SMR about 3.2, 13 to 30 years of potential life lost |

`kappa_phi_d`, the SUD multiplier, is not set from a paper here: its profile
comes from CDC WONDER drug poisonings in `data/raw/`, and its level stays
calibrated to the drug price elasticity of participation, bracketed inside
Degenhardt et al.'s SMR range of 2.5 to 9.8.

## Drug supply elasticity

| file | what it is | what it set |
|---|---|---|
| `Alpert_Powell_Pacula_2018_Supply_side_drug_policy_abuse_deterrent_opioids_AEJ_Policy.pdf` | State level event study of the 2010 OxyContin reformulation | **`psi_2`**. Their Figure 6 regresses purity adjusted heroin prices (DEA STRIDE, 2000 to 2012) on initial OxyContin misuse. No significant differential price response where the demand shock was larger. Only a demand shift can identify a supply elasticity, and their time fixed effects absorb the national decline, so the Mexican supply expansion and post 2013 fentanyl entry are differenced out |
| `Evans_Lieber_Power_2018_How_OxyContin_reformulation_ignited_heroin_epidemic_NBER_w24475.pdf` | The substitution from OxyContin to heroin | Corroboration: heroin purity did not change at the reformulation. Also the source of the caution, they attribute the post 2013 deaths per use rise to fentanyl, and document the price fall from \$3,000 per pure gram in 1981 to under \$500 in 2012 as a supply expansion, not an elasticity |
| `Dobkin_Nicosia_2009_War_on_Drugs_Methamphetamine_AER.pdf` | 1995 DEA precursor seizure | Corroboration only. Prices tripled and recovered within about four months, hard to square with steep supply, but as a SUPPLY shock it identifies the demand elasticity rather than this one |

## Drug supply elasticity, the level

| file | what it is | what it set |
|---|---|---|
| `Hansen_Miller_Weber_2017_Taxation_of_Recreational_Marijuana_Washington_NBER_w23632.pdf` | Washington's 2015 switch from a 25% gross receipts tax at every supply chain stage to a single 37% retail excise, with universal state traceability data | **The only MEASURED supply elasticity in any drug market.** Consumers bear **44%** of the additional retail tax burden; their demand elasticity is about $-1$ within two weeks. Textbook incidence then implies $\varepsilon_s\approx 0.79$. Three caveats, all stated in the note: it is a LEGAL licensed market with capped canopy, the reform changed tax STRUCTURE rather than a rate, and they find tax invariance did not hold, so the textbook mapping is an approximation |
| `Rydell_Everingham_1994_Controlling_Cocaine_Supply_Versus_Demand_RAND_MR331.pdf` | The RAND cost effectiveness study of cocaine control, source of the often quoted supply elasticity near $-3.6$ | **Not used for `psi_2`, and the reason matters.** A negative elasticity means a downward sloping supply curve, driven by enforcement swamping: a larger market dilutes per unit enforcement risk. Caulkins and Reuter note that swamping "pertains to total drug volume ... not just or primarily drug-specific market volume", so it operates on the aggregate market. Our counterfactuals move one drug market and leave total US drug volume essentially unchanged, so that force is not active at our margin. Scanned with no text layer; OCR it if the figure is needed |
| `Caulkins_Reuter_2010_How_Drug_Enforcement_Affects_Drug_Prices_Crime_and_Justice.pdf` | The risks and prices framework | The cost STRUCTURE, not the slope. Growing and refining are under 1% of cocaine's retail price; a \$100 gram leaves Colombia at barely \$1; importation is 12% of the total and almost all risk compensation, in a competitive market. Also the source of the resolution of the sign problem: enforcement swamping "pertains to total drug volume ... not just or primarily drug-specific market volume", so the downward sloping force works on the aggregate market and not on ours |

## Housing First trials, and what they say about the health channels

| file | what it is | what it settled |
|---|---|---|
| `Stergiopoulos_et_al_2015_At_Home_Chez_Soi_RCT_scattered_site_housing_ICM_moderate_needs_JAMA.odt` | At Home/Chez Soi, N=1198, scattered site housing plus intensive case management, moderate needs, 4 Canadian cities | **The housing to mental health channel should NOT be added.** Mental illness symptom severity is null at every wave, $-0.96$ (p=.16), $-0.51$ (p=.46), 0.18 (p=.79), 0.57 (p=.44). Recovery Assessment Scale 0.09 (p=.92). **Severity of substance use problems 1.04 (0.89 to 1.21), p=.66, also null.** What IS large and significant: housing stability, the primary outcome, and condition specific quality of life, 5.91 (3.41 to 8.41), p<.001 |
| `Aubry_et_al_2015_At_Home_Chez_Soi_RCT_Housing_First_with_ACT_high_needs_PsychServices.pdf` | The high needs arm of the same trial, Housing First with Assertive Community Treatment | Same design, sicker population. Outcomes measured on the Colorado Symptom Index and the GAIN substance problem scale |
| `Sadowski_et_al_2009_Housing_and_case_management_ED_visits_hospitalizations_Chicago_RCT_JAMA.odt` | Chicago RCT, N=407, housing plus case management for chronically ill homeless adults | Health SERVICE use, emergency department visits and hospitalisations. The outcome family the model has no state for |
| `Milby_et_al_2005_To_House_or_Not_to_House_abstinence_contingent_housing_RCT_AJPH.pdf` | The trial behind `mu_H` and `b_hl_ratio`. N=196 cocaine-dependent homeless adults in day treatment, randomised across three housing conditions: no housing (NH), housing NOT contingent on abstinence (NACH), and abstinence-contingent housing (ACH) | **Read the arms before using the ratio.** The outcome is the LONGEST STRING of consecutive weeks abstinent out of a possible **24**, not a recovery hazard and not total weeks abstinent. Means (SD): NH **4.48** (4.98), NACH **6.60** (6.32), ACH **8.32** (6.79). The significance runs the other way from the target: NH vs ACH **P=.0004**, NACH vs ACH **P=.35**, and NH vs NACH **P=.058** |

**The Milby tension, and it is productive rather than awkward.** The model's
`b_hl_ratio` is calibrated to Milby, where housing raised abstinence. At Home/Chez
Soi finds unconditional housing does nothing to substance use. That is not a
contradiction: Milby's housing was **contingent on abstinence** and At Home/Chez
Soi's is **unconditional**. Contingency is doing the work, not housing. That
distinction is exactly what this paper is about, and the two trials together are
better evidence for it than either alone.

## Evidence reviews used for validation

| file | what it is |
|---|---|
| `Rog_et_al_Permanent_Supportive_Housing_Assessing_the_Evidence_PsychServices.mht` | *Psychiatric Services* review of permanent supportive housing. Housing retention and treatment engagement effects. A second capture of the same article is kept as `..._capture2.mht`; identical content, different save. |
| `Keenan_et_al_Accommodation_based_interventions_homelessness_review_PMC.mht` | Systematic review of accommodation-based interventions. |
| `CSH_literature_review_supportive_housing_by_study.pdf` | CSH study-by-study outcomes table. Marked *do not distribute without permission* — do not redistribute. |
| `To_House_or_Not_to_House_commentary.mht` | MIS-NAMED. Its `Snapshot-Content-Location` is `ajph.aphapublications.org/doi/full/10.2105/AJPH.2004.039743`, which is Milby et al. (2005) itself, not a commentary on it. Kept because the HTML capture carries the Results text in a searchable form that the PDF's text layer does not; the PDF above is the citable copy. |
| `Long_term_health_outcomes_homelessness_link.mht` | Long-term health outcomes of homelessness. |
| `Key_substance_use_and_mental_health_indicators_SAMHSA.mht` | SAMHSA key indicators report — the narrative companion to the NSDUH detailed tables in `data/raw/`. |

## Cited but not held here

Referenced in the note without a local copy: Desmond & Gershenson
(the homelessness–employment penalty κ_ueH), Loubière et al. (the eight-country
contingent valuation behind κ_x), and the National Alliance to End Homelessness
figure χ_H previously rested on.
