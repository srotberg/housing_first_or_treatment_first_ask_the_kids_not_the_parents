# Section 4 against the code, claim by claim

Every statement Section 4 makes about the quantitative model, checked against
`code/housing_first_or_treatment_first_SR_v1.f90`. The rule is that the note and
the code must say the same thing; where they do not, the entry says which one is
wrong and what was done.

Status: **ALIGNED** the code does what the note says; **FIXED** it did not and
now does; **MISMATCH** it does not and the resolution is the author's call;
**MISSING** the note describes a mechanism the code does not contain.

## 4.1 Demographics, state and choice sets

| claim | verdict |
|---|---|
| State `s=(a,y,e,d,m,eta)`, `e in {1,2,3}` | **ALIGNED.** `financial_index`, `employment_index`, and `unemployment_index` which packs `(e,m,d)` through `emp_of`/`smi_of`/`sud_of`, plus `voucher_index`. |
| Housing `h' in {h1,h2,h3,h4}`, `h1` homelessness | **ALIGNED.** `housing_status_grid_size=3` with `lowest_housing_grid_point=-1` gives the four statuses -1,0,1,2. |
| Survival `phi(j,h',d,m,tau)` | **ALIGNED.** `survival_probability(age_index,is_homeless_1,survival_sud_of(addiction_index,treatment_choice_now),smi_of(unemployment_index))`. |
| Newborns replace the dead exactly | **ALIGNED.** |

## 4.2 Preferences

| claim | verdict |
|---|---|
| Weights `1-gamma-theta`, `gamma`, `theta` sum to one | **ALIGNED.** `relative_share_of_housing_1=relative_share_of_housing*(1-relative_share_of_addiction_1)` and the consumption weight `(1-relative_share_of_housing)*(1-relative_share_of_addiction_1)`; the three sum to one. NOTE the Fortran's `relative_share_of_housing` is `gamma/(1-theta)`, not `gamma`. |
| Leisure `omega_ell (1-n)^(1-sigma_ell)/(1-sigma_ell)` | **ALIGNED.** `max_labor_supply=1.d0`, so `(max_labor_supply-labor_supply)` is `(1-n)`. |
| `+aleph` | **ALIGNED.** |
| `-tau*bar_tau^u` | **ALIGNED.** |
| `-kappa_x H` | **ALIGNED in substance.** Applied in `value_function_comparison`, not the Bellman. `H` is aggregate and taken as given, so it shifts every value equally and cannot move a policy; the welfare comparison is where it must appear, and it does. |

## 4.3 Income, taxes and transfers

| claim | verdict |
|---|---|
| UI paid in the first period of a spell only | **FIXED.** `employment_transition` continued a spell in the SAME state, so with `probability_of_ui=1` every job loser entered the insured state and never left: UI ran for life and the uninsured state carried zero mass. Now `1 -> 3 -> 2 -> 2`. |
| DI: `zeta_DI*y*eps(j)` for `j<J_R, e=3, m=1`, not stopping until recovery | **MISSING.** `zeta_DI=0.25` occurs exactly once in the file, its own declaration. Disability insurance is not in the model. A non-employed household with SMI receives nothing once UI ends. |
| Retirement income `0.40*y` | **MISMATCH.** The code uses the US PIA bend points on lifetime income relative to the average: 0.9 below 0.3, `0.27+0.32*(x-0.3)` to 2, `0.81+0.15*(x-2)` to 4.1, flat 1.13 above. Progressive and capped, not a flat 40 per cent of `y`. |
| UI base `psi*min{y*eps(j), ybar}` | **MISMATCH.** The code pays `min(psi*average_labor_income_by_employment(node), cap*average_income)`. The base is the node's average income, not the household's own current earnings `y*eps(j)`, so it carries neither the age profile nor `rho_d`/`rho_m`. |
| Food assistance `F=max{0, cbar*ybar - varrho*(y^g+ra)}` | **ALIGNED.** `max_food_cost*avg_income_to_use_1` less `food_stamp_taper=0.30` times means-tested income. |
| Progressive labour tax `tau_ell*(y^g)^xi`, flat `tau_k` on capital | pending |
| Voucher `Vch=1{eta=1}1{h'!=h1}max{0, p_r*h' - kappa_r*y^g}` | pending |
| A voucher holder who becomes homeless keeps the voucher | pending |
| Rents normalised to one | **MISMATCH.** `rent_calibrated=1.079`. Scaling only, but the note's sentence is not literally true of the code. |
| Progressive labour tax `tau_ell*(y^g)^xi`, flat `tau_k` on capital | **ALIGNED.** `wage_income_tax_paid = max(taxable - tau_ell*taxable^xi, 0)` with `taxable = y^g - personal_exemption - deduction`, and BOTH of those are zero (`standard_deduction_data=0`, `personal_exemption_data=0`), so after-tax labour income is exactly `tau_ell*(y^g)^xi`. `investment_income_tax=0.15` is the note's `tau_k`. |
| Voucher `Vch=1{eta=1}1{h'!=h1}max{0, p_r*h' - kappa_r*y^g}` | **ALIGNED.** `calculate_housing_voucher` computes the subsidy on the household's OWN chosen dwelling, and its comment records that it was changed away from a HUD payment standard specifically to match this equation. Homelessness needs no indicator: it pays no rent, so the subsidy is zero there. |
| A voucher holder who becomes homeless keeps the voucher | **ALIGNED.** Retention is tested on income eligibility only. |
| No tenure choice; all four statuses are rental or the street | **ALIGNED.** The owner states were removed; the grid comment records that six of the old eight slots were owner states that no longer exist. |

