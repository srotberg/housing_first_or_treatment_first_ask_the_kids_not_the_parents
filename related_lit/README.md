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
| `Costantini_2025_Housing_First_or_Treatment_First_VA.pdf` | Costantini, *Housing First or Treatment First? Evidence from the VA's homelessness programs* (Nov 2025). Shares this paper's title and question, with quasi-experimental VA evidence. AE A14. |

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

## Evidence reviews used for validation

| file | what it is |
|---|---|
| `Rog_et_al_Permanent_Supportive_Housing_Assessing_the_Evidence_PsychServices.mht` | *Psychiatric Services* review of permanent supportive housing. Housing-retention and treatment-engagement effects. |
| `Keenan_et_al_Accommodation_based_interventions_homelessness_review_PMC.mht` | Systematic review of accommodation-based interventions. |
| `CSH_literature_review_supportive_housing_by_study.pdf` | CSH study-by-study outcomes table. Marked *do not distribute without permission* — do not redistribute. |
| `To_House_or_Not_to_House_commentary.mht` | Commentary on the Housing First / Treatment First debate. |
| `Long_term_health_outcomes_homelessness_link.mht` | Long-term health outcomes of homelessness. |
| `Key_substance_use_and_mental_health_indicators_SAMHSA.mht` | SAMHSA key indicators report — the narrative companion to the NSDUH detailed tables in `data/raw/`. |

## Cited but not held here

Referenced in the note without a local copy: Milby et al. (the abstinence and
housing-access arms behind `b_hl_ratio` and moment 24), Desmond & Gershenson
(the homelessness–employment penalty κ_ueH), Loubière et al. (the eight-country
contingent valuation behind κ_x), and the National Alliance to End Homelessness
figure χ_H previously rested on.
