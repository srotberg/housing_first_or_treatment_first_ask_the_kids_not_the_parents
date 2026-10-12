# Two-pass vs one-pass measurement at the same parameter vector

## Verdict: **FAIL**

**Not every moment agrees to 4 significant figures.** 135 of 238 compared fields differ by more than 4 significant figures, including 23 of the 46 `MOMENT` fields and 73 of the 100 `DIAG` fields.

### What was compared

Both runs use the identical 28-parameter vector in `code/VALIDATE.txt`, in which the two discount factors are set equal (`discount_factor=0.99715`, `discount_factor_impatient=0.99715`). The only difference between the runs is

```fortran
integer, parameter :: number_of_beta_types=2   ! two-pass, code/points/point_110278961e_twobeta_equal.txt
integer, parameter :: number_of_beta_types=1   ! one-pass, code/points/point_110278961e_onebeta.txt
```

With the two discount factors equal, the two-type population is two identical copies of the one-type population, so every moment should reproduce to machine precision. They do not.

### Corroborating signals

- Every field that is a fixed input (`target=`, `data=`, `observed=`) reproduces **exactly**, with one exception noted below. The parse is therefore sound and every disagreement below is a model-generated quantity.
- The single exception is `MOMENT p_m SMI population share | target`, which agrees only to 3.8 s.f. That "target" is itself endogenous, so it is a genuine disagreement rather than a parsing artefact.
- A large cluster of ratios sits at almost exactly **0.5** or **2.0**, concentrated in mass-valued diagnostics (`working age homeless mass` 0.485, `mass ON the top savings grid point` 0.501, `mass in the top THREE savings grid points` 0.502, `mass with a NEGATIVE value of life` 0.494, `MOMENT tau_l average labour income tax` 2.012, `MOMENT pi_eu unemployment rate` 1.963). This is the signature of the two type-blocks each carrying full population weight instead of one half each, i.e. the weights across beta types not summing to one.
- Not all of the disagreement is a clean factor of two: `MOMENT tau_u treatment take up` differs by 11.1x, `DIAG users band 1 use rate | share with the disorder` by 11.0x and `UNTARGETED drug deaths, share of deaths` by 6.4x, so behaviour diverges as well as scale.
- The two-pass run also emits a runaway print: `DIAG SUD rate, income band 7` is written **365 times** (lines 83-447 of the two-pass file) with an unadvancing band index, against a single, correctly indexed pass over bands 1-7 in the one-pass file. The band-7 model value is 0.0 in both. This is a loop-bound or index bug in the two-type path and is consistent with the numerical disagreement.

### The three `want 1.0` diagnostics

These are internal consistency checks and they **pass in both runs** — the disagreement is not a failure of the distribution to integrate to one.

Two-pass (`point_110278961e_twobeta_equal.txt`):

```
 DIAG income histogram mass / distribution (want 1.0) =   1.0000203305734687     
 DIAG histogram mass / distribution  (want 1.0)   =   1.0000203305734781     
 DIAG histogram wealth / total wealth (want 1.0)  =   1.0000000000001881     
```

One-pass (`point_110278961e_onebeta.txt`):

```
 DIAG income histogram mass / distribution (want 1.0) =   1.0000000000000819     
 DIAG histogram mass / distribution  (want 1.0)   =   1.0000000000000850     
 DIAG histogram wealth / total wealth (want 1.0)  =   1.0000000000001046     
```

The two-pass histogram-mass checks are off by 2.0e-5 where the one-pass ones are off by 8.5e-14, so the two-type distribution is very slightly less well integrated, but both are within tolerance and neither explains disagreements of 2x and more.

---

## Fields that do NOT agree to 4 significant figures (135)

