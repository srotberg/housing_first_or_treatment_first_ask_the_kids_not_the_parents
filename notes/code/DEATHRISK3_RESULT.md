# Three death-risk specifications, measured

One parameter vector, three values of `homeless_death_risk_flat_in_age`, nothing
else moved. The question is whether the mortality gradient on the street is what
keeps the model's homeless young: the HUD count puts 26 per cent of the homeless
in the youngest band and the model puts 97 to 98 per cent there, and the age
gradient in the death risk is the one force in the model that punishes an old
household for sleeping rough more than a young one.

| setting | meaning | point file |
| --- | --- | --- |
| 0 | Baggett's age-varying mortality ratios; the status quo | `points/point_beb77d236b.txt` |
| 2 | flat MULTIPLIER of 1.6, quoted from Meyer, Wyse and Logani in the note's external calibration table | `points/point_1c4b7759d4.txt` |
| 1 | flat excess RISK, so the implied multiplier falls with age | `points/point_606feea4bf.txt` |

## (a) Share of the homeless, by age band

This is the point of the exercise.

| band | 0 Baggett | 2 flat multiplier | 1 flat risk | observed |
| --- | --- | --- | --- | --- |
| 1 | 0.978709 | 0.970664 | 0.963890 | 0.260 |
| 2 | 0.013413 | 0.009996 | 0.021147 | 0.272 |
| 3 | 0.003756 | 0.003598 | 0.006676 | 0.210 |
| 4 | 0.003742 | 0.002260 | 0.006624 | 0.184 |
| 5 | 0.000380 | 0.013482 | 0.001662 | 0.075 |
| **2 to 5** | **0.021291** | **0.029336** | **0.036110** | **0.741** |

**Setting 1, the flat excess risk, puts the most weight in bands 2 to 5.** It
carries 0.0361 there against 0.0213 under the status quo and 0.0293 under the
flat multiplier: 1.70 times the status quo, and 1.23 times the flat multiplier.
Ranked, it is 1 then 2 then 0, which is the order the mechanism predicts — the
flat excess risk is the specification whose multiplier falls fastest with age
and so penalises an old homeless household least.

The size of the move is the other half of the answer. The observed mass in bands
2 to 5 is 0.741. The status quo reaches 2.9 per cent of it, the flat multiplier
4.0 per cent, the flat excess risk 4.9 per cent. Band 1 goes from 0.9787 to
0.9639 against an observed 0.260. The gap closed is 1.5 points of a 72-point
gap, so on this margin the three specifications are the same specification.

## (b) Homelessness rate, by age band

| band | 0 Baggett | 2 flat multiplier | 1 flat risk | observed |
| --- | --- | --- | --- | --- |
| 1 | 0.02185239 | 0.03825325 | 0.01420942 | 0.003161 |
| 2 | 0.00027408 | 0.00036064 | 0.00028530 | 0.003378 |
| 3 | 0.00007921 | 0.00013405 | 0.00009298 | 0.002912 |
| 4 | 0.00008429 | 0.00008995 | 0.00009851 | 0.002496 |
| 5 | 0.00000561 | 0.00035156 | 0.00001618 | 0.00077 |

In levels the observed profile is nearly flat across bands 1 to 4 — 0.0032,
0.0034, 0.0029, 0.0025 — and every setting is an order of magnitude high in band
1 and one to two orders low in bands 2 to 5. Band 1 is where the three
specifications actually differ: 0.0383 under the flat multiplier, 0.0219 under
Baggett, 0.0142 under the flat excess risk, a factor of 2.7 from end to end.
Bands 2, 3 and 4 barely move between settings at all (band 2 spans 0.00027 to
0.00036 across all three). The one exception is band 5 under the flat
multiplier, 0.00035 against 0.0000056 under the status quo, a factor of 63 —
which is what produces that setting's 0.0135 share in band 5 and is the single
largest response anywhere in this table.

## (c) MOMENT h_1, the aggregate homelessness rate

