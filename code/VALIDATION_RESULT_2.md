# Equal-beta validation of the two-type model: FAIL

**Not every moment agrees to 4 significant figures.** Of 242 numeric values compared
across `MOMENT`, `DIAG` and `UNTARGETED` rows, **135 disagree** at 4 significant
figures: 23 of 46 `MOMENT` values,
73 of 104 `DIAG` values, and
39 of 92 `UNTARGETED` values.

Every value that does disagree is listed below with its ratio.

## What was run

Two points at the same parameter vector, differing in one coordinate only
(`number_of_beta_types`), from `code/VALIDATE2.txt`. Both discount factors were
set equal (`discount_factor=discount_factor_impatient=0.99715`).

| | one type | two types |
| --- | --- | --- |
| point file | `point_cc2658fdf5_frozen_beta.txt` | `point_f48e057502_frozen_beta.txt` |
| tag | `cc2658fdf5` | `f48e057502` |
| model hash | `4b6f4c88bf` | `4b6f4c88bf` |
| handover | 29 of 29 | 29 of 29 |
| solve time | 12 min | 18 min |

Both runs used the same `hftf` binary: the source was unchanged between them, so
the second run did not rebuild, and both point files carry the same `MODEL` hash.

That hash is also how the two points can be told apart from ordinary ones without
reading this file. `MODEL` is the first ten characters of the md5 of the Fortran
source. The committed source hashes to `d70ad1c545`; these two points are stamped
`4b6f4c88bf`, which is the same file with `freeze_beta_bisection` flipped to 1.
Any point in `code/points/` carrying `4b6f4c88bf` was measured on the frozen
build and is not an ordinary point.

### These two points are validation artefacts, not ordinary points

Both were measured with `freeze_beta_bisection=1`, which is **not** the committed
default (the declaration at line 1369 reads `=0` and has been restored to `=0`).
Freezing the internal bisection is what makes the comparison meaningful — it stops
the solver from moving `beta` between the two runs — but it also means neither
point is a calibrated measurement of anything: `MOMENT beta wealth over output`
sits at 4.012147737
against a target of 3.0 and was never allowed to move toward it. **Both files are
named `*_frozen_beta.txt` so nothing scores them as ordinary points.**

## The test, and what it means that it failed

With both discount factors equal and the bisection frozen, the two passes of the
two-type model solve the identical household problem over the identical state
space. The two-type population is therefore two identical copies of the one-type
population, and since the accumulators are deliberately not reset on the second
pass, every accumulator should come out exactly doubled. Every targeted moment is
a ratio, so the doubling cancels and every moment must reproduce to machine
precision. It does not.

## Where the failure is, and where it is not

The comparison splits cleanly, and the split localises the bug.

**Reproduces exactly.** Every input constant (targets, data values, handed-over
parameters), and — importantly — the objects computed from the value and policy
functions before any distribution is involved:

| row | one-type | two-type |
| --- | ---: | ---: |
| `DIAG lowest value of a period of life` | -60.02480489061115 | -60.02480489061115 |
| `DIAG drug threshold, (phi/theta)*p*b` | 0.015180225478830281 | 0.015180225478830281 |
| `MOMENT sigma_y bottom half earnings share` | 0.16905002140174125 | 0.16905002140174125 |

`lowest value of a period of life` agreeing to all sixteen digits is the useful
one: the second pass really does solve the same problem and get the same policy
functions. So the two passes are not disagreeing about the household problem.

**Does not reproduce.** Essentially every quantity that is accumulated over the
distribution. That is exactly the class the test was built to probe, and it
confirms the failure is in how the second pass accumulates rather than in how it
solves.

**The ratios are not a single clean factor.** They run from
0.09038263433 to 4.175844033 across the
targeted moments. A uniformly missing reset would show every ratio at 0.5 or 2.0;
these do not, so this is not one forgotten `accumulating_beta_types==0` guard.
Some rows are close to a factor of two in either direction
(`tau_l` at 0.4969428997,
`pi_eu` at 0.5093982322,
`y_u` at 1.973435088),
which is the signature of one side of a ratio doubling while the other does not.
Others are nowhere near it
(`tau_u` at 0.09038263433,
`kappa_ued` at 4.175844033,
`aleph` at 2.816844922),
which means doubled aggregates are also feeding back into quantities that depend
on levels rather than ratios — thresholds defined against an average or a median,
and the equilibrium objects the two passes share (prices, the government budget,
inheritance). A moment measured against a doubled mean is not rescalable.

