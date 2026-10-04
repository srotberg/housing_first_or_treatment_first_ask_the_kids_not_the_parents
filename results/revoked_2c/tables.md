# GUARDS (T = 10)
  Treatment First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 3.36e-13 (rule 1e-10) PASS
  Treatment First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 6.0e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 1.1e-03 PASS
  Treatment First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Treatment First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Treatment First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Housing First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 1.13e-13 (rule 1e-10) PASS
  Housing First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 8.5e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 9.1e-04 PASS
  Housing First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Housing First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Housing First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  tags: written {1: 0.1398906398562, 2: 0.02055695262089897, 3: 0.00576352629909628}, read {1: 0.1398906398562, 2: 0.02055695262089897, 3: 0.00576352629909628} PASS
  group 1 (revoked in year 1): starting mass 1.398906e-01 under Treatment First, 1.398906e-01 in the counterfactual PASS
  group 2 (revoked in year 2): starting mass 2.055695e-02 under Treatment First, 2.055695e-02 in the counterfactual PASS
  group 3 (revoked in year 3): starting mass 5.763526e-03 under Treatment First, 5.763526e-03 in the counterfactual PASS
  group 4 (holding a voucher at the reform): starting mass 3.603069e+00 under Treatment First, 3.603069e+00 in the counterfactual PASS
  Housing First stationarity (the no-policy steady state pushed through its own kernel, newborns added):
    t=1: sum over cells of |dist(t) - dist(t-1)| = 2.12e-03; SUD 0.03813902, homeless 0.00613093, deaths 0.99998364, alive 50.8275885674
    t=2: sum over cells of |dist(t) - dist(t-1)| = 2.35e-03; SUD 0.03813843, homeless 0.00613098, deaths 0.99999101, alive 50.8277494929
    t=3: sum over cells of |dist(t) - dist(t-1)| = 2.61e-03; SUD 0.03813833, homeless 0.00613088, deaths 0.99999328, alive 50.8277577762
    t=4: sum over cells of |dist(t) - dist(t-1)| = 3.00e-03; SUD 0.03813436, homeless 0.00612891, deaths 0.99998854, alive 50.8277396936
    t=5: sum over cells of |dist(t) - dist(t-1)| = 3.42e-03; SUD 0.03813339, homeless 0.00612882, deaths 0.99998992, alive 50.8276983541
    t=6: sum over cells of |dist(t) - dist(t-1)| = 3.73e-03; SUD 0.03813240, homeless 0.00612950, deaths 0.99999887, alive 50.8277005326
    t=7: sum over cells of |dist(t) - dist(t-1)| = 4.04e-03; SUD 0.03813256, homeless 0.00612974, deaths 0.99996939, alive 50.8278111045
    t=8: sum over cells of |dist(t) - dist(t-1)| = 4.43e-03; SUD 0.03813287, homeless 0.00612978, deaths 0.99999522, alive 50.8279115796
    t=9: sum over cells of |dist(t) - dist(t-1)| = 5.08e-03; SUD 0.03813256, homeless 0.00612991, deaths 1.00000641, alive 50.8279697182
GUARD SUMMARY: PASS

# TABLES

