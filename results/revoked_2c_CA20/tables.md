# GUARDS (T = 10)
  Treatment First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 3.33e-13 (rule 1e-10) PASS
  Treatment First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 3.2e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 7.4e-04 PASS
  Treatment First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Treatment First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Treatment First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Housing First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 1.16e-13 (rule 1e-10) PASS
  Housing First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 5.9e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 1.7e-03 PASS
  Housing First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Housing First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Housing First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  tags: written {1: 0.032876026133607315, 2: 0.025815687279275662, 3: 0.020978766410033836}, read {1: 0.032876026133607315, 2: 0.025815687279275662, 3: 0.020978766410033836} PASS
  group 1 (revoked in year 1): starting mass 3.287603e-02 under Treatment First, 3.287603e-02 in the counterfactual PASS
  group 2 (revoked in year 2): starting mass 2.581569e-02 under Treatment First, 2.581569e-02 in the counterfactual PASS
  group 3 (revoked in year 3): starting mass 2.097877e-02 under Treatment First, 2.097877e-02 in the counterfactual PASS
  group 4 (holding a voucher at the reform): starting mass 3.601779e+00 under Treatment First, 3.601779e+00 in the counterfactual PASS
  Housing First stationarity (the no-policy steady state pushed through its own kernel, newborns added):
    t=1: sum over cells of |dist(t) - dist(t-1)| = 5.25e-03; SUD 0.03826946, homeless 0.00612976, deaths 1.00009050, alive 50.8255662238
    t=2: sum over cells of |dist(t) - dist(t-1)| = 4.99e-03; SUD 0.03826958, homeless 0.00612976, deaths 0.99999080, alive 50.8255636088
    t=3: sum over cells of |dist(t) - dist(t-1)| = 4.91e-03; SUD 0.03826990, homeless 0.00612973, deaths 0.99999549, alive 50.8255894234
    t=4: sum over cells of |dist(t) - dist(t-1)| = 4.96e-03; SUD 0.03826828, homeless 0.00612776, deaths 0.99998760, alive 50.8255307251
    t=5: sum over cells of |dist(t) - dist(t-1)| = 5.05e-03; SUD 0.03826837, homeless 0.00612808, deaths 0.99995589, alive 50.8256206073
    t=6: sum over cells of |dist(t) - dist(t-1)| = 5.36e-03; SUD 0.03826367, homeless 0.00612847, deaths 1.00000029, alive 50.8253483247
    t=7: sum over cells of |dist(t) - dist(t-1)| = 5.46e-03; SUD 0.03826435, homeless 0.00612872, deaths 0.99999105, alive 50.8253537175
    t=8: sum over cells of |dist(t) - dist(t-1)| = 5.45e-03; SUD 0.03826448, homeless 0.00612897, deaths 1.00002389, alive 50.8253304004
    t=9: sum over cells of |dist(t) - dist(t-1)| = 5.58e-03; SUD 0.03826464, homeless 0.00612909, deaths 1.00001856, alive 50.8254003783
GUARD SUMMARY: PASS

# TABLES