**Three of the doubled rows are levels, and those are not the bug.** The design
comment at the head of the beta-type loop says explicitly that a level comes out
doubled and that it is "worth checking that no targeted moment is one". Three
diagnostics are levels by name and behave exactly as predicted:

| row | one-type | two-type | ratio |
| --- | ---: | ---: | ---: |
| `DIAG mass ON the top savings grid point` | 0.0001438727512 | 0.0002870193418 | 1.994952757 |
| `DIAG mass in the top THREE savings grid points` | 0.0006273502685 | 0.001250754114 | 1.993709378 |
| `DIAG working age homeless mass` | 0.199502893 | 0.4117072226 | 2.063665425 |

These are diagnostics rather than targeted moments, so their doubling is the
design working as documented and should not be chased. `DIAG mass with a NEGATIVE
value of life` doubles the same way, to 1.155997771 — worth noting only because a
quantity that reads as a share is now above one, so if anything downstream ever
treats that row as a share it will be wrong on the two-type path.

The rows that must be 1.0 and are near 2.0 are a different matter, because they are
ratios by construction and a ratio cannot legitimately double:
`MOMENT y_u income of drug users` at 1.973435088,
`DIAG income of WORKING AGE drug users / average` at 2.035449647, and
`UNTARGETED income of the homeless` at 2.00959383. In each the numerator picked up
the second pass and the denominator did not.

**One target moved, which no target should.** Every other target and data value in
both files is bit-identical, as they must be — they are constants. `MOMENT p_m SMI
population share` is the exception: its target reads 0.04820667885 in the one-type run and
0.04821525648 in the two-type run. That target is therefore not a constant but is computed
from the model, so the second pass is reaching something that was assumed fixed.
The move is small, but it means `p_m` is being scored against a moving goalpost on
the two-type path.

One further sign that the second pass is not merely additive: the three internal
consistency checks below, which are ratios of one accumulator to another and hold
to thirteen digits in the one-type run, lose eight digits in the two-type run.

## The `want 1.0` diagnostics

These are internal consistency checks; each should be exactly 1.0.

One type (`point_cc2658fdf5_frozen_beta.txt`):

```
 DIAG income histogram mass / distribution (want 1.0) =   1.0000000000000810
 DIAG histogram mass / distribution  (want 1.0)   =   1.0000000000000853
 DIAG histogram wealth / total wealth (want 1.0)  =   1.0000000000001006
```

Two types (`point_f48e057502_frozen_beta.txt`):

```
 DIAG income histogram mass / distribution (want 1.0) =   1.0000203740833264
 DIAG histogram mass / distribution  (want 1.0)   =   1.0000203740833347
 DIAG histogram wealth / total wealth (want 1.0)  =   1.0000000000001958
```

The wealth check is essentially unchanged. Both mass checks degrade from agreeing
with 1.0 to thirteen digits to agreeing to only five — small in absolute terms,
but it is a histogram mass that no longer matches the distribution it was built
from, and it appears only on the two-type path.

## Every disagreeing value

### Targeted moments (23 of 46 values)

