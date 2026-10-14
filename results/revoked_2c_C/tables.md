# GUARDS (T = 10)
  Treatment First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 3.73e-13 (rule 1e-10) PASS
  Treatment First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 8.8e-07 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 2.2e-04 PASS
  Treatment First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Treatment First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Treatment First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Housing First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 8.41e-14 (rule 1e-10) PASS
  Housing First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 1.4e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 4.0e-04 PASS
  Housing First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Housing First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Housing First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  tags: written {1: 0.005247071777425075, 2: 0.004359708939722313, 3: 0.0038145255948595714}, read {1: 0.005247071777425075, 2: 0.004359708939722313, 3: 0.0038145255948595714} PASS
  group 1 (revoked in year 1): starting mass 5.247072e-03 under Treatment First, 5.247072e-03 in the counterfactual PASS
  group 2 (revoked in year 2): starting mass 4.359709e-03 under Treatment First, 4.359709e-03 in the counterfactual PASS
  group 3 (revoked in year 3): starting mass 3.814526e-03 under Treatment First, 3.814526e-03 in the counterfactual PASS
  group 4 (holding a voucher at the reform): starting mass 3.603172e+00 under Treatment First, 3.603172e+00 in the counterfactual PASS
  Housing First stationarity (the no-policy steady state pushed through its own kernel, newborns added):
    t=1: sum over cells of |dist(t) - dist(t-1)| = 1.39e-03; SUD 0.03814673, homeless 0.00613101, deaths 1.00001524, alive 50.8279422741
    t=2: sum over cells of |dist(t) - dist(t-1)| = 1.35e-03; SUD 0.03814680, homeless 0.00613112, deaths 1.00001595, alive 50.8279286965
    t=3: sum over cells of |dist(t) - dist(t-1)| = 1.31e-03; SUD 0.03814691, homeless 0.00613114, deaths 1.00001659, alive 50.8279198180
    t=4: sum over cells of |dist(t) - dist(t-1)| = 1.08e-03; SUD 0.03814717, homeless 0.00613111, deaths 1.00021252, alive 50.8277055659
    t=5: sum over cells of |dist(t) - dist(t-1)| = 9.18e-04; SUD 0.03814721, homeless 0.00613109, deaths 0.99999957, alive 50.8277628878
    t=6: sum over cells of |dist(t) - dist(t-1)| = 1.00e-03; SUD 0.03814682, homeless 0.00613109, deaths 1.00002969, alive 50.8277492719
    t=7: sum over cells of |dist(t) - dist(t-1)| = 1.05e-03; SUD 0.03814655, homeless 0.00613108, deaths 0.99999622, alive 50.8277427300
    t=8: sum over cells of |dist(t) - dist(t-1)| = 1.06e-03; SUD 0.03814671, homeless 0.00613108, deaths 0.99999573, alive 50.8277488260
    t=9: sum over cells of |dist(t) - dist(t-1)| = 1.05e-03; SUD 0.03814668, homeless 0.00613109, deaths 0.99999619, alive 50.8277546660
GUARD SUMMARY: PASS

# TABLES

