#!/usr/bin/env bash
# Run the coordinate scan locally, base point first, then stage 1's instruments,
# then the rest.  Each file is a list of run_one_point.sh lines; run_one_point
# flocks, so this is safe beside anything else in the checkout.
cd "$(dirname "$0")/.."
ORDER="_base kkk_sigma_scale probability_becoming_unemployed addiction_scalar_1 \
max_food_cost discount_factor lambda_addiction smi_onset_level \
smallest_rental_relative_to_lowest_income relative_share_of_leisure \
relative_share_of_housing relative_share_of_addiction_1 \
probability_of_voucher_benchmark_used labor_income_tax_rate value_of_life \
multiple_of_probabilities_of_employment_if_addicted bottom_productivity_level \
kappa_uem utility_cost_of_treatment mu_homeless size_homelessness \
rr_homeless_old_level"
for name in $ORDER; do
  f="code/scan/$name.txt"
  [ -f "$f" ] || continue
  n=0
  while IFS= read -r line; do
    n=$((n+1)); [ -z "$line" ] && continue
    echo "$(date -u +%H:%M:%S)  $name line $n" >> code/scan_run.log
    eval "$line" >> code/scan_run.log 2>&1
  done < "$f"
  echo "$(date -u +%H:%M:%S)  DONE $name" >> code/scan_run.log
done
echo "$(date -u +%H:%M:%S)  SCAN COMPLETE" >> code/scan_run.log
