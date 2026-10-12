# The three upward points on addiction_scalar_1

Measured 1 September 2026 on `MODEL 33160acfdd`
(`33160acfdd4fbb016123f3bceaf958d2`), two beta types, four cores. Twelve to
thirteen minutes each. All three printed a full moments block and all sixteen
invariants PASS.

## The seven points

The three measured here and the four given with the request. **They are not one
curve** and the table is ruled to say so: the four were measured on
`MODEL df02e3db80` and these three on `MODEL 33160acfdd`, and the level moved
enormously between the two. The old model gives b = 0.301 at
`addiction_scalar_1` = 0.0225; the new one gives b = 0.157 at 0.028, which is
*lower on the moment at a higher value of the parameter*. Nothing should be
interpolated across the rule.

| addiction_scalar_1 | b | lambda_d | y_u | theta | w_bot | beta | h_1 | tau_u | aleph | tau_l |
|---|---|---|---|---|---|---|---|---|---|---|
| *on MODEL df02e3db80* |||||||||||
| 0.0178 | 0.50173 | 0.38210 | 0.54561 | -- | -- | -- | -- | -- | -- | -- |
| 0.0180 | 0.48242 | 0.36931 | 0.53108 | -- | -- | -- | -- | -- | -- | -- |
| 0.0182 | 0.38883 | 0.32509 | 1.49692 | -- | -- | -- | -- | -- | -- | -- |
| 0.0224532 | 0.30073 | 0.25521 | 1.57250 | -- | -- | -- | -- | -- | -- | -- |
| *on MODEL 33160acfdd* |||||||||||
| 0.028 | 0.15707094 | 0.14053579 | 0.97270194 | not measured | 0.07405268 | 2.53531220 | 0.00223976 | 0.99969675 | 3.46995532 | 0.23816311 |
| 0.034 | 0.07616054 | 0.06743584 | 0.80523243 | not measured | 0.06203570 | 2.25199420 | 0.00211289 | 0.99998549 | 3.90222199 | 0.24433388 |
| 0.042 | 0.00028910 | 0.00021243 | 0.87021181 | not measured | 0.04591737 | 2.09173275 | 0.00150181 | 0.99998074 | 4.48420600 | 0.24224788 |
| target | 0.089 | 0.0368 | 0.740 | 0.162 | 0.025 | 3.0 (3.0-4.5) | 0.00399 | 0.245 | 80.0 | 0.224 |

`theta` is recorded as not measured, not as a value. All three points print
`MOMENT theta ... model= -1.0000000000000000`, and -1 is the explicit sentinel
`weighted_drug_share_now()` returns when neither the experimenters' nor the
addicts' spending share clears its income floor. It is not a drug spending
share of minus one.

`beta` is below its 3.0 to 4.5 band at all three points and falls as
`addiction_scalar_1` rises: 2.535, 2.252, 2.092.

## 1. Is 0.089 inside the measured range of b?

Yes. b falls from 0.15707094 at `addiction_scalar_1` = 0.028 to 0.07616054 at
0.034, so the target of 0.089 falls between those two adjacent points -- above
the target at 0.028 and below it at 0.034. Interpolating linearly between that
pair alone gives `addiction_scalar_1` = **0.033048**.

## 2. Is 0.0368 inside the measured range of lambda_d?

Yes, but on a different pair. lambda_d is still above target at both 0.028
(0.14053579) and 0.034 (0.06743584), and is below it at 0.042 (0.00021243), so
the target of 0.0368 falls between 0.034 and 0.042. Interpolating between that
pair alone gives `addiction_scalar_1` = **0.037646**.

## 3. Do the two agree?

No. b wants 0.033048 and lambda_d wants 0.037646, a gap of 0.004598, which is
13.9 per cent of the b root. The gap is wider than either bracket is tight, so
it is not a rounding artefact: one parameter cannot hit both moments, and
`lambda_addiction` has to move as well. The direction is legible from the two
roots -- lambda_d needs a larger `addiction_scalar_1` than b does, so at the
value that fixes b the disorder rate is still too high, and `lambda_addiction`
must come down to convert fewer users into the disorder.