## 4.6 Drug use, the SUD, recovery and treatment

| claim | verdict |
|---|---|
| `pi_d(v)=1-exp(-lambda v)` | **ALIGNED.** `addiction_onset_hazard`, in the QUANTITY not the spending. |
| Initiation only up to age `J_E` | **ALIGNED.** `max_age_to_choose_addiction` gates `allow_to_choose_addiction` at all five call sites. |
| `pi_r=min{1, pibar_r * mu_H^1{h1} * mu_m^1{m} * g^tau}` | **ALIGNED.** `mu_H` is folded into the base (`probability_of_stopping_addiction_if_homeless` is `(4.48/6.60)*0.025`), `g` is `treatment_effect_on_recovery=1.35`, `mu_m=0.82` via `recovery_with_smi`, all multiplicative under a `min` at one. |
| Treatment requires `v=0` | **ALIGNED as the code stands**, but see the open item below: removing this restriction was approved and has not been done, and doing it makes the note wrong. |
| Treatment restores baseline mortality for that period | **ALIGNED.** `survival_sud_of(d,tau)=d*(1-tau*include_treatment)`. |

## 4.7 Serious mental illness

| claim | verdict |
|---|---|
| `onset_m(j)=(s(j+1)-s(j)(1-lambda_m))/(1-s(j))` | **ALIGNED**, written out exactly, with a clip at zero that is counted and reported rather than silent. |
| `Pr(m'=1|m=0,d)=onset_m(j)*iota^1{d=1}`, `Pr(m'=0|m=1)=lambda_m` | **ALIGNED.** `smi_transition`. |
| The SMI chain does not depend on housing | **ALIGNED**, and the function carries a comment forbidding a housing argument, citing At Home / Chez Soi. |
| SMI affects five objects, the fifth being disability income | **MISSING**, see DI above. Four of the five are present. |

## 4.8 What the SUD, SMI and homelessness cost

| claim | verdict |
|---|---|
| `phi=1-min{1,(1-phibar)*kappa_phiH^1{h1}*kappa_phid^{1{d}1{tau=0}}*kappa_phim^1{m}}` | **ALIGNED**, all three multiplicative under a `min` at one, with `tau` switching the SUD factor off. |
| `kappa_phid(j)=1+(kappabar_phid-1)*sigma_d(j)` | **ALIGNED.** |
| `kappa_phiH(j)=max{1, RR(j)/((1-s)+s*kappa_phid(j))}` | **ALIGNED.** |
| `kappabar_phid` between 6 and 10 | **ALIGNED.** `kappa_phi_d_level=8.0`. |
| Separation and finding carry no productivity term | **ALIGNED.** `adjusting_unemployment_probabilities_based_on_productivity` returns a profile and then overwrites it with 1, and says so in a comment: the factor is deliberately dead. |
| Equation (femp): `kappa^{+1}` on job FINDING and `kappa^{-1}` on separation, "each multiplier below one makes a job likelier to lose" | **MISMATCH, AND THE EQUATION IS THE ONE THAT IS WRONG.** `employment_transition` does `sep*kappa_uem` and `find/kappa_uem`, so ABOVE one is worse. The note's own prose agrees with the code -- the entry for `kappa_ued` says "raise it and the private cost rises" -- so only the exponents in (femp) are reversed. |