(a) = Treatment First as it happened to them; (b) = the same households, voucher kept, under Housing First's rules.
Deaths include the end of life (age 85, the model's last age); 'hazard' is the survival draw alone.

## revoked in year 1 (starting mass 3.287603e-02 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 3.287603e-02 | 3.287603e-02 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 96.17 | 96.17 | 0.00 | 0.00 | 0.00 | 100.00 |
| 2 | 1 | 3.210670e-02 | 3.219968e-02 | 7.693292e-04 | 6.763482e-04 | 2.34 | 2.06 | 2.29 | 2.01 | 93.07 | 93.07 | 28.86 | 0.00 | 0.00 | 86.53 |
| 3 | 2 | 3.135439e-02 | 3.153607e-02 | 1.521636e-03 | 1.339953e-03 | 4.63 | 4.08 | 4.53 | 3.98 | 90.04 | 89.98 | 28.47 | 0.00 | 1.42 | 75.37 |
| 4 | 3 | 3.061996e-02 | 3.088390e-02 | 2.256067e-03 | 1.992131e-03 | 6.86 | 6.06 | 6.72 | 5.91 | 87.04 | 86.92 | 27.15 | 0.00 | 3.10 | 65.87 |
| 5 | 4 | 2.990375e-02 | 3.024182e-02 | 2.972271e-03 | 2.634205e-03 | 9.04 | 8.01 | 8.85 | 7.82 | 84.06 | 83.87 | 25.06 | 0.03 | 4.57 | 57.81 |
| 6 | 5 | 2.920449e-02 | 2.960849e-02 | 3.671537e-03 | 3.267534e-03 | 11.17 | 9.94 | 10.92 | 9.69 | 81.10 | 80.85 | 22.79 | 0.12 | 5.70 | 50.98 |
| 7 | 6 | 2.852099e-02 | 2.898266e-02 | 4.355031e-03 | 3.893365e-03 | 13.25 | 11.84 | 12.95 | 11.55 | 78.14 | 77.86 | 20.48 | 0.27 | 6.50 | 45.19 |
| 8 | 7 | 2.785197e-02 | 2.836317e-02 | 5.024056e-03 | 4.512861e-03 | 15.28 | 13.73 | 14.93 | 13.38 | 75.19 | 74.89 | 18.26 | 0.44 | 7.04 | 40.28 |
| 9 | 8 | 2.719583e-02 | 2.774889e-02 | 5.680201e-03 | 5.127136e-03 | 17.28 | 15.60 | 16.87 | 15.19 | 72.26 | 71.96 | 16.22 | 0.63 | 7.38 | 36.10 |

## revoked in year 2 (starting mass 2.581569e-02 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 0 | 2.581569e-02 | 2.581569e-02 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 96.18 | 96.18 | 0.00 | 0.00 | 0.00 | 100.00 |
| 3 | 1 | 2.520972e-02 | 2.527825e-02 | 6.059652e-04 | 5.374377e-04 | 2.35 | 2.08 | 2.30 | 2.03 | 93.03 | 93.07 | 26.43 | 0.00 | 0.00 | 86.59 |
| 4 | 2 | 2.461631e-02 | 2.475110e-02 | 1.199379e-03 | 1.064585e-03 | 4.65 | 4.12 | 4.55 | 4.03 | 89.95 | 89.98 | 26.65 | 0.00 | 1.42 | 75.47 |
| 5 | 3 | 2.403607e-02 | 2.423319e-02 | 1.779619e-03 | 1.582497e-03 | 6.89 | 6.13 | 6.75 | 5.98 | 86.93 | 86.91 | 25.99 | 0.00 | 3.10 | 65.98 |
| 6 | 4 | 2.346970e-02 | 2.372346e-02 | 2.345983e-03 | 2.092232e-03 | 9.09 | 8.10 | 8.89 | 7.91 | 83.93 | 83.85 | 24.29 | 0.02 | 4.57 | 57.92 |
| 7 | 5 | 2.291643e-02 | 2.322086e-02 | 2.899258e-03 | 2.594827e-03 | 11.23 | 10.05 | 10.98 | 9.80 | 80.94 | 80.82 | 22.27 | 0.11 | 5.70 | 51.09 |
| 8 | 6 | 2.237543e-02 | 2.272440e-02 | 3.440258e-03 | 3.091292e-03 | 13.33 | 11.97 | 13.02 | 11.67 | 77.97 | 77.82 | 20.12 | 0.25 | 6.50 | 45.30 |
| 9 | 7 | 2.184577e-02 | 2.223312e-02 | 3.969913e-03 | 3.582571e-03 | 15.38 | 13.88 | 15.02 | 13.52 | 75.01 | 74.84 | 18.00 | 0.43 | 7.05 | 40.39 |

## revoked in year 3 (starting mass 2.097877e-02 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 0 | 2.097877e-02 | 2.097877e-02 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 96.20 | 96.20 | 0.00 | 0.00 | 0.00 | 100.00 |
| 4 | 1 | 2.048877e-02 | 2.054046e-02 | 4.899914e-04 | 4.383044e-04 | 2.34 | 2.09 | 2.29 | 2.04 | 92.99 | 93.08 | 24.16 | 0.00 | 0.00 | 86.53 |
| 5 | 2 | 2.000813e-02 | 2.011041e-02 | 9.706321e-04 | 8.683546e-04 | 4.63 | 4.14 | 4.53 | 4.04 | 89.87 | 89.99 | 24.85 | 0.00 | 1.42 | 75.42 |
| 6 | 3 | 1.953717e-02 | 1.968776e-02 | 1.441596e-03 | 1.291006e-03 | 6.87 | 6.15 | 6.73 | 6.01 | 86.82 | 86.91 | 24.75 | 0.00 | 3.09 | 65.93 |
| 7 | 4 | 1.907681e-02 | 1.927170e-02 | 1.901956e-03 | 1.707068e-03 | 9.07 | 8.14 | 8.87 | 7.94 | 83.81 | 83.85 | 23.43 | 0.02 | 4.56 | 57.88 |
| 8 | 5 | 1.862657e-02 | 1.886139e-02 | 2.352200e-03 | 2.117378e-03 | 11.21 | 10.09 | 10.96 | 9.85 | 80.81 | 80.81 | 21.66 | 0.11 | 5.69 | 51.06 |
| 9 | 6 | 1.818588e-02 | 1.845600e-02 | 2.792884e-03 | 2.522765e-03 | 13.31 | 12.03 | 13.01 | 11.72 | 77.83 | 77.80 | 19.69 | 0.24 | 6.50 | 45.30 |

## holding a voucher at the reform (starting mass 3.601779e+00 of a population of 1)

| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) | hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 3.601779e+00 | 3.601779e+00 | 0.000000e+00 | 0.000000e+00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.40 | 5.40 | 0.58 | 0.58 | 100.00 | 100.00 |
| 1 | 1 | 3.445569e+00 | 3.445569e+00 | 1.562099e-01 | 1.562099e-01 | 4.34 | 4.34 | 1.97 | 1.97 | 5.34 | 5.38 | 0.00 | 0.00 | 87.28 | 88.24 |
| 2 | 2 | 3.295657e+00 | 3.295740e+00 | 3.061213e-01 | 3.060382e-01 | 8.50 | 8.50 | 3.85 | 3.84 | 5.29 | 5.37 | 0.28 | 0.00 | 77.68 | 79.19 |
| 3 | 3 | 3.152118e+00 | 3.152336e+00 | 4.496606e-01 | 4.494424e-01 | 12.48 | 12.48 | 5.62 | 5.62 | 5.23 | 5.34 | 0.48 | 0.01 | 69.90 | 71.70 |
| 4 | 4 | 3.015013e+00 | 3.015395e+00 | 5.867658e-01 | 5.863836e-01 | 16.29 | 16.28 | 7.31 | 7.30 | 5.16 | 5.31 | 0.65 | 0.04 | 63.36 | 65.25 |
| 5 | 5 | 2.884355e+00 | 2.884912e+00 | 7.174239e-01 | 7.168661e-01 | 19.92 | 19.90 | 8.90 | 8.89 | 5.09 | 5.26 | 0.79 | 0.11 | 57.69 | 59.57 |
| 6 | 6 | 2.760123e+00 | 2.760856e+00 | 8.416560e-01 | 8.409229e-01 | 23.37 | 23.35 | 10.41 | 10.39 | 5.02 | 5.21 | 0.90 | 0.19 | 52.70 | 54.50 |
| 7 | 7 | 2.642299e+00 | 2.643198e+00 | 9.594800e-01 | 9.585805e-01 | 26.64 | 26.61 | 11.82 | 11.80 | 4.94 | 5.14 | 0.98 | 0.27 | 48.23 | 49.92 |
| 8 | 8 | 2.530836e+00 | 2.531887e+00 | 1.070942e+00 | 1.069891e+00 | 29.73 | 29.70 | 13.16 | 13.13 | 4.85 | 5.07 | 1.04 | 0.35 | 44.20 | 45.78 |
| 9 | 9 | 2.425679e+00 | 2.426863e+00 | 1.176100e+00 | 1.174915e+00 | 32.65 | 32.62 | 14.41 | 14.38 | 4.76 | 4.98 | 1.07 | 0.42 | 40.56 | 42.01 |