(a) = Treatment First as it happened to them; (b) = the same households, voucher kept, under Housing First's rules.
Deaths include the end of life (age 85, the model's last age); 'hazard' is the survival draw alone.

## revoked in year 1 (starting mass 5.247072e-03 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 5.247072e-03 | 5.247072e-03 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 97.08 | 97.08 | 0.00 | 0.00 | 0.00 | 100.00 |
| 2 | 1 | 5.007492e-03 | 5.007493e-03 | 2.395799e-04 | 2.395789e-04 | 4.57 | 4.57 | 4.26 | 4.26 | 94.17 | 94.19 | 0.00 | 0.00 | 0.00 | 72.49 |
| 3 | 2 | 4.789089e-03 | 4.789190e-03 | 4.579831e-04 | 4.578821e-04 | 8.73 | 8.73 | 8.11 | 8.11 | 91.24 | 91.30 | 0.08 | 0.00 | 1.14 | 57.99 |
| 4 | 3 | 4.590234e-03 | 4.590584e-03 | 6.568374e-04 | 6.564877e-04 | 12.52 | 12.51 | 11.59 | 11.58 | 88.30 | 88.43 | 0.74 | 0.00 | 2.51 | 48.65 |
| 5 | 4 | 4.409308e-03 | 4.410063e-03 | 8.377636e-04 | 8.370091e-04 | 15.97 | 15.95 | 14.72 | 14.70 | 85.39 | 85.58 | 1.56 | 0.01 | 3.83 | 41.82 |
| 6 | 5 | 4.244665e-03 | 4.245965e-03 | 1.002407e-03 | 1.001107e-03 | 19.10 | 19.08 | 17.53 | 17.50 | 82.51 | 82.77 | 2.47 | 0.17 | 5.01 | 36.54 |
| 7 | 6 | 4.094635e-03 | 4.096578e-03 | 1.152437e-03 | 1.150494e-03 | 21.96 | 21.93 | 20.05 | 20.01 | 79.69 | 80.02 | 3.18 | 0.43 | 6.03 | 32.33 |
| 8 | 7 | 3.957580e-03 | 3.960201e-03 | 1.289492e-03 | 1.286871e-03 | 24.58 | 24.53 | 22.31 | 22.26 | 76.93 | 77.35 | 3.69 | 0.75 | 6.90 | 28.91 |
| 9 | 8 | 3.831874e-03 | 3.835158e-03 | 1.415198e-03 | 1.411914e-03 | 26.97 | 26.91 | 24.34 | 24.28 | 74.24 | 74.75 | 3.98 | 1.07 | 7.62 | 26.05 |

## revoked in year 2 (starting mass 4.359709e-03 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 0 | 4.359709e-03 | 4.359709e-03 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 97.06 | 97.06 | 0.00 | 0.00 | 0.00 | 100.00 |
| 3 | 1 | 4.162152e-03 | 4.162152e-03 | 1.975574e-04 | 1.975564e-04 | 4.53 | 4.53 | 4.24 | 4.24 | 94.12 | 94.14 | 0.00 | 0.00 | 0.00 | 72.58 |
| 4 | 2 | 3.981616e-03 | 3.981701e-03 | 3.780933e-04 | 3.780079e-04 | 8.67 | 8.67 | 8.08 | 8.08 | 91.17 | 91.23 | 0.08 | 0.00 | 1.14 | 58.14 |
| 5 | 3 | 3.816806e-03 | 3.817100e-03 | 5.429024e-04 | 5.426085e-04 | 12.45 | 12.45 | 11.56 | 11.55 | 88.21 | 88.33 | 0.72 | 0.00 | 2.52 | 48.83 |
| 6 | 4 | 3.666441e-03 | 3.667073e-03 | 6.932676e-04 | 6.926358e-04 | 15.90 | 15.89 | 14.70 | 14.69 | 85.28 | 85.46 | 1.52 | 0.01 | 3.85 | 42.02 |
| 7 | 5 | 3.529220e-03 | 3.530307e-03 | 8.304889e-04 | 8.294022e-04 | 19.05 | 19.02 | 17.53 | 17.51 | 82.38 | 82.63 | 2.41 | 0.17 | 5.04 | 36.77 |
| 8 | 6 | 3.403821e-03 | 3.405447e-03 | 9.558877e-04 | 9.542616e-04 | 21.93 | 21.89 | 20.08 | 20.04 | 79.53 | 79.86 | 3.12 | 0.42 | 6.07 | 32.60 |
| 9 | 7 | 3.288947e-03 | 3.291142e-03 | 1.070762e-03 | 1.068567e-03 | 24.56 | 24.51 | 22.38 | 22.33 | 76.75 | 77.16 | 3.63 | 0.73 | 6.95 | 29.21 |

## revoked in year 3 (starting mass 3.814526e-03 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 0 | 3.814526e-03 | 3.814526e-03 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 97.03 | 97.03 | 0.00 | 0.00 | 0.00 | 100.00 |
| 4 | 1 | 3.645905e-03 | 3.645906e-03 | 1.686203e-04 | 1.686195e-04 | 4.42 | 4.42 | 4.15 | 4.15 | 94.07 | 94.09 | 0.00 | 0.00 | 0.00 | 72.48 |
| 5 | 2 | 3.491159e-03 | 3.491234e-03 | 3.233661e-04 | 3.232913e-04 | 8.48 | 8.48 | 7.93 | 7.93 | 91.09 | 91.16 | 0.07 | 0.00 | 1.14 | 58.12 |
| 6 | 3 | 3.349272e-03 | 3.349525e-03 | 4.652538e-04 | 4.650003e-04 | 12.20 | 12.19 | 11.37 | 11.37 | 88.12 | 88.24 | 0.68 | 0.00 | 2.52 | 48.84 |
| 7 | 4 | 3.219232e-03 | 3.219775e-03 | 5.952936e-04 | 5.947504e-04 | 15.61 | 15.59 | 14.50 | 14.48 | 85.16 | 85.35 | 1.45 | 0.01 | 3.85 | 42.07 |
| 8 | 5 | 3.100019e-03 | 3.100956e-03 | 7.145067e-04 | 7.135691e-04 | 18.73 | 18.71 | 17.33 | 17.31 | 82.24 | 82.49 | 2.32 | 0.16 | 5.05 | 36.88 |
| 9 | 6 | 2.990584e-03 | 2.991993e-03 | 8.239412e-04 | 8.225322e-04 | 21.60 | 21.56 | 19.90 | 19.86 | 79.37 | 79.70 | 3.03 | 0.40 | 6.09 | 32.76 |

## holding a voucher at the reform (starting mass 3.603172e+00 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 3.603172e+00 | 3.603172e+00 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.40 | 5.40 | 0.58 | 0.58 | 100.00 | 100.00 |
| 1 | 1 | 3.446856e+00 | 3.446856e+00 | 1.563168e-01 | 1.563168e-01 | 4.34 | 4.34 | 1.97 | 1.97 | 5.31 | 5.39 | 0.00 | 0.00 | 88.09 | 88.24 |
| 2 | 2 | 3.296921e+00 | 3.296903e+00 | 3.062516e-01 | 3.062694e-01 | 8.50 | 8.50 | 3.85 | 3.85 | 5.23 | 5.37 | 0.00 | 0.00 | 78.98 | 79.20 |
| 3 | 3 | 3.153431e+00 | 3.153379e+00 | 4.497417e-01 | 4.497931e-01 | 12.48 | 12.48 | 5.62 | 5.62 | 5.14 | 5.34 | 0.01 | 0.01 | 71.46 | 71.71 |
| 4 | 4 | 3.016382e+00 | 3.016283e+00 | 5.867904e-01 | 5.868891e-01 | 16.29 | 16.29 | 7.30 | 7.31 | 5.06 | 5.31 | 0.05 | 0.04 | 65.01 | 65.26 |
| 5 | 5 | 2.885845e+00 | 2.885687e+00 | 7.173270e-01 | 7.174850e-01 | 19.91 | 19.91 | 8.89 | 8.89 | 4.97 | 5.26 | 0.11 | 0.11 | 59.33 | 59.59 |
| 6 | 6 | 2.761753e+00 | 2.761525e+00 | 8.414196e-01 | 8.416471e-01 | 23.35 | 23.36 | 10.39 | 10.39 | 4.88 | 5.20 | 0.19 | 0.19 | 54.26 | 54.51 |
| 7 | 7 | 2.644077e+00 | 2.643772e+00 | 9.590952e-01 | 9.594007e-01 | 26.62 | 26.63 | 11.80 | 11.81 | 4.78 | 5.13 | 0.28 | 0.27 | 49.69 | 49.94 |
| 8 | 8 | 2.532765e+00 | 2.532374e+00 | 1.070407e+00 | 1.070798e+00 | 29.71 | 29.72 | 13.13 | 13.14 | 4.68 | 5.06 | 0.36 | 0.35 | 45.54 | 45.79 |
| 9 | 9 | 2.427749e+00 | 2.427266e+00 | 1.175423e+00 | 1.175907e+00 | 32.62 | 32.64 | 14.38 | 14.39 | 4.58 | 4.97 | 0.43 | 0.42 | 41.78 | 42.02 |

## the three revoked cohorts pooled, by years since revocation (each cohort from its own revocation year)

| years since | cohorts | starting mass | cum. deaths % (a) | cum. deaths % (b) | gap (a)-(b) pp | hazard % (a) | hazard % (b) | hazard gap pp |
|---|---|---|---|---|---|---|---|---|
| 0 | 3 | 1.342131e-02 | 0.00 | 0.00 | +0.00 | 0.00 | 0.00 | +0.00 |
| 1 | 3 | 1.342131e-02 | 4.51 | 4.51 | +0.00 | 4.22 | 4.22 | +0.00 |
| 2 | 3 | 1.342131e-02 | 8.64 | 8.64 | +0.00 | 8.05 | 8.05 | +0.00 |
| 3 | 3 | 1.342131e-02 | 12.41 | 12.40 | +0.01 | 11.52 | 11.51 | +0.01 |
| 4 | 3 | 1.342131e-02 | 15.84 | 15.83 | +0.01 | 14.65 | 14.64 | +0.01 |
| 5 | 3 | 1.342131e-02 | 18.98 | 18.96 | +0.02 | 17.47 | 17.45 | +0.02 |
| 6 | 3 | 1.342131e-02 | 21.85 | 21.81 | +0.04 | 20.02 | 19.98 | +0.04 |

## the whole population, Treatment First path against Housing First

| year | deaths, Treatment First | deaths, Housing First | SUD %, Treatment First | SUD %, Housing First | homeless %, Treatment First | homeless %, Housing First | holding %, Treatment First | holding %, Housing First | excluded %, Treatment First |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.000015e+00 | 1.000015e+00 | 3.74 | 3.81 | 0.61 | 0.61 | 7.05 | 7.09 | 0.04 |
| 2 | 9.998722e-01 | 1.000016e+00 | 3.66 | 3.81 | 0.61 | 0.61 | 7.02 | 7.09 | 0.07 |
| 3 | 9.997307e-01 | 1.000017e+00 | 3.59 | 3.81 | 0.61 | 0.61 | 7.00 | 7.09 | 0.08 |
| 4 | 9.997848e-01 | 1.000213e+00 | 3.52 | 3.81 | 0.60 | 0.61 | 6.98 | 7.09 | 0.09 |
| 5 | 9.994318e-01 | 9.999996e-01 | 3.45 | 3.81 | 0.60 | 0.61 | 6.97 | 7.09 | 0.10 |
| 6 | 9.993206e-01 | 1.000030e+00 | 3.39 | 3.81 | 0.60 | 0.61 | 6.96 | 7.09 | 0.10 |
| 7 | 9.991454e-01 | 9.999962e-01 | 3.32 | 3.81 | 0.60 | 0.61 | 6.95 | 7.09 | 0.10 |
| 8 | 9.990006e-01 | 9.999957e-01 | 3.26 | 3.81 | 0.60 | 0.61 | 6.94 | 7.09 | 0.10 |
| 9 | 9.988541e-01 | 9.999962e-01 | 3.21 | 3.81 | 0.60 | 0.61 | 6.93 | 7.09 | 0.10 |

HEADLINE: three-year cumulative mortality of the households revoked in years 1-3: 12.41 per cent under Treatment First against 12.40 per cent had they kept the voucher; gap +0.01 pp (survival draw alone +0.01 pp)
