# Point `de322e4659` — borrowing off (`include_unsecured_borrowing=0`)

Measured from line 1 of `code/batch_bn_off.txt`, run through
`code/run_one_point.sh`. Raw output: `code/points/point_de322e4659.txt`.
Exit code 0; all invariants report PASS.

## 1. `w_bot` — net worth share of the bottom half

| | value |
|---|---|
| model | `0.0247429` |
| target | `0.0250` |
| absolute gap | `-0.0002571` |
| per-cent gap | **-1.03%** |

`w_bot` is essentially on target. It is the second-tightest of the 23 scored
moments. Taken alone it would say the bottom of the wealth distribution is
right; Section 2 says it is not.

## 2. Bottom-percentile wealth shares — IS ANY NEGATIVE?

**NO. Not one bottom-percentile wealth share is negative. Every one is
strictly positive, and the data values they are meant to match are all
negative.**

| share | model | data | sign |
|---|---|---|---|
| bottom 1 pct | `+1.212822e-04` | `-2.250e-03` | wrong sign |
| bottom 5 pct | `+6.064111e-04` | `-4.220e-03` | wrong sign |
| bottom 10 pct | `+1.212822e-03` | `-4.460e-03` | wrong sign |
| bottom 25 pct (DIAG) | `+3.032055e-03` | — | positive |

A search of the whole point file for a negative `model=` value returns
nothing: there is no negative model moment anywhere in the run.

This is the expected mechanical consequence of the vector, not a surprise:
`include_unsecured_borrowing=0` removes the only channel through which a
household can hold negative net worth, so the asset grid is bounded below at
zero and no percentile of it can integrate to a negative share. With borrowing
off the model cannot reproduce the sign of the bottom tail, whatever the rest
of the vector does.

The three model numbers are also exactly proportional — `5x` and `10x` the
bottom-1-pct value to seven digits. Each percentile in the bottom decile
contributes an identical share, i.e. the whole bottom tenth sits at one common
wealth level (the lowest grid point) rather than being spread. So the bottom
tail is not merely the wrong sign, it is degenerate.

That `w_bot` still lands within 1% of its target while the tail below it is
wrong in sign and degenerate in shape means `w_bot` is not disciplining the
bottom tail here. It is being hit by the composition of the 25th-to-50th
percentile band, and cannot detect the failure Section 2 describes.

## 3. `beta` — wealth over output

| | value |
|---|---|
| model | `2.4532` |
| target | `3.0000` |
| target band | 3.0 – 4.5 |
| per-cent gap vs 3.0 | **-18.23%** |

**Below the band.** `beta = 2.45` falls short of the band's lower edge of 3.0
by 0.547 (-18.2%). It is not inside 3.0–4.5 at any point.

## 4. Every scored moment and its per-cent gap

23 scored (`MOMENT`) lines, in file order.

| moment | description | model | target | gap % |
|---|---|---|---|---|
| `sigma_y` | bottom half earnings share | 0.169050 | 0.172000 | -1.72 |
| `tau_l` | average labour income tax | 0.225766 | 0.224000 | +0.79 |
| `omega_l` | labour supply / total hours | 0.363505 | 0.400000 | -9.12 |
| `beta` | wealth over output | 2.453219 | 3.000000 | -18.23 |
| `h_2` | above half of spending | 0.037185 | 0.101000 | -63.18 |
| `h_3` | share in the largest unit | 0.436068 | 0.626723 | -30.42 |
| `gamma` | housing over expenditure | 0.122696 | 0.268000 | -54.22 |
| `h_1` | homelessness rate | 0.044696 | 0.003990 | +1020.20 |
| `b` | total drug users | 0.407166 | 0.089000 | +357.49 |
| `lambda_d` | disorder rate | 0.293895 | 0.036800 | +698.63 |
| `theta` | drug spending share | 0.305018 | 0.162000 | +88.28 |
| `aleph` | value of life / income | 76.0737 | 80.0000 | -4.91 |
| `pi_eu` | unemployment rate | 0.134271 | 0.049000 | +174.02 |
| `kappa_ued` | unemployment given SUD | 0.244502 | 0.162500 | +50.46 |
| `kappa_uem` | employment given SMI | 0.147743 | 0.300000 | -50.75 |
| `p_m` | SMI population share | 0.050300 | 0.052257 | -3.75 |
| `lambda_m` | SMI share of the homeless | 0.026489 | 0.250000 | -89.40 |
| `pi_V` | eligibles with a voucher | 0.255493 | 0.266000 | -3.95 |
| `cbar` | food stamps / income | 0.003934 | 0.004200 | -6.33 |
| `tau_u` | treatment take up | 0.000000 | 0.245000 | -100.00 |
| `mu_H` | recovery housed / homeless | 1.091779 | 1.473214 | -25.89 |
| `w_bot` | net worth share, bottom half | 0.024743 | 0.025000 | -1.03 |
| `y_u` | income of drug users | 0.838741 | 0.740000 | +13.34 |

Ranked by absolute gap, worst first:

`h_1` +1020.20, `lambda_d` +698.63, `b` +357.49, `pi_eu` +174.02,
`tau_u` -100.00, `lambda_m` -89.40, `theta` +88.28, `h_2` -63.18,
`gamma` -54.22, `kappa_uem` -50.75, `kappa_ued` +50.46, `h_3` -30.42,
`mu_H` -25.89, `beta` -18.23, `y_u` +13.34, `omega_l` -9.12, `cbar` -6.33,
`aleph` -4.91, `pi_V` -3.95, `p_m` -3.75, `sigma_y` -1.72, `w_bot` -1.03,
`tau_l` +0.79.

Notes on the extremes:

- `tau_u` is exactly zero, a -100% gap: nobody takes up treatment. Consistent
  with `money_cost_of_treatment=0` and `utility_cost_of_treatment=1.537`, the
  three treatment-admission untargeted moments are also identically zero.
- `h_1`, `b` and `lambda_d` are each an order of magnitude above target —
  homelessness at 4.47% against 0.399%, drug users at 40.7% against 8.9%,
  disorder at 29.4% against 3.68%. The addiction and homelessness blocks are
  not near their targets at this vector.
- `lambda_m` (SMI share of the homeless) is -89% while `p_m` (SMI population
  share) is within 4%: the SMI population is roughly the right size but almost
  none of it is homeless.
- Only five moments sit inside 5%: `tau_l`, `w_bot`, `sigma_y`, `p_m`, `pi_V`,
  plus `aleph` at -4.91%.

## 5. Homeownership

`INVARIANT PASS homeownership rate = 0.0000000000`. With borrowing off, nobody
owns. The `h_2` and `h_3` housing-rung moments (-63% and -30%) are being read
off a purely renting population.