## the three revoked cohorts pooled, by years since revocation (each cohort from its own revocation year)

| years since | cohorts | starting mass | cum. deaths % (a) | cum. deaths % (b) | gap (a)-(b) pp | hazard % (a) | hazard % (b) | hazard gap pp |
|---|---|---|---|---|---|---|---|---|
| 0 | 3 | 7.967048e-02 | 0.00 | 0.00 | +0.00 | 0.00 | 0.00 | +0.00 |
| 1 | 3 | 7.967048e-02 | 2.34 | 2.07 | +0.27 | 2.29 | 2.03 | +0.27 |
| 2 | 3 | 7.967048e-02 | 4.63 | 4.11 | +0.53 | 4.54 | 4.01 | +0.53 |
| 3 | 3 | 7.967048e-02 | 6.87 | 6.11 | +0.77 | 6.73 | 5.96 | +0.77 |
| 4 | 3 | 7.967048e-02 | 9.06 | 8.08 | +0.99 | 8.87 | 7.88 | +0.99 |
| 5 | 3 | 7.967048e-02 | 11.20 | 10.02 | +1.18 | 10.95 | 9.77 | +1.18 |
| 6 | 3 | 7.967048e-02 | 13.29 | 11.93 | +1.36 | 12.99 | 11.63 | +1.36 |

