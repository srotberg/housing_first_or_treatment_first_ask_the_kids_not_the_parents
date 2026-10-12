# Two betas, untargeted: one-beta control against beta_impatient 0.95 and 0.90

Three points, identical in every coordinate except the discount-factor block.

| | point file | `number_of_beta_types` | `discount_factor` | `discount_factor_impatient` |
|---|---|---|---|---|
| one-beta control | `code/points/point_d4ffbfdab5.txt` | 1 | 0.99715 | 0.99715 |
| beta_imp 0.95 | `code/points/point_18da9be82d.txt` | 2 | 0.99715 | 0.95 |
| beta_imp 0.90 | `code/points/point_8d54dcdc46.txt` | 2 | 0.99715 | 0.90 |

Both two-beta points reported `HANDOVER OK` and ended with `===== END OF MOMENTS =====`.
Each solved in 27 minutes on 4 cores.

> **Read the tables with two caveats, both established below.** First, the parameter
> vector is a *one-beta* calibration; it was not re-solved for the two-beta economies, so
> the targeted moments in section (b) are badly missed by the two-beta runs and the
> untargeted movements in section (a) are not movements along a re-fitted calibration.
> Second, three internal consistency diagnostics that read 1.0 in the control read well
> above 1.0 in both two-beta runs; see "A consistency check that does not pass" at the end.

## (a) Every `UNTARGETED` line (46 rows)

| Untargeted moment | one-beta control | beta_imp 0.95 | beta_imp 0.90 | observed |
|---|---|---|---|---|
| mean age of drug users | 47.6090 | 43.1753 | 43.6582 | 45.4800 |
| users aged 26-34, share | 0.473168 | 0.293284 | 0.278457 | 0.284040 |
| users aged 35-44, share | 0.103102 | 0.300980 | 0.287789 | 0.250540 |
| users aged 45-54, share | 0.057850 | 0.222175 | 0.232883 | 0.177680 |
| users aged 55-64, share | 0.070592 | 0.119281 | 0.139243 | 0.163270 |
| users aged 65 plus, share | 0.295288 | 0.064280 | 0.061628 | 0.124450 |
| housing over income, renters | 0.254065 | 0.128154 | 0.122524 | 0.202000 |
| delta_d child SUD ratio | 1.2806 | 1.0517 | 1.0131 | 2.0000 |
| wealth share bottom 1 pct | 0 | 0 | 0 | -0.002250 |
| wealth share bottom 5 pct | 0.000439 | 0 | 0 | -0.004220 |
| wealth share bottom 10 pct | 0.003101 | 0 | 0 | -0.004460 |
| income share bottom 1 pct | 0.000680 | 0.000486 | 0.000431 | 9.0000e-05 |
| income share bottom 5 pct | 0.003401 | 0.002432 | 0.002153 | 0.002880 |
| income share bottom 10 pct | 0.008216 | 0.004864 | 0.004306 | 0.009240 |
| delta_h child homelessness ratio | 2.2136 | 3.5865 | 3.8887 | 2.1000 |
| homelessness rate, band 1 | 0.021852 | 0.026819 | 0.023822 | 0.003161 |
| homelessness rate, band 2 | 0.000274 | 0.001248 | 0.001593 | 0.003378 |
| homelessness rate, band 3 | 7.9213e-05 | 0.000530 | 0.000838 | 0.002912 |
| homelessness rate, band 4 | 8.4296e-05 | 0.000575 | 0.000743 | 0.002496 |
| homelessness rate, band 5 | 5.6105e-06 | 4.3396e-05 | 0.000149 | 0.000770 |
| homelessness profile, band 1 | 5.5362 | 4.5078 | 4.1547 | 1.2808 |
| homelessness profile, band 2 | 0.069435 | 0.209763 | 0.277836 | 1.3687 |
| homelessness profile, band 3 | 0.020068 | 0.089148 | 0.146222 | 1.1799 |
| homelessness profile, band 4 | 0.021356 | 0.096716 | 0.129665 | 1.0113 |
| homelessness profile, band 5 | 0.001421 | 0.007294 | 0.026003 | 0.311994 |
| share of the homeless, band 1 | 0.978708 | 0.919951 | 0.882264 | 0.260000 |
| share of the homeless, band 2 | 0.013413 | 0.045156 | 0.062079 | 0.272000 |
| share of the homeless, band 3 | 0.003756 | 0.017357 | 0.029287 | 0.210000 |
| share of the homeless, band 4 | 0.003742 | 0.015921 | 0.021149 | 0.184000 |
| share of the homeless, band 5 | 0.000380 | 0.001614 | 0.005222 | 0.075000 |
| earnings share, bottom tenth | 0.012507 | 0.012507 | 0.012507 | 0.009900 |
| earnings share, top tenth | 0.308662 | 0.308662 | 0.308662 | 0.411000 |
| renters above 30 pct of income | 0.414862 | 0.342145 | 0.339298 | 0.406000 |
| renters above 50 pct of income | 0.257411 | 0.331011 | 0.329396 | 0.175000 |
| tenant contribution rate | 0.470907 | 0.695772 | 0.670805 | 0.312000 |
| voucher holders, wages main | 0.488430 | 0.475749 | 0.468409 | 0.280000 |
| participation, with a SUD | 0.766207 | 0.962481 | 0.954057 | 0.658000 |
| participation, without a SUD | 0.748529 | 0.666601 | 0.742016 | 0.615000 |
| homeless at treatment admission | 0.000161 | 0.000862 | 0.001535 | 0.145000 |
| SMI alongside SUD at admission | 0.018155 | 0.026077 | 0.036790 | 0.431000 |
| working, homeless in treatment | 0.054337 | 0.362338 | 0.350719 | 0.066000 |
| SUD share of the homeless | 0.000782 | 0.062767 | 0.144475 | 0.217000 |
| drug deaths, share of deaths | 0.166995 | 0.836630 | 0.847120 | 0.200000 |
| income of the homeless | 0.274293 | 0.455352 | 0.444680 | 0.191000 |
| employed share of the homeless | 0.975902 | 0.922185 | 0.884625 | 0.460000 |
| income with a SUD | 0.389206 | 1.5588 | 1.7379 | 0.711000 |