(a) = Treatment First as it happened to them; (b) = the same households, voucher kept, under Housing First's rules.
Deaths include the end of life (age 85, the model's last age); 'hazard' is the survival draw alone.

## revoked in year 1 (starting mass 1.398906e-01 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 1.398906e-01 | 1.398906e-01 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 96.14 | 96.14 | 0.00 | 0.00 | 0.00 | 100.00 |
| 2 | 1 | 1.365754e-01 | 1.369741e-01 | 3.315247e-03 | 2.916494e-03 | 2.37 | 2.08 | 2.32 | 2.04 | 92.96 | 93.02 | 28.61 | 0.00 | 0.00 | 86.34 |
| 3 | 2 | 1.333371e-01 | 1.341152e-01 | 6.553533e-03 | 5.775473e-03 | 4.68 | 4.13 | 4.59 | 4.03 | 89.84 | 89.93 | 28.24 | 0.00 | 0.35 | 75.33 |
| 4 | 3 | 1.301743e-01 | 1.313082e-01 | 9.716351e-03 | 8.582464e-03 | 6.95 | 6.14 | 6.80 | 5.99 | 86.78 | 86.86 | 27.37 | 0.00 | 0.68 | 65.87 |
| 5 | 4 | 1.270880e-01 | 1.285475e-01 | 1.280264e-02 | 1.134310e-02 | 9.15 | 8.11 | 8.95 | 7.91 | 83.75 | 83.81 | 25.79 | 0.02 | 1.00 | 57.83 |
| 6 | 5 | 1.240723e-01 | 1.258276e-01 | 1.581835e-02 | 1.406308e-02 | 11.31 | 10.05 | 11.06 | 9.80 | 80.75 | 80.79 | 24.01 | 0.11 | 1.31 | 51.02 |
| 7 | 6 | 1.211232e-01 | 1.231429e-01 | 1.876748e-02 | 1.674770e-02 | 13.42 | 11.97 | 13.11 | 11.67 | 77.76 | 77.78 | 22.09 | 0.26 | 1.61 | 45.23 |
| 8 | 7 | 1.182357e-01 | 1.204881e-01 | 2.165493e-02 | 1.940253e-02 | 15.48 | 13.87 | 15.12 | 13.51 | 74.80 | 74.81 | 20.12 | 0.44 | 1.92 | 40.32 |
| 9 | 8 | 1.154047e-01 | 1.178586e-01 | 2.448594e-02 | 2.203205e-02 | 17.50 | 15.75 | 17.08 | 15.33 | 71.87 | 71.87 | 18.24 | 0.62 | 2.22 | 36.15 |

## revoked in year 2 (starting mass 2.055695e-02 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 0 | 2.055695e-02 | 2.055695e-02 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 96.14 | 96.14 | 0.00 | 0.00 | 0.00 | 100.00 |
| 3 | 1 | 2.006826e-02 | 2.012274e-02 | 4.886894e-04 | 4.342127e-04 | 2.38 | 2.11 | 2.33 | 2.06 | 92.90 | 93.02 | 25.85 | 0.00 | 0.00 | 86.43 |
| 4 | 2 | 1.959037e-02 | 1.969725e-02 | 9.665868e-04 | 8.596996e-04 | 4.70 | 4.18 | 4.60 | 4.08 | 89.74 | 89.92 | 26.07 | 0.00 | 0.35 | 75.49 |
| 5 | 3 | 1.912271e-02 | 1.927965e-02 | 1.434247e-03 | 1.277305e-03 | 6.98 | 6.21 | 6.83 | 6.06 | 86.65 | 86.85 | 26.01 | 0.00 | 0.69 | 66.05 |
| 6 | 4 | 1.866591e-02 | 1.886911e-02 | 1.891039e-03 | 1.687847e-03 | 9.20 | 8.21 | 9.00 | 8.01 | 83.60 | 83.79 | 24.87 | 0.02 | 1.00 | 58.01 |
| 7 | 5 | 1.821932e-02 | 1.846481e-02 | 2.337629e-03 | 2.092138e-03 | 11.37 | 10.18 | 11.12 | 9.92 | 80.57 | 80.75 | 23.36 | 0.10 | 1.31 | 51.18 |
| 8 | 6 | 1.778235e-02 | 1.806588e-02 | 2.774599e-03 | 2.491075e-03 | 13.50 | 12.12 | 13.19 | 11.81 | 77.58 | 77.73 | 21.62 | 0.24 | 1.62 | 45.40 |
| 9 | 7 | 1.735446e-02 | 1.767159e-02 | 3.202488e-03 | 2.885367e-03 | 15.58 | 14.04 | 15.21 | 13.67 | 74.60 | 74.75 | 19.77 | 0.41 | 1.93 | 40.49 |

## revoked in year 3 (starting mass 5.763526e-03 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 0 | 5.763526e-03 | 5.763526e-03 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 96.26 | 96.26 | 0.00 | 0.00 | 0.00 | 100.00 |
| 4 | 1 | 5.647956e-03 | 5.658411e-03 | 1.155698e-04 | 1.051154e-04 | 2.01 | 1.82 | 1.97 | 1.79 | 93.01 | 93.23 | 19.20 | 0.00 | 0.00 | 85.36 |
| 5 | 2 | 5.533618e-03 | 5.554423e-03 | 2.299078e-04 | 2.091036e-04 | 3.99 | 3.63 | 3.93 | 3.57 | 89.85 | 90.22 | 20.11 | 0.00 | 0.34 | 73.98 |
| 6 | 3 | 5.420370e-03 | 5.451422e-03 | 3.431564e-04 | 3.121044e-04 | 5.95 | 5.42 | 5.86 | 5.32 | 86.77 | 87.24 | 20.89 | 0.00 | 0.67 | 64.35 |
| 7 | 4 | 5.308414e-03 | 5.349273e-03 | 4.551122e-04 | 4.142536e-04 | 7.90 | 7.19 | 7.77 | 7.06 | 83.76 | 84.28 | 20.73 | 0.02 | 0.97 | 56.23 |
| 8 | 5 | 5.197707e-03 | 5.247823e-03 | 5.658190e-04 | 5.157033e-04 | 9.82 | 8.95 | 9.66 | 8.79 | 80.80 | 81.33 | 20.05 | 0.09 | 1.26 | 49.42 |
| 9 | 6 | 5.088237e-03 | 5.146917e-03 | 6.752889e-04 | 6.166098e-04 | 11.72 | 10.70 | 11.52 | 10.50 | 77.87 | 78.41 | 18.99 | 0.24 | 1.55 | 43.73 |

## holding a voucher at the reform (starting mass 3.603069e+00 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 3.603069e+00 | 3.603069e+00 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.40 | 5.40 | 0.58 | 0.58 | 100.00 | 100.00 |
| 1 | 1 | 3.446758e+00 | 3.446758e+00 | 1.563112e-01 | 1.563112e-01 | 4.34 | 4.34 | 1.97 | 1.97 | 5.34 | 5.39 | 0.00 | 0.00 | 84.18 | 88.24 |
| 2 | 2 | 3.296422e+00 | 3.296811e+00 | 3.066473e-01 | 3.062580e-01 | 8.51 | 8.50 | 3.86 | 3.85 | 5.28 | 5.37 | 1.19 | 0.00 | 75.07 | 79.20 |
| 3 | 3 | 3.152485e+00 | 3.153292e+00 | 4.505842e-01 | 4.497774e-01 | 12.51 | 12.48 | 5.65 | 5.62 | 5.23 | 5.34 | 1.35 | 0.01 | 67.97 | 71.71 |
| 4 | 4 | 3.015037e+00 | 3.016240e+00 | 5.880323e-01 | 5.868296e-01 | 16.32 | 16.29 | 7.34 | 7.30 | 5.16 | 5.31 | 1.40 | 0.04 | 61.92 | 65.26 |
| 5 | 5 | 2.884082e+00 | 2.885646e+00 | 7.189874e-01 | 7.174234e-01 | 19.95 | 19.91 | 8.94 | 8.89 | 5.09 | 5.26 | 1.42 | 0.11 | 56.60 | 59.59 |
| 6 | 6 | 2.759598e+00 | 2.761488e+00 | 8.434715e-01 | 8.415817e-01 | 23.41 | 23.36 | 10.45 | 10.39 | 5.02 | 5.20 | 1.44 | 0.19 | 51.84 | 54.51 |
| 7 | 7 | 2.641561e+00 | 2.643740e+00 | 9.615084e-01 | 9.593296e-01 | 26.69 | 26.63 | 11.87 | 11.81 | 4.94 | 5.13 | 1.44 | 0.27 | 47.53 | 49.94 |
| 8 | 8 | 2.529913e+00 | 2.532343e+00 | 1.073157e+00 | 1.070726e+00 | 29.78 | 29.72 | 13.21 | 13.14 | 4.85 | 5.06 | 1.43 | 0.35 | 43.61 | 45.79 |
| 9 | 9 | 2.424587e+00 | 2.427233e+00 | 1.178482e+00 | 1.175837e+00 | 32.71 | 32.63 | 14.47 | 14.39 | 4.75 | 4.97 | 1.40 | 0.42 | 40.05 | 42.02 |

## the three revoked cohorts pooled, by years since revocation (each cohort from its own revocation year)

| years since | cohorts | starting mass | cum. deaths % (a) | cum. deaths % (b) | gap (a)-(b) pp | hazard % (a) | hazard % (b) | hazard gap pp |
|---|---|---|---|---|---|---|---|---|
| 0 | 3 | 1.662111e-01 | 0.00 | 0.00 | +0.00 | 0.00 | 0.00 | +0.00 |
| 1 | 3 | 1.662111e-01 | 2.36 | 2.08 | +0.28 | 2.31 | 2.03 | +0.28 |
| 2 | 3 | 1.662111e-01 | 4.66 | 4.12 | +0.54 | 4.57 | 4.02 | +0.54 |
| 3 | 3 | 1.662111e-01 | 6.92 | 6.12 | +0.80 | 6.77 | 5.97 | +0.80 |
| 4 | 3 | 1.662111e-01 | 9.11 | 8.09 | +1.02 | 8.92 | 7.89 | +1.02 |
| 5 | 3 | 1.662111e-01 | 11.26 | 10.03 | +1.23 | 11.02 | 9.78 | +1.23 |
| 6 | 3 | 1.662111e-01 | 13.37 | 11.95 | +1.42 | 13.06 | 11.64 | +1.42 |

## the whole population, Treatment First path against Housing First

| year | deaths, Treatment First | deaths, Housing First | SUD %, Treatment First | SUD %, Housing First | homeless %, Treatment First | homeless %, Housing First | holding %, Treatment First | holding %, Housing First | excluded %, Treatment First |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 9.999856e-01 | 9.999836e-01 | 3.69 | 3.81 | 0.61 | 0.61 | 6.69 | 7.09 | 0.40 |
| 2 | 1.000216e+00 | 9.999910e-01 | 3.58 | 3.81 | 0.70 | 0.61 | 6.60 | 7.09 | 0.42 |
| 3 | 1.000083e+00 | 9.999933e-01 | 3.47 | 3.81 | 0.71 | 0.61 | 6.56 | 7.09 | 0.41 |
| 4 | 9.998921e-01 | 9.999885e-01 | 3.36 | 3.81 | 0.71 | 0.61 | 6.53 | 7.09 | 0.40 |
| 5 | 9.996978e-01 | 9.999899e-01 | 3.26 | 3.81 | 0.72 | 0.61 | 6.51 | 7.09 | 0.39 |
| 6 | 9.995049e-01 | 9.999989e-01 | 3.16 | 3.81 | 0.72 | 0.61 | 6.49 | 7.09 | 0.39 |
| 7 | 9.992679e-01 | 9.999694e-01 | 3.07 | 3.81 | 0.72 | 0.61 | 6.48 | 7.09 | 0.38 |
| 8 | 9.990756e-01 | 9.999952e-01 | 2.97 | 3.81 | 0.71 | 0.61 | 6.47 | 7.09 | 0.38 |
| 9 | 9.988670e-01 | 1.000006e+00 | 2.89 | 3.81 | 0.71 | 0.61 | 6.47 | 7.09 | 0.37 |

HEADLINE: three-year cumulative mortality of the households revoked in years 1-3: 6.92 per cent under Treatment First against 6.12 per cent had they kept the voucher; gap +0.80 pp (survival draw alone +0.80 pp)
