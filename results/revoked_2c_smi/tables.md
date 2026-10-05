# GUARDS (T = 10, four threads; the tracked numbers are serial and exact, see code/revoked_2c)
  Treatment First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 3.74e-13 (rule 1e-10) PASS
  Treatment First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 7.4e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 1.5e-03 PASS
  Treatment First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Treatment First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Treatment First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Treatment First path: the SMI halves summed against the unsplit group, 272 comparisons (levels; shares times survivors): 23 bit for bit, worst relative difference 1.5e-13 (rule 1e-12) PASS
    (not identity: the module totals a group by summing whole arrays, a half by summing its own cells, so even at the start, where the cut is an exact partition of cells, the totals are added in a different order (starting masses bit for bit: False); after it the halves move in separate passes and rejoin in the same cells as SMI is left and entered. The rule is rounding.)
  Treatment First path: SMI share at the start: exactly 0 in the halves without SMI ([0.0, 0.0, 0.0, 0.0]), 1 to rounding in the halves with it (worst |share - 1| 1.9e-14, rule 1e-12; a share of slices over a sum of the whole) PASS
  Treatment First path: mass accounting in the halves, worst 4.9e-13 (rule 1e-10) PASS
  Housing First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 9.91e-14 (rule 1e-10) PASS
  Housing First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 4.9e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 9.7e-04 PASS
  Housing First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Housing First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Housing First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Housing First path: the SMI halves summed against the unsplit group, 272 comparisons (levels; shares times survivors): 52 bit for bit, worst relative difference 7.9e-14 (rule 1e-12) PASS
    (not identity: the module totals a group by summing whole arrays, a half by summing its own cells, so even at the start, where the cut is an exact partition of cells, the totals are added in a different order (starting masses bit for bit: False); after it the halves move in separate passes and rejoin in the same cells as SMI is left and entered. The rule is rounding.)
  Housing First path: SMI share at the start: exactly 0 in the halves without SMI ([0.0, 0.0, 0.0, 0.0]), 1 to rounding in the halves with it (worst |share - 1| 1.9e-14, rule 1e-12; a share of slices over a sum of the whole) PASS
  Housing First path: mass accounting in the halves, worst 1.6e-13 (rule 1e-10) PASS
  group 1, SMI at start 0: starting mass 1.228401e-01 (a), 1.228401e-01 (b) PASS
  group 1, SMI at start 1: starting mass 1.706515e-02 (a), 1.706515e-02 (b) PASS
  group 2, SMI at start 0: starting mass 1.806415e-02 (a), 1.806415e-02 (b) PASS
  group 2, SMI at start 1: starting mass 2.496183e-03 (a), 2.496183e-03 (b) PASS
  group 3, SMI at start 0: starting mass 5.122992e-03 (a), 5.122992e-03 (b) PASS
  group 3, SMI at start 1: starting mass 6.404701e-04 (a), 6.404701e-04 (b) PASS
  group 4, SMI at start 0: starting mass 3.377636e+00 (a), 3.377636e+00 (b) PASS
  group 4, SMI at start 1: starting mass 2.255530e-01 (a), 2.255530e-01 (b) PASS
GUARD SUMMARY: PASS

# THE REVOKED BY SMI AT REVOCATION

(a) Treatment First as it happened to them; (b) the same households, voucher kept, under Housing First's rules. Deaths include the end of life. Homeless and SMI shares are of the survivors. Per household made homeless: the three-year gap over the average rise (a)-(b) in the survivors' homeless share in years 1-3, as in code/paper/export_revoked.py.

## pooled, years 1-3

| group | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | 3-yr deaths (b) % | gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | per household made homeless pp | 4-yr gap pp | 6-yr gap pp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| with SMI | 12.15 | 96.70 | 45.4 | 8.31 | 6.40 | +1.92 | 50.8 / 52.2 / 52.8 | 0.0 / 0.0 / 0.0 | 3.7 | +2.48 | +3.49 |
| without SMI | 87.85 | 96.06 | 46.6 | 6.72 | 6.08 | +0.64 | 24.8 / 24.3 / 23.5 | 0.0 / 0.0 / 0.0 | 2.6 | +0.82 | +1.14 |
| all (unsplit) | 100.00 | 96.14 | 46.4 | 6.91 | 6.12 | +0.80 | 27.9 / 27.7 / 27.0 | 0.0 / 0.0 / 0.0 | 2.9 | +1.02 | +1.42 |

