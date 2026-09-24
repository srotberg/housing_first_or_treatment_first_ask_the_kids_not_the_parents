# omega_c = 1 -- FULL INTERNALISATION OF THE CHILD EXTERNALITY

Run 2026-09-23 23:34Z to 2026-09-24 01:41Z, `sh code/remote_scan_point.sh 1`,
frozen on the published two-class omega_c = 0 benchmark seed. Reference:
b = 0.098916, lambda_d = 0.043579.

This is the upper-bound bookend to the chosen omega_c = 0.06, not a candidate
value. The parent values the child exactly as itself.

## THE BLOCK TABLE

Verbatim from `run.log`. Every block printed b, lambda_d and exactly one
`BUDGET bequest_residual`, so the pairing is 1:1 with no interpolation.
`y` is carried through because it is on the same line.

| block | b | lambda_d | bequest_residual | block_move | h_1 | y |
|---|---|---|---|---|---|---|
| 1 | 1.2130482389251972E-002 | 6.5994823987233150E-003 | 1.9888100874124532 | 1.0000000000000000 | 5.9368960653450832E-003 | 1.1468732371200603 |
| 2 | 2.0278037824807017E-002 | 8.1785916456567527E-003 | 1.6972770404750734 | 0.67165964007944656 | 5.3293713737602479E-003 | 1.3855718128654884 |
| 3 | 2.0935224869149512E-002 | 8.9531159630699964E-003 | 1.5046893900898575 | 9.4701429166543047E-002 | 5.2139132559927909E-003 | 1.5052737867180901 |
| 4 | 2.0230211236871805E-002 | 8.7553503523232368E-003 | 1.4167287353755771 | 4.0245902125614297E-002 | 5.1337259872240764E-003 | 1.5658548882105991 |
| 5 | 1.9752393281677046E-002 | 8.6110530919350104E-003 | 1.3850676706080389 | 2.3619029460447860E-002 | 5.0449360560677189E-003 | 1.5961579018782710 |
| 6 | 2.0048932573882763E-002 | 8.5585209724877154E-003 | 1.3447845782164842 | 1.5012828469793368E-002 | 5.0618966090018288E-003 | 1.6110361677340177 |
| 7 | 2.0162829239923349E-002 | 8.6028825075235467E-003 | 1.3328984522546725 | 5.6809341654905018E-003 | 5.0761523209769521E-003 | 1.6185732519467275 |
| 8 | 2.0180647095899493E-002 | 8.6228466294290158E-003 | 1.3287457198060428 | 2.3423210604096782E-003 | 5.0785413418635399E-003 | 1.6223644701625781 |
| 9 | 2.0193681800784184E-002 | 8.6396190579697343E-003 | 1.3251517352725006 | 2.1823465689163389E-003 | 5.0674582045910242E-003 | 1.6242795766736515 |

## WHY IT STOPPED

**The 0.5 per cent rule fired at block 9.** Not block 12, and not block_move.

    |b(8) - b(7)| / b(7) = |0.020180647 - 0.020162829| / 0.020162829 = 0.0884%
    |b(9) - b(8)| / b(8) = |0.020193682 - 0.020180647| / 0.020180647 = 0.0646%

Two consecutive blocks under 0.5 per cent, so the run was stopped by hand at
block 9 in accordance with the family rule. `block_move` never came near its
own 1e-3 rule -- it was still 2.18e-3 at block 9 -- and was correctly not used.

Last three b, for checking the arithmetic:

    block 7   0.020162829239923349
    block 8   0.020180647095899493
    block 9   0.020193681800784184

## HEADLINE OUTCOMES, MODEL UNITS, BLOCK 9

    b          total drug users     0.020193681800784184
    lambda_d   disorder rate        0.0086396190579697343
    h_1        homelessness rate    0.0050674582045910242
    theta      drug spending share  0.50805043550561035
    tau_u      treatment take up    0.25263599880367471
    y                               1.6242795766736515
    bequest_residual                1.3251517352725006

**CEV: NOT AVAILABLE. `save_welfare_curve` did NOT run.** The process was
terminated at the stop rule during block 10, so it never reached the welfare
curve. This is verified rather than assumed: `run.err` contains exactly
`Terminated`, and no `welfare_curve`, `welfare_code_output`,
`utility_improvement` or `value_of_life` file exists in the run directory. The
string "CEV" appears zero times in the 1.17 MB log. A CEV for this point
requires a further run that is allowed to reach the curve.