## 4.12-4.15 Government, drug market, law of motion

| claim | verdict |
|---|---|
| `C(S_v)=(nu_1/nu_2)S_v^{nu_2}`, `p_v=nu_1 S_v^{nu_2-1}`, elasticity `1/(nu_2-1)`, `nu_1` set so `p_v=1` at the benchmark | **ALIGNED**, stated in the code in the same algebra. |
| `tau_ell` clears the budget every simulation | **ALIGNED.** |
| Government outlay includes DI | **MISSING**, as above. |
| Newborns start with zero assets, clean, **without SMI**, without a voucher | **MISMATCH.** Newborns are seeded with SMI at the age-one prevalence, `newborn_smi_at_birth=smi_prevalence_by_age(1)`, about 0.121. That seeding was added deliberately: without it the chain built SMI by onset from age two alone and the all-ages rate came out three times too small. The code is right and the note's sentence is stale. |

## Open items: all closed

Resolved by moving the CODE to the note, on the author's instruction.

| item | what was done |
|---|---|
| **Disability insurance was not in the model.** `zeta_DI=0.25` occurred exactly once in 32,000 lines, its own declaration, while the note gave DI a case in the income equation, a place in the list of what SMI affects, an entry in the calibration table and a line in the government budget. | **IMPLEMENTED.** A household that is out of work past the insured period and carries SMI now receives `zeta_DI*y*eps(j)`, and it does not stop until the household recovers, which the state encodes on its own: the uninsured state persists until a job is found and SMI until `lambda_m` fires. `govt_spending_on_di` is accumulated separately and subtracted in the budget, so eq:fgovt's outlay side is complete. |
| **Retirement income** was the US PIA bend point schedule on lifetime income relative to the average, not the note's `0.40*y`. | **REPLACED** by `ss_replacement_rate*y` with the rate at 0.40. The old schedule replaced 90 per cent at the bottom against the note's 40 and capped the top, where the note has no cap. |
| **The UI earnings base** was `min(psi*node average income, cap*average income)`, which carried neither the age profile nor `rho_d`/`rho_m` and put the cap on the benefit rather than on the base. | **REPLACED** by `psi*min{y*eps(j), ybar}`, the note's rule. |
| **Rents were not normalised to one**, `rent_calibrated=1.079`. | **NORMALISED.** The earlier attempt set the rent constants to one and left `calibrated_stationary_housing_price` at 13, so the market routine still produced `0.083*13=1.079` and the constants lied. The price is now `1/himmelberg_etal_rent_to_price`, so the product is one by construction and Himmelberg's ratio is untouched; the management cost is scaled by the same factor. |
| **The treatment abstention restriction.** | **KEPT**, on instruction. `optimize_frac_spent_on_addiciton` returns `frac_spent_on_addiction=0` whenever treatment is taken, which is what Section 4.6 says and what the mortality exemption in Section 4.8 is justified by. Note and code agree; nothing to do. |

Two further repairs found while doing this:

- **`out_of_work_income` now exists.** What a working age household out of work receives was written out at FOUR sites: its own income and three statistics that have to agree with it. That is how the UI rule drifted in the first place, so the rule now lives in one function and the four sites call it.
- **`income_by_age_renter` added the population to the income.** It accumulated `(benefit) + distribution_mass_used` where every sibling accumulator uses a product. Fixed in the same pass.

## Where the note was the one that moved

| item | what was done |
|---|---|
| Equation (femp) had `kappa^{+1}` on job finding and `kappa^{-1}` on separation, making a `kappa` BELOW one the bad case | **NOTE CORRECTED.** The code does the reverse and so does this section's own prose, which says of `kappa_ued` that raising it raises the private cost. Exponents swapped; the sentence now reads "above one". |
| Newborns were described as arriving without SMI | **NOTE CORRECTED.** They are seeded at the age-one prevalence, about 0.121, which was added deliberately: building the chain by onset from age two alone left the all-ages rate three times too small. |