mass-weighted combination of the halves: 6.9129 (a), 6.1176 (b), gap +0.7953 pp; unsplit 6.9129, 6.1176, +0.7953

SMI among the survivors of the halves, years since revocation 0 / 1 / 2 / 3 / 6, (a) and (b): with SMI: 100.0, 100.0 / 93.4, 93.4 / 87.1, 87.2 / 81.3, 81.3 / 65.8, 66.0; without SMI: 0.0, 0.0 / 0.3, 0.3 / 0.6, 0.6 / 0.8, 0.8 / 1.4, 1.4

SUD among the survivors three years on, (a) and (b): with SMI 90.7, 90.4; without 86.2, 86.4

## year-1 cohort

| group | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | 3-yr deaths (b) % | gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | per household made homeless pp | 4-yr gap pp | 6-yr gap pp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| with SMI | 12.20 | 96.69 | 45.5 | 8.35 | 6.41 | +1.94 | 51.6 / 52.9 / 53.4 | 0.0 / 0.0 / 0.0 | 3.7 | +2.51 | +3.52 |
| without SMI | 87.80 | 96.06 | 46.6 | 6.75 | 6.09 | +0.65 | 25.4 / 24.8 / 23.8 | 0.0 / 0.0 / 0.0 | 2.6 | +0.84 | +1.15 |
| all (unsplit) | 100.00 | 96.14 | 46.4 | 6.94 | 6.13 | +0.81 | 28.6 / 28.2 / 27.4 | 0.0 / 0.0 / 0.0 | 2.9 | +1.04 | +1.44 |

mass-weighted combination of the halves: 6.9433 (a), 6.1328 (b), gap +0.8105 pp; unsplit 6.9433, 6.1328, +0.8105

SMI among the survivors of the halves, years since revocation 0 / 1 / 2 / 3 / 6, (a) and (b): with SMI: 100.0, 100.0 / 93.4, 93.4 / 87.1, 87.1 / 81.3, 81.3 / 65.8, 66.0; without SMI: 0.0, 0.0 / 0.3, 0.3 / 0.6, 0.6 / 0.8, 0.8 / 1.4, 1.4

SUD among the survivors three years on, (a) and (b): with SMI 90.7, 90.4; without 86.2, 86.4

## year-2 cohort

| group | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | 3-yr deaths (b) % | gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | per household made homeless pp | 4-yr gap pp | 6-yr gap pp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| with SMI | 12.14 | 96.71 | 45.6 | 8.36 | 6.48 | +1.89 | 48.8 / 50.6 / 51.7 | 0.0 / 0.0 / 0.0 | 3.7 | +2.45 | +3.45 |
| without SMI | 87.86 | 96.06 | 46.8 | 6.78 | 6.17 | +0.61 | 22.7 / 22.7 / 22.5 | 0.0 / 0.0 / 0.0 | 2.7 | +0.79 | +1.09 |
| all (unsplit) | 100.00 | 96.14 | 46.6 | 6.97 | 6.21 | +0.76 | 25.9 / 26.1 / 26.0 | 0.0 / 0.0 / 0.0 | 2.9 | +0.99 | +1.38 |

mass-weighted combination of the halves: 6.9749 (a), 6.2114 (b), gap +0.7635 pp; unsplit 6.9749, 6.2114, +0.7635

SMI among the survivors of the halves, years since revocation 0 / 1 / 2 / 3 / 6, (a) and (b): with SMI: 100.0, 100.0 / 93.4, 93.4 / 87.1, 87.1 / 81.3, 81.3 / 65.8, 66.0; without SMI: 0.0, 0.0 / 0.3, 0.3 / 0.6, 0.6 / 0.8, 0.8 / 1.4, 1.4

