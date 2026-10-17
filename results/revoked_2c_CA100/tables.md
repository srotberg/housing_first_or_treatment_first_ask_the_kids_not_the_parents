# GUARDS (T = 10)
  Treatment First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 2.54e-13 (rule 1e-10) PASS
  Treatment First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 2.9e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 7.6e-04 PASS
  Treatment First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Treatment First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Treatment First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Housing First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 1.06e-13 (rule 1e-10) PASS
  Housing First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 3.5e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 6.6e-04 PASS
  Housing First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Housing First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Housing First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  tags: written {1: 0.16440745819324612, 2: 0.0, 3: 0.0}, read {1: 0.16440745819324612, 2: 0.0, 3: 0.0} PASS
  group 1 (revoked in year 1): starting mass 1.644075e-01 under Treatment First, 1.644075e-01 in the counterfactual PASS
  group 2 (revoked in year 2): starting mass 0.000000e+00 under Treatment First, 0.000000e+00 in the counterfactual PASS
  group 3 (revoked in year 3): starting mass 0.000000e+00 under Treatment First, 0.000000e+00 in the counterfactual PASS
  group 4 (holding a voucher at the reform): starting mass 3.601840e+00 under Treatment First, 3.601840e+00 in the counterfactual PASS
  Housing First stationarity (the no-policy steady state pushed through its own kernel, newborns added):
    t=1: sum over cells of |dist(t) - dist(t-1)| = 2.11e-03; SUD 0.03827437, homeless 0.00613002, deaths 1.00000389, alive 50.8250093574
    t=2: sum over cells of |dist(t) - dist(t-1)| = 1.97e-03; SUD 0.03827401, homeless 0.00613007, deaths 0.99999421, alive 50.8249780550
    t=3: sum over cells of |dist(t) - dist(t-1)| = 1.87e-03; SUD 0.03827437, homeless 0.00613006, deaths 1.00002058, alive 50.8249575625
    t=4: sum over cells of |dist(t) - dist(t-1)| = 1.83e-03; SUD 0.03827449, homeless 0.00613008, deaths 0.99998312, alive 50.8250007050
    t=5: sum over cells of |dist(t) - dist(t-1)| = 1.84e-03; SUD 0.03827472, homeless 0.00613005, deaths 0.99998119, alive 50.8250176112
    t=6: sum over cells of |dist(t) - dist(t-1)| = 2.06e-03; SUD 0.03827298, homeless 0.00613101, deaths 0.99997902, alive 50.8249890533
    t=7: sum over cells of |dist(t) - dist(t-1)| = 2.14e-03; SUD 0.03827339, homeless 0.00613096, deaths 0.99997357, alive 50.8250176006
    t=8: sum over cells of |dist(t) - dist(t-1)| = 2.27e-03; SUD 0.03827213, homeless 0.00613049, deaths 0.99998296, alive 50.8250153529
    t=9: sum over cells of |dist(t) - dist(t-1)| = 2.35e-03; SUD 0.03827272, homeless 0.00613022, deaths 0.99999196, alive 50.8250316691
GUARD SUMMARY: PASS

# TABLES

