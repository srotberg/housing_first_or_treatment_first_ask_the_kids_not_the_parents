# aleph: what is actually wrong

All lines are `code/housing_first_or_treatment_first_SR_v1.f90`. Read only; nothing run.

## 1. `model_value_of_life` -- construction is self-consistent, but it is an AGE-1 aggregate divided by a WHOLE-POPULATION ratio

Reset (7758), guarded: `if (accumulating_beta_types==0) model_value_of_life(time_period)=0`.
Accumulated once only, at 8003, inside `if (age_index==1)` (7986) and `if (distribution_mass_used>0)` (7997):
`model_value_of_life(time_period)=model_value_of_life(time_period)+(value_function_used/MU_1)*distribution_mass_used`.
It IS mass-weighted, and it runs over age one only, so its mass is one cohort (about 1 on `sum_of_distribution` ~51 with `life_span=60`, 170), not the population.
Divided once, at 9312, guarded `if (current_beta_type==number_of_beta_types) then`:
`model_value_of_life(time_period)=model_value_of_life(time_period)/max(pooled_mass_all/max(mass_by_beta_type(1),10.d0**(-12)),10.d0**(-12))`.
`pooled_mass_all` (9101-9104) is the mass of BOTH types over ALL ages; `mass_by_beta_type(1)` the first type's over all ages. The ratio is ~2 at two types, which is right for pass-doubling. But the numerator's own divisor is a newborn mass, and one already exists and is unused here: `pooled_mass_youngest` (14301-14303), which `calculate_welfare` uses at 14307 for exactly this cohort. Nothing else writes `model_value_of_life`.

## 2. `model_average_labour_income` -- it IS overwritten after the division, before `vsl_1` is read

Reset 7795: `if (accumulating_beta_types==0) model_average_labour_income(time_period)=0`.
Accumulated 8947, inside `if ((in_retirement==0) .AND. ((emp_of(unemployment_index)==1)))` (8943).
Divided at 9676, guard exactly: `if (current_beta_type==number_of_beta_types) model_average_labour_income(time_period)=model_average_labour_income(time_period)/max(model_total_workers(time_period),10.d0**(-14))`.
The nine-routine chain is called at 35327-35336. The division is in the first of them (`stationary_equilibrium_statistics`, 7614-9710). **No other routine in the chain writes it** -- every later occurrence (9725, 10629, 10905, 11519, 13643, 14114, 14331, 15359 ...) is a read of the form `avg_income_to_use_1=is_counterfactual*average_labor_income_calibrated+(1-is_counterfactual)*model_average_labour_income(time_period)`; 13537 is `model_average_labour_income_TAX`, a different variable.

**But `calibrating_model` writes it between the chain and the print.** At 37743-37745, after the chain and before `call print_all_moments()` (37871):
`model_average_labour_income(1)=weight_on_labor_income*model_average_labour_income(1)+(1-weight_on_labor_income)*previous_average_labor_income`, `weight_on_labor_income=0.5` (4024).
`previous_average_labor_income` is assigned in only two places (34993, 35321). 35321 sits INSIDE the beta loop `do current_beta_type=1,number_of_beta_types` (35249) ... `end do` (35337), at line 35321, BEFORE `call stationary_equilibrium_statistics(1)` (35327). On the last pass (`current_beta_type=2`) it therefore captures the value left by pass 1 -- and pass 1 skipped the 9676 division, because `1/=number_of_beta_types`. So at two types `previous_average_labor_income` is the UNDIVIDED SUM of labour income over the patient type's workers, and line 37743 mixes it half-and-half into the mean.
Consequences, in order: `call set_SS_benefits(1)` (37783) multiplies `model_ss_benefits` by that inflated value (28716-28718); `print_all_moments` reads it at 4939, so the printed `MOMENT aleph` (5253) uses a denominator inflated by roughly `(1+W1)/2` where `W1` is the first type's worker mass; the next outer iteration's solve reads it as `avg_income_to_use_1` and as `standard_deduction` (27105). At `number_of_beta_types=1` the same lines are harmless (35321 then captures a properly divided mean), which matches aleph being stable at one type and swinging at two.
Note also that the calibration's own aleph, `model_vsl_ratio_1=model_value_of_life(1)/model_average_labour_income(1)` (37065-37066), runs BEFORE 37743 and so uses a DIFFERENT denominator from the printed one. The two aleph figures in a single point are not the same statistic.

