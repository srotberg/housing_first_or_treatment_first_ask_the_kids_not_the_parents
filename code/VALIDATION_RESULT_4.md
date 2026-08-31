# FAIL — 186 of 240 compared values disagree beyond 4 significant figures (previously 135 of 242)

Re-run of the frozen-beta two-type identity test after the four bug fixes. The
test: with `discount_factor` and `discount_factor_impatient` both 0.99715 AND
`freeze_beta_bisection=1`, the two-type population is two identical copies of
the one-type population, so every reported number must reproduce to machine
precision.

**It does not. The disagreement got worse, not better: 186 values now differ
where 135 differed before.**

## Which code this measures — read this first

Both runs were built from commit **`13f5cc8`** ("Audit G: the driver and
counterfactuals"), the branch head when this validation started. That commit
does contain the tau_l fix the brief points to (`85c0d8d`, "Fix tau_l, the
band-7 print, and a stale comment"), which is why tau_l no longer halves below.

**Seven further source commits landed on this branch while the two runs were
executing**, between 19:57 and 20:34 UTC, ending at `1e0c8be`:

    7bc05ee Stop damp_on_flip resurrecting pinned adjusters
    980f04c Normalise once, on the last pass, at all 187 sites
    a636f31 Fix aleph, cbar, the age-profile mass and four unguarded trackers
    45848e4 Fix an unassigned array index, a probability vector, and the loop that could not exit
    eec57d6 Make the income-of-users numerators interest-inclusive
    50e121d Give the homelessness rate a single owner
    1e0c8be Revert the aleph and cbar normalisations, which the arithmetic contradicts

Those commits touch `aleph`, `cbar`, the homelessness rate, the age-profile
mass and the income-of-users numerators — which are among the quantities
reported as disagreeing below. **The numbers in this file are therefore a
correct measurement of `13f5cc8` and are already out of date with respect to
the branch head.** The test should be re-run against `1e0c8be` before any of
the diagnoses here are acted on. Nothing below has been adjusted to guess at
what those commits changed.

## How this was run

| | |
|---|---|
| Branch | `claude/two-period-addiction-hazard-d7gb61` |
| Commit built and run | `13f5cc8` (branch head has since moved to `1e0c8be`) |
| Source edit | `freeze_beta_bisection=0` -> `1` (line 1369), reverted before commit |
| Run 1 | `number_of_beta_types=1`, point `fdee960558`, model `f0deae7141`, solved in 12 min |
| Run 2 | `number_of_beta_types=2`, point `03ac59f09e`, solved in 21 min |
| Point files | `code/points/point_fdee960558_frozen_beta_v4.txt`, `code/points/point_03ac59f09e_frozen_beta_v4.txt` |

Both runs printed `HANDOVER OK: 31 of 31 parameters applied` and ended with
`===== END OF MOMENTS =====`.

### A note on the denominator

The brief asks for a count out of 242. This binary emits **240** model-produced
values across the `MOMENT`, `DIAG` and `UNTARGETED` lines, counting each numeric
field once and excluding the fixed reference constants (`target=`, `observed=`,
`data=`, `data outpatient=`). Both runs emit the same 165 lines in the same
order, so the comparison is one-to-one and nothing is dropped. The denominator
moved because the fixes changed what the code reports, not because values were
excluded; if the reference constants are counted too the totals are 186 of 253.
The 186 numerator is unaffected by the convention.

## (b) The five diagnostics that read exactly 2.0 before the fixes

**None of them is 1.0. Four are still ~2.0 and one has become dramatically
worse.**

| Diagnostic | one type | two types | ratio | before | now 1.0? |
|---|---|---|---|---|---|
| mass in the top THREE savings grid points | 0.0006273503150 | 0.001250753759 | **1.99371** | 2.0 | **No — still 2.0** |
| mass ON the top savings grid point | 0.0001438727619 | 0.0002870192466 | **1.99495** | 2.0 | **No — still 2.0** |
| mass with a NEGATIVE value of life | 0.5714299038 | 1.156001887 | **2.02300** | 2.0 | **No — still 2.0** |
| working age homeless mass | 0.1995028925 | 0.4117075161 | **2.06367** | 2.0 | **No — still 2.0** |
| average assets of the homeless | 0.02114955964 | 0.1459491192 | **6.90081** | 2.0 | **No — now 6.9, far worse** |

These four ~2.0 ratios are the original double-counting signature, untouched.
A quantity that should be invariant to replicating the population is still
being summed over both types instead of averaged. `average assets of the
homeless` has moved off 2.0 in the wrong direction.

## (c) MOMENT tau_l — the single most important number

| | value |
|---|---|
| one type | 0.23761995071811023 |
| two types | 0.23720507720319453 |
| **ratio** | **0.998254** |
| previous ratio | 0.497 |

**tau_l no longer halves — the duplicate `govt_revenues_calc` call was the cause
of that and removing it worked. But tau_l still does not agree.** The ratio is
0.998254, not 1.0: the two runs part company in the fourth significant figure
(0.2376 against 0.2372), which is a 0.17% gap, roughly 35 times the 4-s.f.
tolerance. The gross factor-of-two error is fixed; a real residual difference
remains, and under this test tau_l must reproduce exactly.

## (d) The five moments quoted in the brief

| MOMENT | one type | two types | ratio | previous ratio | verdict |
|---|---|---|---|---|---|
| `pi_eu` unemployment rate | 0.05298364577 | 0.02698978747 | 0.509398 | 0.509 | unchanged — still halved |
| `y_u` income of drug users | 0.1701815151 | 0.3035585486 | 1.78373 | 1.973 | moved, still wrong |
| `tau_u` treatment take up | 0.08381990622 | 0.1319017425 | 1.57363 | 0.090 | moved a long way, still wrong |
| `kappa_ued` unemployment given SUD | 0.1028213285 | 0.4293716926 | 4.17590 | 4.18 | unchanged |
| `aleph` value of life / income | 57.51182662 | 162.0018834 | 2.81684 | 2.82 | unchanged |

`pi_eu`, `kappa_ued` and `aleph` are bit-for-bit where they were before the
fixes. Whatever the four fixes addressed, it did not touch these paths.
`tau_u` moved from 0.090 to 1.574 and `y_u` from 1.973 to 1.784 — movement, but
not toward 1.0.

## (f) INVARIANT lines

**Run 1 (one type) — all 11 PASS:**

     INVARIANT PASS     income histogram holds the whole distribution  =     1.0000000000
     INVARIANT PASS     wealth histogram holds the whole distribution  =     1.0000000000
     INVARIANT PASS     wealth histogram holds the whole of net worth  =     1.0000000000
     INVARIANT PASS          rental market clears, demand over supply  =     1.0000000000
     INVARIANT PASS                                 homelessness rate  =     0.0039142594
     INVARIANT PASS                                        drug users  =     0.0246234999
     INVARIANT PASS                                     disorder rate  =     0.0071491275
     INVARIANT PASS                              SMI population share  =     0.0439839890
     INVARIANT PASS                                 unemployment rate  =     0.0529836458
     INVARIANT PASS                                homeownership rate  =     0.0000000000
     INVARIANT PASS       the five age bands hold all of the homeless  =     1.0000000000
     INVARIANTS: all PASS

**Run 2 (two types) — 2 FAIL:**

     INVARIANT FAIL     income histogram holds the whole distribution  =     1.0000203670   want   1.0000
     INVARIANT FAIL     wealth histogram holds the whole distribution  =     1.0000203670   want   1.0000
     INVARIANT PASS     wealth histogram holds the whole of net worth  =     1.0000000000
     INVARIANT PASS          rental market clears, demand over supply  =     1.0000000000
     INVARIANT PASS                                 homelessness rate  =     0.0021026088
     INVARIANT PASS                                        drug users  =     0.0141245554
     INVARIANT PASS                                     disorder rate  =     0.0028915262
     INVARIANT PASS                              SMI population share  =     0.0439884114
     INVARIANT PASS                                 unemployment rate  =     0.0269897875
     INVARIANT PASS                                homeownership rate  =     0.0000000000
     INVARIANT PASS       the five age bands hold all of the homeless  =     1.0000000000
     INVARIANTS:            2  FAILED -- see the lines above

The two failures, verbatim:

    INVARIANT FAIL     income histogram holds the whole distribution  =     1.0000203670   want   1.0000
    INVARIANT FAIL     wealth histogram holds the whole distribution  =     1.0000203670   want   1.0000

Both overshoot by the identical 2.0367e-05, so one shared mass accumulator is
double-adding a sliver of the second type. The invariants are doing their job:
they catch in the two-type run exactly the class of bug this test is looking
for, and they are clean in the one-type run.

Note the brief expected ten invariants; the binary emits eleven.

## (e) Every line still outside 4 significant figures

All 186 disagreeing values, with the two-type value over the one-type value.

| kind | line | field | one type | two types | ratio |
|---|---|---|---|---|---|
| `MOMENT` | MOMENT tau_l average labour income tax model |  | 0.2376199507 | 0.2372050772 | 0.998254 |
| `MOMENT` | MOMENT omega_l labour supply / total hours model |  | 0.4011421038 | 0.4026777912 | 1.00383 |
| `MOMENT` | MOMENT beta wealth over output model |  | 4.012148379 | 4.047583529 | 1.00883 |
| `MOMENT` | MOMENT h_2 above half of spending model |  | 0.04940572528 | 0.05241620163 | 1.06093 |
| `MOMENT` | MOMENT h_3 share in the largest unit model |  | 0.6702233036 | 0.6758846737 | 1.00845 |
| `DIAG` | DIAG unit 0 share of renters |  | 0.1206637175 | 0.1185402451 | 0.982402 |
| `DIAG` | DIAG unit 1 share of renters |  | 0.2091129789 | 0.2083504583 | 0.996354 |
| `DIAG` | DIAG unit 2 share of renters |  | 0.6702233036 | 0.6731092966 | 1.00431 |
| `DIAG` | DIAG unit 2 share of renters | field 2 | 0.3812034669 | 0.4085963372 | 1.07186 |
| `DIAG` | DIAG aggregate rent / aggregate income |  | 0.2074195944 | 0.2082764221 | 1.00413 |
| `DIAG` | DIAG aggregate housing / aggregate expenditure |  | 0.1866914791 | 0.1916184714 | 1.02639 |
| `DIAG` | DIAG over half of EXPENDITURE, all households |  | 0.04940572528 | 0.05241620163 | 1.06093 |
| `DIAG` | DIAG over half of EXPENDITURE, housed only |  | 0.04959987205 | 0.05262876595 | 1.06107 |
| `UNTARGETED` | UNTARGETED mean age of drug users model |  | 68.42873157 | 66.99048353 | 0.978982 |
| `UNTARGETED` | UNTARGETED users aged 26-34, share model |  | 0.07282732545 | 0.1201554492 | 1.64987 |
| `UNTARGETED` | UNTARGETED users aged 35-44, share model |  | 0.04181992608 | 0.0238725981 | 0.570843 |
| `UNTARGETED` | UNTARGETED users aged 45-54, share model |  | 0.04905685342 | 0.0452199853 | 0.921787 |
| `UNTARGETED` | UNTARGETED users aged 55-64, share model |  | 0.1362091445 | 0.129203319 | 0.948566 |
| `UNTARGETED` | UNTARGETED users aged 65 plus, share model |  | 0.7000867505 | 0.6815486484 | 0.97352 |
| `DIAG` | DIAG income of WORKING AGE drug users / average |  | 0.1633099164 | 0.3277082336 | 2.00666 |
| `DIAG` | DIAG working age share of drug users |  | 0.3136023951 | 0.3312152458 | 1.05616 |
| `DIAG` | DIAG users band 1 use rate |  | 0.01020895587 | 0.01791711805 | 1.75504 |
| `DIAG` | DIAG users band 1 use rate | field 2 | 0.2798909502 | 0.09798360517 | 0.350078 |
| `DIAG` | DIAG users band 1 use rate | field 3 | 0.1881006785 | 0.4691304329 | 2.49404 |
| `DIAG` | DIAG users band 2 use rate |  | 0.005350249663 | 0.003248329032 | 0.607136 |
| `DIAG` | DIAG users band 2 use rate | field 2 | 0.9396400285 | 0.8722583896 | 0.92829 |
| `DIAG` | DIAG users band 2 use rate | field 3 | 0.2863734656 | 0.4870281229 | 1.70067 |
| `DIAG` | DIAG users band 3 use rate |  | 0.006457736903 | 0.006329070472 | 0.980076 |
| `DIAG` | DIAG users band 3 use rate | field 2 | 0.4835181208 | 0.2802974972 | 0.579704 |
| `DIAG` | DIAG users band 3 use rate | field 3 | 0.1838385276 | 0.2522234973 | 1.37198 |
| `DIAG` | DIAG users band 4 use rate |  | 0.01908656929 | 0.01924798381 | 1.00846 |
| `DIAG` | DIAG users band 4 use rate | field 2 | 0.08395186933 | 0.05899610087 | 0.702737 |
| `DIAG` | DIAG users band 4 use rate | field 3 | 0.1110278884 | 0.2056600503 | 1.85233 |
| `DIAG` | DIAG users band 5 use rate |  | 0.06406059483 | 0.06640868408 | 1.03665 |
| `DIAG` | DIAG users band 5 use rate | field 2 | 0.2792558334 | 0.2806475668 | 1.00498 |
| `DIAG` | DIAG users band 5 use rate | field 3 | 0.1719286576 | 0.3368978615 | 1.95952 |
| `DIAG` | DIAG buyers: mean C |  | 0.1333450322 | 0.1316519156 | 0.987303 |
| `DIAG` | DIAG non-buyers: mean C |  | 0.3967882672 | 0.3953833359 | 0.996459 |
| `DIAG` | DIAG buyers: mean income |  | 0.08485117521 | 0.09064085955 | 1.06823 |
| `DIAG` | DIAG non-buyers: mean income |  | 0.5084960444 | 0.5075818165 | 0.998202 |
| `DIAG` | DIAG buyers as a share of clean households |  | 0.01760019848 | 0.01992620186 | 1.13216 |
| `DIAG` | DIAG assets of drug users / average net worth |  | 0.2079007357 | 0.1775194878 | 0.853867 |
| `DIAG` | DIAG assets of experimenters / average net worth |  | 0.2190489182 | 0.3971311329 | 1.81298 |
| `DIAG` | DIAG assets with a SUD / average net worth |  | 0.1806516076 | 0.7488324901 | 4.14517 |
| `DIAG` | DIAG mass with a NEGATIVE value of life |  | 0.5714299038 | 1.156001887 | 2.023 |
| `DIAG` | DIAG value of life, drug users |  | 16.8974117 | 16.00089282 | 0.946943 |
| `DIAG` | DIAG value of life, everyone else |  | 18.68946365 | 18.64645222 | 0.997699 |
| `DIAG` | DIAG treatment price / average labour income |  | 0.1006946495 | 0.1431319195 | 1.42145 |
| `DIAG` | DIAG households receiving food stamps |  | 1.546147649 | 3.091088713 | 1.99922 |
| `DIAG` | DIAG aggregate rent / output |  | 0.2406935149 | 0.2419896657 | 1.00539 |
| `DIAG` | DIAG share in the smallest unit |  | 0.1206637175 | 0.1164981912 | 0.965478 |
| `MOMENT` | MOMENT gamma housing over expenditure model |  | 0.1866914791 | 0.1916184714 | 1.02639 |
| `UNTARGETED` | UNTARGETED housing over income, renters model |  | 0.2523736032 | 0.1307276927 | 0.517993 |
| `MOMENT` | MOMENT h_1 homelessness rate model |  | 0.003914259411 | 0.002102608798 | 0.537166 |
| `MOMENT` | MOMENT b total drug users model |  | 0.02462349991 | 0.01412455541 | 0.573621 |
| `MOMENT` | MOMENT lambda_d disorder rate model |  | 0.007149127491 | 0.002891526217 | 0.404459 |
| `MOMENT` | MOMENT theta drug spending share model |  | 0.2570815718 | 2.706836648 | 10.5291 |
| `MOMENT` | MOMENT aleph value of life / income model |  | 57.51182662 | 162.0018834 | 2.81684 |
| `MOMENT` | MOMENT pi_eu unemployment rate model |  | 0.05298364577 | 0.02698978747 | 0.509398 |
| `MOMENT` | MOMENT kappa_ued unemployment given SUD model |  | 0.1028213285 | 0.4293716926 | 4.1759 |
| `MOMENT` | MOMENT kappa_uem employment given SMI model |  | 0.3018190953 | 0.3024128827 | 1.00197 |
| `MOMENT` | MOMENT lambda_m SMI share of the homeless model |  | 0.2331997727 | 0.1906958823 | 0.817736 |
| `MOMENT` | MOMENT pi_V eligibles with a voucher model |  | 0.289923111 | 0.1036104882 | 0.357372 |
| `MOMENT` | MOMENT cbar food stamps / labour income model |  | 0.01120513728 | 0.03162957514 | 2.82277 |
| `MOMENT` | MOMENT tau_u treatment take up model |  | 0.08381990622 | 0.1319017425 | 1.57363 |
| `MOMENT` | MOMENT mu_H recovery housed / homeless model |  | 1.405873632 | 0.0001782013162 | 0.000126755 |
| `UNTARGETED` | UNTARGETED delta_d child SUD ratio model |  | 1.962789342 | 3.758936455 | 1.9151 |
| `UNTARGETED` | UNTARGETED wealth share bottom 5 pct model |  | 0.0003358042181 | 0.0003873563376 | 1.15352 |
| `UNTARGETED` | UNTARGETED wealth share bottom 10 pct model |  | 0.002996247178 | 0.003033824728 | 1.01254 |
| `UNTARGETED` | UNTARGETED income share bottom 1 pct model |  | 0.0006904082791 | 0.0006944274755 | 1.00582 |
| `UNTARGETED` | UNTARGETED income share bottom 5 pct model |  | 0.003452041396 | 0.003472137378 | 1.00582 |
| `UNTARGETED` | UNTARGETED income share bottom 10 pct model |  | 0.008680990496 | 0.008607053003 | 0.991483 |
| `DIAG` | DIAG SUD rate, income band 1 model |  | 0.02162877687 | 0.02237252345 | 1.03439 |
| `DIAG` | DIAG SUD rate, income band 2 model |  | 0.01598192422 | 0.01113792939 | 0.696908 |
| `DIAG` | DIAG SUD rate, income band 3 model |  | 0.002402138174 | 0.001555804959 | 0.647675 |
| `DIAG` | DIAG SUD rate, income band 4 model |  | 0.001893112159 | 0.0009878736242 | 0.521825 |
| `DIAG` | DIAG SUD rate, income band 5 model |  | 0.000181562803 | 0.0001015692291 | 0.559417 |
| `DIAG` | DIAG SUD rate, income band 6 model |  | 2.556361667e-08 | 1.340093669e-08 | 0.524219 |
| `UNTARGETED` | UNTARGETED delta_h child homelessness ratio model |  | 2.217882246 | 3.626892575 | 1.6353 |
| `DIAG` | DIAG homelessness rate rebuilt from the bands |  | 0.003914259411 | 0.004038937935 | 1.03185 |
| `UNTARGETED` | UNTARGETED homelessness rate, band 1 model |  | 0.02180529669 | 0.02249791786 | 1.03176 |
| `UNTARGETED` | UNTARGETED homelessness rate, band 2 model |  | 0.0002760650897 | 0.0002878505603 | 1.04269 |
| `UNTARGETED` | UNTARGETED homelessness rate, band 3 model |  | 7.70705138e-05 | 8.007454164e-05 | 1.03898 |
| `UNTARGETED` | UNTARGETED homelessness rate, band 4 model |  | 8.513245623e-05 | 8.484267351e-05 | 0.996596 |
| `UNTARGETED` | UNTARGETED homelessness rate, band 5 model |  | 5.647932529e-06 | 5.555893666e-06 | 0.983704 |
| `UNTARGETED` | UNTARGETED homelessness profile, band 2 model |  | 0.07052805159 | 0.07126887439 | 1.0105 |
| `UNTARGETED` | UNTARGETED homelessness profile, band 3 model |  | 0.01968967963 | 0.01982564301 | 1.00691 |
| `UNTARGETED` | UNTARGETED homelessness profile, band 4 model |  | 0.0217493138 | 0.02100618402 | 0.965832 |
| `UNTARGETED` | UNTARGETED homelessness profile, band 5 model |  | 0.001442912167 | 0.001375582828 | 0.953338 |
| `DIAG` | DIAG disorder rate, band 1 |  | 0.00285739436 | 0.001755583821 | 0.6144 |
| `DIAG` | DIAG disorder rate, band 2 |  | 0.005027308746 | 0.002833382251 | 0.563598 |
| `DIAG` | DIAG disorder rate, band 3 |  | 0.003122432812 | 0.001774022613 | 0.568154 |
| `DIAG` | DIAG disorder rate, band 4 |  | 0.001602353171 | 0.001135555995 | 0.70868 |
| `DIAG` | DIAG disorder rate, band 5 |  | 0.0178892948 | 0.0186374356 | 1.04182 |
| `DIAG` | DIAG SUD share of the homeless, band 1 |  | 0.0002177378809 | 0.0001087205482 | 0.499318 |
| `DIAG` | DIAG SUD share of the homeless, band 2 |  | 0.006362889921 | 0.003184066379 | 0.500412 |
| `DIAG` | DIAG SUD share of the homeless, band 3 |  | 0.0007036457605 | 0.0006745297638 | 0.958621 |
| `DIAG` | DIAG SUD share of the homeless, band 4 |  | 0.001492500497 | 0.001527113648 | 1.02319 |
| `DIAG` | DIAG SUD share of the homeless, band 5 |  | 0.0003312613156 | 0.0003580025271 | 1.08073 |
| `UNTARGETED` | UNTARGETED share of the homeless, band 2 model |  | 0.01357440745 | 0.01371995462 | 1.01072 |
| `UNTARGETED` | UNTARGETED share of the homeless, band 3 model |  | 0.003683051345 | 0.003710486618 | 1.00745 |
| `UNTARGETED` | UNTARGETED share of the homeless, band 4 model |  | 0.003821850844 | 0.003693590066 | 0.96644 |
| `UNTARGETED` | UNTARGETED share of the homeless, band 5 model |  | 0.0003882849606 | 0.0003698041959 | 0.952404 |
| `MOMENT` | MOMENT w_bot net worth share, bottom half model |  | 0.1571599252 | 0.1592922617 | 1.01357 |
| `UNTARGETED` | UNTARGETED renters above 30 pct of income model |  | 0.4174391993 | 0.433795848 | 1.03918 |
| `UNTARGETED` | UNTARGETED renters above 50 pct of income model |  | 0.2554914469 | 0.2996080326 | 1.17267 |
| `UNTARGETED` | UNTARGETED tenant contribution rate model |  | 0.4696274256 | 0.7397875482 | 1.57526 |
| `UNTARGETED` | UNTARGETED voucher holders, wages main model |  | 0.4898470023 | 0.4777012318 | 0.975205 |
| `UNTARGETED` | UNTARGETED participation, with a SUD model |  | 0.3292863973 | 0.2195288575 | 0.666681 |
| `UNTARGETED` | UNTARGETED participation, without a SUD model |  | 0.7505383944 | 0.7511929499 | 1.00087 |
| `DIAG` | DIAG households with no wage income, working age |  | 0.05298364577 | 0.05277769909 | 0.996113 |
| `UNTARGETED` | UNTARGETED SMI alongside SUD at admission model |  | 0.008849170681 | 0.008561060692 | 0.967442 |
| `DIAG` | DIAG employed share of the homeless, working age |  | 0.9769542087 | 0.9311410554 | 0.953106 |
| `DIAG` | DIAG working age homeless mass |  | 0.1995028925 | 0.4117075161 | 2.06367 |
| `UNTARGETED` | UNTARGETED SUD share of the homeless model |  | 0.0003078603343 | 0.001441875879 | 4.68354 |
| `UNTARGETED` | UNTARGETED drug deaths, share of deaths model |  | 0.0261987161 | 0.01526921472 | 0.582823 |
| `UNTARGETED` | UNTARGETED income of the homeless model |  | 0.2743319781 | 3.092731856 | 11.2737 |
| `UNTARGETED` | UNTARGETED employed share of the homeless model |  | 0.9769542087 | 0.9311410554 | 0.953106 |
| `DIAG` | DIAG homeless who could afford it on INCOME ALONE |  | 0.9356896519 | 5.33388581 | 5.70049 |
| `DIAG` | DIAG homeless by choice, share of the homeless |  | 0.9357263219 | 5.33409811 | 5.70049 |
| `DIAG` | DIAG homeless receiving food stamps |  | 9.778476139e-05 | 0.0005593063335 | 5.71977 |
| `DIAG` | DIAG average assets of the homeless |  | 0.02114955964 | 0.1459491192 | 6.90081 |
| `DIAG` | DIAG wealth share of the bottom 25 pct |  | 0.03153349257 | 0.03196704496 | 1.01375 |
| `DIAG` | DIAG mean drug quantity, users |  | 0.0307183485 | 0.02238358757 | 0.728672 |
| `DIAG` | DIAG onset at the mean quantity |  | 0.4474037703 | 0.3509173959 | 0.784342 |
| `MOMENT` | MOMENT y_u income of drug users model |  | 0.1701815151 | 0.3035585486 | 1.78373 |
| `UNTARGETED` | UNTARGETED income with a SUD model |  | 0.206082506 | 1.716650401 | 8.32992 |
| `DIAG` | DIAG carriers of the disorder consuming no drugs |  | 0.005460329644 | 0.02340151988 | 4.28573 |
| `DIAG` | DIAG income of experimenters / average |  | 0.1554936765 | 0.6060050697 | 3.8973 |
| `DIAG` | DIAG income of drug users / labour income |  | 0.1556699664 | 0.2003531552 | 1.28704 |
| `DIAG` | DIAG income with a SUD / labour income |  | 0.1885096438 | 1.133014787 | 6.01038 |
| `DIAG` | DIAG mass ON the top savings grid point |  | 0.0001438727619 | 0.0002870192466 | 1.99495 |
| `DIAG` | DIAG mass in the top THREE savings grid points |  | 0.000627350315 | 0.001250753759 | 1.99371 |
| `DIAG` | DIAG age 26 homeless |  | 0.152777 | 0.061847 | 0.404819 |
| `DIAG` | DIAG age 26 homeless | field 4 | -0.03514 | -0.03508 | 0.998293 |
| `DIAG` | DIAG age 29 homeless |  | 0.004066 | 0.002796 | 0.687654 |
| `DIAG` | DIAG age 29 homeless | field 3 | 0.31243 | 0.31721 | 1.0153 |
| `DIAG` | DIAG age 29 homeless | field 4 | -0.02039 | -0.02065 | 1.01275 |
| `DIAG` | DIAG age 32 homeless |  | 0.001285 | 0.000683 | 0.531518 |
| `DIAG` | DIAG age 32 homeless | field 3 | 0.55313 | 0.56073 | 1.01374 |
| `DIAG` | DIAG age 32 homeless | field 4 | -0.01086 | -0.01098 | 1.01105 |
| `DIAG` | DIAG age 35 homeless |  | 0.000525 | 0.000278 | 0.529524 |
| `DIAG` | DIAG age 35 homeless | field 3 | 0.79471 | 0.80363 | 1.01122 |
| `DIAG` | DIAG age 35 homeless | field 4 | -0.00113 | -0.00127 | 1.12389 |
| `DIAG` | DIAG age 38 homeless |  | 0.000332 | 0.000172 | 0.518072 |
| `DIAG` | DIAG age 38 homeless | field 3 | 1.05411 | 1.067 | 1.01223 |
| `DIAG` | DIAG age 38 homeless | field 4 | 0.00939 | 0.00926 | 0.986155 |
| `DIAG` | DIAG age 41 homeless |  | 0.000174 | 9e-05 | 0.517241 |
| `DIAG` | DIAG age 41 homeless | field 3 | 1.31516 | 1.33423 | 1.0145 |
| `DIAG` | DIAG age 41 homeless | field 4 | 0.01969 | 0.01968 | 0.999492 |
| `DIAG` | DIAG age 44 homeless |  | 0.000109 | 6.1e-05 | 0.559633 |
| `DIAG` | DIAG age 44 homeless | field 3 | 1.58142 | 1.60941 | 1.0177 |
| `DIAG` | DIAG age 44 homeless | field 4 | 0.02947 | 0.02965 | 1.00611 |
| `DIAG` | DIAG age 47 homeless |  | 6.6e-05 | 3.5e-05 | 0.530303 |
| `DIAG` | DIAG age 47 homeless | field 3 | 1.84234 | 1.88361 | 1.0224 |
| `DIAG` | DIAG age 47 homeless | field 4 | 0.03828 | 0.0388 | 1.01358 |
| `DIAG` | DIAG age 50 homeless |  | 8.6e-05 | 4.6e-05 | 0.534884 |
| `DIAG` | DIAG age 50 homeless | field 3 | 2.0945 | 2.15226 | 1.02758 |
| `DIAG` | DIAG age 50 homeless | field 4 | 0.04606 | 0.04698 | 1.01997 |
| `DIAG` | DIAG age 53 homeless |  | 7e-05 | 3.7e-05 | 0.528571 |
| `DIAG` | DIAG age 53 homeless | field 3 | 2.32543 | 2.40412 | 1.03384 |
| `DIAG` | DIAG age 53 homeless | field 4 | 0.05222 | 0.05359 | 1.02624 |
| `DIAG` | DIAG age 56 homeless |  | 6.4e-05 | 3.4e-05 | 0.53125 |
| `DIAG` | DIAG age 56 homeless | field 3 | 2.51179 | 2.61997 | 1.04307 |
| `DIAG` | DIAG age 56 homeless | field 4 | 0.05612 | 0.05813 | 1.03582 |
| `DIAG` | DIAG age 59 homeless |  | 7.6e-05 | 4.8e-05 | 0.631579 |
| `DIAG` | DIAG age 59 homeless | field 3 | 2.63623 | 2.79466 | 1.0601 |
| `DIAG` | DIAG age 59 homeless | field 4 | 0.05743 | 0.0607 | 1.05694 |
| `DIAG` | DIAG age 62 homeless |  | 9.3e-05 | 4.8e-05 | 0.516129 |
| `DIAG` | DIAG age 62 homeless | field 3 | 2.69017 | 2.89359 | 1.07562 |
| `DIAG` | DIAG age 62 homeless | field 4 | 0.05654 | 0.06061 | 1.07198 |
| `DIAG` | DIAG age 65 homeless |  | 7.8e-05 | 4.2e-05 | 0.538462 |
| `DIAG` | DIAG age 65 homeless | field 3 | 2.67229 | 2.9297 | 1.09633 |
| `DIAG` | DIAG age 65 homeless | field 4 | 0.05271 | 0.05767 | 1.0941 |
| `DIAG` | DIAG age 68 homeless | field 3 | 2.43073 | 2.72994 | 1.12309 |
| `DIAG` | DIAG age 68 homeless | field 4 | 0.62879 | 0.56639 | 0.900762 |
| `DIAG` | DIAG age 71 homeless | field 3 | 2.05868 | 2.3894 | 1.16065 |
| `DIAG` | DIAG age 71 homeless | field 4 | 0.61763 | 0.57674 | 0.933795 |
| `DIAG` | DIAG age 74 homeless | field 3 | 1.63659 | 1.98609 | 1.21355 |
| `DIAG` | DIAG age 74 homeless | field 4 | 0.60497 | 0.59363 | 0.981255 |
| `DIAG` | DIAG age 77 homeless | field 3 | 1.1826 | 1.52683 | 1.29108 |
| `DIAG` | DIAG age 77 homeless | field 4 | 0.59135 | 0.62264 | 1.05291 |
| `DIAG` | DIAG age 80 homeless | field 3 | 0.72861 | 1.03221 | 1.41668 |
| `DIAG` | DIAG age 80 homeless | field 4 | 0.57773 | 0.67673 | 1.17136 |
| `DIAG` | DIAG age 83 homeless | field 3 | 0.33229 | 0.56833 | 1.71034 |
| `DIAG` | DIAG age 83 homeless | field 4 | 0.56584 | 0.82361 | 1.45555 |
## Reading of the result

21 of the 23 `MOMENT` values disagree; only `sigma_y` and `kappa_uem` survive
to 4 significant figures. 126 of 171 `DIAG` values and 39 of 46 `UNTARGETED`
values disagree.

The four fixes did land: `tau_l` no longer halves, and that was the specific
defect they targeted. But the population-replication identity is still broken
across nearly every reported quantity, several ratios sit at a clean 2.0, and
the two-type run now fails two mass-conservation invariants that the one-type
run passes. The count rising from 135 to 186 is not necessarily 51 new bugs —
the reported set changed and `tau_l`'s correction shifts every quantity that
depends on the tax rate — but it is not progress toward the identity either.

The 2.0 ratios and the 2.0367e-05 histogram overshoot are the most direct
leads: both point at accumulation over types where an average is wanted.