(a) = Treatment First as it happened to them; (b) = the same households, voucher kept, under Housing First's rules.
Deaths include the end of life (age 85, the model's last age); 'hazard' is the survival draw alone.

## revoked in year 1 (starting mass 1.644075e-01 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 1.644075e-01 | 1.644075e-01 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 96.17 | 96.17 | 0.00 | 0.00 | 0.00 | 100.00 |
| 2 | 1 | 1.605618e-01 | 1.610232e-01 | 3.845654e-03 | 3.384263e-03 | 2.34 | 2.06 | 2.29 | 2.01 | 92.99 | 93.06 | 28.43 | 0.00 | 0.00 | 86.29 |
| 3 | 2 | 1.568028e-01 | 1.577027e-01 | 7.604617e-03 | 6.704743e-03 | 4.63 | 4.08 | 4.53 | 3.98 | 89.87 | 89.98 | 28.06 | 0.00 | 0.10 | 75.26 |
| 4 | 3 | 1.531265e-01 | 1.544395e-01 | 1.128100e-02 | 9.968000e-03 | 6.86 | 6.06 | 6.72 | 5.92 | 86.81 | 86.91 | 27.28 | 0.00 | 0.30 | 65.79 |
| 5 | 4 | 1.495329e-01 | 1.512268e-01 | 1.487455e-02 | 1.318062e-02 | 9.05 | 8.02 | 8.85 | 7.82 | 83.77 | 83.87 | 25.82 | 0.02 | 0.56 | 57.74 |
| 6 | 5 | 1.460165e-01 | 1.480583e-01 | 1.839093e-02 | 1.634918e-02 | 11.19 | 9.94 | 10.94 | 9.70 | 80.77 | 80.85 | 24.10 | 0.11 | 0.86 | 50.92 |
| 7 | 6 | 1.425732e-01 | 1.449273e-01 | 2.183430e-02 | 1.948013e-02 | 13.28 | 11.85 | 12.98 | 11.55 | 77.79 | 77.85 | 22.22 | 0.26 | 1.18 | 45.14 |
| 8 | 7 | 1.391984e-01 | 1.418282e-01 | 2.520901e-02 | 2.257930e-02 | 15.33 | 13.73 | 14.98 | 13.38 | 74.83 | 74.89 | 20.27 | 0.43 | 1.50 | 40.23 |
| 9 | 8 | 1.358865e-01 | 1.387553e-01 | 2.852095e-02 | 2.565212e-02 | 17.35 | 15.60 | 16.94 | 15.20 | 71.90 | 71.95 | 18.38 | 0.62 | 1.83 | 36.06 |

## revoked in year 2: no revoked mass, no table; it adds nothing to the pooled rows

## revoked in year 3: no revoked mass, no table; it adds nothing to the pooled rows

## holding a voucher at the reform (starting mass 3.601840e+00 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 3.601840e+00 | 3.601840e+00 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.40 | 5.40 | 0.58 | 0.58 | 100.00 | 100.00 |
| 1 | 1 | 3.445646e+00 | 3.445646e+00 | 1.561944e-01 | 1.561944e-01 | 4.34 | 4.34 | 1.97 | 1.97 | 5.34 | 5.39 | 0.00 | 0.00 | 83.47 | 88.24 |
| 2 | 2 | 3.295358e+00 | 3.295811e+00 | 3.064816e-01 | 3.060291e-01 | 8.51 | 8.50 | 3.86 | 3.84 | 5.29 | 5.37 | 1.39 | 0.00 | 74.95 | 79.19 |
| 3 | 3 | 3.151514e+00 | 3.152394e+00 | 4.503259e-01 | 4.494464e-01 | 12.50 | 12.48 | 5.64 | 5.62 | 5.23 | 5.35 | 1.40 | 0.01 | 67.92 | 71.70 |
| 4 | 4 | 3.014169e+00 | 3.015448e+00 | 5.876708e-01 | 5.863921e-01 | 16.32 | 16.28 | 7.33 | 7.30 | 5.16 | 5.31 | 1.43 | 0.04 | 61.88 | 65.25 |
| 5 | 5 | 2.883314e+00 | 2.884957e+00 | 7.185262e-01 | 7.168829e-01 | 19.95 | 19.90 | 8.93 | 8.89 | 5.10 | 5.26 | 1.45 | 0.11 | 56.56 | 59.58 |
| 6 | 6 | 2.758926e+00 | 2.760899e+00 | 8.429136e-01 | 8.409405e-01 | 23.40 | 23.35 | 10.44 | 10.39 | 5.02 | 5.21 | 1.46 | 0.19 | 51.80 | 54.50 |
| 7 | 7 | 2.640974e+00 | 2.643240e+00 | 9.608657e-01 | 9.585996e-01 | 26.68 | 26.61 | 11.86 | 11.80 | 4.94 | 5.14 | 1.46 | 0.27 | 47.50 | 49.93 |
| 8 | 8 | 2.529411e+00 | 2.531932e+00 | 1.072429e+00 | 1.069908e+00 | 29.77 | 29.70 | 13.20 | 13.13 | 4.85 | 5.07 | 1.44 | 0.35 | 43.59 | 45.78 |
| 9 | 9 | 2.424167e+00 | 2.426905e+00 | 1.177673e+00 | 1.174935e+00 | 32.70 | 32.62 | 14.46 | 14.38 | 4.75 | 4.98 | 1.42 | 0.42 | 40.03 | 42.01 |

## the three revoked cohorts pooled, by years since revocation (each cohort from its own revocation year)

| years since | cohorts | starting mass | cum. deaths % (a) | cum. deaths % (b) | gap (a)-(b) pp | hazard % (a) | hazard % (b) | hazard gap pp |
|---|---|---|---|---|---|---|---|---|
| 0 | 3 | 1.644075e-01 | 0.00 | 0.00 | +0.00 | 0.00 | 0.00 | +0.00 |
| 1 | 3 | 1.644075e-01 | 2.34 | 2.06 | +0.28 | 2.29 | 2.01 | +0.28 |
| 2 | 3 | 1.644075e-01 | 4.63 | 4.08 | +0.55 | 4.53 | 3.98 | +0.55 |
| 3 | 3 | 1.644075e-01 | 6.86 | 6.06 | +0.80 | 6.72 | 5.92 | +0.80 |
| 4 | 3 | 1.644075e-01 | 9.05 | 8.02 | +1.03 | 8.85 | 7.82 | +1.03 |
| 5 | 3 | 1.644075e-01 | 11.19 | 9.94 | +1.24 | 10.94 | 9.70 | +1.24 |
| 6 | 3 | 1.644075e-01 | 13.28 | 11.85 | +1.43 | 12.98 | 11.55 | +1.43 |

## the whole population, Treatment First path against Housing First

| year | deaths, Treatment First | deaths, Housing First | SUD %, Treatment First | SUD %, Housing First | homeless %, Treatment First | homeless %, Housing First | holding %, Treatment First | holding %, Housing First | excluded %, Treatment First |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.000006e+00 | 1.000004e+00 | 3.67 | 3.83 | 0.61 | 0.61 | 6.70 | 7.09 | 0.39 |
| 2 | 1.000210e+00 | 9.999942e-01 | 3.51 | 3.83 | 0.70 | 0.61 | 6.70 | 7.09 | 0.31 |
| 3 | 1.000012e+00 | 1.000021e+00 | 3.36 | 3.83 | 0.70 | 0.61 | 6.71 | 7.09 | 0.26 |
| 4 | 9.996803e-01 | 9.999831e-01 | 3.22 | 3.83 | 0.70 | 0.61 | 6.72 | 7.09 | 0.23 |
| 5 | 9.994080e-01 | 9.999812e-01 | 3.08 | 3.83 | 0.70 | 0.61 | 6.73 | 7.09 | 0.21 |
| 6 | 9.991315e-01 | 9.999790e-01 | 2.94 | 3.83 | 0.70 | 0.61 | 6.74 | 7.09 | 0.19 |
| 7 | 9.988420e-01 | 9.999736e-01 | 2.81 | 3.83 | 0.69 | 0.61 | 6.75 | 7.09 | 0.18 |
| 8 | 9.985576e-01 | 9.999830e-01 | 2.69 | 3.83 | 0.68 | 0.61 | 6.76 | 7.09 | 0.16 |
| 9 | 9.982623e-01 | 9.999920e-01 | 2.56 | 3.83 | 0.68 | 0.61 | 6.77 | 7.09 | 0.15 |

HEADLINE: three-year cumulative mortality of the households revoked in years 1-3: 6.86 per cent under Treatment First against 6.06 per cent had they kept the voucher; gap +0.80 pp (survival draw alone +0.80 pp)