| name | two-pass | one-pass | ratio (one/two) | matching s.f. | verdict |
|---|---|---|---|---|---|
| `MOMENT tau_l average labour income tax model` | 0.118083553684 | 0.237619975462 | 2.012304 | 0.3 | **DIFFERS** |
| `MOMENT omega_l labour supply / total hours model` | 0.402677809847 | 0.401142109073 | 0.996186 | 2.4 | **DIFFERS** |
| `MOMENT beta wealth over output model` | 4.04758267909 | 4.01214825459 | 0.991246 | 2.1 | **DIFFERS** |
| `MOMENT h_2 above half of spending model` | 0.0524160920162 | 0.0494055842017 | 0.942565 | 1.2 | **DIFFERS** |
| `MOMENT h_3 share in the largest unit model` | 0.675884490171 | 0.670223267812 | 0.991624 | 2.1 | **DIFFERS** |
| `DIAG unit 0 share of renters` | 0.118540326738 | 0.120663656643 | 1.017912 | 1.8 | **DIFFERS** |
| `DIAG unit 1 share of renters` | 0.20835051071 | 0.209113075545 | 1.003660 | 2.4 | **DIFFERS** |
| `DIAG unit 2 share of renters` | 0.673109162552 | 0.670223267812 | 0.995713 | 2.4 | **DIFFERS** |
| `DIAG unit 2 share of renters \| of whom over half of income` | 0.408596138465 | 0.381203203285 | 0.932958 | 1.2 | **DIFFERS** |
| `DIAG aggregate rent / aggregate income` | 0.20827633691 | 0.207419534792 | 0.995886 | 2.4 | **DIFFERS** |
| `DIAG aggregate housing / aggregate expenditure` | 0.191618432632 | 0.186691449299 | 0.974288 | 1.6 | **DIFFERS** |
| `DIAG over half of EXPENDITURE, all households` | 0.0524160920162 | 0.0494055842017 | 0.942565 | 1.2 | **DIFFERS** |
| `DIAG over half of EXPENDITURE, housed only` | 0.0526286556337 | 0.0495997305252 | 0.942447 | 1.2 | **DIFFERS** |
| `UNTARGETED mean age of drug users model` | 65.7150180704 | 68.4287456349 | 1.041295 | 1.4 | **DIFFERS** |
| `UNTARGETED users aged 26-34, share model` | 0.162128249067 | 0.0728279522325 | 0.449200 | 0.3 | **DIFFERS** |
| `UNTARGETED users aged 35-44, share model` | 0.00795561060672 | 0.0418198671258 | 5.256651 | 0.1 | **DIFFERS** |
| `UNTARGETED users aged 45-54, share model` | 0.0418165979219 | 0.0490572677057 | 1.173153 | 0.8 | **DIFFERS** |
| `UNTARGETED users aged 55-64, share model` | 0.122989772928 | 0.136206422339 | 1.107461 | 1.0 | **DIFFERS** |
| `UNTARGETED users aged 65 plus, share model` | 0.665109769476 | 0.700088490597 | 1.052591 | 1.3 | **DIFFERS** |
| `DIAG income of WORKING AGE drug users / average` | 0.332529188669 | 0.163365811063 | 0.491283 | 0.3 | **DIFFERS** |
| `DIAG working age share of drug users` | 0.346833524738 | 0.31360077051 | 0.904182 | 1.0 | **DIFFERS** |
| `DIAG users band 1 use rate` | 0.0128128151852 | 0.0102089558742 | 0.796777 | 0.7 | **DIFFERS** |
| `DIAG users band 1 use rate \| share with the disorder` | 0.0255166616571 | 0.279890950229 | 10.968949 | 0.0 | **DIFFERS** |
| `DIAG users band 1 use rate \| income/average` | 0.508405553322 | 0.188113192745 | 0.370006 | 0.2 | **DIFFERS** |
| `DIAG users band 2 use rate` | 0.000573713447969 | 0.00535019642044 | 9.325555 | 0.0 | **DIFFERS** |
| `DIAG users band 2 use rate \| share with the disorder` | 0.558132443089 | 0.939639423882 | 1.683542 | 0.4 | **DIFFERS** |
| `DIAG users band 2 use rate \| income/average` | 0.127567235508 | 0.286558132999 | 2.246330 | 0.3 | **DIFFERS** |
| `DIAG users band 3 use rate` | 0.00310184008585 | 0.0064577354611 | 2.081905 | 0.3 | **DIFFERS** |
| `DIAG users band 3 use rate \| share with the disorder` | 0.0688639349206 | 0.483518037456 | 7.021354 | 0.1 | **DIFFERS** |
| `DIAG users band 3 use rate \| income/average` | 0.137855310951 | 0.183977174907 | 1.334567 | 0.6 | **DIFFERS** |
| `DIAG users band 4 use rate` | 0.009710500269 | 0.0190860481362 | 1.965506 | 0.3 | **DIFFERS** |
| `DIAG users band 4 use rate \| share with the disorder` | 0.0344855332177 | 0.0839175436916 | 2.433413 | 0.2 | **DIFFERS** |
| `DIAG users band 4 use rate \| income/average` | 0.192857333694 | 0.11104115715 | 0.575768 | 0.4 | **DIFFERS** |
| `DIAG users band 5 use rate` | 0.0343465010981 | 0.0640602581614 | 1.865117 | 0.3 | **DIFFERS** |
| `DIAG users band 5 use rate \| share with the disorder` | 0.281951209154 | 0.279251255267 | 0.990424 | 2.0 | **DIFFERS** |
| `DIAG users band 5 use rate \| income/average` | 0.335213892091 | 0.171929661676 | 0.512895 | 0.3 | **DIFFERS** |
| `DIAG buyers: mean C` | 0.130314611264 | 0.133344999067 | 1.023254 | 1.6 | **DIFFERS** |
| `DIAG non-buyers: mean C` | 0.393973868844 | 0.396788332461 | 1.007144 | 2.1 | **DIFFERS** |
| `DIAG buyers: mean income` | 0.0952142752408 | 0.0848511117176 | 0.891160 | 1.0 | **DIFFERS** |
| `DIAG non-buyers: mean income` | 0.506799738845 | 0.508528358579 | 1.003411 | 2.5 | **DIFFERS** |
| `DIAG buyers as a share of clean households` | 0.0222487379562 | 0.0176002327113 | 0.791067 | 0.7 | **DIFFERS** |
| `DIAG assets of drug users / average net worth` | 0.184766382778 | 0.20789982696 | 1.125204 | 1.0 | **DIFFERS** |
| `DIAG assets of experimenters / average net worth` | 0.204684404424 | 0.219048527298 | 1.070177 | 1.2 | **DIFFERS** |
| `DIAG assets with a SUD / average net worth` | 0.106675562598 | 0.180648463102 | 1.693438 | 0.4 | **DIFFERS** |
| `DIAG mass with a NEGATIVE value of life` | 1.15599838812 | 0.571424239599 | 0.494312 | 0.3 | **DIFFERS** |
| `DIAG value of life, drug users` | 16.0009468178 | 16.8973603446 | 1.056023 | 1.3 | **DIFFERS** |
| `DIAG value of life, everyone else` | 18.6464525672 | 18.6894690425 | 1.002307 | 2.6 | **DIFFERS** |
| `DIAG treatment price / average labour income` | 0.143131893162 | 0.100694643128 | 0.703509 | 0.5 | **DIFFERS** |
| `DIAG households receiving food stamps` | 1.54495399791 | 1.54613371483 | 1.000764 | 3.1 | **DIFFERS** |
| `DIAG aggregate rent / output` | 0.241989558636 | 0.240693441751 | 0.994644 | 2.3 | **DIFFERS** |
| `DIAG share in the smallest unit` | 0.116498263966 | 0.120663656643 | 1.035755 | 1.5 | **DIFFERS** |
| `MOMENT gamma housing over expenditure model` | 0.191618432632 | 0.186691449299 | 0.974288 | 1.6 | **DIFFERS** |
| `UNTARGETED housing over income, renters model` | 0.130727658637 | 0.25237347602 | 1.930529 | 0.3 | **DIFFERS** |
| `MOMENT h_1 homelessness rate model` | 0.00416361096546 | 0.00391426166076 | 0.940112 | 1.2 | **DIFFERS** |
| `MOMENT b total drug users model` | 0.0277659847163 | 0.0246232993171 | 0.886815 | 0.9 | **DIFFERS** |
| `MOMENT lambda_d disorder rate model` | 0.00289152546133 | 0.00714888871069 | 2.472359 | 0.2 | **DIFFERS** |
| `MOMENT theta drug spending share model` | 0.213183594569 | 0.256927041689 | 1.205191 | 0.8 | **DIFFERS** |
| `MOMENT aleph value of life / income model` | 162.001951919 | 57.5118230074 | 0.355007 | 0.2 | **DIFFERS** |
| `MOMENT pi_eu unemployment rate model` | 0.0269897996201 | 0.0529836262935 | 1.963098 | 0.3 | **DIFFERS** |
| `MOMENT kappa_ued unemployment given SUD model` | 0.429359916097 | 0.102819874513 | 0.239472 | 0.1 | **DIFFERS** |
| `MOMENT kappa_uem employment given SMI model` | 0.302412883835 | 0.301819111294 | 0.998037 | 2.7 | **DIFFERS** |
| `MOMENT p_m SMI population share model` | 0.0439884115778 | 0.0439840054712 | 0.999900 | 4.0 | **DIFFERS** |
| `MOMENT p_m SMI population share model \| target` | 0.0482152529807 | 0.0482066834481 | 0.999822 | 3.8 | **DIFFERS** |
| `MOMENT lambda_m SMI share of the homeless model` | 0.190696028985 | 0.233199746014 | 1.222887 | 0.7 | **DIFFERS** |
| `MOMENT pi_V eligibles with a voucher model` | 0.173046711622 | 0.271438578949 | 1.568586 | 0.4 | **DIFFERS** |
| `MOMENT cbar food stamps / labour income model` | 0.0157022313479 | 0.0112050364973 | 0.713595 | 0.5 | **DIFFERS** |
| `MOMENT tau_u treatment take up model` | 0.00757602768324 | 0.0838077278224 | 11.062226 | 0.0 | **DIFFERS** |
| `MOMENT mu_H recovery housed / homeless model` | 1.36460782452 | 1.40585784829 | 1.030228 | 1.5 | **DIFFERS** |
| `UNTARGETED delta_d child SUD ratio model` | 2.34732441477 | 1.96270393397 | 0.836145 | 0.8 | **DIFFERS** |
| `UNTARGETED wealth share bottom 5 pct model` | 0.000387357419005 | 0.000335809629857 | 0.866924 | 0.9 | **DIFFERS** |
| `UNTARGETED wealth share bottom 10 pct model` | 0.00303382550005 | 0.00299625184382 | 0.987615 | 1.9 | **DIFFERS** |
| `UNTARGETED income share bottom 1 pct model` | 0.000694427306624 | 0.000690409660167 | 0.994214 | 2.2 | **DIFFERS** |
| `UNTARGETED income share bottom 5 pct model` | 0.00347213653312 | 0.00345204830084 | 0.994214 | 2.2 | **DIFFERS** |
| `UNTARGETED income share bottom 10 pct model` | 0.0086070734459 | 0.00868103086231 | 1.008593 | 2.1 | **DIFFERS** |
| `DIAG SUD rate, income band 1 model` | 0.022372217484 | 0.021628248659 | 0.966746 | 1.5 | **DIFFERS** |
| `DIAG SUD rate, income band 2 model` | 0.011137966561 | 0.0159811813415 | 1.434838 | 0.5 | **DIFFERS** |
| `DIAG SUD rate, income band 3 model` | 0.00155579894621 | 0.00240202451272 | 1.543917 | 0.5 | **DIFFERS** |
| `DIAG SUD rate, income band 4 model` | 0.000987846000622 | 0.00189296025835 | 1.916250 | 0.3 | **DIFFERS** |
| `DIAG SUD rate, income band 5 model` | 0.000101568319427 | 0.000181550454017 | 1.787471 | 0.4 | **DIFFERS** |
| `DIAG SUD rate, income band 6 model` | 1.34009285703e-08 | 2.55636151561e-08 | 1.907600 | 0.3 | **DIFFERS** |
| `UNTARGETED delta_h child homelessness ratio model` | 2.21498263652 | 2.21788388832 | 1.001310 | 2.9 | **DIFFERS** |
| `DIAG homelessness rate rebuilt from the bands` | 0.0040389330657 | 0.00391426166076 | 0.969133 | 1.5 | **DIFFERS** |
| `UNTARGETED homelessness rate, band 1 model` | 0.0224978910385 | 0.0218052966936 | 0.969215 | 1.5 | **DIFFERS** |
| `UNTARGETED homelessness rate, band 2 model` | 0.000287849617328 | 0.000276065108101 | 0.959060 | 1.4 | **DIFFERS** |
| `UNTARGETED homelessness rate, band 3 model` | 8.00743346667e-05 | 7.70705107429e-05 | 0.962487 | 1.4 | **DIFFERS** |
| `UNTARGETED homelessness rate, band 4 model` | 8.48447854645e-05 | 8.51351217195e-05 | 1.003422 | 2.5 | **DIFFERS** |
| `UNTARGETED homelessness rate, band 5 model` | 5.55586232954e-06 | 5.64793757094e-06 | 1.016573 | 1.8 | **DIFFERS** |
| `UNTARGETED homelessness profile, band 2 model` | 0.071268726826 | 0.0705280157606 | 0.989607 | 2.0 | **DIFFERS** |
| `UNTARGETED homelessness profile, band 3 model` | 0.0198256156673 | 0.0196896675344 | 0.993143 | 2.2 | **DIFFERS** |
| `UNTARGETED homelessness profile, band 4 model` | 0.0210067322445 | 0.0217499822695 | 1.035382 | 1.5 | **DIFFERS** |
| `UNTARGETED homelessness profile, band 5 model` | 0.00137557672761 | 0.00144291262579 | 1.048951 | 1.3 | **DIFFERS** |
| `DIAG disorder rate, band 1` | 0.00175558268171 | 0.00285739436047 | 1.627605 | 0.4 | **DIFFERS** |
| `DIAG disorder rate, band 2` | 0.00283338113074 | 0.00502725548216 | 1.774296 | 0.4 | **DIFFERS** |
| `DIAG disorder rate, band 3` | 0.00177392756603 | 0.00312243157656 | 1.760180 | 0.4 | **DIFFERS** |
| `DIAG disorder rate, band 4` | 0.00113555951189 | 0.00160165427837 | 1.410454 | 0.5 | **DIFFERS** |
| `DIAG disorder rate, band 5` | 0.0186372418737 | 0.0178889075043 | 0.959847 | 1.4 | **DIFFERS** |
| `DIAG SUD share of the homeless, band 1` | 0.000108720676744 | 0.000217737880938 | 2.002727 | 0.3 | **DIFFERS** |
| `DIAG SUD share of the homeless, band 2` | 0.0031840767649 | 0.00636289280218 | 1.998348 | 0.3 | **DIFFERS** |
| `DIAG SUD share of the homeless, band 3` | 0.000674529040852 | 0.000703645744845 | 1.043166 | 1.4 | **DIFFERS** |
| `DIAG SUD share of the homeless, band 4` | 0.00152709499882 | 0.00149245570884 | 0.977317 | 1.6 | **DIFFERS** |
| `DIAG SUD share of the homeless, band 5` | 0.000358004525922 | 0.000331250179863 | 0.925268 | 1.1 | **DIFFERS** |
| `UNTARGETED share of the homeless, band 2 model` | 0.0137199252063 | 0.0135744059239 | 0.989394 | 2.0 | **DIFFERS** |
| `UNTARGETED share of the homeless, band 3 model` | 0.00371048116065 | 0.00368305100371 | 0.992607 | 2.1 | **DIFFERS** |
| `UNTARGETED share of the homeless, band 4 model` | 0.00369368750416 | 0.00382196514822 | 1.034729 | 1.5 | **DIFFERS** |
| `UNTARGETED share of the homeless, band 5 model` | 0.000369802548847 | 0.000388284926588 | 1.049979 | 1.3 | **DIFFERS** |
| `MOMENT w_bot net worth share, bottom half model` | 0.159292323968 | 0.157159982335 | 0.986614 | 1.9 | **DIFFERS** |
| `UNTARGETED renters above 30 pct of income model` | 0.433795510617 | 0.417439046709 | 0.962295 | 1.4 | **DIFFERS** |
| `UNTARGETED renters above 50 pct of income model` | 0.299607761653 | 0.255491256606 | 0.852752 | 0.8 | **DIFFERS** |
| `UNTARGETED tenant contribution rate model` | 0.739787448926 | 0.469627279049 | 0.634814 | 0.4 | **DIFFERS** |
| `UNTARGETED voucher holders, wages main model` | 0.477701216109 | 0.48984751113 | 1.025427 | 1.6 | **DIFFERS** |
| `UNTARGETED participation, with a SUD model` | 0.0804607395111 | 0.329278839314 | 4.092416 | 0.1 | **DIFFERS** |
| `UNTARGETED participation, without a SUD model` | 0.751846382421 | 0.75053846505 | 0.998260 | 2.8 | **DIFFERS** |
| `DIAG households with no wage income, working age` | 0.0527776913198 | 0.0529836262935 | 1.003902 | 2.4 | **DIFFERS** |
| `UNTARGETED SMI alongside SUD at admission model` | 0.00452225678841 | 0.00884927513948 | 1.956827 | 0.3 | **DIFFERS** |
| `DIAG employed share of the homeless, working age` | 0.931140972943 | 0.976954211288 | 1.049201 | 1.3 | **DIFFERS** |
| `DIAG working age homeless mass` | 0.411707051061 | 0.199502915449 | 0.484575 | 0.3 | **DIFFERS** |
| `UNTARGETED SUD share of the homeless model` | 0.00144187910114 | 0.000307860333977 | 0.213513 | 0.1 | **DIFFERS** |
| `UNTARGETED drug deaths, share of deaths model` | 0.00408742657055 | 0.0261984047804 | 6.409511 | 0.1 | **DIFFERS** |
| `UNTARGETED income of the homeless model` | 0.551929987156 | 0.274647415931 | 0.497613 | 0.3 | **DIFFERS** |
| `UNTARGETED employed share of the homeless model` | 0.931140972943 | 0.976954211288 | 1.049201 | 1.3 | **DIFFERS** |
| `DIAG homeless who could afford it on INCOME ALONE` | 0.924750477024 | 0.935689658712 | 1.011829 | 1.9 | **DIFFERS** |
| `DIAG homeless by choice, share of the homeless` | 0.92478998273 | 0.93572632876 | 1.011826 | 1.9 | **DIFFERS** |
| `DIAG homeless receiving food stamps` | 0.000104114725561 | 9.77847567438e-05 | 0.939202 | 1.2 | **DIFFERS** |
| `DIAG average assets of the homeless` | 0.0462887234058 | 0.0211495571489 | 0.456905 | 0.3 | **DIFFERS** |
| `DIAG wealth share of the bottom 25 pct` | 0.0319670651717 | 0.0315335177182 | 0.986438 | 1.9 | **DIFFERS** |
| `DIAG mean drug quantity, users` | 0.0205287432916 | 0.03071775178 | 1.496329 | 0.5 | **DIFFERS** |
| `DIAG onset at the mean quantity` | 0.327249591486 | 0.447397403421 | 1.367144 | 0.6 | **DIFFERS** |
| `MOMENT y_u income of drug users model` | 0.33587993171 | 0.170199635262 | 0.506728 | 0.3 | **DIFFERS** |
| `UNTARGETED income with a SUD model` | 0.3050776802 | 0.206146607688 | 0.675718 | 0.5 | **DIFFERS** |
| `DIAG carriers of the disorder consuming no drugs` | 0.0233934399947 | 0.00545526050983 | 0.233196 | 0.1 | **DIFFERS** |
| `DIAG income of experimenters / average` | 0.343736423816 | 0.155493508049 | 0.452363 | 0.3 | **DIFFERS** |
| `DIAG income of drug users / labour income` | 0.221685815371 | 0.155686583885 | 0.702285 | 0.5 | **DIFFERS** |
| `DIAG income with a SUD / labour income` | 0.201355865301 | 0.188568330837 | 0.936493 | 1.2 | **DIFFERS** |
| `DIAG mass ON the top savings grid point` | 0.000287019374393 | 0.00014387282807 | 0.501265 | 0.3 | **DIFFERS** |
| `DIAG mass in the top THREE savings grid points` | 0.00125075419105 | 0.000627350603494 | 0.501578 | 0.3 | **DIFFERS** |

