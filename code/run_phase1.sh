#!/usr/bin/env bash
# PHASE 1, end to end: one benchmark, then the counterfactuals off it.
#
# The benchmark is ONE SOLVE. run_variant.sh save prints the complete moments
# block and then writes the fifty-five .dat files a counterfactual imports, so
# the numbers quoted and the numbers imported come from the same pass over the
# same distribution. benchmark_of_record.py extracts the former from the log
# that produced the latter, and verify_benchmark_state.py refuses to go on if
# the two ever come apart.
set -uo pipefail
cd /home/user/housing_first_or_treatment_first

VEC=$(grep -a "^VECTOR " code/points/point_6876263050.txt 2>/dev/null | head -1 | sed 's/^VECTOR //')
[ -n "$VEC" ] || { echo "PHASE1: no benchmark vector"; exit 1; }

echo "PHASE1 benchmark"
bash code/run_variant.sh save $VEC > code/p1_bench.log 2>&1
grep -a "run_variant: finished" code/p1_bench.log || { echo "PHASE1 benchmark FAILED"; exit 1; }
python3 code/benchmark_of_record.py || exit 1
python3 code/verify_benchmark_state.py || { echo "PHASE1 STOPPED: the state is not importable"; exit 1; }
echo "PHASE1 benchmark done and audited"

run () {
    name=$1; shift
    echo "PHASE1 $name starting"
    bash code/run_variant.sh cf $VEC "$@" > "code/p1_${name}.log" 2>&1
    echo "PHASE1 $name: $(grep -a 'run_variant: finished' code/p1_${name}.log)"
    # DID IT CONVERGE, OR DID IT HIT THE CAP? A run that stops at
    # max_counterfactual_loops is NOT a result and must not be read as one.
    ML=$(grep -a "run_variant: log is\|log variant_cf" "code/p1_${name}.log" | tail -1 | sed 's/.*log //;s/.*log is //')
    LOOPS=$(grep -ac "loop_count=" "code/${ML}" 2>/dev/null || echo 0)
    if [ "${LOOPS:-0}" -ge 80 ]; then
        echo "PHASE1 $name NOT CONVERGED: hit the ${LOOPS}-loop cap"
    else
        echo "PHASE1 $name converged in ${LOOPS} loops"
    fi
}

# TF WITH RATIONED VOUCHERS. The voucher rate stays at the benchmark's, so this
# is a change in who gets the scarce vouchers plus the drug test, not a change
# in how many exist. Expressible only since universality was keyed on the rate
# rather than on the conditionality.
run tf_rationed  increased_prob_of_voucher_if_homeless_and_addicted=0 \
                 voucher_conditional_on_clean=1

# UNIVERSAL HF. Every eligible household gets a voucher, the addicted homeless
# keep their preference, nothing is conditional.
run universal_hf probability_of_voucher_benchmark_used=1 \
                 increased_prob_of_voucher_if_homeless_and_addicted=1 \
                 voucher_conditional_on_clean=0

# UNIVERSAL TF. Every eligible household gets one and keeps it only on v=0 and
# no SUD, tested at 0.9 detection and 0.05 false positive.
run universal_tf probability_of_voucher_benchmark_used=1 \
                 increased_prob_of_voucher_if_homeless_and_addicted=0 \
                 voucher_conditional_on_clean=1

echo "PHASE1 COMPLETE"
