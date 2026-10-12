# VERDICT: **FAIL** -- 188 of 237 model-generated values disagree beyond 4 significant figures (previous test: 135 of 242).

> **Provenance: this measures commit `50e121d`, not the current head.**
> Both runs were solved against `code/housing_first_or_treatment_first_SR_v1.f90`
> at `md5 df02e3db80`, which is commit `50e121d` ("Give the homelessness rate a
> single owner") -- the branch head when the runs started. The branch has since
> advanced, and the source is now `md5 163f49d500`. Several of the commits that
> landed in between target faults this test reports, in particular `9479667`
> ("Give every shared counter one owner, and stop aleph doubling at two types")
> and `84c1ee5` ("Fix two undefined reads in the secant and a race in the
> distribution sweep"). **The counts and ratios below therefore describe
> `50e121d` and should not be read as the current state of the branch.** Re-run
> both lines of `code/VALIDATE3.txt` against the present head before drawing
> conclusions about it.

## What was run

Branch `claude/two-period-addiction-hazard-d7gb61`, source `md5 df02e3db80` (commit `50e121d`), with the single
edit `freeze_beta_bisection=0 -> 1` in place for both runs and reverted afterwards. Both runs
report the same compiled model, `MODEL 59adddbccd`, and both printed `HANDOVER OK: 31 of 31
parameters applied` and ended with `===== END OF MOMENTS =====`.

| run | line | point file | solve |
|---|---|---|---|
| one-type | `number_of_beta_types=1` | `code/points/point_fdee960558_frozen_beta_v5.txt` | 12 min |
| two-type | `number_of_beta_types=2` | `code/points/point_03ac59f09e_frozen_beta_v5.txt` | 18 min |

`discount_factor` and `discount_factor_impatient` are both `0.99715`, so the two-type population
is two identical copies of the one-type population and every reported number must reproduce to
machine precision. Ratios below are **one-type / two-type**, the convention the previous test used.

### On the denominator

The comparator parses every numeric field on every `MOMENT`, `DIAG` and `UNTARGETED` line.
It finds 237 model-generated values in this build (plus 81 constants -- targets, observed
data -- which are inputs and agree trivially). Replaying the same comparator over the previous
test's own two point files (`point_f48e057502_frozen_beta.txt` and `point_cc2658fdf5_frozen_beta.txt`)
returns **136 disagreements out of 238**, against the 135 of 242 on record -- so the method is
the same one, and the small denominator drift is this build emitting a few more values, not a
different counting rule. The counts are therefore comparable.

## (b) tau_l -- the single most important number

| | value |
|---|---|
| `MOMENT tau_l` one-type | `0.23761995120787788` |
| `MOMENT tau_l` two-type | `0.23820523325586737` |
| ratio one/two | **0.997542951** |
| previous | 0.497 (exactly halved) |

**The exact halving is gone.** `tau_l` was 0.497 -- a clean factor of two -- and is now 0.9975.
That specific bug, the one that halved the labour income tax, is fixed.

**But `tau_l` still does not agree.** 0.9975 is a 0.25% gap, roughly 2,500 times looser than
4 significant figures. Two identical copies of the same population must return the same average
labour income tax bit for bit. So the answer to "does it now agree" is: **no, it does not** --
it has stopped being wrong by a factor of two and started being wrong by a quarter of a percent.

## (c) The nine that disagreed before

| moment | one-type | two-type | ratio one/two | previous | agrees now? |
|---|---|---|---|---|---|
| `pi_eu` | 0.05298364856 | 0.05279566072 | **1.003561** | 0.509 | **no** |
| `y_u` | 0.1886794059 | 0.1961931246 | **0.961702** | 1.973 | **no** |
| `tau_u` | 0.08382140638 | 0.06470493699 | **1.295441** | 0.09 | **no** |
| `kappa_ued` | 0.102821319 | 0.09579811092 | **1.073313** | 4.18 | **no** |
| `aleph` | 1.128320071 | 0.06520200828 | **17.304990** | 2.82 | **no** |
| `b` | 0.02462338653 | 0.02463741848 | **0.999430** | 1.128 | **no** |
| `h_1` | 0.0039142606 | 0.004512255905 | **0.867473** | 1.064 | **no** |
| `cbar` | 0.0002198308526 | 1.289228428e-05 | **17.051350** | 1.401 | **no** |
| `w_bot` | 0.1571600243 | 0.1551140646 | **1.013190** | 1.014 | **no** |

None of the nine agrees. `aleph` (17.30) and `cbar` (17.05) are far worse than the factor-of-two
era they came from; `b` (0.9994) and `w_bot` (1.0132) are close but still outside 4 significant
figures; the rest sit between 0.87 and 1.30.

## (d) The five diagnostics that read exactly 2.0 before

| diagnostic | one-type | two-type | ratio one/two | previous |
|---|---|---|---|---|
| mass in the top THREE savings grid points | 0.0006273505055 | 0.001232093913 | **0.509174** | 2.0 |
| mass ON the top savings grid point | 0.0001438728056 | 0.0002718876055 | **0.529163** | 2.0 |
| mass with a NEGATIVE value of life | 0.5714241616 | 1.147730787 | **0.497873** | 2.0 |
| working age homeless mass | 0.1995028925 | 0.460071761 | **0.433634** | 2.0 |
| average assets of the homeless | 0.02114955967 | 0.05158894442 | **0.409963** | 2.0 |

**These have inverted, not converged.** They read 2.0 before, meaning the two-type run reported
half the one-type value. They now read about 0.5, meaning the two-type run reports roughly
*double* it. The normalisation that was dividing once too often is now not dividing at all for
this group of five.

Two of them are provably wrong on their own, without reference to the one-type run:

- `mass with a NEGATIVE value of life` = **1.147730787** in the two-type run.
  This is a population share and cannot exceed 1.
- `average assets of the homeless` goes 0.02114955967 -> 0.05158894442.
  An *average* over two identical copies must equal the average over one. Doubling it means a
  per-type sum is being reported where a mean is intended.

## (e) Every line still outside 4 significant figures

189 values, of which 188 are model-generated and one is the `p_m` target
(itself model-derived: 0.04820668 vs 0.04820280). The list is not empty. Full list:

`#N` indexes the Nth numeric field on that printed line. On the age lines the label is the
text up to the first `=`, so `DIAG age 68 homeless #1` is `homeless`, `#2` is `own`, `#3` is
`renter wealth` and `#4` is `renter income`. Likewise `DIAG unit 2 share of renters #2` is the
`of whom over half of income` field, and `DIAG users band 1 use rate #2` and `#3` are
`share with the disorder` and `income/average`.

| line | one-type | two-type | ratio one/two |
|---|---|---|---|
| `MOMENT tau_l average labour income tax model #1` | 0.2376199512 | 0.2382052333 | 0.997543 |
| `MOMENT omega_l labour supply / total hours model #1` | 0.4011421033 | 0.399027622 | 1.0053 |
| `MOMENT beta wealth over output model #1` | 4.012148292 | 3.990741344 | 1.00536 |
| `MOMENT h_2 above half of spending model #1` | 0.04940556087 | 0.04951970362 | 0.997695 |
| `MOMENT h_3 share in the largest unit model #1` | 0.6702232058 | 0.6779071092 | 0.988665 |
| `DIAG unit 0 share of renters #1` | 0.1206637515 | 0.1155274104 | 1.04446 |
| `DIAG unit 1 share of renters #1` | 0.2091130427 | 0.2065654804 | 1.01233 |
| `DIAG unit 2 share of renters #1` | 0.6702232058 | 0.6779071092 | 0.988665 |
| `DIAG unit 2 share of renters #2` | 0.3812031983 | 0.3491025305 | 1.09195 |
| `DIAG aggregate rent / aggregate income #1` | 0.2074195227 | 0.2100293316 | 0.987574 |
| `DIAG aggregate housing / aggregate expenditure #1` | 0.1866914445 | 0.1851122729 | 1.00853 |
| `DIAG over half of EXPENDITURE, all households #1` | 0.04940556087 | 0.04951970362 | 0.997695 |
| `DIAG over half of EXPENDITURE, housed only #1` | 0.04959970705 | 0.049744162 | 0.997096 |
| `UNTARGETED mean age of drug users model #1` | 68.42868494 | 67.37512857 | 1.01564 |
| `UNTARGETED users aged 26-34, share model #1` | 0.07282768292 | 0.1119656138 | 0.650447 |
| `UNTARGETED users aged 35-44, share model #1` | 0.04182028143 | 0.02454054323 | 1.70413 |
| `UNTARGETED users aged 45-54, share model #1` | 0.04905709415 | 0.03968474968 | 1.23617 |
| `UNTARGETED users aged 55-64, share model #1` | 0.1362097834 | 0.1343861682 | 1.01357 |
| `UNTARGETED users aged 65 plus, share model #1` | 0.7000851581 | 0.6894229251 | 1.01547 |
| `DIAG income of WORKING AGE drug users / average #1` | 0.1890373048 | 0.2124225618 | 0.889912 |
| `DIAG working age share of drug users #1` | 0.3136040546 | 0.3242655347 | 0.967121 |
| `DIAG users band 1 use rate #1` | 0.01020895587 | 0.01571162061 | 0.649771 |
| `DIAG users band 1 use rate #2` | 0.2798909502 | 0.114246535 | 2.44989 |
| `DIAG users band 1 use rate #3` | 0.203012264 | 0.2968295173 | 0.683936 |
| `DIAG users band 2 use rate #1` | 0.005350268754 | 0.003142383586 | 1.70261 |
| `DIAG users band 2 use rate #2` | 0.9396402451 | 0.9105290037 | 1.03197 |
| `DIAG users band 2 use rate #3` | 0.3204246511 | 0.3371893962 | 0.950281 |
| `DIAG users band 3 use rate #1` | 0.006457736906 | 0.005226923755 | 1.23548 |
| `DIAG users band 3 use rate #2` | 0.4835181202 | 0.3354327783 | 1.44148 |
| `DIAG users band 3 use rate #3` | 0.2107387189 | 0.182785533 | 1.15293 |
| `DIAG users band 4 use rate #1` | 0.01908656547 | 0.01884540846 | 1.0128 |
| `DIAG users band 4 use rate #2` | 0.08395166927 | 0.07247265538 | 1.15839 |
| `DIAG users band 4 use rate #3` | 0.1385104019 | 0.135652063 | 1.02107 |
| `DIAG users band 5 use rate #1` | 0.0640602071 | 0.063132533 | 1.01469 |
| `DIAG users band 5 use rate #2` | 0.2792510733 | 0.2794466608 | 0.9993 |
| `DIAG users band 5 use rate #3` | 0.1875336757 | 0.18740319 | 1.0007 |
| `DIAG buyers: mean C #1` | 0.1333450623 | 0.1362336432 | 0.978797 |
| `DIAG non-buyers: mean C #1` | 0.3967883217 | 0.3966754663 | 1.00028 |
| `DIAG buyers: mean income #1` | 0.08485121051 | 0.09379019927 | 0.904692 |
| `DIAG non-buyers: mean income #1` | 0.508496131 | 0.5059498946 | 1.00503 |
| `DIAG buyers as a share of clean households #1` | 0.01760019461 | 0.01857629687 | 0.947454 |
| `DIAG assets of drug users / average net worth #1` | 0.2079014253 | 0.1993837881 | 1.04272 |
| `DIAG assets of experimenters / average net worth #1` | 0.2190489153 | 0.2144169736 | 1.0216 |
| `DIAG assets with a SUD / average net worth #1` | 0.1806535674 | 0.366187141 | 0.493337 |
| `DIAG mass with a NEGATIVE value of life #1` | 0.5714241616 | 1.147730787 | 0.497873 |
| `DIAG value of life, drug users #1` | 16.89742996 | 16.46415598 | 1.02632 |
| `DIAG value of life, everyone else #1` | 18.68946891 | 18.69183424 | 0.999873 |
| `DIAG treatment price / average labour income #1` | 0.1006946494 | 0.005829414074 | 17.2735 |
| `DIAG households receiving food stamps #1` | 1.546134745 | 3.131991919 | 0.493659 |
| `DIAG aggregate rent / output #1` | 0.2406934296 | 0.2435526295 | 0.98826 |
| `DIAG share in the smallest unit #1` | 0.1206637515 | 0.1155274104 | 1.04446 |
| `MOMENT gamma housing over expenditure model #1` | 0.1866914445 | 0.1851122729 | 1.00853 |
| `UNTARGETED housing over income, renters model #1` | 0.2523734712 | 0.2530672983 | 0.997258 |
| `MOMENT h_1 homelessness rate model #1` | 0.0039142606 | 0.004512255905 | 0.867473 |
| `MOMENT b total drug users model #1` | 0.02462338653 | 0.02463741848 | 0.99943 |
| `MOMENT lambda_d disorder rate model #1` | 0.007149015988 | 0.006180158023 | 1.15677 |
| `MOMENT theta drug spending share model #1` | 0.2570791252 | -1 | -0.257079 |
| `MOMENT aleph value of life / income model #1` | 1.128320071 | 0.06520200828 | 17.305 |
| `MOMENT pi_eu unemployment rate model #1` | 0.05298364856 | 0.05279566072 | 1.00356 |
| `MOMENT kappa_ued unemployment given SUD model #1` | 0.102821319 | 0.09579811092 | 1.07331 |
| `MOMENT kappa_uem employment given SMI model #1` | 0.3018190619 | 0.3024182817 | 0.998019 |
| `MOMENT p_m SMI population share model #1` | 0.04398400643 | 0.04397984627 | 1.00009 |
| `MOMENT p_m SMI population share model #2` | 0.04820668218 | 0.04820280192 | 1.00008 |
| `MOMENT lambda_m SMI share of the homeless model #1` | 0.2331997728 | 0.165347038 | 1.41037 |
| `MOMENT pi_V eligibles with a voucher model #1` | 0.2899231422 | 0.1137811654 | 2.54808 |
| `MOMENT cbar food stamps / labour income model #1` | 0.0002198308526 | 1.289228428e-05 | 17.0514 |
| `MOMENT tau_u treatment take up model #1` | 0.08382140638 | 0.06470493699 | 1.29544 |
| `MOMENT mu_H recovery housed / homeless model #1` | 1.405875595 | 1.384914385 | 1.01514 |
| `UNTARGETED delta_d child SUD ratio model #1` | 1.962684928 | 2.083383171 | 0.942066 |
| `UNTARGETED wealth share bottom 5 pct model #1` | 0.0003358111747 | 0.0003319074085 | 1.01176 |
| `UNTARGETED wealth share bottom 10 pct model #1` | 0.00299625339 | 0.00302718099 | 0.989783 |
| `UNTARGETED income share bottom 1 pct model #1` | 0.0006904095505 | 0.0006939138509 | 0.99495 |
| `UNTARGETED income share bottom 5 pct model #1` | 0.003452047752 | 0.003469569255 | 0.99495 |
| `UNTARGETED income share bottom 10 pct model #1` | 0.008681035567 | 0.008523595527 | 1.01847 |
| `DIAG income histogram mass / distribution (want 1.0) #1` | 1 | 0.9997721849 | 1.00023 |
| `DIAG SUD rate, income band 1 model #1` | 0.02162831969 | 0.02046593974 | 1.0568 |
| `DIAG SUD rate, income band 2 model #1` | 0.01598186721 | 0.01083173355 | 1.47547 |
| `DIAG SUD rate, income band 3 model #1` | 0.00240213056 | 0.001397345614 | 1.71907 |
| `DIAG SUD rate, income band 4 model #1` | 0.001893112051 | 0.001724494032 | 1.09778 |
| `DIAG SUD rate, income band 5 model #1` | 0.0001815628035 | 0.0006339495309 | 0.286399 |
| `DIAG SUD rate, income band 6 model #1` | 2.556361667e-08 | 2.482779687e-05 | 0.00102964 |
| `DIAG SUD rate, income band 7 model #1` | 0 | 3.414511975e-08 | 0 |
| `UNTARGETED delta_h child homelessness ratio model #1` | 2.217883635 | 2.153336498 | 1.02998 |
| `DIAG homelessness rate rebuilt from the bands #1` | 0.0039142606 | 0.004512255905 | 0.867473 |
| `UNTARGETED homelessness rate, band 1 model #1` | 0.02180529669 | 0.02521170494 | 0.864888 |
| `UNTARGETED homelessness rate, band 2 model #1` | 0.0002760650854 | 0.0002815051579 | 0.980675 |
| `UNTARGETED homelessness rate, band 3 model #1` | 7.707051391e-05 | 7.61240523e-05 | 1.01243 |
| `UNTARGETED homelessness rate, band 4 model #1` | 8.51324577e-05 | 8.423643927e-05 | 1.01064 |
| `UNTARGETED homelessness rate, band 5 model #1` | 5.64793891e-06 | 5.646438637e-06 | 1.00027 |
| `UNTARGETED homelessness profile, band 1 model #1` | 5.570731978 | 5.587383666 | 0.99702 |
| `UNTARGETED homelessness profile, band 2 model #1` | 0.07052802908 | 0.06238678917 | 1.1305 |
| `UNTARGETED homelessness profile, band 3 model #1` | 0.01968967368 | 0.01687050865 | 1.16711 |
| `UNTARGETED homelessness profile, band 4 model #1` | 0.02174930757 | 0.01866836479 | 1.16504 |
| `UNTARGETED homelessness profile, band 5 model #1` | 0.001442913359 | 0.00125135603 | 1.15308 |
| `DIAG disorder rate, band 1 #1` | 0.00285739436 | 0.001794998214 | 1.59186 |
| `DIAG disorder rate, band 2 #1` | 0.005027327843 | 0.002861231396 | 1.75705 |
| `DIAG disorder rate, band 3 #1` | 0.003122432809 | 0.001753281557 | 1.78091 |
| `DIAG disorder rate, band 4 #1` | 0.001602349032 | 0.001365776793 | 1.17321 |
| `DIAG disorder rate, band 5 #1` | 0.01788888159 | 0.01764217553 | 1.01398 |
| `DIAG SUD share of the homeless, band 1 #1` | 0.0002177378809 | 9.416108301e-05 | 2.3124 |
| `DIAG SUD share of the homeless, band 2 #1` | 0.00636289498 | 0.003119558302 | 2.03968 |
| `DIAG SUD share of the homeless, band 3 #1` | 0.0007036457607 | 0.0003835400898 | 1.83461 |
| `DIAG SUD share of the homeless, band 4 #1` | 0.001492500498 | 0.001507404474 | 0.990113 |
| `UNTARGETED share of the homeless, band 1 model #1` | 0.9785324053 | 0.9812198515 | 0.997261 |
| `UNTARGETED share of the homeless, band 2 model #1` | 0.01357440752 | 0.01200637101 | 1.1306 |
| `UNTARGETED share of the homeless, band 3 model #1` | 0.003683051344 | 0.003156456493 | 1.16683 |
| `UNTARGETED share of the homeless, band 4 model #1` | 0.00382185084 | 0.003280571027 | 1.165 |
| `UNTARGETED share of the homeless, band 5 model #1` | 0.0003882849603 | 0.0003367499559 | 1.15304 |
| `MOMENT w_bot net worth share, bottom half model #1` | 0.1571600243 | 0.1551140646 | 1.01319 |
| `UNTARGETED renters above 30 pct of income model #1` | 0.4174390245 | 0.7941856352 | 0.525619 |
| `UNTARGETED renters above 50 pct of income model #1` | 0.2554912297 | 0.4734946472 | 0.539586 |
| `UNTARGETED tenant contribution rate model #1` | 0.4696273473 | 0.3754713056 | 1.25077 |
| `UNTARGETED voucher holders, wages main model #1` | 0.4898475147 | 0.4971236563 | 0.985364 |
| `UNTARGETED participation, with a SUD model #1` | 0.3292920471 | 0.2350855204 | 1.40073 |
| `UNTARGETED participation, without a SUD model #1` | 0.7505385356 | 0.7507000012 | 0.999785 |
| `DIAG households with no wage income, working age #1` | 0.05298364856 | 0.05279566072 | 1.00356 |
| `UNTARGETED SMI alongside SUD at admission model #1` | 0.008849151501 | 0.008601708993 | 1.02877 |
| `DIAG employed share of the homeless, working age #1` | 0.9769542087 | 0.9828905293 | 0.99396 |
| `DIAG working age homeless mass #1` | 0.1995028925 | 0.460071761 | 0.433634 |
| `UNTARGETED SUD share of the homeless model #1` | 0.0003078604034 | 0.0001361146212 | 2.26177 |
| `UNTARGETED drug deaths, share of deaths model #1` | 0.02619879981 | 0.01541931168 | 1.69909 |
| `UNTARGETED income of the homeless model #1` | 0.2755197676 | 0.497909454 | 0.553353 |
| `UNTARGETED employed share of the homeless model #1` | 0.9769542087 | 0.9828905293 | 0.99396 |
| `DIAG homeless who could afford it on INCOME ALONE #1` | 0.9356896519 | 1.655156538 | 0.565318 |
| `DIAG homeless by choice, share of the homeless #1` | 0.9357263219 | 1.655212847 | 0.565321 |
| `DIAG homeless receiving food stamps #1` | 0.004984206496 | 0.009009723096 | 0.553203 |
| `DIAG average assets of the homeless #1` | 0.02114955967 | 0.05158894442 | 0.409963 |
| `DIAG wealth share of the bottom 25 pct #1` | 0.03153353652 | 0.0313835411 | 1.00478 |
| `DIAG mean drug quantity, users #1` | 0.03071836087 | 0.02614582901 | 1.17489 |
| `DIAG onset at the mean quantity #1` | 0.4474039023 | 0.3963971504 | 1.12868 |
| `MOMENT y_u income of drug users model #1` | 0.1886794059 | 0.1961931246 | 0.961702 |
| `UNTARGETED income with a SUD model #1` | 0.2300543449 | 0.5161332057 | 0.445727 |
| `DIAG carriers of the disorder consuming no drugs #1` | 0.005455249956 | 0.01180222 | 0.462222 |
| `DIAG income of experimenters / average #1` | 0.1554936974 | 0.172872487 | 0.89947 |
| `DIAG income of drug users / labour income #1` | 0.1725905721 | 0.01032954495 | 16.7084 |
| `DIAG income with a SUD / labour income #1` | 0.2104374391 | 0.02717435261 | 7.74397 |
| `DIAG mass ON the top savings grid point #1` | 0.0001438728056 | 0.0002718876055 | 0.529163 |
| `DIAG mass in the top THREE savings grid points #1` | 0.0006273505055 | 0.001232093913 | 0.509174 |
| `DIAG histogram mass / distribution (want 1.0) #1` | 1 | 0.9997721849 | 1.00023 |
| `DIAG age 26 homeless #1` | 0.152777 | 0.149182 | 1.0241 |
| `DIAG age 26 homeless #4` | -0.03514 | -0.03539 | 0.992936 |
| `DIAG age 29 homeless #1` | 0.004066 | 0.005387 | 0.75478 |
| `DIAG age 29 homeless #3` | 0.31243 | 0.312 | 1.00138 |
| `DIAG age 29 homeless #4` | -0.02039 | -0.01948 | 1.04671 |
| `DIAG age 32 homeless #1` | 0.001285 | 0.001359 | 0.945548 |
| `DIAG age 32 homeless #3` | 0.55313 | 0.54695 | 1.0113 |
| `DIAG age 32 homeless #4` | -0.01086 | -0.01036 | 1.04826 |
| `DIAG age 35 homeless #1` | 0.000525 | 0.000549 | 0.956284 |
| `DIAG age 35 homeless #3` | 0.79471 | 0.78132 | 1.01714 |
| `DIAG age 35 homeless #4` | -0.00113 | -0.00087 | 1.29885 |
| `DIAG age 38 homeless #1` | 0.000332 | 0.00034 | 0.976471 |
| `DIAG age 38 homeless #3` | 1.05411 | 1.03415 | 1.0193 |
| `DIAG age 38 homeless #4` | 0.00939 | 0.00936 | 1.00321 |
| `DIAG age 41 homeless #1` | 0.000174 | 0.000178 | 0.977528 |
| `DIAG age 41 homeless #3` | 1.31516 | 1.29102 | 1.0187 |
| `DIAG age 41 homeless #4` | 0.01969 | 0.01945 | 1.01234 |
| `DIAG age 44 homeless #1` | 0.000109 | 0.0001 | 1.09 |
| `DIAG age 44 homeless #3` | 1.58142 | 1.55169 | 1.01916 |
| `DIAG age 44 homeless #4` | 0.02947 | 0.02913 | 1.01167 |
| `DIAG age 47 homeless #1` | 6.6e-05 | 6.8e-05 | 0.970588 |
| `DIAG age 47 homeless #3` | 1.84234 | 1.80977 | 1.018 |
| `DIAG age 47 homeless #4` | 0.03828 | 0.03787 | 1.01083 |
| `DIAG age 50 homeless #1` | 8.6e-05 | 8.8e-05 | 0.977273 |
| `DIAG age 50 homeless #3` | 2.0945 | 2.05702 | 1.01822 |
| `DIAG age 50 homeless #4` | 0.04606 | 0.04551 | 1.01209 |
| `DIAG age 53 homeless #1` | 7e-05 | 6.7e-05 | 1.04478 |
| `DIAG age 53 homeless #3` | 2.32543 | 2.29483 | 1.01333 |
| `DIAG age 53 homeless #4` | 0.05222 | 0.05207 | 1.00288 |
| `DIAG age 56 homeless #1` | 6.4e-05 | 6.2e-05 | 1.03226 |
| `DIAG age 56 homeless #3` | 2.51179 | 2.48037 | 1.01267 |
| `DIAG age 56 homeless #4` | 0.05612 | 0.0559 | 1.00394 |
| `DIAG age 59 homeless #3` | 2.63623 | 2.60641 | 1.01144 |
| `DIAG age 59 homeless #4` | 0.05743 | 0.0573 | 1.00227 |
| `DIAG age 62 homeless #3` | 2.69017 | 2.66475 | 1.00954 |
| `DIAG age 62 homeless #4` | 0.05654 | 0.05651 | 1.00053 |
| `DIAG age 65 homeless #3` | 2.67229 | 2.64989 | 1.00845 |
| `DIAG age 65 homeless #4` | 0.05271 | 0.05281 | 0.998106 |
| `DIAG age 68 homeless #3` | 2.43073 | 2.4113 | 1.00806 |
| `DIAG age 68 homeless #4` | 0.62879 | 10.37773 | 0.0605903 |
| `DIAG age 71 homeless #3` | 2.05868 | 2.04239 | 1.00798 |
| `DIAG age 71 homeless #4` | 0.61763 | 10.36667 | 0.0595784 |
| `DIAG age 74 homeless #3` | 1.63659 | 1.62303 | 1.00835 |
| `DIAG age 74 homeless #4` | 0.60497 | 10.35394 | 0.058429 |
| `DIAG age 77 homeless #3` | 1.1826 | 1.1717 | 1.0093 |
| `DIAG age 77 homeless #4` | 0.59135 | 10.34 | 0.0571905 |
| `DIAG age 80 homeless #3` | 0.72861 | 0.72133 | 1.01009 |
| `DIAG age 80 homeless #4` | 0.57773 | 10.32355 | 0.0559623 |
| `DIAG age 83 homeless #3` | 0.33229 | 0.32837 | 1.01194 |
| `DIAG age 83 homeless #4` | 0.56584 | 10.29246 | 0.0549762 |

### Shape of the failure

- 46 within 1% of agreeing but outside 4 significant figures
- 68 between 1% and 10% out
- 7 near a factor of two either way
- 4 near a factor of **17**: `aleph` (17.30), `cbar` (17.05), `treatment price / average
  labour income` (17.27) and `income of drug users / labour income` (16.71). All four divide by
  a labour-income aggregate, which points at one shared denominator rather than four faults.

Two results stand apart from the ratio arithmetic:

- `MOMENT theta drug spending share` returns **-1.0** in the two-type run against 0.2571 in the
  one-type run. A negative share is a sentinel, not a quantity: that moment is not being
  computed at all when a second type is present.
- In the age block, `renter income` for ages 68-83 reads about **10.3** in the two-type run
  against about **0.6** in the one-type run, while ages 26-65 agree to roughly 1%. The break is
  exactly at retirement, and it is the same ~17x as the cluster above.

## (f) Invariants

**Not all ten pass.** The build emits eleven invariant checks plus a summary line. All eleven
pass in the one-type run. **Two fail in the two-type run.**

### One-type run -- all PASS

```
 INVARIANT PASS     income histogram holds the whole distribution  =     1.0000000000
 INVARIANT PASS     wealth histogram holds the whole distribution  =     1.0000000000
 INVARIANT PASS     wealth histogram holds the whole of net worth  =     1.0000000000
 INVARIANT PASS          rental market clears, demand over supply  =     1.0000000000
 INVARIANT PASS                                 homelessness rate  =     0.0039142606
 INVARIANT PASS                                        drug users  =     0.0246233865
 INVARIANT PASS                                     disorder rate  =     0.0071490160
 INVARIANT PASS                              SMI population share  =     0.0439840064
 INVARIANT PASS                                 unemployment rate  =     0.0529836486
 INVARIANT PASS                                homeownership rate  =     0.0000000000
 INVARIANT PASS       the five age bands hold all of the homeless  =     1.0000000000
 INVARIANTS: all PASS
```

### Two-type run -- 2 FAILED

```
 INVARIANT FAIL     income histogram holds the whole distribution  =     0.9997721849   want   1.0000
 INVARIANT FAIL     wealth histogram holds the whole distribution  =     0.9997721849   want   1.0000
 INVARIANT PASS     wealth histogram holds the whole of net worth  =     1.0000000000
 INVARIANT PASS          rental market clears, demand over supply  =     1.0000000000
 INVARIANT PASS                                 homelessness rate  =     0.0045122559
 INVARIANT PASS                                        drug users  =     0.0246374185
 INVARIANT PASS                                     disorder rate  =     0.0061801580
 INVARIANT PASS                              SMI population share  =     0.0439798463
 INVARIANT PASS                                 unemployment rate  =     0.0527956607
 INVARIANT PASS                                homeownership rate  =     0.0000000000
 INVARIANT PASS       the five age bands hold all of the homeless  =     1.0000000000
 INVARIANTS:            2  FAILED -- see the lines above
```

The two failures, quoted verbatim:

```
INVARIANT FAIL     income histogram holds the whole distribution  =     0.9997721849   want   1.0000
INVARIANT FAIL     wealth histogram holds the whole distribution  =     0.9997721849   want   1.0000
INVARIANTS:            2  FAILED -- see the lines above
```

Both are the same shortfall, 0.9997721849 against 1.0 -- the histograms are losing 2.28e-4 of
the distribution when a second type is present. The one-type run holds both at 1.0000000000.

## (g) DIAG age block, two-type run

```
DIAG age  26  homeless=  0.149182  own=  0.00000  renter wealth=    0.00000  renter income=   -0.03539
DIAG age  29  homeless=  0.005387  own=  0.00000  renter wealth=    0.31200  renter income=   -0.01948
DIAG age  32  homeless=  0.001359  own=  0.00000  renter wealth=    0.54695  renter income=   -0.01036
DIAG age  35  homeless=  0.000549  own=  0.00000  renter wealth=    0.78132  renter income=   -0.00087
DIAG age  38  homeless=  0.000340  own=  0.00000  renter wealth=    1.03415  renter income=    0.00936
DIAG age  41  homeless=  0.000178  own=  0.00000  renter wealth=    1.29102  renter income=    0.01945
DIAG age  44  homeless=  0.000100  own=  0.00000  renter wealth=    1.55169  renter income=    0.02913
DIAG age  47  homeless=  0.000068  own=  0.00000  renter wealth=    1.80977  renter income=    0.03787
DIAG age  50  homeless=  0.000088  own=  0.00000  renter wealth=    2.05702  renter income=    0.04551
DIAG age  53  homeless=  0.000067  own=  0.00000  renter wealth=    2.29483  renter income=    0.05207
DIAG age  56  homeless=  0.000062  own=  0.00000  renter wealth=    2.48037  renter income=    0.05590
DIAG age  59  homeless=  0.000076  own=  0.00000  renter wealth=    2.60641  renter income=    0.05730
DIAG age  62  homeless=  0.000093  own=  0.00000  renter wealth=    2.66475  renter income=    0.05651
DIAG age  65  homeless=  0.000078  own=  0.00000  renter wealth=    2.64989  renter income=    0.05281
DIAG age  68  homeless=  0.000000  own=  0.00000  renter wealth=    2.41130  renter income=   10.37773
DIAG age  71  homeless=  0.000000  own=  0.00000  renter wealth=    2.04239  renter income=   10.36667
DIAG age  74  homeless=  0.000000  own=  0.00000  renter wealth=    1.62303  renter income=   10.35394
DIAG age  77  homeless=  0.000000  own=  0.00000  renter wealth=    1.17170  renter income=   10.34000
DIAG age  80  homeless=  0.000000  own=  0.00000  renter wealth=    0.72133  renter income=   10.32355
DIAG age  83  homeless=  0.000000  own=  0.00000  renter wealth=    0.32837  renter income=   10.29246
```

For reference, the same block from the one-type run:

```
DIAG age  26  homeless=  0.152777  own=  0.00000  renter wealth=    0.00000  renter income=   -0.03514
DIAG age  29  homeless=  0.004066  own=  0.00000  renter wealth=    0.31243  renter income=   -0.02039
DIAG age  32  homeless=  0.001285  own=  0.00000  renter wealth=    0.55313  renter income=   -0.01086
DIAG age  35  homeless=  0.000525  own=  0.00000  renter wealth=    0.79471  renter income=   -0.00113
DIAG age  38  homeless=  0.000332  own=  0.00000  renter wealth=    1.05411  renter income=    0.00939
DIAG age  41  homeless=  0.000174  own=  0.00000  renter wealth=    1.31516  renter income=    0.01969
DIAG age  44  homeless=  0.000109  own=  0.00000  renter wealth=    1.58142  renter income=    0.02947
DIAG age  47  homeless=  0.000066  own=  0.00000  renter wealth=    1.84234  renter income=    0.03828
DIAG age  50  homeless=  0.000086  own=  0.00000  renter wealth=    2.09450  renter income=    0.04606
DIAG age  53  homeless=  0.000070  own=  0.00000  renter wealth=    2.32543  renter income=    0.05222
DIAG age  56  homeless=  0.000064  own=  0.00000  renter wealth=    2.51179  renter income=    0.05612
DIAG age  59  homeless=  0.000076  own=  0.00000  renter wealth=    2.63623  renter income=    0.05743
DIAG age  62  homeless=  0.000093  own=  0.00000  renter wealth=    2.69017  renter income=    0.05654
DIAG age  65  homeless=  0.000078  own=  0.00000  renter wealth=    2.67229  renter income=    0.05271
DIAG age  68  homeless=  0.000000  own=  0.00000  renter wealth=    2.43073  renter income=    0.62879
DIAG age  71  homeless=  0.000000  own=  0.00000  renter wealth=    2.05868  renter income=    0.61763
DIAG age  74  homeless=  0.000000  own=  0.00000  renter wealth=    1.63659  renter income=    0.60497
DIAG age  77  homeless=  0.000000  own=  0.00000  renter wealth=    1.18260  renter income=    0.59135
DIAG age  80  homeless=  0.000000  own=  0.00000  renter wealth=    0.72861  renter income=    0.57773
DIAG age  83  homeless=  0.000000  own=  0.00000  renter wealth=    0.33229  renter income=    0.56584
```

**The age profile did not double -- and that is the correct outcome.** The brief anticipated
roughly doubled numbers against an earlier point, on the reasoning that the mass had been
divided by three times one type's mass instead of two. Against *this* one-type run the
`homeless`, `own` and `renter wealth` columns agree to about 1%, which is what two identical
copies should give: the profile is a per-capita rate, so it must match, not double. The
over-division by three has been corrected without introducing a doubling here.

The exception is `renter income` from age 68 on, which is 17x too large, as noted above. Ages
26 through 65 track the one-type run to about 1%.

## Summary

The seventeen fixes changed the *character* of the failure without closing it. The clean
factor-of-two signature is gone -- `tau_l` moved from 0.497 to 0.9975, and only 7 of 189
disagreements remain near a factor of two. The 187-normalisation fix is visibly real: the age
profile now reproduces instead of being divided by three.

But the count went **up**, from 135 of 242 to 188 of 237, and the two runs are further
from machine precision than that framing suggests, because most of the remaining gaps are small
and diffuse rather than structural. Two invariants now fail that did not before, `theta` returns
a sentinel, and a labour-income denominator is off by 17x. Aggregation over types is still not
measure-preserving.

Reproduce with `code/VALIDATE3.txt` lines 1 and 2 under `freeze_beta_bisection=1`.
