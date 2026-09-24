# TREATMENT FIRST at omega_c = 0.06 -- CONVERGED

Run 2026-09-24 00:52Z to 03:07Z, `sh code/remote_tf_point.sh 0.06`, frozen on
the published two-class omega_c = 0 benchmark seed in `code/scan_seed/`.
Reference: b = 0.098916, lambda_d = 0.043579.

This is the policy arm the paper turns on. It differs from the benchmark in
exactly three places, everything else being the converged vector:

    weight_on_child                                     0.06
    voucher_conditional_on_clean                        1
    increased_prob_of_voucher_if_homeless_and_addicted  0

The three test parameters bind for the FIRST time in this run -- they are inert
in the benchmark, where `voucher_conditional_on_clean = 0`, which is why they
are absent from the calibration table. Left at their declared values, carried
unchanged by the seed:

    probability_of_detection       0.95      line 487
    probability_of_false_positive  0.005     line 488
    cost_per_drug_test             0.00031   line 504

kappa_x ran at the calibrated 0.8139 from the handover base, not the declared
0.002: the log records `HANDOVER kappa_x: 2.0E-003 -> 0.8139`.

## THE BLOCK TABLE

Verbatim from `run.log`. Every block printed b, lambda_d and exactly one
non-zero `BUDGET bequest_residual`, so the pairing is 1:1 with no interpolation.
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
| 8 | 3.2113972866430134E-002 | 1.3631575997157282E-002 | 1.5188582681383305 | 7.7126310073639967E-003 | 6.1174375989379425E-003 | 1.6223657274207535 |
| 9 | 3.2078509824432895E-002 | 1.3599508752394534E-002 | 1.5173224456696981 | 2.3524238700965865E-003 | 6.1140645215035372E-003 | 1.6244478652420207 |

## WHY IT STOPPED

**The 0.5 per cent rule fired at block 9.** Not block 12, and not `block_move`.

    |b(8) - b(7)| / b(7) = |0.032113973 - 0.032231355| / 0.032231355 = 0.3642%
    |b(9) - b(8)| / b(8) = |0.032078510 - 0.032113973| / 0.032113973 = 0.1104%

Two consecutive blocks under 0.5 per cent, so the run was stopped by hand at
block 9 in accordance with the family rule. `block_move` was still 2.35e-3
against its own 1e-3 rule and would never have fired; it was correctly not used.

Last three b, for checking the arithmetic:

    block 7   0.032231354918082954
    block 8   0.032113972866430134
    block 9   0.032078509824432895

A false start at block 4 is why blocks 5 to 7 were run rather than stopped: the
step fell to 0.84 per cent there and then ROSE again to 3.99, 6.64 and 3.11 per
cent. The full step sequence:

    1->2  22.15%   2->3   5.90%   3->4   0.84%   4->5   3.99%
    5->6   6.64%   6->7   3.11%   7->8   0.36%   8->9   0.11%

## HEADLINE OUTCOMES, MODEL UNITS, BLOCK 9

    b          total drug users     0.032078509824432895
    lambda_d   disorder rate        0.013599508752394534
    h_1        homelessness rate    0.0061140645215035372
    theta      drug spending share  0.50268094097257798
    tau_u      treatment take up    0.30281326508440204
    pi_V       eligibles w/ voucher 0.24179833385677008
    y                               1.6244478652420207
    bequest_residual                1.5173224456696981

    govt_spending_on_drug_tests     1.0186070697786433E-003
    model_drug_tests                3.2858  (derived, see below)

`model_drug_tests` is never written to the log. `BUDGET drug_tests=` is
`govt_spending_on_drug_tests` (written at line 20691), which line 20655 builds
as `voucher_conditional_on_clean * cost_per_drug_test * model_drug_tests`, so
the count is recovered exactly as 1.0186070697786433E-003 / 3.1E-004.

## THE REDUCTION

    vs benchmark      b 0.098916 -> 0.032079    -67.57%
    vs omega_c = 0.06 b 0.081242 -> 0.032079    -60.51%