| row | one-type | two-type | ratio (two/one) |
| --- | ---: | ---: | ---: |
| `MOMENT tau_l average labour income tax *(model)*` | 0.2376199219 | 0.118083533 | 0.4969428997 |
| `MOMENT omega_l labour supply / total hours *(model)*` | 0.4011421363 | 0.4026778036 | 1.003828237 |
| `MOMENT beta wealth over output *(model)*` | 4.012147737 | 4.047583053 | 1.008832007 |
| `MOMENT h_2 above half of spending *(model)*` | 0.04940559841 | 0.05241614441 | 1.060935321 |
| `MOMENT h_3 share in the largest unit *(model)*` | 0.6702230446 | 0.6758845767 | 1.008447236 |
| `MOMENT gamma housing over expenditure *(model)*` | 0.1866914537 | 0.1916184481 | 1.026391108 |
| `MOMENT h_1 homelessness rate *(model)*` | 0.003914259131 | 0.00416361506 | 1.063704502 |
| `MOMENT b total drug users *(model)*` | 0.02462337866 | 0.0277659942 | 1.127627308 |
| `MOMENT lambda_d disorder rate *(model)*` | 0.007149013737 | 0.002891527774 | 0.4044652704 |
| `MOMENT theta drug spending share *(model)*` | 0.2569293645 | 0.2131835712 | 0.8297361092 |
| `MOMENT aleph value of life / income *(model)*` | 57.51183111 | 162.0019094 | 2.816844922 |
| `MOMENT pi_eu unemployment rate *(model)*` | 0.05298367015 | 0.02698978791 | 0.5093982322 |
| `MOMENT kappa_ued unemployment given SUD *(model)*` | 0.1028213127 | 0.429365765 | 4.175844033 |
| `MOMENT kappa_uem employment given SMI *(model)*` | 0.301819096 | 0.3024128937 | 1.001967396 |
| `MOMENT p_m SMI population share *(model)*` | 0.04398398609 | 0.04398841159 | 1.000100616 |
| `MOMENT p_m SMI population share *(target)*` | 0.04820667885 | 0.04821525648 | 1.000177935 |
| `MOMENT lambda_m SMI share of the homeless *(model)*` | 0.2331997747 | 0.190695991 | 0.8177366008 |
| `MOMENT pi_V eligibles with a voucher *(model)*` | 0.2714389236 | 0.173046588 | 0.6375157464 |
| `MOMENT cbar food stamps / labour income *(model)*` | 0.01120508118 | 0.0157021897 | 1.401345466 |
| `MOMENT tau_u treatment take up *(model)*` | 0.08382139321 | 0.007575998331 | 0.09038263433 |
| `MOMENT mu_H recovery housed / homeless *(model)*` | 1.405875577 | 1.36460639 | 0.9706452066 |
| `MOMENT w_bot net worth share, bottom half *(model)*` | 0.1571599575 | 0.1592922844 | 1.013567876 |
| `MOMENT y_u income of drug users *(model)*` | 0.170200664 | 0.3358799623 | 1.973435088 |

### Diagnostics (73 of 104 values)