The interval between the two roots is also where the model runs out of drug
users altogether: b is 0.00028910 at 0.042, three orders of magnitude below its
target of 0.089. The two roots are close together in the parameter and very far
apart in what the economy looks like on either side.

## 4. Is b monotone in addiction_scalar_1?

Across my three, yes, strictly decreasing: 0.15707094, 0.07616054, 0.00028910.

Across the four given, also yes, strictly decreasing: 0.50173, 0.48242,
0.38883, 0.30073. **The premise that it was not monotone across the first four
does not hold for b** -- those four b values fall at every step, so there is no
turn in b to point to. What is not monotone across the four is `y_u`, which
goes 0.54561, 0.53108, 1.49692, 1.57250: it falls from 0.0178 to 0.0180 and
then nearly triples between 0.0180 and 0.0182. If a turn was wanted, that is
where it is, and it is in `y_u`, not in b.

Laid end to end the seven values of b are monotone decreasing as well, but that
ordering spans the model change and should not be read as one curve.

## The pooled mass and the invariants

**The two histograms now read 1.0.** At all three points
`income histogram holds the whole distribution` and
`wealth histogram holds the whole distribution` are exactly `1.0000000000`,
where the four earlier points read 1.19. Every one of the sixteen invariants
PASSes at every point.

`pooled mass` is the sum of the two types and not a count of the passes:
51.407953 + 44.026822 = 95.434775 at the first point, and the same identity
holds at the other two. The impatient mass rises towards the patient one as
`addiction_scalar_1` rises -- ratio 1.167651, then 1.074613, then 0.999991 --
which is what it should do, since at 0.042 drug use has collapsed to nothing
and the two types have almost nothing left to tell them apart.

### addiction_scalar_1 = 0.028   (point 9659f8b99e)
```
 DIAG mass by beta type:  patient=     51.407953  impatient=     44.026822  patient/impatient=  1.167651
 DIAG pooled mass=   95.434775473775332       one-type equivalent=   51.407953479619820     
MODEL 33160acfdd
 ===== INVARIANTS =====
 INVARIANT PASS     income histogram holds the whole distribution  =     1.0000000000
 INVARIANT PASS     wealth histogram holds the whole distribution  =     1.0000000000
 INVARIANT PASS     wealth histogram holds the whole of net worth  =     1.0000000000
 INVARIANT PASS          rental market clears, demand over supply  =     1.0000000000
 INVARIANT PASS                                 homelessness rate  =     0.0022397598
 INVARIANT PASS                                        drug users  =     0.1570709421
 INVARIANT PASS                                     disorder rate  =     0.1405357870
 INVARIANT PASS                              SMI population share  =     0.0480751602
 INVARIANT PASS                                 unemployment rate  =     0.0714630371
 INVARIANT PASS                                homeownership rate  =     0.0000000000
 INVARIANT PASS         homeless by choice, share of the homeless  =     0.9999854328
 INVARIANT PASS            homeless who could afford it on income  =     0.9999854328
 INVARIANT PASS                    employed share of the homeless  =     0.9693998026
 INVARIANT PASS                         SMI share of the homeless  =     0.2372804587
 INVARIANT PASS                  households receiving food stamps  =     0.0548606712
 INVARIANT PASS       the five age bands hold all of the homeless  =     1.0000000000
 INVARIANTS: all PASS
```