---

## All `MOMENT` fields (46)

| name | two-pass | one-pass | ratio (one/two) | matching s.f. | verdict |
|---|---|---|---|---|---|
| `MOMENT sigma_y bottom half earnings share model` | 0.169050021402 | 0.169050021402 | 1.000000 | exact | ok |
| `MOMENT sigma_y bottom half earnings share model \| target` | 0.172 | 0.172 | 1.000000 | exact | ok |
| `MOMENT tau_l average labour income tax model` | 0.118083553684 | 0.237619975462 | 2.012304 | 0.3 | **DIFFERS** |
| `MOMENT tau_l average labour income tax model \| target` | 0.224000006914 | 0.224000006914 | 1.000000 | exact | ok |
| `MOMENT omega_l labour supply / total hours model` | 0.402677809847 | 0.401142109073 | 0.996186 | 2.4 | **DIFFERS** |
| `MOMENT omega_l labour supply / total hours model \| target` | 0.40000000596 | 0.40000000596 | 1.000000 | exact | ok |
| `MOMENT beta wealth over output model` | 4.04758267909 | 4.01214825459 | 0.991246 | 2.1 | **DIFFERS** |
| `MOMENT beta wealth over output model \| target` | 3 | 3 | 1.000000 | exact | ok |
| `MOMENT h_2 above half of spending model` | 0.0524160920162 | 0.0494055842017 | 0.942565 | 1.2 | **DIFFERS** |
| `MOMENT h_2 above half of spending model \| target` | 0.101 | 0.101 | 1.000000 | exact | ok |
| `MOMENT h_3 share in the largest unit model` | 0.675884490171 | 0.670223267812 | 0.991624 | 2.1 | **DIFFERS** |
| `MOMENT h_3 share in the largest unit model \| target` | 0.626723 | 0.626723 | 1.000000 | exact | ok |
| `MOMENT gamma housing over expenditure model` | 0.191618432632 | 0.186691449299 | 0.974288 | 1.6 | **DIFFERS** |
| `MOMENT gamma housing over expenditure model \| target` | 0.268000006676 | 0.268000006676 | 1.000000 | exact | ok |
| `MOMENT h_1 homelessness rate model` | 0.00416361096546 | 0.00391426166076 | 0.940112 | 1.2 | **DIFFERS** |
| `MOMENT h_1 homelessness rate model \| target` | 0.00399000011384 | 0.00399000011384 | 1.000000 | exact | ok |
| `MOMENT b total drug users model` | 0.0277659847163 | 0.0246232993171 | 0.886815 | 0.9 | **DIFFERS** |
| `MOMENT b total drug users model \| target` | 0.0890000015497 | 0.0890000015497 | 1.000000 | exact | ok |
| `MOMENT lambda_d disorder rate model` | 0.00289152546133 | 0.00714888871069 | 2.472359 | 0.2 | **DIFFERS** |
| `MOMENT lambda_d disorder rate model \| target` | 0.0368000008166 | 0.0368000008166 | 1.000000 | exact | ok |
| `MOMENT theta drug spending share model` | 0.213183594569 | 0.256927041689 | 1.205191 | 0.8 | **DIFFERS** |
| `MOMENT theta drug spending share model \| target` | 0.162000000477 | 0.162000000477 | 1.000000 | exact | ok |
| `MOMENT aleph value of life / income model` | 162.001951919 | 57.5118230074 | 0.355007 | 0.2 | **DIFFERS** |
| `MOMENT aleph value of life / income model \| target` | 80 | 80 | 1.000000 | exact | ok |
| `MOMENT pi_eu unemployment rate model` | 0.0269897996201 | 0.0529836262935 | 1.963098 | 0.3 | **DIFFERS** |
| `MOMENT pi_eu unemployment rate model \| target` | 0.0485000014305 | 0.0485000014305 | 1.000000 | exact | ok |
| `MOMENT kappa_ued unemployment given SUD model` | 0.429359916097 | 0.102819874513 | 0.239472 | 0.1 | **DIFFERS** |
| `MOMENT kappa_ued unemployment given SUD model \| target` | 0.16249999404 | 0.16249999404 | 1.000000 | exact | ok |
| `MOMENT kappa_uem employment given SMI model` | 0.302412883835 | 0.301819111294 | 0.998037 | 2.7 | **DIFFERS** |
| `MOMENT kappa_uem employment given SMI model \| target` | 0.300000011921 | 0.300000011921 | 1.000000 | exact | ok |
| `MOMENT p_m SMI population share model` | 0.0439884115778 | 0.0439840054712 | 0.999900 | 4.0 | **DIFFERS** |
| `MOMENT p_m SMI population share model \| target` | 0.0482152529807 | 0.0482066834481 | 0.999822 | 3.8 | **DIFFERS** |
| `MOMENT lambda_m SMI share of the homeless model` | 0.190696028985 | 0.233199746014 | 1.222887 | 0.7 | **DIFFERS** |
| `MOMENT lambda_m SMI share of the homeless model \| target` | 0.25 | 0.25 | 1.000000 | exact | ok |
| `MOMENT pi_V eligibles with a voucher model` | 0.173046711622 | 0.271438578949 | 1.568586 | 0.4 | **DIFFERS** |
| `MOMENT pi_V eligibles with a voucher model \| target` | 0.266000002623 | 0.266000002623 | 1.000000 | exact | ok |
| `MOMENT cbar food stamps / labour income model` | 0.0157022313479 | 0.0112050364973 | 0.713595 | 0.5 | **DIFFERS** |
| `MOMENT cbar food stamps / labour income model \| target` | 0.00419999985024 | 0.00419999985024 | 1.000000 | exact | ok |
| `MOMENT tau_u treatment take up model` | 0.00757602768324 | 0.0838077278224 | 11.062226 | 0.0 | **DIFFERS** |
| `MOMENT tau_u treatment take up model \| target` | 0.245000004768 | 0.245000004768 | 1.000000 | exact | ok |
| `MOMENT mu_H recovery housed / homeless model` | 1.36460782452 | 1.40585784829 | 1.030228 | 1.5 | **DIFFERS** |
| `MOMENT mu_H recovery housed / homeless model \| target` | 1.47321428571 | 1.47321428571 | 1.000000 | exact | ok |
| `MOMENT w_bot net worth share, bottom half model` | 0.159292323968 | 0.157159982335 | 0.986614 | 1.9 | **DIFFERS** |
| `MOMENT w_bot net worth share, bottom half model \| target` | 0.025 | 0.025 | 1.000000 | exact | ok |
| `MOMENT y_u income of drug users model` | 0.33587993171 | 0.170199635262 | 0.506728 | 0.3 | **DIFFERS** |
| `MOMENT y_u income of drug users model \| target` | 0.74 | 0.74 | 1.000000 | exact | ok |

