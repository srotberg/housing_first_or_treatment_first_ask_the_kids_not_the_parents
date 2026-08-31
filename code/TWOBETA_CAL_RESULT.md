# Two-type calibration: aiming the impatient discount factor at `w_bot`

Three points were solved at one parameter vector, differing in
`discount_factor_impatient` only (0.93, 0.95, 0.97), from `code/TWOBETA_CAL.txt`.
The patient discount factor is bisected inside the model onto `beta`, wealth over
output, against a target of 3.0; the impatient one is set externally and is aimed
at `w_bot`, the bottom half's share of net worth, against a target of 0.025.

| `discount_factor_impatient` | point file | `MODEL` | handover |
| ---: | --- | --- | --- |
| 0.93 | `code/points/point_f5d32f8765.txt` | `c7cb2b24b6` | 31 of 31 |
| 0.95 | `code/points/point_445884ebe4.txt` | `dc8abdfbce` | 31 of 31 |
| 0.97 | `code/points/point_b1c5d0df00.txt` | `a1b808c1dc` | 31 of 31 |

All three printed `HANDOVER OK` and ended with `===== END OF MOMENTS =====`.

## READ THIS FIRST: the three points were measured on three different models

**The `MODEL` hashes above are all different, and none of them is the current
head** (the working tree hashed to `cd64b3a190` when the third point finished).
`MODEL` is the md5 of the Fortran source, so the source moved between every pair
of runs. It moved because the runs were sequenced with a `git pull --rebase`
between them, and a concurrent line of work was landing model fixes on this same
branch throughout -- among them `a636f31` "Fix aleph, cbar, the age-profile mass
and four unguarded trackers", `45848e4` "Fix an unassigned array index, a
probability vector, and the loop that could not exit", `eec57d6` "Make the
income-of-users numerators interest-inclusive", `50e121d` "Give the homelessness
rate a single owner", `1e0c8be` "Revert the aleph and cbar normalisations" and
`84c1ee5` "Fix two undefined reads in the secant and a race in the distribution
sweep".

This is not a hypothetical contamination; three rows show it plainly:

| moment | 0.93 | 0.95 | 0.97 |
| --- | ---: | ---: | ---: |
| `aleph` | 119.17 | 121.71 | **5.0638** |
| `cbar` | 0.060126 | 0.053169 | **0.0024472** |
| `tau_l` | 0.083067 | 0.089797 | **0.241** |

`aleph` falls by a factor of 24 and `cbar` by a factor of 22 between the second
and third point, and `tau_l` triples. No discount factor does that. Those are
`1e0c8be` reverting the aleph and cbar normalisations, and `85c0d8d` fixing
`tau_l`, arriving between the runs. **The 0.97 column is a different model from
the 0.93 and 0.95 columns, and tables (b), (d) and (e) below must be read across
rows, not across columns.**

Two further notes on why this went unnoticed until after the fact. The
already-measured check in `run_one_point.sh` keys the tag on the **parameter
vector alone** and not on `MODEL`, so a point measured on a superseded build is
never re-measured when the model changes -- and re-running these three vectors on
one pinned build is refused as "already measured" without first moving the
committed point files aside. Nothing in the pipeline warns that a sweep has
straddled a source change.

**What this does and does not cost.** Section (a), the point of the exercise, is
the part that survives: `w_bot` and `beta` are both monotone and smooth across
the three points, the target sits far outside the measured range rather than near
its edge, and the conclusion below would need the drift to be worth more than a
factor of two to overturn. Sections (b), (d) and (e) are cross-version and should
be treated as indicative only. A clean re-measurement of all three on one build
is the recommended next step.

## (a) `w_bot` and `beta` against their targets

| `discount_factor_impatient` | `w_bot` | target | `beta` | band |
| ---: | ---: | ---: | ---: | --- |
| 0.93 | 0.054460 | 0.025 | 2.8272 | 3.0 to 4.5 |
| 0.95 | 0.069736 | 0.025 | 2.8642 | 3.0 to 4.5 |
| 0.97 | 0.084344 | 0.025 | 2.9325 | 3.0 to 4.5 |

**The target of 0.025 does NOT lie inside the measured range of `w_bot`**, which
runs from 0.054460 to 0.084344. The target is below the whole of it -- the
closest point, 0.93, still overshoots by a factor of 2.2.