| | 0 Baggett | 2 flat multiplier | 1 flat risk | target |
| --- | --- | --- | --- | --- |
| h_1 | 0.00394721 | 0.00697341 | 0.00260616 | 0.00399 |

All three change the level as well as the shape, and they change it in opposite
directions. The status quo sits essentially on target, 0.003947 against 0.00399.
The flat multiplier raises homelessness to 0.006973, 1.77 times the status quo
and 1.75 times target. The flat excess risk cuts it to 0.002606, 0.66 times the
status quo and 0.65 times target. This is not a verdict on either: the level is
`size_homelessness`'s to set and it will be re-calibrated. It is recorded here
so the shape rows above are read knowing which way the level moved under each,
and knowing that the shape comparison in (a) is between distributions, not
counts.

## (d) Are the model's homeless there by choice?

| | 0 Baggett | 2 flat multiplier | 1 flat risk |
| --- | --- | --- | --- |
| homeless by choice, share of the homeless | 0.935795 | 0.956931 | 0.901607 |
| homeless who could afford it on INCOME ALONE | 0.935755 | 0.949720 | 0.901291 |

**No setting reduces this in any material way.** The reference point has both at
0.9358. The flat multiplier moves them the wrong way, up to 0.9569 and 0.9497.
The flat excess risk moves them down, to 0.9016 and 0.9013 — a fall of 3.4 and
3.5 percentage points, the largest reduction of the three, and it still leaves
90 per cent of the model's homeless able to afford rent on income alone and
choosing the street. Whatever the mortality specification, the model's
homelessness is a preference outcome rather than a budget outcome, and none of
these three touches that.

## (e) Every targeted moment

| moment | description | 0 Baggett | 2 flat multiplier | 1 flat risk | target |
| --- | --- | --- | --- | --- | --- |
| sigma_y | bottom half earnings share | 0.16905 | 0.16905 | 0.16905 | 0.172 |
| tau_l | average labour income tax | 0.238276 | 0.238331 | 0.238263 | 0.224 |
| omega_l | labour supply / total hours | 0.400977 | 0.400970 | 0.401093 | 0.4 |
| beta | wealth over output | 4.00162 | 4.00611 | 4.00144 | 3 |
| h_2 | above half of spending | 0.051133 | 0.0513191 | 0.0511314 | 0.101 |
| h_3 | share in the largest unit | 0.66949 | 0.670263 | 0.668397 | 0.626723 |
| gamma | housing over expenditure | 0.186279 | 0.185851 | 0.186365 | 0.268 |
| h_1 | homelessness rate | 0.00394721 | 0.00697341 | 0.00260616 | 0.00399 |
| b | total drug users | 0.0598245 | 0.0607302 | 0.059753 | 0.089 |
| lambda_d | disorder rate | 0.0210789 | 0.0231004 | 0.0210915 | 0.0368 |
| theta | drug spending share | 0.163434 | 0.172743 | 0.163672 | 0.162 |
| aleph | value of life / income | 56.7472 | 56.6977 | 56.6826 | 80 |
| pi_eu | unemployment rate | 0.0557381 | 0.0562344 | 0.0556756 | 0.0485 |
| kappa_ued | unemployment given SUD | 0.135374 | 0.137341 | 0.135386 | 0.1625 |
| kappa_uem | employment given SMI | 0.299354 | 0.298494 | 0.300354 | 0.3 |
| p_m | SMI population share | 0.0444186 | 0.0445207 | 0.0444201 | 0.0483431 |
| lambda_m | SMI share of the homeless | 0.232604 | 0.158321 | 0.223088 | 0.25 |
| pi_V | eligibles with a voucher | 0.269294 | 0.26939 | 0.26931 | 0.266 |
| cbar | food stamps / labour income | 0.0118216 | 0.0117928 | 0.0117588 | 0.0042 |
| tau_u | treatment take up | 0.900579 | 0.91119 | 0.900627 | 0.245 |
| mu_H | recovery housed / homeless | 1.27838 | 1.92298 | 2.08266 | 1.47321 |
| w_bot | net worth share, bottom half | 0.156302 | 0.157311 | 0.156357 | 0.025 |
| y_u | income of drug users | 0.341084 | 0.342068 | 0.341444 | 0.74 |