SUD among the survivors three years on, (a) and (b): with SMI 90.6, 90.4; without 86.1, 86.4

## year-3 cohort

| group | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | 3-yr deaths (b) % | gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | per household made homeless pp | 4-yr gap pp | 6-yr gap pp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| with SMI | 11.11 | 96.89 | 43.8 | 7.04 | 5.67 | +1.37 | 37.4 / 39.8 / 41.9 | 0.0 / 0.0 / 0.0 | 3.5 | +1.81 | +2.61 |
| without SMI | 88.89 | 96.18 | 45.2 | 5.82 | 5.38 | +0.43 | 16.9 / 17.7 / 18.3 | 0.0 / 0.0 / 0.0 | 2.5 | +0.57 | +0.82 |
| all (unsplit) | 100.00 | 96.26 | 45.1 | 5.95 | 5.41 | +0.54 | 19.2 / 20.1 / 20.9 | 0.0 / 0.0 / 0.0 | 2.7 | +0.71 | +1.02 |

mass-weighted combination of the halves: 5.9516 (a), 5.4131 (b), gap +0.5384 pp; unsplit 5.9516, 5.4131, +0.5384

SMI among the survivors of the halves, years since revocation 0 / 1 / 2 / 3 / 6, (a) and (b): with SMI: 100.0, 100.0 / 93.4, 93.4 / 87.1, 87.2 / 81.3, 81.3 / 65.9, 66.1; without SMI: 0.0, 0.0 / 0.3, 0.3 / 0.6, 0.6 / 0.9, 0.9 / 1.4, 1.4

SUD among the survivors three years on, (a) and (b): with SMI 90.5, 90.7; without 86.3, 86.8

## pooled, by years since revocation

| years since | deaths with SMI (a) % | (b) % | gap pp | deaths without SMI (a) % | (b) % | gap pp | all (a) % | (b) % | gap pp |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2.80 | 2.13 | +0.67 | 2.30 | 2.07 | +0.23 | 2.36 | 2.08 | +0.28 |
| 2 | 5.57 | 4.26 | +1.31 | 4.53 | 4.10 | +0.44 | 4.66 | 4.12 | +0.54 |
| 3 | 8.31 | 6.40 | +1.92 | 6.72 | 6.08 | +0.64 | 6.91 | 6.12 | +0.80 |
| 4 | 11.01 | 8.53 | +2.48 | 8.85 | 8.03 | +0.82 | 9.11 | 8.09 | +1.02 |
| 6 | 16.28 | 12.80 | +3.49 | 12.96 | 11.82 | +1.14 | 13.36 | 11.94 | +1.42 |

## every holder at the reform, by SMI at the reform (t = 0)

| group | share % | deaths at 3 yrs (a) % | (b) % | gap pp | homeless at 3 yrs (a) % | (b) % |
|---|---|---|---|---|---|---|
| with SMI | 6.26 | 4.92 | 4.81 | +0.11 | 4.70 | 0.00 |
| without SMI | 93.74 | 13.01 | 13.00 | +0.02 | 1.11 | 0.01 |
| all | 100.00 | 12.51 | 12.48 | +0.02 | 1.35 | 0.01 |

HEADLINE WITH SMI: 12.2 per cent of the revoked (pooled, years 1-3); three-year mortality 8.31 against 6.40 per cent, gap +1.92 pp; homeless 50.8, 52.2, 52.8 per cent in years 1-3; per household made homeless 3.7 pp
HEADLINE WITHOUT SMI: 87.8 per cent of the revoked (pooled, years 1-3); three-year mortality 6.72 against 6.08 per cent, gap +0.64 pp; homeless 24.8, 24.3, 23.5 per cent in years 1-3; per household made homeless 2.6 pp
HEADLINE ALL: 100.0 per cent of the revoked (pooled, years 1-3); three-year mortality 6.91 against 6.12 per cent, gap +0.80 pp; homeless 27.9, 27.7, 27.0 per cent in years 1-3; per household made homeless 2.9 pp
AGAINST code/revoked_2c (re-solved arms): 6.91 / 6.12 / +0.80 against 6.92 / 6.12 / +0.80