## All `DIAG` fields (100)

| name | two-pass | one-pass | ratio (one/two) | matching s.f. | verdict |
|---|---|---|---|---|---|
| `DIAG unit 0 share of renters` | 0.118540326738 | 0.120663656643 | 1.017912 | 1.8 | **DIFFERS** |
| `DIAG unit 0 share of renters \| of whom over half of income` | 0 | 0 | 1.000000 | exact | ok |
| `DIAG unit 1 share of renters` | 0.20835051071 | 0.209113075545 | 1.003660 | 2.4 | **DIFFERS** |
| `DIAG unit 1 share of renters \| of whom over half of income` | 0 | 0 | 1.000000 | exact | ok |
| `DIAG unit 2 share of renters` | 0.673109162552 | 0.670223267812 | 0.995713 | 2.4 | **DIFFERS** |
| `DIAG unit 2 share of renters \| of whom over half of income` | 0.408596138465 | 0.381203203285 | 0.932958 | 1.2 | **DIFFERS** |
| `DIAG aggregate rent / aggregate income` | 0.20827633691 | 0.207419534792 | 0.995886 | 2.4 | **DIFFERS** |
| `DIAG aggregate housing / aggregate expenditure` | 0.191618432632 | 0.186691449299 | 0.974288 | 1.6 | **DIFFERS** |
| `DIAG over half of EXPENDITURE, all households` | 0.0524160920162 | 0.0494055842017 | 0.942565 | 1.2 | **DIFFERS** |
| `DIAG over half of EXPENDITURE, housed only` | 0.0526286556337 | 0.0495997305252 | 0.942447 | 1.2 | **DIFFERS** |
| `DIAG income of WORKING AGE drug users / average` | 0.332529188669 | 0.163365811063 | 0.491283 | 0.3 | **DIFFERS** |
| `DIAG working age share of drug users` | 0.346833524738 | 0.31360077051 | 0.904182 | 1.0 | **DIFFERS** |
| `DIAG users band 1 use rate` | 0.0128128151852 | 0.0102089558742 | 0.796777 | 0.7 | **DIFFERS** |
| `DIAG users band 1 use rate \| share with the disorder` | 0.0255166616571 | 0.279890950229 | 10.968949 | 0.0 | **DIFFERS** |
| `DIAG users band 1 use rate \| income/average` | 0.508405553322 | 0.188113192745 | 0.370006 | 0.2 | **DIFFERS** |
| `DIAG users band 2 use rate` | 0.000573713447969 | 0.00535019642044 | 9.325555 | 0.0 | **DIFFERS** |
| `DIAG users band 2 use rate \| share with the disorder` | 0.558132443089 | 0.939639423882 | 1.683542 | 0.4 | **DIFFERS** |
| `DIAG users band 2 use rate \| income/average` | 0.127567235508 | 0.286558132999 | 2.246330 | 0.3 | **DIFFERS** |
| `DIAG users band 3 use rate` | 0.00310184008585 | 0.0064577354611 | 2.081905 | 0.3 | **DIFFERS** |
| `DIAG users band 3 use rate \| share with the disorder` | 0.0688639349206 | 0.483518037456 | 7.021354 | 0.1 | **DIFFERS** |
| `DIAG users band 3 use rate \| income/average` | 0.137855310951 | 0.183977174907 | 1.334567 | 0.6 | **DIFFERS** |
| `DIAG users band 4 use rate` | 0.009710500269 | 0.0190860481362 | 1.965506 | 0.3 | **DIFFERS** |
| `DIAG users band 4 use rate \| share with the disorder` | 0.0344855332177 | 0.0839175436916 | 2.433413 | 0.2 | **DIFFERS** |
| `DIAG users band 4 use rate \| income/average` | 0.192857333694 | 0.11104115715 | 0.575768 | 0.4 | **DIFFERS** |
| `DIAG users band 5 use rate` | 0.0343465010981 | 0.0640602581614 | 1.865117 | 0.3 | **DIFFERS** |
| `DIAG users band 5 use rate \| share with the disorder` | 0.281951209154 | 0.279251255267 | 0.990424 | 2.0 | **DIFFERS** |
| `DIAG users band 5 use rate \| income/average` | 0.335213892091 | 0.171929661676 | 0.512895 | 0.3 | **DIFFERS** |
| `DIAG drug threshold, (phi/theta)*p*b` | 0.0151802254788 | 0.0151802254788 | 1.000000 | exact | ok |
| `DIAG buyers: mean C` | 0.130314611264 | 0.133344999067 | 1.023254 | 1.6 | **DIFFERS** |
| `DIAG non-buyers: mean C` | 0.393973868844 | 0.396788332461 | 1.007144 | 2.1 | **DIFFERS** |
| `DIAG buyers: mean income` | 0.0952142752408 | 0.0848511117176 | 0.891160 | 1.0 | **DIFFERS** |
| `DIAG non-buyers: mean income` | 0.506799738845 | 0.508528358579 | 1.003411 | 2.5 | **DIFFERS** |
| `DIAG buyers as a share of clean households` | 0.0222487379562 | 0.0176002327113 | 0.791067 | 0.7 | **DIFFERS** |
| `DIAG assets of drug users / average net worth` | 0.184766382778 | 0.20789982696 | 1.125204 | 1.0 | **DIFFERS** |
| `DIAG assets of experimenters / average net worth` | 0.204684404424 | 0.219048527298 | 1.070177 | 1.2 | **DIFFERS** |
| `DIAG assets with a SUD / average net worth` | 0.106675562598 | 0.180648463102 | 1.693438 | 0.4 | **DIFFERS** |
| `DIAG mass with a NEGATIVE value of life` | 1.15599838812 | 0.571424239599 | 0.494312 | 0.3 | **DIFFERS** |
| `DIAG lowest value of a period of life` | -60.0248048906 | -60.0248048906 | 1.000000 | exact | ok |
| `DIAG value of life, drug users` | 16.0009468178 | 16.8973603446 | 1.056023 | 1.3 | **DIFFERS** |
| `DIAG value of life, everyone else` | 18.6464525672 | 18.6894690425 | 1.002307 | 2.6 | **DIFFERS** |
| `DIAG aleph itself, for scale` | 34.41327 | 34.41327 | 1.000000 | exact | ok |
| `DIAG treatment price / average labour income` | 0.143131893162 | 0.100694643128 | 0.703509 | 0.5 | **DIFFERS** |
| `DIAG treatment price / average labour income \| data outpatient` | 0.034 | 0.034 | 1.000000 | exact | ok |
| `DIAG households receiving food stamps` | 1.54495399791 | 1.54613371483 | 1.000764 | 3.1 | **DIFFERS** |
| `DIAG households receiving food stamps \| data` | 0.125 | 0.125 | 1.000000 | exact | ok |
| `DIAG max allotment / avg labour income` | 0.007331089 | 0.007331089 | 1.000000 | exact | ok |
| `DIAG max allotment / avg labour income \| data` | 0.039586 | 0.039586 | 1.000000 | exact | ok |
| `DIAG gross eligibility cutoff` | 0.0244369633333 | 0.0244369633333 | 1.000000 | exact | ok |
| `DIAG gross eligibility cutoff \| data` | 0.214872 | 0.214872 | 1.000000 | exact | ok |
| `DIAG aggregate rent / output` | 0.241989558636 | 0.240693441751 | 0.994644 | 2.3 | **DIFFERS** |
| `DIAG asset grid, reachable points` | 25 | 25 | 1.000000 | exact | ok |
| `DIAG share in the smallest unit` | 0.116498263966 | 0.120663656643 | 1.035755 | 1.5 | **DIFFERS** |
| `DIAG income histogram mass / distribution (want 1.0)` | 1.00002033057 | 1 | 0.999980 | 4.7 | ok |
| `DIAG SUD rate, income band 1 model` | 0.022372217484 | 0.021628248659 | 0.966746 | 1.5 | **DIFFERS** |
| `DIAG SUD rate, income band 1 model \| data` | 0.1365 | 0.1365 | 1.000000 | exact | ok |
| `DIAG SUD rate, income band 2 model` | 0.011137966561 | 0.0159811813415 | 1.434838 | 0.5 | **DIFFERS** |
| `DIAG SUD rate, income band 2 model \| data` | 0.1308 | 0.1308 | 1.000000 | exact | ok |
| `DIAG SUD rate, income band 3 model` | 0.00155579894621 | 0.00240202451272 | 1.543917 | 0.5 | **DIFFERS** |
| `DIAG SUD rate, income band 3 model \| data` | 0.0911 | 0.0911 | 1.000000 | exact | ok |
| `DIAG SUD rate, income band 4 model` | 0.000987846000622 | 0.00189296025835 | 1.916250 | 0.3 | **DIFFERS** |
| `DIAG SUD rate, income band 4 model \| data` | 0.102 | 0.102 | 1.000000 | exact | ok |
| `DIAG SUD rate, income band 5 model` | 0.000101568319427 | 0.000181550454017 | 1.787471 | 0.4 | **DIFFERS** |
| `DIAG SUD rate, income band 5 model \| data` | 0.0786 | 0.0786 | 1.000000 | exact | ok |
| `DIAG SUD rate, income band 6 model` | 1.34009285703e-08 | 2.55636151561e-08 | 1.907600 | 0.3 | **DIFFERS** |
| `DIAG SUD rate, income band 6 model \| data` | 0.0717 | 0.0717 | 1.000000 | exact | ok |
| `DIAG SUD rate, income band 7 model` | 0 | 0 | 1.000000 | exact | ok |
| `DIAG SUD rate, income band 7 model \| data` | 0.0482 | 0.0482 | 1.000000 | exact | ok |
| `DIAG homelessness rate rebuilt from the bands` | 0.0040389330657 | 0.00391426166076 | 0.969133 | 1.5 | **DIFFERS** |
| `DIAG disorder rate, band 1` | 0.00175558268171 | 0.00285739436047 | 1.627605 | 0.4 | **DIFFERS** |
| `DIAG disorder rate, band 2` | 0.00283338113074 | 0.00502725548216 | 1.774296 | 0.4 | **DIFFERS** |
| `DIAG disorder rate, band 3` | 0.00177392756603 | 0.00312243157656 | 1.760180 | 0.4 | **DIFFERS** |
| `DIAG disorder rate, band 4` | 0.00113555951189 | 0.00160165427837 | 1.410454 | 0.5 | **DIFFERS** |
| `DIAG disorder rate, band 5` | 0.0186372418737 | 0.0178889075043 | 0.959847 | 1.4 | **DIFFERS** |
| `DIAG SUD share of the homeless, band 1` | 0.000108720676744 | 0.000217737880938 | 2.002727 | 0.3 | **DIFFERS** |
| `DIAG SUD share of the homeless, band 2` | 0.0031840767649 | 0.00636289280218 | 1.998348 | 0.3 | **DIFFERS** |
| `DIAG SUD share of the homeless, band 3` | 0.000674529040852 | 0.000703645744845 | 1.043166 | 1.4 | **DIFFERS** |
| `DIAG SUD share of the homeless, band 4` | 0.00152709499882 | 0.00149245570884 | 0.977317 | 1.6 | **DIFFERS** |
| `DIAG SUD share of the homeless, band 5` | 0.000358004525922 | 0.000331250179863 | 0.925268 | 1.1 | **DIFFERS** |
| `DIAG participation, with a SUD, working age` | 1 | 1 | 1.000000 | exact | ok |
| `DIAG households with no wage income, working age` | 0.0527776913198 | 0.0529836262935 | 1.003902 | 2.4 | **DIFFERS** |
| `DIAG households with no wage income, working age \| data` | 0.1393 | 0.1393 | 1.000000 | exact | ok |
| `DIAG participation, without a SUD, working age` | 1 | 1 | 1.000000 | exact | ok |
| `DIAG employed share of the homeless, working age` | 0.931140972943 | 0.976954211288 | 1.049201 | 1.3 | **DIFFERS** |
| `DIAG working age homeless mass` | 0.411707051061 | 0.199502915449 | 0.484575 | 0.3 | **DIFFERS** |
| `DIAG kappa_phi_d_level, SUD mortality level` | 8 | 8 | 1.000000 | exact | ok |
| `DIAG homeless who could afford it on INCOME ALONE` | 0.924750477024 | 0.935689658712 | 1.011829 | 1.9 | **DIFFERS** |
| `DIAG homeless by choice, share of the homeless` | 0.92478998273 | 0.93572632876 | 1.011826 | 1.9 | **DIFFERS** |
| `DIAG homeless receiving food stamps` | 0.000104114725561 | 9.77847567438e-05 | 0.939202 | 1.2 | **DIFFERS** |
| `DIAG average assets of the homeless` | 0.0462887234058 | 0.0211495571489 | 0.456905 | 0.3 | **DIFFERS** |
| `DIAG wealth share of the bottom 25 pct` | 0.0319670651717 | 0.0315335177182 | 0.986438 | 1.9 | **DIFFERS** |
| `DIAG mean drug quantity, users` | 0.0205287432916 | 0.03071775178 | 1.496329 | 0.5 | **DIFFERS** |
| `DIAG onset at the mean quantity` | 0.327249591486 | 0.447397403421 | 1.367144 | 0.6 | **DIFFERS** |
| `DIAG carriers of the disorder consuming no drugs` | 0.0233934399947 | 0.00545526050983 | 0.233196 | 0.1 | **DIFFERS** |
| `DIAG income of experimenters / average` | 0.343736423816 | 0.155493508049 | 0.452363 | 0.3 | **DIFFERS** |
| `DIAG income of drug users / labour income` | 0.221685815371 | 0.155686583885 | 0.702285 | 0.5 | **DIFFERS** |
| `DIAG income with a SUD / labour income` | 0.201355865301 | 0.188568330837 | 0.936493 | 1.2 | **DIFFERS** |
| `DIAG mass ON the top savings grid point` | 0.000287019374393 | 0.00014387282807 | 0.501265 | 0.3 | **DIFFERS** |
| `DIAG mass in the top THREE savings grid points` | 0.00125075419105 | 0.000627350603494 | 0.501578 | 0.3 | **DIFFERS** |
| `DIAG histogram mass / distribution (want 1.0)` | 1.00002033057 | 1 | 0.999980 | 4.7 | ok |
| `DIAG histogram wealth / total wealth (want 1.0)` | 1 | 1 | 1.000000 | 13.1 | ok |