`w_bot` is increasing in the impatient discount factor, monotonically and close
to linearly (0.0153 per 0.02 of beta on the lower leg, 0.0146 on the upper), so
**the bracket must extend DOWNWARD, to impatient discount factors below 0.93.**
Making the impatient type more impatient is what lowers the bottom half's share
of net worth. No interpolated value is quoted, and none is extrapolated: the
measured leg does not reach the target, and the run of `w_bot` below 0.93 is not
established by these three points.

`beta` sits just below the 3.0 to 4.5 band at all three points (2.83 to 2.93,
between 5.8 and 2.2 per cent short of 3.0), and rises with the impatient discount
factor. Note that pushing the impatient factor down to chase `w_bot` will pull
`beta` further below the band, so the internal bisection has to absorb that; the
two aims are not independent along this leg.

## (b) Every targeted moment, all three points

Model value and per cent gap against target. `theta` at 0.97 is the
empty-population sentinel (-1.0), not a value, and carries no gap.

| moment | target | 0.93 | gap % | 0.95 | gap % | 0.97 | gap % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `sigma_y bottom half earnings share` | 0.172 | 0.1691 | -1.7 | 0.1691 | -1.7 | 0.1691 | -1.7 |
| `tau_l average labour income tax` | 0.224 | 0.08307 | -62.9 | 0.0898 | -59.9 | 0.241 | +7.6 |
| `omega_l labour supply / total hours` | 0.4 | 0.3932 | -1.7 | 0.3942 | -1.4 | 0.3926 | -1.8 |
| `beta wealth over output` | 3 | 2.827 | -5.8 | 2.864 | -4.5 | 2.933 | -2.2 |
| `h_2 above half of spending` | 0.101 | 0.07438 | -26.4 | 0.0721 | -28.6 | 0.06646 | -34.2 |
| `h_3 share in the largest unit` | 0.6267 | 0.3934 | -37.2 | 0.4319 | -31.1 | 0.6014 | -4.0 |
| `gamma housing over expenditure` | 0.268 | 0.1805 | -32.6 | 0.1811 | -32.4 | 0.1776 | -33.7 |
| `h_1 homelessness rate` | 0.00399 | 0.004644 | +16.4 | 0.009014 | +125.9 | 0.003812 | -4.5 |
| `b total drug users` | 0.089 | 0.4243 | +376.7 | 0.7688 | +763.8 | 0.3614 | +306.1 |
| `lambda_d disorder rate` | 0.0368 | 0.3652 | +892.3 | 0.3208 | +771.9 | 0.2743 | +645.4 |
| `theta drug spending share` | 0.162 | 0.3762 | +132.2 | 0.3622 | +123.6 | *sentinel* | -- |
| `aleph value of life / income` | 80 | 119.2 | +49.0 | 121.7 | +52.1 | 5.064 | -93.7 |
| `pi_eu unemployment rate` | 0.0485 | 0.06712 | +38.4 | 0.06413 | +32.2 | 0.08686 | +79.1 |
| `kappa_ued unemployment given SUD` | 0.1625 | 0.1491 | -8.3 | 0.1423 | -12.4 | 0.132 | -18.7 |
| `kappa_uem employment given SMI` | 0.3 | 0.2902 | -3.3 | 0.2999 | -0.0 | 0.3079 | +2.6 |
| `p_m SMI population share` | 0.05221 | 0.0527 | +0.9 | 0.05247 | +0.5 | 0.05132 | -1.7 |
| `lambda_m SMI share of the homeless` | 0.25 | 0.1131 | -54.7 | 0.1297 | -48.1 | 0.1217 | -51.3 |
| `pi_V eligibles with a voucher` | 0.266 | 0.08252 | -69.0 | 0.09506 | -64.3 | 0.1123 | -57.8 |
| `cbar food stamps / labour income` | 0.0042 | 0.06013 | +1331.6 | 0.05317 | +1165.9 | 0.002447 | -41.7 |
| `tau_u treatment take up` | 0.245 | 0.9671 | +294.7 | 0.9595 | +291.6 | 0.9559 | +290.2 |
| `mu_H recovery housed / homeless` | 1.473 | 1.278 | -13.3 | 1.27 | -13.8 | 1.281 | -13.1 |
| `w_bot net worth share, bottom half` | 0.025 | 0.05446 | +117.8 | 0.06974 | +178.9 | 0.08434 | +237.4 |
| `y_u income of drug users` | 0.74 | 1.606 | +117.0 | 1.497 | +102.3 | 0.5438 | -26.5 |