## the whole population, Treatment First path against Housing First

| year | deaths, Treatment First | deaths, Housing First | SUD %, Treatment First | SUD %, Housing First | homeless %, Treatment First | homeless %, Housing First | holding %, Treatment First | holding %, Housing First | excluded %, Treatment First |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.000091e+00 | 1.000090e+00 | 3.72 | 3.83 | 0.61 | 0.61 | 6.99 | 7.09 | 0.09 |
| 2 | 9.998977e-01 | 9.999908e-01 | 3.61 | 3.83 | 0.63 | 0.61 | 6.93 | 7.09 | 0.14 |
| 3 | 9.997840e-01 | 9.999955e-01 | 3.51 | 3.83 | 0.64 | 0.61 | 6.89 | 7.09 | 0.16 |
| 4 | 9.996358e-01 | 9.999876e-01 | 3.41 | 3.83 | 0.64 | 0.61 | 6.87 | 7.09 | 0.16 |
| 5 | 9.994482e-01 | 9.999559e-01 | 3.31 | 3.83 | 0.65 | 0.61 | 6.85 | 7.09 | 0.16 |
| 6 | 9.993213e-01 | 1.000000e+00 | 3.22 | 3.83 | 0.65 | 0.61 | 6.84 | 7.09 | 0.16 |
| 7 | 9.991318e-01 | 9.999910e-01 | 3.13 | 3.83 | 0.65 | 0.61 | 6.83 | 7.09 | 0.16 |
| 8 | 9.989722e-01 | 1.000024e+00 | 3.04 | 3.83 | 0.65 | 0.61 | 6.83 | 7.09 | 0.15 |
| 9 | 9.987659e-01 | 1.000019e+00 | 2.96 | 3.83 | 0.65 | 0.61 | 6.83 | 7.09 | 0.15 |

HEADLINE: three-year cumulative mortality of the households revoked in years 1-3: 6.87 per cent under Treatment First against 6.11 per cent had they kept the voucher; gap +0.77 pp (survival draw alone +0.77 pp)