## `UNTARGETED` fields (92, included for completeness)

| name | two-pass | one-pass | ratio (one/two) | matching s.f. | verdict |
|---|---|---|---|---|---|
| `UNTARGETED mean age of drug users model` | 65.7150180704 | 68.4287456349 | 1.041295 | 1.4 | **DIFFERS** |
| `UNTARGETED mean age of drug users model \| observed` | 45.48 | 45.48 | 1.000000 | exact | ok |
| `UNTARGETED users aged 26-34, share model` | 0.162128249067 | 0.0728279522325 | 0.449200 | 0.3 | **DIFFERS** |
| `UNTARGETED users aged 26-34, share model \| observed` | 0.28404 | 0.28404 | 1.000000 | exact | ok |
| `UNTARGETED users aged 35-44, share model` | 0.00795561060672 | 0.0418198671258 | 5.256651 | 0.1 | **DIFFERS** |
| `UNTARGETED users aged 35-44, share model \| observed` | 0.25054 | 0.25054 | 1.000000 | exact | ok |
| `UNTARGETED users aged 45-54, share model` | 0.0418165979219 | 0.0490572677057 | 1.173153 | 0.8 | **DIFFERS** |
| `UNTARGETED users aged 45-54, share model \| observed` | 0.17768 | 0.17768 | 1.000000 | exact | ok |
| `UNTARGETED users aged 55-64, share model` | 0.122989772928 | 0.136206422339 | 1.107461 | 1.0 | **DIFFERS** |
| `UNTARGETED users aged 55-64, share model \| observed` | 0.16327 | 0.16327 | 1.000000 | exact | ok |
| `UNTARGETED users aged 65 plus, share model` | 0.665109769476 | 0.700088490597 | 1.052591 | 1.3 | **DIFFERS** |
| `UNTARGETED users aged 65 plus, share model \| observed` | 0.12445 | 0.12445 | 1.000000 | exact | ok |
| `UNTARGETED housing over income, renters model` | 0.130727658637 | 0.25237347602 | 1.930529 | 0.3 | **DIFFERS** |
| `UNTARGETED housing over income, renters model \| observed` | 0.202 | 0.202 | 1.000000 | exact | ok |
| `UNTARGETED delta_d child SUD ratio model` | 2.34732441477 | 1.96270393397 | 0.836145 | 0.8 | **DIFFERS** |
| `UNTARGETED delta_d child SUD ratio model \| observed` | 2 | 2 | 1.000000 | exact | ok |
| `UNTARGETED wealth share bottom 1 pct model` | 0 | 0 | 1.000000 | exact | ok |
| `UNTARGETED wealth share bottom 1 pct model \| observed` | -0.00225 | -0.00225 | 1.000000 | exact | ok |
| `UNTARGETED wealth share bottom 5 pct model` | 0.000387357419005 | 0.000335809629857 | 0.866924 | 0.9 | **DIFFERS** |
| `UNTARGETED wealth share bottom 5 pct model \| observed` | -0.00422 | -0.00422 | 1.000000 | exact | ok |
| `UNTARGETED wealth share bottom 10 pct model` | 0.00303382550005 | 0.00299625184382 | 0.987615 | 1.9 | **DIFFERS** |
| `UNTARGETED wealth share bottom 10 pct model \| observed` | -0.00446 | -0.00446 | 1.000000 | exact | ok |
| `UNTARGETED income share bottom 1 pct model` | 0.000694427306624 | 0.000690409660167 | 0.994214 | 2.2 | **DIFFERS** |
| `UNTARGETED income share bottom 1 pct model \| observed` | 9e-05 | 9e-05 | 1.000000 | exact | ok |
| `UNTARGETED income share bottom 5 pct model` | 0.00347213653312 | 0.00345204830084 | 0.994214 | 2.2 | **DIFFERS** |
| `UNTARGETED income share bottom 5 pct model \| observed` | 0.00288 | 0.00288 | 1.000000 | exact | ok |
| `UNTARGETED income share bottom 10 pct model` | 0.0086070734459 | 0.00868103086231 | 1.008593 | 2.1 | **DIFFERS** |
| `UNTARGETED income share bottom 10 pct model \| observed` | 0.00924 | 0.00924 | 1.000000 | exact | ok |
| `UNTARGETED delta_h child homelessness ratio model` | 2.21498263652 | 2.21788388832 | 1.001310 | 2.9 | **DIFFERS** |
| `UNTARGETED delta_h child homelessness ratio model \| observed` | 2.1 | 2.1 | 1.000000 | exact | ok |
| `UNTARGETED homelessness rate, band 1 model` | 0.0224978910385 | 0.0218052966936 | 0.969215 | 1.5 | **DIFFERS** |
| `UNTARGETED homelessness rate, band 1 model \| observed` | 0.003161 | 0.003161 | 1.000000 | exact | ok |
| `UNTARGETED homelessness rate, band 2 model` | 0.000287849617328 | 0.000276065108101 | 0.959060 | 1.4 | **DIFFERS** |
| `UNTARGETED homelessness rate, band 2 model \| observed` | 0.003378 | 0.003378 | 1.000000 | exact | ok |
| `UNTARGETED homelessness rate, band 3 model` | 8.00743346667e-05 | 7.70705107429e-05 | 0.962487 | 1.4 | **DIFFERS** |
| `UNTARGETED homelessness rate, band 3 model \| observed` | 0.002912 | 0.002912 | 1.000000 | exact | ok |
| `UNTARGETED homelessness rate, band 4 model` | 8.48447854645e-05 | 8.51351217195e-05 | 1.003422 | 2.5 | **DIFFERS** |
| `UNTARGETED homelessness rate, band 4 model \| observed` | 0.002496 | 0.002496 | 1.000000 | exact | ok |
| `UNTARGETED homelessness rate, band 5 model` | 5.55586232954e-06 | 5.64793757094e-06 | 1.016573 | 1.8 | **DIFFERS** |
| `UNTARGETED homelessness rate, band 5 model \| observed` | 0.00077 | 0.00077 | 1.000000 | exact | ok |
| `UNTARGETED homelessness profile, band 1 model` | 5.57025597416 | 5.57073046809 | 1.000085 | 4.1 | ok |
| `UNTARGETED homelessness profile, band 1 model \| observed` | 1.28079416532 | 1.28079416532 | 1.000000 | exact | ok |
| `UNTARGETED homelessness profile, band 2 model` | 0.071268726826 | 0.0705280157606 | 0.989607 | 2.0 | **DIFFERS** |
| `UNTARGETED homelessness profile, band 2 model \| observed` | 1.36871961102 | 1.36871961102 | 1.000000 | exact | ok |
| `UNTARGETED homelessness profile, band 3 model` | 0.0198256156673 | 0.0196896675344 | 0.993143 | 2.2 | **DIFFERS** |
| `UNTARGETED homelessness profile, band 3 model \| observed` | 1.17990275527 | 1.17990275527 | 1.000000 | exact | ok |
| `UNTARGETED homelessness profile, band 4 model` | 0.0210067322445 | 0.0217499822695 | 1.035382 | 1.5 | **DIFFERS** |
| `UNTARGETED homelessness profile, band 4 model \| observed` | 1.0113452188 | 1.0113452188 | 1.000000 | exact | ok |
| `UNTARGETED homelessness profile, band 5 model` | 0.00137557672761 | 0.00144291262579 | 1.048951 | 1.3 | **DIFFERS** |
| `UNTARGETED homelessness profile, band 5 model \| observed` | 0.311993517018 | 0.311993517018 | 1.000000 | exact | ok |
| `UNTARGETED share of the homeless, band 1 model` | 0.97850610358 | 0.978532292998 | 1.000027 | 4.6 | ok |
| `UNTARGETED share of the homeless, band 1 model \| observed` | 0.26 | 0.26 | 1.000000 | exact | ok |
| `UNTARGETED share of the homeless, band 2 model` | 0.0137199252063 | 0.0135744059239 | 0.989394 | 2.0 | **DIFFERS** |
| `UNTARGETED share of the homeless, band 2 model \| observed` | 0.272 | 0.272 | 1.000000 | exact | ok |
| `UNTARGETED share of the homeless, band 3 model` | 0.00371048116065 | 0.00368305100371 | 0.992607 | 2.1 | **DIFFERS** |
| `UNTARGETED share of the homeless, band 3 model \| observed` | 0.21 | 0.21 | 1.000000 | exact | ok |
| `UNTARGETED share of the homeless, band 4 model` | 0.00369368750416 | 0.00382196514822 | 1.034729 | 1.5 | **DIFFERS** |
| `UNTARGETED share of the homeless, band 4 model \| observed` | 0.184 | 0.184 | 1.000000 | exact | ok |
| `UNTARGETED share of the homeless, band 5 model` | 0.000369802548847 | 0.000388284926588 | 1.049979 | 1.3 | **DIFFERS** |
| `UNTARGETED share of the homeless, band 5 model \| observed` | 0.075 | 0.075 | 1.000000 | exact | ok |
| `UNTARGETED earnings share, bottom tenth model` | 0.0125067108506 | 0.0125067108506 | 1.000000 | exact | ok |
| `UNTARGETED earnings share, bottom tenth model \| observed` | 0.0099 | 0.0099 | 1.000000 | exact | ok |
| `UNTARGETED earnings share, top tenth model` | 0.30866237765 | 0.30866237765 | 1.000000 | exact | ok |
| `UNTARGETED earnings share, top tenth model \| observed` | 0.411 | 0.411 | 1.000000 | exact | ok |
| `UNTARGETED renters above 30 pct of income model` | 0.433795510617 | 0.417439046709 | 0.962295 | 1.4 | **DIFFERS** |
| `UNTARGETED renters above 30 pct of income model \| observed` | 0.406 | 0.406 | 1.000000 | exact | ok |
| `UNTARGETED renters above 50 pct of income model` | 0.299607761653 | 0.255491256606 | 0.852752 | 0.8 | **DIFFERS** |
| `UNTARGETED renters above 50 pct of income model \| observed` | 0.175 | 0.175 | 1.000000 | exact | ok |
| `UNTARGETED tenant contribution rate model` | 0.739787448926 | 0.469627279049 | 0.634814 | 0.4 | **DIFFERS** |
| `UNTARGETED tenant contribution rate model \| observed` | 0.312 | 0.312 | 1.000000 | exact | ok |
| `UNTARGETED voucher holders, wages main model` | 0.477701216109 | 0.48984751113 | 1.025427 | 1.6 | **DIFFERS** |
| `UNTARGETED voucher holders, wages main model \| observed` | 0.28 | 0.28 | 1.000000 | exact | ok |
| `UNTARGETED participation, with a SUD model` | 0.0804607395111 | 0.329278839314 | 4.092416 | 0.1 | **DIFFERS** |
| `UNTARGETED participation, with a SUD model \| observed` | 0.658 | 0.658 | 1.000000 | exact | ok |
| `UNTARGETED participation, without a SUD model` | 0.751846382421 | 0.75053846505 | 0.998260 | 2.8 | **DIFFERS** |
| `UNTARGETED participation, without a SUD model \| observed` | 0.615 | 0.615 | 1.000000 | exact | ok |
| `UNTARGETED homeless at treatment admission model` | 0 | 0 | 1.000000 | exact | ok |
| `UNTARGETED homeless at treatment admission model \| observed` | 0.145 | 0.145 | 1.000000 | exact | ok |
| `UNTARGETED SMI alongside SUD at admission model` | 0.00452225678841 | 0.00884927513948 | 1.956827 | 0.3 | **DIFFERS** |
| `UNTARGETED SMI alongside SUD at admission model \| observed` | 0.431 | 0.431 | 1.000000 | exact | ok |
| `UNTARGETED working, homeless in treatment model` | 0 | 0 | 1.000000 | exact | ok |
| `UNTARGETED working, homeless in treatment model \| observed` | 0.066 | 0.066 | 1.000000 | exact | ok |
| `UNTARGETED SUD share of the homeless model` | 0.00144187910114 | 0.000307860333977 | 0.213513 | 0.1 | **DIFFERS** |
| `UNTARGETED SUD share of the homeless model \| observed` | 0.217 | 0.217 | 1.000000 | exact | ok |
| `UNTARGETED drug deaths, share of deaths model` | 0.00408742657055 | 0.0261984047804 | 6.409511 | 0.1 | **DIFFERS** |
| `UNTARGETED drug deaths, share of deaths model \| observed` | 0.2 | 0.2 | 1.000000 | exact | ok |
| `UNTARGETED income of the homeless model` | 0.551929987156 | 0.274647415931 | 0.497613 | 0.3 | **DIFFERS** |
| `UNTARGETED income of the homeless model \| observed` | 0.191 | 0.191 | 1.000000 | exact | ok |
| `UNTARGETED employed share of the homeless model` | 0.931140972943 | 0.976954211288 | 1.049201 | 1.3 | **DIFFERS** |
| `UNTARGETED employed share of the homeless model \| observed` | 0.46 | 0.46 | 1.000000 | exact | ok |
| `UNTARGETED income with a SUD model` | 0.3050776802 | 0.206146607688 | 0.675718 | 0.5 | **DIFFERS** |
| `UNTARGETED income with a SUD model \| observed` | 0.711 | 0.711 | 1.000000 | exact | ok |