Four settings in the parameter vector behind these points look wrong and are
deliberate, per the run's own briefing: `lambda_addiction` near 18,
`addiction_scalar_1` near 0.0184, `probability_becoming_unemployed` near 0.0064
and `kappa_uem` near 28 are all intended values, not errors. They are inputs, so
none of them is a row in the table above -- the `kappa_uem` row there is the
targeted moment of that name, employment given SMI, which sits at 0.30.

## (c) Moments to treat as provisional

The equal-beta validation in `code/VALIDATION_RESULT_2.md` set both discount
factors equal and froze the internal bisection, so the two-type model should have
reproduced the one-type model exactly on every ratio. It did not. Six targeted
moments disagreed by the margins below, and **every one of them is therefore
provisional at all three points here, because all three are two-type runs.**

| moment | one-pass vs two-pass ratio | 0.93 | 0.95 | 0.97 | target |
| --- | ---: | ---: | ---: | ---: | ---: |
| `tau_l` average labour income tax | 0.497 | 0.083067 | 0.089797 | 0.241 | 0.224 |
| `pi_eu` unemployment rate | 0.509 | 0.067116 | 0.064128 | 0.086861 | 0.0485 |
| `y_u` income of drug users | 1.973 | 1.6056 | 1.4973 | 0.54379 | 0.74 |
| `tau_u` treatment take up | 0.090 | 0.96707 | 0.95948 | 0.95592 | 0.245 |
| `kappa_ued` unemployment given SUD | 4.18 | 0.14905 | 0.14227 | 0.13203 | 0.1625 |
| `aleph` value of life / income | 2.82 | 119.17 | 121.71 | 5.0638 | 80 |

None of these six should be read as a measurement of the economy until the
two-pass accumulation is fixed. `tau_u` is the starkest: it sits near 0.96
against a target of 0.245 at all three points, and its validation ratio of 0.090
is the largest disagreement of any targeted moment, so the level itself is not
informative.

**`w_bot` and `beta` are NOT provisional.** In the same validation they agreed to
within 1.4 per cent (`beta` at a ratio of 1.0088, `w_bot` at 1.0136), which is
why the exercise in section (a) rests on them and not on the six above.

## (d) Every untargeted moment, all three points

Model value against the observed value.