## 3. `model_total_workers` -- a MASS, never normalised

Reset 7789 `if (accumulating_beta_types==0) model_total_workers(time_period)=0`; accumulated 8945 `model_total_workers(time_period)=model_total_workers(time_period)+distribution_mass_used`, under the same employed/working-age guard. There is no other write anywhere (only the print at 31121). So it is a sum of distribution weights of order tens, pooled over both passes, and 9676 does produce a genuine per-worker average -- on the last pass only.

## 4. Units -- `model_average_labour_income` matches the budget constraint exactly; `model_output` differs only by the SUD/SMI penalties

Accumulator (8947-8952): `labor_supply_used*employment_grid(age_index,employment_index)*labour_deterministic_efficiency(age_index)*(rho_d**(min(sud_of(unemployment_index),1)*include_rho_d))*(rho_m**(min(smi_of(unemployment_index),1)*include_rho_m))*distribution_mass_used`.
Budget (21109-21116): `max_gross_wage_income_1=employment_grid(age_index,employment_index)*labour_deterministic_efficiency(age_index)*(rho_d**...)*(rho_m**...)` then `gross_wage_income_1=labor_supply_1*max_gross_wage_income_1`. Identical per-unit term. There is no wage variable in the file at all (no `wage_rate`, no price on labour anywhere): the wage is one, so "efficiency units" and "goods" are the same unit here and nothing is missing.
`model_output` (8043-8046): `(labor_supply_used*employment_grid(...)*labour_deterministic_efficiency(age_index))*distribution_mass_used` -- the same product WITHOUT `rho_d`/`rho_m`. So yes, same units; `model_output` is literally identical to `model_total_efficiency_units` (8047-8049). Units are not the fault.

## 5. Other places that read it as a per-household mean

`5189` treatment price over average vs 0.034-0.065; `5222` `max_food_cost/avg` vs 0.039586; `5225-5226` gross eligibility cutoff vs 0.214872; `5327` food stamps over average (labelled OLD); `5950-5955` income of drug users / of the disordered over average; `6132` `floor_1=10.d0**(-1)*model_average_labour_income(1)` in `weighted_drug_share_now`; `27105` `standard_deduction=(model_average_labour_income(1)*standard_deduction_as_percent_of_average_labor_income)`; `28716-28718` `model_ss_benefits(...)=model_ss_benefits(...)*model_average_labour_income(time_period)`; `21095-21096`, `21191-21192` (`max_MID_debt` cap), and every `avg_income_to_use_1` site listed in (2); `36821` `income_floor_1=10.d0**(-1)*model_average_labour_income(1)`; `36915-36916` and `36967-36970` income-of-the-disordered-over-mean comparisons; `37124`, `37131-37135` cbar's update and distance.
`37124` is a second, independent level-over-mean fault: `govt_spending_on_food_stamps(1)/model_average_labour_income(1)` is an AGGREGATE over a MEAN. The declaration at 2646-2654 says the per-household figure "is computed once ... and the moment reads this instead", but `model_food_stamps_per_household` is declared at 2654 and never assigned or read anywhere in the file.

## What would settle the rest

Two prints from one two-type point, taken at 4939: `model_total_workers(1)` and the pass-1 partial sum. If `model_average_labour_income(1)*model_total_workers(1)` (already printed at 4970) is not close to `model_all_labour_income(1)`, the 37743 contamination is confirmed numerically. To settle whether aleph's target of 80 was set against a per-newborn or an aggregate figure, compare `model_value_of_life(1)` with `pooled_mass_youngest`: if that mass is near one, the current aggregate and the per-newborn mean are nearly the same number and the target is fine as written; if it is not, the numerator needs 14301's divisor.