---

## Provenance

Both runs were made against `code/housing_first_or_treatment_first_SR_v1.f90` and `code/run_one_point.sh` as they stood at commit `7d22348`, and those two files are byte-identical across the tree states the two runs were made in, so the only difference between the runs is the `number_of_beta_types` line. Each run reported `HANDOVER OK: 28 of 28 parameters applied` and ended with `===== END OF MOMENTS =====`.

Commit `577ea6d`, which landed on the branch while this comparison was being written, changes the *default* `money_cost_of_treatment` and the comment above it in `code/run_one_point.sh`. It does not affect these runs: the parameter vector in `code/VALIDATE.txt` passes both `money_cost_of_treatment=0.0600702` and `utility_cost_of_treatment=0` explicitly, overriding the defaults, and the 28-of-28 handover confirms both were applied. The source edit was reverted before either point file was committed, so the branch never carries `number_of_beta_types=1`.

## Method

Each line containing `MOMENT`, `DIAG` or `UNTARGETED` is split into its `label= value` fields; a line carrying several values (`model=` / `target=`, or `share of renters=` / `of whom over half of income=`) contributes one comparison row per field, named `<line label> | <field label>`. Repeated identical lines are collapsed to their first occurrence (no repeated line disagreed with itself in either file). Two values are said to agree to 4 significant figures when their relative difference is below 1e-4; the "matching s.f." column is -log10 of that relative difference.

Regenerate with:

```
python3 report.py code/points/point_110278961e_twobeta_equal.txt code/points/point_110278961e_onebeta.txt
```