| untargeted moment | observed | 0.93 | 0.95 | 0.97 |
| --- | ---: | ---: | ---: | ---: |
| mean age of drug users | 45.48 | 43.45 | 43.3 | 42.5 |
| users aged 26-34, share | 0.284 | 0.2838 | 0.2914 | 0.348 |
| users aged 35-44, share | 0.2505 | 0.2946 | 0.2993 | 0.2941 |
| users aged 45-54, share | 0.1777 | 0.229 | 0.2222 | 0.1869 |
| users aged 55-64, share | 0.1633 | 0.1297 | 0.1203 | 0.08325 |
| users aged 65 plus, share | 0.1245 | 0.06284 | 0.06679 | 0.08773 |
| housing over income, renters | 0.202 | 0.1244 | 0.1271 | 0.2724 |
| delta_d child SUD ratio | 2 | 1.034 | 1.054 | 1.068 |
| wealth share bottom 1 pct | -0.00225 | 0 | 0 | 0 |
| wealth share bottom 5 pct | -0.00422 | 0 | 0 | 0 |
| wealth share bottom 10 pct | -0.00446 | 0 | 0 | 0 |
| income share bottom 1 pct | 9.000e-05 | 4.701e-04 | 4.966e-04 | 5.386e-04 |
| income share bottom 5 pct | 0.00288 | 0.002351 | 0.002483 | 0.002693 |
| income share bottom 10 pct | 0.00924 | 0.004701 | 0.004966 | 0.005386 |
| delta_h child homelessness ratio | 2.1 | 3.765 | 3.722 | 3.268 |
| homelessness rate, band 1 | 0.003161 | 0.0259 | 0.02641 | 0.02539 |
| homelessness rate, band 2 | 0.003378 | 0.001413 | 0.00137 | 8.962e-04 |
| homelessness rate, band 3 | 0.002912 | 5.790e-04 | 5.412e-04 | 3.804e-04 |
| homelessness rate, band 4 | 0.002496 | 6.529e-04 | 6.290e-04 | 4.299e-04 |
| homelessness rate, band 5 | 7.700e-04 | 7.350e-05 | 5.409e-05 | 2.627e-05 |
| homelessness profile, band 1 | 1.281 | 4.334 | 4.451 | 4.73 |
| homelessness profile, band 2 | 1.369 | 0.2364 | 0.2309 | 0.1669 |
| homelessness profile, band 3 | 1.18 | 0.09688 | 0.0912 | 0.07085 |
| homelessness profile, band 4 | 1.011 | 0.1093 | 0.106 | 0.08006 |
| homelessness profile, band 5 | 0.312 | 0.0123 | 0.009115 | 0.004893 |
| share of the homeless, band 1 | 0.26 | 0.9083 | 0.9129 | 0.937 |
| share of the homeless, band 2 | 0.272 | 0.05212 | 0.04988 | 0.03493 |
| share of the homeless, band 3 | 0.21 | 0.01916 | 0.01779 | 0.01355 |
| share of the homeless, band 4 | 0.184 | 0.01783 | 0.01741 | 0.01333 |
| share of the homeless, band 5 | 0.075 | 0.00257 | 0.002001 | 0.001149 |
| earnings share, bottom tenth | 0.0099 | 0.01251 | 0.01251 | 0.01251 |
| earnings share, top tenth | 0.411 | 0.3087 | 0.3087 | 0.3087 |
| renters above 30 pct of income | 0.406 | 0.324 | 0.3309 | 0.8233 |
| renters above 50 pct of income | 0.175 | 0.3144 | 0.32 | 0.5932 |
| tenant contribution rate | 0.312 | 0.6713 | 0.6934 | 0.4124 |
| voucher holders, wages main | 0.28 | 0.4765 | 0.4818 | 0.4882 |
| participation, with a SUD | 0.658 | 0.9586 | 0.9621 | 0.9581 |
| participation, without a SUD | 0.615 | 0.6884 | 0.6692 | 0.7239 |
| homeless at treatment admission | 0.145 | 0.001017 | 9.120e-04 | 4.179e-04 |
| SMI alongside SUD at admission | 0.431 | 0.03293 | 0.02583 | 0.02053 |
| working, homeless in treatment | 0.066 | 0.2999 | 0.3486 | 0.4844 |
| SUD share of the homeless | 0.217 | 0.08072 | 0.06644 | 0.01808 |
| drug deaths, share of deaths | 0.2 | 0.8433 | 0.8362 | 0.7116 |
| income of the homeless | 0.191 | 0.4551 | 0.4503 | 0.3281 |
| employed share of the homeless | 0.46 | 0.9153 | 0.9252 | 0.9766 |
| income with a SUD | 0.711 | 1.645 | 1.568 | 0.6494 |

## (e) Which impatient discount factor fits best

Excluding the six provisional moments of section (c), excluding `h_3`, which is
conceded, and excluding the `theta` sentinel at 0.97, the remaining sixteen
targeted moments give a mean absolute gap of 192 per cent at 0.93, 208 per cent
at 0.95 and 96 per cent at 0.97. **Taken at face value the best overall fit is at
an impatient discount factor of 0.97, where the worst remaining gap is
`lambda_d`, the disorder rate, at +645 per cent (0.2743 against a target of
0.0368).** The next worst there are `b`, total drug users, at +306 per cent and
`w_bot` at +237 per cent.

That ranking should not be trusted as a statement about the discount factor, for
the reason set out at the top of this file. The single largest contributor to
0.97's apparent advantage is `cbar`, which moves from +1332 and +1166 per cent at
0.93 and 0.95 to -42 per cent at 0.97 -- and that is `1e0c8be` reverting the
`cbar` normalisation between the runs, not the discount factor doing work. Strip
`cbar` out and the three points sit much closer together. Between 0.93 and 0.95,
which were measured on nearer builds though still not identical ones, 0.93 is the
slightly better of the two.

The honest summary is that these three points establish section (a) -- the
direction the `w_bot` bracket has to extend -- and do not establish a
best-fitting impatient discount factor. That needs all three re-measured on one
build.
