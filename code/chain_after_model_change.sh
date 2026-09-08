#!/usr/bin/env bash
# Re-establish the benchmark and its saved state after a model change, then run
# one counterfactual. Serial by construction: each step needs the one before it.
set -uo pipefail
cd /home/user/housing_first_or_treatment_first
VEC=$(grep -a "^VECTOR " code/points/point_6876263050.txt | head -1 | sed 's/^VECTOR //')
[ -n "$VEC" ] || { echo "CHAIN: no benchmark vector"; exit 1; }

echo "CHAIN 1/3 benchmark point"
bash code/run_one_point.sh $VEC > code/chain_bench.log 2>&1
grep -aq "END OF MOMENTS" code/points/point_*.txt 2>/dev/null
echo "CHAIN 1/3 done: $(tail -3 code/chain_bench.log | head -1)"

echo "CHAIN 2/3 benchmark state"
bash code/run_variant.sh save $VEC > code/chain_save.log 2>&1
echo "CHAIN 2/3 done: $(grep -a 'run_variant: finished' code/chain_save.log)"

echo "CHAIN 3/3 universal TF counterfactual"
bash code/run_variant.sh cf $VEC \
    probability_of_voucher_benchmark_used=1 \
    increased_prob_of_voucher_if_homeless_and_addicted=0 \
    voucher_conditional_on_clean=1 > code/chain_cf_utf.log 2>&1
echo "CHAIN 3/3 done: $(grep -a 'run_variant: finished' code/chain_cf_utf.log)"
echo "CHAIN COMPLETE"