### addiction_scalar_1 = 0.034   (point 5d6df7d597)
```
 DIAG mass by beta type:  patient=     51.411628  impatient=     47.841985  patient/impatient=  1.074613
 DIAG pooled mass=   99.253613041664977       one-type equivalent=   51.411628038966505     
MODEL 33160acfdd
 ===== INVARIANTS =====
 INVARIANT PASS     income histogram holds the whole distribution  =     1.0000000000
 INVARIANT PASS     wealth histogram holds the whole distribution  =     1.0000000000
 INVARIANT PASS     wealth histogram holds the whole of net worth  =     1.0000000000
 INVARIANT PASS          rental market clears, demand over supply  =     1.0000000000
 INVARIANT PASS                                 homelessness rate  =     0.0021128881
 INVARIANT PASS                                        drug users  =     0.0761605446
 INVARIANT PASS                                     disorder rate  =     0.0674358359
 INVARIANT PASS                              SMI population share  =     0.0457906677
 INVARIANT PASS                                 unemployment rate  =     0.0593823961
 INVARIANT PASS                                homeownership rate  =     0.0000000000
 INVARIANT PASS         homeless by choice, share of the homeless  =     1.0000000000
 INVARIANT PASS            homeless who could afford it on income  =     1.0000000000
 INVARIANT PASS                    employed share of the homeless  =     0.9744939528
 INVARIANT PASS                         SMI share of the homeless  =     0.2292653737
 INVARIANT PASS                  households receiving food stamps  =     0.0486828672
 INVARIANT PASS       the five age bands hold all of the homeless  =     1.0000000000
 INVARIANTS: all PASS
```

### addiction_scalar_1 = 0.042   (point e9baea4365)
```
 DIAG mass by beta type:  patient=     51.413201  impatient=     51.413667  patient/impatient=  0.999991
 DIAG pooled mass=   102.82686834460307       one-type equivalent=   51.413201134233617     
MODEL 33160acfdd
 ===== INVARIANTS =====
 INVARIANT PASS     income histogram holds the whole distribution  =     1.0000000000
 INVARIANT PASS     wealth histogram holds the whole distribution  =     1.0000000000
 INVARIANT PASS     wealth histogram holds the whole of net worth  =     1.0000000000
 INVARIANT PASS          rental market clears, demand over supply  =     1.0000000000
 INVARIANT PASS                                 homelessness rate  =     0.0015018118
 INVARIANT PASS                                        drug users  =     0.0002891021
 INVARIANT PASS                                     disorder rate  =     0.0002124260
 INVARIANT PASS                              SMI population share  =     0.0436963725
 INVARIANT PASS                                 unemployment rate  =     0.0477750252
 INVARIANT PASS                                homeownership rate  =     0.0000000000
 INVARIANT PASS         homeless by choice, share of the homeless  =     1.0000000000
 INVARIANT PASS            homeless who could afford it on income  =     1.0000000000
 INVARIANT PASS                    employed share of the homeless  =     0.9639021933
 INVARIANT PASS                         SMI share of the homeless  =     0.2803340701
 INVARIANT PASS                  households receiving food stamps  =     0.0434420603
 INVARIANT PASS       the five age bands hold all of the homeless  =     1.0000000000
 INVARIANTS: all PASS
```

## Two things about the runs themselves

**The handover count is 33, not the 31 the request specified.** Every run
printed `HANDOVER OK: 33 of 33 parameters applied`. The vector gained
`increased_prob_if_homeless` and `rho_d` upstream between the request being
written and the points being measured, and `run_one_point.sh` hands over its
whole default table. All 33 were applied and none was ignored, which is what
the check is for, but the number is not the one asked for and the difference is
the two new names, not a missing pair.

**The first three attempts at point 1 are void and none of their numbers appear
above.** They ran on `8e0688e2d4` and `d08c67c178`, before two bugs were fixed
upstream: the secant's non-convergence warning firing unthrottled from inside
the OpenMP region (`SECANT_WARNING_COST.md`, measured here at a factor of 400
and 7.3 GB of output in 91 minutes), and `grep` reading the model's output
without `-a` and silently discarding all of it. The points above were measured
after both fixes, which is why they take twelve minutes rather than five hours.