| row | one-type | two-type | ratio (two/one) |
| --- | ---: | ---: | ---: |
| `DIAG unit 0 share of renters *(renters)*` | 0.120663992 | 0.1185402549 | 0.9823995787 |
| `DIAG unit 1 share of renters *(renters)*` | 0.2091129634 | 0.2083505044 | 0.9963538419 |
| `DIAG unit 2 share of renters *(renters)*` | 0.6702230446 | 0.6731092406 | 1.004306322 |
| `DIAG unit 2 share of renters *(income)*` | 0.3812032823 | 0.4085962219 | 1.071859139 |
| `DIAG aggregate rent / aggregate income ` | 0.2074195246 | 0.2082763739 | 1.004130996 |
| `DIAG aggregate housing / aggregate expenditure ` | 0.1866914537 | 0.1916184481 | 1.026391108 |
| `DIAG over half of EXPENDITURE, all households ` | 0.04940559841 | 0.05241614441 | 1.060935321 |
| `DIAG over half of EXPENDITURE, housed only ` | 0.04959974467 | 0.05262870836 | 1.061068131 |
| `DIAG income of WORKING AGE drug users / average ` | 0.1633688568 | 0.3325290818 | 2.035449647 |
| `DIAG working age share of drug users ` | 0.3136040498 | 0.3468337043 | 1.10596054 |
| `DIAG users band 1 use rate *(rate)*` | 0.01020895587 | 0.01281282536 | 1.255057375 |
| `DIAG users band 1 use rate *(disorder)*` | 0.2798909502 | 0.02551668154 | 0.09116651152 |
| `DIAG users band 1 use rate *(income/average)*` | 0.1881132401 | 0.5084053461 | 2.702655835 |
| `DIAG users band 2 use rate *(rate)*` | 0.005350268726 | 0.0005737145546 | 0.1072309792 |
| `DIAG users band 2 use rate *(disorder)*` | 0.9396402451 | 0.5581322478 | 0.5939850391 |
| `DIAG users band 2 use rate *(income/average)*` | 0.2865624954 | 0.1275672029 | 0.4451636378 |
| `DIAG users band 3 use rate *(rate)*` | 0.006457725704 | 0.00310185187 | 0.480331933 |
| `DIAG users band 3 use rate *(disorder)*` | 0.4835180926 | 0.06886461418 | 0.142424069 |
| `DIAG users band 3 use rate *(income/average)*` | 0.1839771975 | 0.1378552204 | 0.7493060135 |
| `DIAG users band 4 use rate *(rate)*` | 0.01908656745 | 0.009710498876 | 0.5087608812 |
| `DIAG users band 4 use rate *(disorder)*` | 0.0839517769 | 0.03448510899 | 0.4107728302 |
| `DIAG users band 4 use rate *(income/average)*` | 0.1110477695 | 0.1928573537 | 1.736706236 |
| `DIAG users band 5 use rate *(rate)*` | 0.06406019693 | 0.03434650545 | 0.536159848 |
| `DIAG users band 5 use rate *(disorder)*` | 0.2792510623 | 0.2819513222 | 1.009669649 |
| `DIAG users band 5 use rate *(income/average)*` | 0.1719298125 | 0.3352139956 | 1.949714193 |
| `DIAG buyers: mean C ` | 0.133345062 | 0.1303146157 | 0.9772736519 |
| `DIAG non-buyers: mean C ` | 0.3967882301 | 0.3939738407 | 0.9929070745 |
| `DIAG buyers: mean income ` | 0.08485120853 | 0.0952142657 | 1.12213211 |
| `DIAG non-buyers: mean income ` | 0.5085282515 | 0.5067996522 | 0.9966007804 |
| `DIAG buyers as a share of clean households ` | 0.01760018892 | 0.02224874506 | 1.264119673 |
| `DIAG assets of drug users / average net worth ` | 0.2079014463 | 0.1847664149 | 0.8887211619 |
| `DIAG assets of experimenters / average net worth ` | 0.2190489341 | 0.2046844518 | 0.9344234095 |
| `DIAG assets with a SUD / average net worth ` | 0.1806535943 | 0.1066755446 | 0.5904977702 |
| `DIAG mass with a NEGATIVE value of life ` | 0.5714269982 | 1.155997771 | 2.023001669 |
| `DIAG value of life, drug users ` | 16.89743019 | 16.00090392 | 0.9469430402 |
| `DIAG value of life, everyone else ` | 18.68946513 | 18.64645395 | 0.9976986403 |
| `DIAG treatment price / average labour income  *(value)*` | 0.1006946573 | 0.1431318998 | 1.421444828 |
| `DIAG households receiving food stamps  *(value)*` | 1.546139281 | 1.54495081 | 0.9992313303 |
| `DIAG aggregate rent / output ` | 0.2406934268 | 0.2419896052 | 1.005385184 |
| `DIAG share in the smallest unit ` | 0.120663992 | 0.1164982075 | 0.965476159 |
| `DIAG SUD rate, income band 1 *(model)*` | 0.02162831087 | 0.02237245381 | 1.034405967 |
| `DIAG SUD rate, income band 2 *(model)*` | 0.01598186786 | 0.01113796065 | 0.6969123222 |
| `DIAG SUD rate, income band 3 *(model)*` | 0.002402135206 | 0.00155580496 | 0.6476758496 |
| `DIAG SUD rate, income band 4 *(model)*` | 0.001893106356 | 0.000987867443 | 0.5218235309 |
| `DIAG SUD rate, income band 5 *(model)*` | 0.0001815627842 | 0.0001015692178 | 0.559416503 |
| `DIAG SUD rate, income band 6 *(model)*` | 2.556361407e-08 | 1.340093504e-08 | 0.524219111 |
| `DIAG homelessness rate rebuilt from the bands ` | 0.003914259131 | 0.004038935278 | 1.031851787 |
| `DIAG disorder rate, band 1 ` | 0.00285739436 | 0.001755583196 | 0.6144000355 |
| `DIAG disorder rate, band 2 ` | 0.005027327817 | 0.002833381641 | 0.5635959587 |
| `DIAG disorder rate, band 3 ` | 0.003122427215 | 0.001774013791 | 0.5681521678 |
| `DIAG disorder rate, band 4 ` | 0.001602351253 | 0.001135556391 | 0.7086813139 |
| `DIAG disorder rate, band 5 ` | 0.01788887805 | 0.01863739081 | 1.041842354 |
| `DIAG SUD share of the homeless, band 1 ` | 0.0002177378809 | 0.0001087206228 | 0.4993188246 |
| `DIAG SUD share of the homeless, band 2 ` | 0.00636289498 | 0.003184073299 | 0.5004126753 |
| `DIAG SUD share of the homeless, band 3 ` | 0.000703645251 | 0.0006745306467 | 0.9586231781 |
| `DIAG SUD share of the homeless, band 4 ` | 0.001492500341 | 0.001527115277 | 1.023192581 |
| `DIAG SUD share of the homeless, band 5 ` | 0.0003312613158 | 0.0003580045259 | 1.080731461 |
| `DIAG households with no wage income, working age  *(value)*` | 0.05298367015 | 0.0527777007 | 0.9961125863 |
| `DIAG employed share of the homeless, working age ` | 0.9769542062 | 0.9311410024 | 0.9531060888 |
| `DIAG working age homeless mass ` | 0.199502893 | 0.4117072226 | 2.063665425 |
| `DIAG homeless who could afford it on INCOME ALONE` | 0.935689652 | 0.9247503019 | 0.9883087837 |
| `DIAG homeless by choice, share of the homeless ` | 0.9357263221 | 0.9247898065 | 0.9883122711 |
| `DIAG homeless receiving food stamps ` | 9.778476095e-05 | 0.0001041146131 | 1.064732501 |
| `DIAG average assets of the homeless ` | 0.02114956071 | 0.04628869511 | 2.188636244 |
| `DIAG wealth share of the bottom 25 pct ` | 0.03153353371 | 0.03196705565 | 1.013747966 |
| `DIAG mean drug quantity, users ` | 0.03071836163 | 0.02052874167 | 0.6682889511 |
| `DIAG onset at the mean quantity ` | 0.4474039104 | 0.3272495704 | 0.7314410151 |
| `DIAG carriers of the disorder consuming no drugs ` | 0.005455251809 | 0.02339190158 | 4.287960007 |
| `DIAG income of experimenters / average ` | 0.1554937246 | 0.3437364442 | 2.210612969 |
| `DIAG income of drug users / labour income ` | 0.1556875076 | 0.2216858105 | 1.423915213 |
| `DIAG income with a SUD / labour income ` | 0.1885704057 | 0.2013558917 | 1.067802188 |
| `DIAG mass ON the top savings grid point ` | 0.0001438727512 | 0.0002870193418 | 1.994952757 |
| `DIAG mass in the top THREE savings grid points ` | 0.0006273502685 | 0.001250754114 | 1.993709378 |