## NOT A CORNER

    b          0.020194   ~1/5 of benchmark, not zero, and approached from BELOW
                          (0.01213 blk 1 -> 0.02094 blk 3 -> 0.01975 blk 5 -> 0.02019 blk 9)
    h_1        0.005067   not zero; above its own 0.004 target
    pi_eu      0.053289   unemployment normal, against a 0.049 target

One moment IS pinned at a bound: `omega_l` (labour supply / total hours) reads
exactly 1.0000000000000000 against a 0.47 target, unchanged to sixteen digits
across all nine blocks. **This is pre-existing and not caused by omega_c.** A
block-1 diagnostic at omega_c = 0 from the same seed reads exactly 1.0 as well.
It is a broken moment in this build -- historical records have it at 0.37-0.41
-- and is worth fixing independently, but it does not invalidate this point.

## THE CAVEAT: THE RESIDUAL IS BELOW THE FAMILY BAND AND STILL DRIFTING

Every other settled point in this scan lands at a residual of about 1.45-1.48
(benchmark 1.4771, omega_c = 0.06 at 1.45135, omega_c = 0.07 at 1.4496). This
point settled at **1.3252 -- below that band** -- and fell monotonically across
all nine blocks without once turning:

    1.9888  1.6973  1.5047  1.4167  1.3851  1.3448  1.3329  1.3287  1.3252

Last two steps -0.0042 and -0.0036: decelerating, not flat.

The published `bequest_residual` guidance is one-sided -- it warns about a
residual still well ABOVE 1.48 -- and does not cover this case. Two readings,
and one run cannot separate them:

1. **Genuine.** `weight_on_child = 1` acts directly on the bequest motive, so at
   full internalisation the residual has a real reason to rest somewhere else.
   At omega_c = 0.06-0.07 the residual barely leaves the benchmark because
   omega_c is tiny; that is not evidence about omega_c = 1.
2. **Unconverged.** The residual is still creeping and dragging the wealth
   distribution with it.

Against (2): b itself is firmly settled, the last three blocks differing by
about 1.3e-5, while the residual still moves. b and the residual have decoupled,
which is not what the restart-transient account predicts.

Treat b = 0.020194 as carrying some residual drift. Extending the run to block
12 would cost about 25 minutes and would settle it.

## WHAT IS IN THIS DIRECTORY

    PARAM_HANDOVER.txt                 97 lines, the vector the run was given
    calibration_state.dat              terminal state, v3, written at block 9
    calibration_distribution1.dat.gz   265,496,400 bytes raw
    calibration_distribution2.dat.gz    23,894,676 bytes raw
    calibration_distribution_shape.dat
    newborn_parent_share.dat
    resume_seed.dat
    run.log.gz                         the full 1.17 MB log

Distributions are gzipped because raw `calibration_distribution1.dat` is 265 MB
and GitHub hard-rejects any blob over 100 MB. This mirrors `code/scan_seed/`.

**PARAM_HANDOVER.txt is the INPUT vector, not a solve-produced one.** The point
was frozen (`freeze_all_but_omega_c 1`, `omega_c_is_pinned 1`), so no adjuster
moved and the handover out is the handover in. It differs from
`code/scan_seed/PARAM_HANDOVER_base.txt` by exactly one line:

    94c94
    < weight_on_child 0
    ---
    > weight_on_child 1

The terminal steady state itself is carried by `calibration_state.dat` and the
two distributions, not by the handover. For a T = 60 transition, the handover
pins the parameters and the state plus distributions supply the terminal
equilibrium.

## THE WELFARE PASS WAS CANCELLED BY THE AUTHOR

There is no CEV for this point, by decision rather than by failure: "we dont
need CEV for the omega_c=1 case or homelesnes internalization". The block 9
equilibrium above stands as the result. Two things were learned first.

A RESUME DOES NOT CONTINUE THIS EQUILIBRIUM. A two-block pass resumed from the
converged state re-entered the restart transient instead of staying at the
point: block-1 bequest_residual 1.9942, against this run's own block-1 1.9888
and nothing like the settled 1.3252, and b = 0.019494166, which is -3.46 per
cent -- 346 times the 1e-4 control. Its curve is a different economy's and was
discarded. `frozen_stop_after_blocks` itself works: the loop exited on schedule
and save_welfare_curve ran and wrote.

NOT SETTLED. A fresh rerun's block 1 gave b = 0.012128773 against this run's
0.012130482, a relative difference of 1.409e-04, while bequest_residual differed
by only 1.05e-05. That is a single block, cancelled before more arrived. Whether
it is thread-reduction noise or a real effect is unresolved, and the 1e-4
control should be read as neither validated nor refuted by it.
