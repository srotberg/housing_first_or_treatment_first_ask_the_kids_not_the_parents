# TREATMENT FIRST at omega_c = 0.06 -- PARTIAL, NOT CONVERGED

**Read at block 7, 2026-09-24 02:55Z. The run is still going.**
Nothing here is a final number. The stop rule has NOT fired.

Run started 2026-09-24 00:52Z, `sh code/remote_tf_point.sh 0.06`, frozen on the
published two-class omega_c = 0 benchmark seed in `code/scan_seed/`.
Reference: b = 0.098916, lambda_d = 0.043579.

This is the policy arm the paper turns on. It differs from the benchmark in
exactly three places, everything else being the converged vector:

    weight_on_child                                     0.06
    voucher_conditional_on_clean                        1
    increased_prob_of_voucher_if_homeless_and_addicted  0

The three test parameters bind for the first time in this run -- they are inert
in the benchmark, where `voucher_conditional_on_clean = 0` -- and are left at
their declared values, carried unchanged by the seed:

    probability_of_detection       0.95      line 487
    probability_of_false_positive  0.005     line 488
    cost_per_drug_test             0.00031   line 504

kappa_x is at the calibrated 0.8139 from the handover base, not the declared
0.002; the log records `HANDOVER kappa_x: 2.0E-003 -> 0.8139`.

## THE BLOCK TABLE

Verbatim from `run.log`. Every block printed b, lambda_d and exactly one
`BUDGET bequest_residual`, so the pairing is 1:1 with no interpolation.
`y` is carried through because it is on the same line.

| block | b | lambda_d | bequest_residual | block_move | h_1 | y |
|---|---|---|---|---|---|---|
| 1 | 5.1092800075345876E-002 | 2.3275213214654544E-002 | 2.1391690213851584 | 1.0000000000000000 | 7.6762296327784587E-003 | 1.1459536063642153 |
| 2 | 3.9777410843911620E-002 | 1.6882351414743969E-002 | 1.8848057458674137 | 0.27466394146222045 | 6.6219939468162084E-003 | 1.3832667489509447 |
| 3 | 3.7429644792203835E-002 | 1.5822967777763586E-002 | 1.6869277376552747 | 8.6948908602583017E-002 | 6.3539702742445390E-003 | 1.5035402830784725 |
| 4 | 3.7114706445256114E-002 | 1.5661533730520344E-002 | 1.6186114942240206 | 4.0429401638165885E-002 | 6.3079604141100028E-003 | 1.5643275170622137 |
| 5 | 3.5632041914979665E-002 | 1.5367836620607620E-002 | 1.5869984307874863 | 3.9948168052019145E-002 | 6.2742176384389141E-003 | 1.5947827145795894 |
| 6 | 3.3265070267941281E-002 | 1.4376263900875725E-002 | 1.5427841867776044 | 6.6428178679350733E-002 | 6.1878181605855547E-003 | 1.6102183912300738 |
| 7 | 3.2231354918082954E-002 | 1.3737528485317689E-002 | 1.5231418282104052 | 4.4429861608141961E-002 | 6.1269087170518028E-003 | 1.6182628323185964 |

## WHY IT HAS NOT STOPPED

The family rule is |b(k) - b(k-1)| / b(k-1) < 0.5 per cent for TWO CONSECUTIVE
blocks, or block 12, whichever comes first. `block_move` is never used alone.

    1 -> 2   22.15%
    2 -> 3    5.90%
    3 -> 4    0.84%
    4 -> 5    3.99%
    5 -> 6    6.64%
    6 -> 7    3.11%

No block has yet come under 0.5 per cent, so the two-consecutive counter has
never started. The step fell to 0.84 per cent at block 4 and then rose again,
which is why block 4 was NOT treated as convergence.

It is not cycling: b falls monotonically at every block. The steps are noisy
but bounded, and `bequest_residual` descends monotonically throughout --
2.1392, 1.8848, 1.6869, 1.6186, 1.5870, 1.5428, 1.5231 -- and is now about
0.04 to 0.07 above the 1.45-1.48 band where every settled point in this family
rests. On the family's own evidence the run is still inside the restart
transient, and the early blocks of every point OVERSTATE the drop.

## LATEST BLOCK ONLY -- BLOCK 7

    model_drug_tests               3.2751       derived, see below
    govt_spending_on_drug_tests    1.0152813540873138E-003
    tau_u  treatment take up       0.30650792732039178      target 0.245

`model_drug_tests` is never written to the log. `BUDGET drug_tests=` is
`govt_spending_on_drug_tests` (written at line 20691), which line 20655 builds
as `voucher_conditional_on_clean * cost_per_drug_test * model_drug_tests`, so
the count is recovered exactly as 1.0152813540873138E-003 / 3.1E-004.

## PROVISIONAL REDUCTIONS -- DO NOT QUOTE

Against the benchmark b = 0.098916 and against the pure omega_c = 0.06 point
b = 0.081242. Both widen at every block and neither has settled.

| block | vs benchmark | vs omega_c = 0.06 |
|---|---|---|
| 1 | -48.35% | -37.11% |
| 4 | -62.48% | -54.32% |
| 7 | -67.42% | -60.33% |

## ONE CAVEAT ON WHAT THIS RUN MEASURES

`is_counterfactual` is a compile-time `parameter` fixed at 0 (line 189), and the
branch at line 32257 that takes the voucher from a HOUSED household which fails
the test is guarded on `is_counterfactual==1`. So in this build the
conditionality binds through the homeless branch at line 32247, which is
ungated, while a housed household that fails stays in category 1 and faces only
the false positive rate. The enforcement block at 36670 is gated only on
`voucher_conditional_on_clean`, so testing and its costs are live throughout.

The run is therefore conditionality that bites on the homeless, not the
universal variant. Recorded so the number is labelled correctly.