### Untargeted moments (39 of 92 values)

Not required by the test, but reported because they are model output measured on
the same two runs and show the same pattern.

| row | one-type | two-type | ratio (two/one) |
| --- | ---: | ---: | ---: |
| `UNTARGETED mean age of drug users *(model)*` | 68.42868548 | 65.71501046 | 0.9603430199 |
| `UNTARGETED users aged 26-34, share *(model)*` | 0.07282767867 | 0.1621283507 | 2.226191383 |
| `UNTARGETED users aged 35-44, share *(model)*` | 0.04182027899 | 0.007955624611 | 0.190233657 |
| `UNTARGETED users aged 45-54, share *(model)*` | 0.04905708867 | 0.0418167499 | 0.8524099379 |
| `UNTARGETED users aged 55-64, share *(model)*` | 0.1362097914 | 0.1229896868 | 0.9029430668 |
| `UNTARGETED users aged 65 plus, share *(model)*` | 0.7000851622 | 0.6651095879 | 0.9500409719 |
| `UNTARGETED housing over income, renters *(model)*` | 0.2523734894 | 0.1307276632 | 0.5179928504 |
| `UNTARGETED delta_d child SUD ratio *(model)*` | 1.962679735 | 2.347327907 | 1.19598112 |
| `UNTARGETED wealth share bottom 5 pct *(model)*` | 0.0003358089277 | 0.000387358194 | 1.15350773 |
| `UNTARGETED wealth share bottom 10 pct *(model)*` | 0.002996251892 | 0.003033826276 | 1.012540462 |
| `UNTARGETED income share bottom 1 pct *(model)*` | 0.0006904091333 | 0.0006944274345 | 1.005820174 |
| `UNTARGETED income share bottom 5 pct *(model)*` | 0.003452045667 | 0.003472137173 | 1.005820174 |
| `UNTARGETED income share bottom 10 pct *(model)*` | 0.008681023866 | 0.008607065286 | 0.9914804312 |
| `UNTARGETED delta_h child homelessness ratio *(model)*` | 2.217883745 | 2.214983011 | 0.9986921162 |
| `UNTARGETED homelessness rate, band 1 *(model)*` | 0.02180529669 | 0.02249790238 | 1.031763186 |
| `UNTARGETED homelessness rate, band 2 *(model)*` | 0.000276065084 | 0.0002878499341 | 1.042688666 |
| `UNTARGETED homelessness rate, band 3 *(model)*` | 7.707043654e-05 | 8.007440893e-05 | 1.038976974 |
| `UNTARGETED homelessness rate, band 4 *(model)*` | 8.513245655e-05 | 8.484263771e-05 | 0.9965956716 |
| `UNTARGETED homelessness rate, band 5 *(model)*` | 5.647937651e-06 | 5.555863624e-06 | 0.9836977614 |
| `UNTARGETED homelessness profile, band 2 *(model)*` | 0.07052805518 | 0.0712687662 | 1.01050236 |
| `UNTARGETED homelessness profile, band 3 *(model)*` | 0.0196896613 | 0.01982562319 | 1.006905243 |
| `UNTARGETED homelessness profile, band 4 *(model)*` | 0.02174931544 | 0.02100618897 | 0.9658321906 |
| `UNTARGETED homelessness profile, band 5 *(model)*` | 0.001442913579 | 0.001375576294 | 0.9533324204 |
| `UNTARGETED share of the homeless, band 2 *(model)*` | 0.01357440749 | 0.01371993456 | 1.010720694 |
| `UNTARGETED share of the homeless, band 3 *(model)*` | 0.003683053829 | 0.003710483064 | 1.007447416 |
| `UNTARGETED share of the homeless, band 4 *(model)*` | 0.003821850831 | 0.003693591023 | 0.966440394 |
| `UNTARGETED share of the homeless, band 5 *(model)*` | 0.0003882849593 | 0.0003698023948 | 0.9523994837 |
| `UNTARGETED renters above 30 pct of income *(model)*` | 0.4174389591 | 0.4337956474 | 1.039183425 |
| `UNTARGETED renters above 50 pct of income *(model)*` | 0.2554912245 | 0.2996078679 | 1.172673811 |
| `UNTARGETED tenant contribution rate *(model)*` | 0.469627559 | 0.7397873521 | 1.575263925 |
| `UNTARGETED voucher holders, wages main *(model)*` | 0.4898473048 | 0.4777011807 | 0.9752042648 |
| `UNTARGETED participation, with a SUD *(model)*` | 0.3292920727 | 0.08046071076 | 0.2443445118 |
| `UNTARGETED participation, without a SUD *(model)*` | 0.7505385702 | 0.7518463912 | 1.00174251 |
| `UNTARGETED SMI alongside SUD at admission *(model)*` | 0.008849152197 | 0.004522279593 | 0.5110410006 |
| `UNTARGETED SUD share of the homeless *(model)*` | 0.0003078604019 | 0.00144187784 | 4.683544332 |
| `UNTARGETED drug deaths, share of deaths *(model)*` | 0.02619879975 | 0.004087432872 | 0.1560160355 |
| `UNTARGETED income of the homeless *(model)*` | 0.274647503 | 0.5519299274 | 2.00959383 |
| `UNTARGETED employed share of the homeless *(model)*` | 0.9769542062 | 0.9311410024 | 0.9531060888 |
| `UNTARGETED income with a SUD *(model)*` | 0.2061488988 | 0.3050777546 | 1.479890295 |

## Method

Values were paired by row text and value position, not by name alone, because
several diagnostic rows repeat verbatim within a file and several carry more than
one number per line. Where a row appears more than once, the last occurrence is
compared; no repeated row varied within either file. One row
(`DIAG SUD rate, income band 7`) appears 365 times in the one-type file and once
in the two-type file — a print-loop artefact, not a missing diagnostic: both files
carry the same 59 distinct `DIAG` row texts, and that row's values agree.

Agreement is "within 4 significant figures", tested as
`abs(a-b)/max(abs(a),abs(b)) < 1e-4`.