## (b) Every `MOMENT` line, with targets (23 rows)

| Targeted moment | one-beta control | beta_imp 0.95 | beta_imp 0.90 | target |
|---|---|---|---|---|
| sigma_y bottom half earnings share | 0.169050 | 0.169050 | 0.169050 | 0.172000 |
| tau_l average labour income tax | 0.238276 | 0.089521 | 0.075942 | 0.224000 |
| omega_l labour supply / total hours | 0.400977 | 0.395375 | 0.393028 | 0.400000 |
| beta wealth over output | 4.0016 | 2.9568 | 2.8330 | 3.0000 |
| h_2 above half of spending | 0.051133 | 0.075226 | 0.080995 | 0.101000 |
| h_3 share in the largest unit | 0.669490 | 0.442971 | 0.376317 | 0.626723 |
| gamma housing over expenditure | 0.186279 | 0.182371 | 0.182142 | 0.268000 |
| h_1 homelessness rate | 0.003947 | 0.008736 | 0.008480 | 0.003990 |
| b total drug users | 0.059824 | 0.761199 | 0.910853 | 0.089000 |
| lambda_d disorder rate | 0.021079 | 0.319008 | 0.401159 | 0.036800 |
| theta drug spending share | 0.163434 | 0.360100 | 0.387783 | 0.162000 |
| aleph value of life / income | 56.7472 | 118.8416 | 112.7629 | 80.0000 |
| pi_eu unemployment rate | 0.055738 | 0.070816 | 0.076253 | 0.048500 |
| kappa_ued unemployment given SUD | 0.135374 | 0.160850 | 0.170504 | 0.162500 |
| kappa_uem employment given SMI | 0.299353 | 0.266046 | 0.250613 | 0.300000 |
| p_m SMI population share | 0.044419 | 0.052114 | 0.052604 | 0.048343 |
| lambda_m SMI share of the homeless | 0.232604 | 0.147054 | 0.153993 | 0.250000 |
| pi_V eligibles with a voucher | 0.269294 | 0.094445 | 0.079586 | 0.266000 |
| cbar food stamps / labour income | 0.011822 | 0.056882 | 0.074764 | 0.004200 |
| tau_u treatment take up | 0.900579 | 0.964813 | 0.973650 | 0.245000 |
| mu_H recovery housed / homeless | 1.2784 | 1.2644 | 1.2952 | 1.4732 |
| w_bot net worth share, bottom half | 0.156302 | 0.071107 | 0.041750 | 0.025000 |
| y_u income of drug users | 0.341084 | 1.4906 | 1.7199 | 0.740000 |

## The three bottom wealth shares

| wealth share | one-beta control | beta_imp 0.95 | beta_imp 0.90 | observed |
|---|---|---|---|---|
| wealth share bottom 1 pct | 0 | 0 | 0 | -0.00225 |
| wealth share bottom 5 pct | 0.000439 | 0 | 0 | -0.00422 |
| wealth share bottom 10 pct | 0.003101 | 0 | 0 | -0.00446 |

**The two-beta runs do not produce negative values.** They produce exactly zero, in all
three shares, at both 0.95 and 0.90. The one-beta control produces zero in the bottom
percentile and small *positive* numbers in the bottom 5 and bottom 10 per cent
(0.000439 and 0.003101). So the second beta moves the bottom 5 and bottom 10 per cent
down onto zero from above, and stops there. Neither economy puts any household in debt.

