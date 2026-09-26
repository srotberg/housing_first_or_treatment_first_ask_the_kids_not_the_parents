# HF omega_c = 0.06 benchmark re-solved with the counterfactual's distribution numerics, 26 September

The author: "run the benchmark re-solve first". Why: the no-policy counterfactual should
reproduce the benchmark and does not (net revenue 6.1753 against the saved 6.0389, welfare
-0.26 per cent of CEV; results/counterfactuals_cf_local/null_tdm). The leading suspect was the
benchmark itself, solved on the loose 6e-4 distribution rule.

Build code/bench_tdm (scratchpad build_bench_tdm.sh): the benchmark binary with the calibration
loop's rule 6e-4 -> 5e-5 and at least 70 sweeps a block, as the counterfactual build cf_tdm.
Same seed and same 97-line handover as cfarm_bench's stage 1, 12 frozen blocks.

| block | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| net revenue, re-solve | 10.340 | 8.823 | 7.401 | 6.720 | 6.379 | 6.203 | 6.120 | 6.079 | 6.055 | 6.045 | 6.039 | 6.036 |
| net revenue, old | 10.277 | 8.804 | 7.439 | 6.788 | 6.411 | 6.231 | 6.122 | 6.084 | 6.060 | 6.049 | 6.041 | 6.039 |

Sweeps per block 70-76. Saved values against the old benchmark: net revenue 6.03603 (6.03888),
welfare of the youngest cohort 1353.065 (1353.052), median income 0.86296 (0.86292), drug
supply level 1.60442 (1.60467), average labour income 1.61679 (1.61642), net wealth 3.34501
(3.34606). THE BENCHMARK REPRODUCES ITSELF: it was not under-solved. The no-policy gap comes
from the counterfactual binary; the revenue-component diagnostic (REVDIAG builds) looks for it.
The full file set (bench_files.tar.gz, 125 MB, over the push limit) is NOT in git: it is in
code/cfarm_bench_tdm/ and the scratchpad (hf_omega_c_006_tdm_bench_files.tar.gz).