The second line is the one the paper wants: holding omega_c fixed at the chosen
0.06, adding the two Treatment First switches takes drug use down a further
60.5 per cent. Treatment First sits far BELOW the pure omega_c points rather
than converging toward them.

**CEV: NOT AVAILABLE. `save_welfare_curve` did NOT run.** Verified, not assumed:
`run.err` contains exactly `Terminated` (11 bytes), no `welfare_curve`,
`utility_improvement` or `value_of_life` file exists in the run directory, and
the string "CEV" appears ZERO times in the log. The curve is written only after
the calibration loop exits (line 52324), and a frozen run never exits that loop,
so a hand-stopped run always dies inside it. A CEV requires a further pass with
`frozen_stop_after_blocks` set above zero.

## THE TRANSIENT, AND WHY THE EARLY BLOCKS UNDERSTATED THE DROP

`bequest_residual` fell monotonically across all nine blocks and never turned:

    2.1392  1.8848  1.6869  1.6186  1.5870  1.5428  1.5231  1.5189  1.5173

Last two steps -0.0043 and -0.0015, decelerating. It settled at **1.5173**,
slightly ABOVE the 1.45-1.48 band where the rest of the family rests
(benchmark 1.4771, omega_c = 0.06 at 1.45135, omega_c = 0.07 at 1.4496).

The reduction widened through the run rather than narrowing: -48.35% at block 1,
-62.48% at block 4, -67.57% at block 9. That is the OPPOSITE direction from the
omega_c = 0.07 point, which read -28.06% at block 1 and settled at -18.65%. So
for this arm the early blocks UNDERSTATED the drop. The transient warning was
still correct to apply -- block 4 was a false stop -- but its direction does not
generalise across arms.

## NOT A CORNER

    b       0.032079   about 1/3 of benchmark, not zero, approached from ABOVE
    h_1     0.006114   not zero; above its own 0.004 target
    tau_u   0.302813   treatment take up RISES under the policy, from a 0.245
                       target -- the sobriety condition buys treatment, which is
                       the mechanism the arm is named for
    pi_eu   0.053780   unemployment normal, against a 0.049 target

One moment IS pinned at a bound: `omega_l` (labour supply / total hours) reads
exactly 1.0000000000000000 against a 0.47 target, unchanged to sixteen digits
across all nine blocks. **Pre-existing and not caused by these switches** -- the
omega_c = 1 point reports the identical reading from the same seed, and records
a block-1 diagnostic at omega_c = 0 that also reads exactly 1.0. A broken moment
in this build, worth fixing independently; it does not invalidate this point.

## WHAT THIS RUN MEASURES, PRECISELY

`is_counterfactual` is a compile-time `parameter` fixed at 0 (line 189), and the
branch at line 32257 that takes the voucher from a HOUSED household which fails
the test is guarded on `is_counterfactual==1`. In this build that branch is
unreachable. The conditionality binds through the homeless branch at line 32247,
which is ungated and routes a failing homeless household to category 3, where
`increased_prob_of_voucher_if_homeless_and_addicted = 0` drives its offer
probability to zero. A housed household that fails stays in category 1 and faces
only the false positive rate. The enforcement block at 36670 is gated solely on
`voucher_conditional_on_clean`, so testing and its costs are live throughout,
and `govt_spending_on_drug_tests` is non-zero at every block.

Line 32381 is gated the same way. That is the branch giving a household in
category 3 the transition to drop to no voucher at all:

    if ((is_counterfactual==1) .AND. (voucher_index_1==3) .AND. &
        (increased_prob_of_voucher_if_homeless_and_addicted==0)) then

so on this path a voucher HOLDER is never tested out of the voucher. What the
conditionality reaches is ENTRY: a failing homeless household routes to category
3, whose offer probability is driven to zero, so it never receives one.

So this is the ENTRY-ONLY variant, not the universal Treatment First the paper
states. The number is sound for what it measures and should be labelled that
way.
Setting `is_counterfactual = 1` would require either a source edit or the
separate counterfactual binary from `code/build_cf.sh`, and was ruled out for
this run. Recorded so the number is labelled correctly.
