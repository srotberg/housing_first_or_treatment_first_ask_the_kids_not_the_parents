# Calibration state — 3 September, 05:00

## The best point

**`8febe659f1`** — worst drug gap **16.19 per cent**, from 70.4 when the engine
restarted at 04:21. `addiction_scalar_1=0.033994`, `lambda_addiction=2.60328`.

    b         0.088746   target 0.089000    -0.29%
    lambda_d  0.030844   target 0.036800   -16.19%

26 points now sit on the current model. The archive was unreadable at the
restart — `next_batch.py` reported 611 of 611 on a different model — and was
recovered by declaring the productivity switch inert for a quantile point in
`model_hash.py`.

## The ranking, current model only

| point | worst | b | lambda_d |
|---|---|---|---|
| 8febe659f1 | 16.19% | -0.29% | -16.19% |
| 886190f18b | 18.86% | +3.38% | -18.86% |
| e1b8b9c8e8 | 26.88% | +26.88% | +16.31% |
| bc56bdbf13 | 35.02% | -7.31% | -35.02% |
| befe0fc5ef | 38.07% | -15.04% | -38.07% |

## What the round has established about the b surface

**Stepping does not work here.** Six Jacobian-fitted steps were solved and all
six landed further from target than the base they were stepped from. Two
interpolations of measured brackets both improved on theirs.

**Most instruments are cliffs or flat:**

- `value_of_life` 42 -> 65.1 takes b to 0.00032, a factor of 430. 42 -> 27.3
  takes it to +360 per cent. A cliff on both sides.
- `relative_share_of_addiction_1` 0.463 -> 0.30095 gives b and lambda_d EXACTLY
  zero; 0.463 -> 0.6 gives +402 and +602 per cent. A cliff on both sides.
- `mu_homeless` moves b by one per cent across its whole range. Flat.
- `utility_cost_of_treatment` moves lambda_d by +5.4 per cent off one base and
  is NON-MONOTONE and flat off another. Its slope does not transfer.

**The one that does transfer:** `probability_becoming_unemployed`. Lowering it
raises both drug moments, with the same sign on two different slices. On
`886190f18b` a single-parameter move put b at +3.4 per cent and h_1 at -2.8,
both inside five, and halved lambda_d's gap.

## In flight

- `batch_cross2.txt` — minimax on the measured straddle b6eef0e3ae ->
  8febe659f1. Predicted worst gap 6.33 per cent.
- `batch_2d.txt` — two moments solved with two measured directions, the straddle
  and pi_eu. Predicted to put both exactly on target. Extrapolates pi_eu to
  0.0203 from a bracket measured over 0.00793 to 0.0122.
- `batch_ucost.txt` — two points on utility_cost_of_treatment. Its prediction is
  no longer believed, since the slope it rests on was shown not to transfer, but
  the points test that directly.

## The open question the gate cannot settle

`pi_eu` owns the unemployment rate. The two-direction solve raises it two thirds
above base to close the drug block, which will move the moment it is the
instrument for. If it does, the drug block and unemployment cannot both be hit
with the instruments in the model, and that is the author's call.

## Not in the calibration, and waiting

The four KKK arms of `batch_kkk0.txt` — the author's own productivity process —
have never produced a valid measurement. Every attempt was lost to the
background-brief failure. `fixed_productivity=1` is the committed default so
none of it touches the running calibration. `code/OPEN_ISSUES.md` has the six
economic findings established in closed form, including that KKK at its
published parameters has a poorest household earning 0.232 of mean productivity
and so cannot generate homelessness at all.
