# TREATMENT FIRST, RATIONED VOUCHERS, EVERY HOLDER TESTED, at omega_c = 0.06 -- CONVERGED AT BLOCK 10

Run 2026-09-24 06:35Z to 08:54Z, `sh code/build_tf_rationed.sh` then
`OMP_NUM_THREADS=2 sh code/remote_tf_rationed.sh 0.06`, frozen on the published
two-class omega_c = 0 benchmark seed in `code/scan_seed/`. Run directory
`code/scan_tfu006/`, one container throughout (`uptime -s` 06:32:15 at every
check, no relaunch). gfortran was missing from the fresh container and was
installed before the build; the build then gave 7 warnings and 0 errors on all
three binaries, and the diff against the tracked source was asserted to be
exactly the two `is_counterfactual==1` guard removals.

The switches, as the run log echoes them:

    HANDOVER weight_on_child:   0.0 ->  5.9999999999999998E-002
    HANDOVER voucher_conditional_on_clean:  0 ->  1.0
    HANDOVER increased_prob_of_voucher_if_homeless_and_addicted:  1.0 ->  0.0
    HANDOVER probability_of_detection:  0.95 ->  0.69999999999999996
    HANDOVER probability_of_false_positive:  5.0E-003 ->  0.0
    HANDOVER include_voucher_exclusion:  0 ->  1.0
    HANDOVER frozen_stop_after_blocks:  0 ->  12
    HANDOVER kappa_x:  2.0E-003 ->  0.93289999999999995

`PARAM_HANDOVER.txt` here is the staged copy the script keeps
(`PARAM_HANDOVER.relaunch.txt`), since the binary deletes the original as it
starts.

## IT STOPPED AT BLOCK 10, NOT 12

The model's own block rule fired before `frozen_stop_after_blocks` did:

    ECONOMY IS STILL: the largest relative move across b, lambda_d, h_1 and average labour income is   8.8150587871054528E-004  which is inside   1.0000000000000000E-003 . Leaving the calibration loop so the state that gets saved is a fixed point rather than an iterate.

So the run went into `save_welfare_curve` from block 10, and the "block-12
outcomes" below are block 10's.

## THE BLOCK TABLE

Verbatim from `run.log`. Every block printed exactly one
`BUDGET bequest_residual` (10 in all), so the pairing is 1:1.

| block | b | lambda_d | bequest_residual | block_move | h_1 | y |
|---|---|---|---|---|---|---|
| 1 | 4.9997388817648758E-002 | 2.2870154460074076E-002 | 2.1124426148799453 | 1.0000000000000000 | 7.7534534352370578E-003 | 1.1458170580928495 |
| 2 | 3.6591164967525777E-002 | 1.5638456831054290E-002 | 1.8170569197826931 | 0.31620676815474219 | 6.5824433004405174E-003 | 1.3826745705171177 |
| 3 | 3.3725649867704044E-002 | 1.4325452980965719E-002 | 1.6157669172463465 | 8.6573215110952062E-002 | 6.3925086948822376E-003 | 1.5023771535389394 |
| 4 | 2.3384715934362837E-002 | 1.1426408911169103E-002 | 1.5433723234014980 | 0.30661926379197124 | 6.2165337067206774E-003 | 1.5626944293029938 |
| 5 | 1.8614186520628958E-002 | 9.5030019590465059E-003 | 1.5013568541991613 | 0.20400202538803522 | 6.0408102203538686E-003 | 1.5928370000469303 |
| 6 | 1.6733393149726161E-002 | 7.5109369054430540E-003 | 1.4563997442828340 | 0.20962481773531361 | 5.8422770185723614E-003 | 1.6081924647292170 |
| 7 | 1.5668719360447347E-002 | 6.6862075903829574E-003 | 1.4405194399219750 | 0.10980378685679396 | 5.8014963663348459E-003 | 1.6164225094635969 |
| 8 | 1.5536062200165684E-002 | 6.5853372061479027E-003 | 1.4368792622074080 | 1.5086337489751382E-002 | 5.7762887671409715E-003 | 1.6207423140026331 |
| 9 | 1.5398306040991754E-002 | 6.5259046098807890E-003 | 1.4335895884028109 | 9.0249890638294025E-003 | 5.7885704377895111E-003 | 1.6230943183288207 |
| 10 | 1.5392346254301054E-002 | 6.5201519866032748E-003 | 1.4330485139645757 | 8.8150587871054528E-004 | 5.7873681376682225E-003 | 1.6242980512524074 |

## THE FAMILY STOP RULE DID NOT FIRE