Outside the homelessness block the three points are nearly the same economy:
sigma_y is identical to five decimals, and tau_l, omega_l, beta, gamma, pi_V,
cbar, w_bot and y_u agree across settings to three or four significant figures.
The moments that do move are the ones the street's death risk reaches. mu_H,
recovery housed over homeless, runs 1.278, 1.923, 2.083 against a target of
1.473 — the widest proportional spread of any targeted moment here, and the only
one where the three settings straddle the target rather than sitting on one side
of it together. lambda_m, the SMI share of the homeless, falls to 0.158 under
the flat multiplier from 0.233 and 0.223 under the other two, against 0.25.
theta and lambda_d move for the flat multiplier alone. No `MOMENT theta` of
-1.0 appears in any of the three, so no band was measured on an empty
population.

## Which build measured which point

The three points do not carry the same `MODEL` stamp, because the branch moved
under them between runs and `run_one_point.sh` rebuilds from whatever source is
in the checkout:

| setting | point | MODEL |
| --- | --- | --- |
| 0 | `point_beb77d236b.txt` | `952f7fbe2e` |
| 2 | `point_1c4b7759d4.txt` | `dc8abdfbce` |
| 1 | `point_606feea4bf.txt` | `c7cb2b24b6` |

Both intervening source commits were read before the next point was run, and
neither changes the solved economy at `number_of_beta_types=1`, which is what
all three lines pass:

- `f893900` flips the *declared default* of `homeless_death_risk_flat_in_age`
  from 1 to 0 and adds a `write` block of by-age diagnostics. All three lines
  hand the setting over explicitly, so the default is overridden in every one of
  them, and a `write` block does not enter the solution.
- `57863ad` and its two predecessors replace `(accumulating_beta_types+1)` with
  `mass_passes` at eleven sites, add one more scaling, remove a duplicate call
  to `calculate_homeownership_by_characteristics`, and flip the declared
  `number_of_beta_types` from 1 to 2. At one beta type `mass_passes` is 1
  everywhere and `(accumulating_beta_types+1)` was also 1 everywhere, the
  removed call was a second pass over a single type that reproduced its own
  input, and the declared type count is overridden by handover. All of it is
  the two-type path.

That reasoning is checkable from the diffs but it is not a measurement. The
clean version of this comparison would re-run all three on one build; doing so
means deleting the two committed point files, because `run_one_point.sh` keys
"already measured" on the parameter vector alone and would otherwise skip them,
and that is the author's call and not one to make in passing.

## What the numbers show

Of the three, the flat excess risk in age reproduces the HUD age profile best,
and the margin is real but small: it holds 0.0361 of the homeless in bands 2 to
5 against 0.0293 for the flat 1.6 multiplier and 0.0213 for Baggett's ratios, so
it moves 1.70 times as much mass off band 1 as the status quo does. Set against
the target the ranking stops mattering. The observed mass in bands 2 to 5 is
0.741 and the best of the three delivers 0.0361, which is 4.9 per cent of it;
band 1 falls from 0.9787 to 0.9639 against an observed 0.260, closing 1.5 points
of a 71.9-point gap, or 2 per cent of it. The spread between the best and worst
of the three specifications, 0.0148 of band-1 share, is a fiftieth of the
distance any of them stands from the data. The level of homelessness responds
far more strongly than its shape does — h_1 spans 0.00261 to 0.00697, a factor
of 2.7, across settings whose band-1 shares span 0.9639 to 0.9787 — so the death
risk from the street is doing most of its work on how many households are
homeless and almost none on which ages they are. On this evidence the choice
among these three mortality specifications is not what determines the model's
age profile of homelessness.