That is the sharp test stated the other way round, and it fails: a purely patient economy
cannot represent a bottom decile that is in debt, but nor can this impatient one. Zero
rather than a negative number at every impatience level, in all three shares, is the
signature of a borrowing constraint at zero assets rather than of insufficient
impatience -- no household can hold negative wealth whatever its discount factor, so
adding a second beta piles mass onto the constraint instead of pushing it through.
A third beta, or a lower one, would not change this; the asset grid would have to admit
negative positions first.

## The homelessness age profile

| share of the homeless | one-beta control | beta_imp 0.95 | beta_imp 0.90 | observed |
|---|---|---|---|---|
| band 1 | 0.978708 | 0.919951 | 0.882264 | 0.26 |
| band 2 | 0.013413 | 0.045156 | 0.062079 | 0.272 |
| band 3 | 0.003756 | 0.017357 | 0.029287 | 0.21 |
| band 4 | 0.003742 | 0.015921 | 0.021149 | 0.184 |
| band 5 | 0.000380 | 0.001614 | 0.005222 | 0.075 |

The control puts 97.9 per cent of its homeless in band 1. **The second beta does move
weight out of band 1 and into bands 2 through 5, but not much of it**:
band 1 falls to 92.0 per cent at beta_impatient 0.95 and 88.2 per cent at 0.90 --
5.9 and 9.6 percentage points respectively.

By band, the weight that arrives is small in level and large only in ratio:

| band | control | 0.95 | 0.90 | pp gained at 0.95 | pp gained at 0.90 | observed |
|---|---|---|---|---|---|---|
| band 2 | 0.013413 | 0.045156 | 0.062079 | +3.17 | +4.87 | 0.272 |
| band 3 | 0.003756 | 0.017357 | 0.029287 | +1.36 | +2.55 | 0.21 |
| band 4 | 0.003742 | 0.015921 | 0.021149 | +1.22 | +1.74 | 0.184 |
| band 5 | 0.000380 | 0.001614 | 0.005222 | +0.12 | +0.48 | 0.075 |

Bands 3, 4 and 5 together hold 0.79 per cent of the homeless in the control, 3.49 per
cent at 0.95 and 5.57 per cent at 0.90, against 46.9 per cent in the data. The direction
is right and the magnitude is not close: the profile is still a band-1 spike at every
setting, and going from 0.95 to 0.90 buys about as much again as going from one beta to
two did. The observed profile is nearly flat across bands 1 to 4; none of the three
points is.

## (e) What the second beta buys

Comparing the one-beta control with beta_impatient 0.95, coordinate by coordinate:
39 of the 46 untargeted moments move by more than 10 per cent, 3 move by less than
1 per cent, and the remaining 4 fall in between.

**Moved more than 10 per cent (39).** Ranked by size of the move:

| untargeted moment | control | 0.95 | change |
|---|---|---|---|
| SUD share of the homeless | 0.000782 | 0.062767 | +7922% |
| homelessness rate, band 5 | 5.6105e-06 | 4.3396e-05 | +673% |
| homelessness rate, band 4 | 8.4296e-05 | 0.000575 | +583% |
| homelessness rate, band 3 | 7.9213e-05 | 0.000530 | +570% |
| working, homeless in treatment | 0.054337 | 0.362338 | +567% |
| homeless at treatment admission | 0.000161 | 0.000862 | +434% |
| homelessness profile, band 5 | 0.001421 | 0.007294 | +413% |
| drug deaths, share of deaths | 0.166995 | 0.836630 | +401% |
| share of the homeless, band 3 | 0.003756 | 0.017357 | +362% |
| homelessness rate, band 2 | 0.000274 | 0.001248 | +355% |
| homelessness profile, band 4 | 0.021356 | 0.096716 | +353% |
| homelessness profile, band 3 | 0.020068 | 0.089148 | +344% |
| share of the homeless, band 4 | 0.003742 | 0.015921 | +325% |
| share of the homeless, band 5 | 0.000380 | 0.001614 | +324% |
| income with a SUD | 0.389206 | 1.5588 | +301% |
| users aged 45-54, share | 0.057850 | 0.222175 | +284% |
| share of the homeless, band 2 | 0.013413 | 0.045156 | +237% |
| homelessness profile, band 2 | 0.069435 | 0.209763 | +202% |
| users aged 35-44, share | 0.103102 | 0.300980 | +192% |
| wealth share bottom 5 pct | 0.000439 | 0 | -100% |
| wealth share bottom 10 pct | 0.003101 | 0 | -100% |
| users aged 65 plus, share | 0.295288 | 0.064280 | -78% |
| users aged 55-64, share | 0.070592 | 0.119281 | +69% |
| income of the homeless | 0.274293 | 0.455352 | +66% |
| delta_h child homelessness ratio | 2.2136 | 3.5865 | +62% |
| housing over income, renters | 0.254065 | 0.128154 | -50% |
| tenant contribution rate | 0.470907 | 0.695772 | +48% |
| SMI alongside SUD at admission | 0.018155 | 0.026077 | +44% |
| income share bottom 10 pct | 0.008216 | 0.004864 | -41% |
| users aged 26-34, share | 0.473168 | 0.293284 | -38% |
| renters above 50 pct of income | 0.257411 | 0.331011 | +29% |
| income share bottom 5 pct | 0.003401 | 0.002432 | -28% |
| income share bottom 1 pct | 0.000680 | 0.000486 | -28% |
| participation, with a SUD | 0.766207 | 0.962481 | +26% |
| homelessness rate, band 1 | 0.021852 | 0.026819 | +23% |
| homelessness profile, band 1 | 5.5362 | 4.5078 | -19% |
| delta_d child SUD ratio | 1.2806 | 1.0517 | -18% |
| renters above 30 pct of income | 0.414862 | 0.342145 | -18% |
| participation, without a SUD | 0.748529 | 0.666601 | -11% |