Two consecutive blocks with |b(k)-b(k-1)|/b(k-1) < 0.5 per cent. The b moves:

    block 2  -26.81%    block 6  -10.10%
    block 3   -7.83%    block 7   -6.36%
    block 4  -30.66%    block 8   -0.85%   (1.5536062200165684E-002 vs 1.5668719360447347E-002)
    block 5  -20.40%    block 9   -0.89%   (1.5398306040991754E-002 vs 1.5536062200165684E-002)
                        block 10  -0.04%   (1.5392346254301054E-002 vs 1.5398306040991754E-002)

Block 10 is the first block under 0.5 per cent, and the run left the loop on
that same block, so there was never a second one. The family rule did not fire
at or before block 10.

## BLOCK-10 OUTCOMES, MODEL UNITS

    b                             1.5392346254301054E-002
    lambda_d                      6.5201519866032748E-003
    h_1                           5.7873681376682225E-003   (target 4.0000001899898052E-003)
    tau_u                         0.30338821763056961       (target 0.24500000476837158)
    pi_V                          0.26148088730650149       (target 0.26600000262260437)
    govt_spending_on_drug_tests   1.1099252199887582E-003

The last diagnostics before the exit:

    DIAG voucher-state mass: none=   47.856617004126527       holding=   3.4209659972254340       excluded=   0.0000000000000000
    BUDGET drug_tests=   1.1099252199887582E-003  homeless=   0.0000000000000000       addicts=   0.0000000000000000
    DIAG drug tests, mass tested                     =   3.5804039354476069       of eligibles=   11.560307103433461

## FLAG: THE EXCLUDED VOUCHER STATE IS EMPTY -- NOBODY WAS EVER EXCLUDED

The excluded voucher-state mass was 1.87E-008 at block 1 and exactly
0.0000000000000000 at every block from 2 to 10. Testing ran (mass tested
3.58 of 11.56 eligibles; spending 1.11E-003), but the `BUDGET drug_tests`
line shows `addicts= 0` at every block: no household tested had a disorder, so
with probability_of_false_positive = 0 nobody failed a test and nobody entered
exclusion. The three-year exclusion in the author's specification therefore
never bound in this solution. Whether that is an economic result (no holder is
ever addicted, e.g. onset is ruled out or ends the voucher) or a bug in how
holders reach the test has NOT been checked; this run should not be read as
the arm-3 policy with exclusion binding until it is.

For comparison, the unrationed TF run (`results/counterfactuals/treatment_first/`)
was at b 3.7114706445256114E-002 at block 4, where this run fell 30.7 per cent
to 2.3384715934362837E-002; it settled at roughly half that run's b.

## KAPPA_X PROBE, VERBATIM

     KAPPA_X PROBE: H*beta^K*D_adult=  0.10519001539785146       measured at kappa_x=  0.93289999999999995
     KAPPA_X PROBE: H=   5.7873681376682225E-003  so beta^K*D_adult=   18.175794747391578
     KAPPA_X PROBE: giving up x=   2.0000000000000000E-003  of consumption for life costs   6.8058355265293358E-002  utils
     KAPPA_X PROBE: IMPLIED kappa_x=  0.64700394812075934       against the coded  0.93289999999999995
     KAPPA_X PROBE: giving up x=   8.0000000000000004E-004  of consumption for life costs   2.7200655182923583E-002  utils
     KAPPA_X PROBE: IMPLIED kappa_x=  0.25858590361494677       against the coded  0.93289999999999995

## WELFARE, VERBATIM

Last block's welfare lines, then the curve:

     average_welfare_of_youngest_cohort=   1352.8823788822776
     average_welfare_of_all_cohorts=   1034.0630712247344
     average_welfare_with_childhood=   791.08974658630109
     WELFARE CURVE: loading the benchmark's own policies
     WELFARE CURVE identity check: w(0)=   790.97722703881095       against average_welfare_of_youngest_cohort=   791.08974658630109       relative difference=   1.4223360620672964E-004
     WELFARE CURVE shift applied:  0.11251954749013748       utils, which is   2.8289967919886286E-003  of consumption
     WELFARE CURVE: written, identity check passed

`welfare_curvebaseline_benchmark.dat` (1491 bytes) is committed beside this
file, with the distributions gzipped.

Also in the log at the save:

     STALE CONSTANT: average_labor_income_calibrated=  0.66786175966262817       but the benchmark realises   1.6242980512524074       -- update the declaration.
     STALE CONSTANT: median_income_calibrated=  0.38750472664833069       but the benchmark realises  0.86504588643039804       -- update the declaration.
