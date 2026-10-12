# Two-beta calibration: the drug-closure vector at two impatient discount factors

Two points, one vector, `discount_factor_impatient` the only coordinate that moves.
The patient factor is bisected inside the model onto `beta` (wealth over output,
target 3.0); the impatient factor is set externally and aimed at `w_bot` (the bottom
half's share of net worth, target 0.025).

| | line 1 | line 2 |
|---|---|---|
| `discount_factor_impatient` | 0.95 | 0.93 |
| point file | `code/points/point_a4e79fb29e.txt` | `code/points/point_d4997341f9.txt` |
| tag | `a4e79fb29e` | `d4997341f9` |
| MODEL stamp | `c7cb2b24b6` | `597c747ad7` |
| solve time | 14 min on 4 cores | 14 min on 4 cores |

Both printed `HANDOVER OK: 31 of 31 parameters applied` and ended at
`===== END OF MOMENTS =====`.

**The two points carry different MODEL stamps, and this is benign.** `c7cb2b24b6` is
commit `57863ad` ("Fix two more pooling bugs"); `597c747ad7` is commit `82a59ba`
("Check ten invariants on every point"), which landed on the branch between the two
runs. The diff between them adds two print-only subroutines and their call sites and
changes no numerics, so the points remain comparable. The gain is one-sided: line 2
carries invariant output and line 1 does not. See **Provisional** below.

**The line-1 point that was already on the branch was stale and has been replaced.**
It was stamped `MODEL 80a0966e5c` = commit `5292489` ("Switch to two betas as the
default"), which predates the pooling fix in `57863ad` -- the source whose by-age
statistics are the wrong population's. The age profile in section (c) below therefore
differs from the one that file carried.

## (a) The two aimed-at moments, and the bracket

| `discount_factor_impatient` | `w_bot` | `beta` | `b` | `lambda_d` |
|---|---|---|---|---|
| 0.95 | 0.068756 | 2.7508 | 0.30073 | 0.25521 |
| 0.93 | 0.050575 | 2.7223 | 0.36041 | 0.30920 |
| **target** | **0.025** | **3.0 - 4.5** | **0.089** | **0.0368** |

**0.025 does not lie between the two `w_bot` values.** They are 0.050575 at 0.93 and
0.068756 at 0.95; both sit above the target, so the target is not bracketed and no
interpolation is reported here.

Lowering the impatient factor from 0.95 to 0.93 moved `w_bot` down by 0.018181
(41.6 per cent of the way from 0.068756 to the target). **The bracket must extend
downward, to impatient discount factors below 0.93.** Extrapolating the two points
would put the crossing outside their span and is not done here.

`beta` is below the 3.0-4.5 band at both points (2.7508 and 2.7223) even though it is
the coordinate the model bisects, so the internal bisection is not reaching its
target from this vector.

**The one-type drug closure does not transfer.** `b` is 0.30073 and 0.36041 against a
target of 0.089, and `lambda_d` is 0.25521 and 0.30920 against 0.0368 -- between three
and eight times their targets, and moving further away as the impatient factor falls.
The interpolation that closed the drug block at one type does not carry to two.

## (b) Every `MOMENT`, worst first

Per cent gap is `(model - target) / |target| x 100`, ordered by the larger of the two
points' absolute gaps.

| moment | description | 0.95 model | 0.93 model | target | gap 0.95 | gap 0.93 |
|---|---|---|---|---|---|---|
| `cbar` | food stamps / labour income | 0.0527251 | 0.0608765 | 0.0042 | +1155.4% | +1349.4% |
| `lambda_d` | disorder rate | 0.255213 | 0.3092 | 0.0368 | +593.5% | +740.2% |
| `b` | total drug users | 0.300726 | 0.360406 | 0.089 | +237.9% | +305.0% |
| `tau_u` | treatment take up | 0.98502 | 0.987621 | 0.245 | +302.0% | +303.1% |
| `w_bot` | net worth share, bottom half | 0.0687556 | 0.0505745 | 0.025 | +175.0% | +102.3% |
| `theta` | drug spending share | 0.361578 | 0.373092 | 0.162 | +123.2% | +130.3% |
| `y_u` | income of drug users | 1.5725 | 1.63923 | 0.74 | +112.5% | +121.5% |
| `aleph` | value of life / income | 142.392 | 138.403 | 80 | +78.0% | +73.0% |
| `pi_V` | eligibles with a voucher | 0.0962608 | 0.0916696 | 0.266 | -63.8% | -65.5% |
| `h_1` | homelessness rate | 0.00145858 | 0.00145238 | 0.00399 | -63.4% | -63.6% |
| `tau_l` | average labour income tax | 0.0957868 | 0.0891441 | 0.224 | -57.2% | -60.2% |
| `h_3` | share in the largest unit | 0.468948 | 0.425951 | 0.626723 | -25.2% | -32.0% |
| `gamma` | housing over expenditure | 0.186699 | 0.185303 | 0.268 | -30.3% | -30.9% |
| `pi_eu` | unemployment rate | 0.0581696 | 0.0624661 | 0.0485 | +19.9% | +28.8% |
| `h_2` | above half of spending | 0.0744613 | 0.0767117 | 0.101 | -26.3% | -24.0% |
| `kappa_ued` | unemployment given SUD | 0.13265 | 0.13619 | 0.1625 | -18.4% | -16.2% |
| `lambda_m` | SMI share of the homeless | 0.280701 | 0.243369 | 0.25 | +12.3% | -2.7% |
| `mu_H` | recovery housed / homeless | 1.33791 | 1.31526 | 1.47321 | -9.2% | -10.7% |
| `beta` | wealth over output | 2.75077 | 2.72233 | 3 | -8.3% | -9.3% |
| `kappa_uem` | employment given SMI | 0.315312 | 0.310297 | 0.3 | +5.1% | +3.4% |
| `omega_l` | labour supply / total hours | 0.382657 | 0.382087 | 0.4 | -4.3% | -4.5% |
| `sigma_y` | bottom half earnings share | 0.16905 | 0.16905 | 0.172 | -1.7% | -1.7% |
| `p_m` | SMI population share | 0.0506451 | 0.0515433 | 0.050716 / 0.051532 | -0.1% | +0.0% |

**The worst moment excluding `h_3` is `cbar` (food stamps over labour income)**, at
0.0527251 and 0.0608765 against a target of 0.0042 -- roughly twelve to fourteen times the
target, a gap of +1155 and +1349 per cent. `lambda_d` and `tau_u` follow.

`p_m` carries a different target at each point (0.050716 at 0.95, 0.051532 at 0.93); it is
matched almost exactly at both. `MOMENT theta` is 0.36158 and 0.37309 -- neither is the
-1.0 empty-population sentinel, so the drug-spending share is measured on a live
population at both points.

## (c) The age profile

### line 1, `discount_factor_impatient` = 0.95 (`MODEL c7cb2b24b6`)

```
DIAG age  26  homeless=  0.027525  own=  0.00000  renter wealth=    0.00000  renter income=   -0.03590
DIAG age  29  homeless=  0.002745  own=  0.00000  renter wealth=    0.32750  renter income=   -0.02215
DIAG age  32  homeless=  0.001208  own=  0.00000  renter wealth=    0.53498  renter income=   -0.01580
DIAG age  35  homeless=  0.000632  own=  0.00000  renter wealth=    0.67786  renter income=   -0.00695
DIAG age  38  homeless=  0.000375  own=  0.00000  renter wealth=    0.82937  renter income=   -0.00302
DIAG age  41  homeless=  0.000218  own=  0.00000  renter wealth=    0.96330  renter income=    0.00310
DIAG age  44  homeless=  0.000187  own=  0.00000  renter wealth=    1.09562  renter income=    0.00897
DIAG age  47  homeless=  0.000179  own=  0.00000  renter wealth=    1.23475  renter income=    0.01463
DIAG age  50  homeless=  0.000156  own=  0.00000  renter wealth=    1.38015  renter income=    0.01984
DIAG age  53  homeless=  0.000136  own=  0.00000  renter wealth=    1.52733  renter income=    0.02431
DIAG age  56  homeless=  0.000124  own=  0.00000  renter wealth=    1.66531  renter income=    0.02754
DIAG age  59  homeless=  0.000111  own=  0.00000  renter wealth=    1.78476  renter income=    0.02954
DIAG age  62  homeless=  0.000158  own=  0.00000  renter wealth=    1.87894  renter income=    0.02971
DIAG age  65  homeless=  0.000114  own=  0.00000  renter wealth=    1.94632  renter income=    0.02874
DIAG age  68  homeless=  0.000000  own=  0.00000  renter wealth=    1.82678  renter income=    0.55172
DIAG age  71  homeless=  0.000000  own=  0.00000  renter wealth=    1.62657  renter income=    0.57362
DIAG age  74  homeless=  0.000000  own=  0.00000  renter wealth=    1.39843  renter income=    0.60402
DIAG age  77  homeless=  0.000000  own=  0.00000  renter wealth=    1.12020  renter income=    0.64789
DIAG age  80  homeless=  0.000000  own=  0.00000  renter wealth=    0.78542  renter income=    0.71446
DIAG age  83  homeless=  0.000000  own=  0.00000  renter wealth=    0.41098  renter income=    0.83903
```

### line 2, `discount_factor_impatient` = 0.93 (`MODEL 597c747ad7`)

```
DIAG age  26  homeless=  0.027525  own=  0.00000  renter wealth=    0.00000  renter income=   -0.03683
DIAG age  29  homeless=  0.002718  own=  0.00000  renter wealth=    0.29916  renter income=   -0.02314
DIAG age  32  homeless=  0.001256  own=  0.00000  renter wealth=    0.48084  renter income=   -0.01741
DIAG age  35  homeless=  0.000697  own=  0.00000  renter wealth=    0.61344  renter income=   -0.01139
DIAG age  38  homeless=  0.000466  own=  0.00000  renter wealth=    0.76656  renter income=   -0.00494
DIAG age  41  homeless=  0.000333  own=  0.00000  renter wealth=    0.91362  renter income=    0.00113
DIAG age  44  homeless=  0.000205  own=  0.00000  renter wealth=    1.06070  renter income=    0.00705
DIAG age  47  homeless=  0.000170  own=  0.00000  renter wealth=    1.21016  renter income=    0.01300
DIAG age  50  homeless=  0.000148  own=  0.00000  renter wealth=    1.36586  renter income=    0.01860
DIAG age  53  homeless=  0.000127  own=  0.00000  renter wealth=    1.52435  renter income=    0.02359
DIAG age  56  homeless=  0.000113  own=  0.00000  renter wealth=    1.67539  renter income=    0.02737
DIAG age  59  homeless=  0.000130  own=  0.00000  renter wealth=    1.81162  renter income=    0.02956
DIAG age  62  homeless=  0.000187  own=  0.00000  renter wealth=    1.92089  renter income=    0.03061
DIAG age  65  homeless=  0.000102  own=  0.00000  renter wealth=    1.99979  renter income=    0.03006
DIAG age  68  homeless=  0.000000  own=  0.00000  renter wealth=    1.90253  renter income=    0.56891
DIAG age  71  homeless=  0.000000  own=  0.00000  renter wealth=    1.73026  renter income=    0.59633
DIAG age  74  homeless=  0.000000  own=  0.00000  renter wealth=    1.50636  renter income=    0.63228
DIAG age  77  homeless=  0.000000  own=  0.00000  renter wealth=    1.21388  renter income=    0.68149
DIAG age  80  homeless=  0.000000  own=  0.00000  renter wealth=    0.85325  renter income=    0.75446
DIAG age  83  homeless=  0.000000  own=  0.00000  renter wealth=    0.44751  renter income=    0.89109
```

### Which column does homelessness track?

**It tracks renter wealth, inversely: homelessness falls as renter wealth rises.**

The other two columns cannot be what it tracks, and the reasons are different:

- **`own` is 0.00000 at every one of the twenty ages, at both points.** The ownership
  column has no variation at all, so homelessness cannot be tracking it. The model's
  own invariant confirms this is the whole population and not a printing artefact:
  `INVARIANT PASS  homeownership rate = 0.0000000000`. Nobody owns at any age.
- **`renter income` moves the wrong way and then jumps.** It is negative at the young
  ages where homelessness is highest, rises through zero around age 41, and then jumps
  by a factor of about eighteen between ages 65 and 68 (0.02874 to 0.55172 at 0.95). Homelessness
  is already at its floor well before that jump, so the two do not move together.

Renter wealth is the one that lines up. At 0.95 it rises monotonically from 0.00000 at
age 26 to 1.94632 at age 65 while homelessness falls monotonically from 0.027525 to
0.000114 -- a factor of 241 -- over exactly the same ages. Line 2 repeats it: 0.00000
to 1.99979 against 0.027525 down to 0.000102.

Two limits on that reading, both visible in the four columns:

- The correspondence is not exact at the top. Renter wealth peaks at age 65 and falls
  back to 0.41098 by age 83, but homelessness does not rise again as it falls -- it is
  0.000000 from age 68 on. So homelessness tracks renter wealth on the way up and not
  on the way down.
- There is one reversal in each point where both columns still move together: at 0.95,
  homelessness ticks up from 0.000111 at age 59 to 0.000158 at 62 while renter wealth's
  climb flattens; at 0.93 the tick is 0.000113 at 56 to 0.000187 at 62.

Nothing beyond the four columns is claimed here.

## (d) The five homelessness bands

### `share of the homeless, band`

| band | 0.95 model | 0.93 model | observed |
|---|---|---|---|
| 1 | 0.907328 | 0.893768 | 0.260 |
| 2 | 0.053945 | 0.066920 | 0.272 |
| 3 | 0.023038 | 0.022513 | 0.210 |
| 4 | 0.014524 | 0.015831 | 0.184 |
| 5 | 0.001164 | 0.000968 | 0.075 |

The model puts 90.7 and 89.4 per cent of the homeless in band 1 against an observed
26.0 per cent, and bands 2-5 are correspondingly starved: band 5 holds about a tenth
of a per cent against an observed 7.5. Homelessness in this model is concentrated in
the youngest band to a degree the data are not.

### `homelessness rate, band`

| band | 0.95 model | 0.93 model | observed |
|---|---|---|---|
| 1 | 0.011735 | 0.011180 | 0.003161 |
| 2 | 0.000659 | 0.000792 | 0.003378 |
| 3 | 0.000307 | 0.000294 | 0.002912 |
| 4 | 0.000222 | 0.000243 | 0.002496 |
| 5 | 0.000012 | 0.000011 | 0.000770 |

The same picture in levels: band 1's rate is about 3.5 times the observed rate, and
every other band is below observed -- band 5 by a factor of about 63 at 0.95. The
observed profile is close to flat across bands 1-4; the model's falls by a factor of
about 50 across the same range.

The five bands do partition the homeless: `INVARIANT PASS  the five age bands hold all
of the homeless = 1.0000000000` on line 2.

## (e) Every remaining `UNTARGETED` line

Band rows are in (d) and are not repeated.

| statistic | 0.95 model | 0.93 model | observed |
|---|---|---|---|
| mean age of drug users | 41.3979 | 42.3902 | 45.48 |
| users aged 26-34, share | 0.330875 | 0.301562 | 0.28404 |
| users aged 35-44, share | 0.329812 | 0.314318 | 0.25054 |
| users aged 45-54, share | 0.207619 | 0.228333 | 0.17768 |
| users aged 55-64, share | 0.0863335 | 0.106272 | 0.16327 |
| users aged 65 plus, share | 0.0453609 | 0.0495143 | 0.12445 |
| housing over income, renters | 0.128328 | 0.125085 | 0.202 |
| delta_d child SUD ratio | 1.01648 | 1.01456 | 2 |
| wealth share bottom  1 pct | 0 | 0 | -0.00225 |
| wealth share bottom  5 pct | 0 | 0 | -0.00422 |
| wealth share bottom 10 pct | 0 | 0 | -0.00446 |
| income share bottom  1 pct | 0.000553309 | 0.000519272 | 9e-05 |
| income share bottom  5 pct | 0.00276655 | 0.00259636 | 0.00288 |
| income share bottom 10 pct | 0.00553309 | 0.00519272 | 0.00924 |
| delta_h child homelessness ratio | 4.7447 | 5.28266 | 2.1 |
| homelessness profile, band           1 | 4.63892 | 4.44766 | 1.28079 |
| homelessness profile, band           2 | 0.260526 | 0.315123 | 1.36872 |
| homelessness profile, band           3 | 0.121453 | 0.117018 | 1.1799 |
| homelessness profile, band           4 | 0.0875766 | 0.0966681 | 1.01135 |
| homelessness profile, band           5 | 0.00481196 | 0.00419715 | 0.311994 |
| earnings share, bottom tenth | 0.0125067 | 0.0125067 | 0.0099 |
| earnings share, top tenth | 0.308662 | 0.308662 | 0.411 |
| renters above 30 pct of income | 0.353238 | 0.342487 | 0.406 |
| renters above 50 pct of income | 0.339943 | 0.331238 | 0.175 |
| tenant contribution rate | 0.701637 | 0.691518 | 0.312 |
| voucher holders, wages main | 0.4716 | 0.466618 | 0.28 |
| participation, with a SUD | 0.976447 | 0.971543 | 0.658 |
| participation, without a SUD | 0.642404 | 0.630494 | 0.615 |
| homeless at treatment admission | 0.000357108 | 0.00055012 | 0.145 |
| SMI alongside SUD at admission | 0.0195665 | 0.0237786 | 0.431 |
| working, homeless in treatment | 0.0616814 | 0.0416819 | 0.066 |
| SUD share of the homeless | 0.0605574 | 0.113572 | 0.217 |
| drug deaths, share of deaths | 0.829068 | 0.839731 | 0.2 |
| income of the homeless | 0.348951 | 0.313372 | 0.191 |
| employed share of the homeless | 0.810052 | 0.777701 | 0.46 |
| income with a SUD | 1.65589 | 1.70981 | 0.711 |

Three lines in the point files record work that was not done rather than a
measurement, and they are the same at both points:

```
VALIDATION NOT COMPUTED: returns to homelessness within 24 months, and the two drug price elasticities; each needs a second solve.
OMEGA SKIPPED    child counterfactual off by measure_child_gap
ELASTICITY SKIPPED  drug price elasticities off by measure_price_elasticity
```

## Provisional

An equal-beta validation found the two-pass code disagreeing with the one-pass code on
six quantities. Three pooling bugs have since been fixed, but **that validation has not
been re-run**. The following six are therefore provisional, and nothing above should be
relied on for them:

- `tau_l`
- `pi_eu`
- `y_u`
- `tau_u`
- `kappa_ued`
- `aleph`

Stating it plainly: these six are carried here because they were measured, not because
they have been shown correct. The disagreement that put them on this list is still
unresolved as of these two points.

`w_bot` and `beta` are **not** provisional. They agreed to within 1.4 per cent even
before the three pooling fixes, so section (a) does not rest on the unre-run
validation.

### Two invariants fail, and this was not previously on the list

Line 2 ran on `597c747ad7`, which carries the ten invariant checks. Nine of eleven
printed lines pass; two fail:

```
 ===== INVARIANTS =====
 INVARIANT FAIL     income histogram holds the whole distribution  =     1.1933543996   want   1.0000
 INVARIANT FAIL     wealth histogram holds the whole distribution  =     1.1933543996   want   1.0000
 INVARIANT PASS     wealth histogram holds the whole of net worth  =     1.0000000000
 INVARIANT PASS          rental market clears, demand over supply  =     1.0000000000
 INVARIANT PASS                                 homelessness rate  =     0.0014523800
 INVARIANT PASS                                        drug users  =     0.3604056877
 INVARIANT PASS                                     disorder rate  =     0.3092003086
 INVARIANT PASS                              SMI population share  =     0.0515433032
 INVARIANT PASS                                 unemployment rate  =     0.0624661256
 INVARIANT PASS                                homeownership rate  =     0.0000000000
 INVARIANT PASS       the five age bands hold all of the homeless  =     1.0000000000
 INVARIANTS:            2  FAILED -- see the lines above
```

The income and wealth histograms each hold 1.1934 rather than 1.0 -- about 19 per cent
of excess mass. This is the same class of failure, and the same detector, that caught
the first pooling bug when it printed 2.0000. **The three fixes have not closed it.**

This bears directly on section (a). `w_bot` is a share of net worth read off the wealth
histogram, and that histogram is one of the two that fail. The third check --
`wealth histogram holds the whole of net worth = 1.0000000000` -- passes, so the two
are measuring different things and the failure is in the population weights rather than
in the net-worth total. Until that is resolved, the `w_bot` levels in (a), and hence
where the bracket has to extend to, should be treated as provisional too, notwithstanding
the 1.4 per cent agreement noted above, which predates this detector.

Line 1 ran on `c7cb2b24b6`, which does not carry the checks, so there is no invariant
output for it. The failure is structural rather than vector-specific -- the two points
differ in one coordinate -- so it should be assumed to affect line 1 equally, but that
is an inference and not a measurement.

### One more thing worth flagging

The run vector does not set `addiction_scalar_1`, so `run_one_point.sh` wrote the
declared default `0.0224532` into `B_SWEEP_GRID.txt`, replacing a pinned `0.018421517`.
Because the model bisects `addiction_scalar_1` against a gap, that is a starting value
rather than the solved one, which is consistent with the solved value landing near
0.0184. The committed `B_SWEEP_GRID.txt` now differs from what was pinned before these
runs.