**Moved less than 1 per cent (3).** All three are unchanged to every digit printed:

| untargeted moment | control | 0.95 | change |
|---|---|---|---|
| wealth share bottom 1 pct | 0 | 0 | 0% |
| earnings share, bottom tenth | 0.012507 | 0.012507 | 0% |
| earnings share, top tenth | 0.308662 | 0.308662 | 0% |

The four in between are mean age of drug users (-9.3%), share of the homeless in band 1
(-6.0%), employed share of the homeless (-5.5%) and voucher holders with wages as their
main income (-2.6%).

What the numbers show is a split by construction rather than by degree. The two earnings
shares are functions of the exogenous productivity process alone -- `sd_permanent_productivity`
and the age profile -- and no discount factor enters them, so they are identical to sixteen
digits; the bottom percentile of wealth is zero in both economies because the borrowing
constraint binds at zero in both. Every other untargeted moment in the list is a function of
the savings decision, and all 39 of them move by more than a tenth. There is no middle
group of moments that a second beta nudges: the discount factor either does not enter the
moment at all, or it relocates it substantially. The largest relocations are concentrated in
the homelessness and drug blocks -- the five band homelessness rates, the five band
profiles, the four band shares, SUD share of the homeless, drug deaths and treatment
admissions -- which is where a mass of impatient, low-asset households can appear at all.
The distributional tail moments (income shares of the bottom 1, 5 and 10 per cent) move by
28 to 41 per cent, all downward.

## A consistency check that does not pass

Three internal diagnostics that read 1.0 in the one-beta control read well above 1.0 in
both two-beta runs:

| diagnostic | one-beta control | beta_imp 0.95 | beta_imp 0.90 |
|---|---|---|---|
| `income histogram mass / distribution (want 1.0)` | 1.0000000000000839 | 1.1957715703759422 | 1.2685937477297373 |
| `histogram mass / distribution (want 1.0)` | 1.0000000000000908 | 1.1957715703759504 | 1.2685937477297471 |
| `mass with a NEGATIVE value of life` | 0.587313 | 1.956068 | 2.432063 |

The first two are labelled `want 1.0` by the code itself. The third is a mass and cannot
exceed 1 by definition, yet it reads 1.96 and 2.43. All three are at their correct values in
the one-beta control and wrong in both two-beta runs, and they get worse as the second beta
gets further from the first (0.90 is worse than 0.95 in all three). That pattern points at
the aggregation over beta types rather than at the solution of either type's problem: the
histogram appears to sum across types without weighting by type share.

This has to be read before the tables above are used, because the wealth shares, the income
shares, the band shares of the homeless and every other distributional moment are computed
off that histogram. The comparison as requested is reported in full and the numbers are
exactly what the runs produced; whether the two-beta columns of the distributional rows mean
what their labels say is a separate question, and this diagnostic says they may not.

Two further points of context on the tables. `HANDOVER OK` reported 29 of 29 parameters for
the 0.95 run and 31 of 31 for the 0.90 run, from command lines that differ only in the value
of `discount_factor_impatient`. And the targeted moments in section (b) are missed by margins
that make the two-beta points hard to describe as calibrated economies at all: `b total drug
users` is 0.089 in the target and 0.059 in the control, but 0.761 at 0.95 and 0.911 at 0.90,
so three-quarters to nine-tenths of the population holds a drug habit; `lambda_d disorder
rate` is 0.319 and 0.401 against a target of 0.037; `tau_l average labour income tax` falls
from 0.238 to 0.090 and 0.076 against a target of 0.224. The untargeted moments moved, in
other words, in economies whose targeted moments moved at least as far.
