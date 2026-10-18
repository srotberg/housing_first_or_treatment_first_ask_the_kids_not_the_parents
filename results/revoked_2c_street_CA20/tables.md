# GUARDS (T = 10, four threads; the tracked numbers are serial and exact, see code/revoked_2c)
  Treatment First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 3.33e-13 (rule 1e-10) PASS
  Treatment First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 7.1e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 1.5e-03 PASS
  Treatment First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Treatment First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Treatment First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Treatment First path: the four parts summed against the unsplit cohort, 192 comparisons (levels; shares times survivors): 16 bit for bit, worst relative difference 1.2e-13 (rule 1e-12); at the split, cell by cell, max |parts - cohort| = 0.0 over 3 splits (rule 0, a partition of cells) PASS
    (the parts move in separate passes through the same kernel and rejoin in the same cells, so a sum of four separately rounded passes can differ from the joint pass in the last bit; at the start the totals differ by 4.2e-14 relative, the order of summation over the same cells)
  Treatment First path: SMI share at revocation 1 in the SMI parts, 0 in the others (to 1e-12, the ratio of two sums): PASS
  Treatment First path: mass accounting in the parts, worst 4.0e-13 (rule 1e-10) PASS
    split of cohort 1 (at t = 2): no SMI housed 2.142703e-02, no SMI street 7.416731e-03, SMI housed 1.934541e-03, SMI street 2.097723e-03; cohort 3.287603e-02; at the last age (no choice, counted housed) 1.575e-05
    split of cohort 2 (at t = 3): no SMI housed 1.737178e-02, no SMI street 5.293361e-03, SMI housed 1.597153e-03, SMI street 1.552591e-03; cohort 2.581489e-02; at the last age (no choice, counted housed) 1.260e-05
    split of cohort 3 (at t = 4): no SMI housed 1.453492e-02, no SMI street 3.912234e-03, SMI housed 1.356654e-03, SMI street 1.174289e-03; cohort 2.097809e-02; at the last age (no choice, counted housed) 1.014e-05
  Housing First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 1.16e-13 (rule 1e-10) PASS
  Housing First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 9.0e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 2.5e-03 PASS
  Housing First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Housing First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Housing First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Housing First path: the four parts summed against the unsplit cohort, 192 comparisons (levels; shares times survivors): 36 bit for bit, worst relative difference 6.3e-14 (rule 1e-12); at the split, cell by cell, max |parts - cohort| = 0.0 over 3 splits (rule 0, a partition of cells) PASS
    (the parts move in separate passes through the same kernel and rejoin in the same cells, so a sum of four separately rounded passes can differ from the joint pass in the last bit; at the start the totals differ by 4.2e-14 relative, the order of summation over the same cells)
  Housing First path: SMI share at revocation 1 in the SMI parts, 0 in the others (to 1e-12, the ratio of two sums): PASS
  Housing First path: mass accounting in the parts, worst 1.7e-13 (rule 1e-10) PASS
    split of cohort 1 (at t = 2): no SMI housed 2.142703e-02, no SMI street 7.416731e-03, SMI housed 1.934541e-03, SMI street 2.097723e-03; cohort 3.287603e-02; at the last age (no choice, counted housed) 0.000e+00
    split of cohort 2 (at t = 3): no SMI housed 1.737178e-02, no SMI street 5.293361e-03, SMI housed 1.597153e-03, SMI street 1.552591e-03; cohort 2.581489e-02; at the last age (no choice, counted housed) 0.000e+00
    split of cohort 3 (at t = 4): no SMI housed 1.453492e-02, no SMI street 3.912234e-03, SMI housed 1.356654e-03, SMI street 1.174289e-03; cohort 2.097809e-02; at the last age (no choice, counted housed) 0.000e+00
  Treatment First path: the classification is the kernel's choice: one year after revocation the survivors' homeless share is 1 in every street part and 0 in every housed part, and the persistence mass equals the street part's survivors (12 parts) PASS
  cohort 1, no SMI, housed: starting mass 2.142703e-02 (a), 2.142703e-02 (b) PASS
  cohort 1, no SMI, on the street: starting mass 7.416731e-03 (a), 7.416731e-03 (b) PASS
  cohort 1, SMI, housed: starting mass 1.934541e-03 (a), 1.934541e-03 (b) PASS
  cohort 1, SMI, on the street: starting mass 2.097723e-03 (a), 2.097723e-03 (b) PASS
  cohort 2, no SMI, housed: starting mass 1.737178e-02 (a), 1.737178e-02 (b) PASS
  cohort 2, no SMI, on the street: starting mass 5.293361e-03 (a), 5.293361e-03 (b) PASS
  cohort 2, SMI, housed: starting mass 1.597153e-03 (a), 1.597153e-03 (b) PASS
  cohort 2, SMI, on the street: starting mass 1.552591e-03 (a), 1.552591e-03 (b) PASS
  cohort 3, no SMI, housed: starting mass 1.453492e-02 (a), 1.453492e-02 (b) PASS
  cohort 3, no SMI, on the street: starting mass 3.912234e-03 (a), 3.912234e-03 (b) PASS
  cohort 3, SMI, housed: starting mass 1.356654e-03 (a), 1.356654e-03 (b) PASS
  cohort 3, SMI, on the street: starting mass 1.174289e-03 (a), 1.174289e-03 (b) PASS
GUARD SUMMARY: PASS

# THE REVOKED BY SMI AT REVOCATION AND BY WHETHER THE REVOCATION PUTS THEM ON THE STREET

(a) Treatment First as it happened to them; (b) the same households, voucher kept, under Housing First's rules. 'On the street': Treatment First's first housing choice after the revocation (the step into the year after it) is the lowest housing grid point. Deaths include the end of life. Homeless, SUD and SMI shares are of the survivors. 'Still on the street': on the street in every year since the revocation, as a share of the survivors.

## pooled, years 1-3 (revoked mass 7.966901e-02)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 4.8246e-03 | 6.06 | 96.3 | 47.7 | 10.30 | 6.71 | +3.59 | +54 | +4.53 | +6.04 | 100.0 / 95.4 / 89.5 | 0.0 / 0.0 / 0.0 | 100.0 / 95.4 / 89.3 |
| SMI, housed | 4.8883e-03 | 6.14 | 97.3 | 43.5 | 6.39 | 6.20 | +0.19 | +3 | +0.34 | +0.68 | 0.0 / 8.6 / 15.0 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 1.6622e-02 | 20.86 | 97.2 | 46.8 | 6.91 | 4.60 | +2.30 | +50 | +2.84 | +3.63 | 100.0 / 83.8 / 69.5 | 0.0 / 0.0 / 0.0 | 100.0 / 83.8 / 69.2 |
| no SMI, housed | 5.3334e-02 | 66.94 | 95.8 | 46.6 | 6.60 | 6.51 | +0.09 | +1 | +0.15 | +0.29 | 0.0 / 4.9 / 8.2 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 9.7130e-03 | 12.19 | 96.8 | 45.6 | 8.34 | 6.45 | +1.88 | +29 | +2.42 | +3.34 | 49.3 / 51.1 / 51.2 | 0.0 / 0.0 / 0.0 | 100.0 / 95.4 / 89.3 |
| on the street, both | 2.1447e-02 | 26.92 | 97.0 | 47.0 | 7.67 | 5.08 | +2.59 | +51 | +3.22 | +4.17 | 100.0 / 86.3 / 73.9 | 0.0 / 0.0 / 0.0 | 100.0 / 86.3 / 73.6 |
| all (the four parts summed) | 7.9669e-02 | 100.00 | 96.2 | 46.5 | 6.87 | 6.11 | +0.77 | +13 | +0.99 | +1.36 | 26.8 / 26.9 / 26.1 | 0.0 / 0.0 / 0.0 | 100.0 / 86.3 / 73.6 |
| all (unsplit cohort lines) | 7.9669e-02 | 100.00 | 96.2 | 46.5 | 6.87 | 6.11 | +0.77 | +13 | +0.99 | +1.36 | 26.8 / 26.9 / 26.1 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 3.52 / 6.96 / 10.30 / 13.54 / 19.72 | 2.20 / 4.44 / 6.71 / 9.01 / 13.68 | 100.0, 100.0 / 81.2, 81.3 | 91.4, 89.9 | 4.2, 93.3 | 96.5 / 88.7 / 80.1 |
| SMI, housed | 2.10 / 4.24 / 6.39 / 8.54 / 12.82 | 2.10 / 4.17 / 6.20 / 8.21 / 12.15 | 100.0, 100.0 / 81.3, 81.3 | 90.3, 91.1 | 3.2, 70.1 | nan / nan / nan |
| no SMI, on the street | 2.40 / 4.70 / 6.91 / 9.04 / 13.15 | 1.50 / 3.03 / 4.60 / 6.21 / 9.52 | 0.0, 0.0 / 0.8, 0.8 | 88.2, 86.2 | 3.6, 77.1 | 97.6 / 79.8 / 64.4 |
| no SMI, housed | 2.24 / 4.44 / 6.60 / 8.71 / 12.79 | 2.24 / 4.41 / 6.51 / 8.56 / 12.51 | 0.0, 0.0 / 0.8, 0.8 | 85.9, 86.5 | 2.8, 59.5 | nan / nan / nan |
| SMI, both | 2.81 / 5.59 / 8.34 / 11.03 / 16.25 | 2.15 / 4.30 / 6.45 / 8.61 / 12.91 | 100.0, 100.0 / 81.3, 81.3 | 90.9, 90.5 | 3.7, 81.6 | 96.5 / 88.7 / 80.1 |
| on the street, both | 2.65 / 5.21 / 7.67 / 10.06 / 14.63 | 1.66 / 3.35 / 5.08 / 6.84 / 10.46 | 22.5, 22.5 / 18.3, 18.6 | 88.9, 87.0 | 3.7, 80.7 | 97.3 / 81.8 / 67.9 |

## year-1 cohort (revoked mass 3.287603e-02)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 2.0977e-03 | 6.38 | 96.2 | 47.4 | 10.16 | 6.61 | +3.55 | +54 | +4.47 | +5.97 | 100.0 / 95.5 / 89.6 | 0.0 / 0.0 / 0.0 | 100.0 / 95.5 / 89.4 |
| SMI, housed | 1.9345e-03 | 5.88 | 97.3 | 43.3 | 6.38 | 6.20 | +0.18 | +3 | +0.32 | +0.64 | 0.0 / 8.3 / 14.2 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 7.4167e-03 | 22.56 | 97.2 | 46.6 | 6.80 | 4.54 | +2.27 | +50 | +2.79 | +3.58 | 100.0 / 83.8 / 69.6 | 0.0 / 0.0 / 0.0 | 100.0 / 83.8 / 69.3 |
| no SMI, housed | 2.1427e-02 | 65.18 | 95.7 | 46.5 | 6.60 | 6.52 | +0.08 | +1 | +0.14 | +0.27 | 0.0 / 4.8 / 7.8 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 4.0323e-03 | 12.27 | 96.7 | 45.5 | 8.34 | 6.41 | +1.93 | +30 | +2.48 | +3.41 | 51.7 / 53.0 / 52.7 | 0.0 / 0.0 / 0.0 | 100.0 / 95.5 / 89.4 |
| on the street, both | 9.5145e-03 | 28.94 | 97.0 | 46.8 | 7.54 | 4.99 | +2.55 | +51 | +3.16 | +4.11 | 100.0 / 86.3 / 73.9 | 0.0 / 0.0 / 0.0 | 100.0 / 86.3 / 73.6 |
| all (the four parts summed) | 3.2876e-02 | 100.00 | 96.2 | 46.4 | 6.86 | 6.06 | +0.80 | +13 | +1.03 | +1.40 | 28.9 / 28.5 / 27.2 | 0.0 / 0.0 / 0.0 | 100.0 / 86.3 / 73.6 |
| all (unsplit cohort lines) | 3.2876e-02 | 100.00 | 96.2 | 46.4 | 6.86 | 6.06 | +0.80 | +13 | +1.03 | +1.40 | 28.9 / 28.5 / 27.2 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 3.47 / 6.86 / 10.16 / 13.35 / 19.46 | 2.17 / 4.37 / 6.61 / 8.88 / 13.49 | 100.0, 100.0 / 81.2, 81.3 | 91.4, 89.9 | 4.2, 93.3 | 96.5 / 88.9 / 80.3 |
| SMI, housed | 2.10 / 4.24 / 6.38 / 8.52 / 12.76 | 2.10 / 4.17 / 6.20 / 8.20 / 12.12 | 100.0, 100.0 / 81.3, 81.3 | 90.4, 91.1 | 3.2, 68.6 | nan / nan / nan |
| no SMI, on the street | 2.36 / 4.63 / 6.80 / 8.91 / 12.97 | 1.48 / 2.99 / 4.54 / 6.12 / 9.39 | 0.0, 0.0 / 0.8, 0.8 | 88.2, 86.3 | 3.6, 77.3 | 97.6 / 80.0 / 64.6 |
| no SMI, housed | 2.24 / 4.45 / 6.60 / 8.71 / 12.78 | 2.24 / 4.41 / 6.52 / 8.57 / 12.51 | 0.0, 0.0 / 0.8, 0.8 | 85.9, 86.5 | 2.8, 58.9 | nan / nan / nan |
| SMI, both | 2.81 / 5.60 / 8.34 / 11.03 / 16.24 | 2.14 / 4.27 / 6.41 / 8.55 / 12.83 | 100.0, 100.0 / 81.3, 81.3 | 90.9, 90.4 | 3.7, 81.4 | 96.5 / 88.9 / 80.3 |
| on the street, both | 2.61 / 5.12 / 7.54 / 9.89 / 14.40 | 1.63 / 3.29 / 4.99 / 6.73 / 10.29 | 22.0, 22.0 / 18.0, 18.2 | 88.9, 87.1 | 3.7, 80.7 | 97.4 / 81.9 / 68.1 |

## year-2 cohort (revoked mass 2.581489e-02)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 1.5526e-03 | 6.01 | 96.3 | 47.8 | 10.36 | 6.75 | +3.61 | +54 | +4.55 | +6.07 | 100.0 / 95.4 / 89.5 | 0.0 / 0.0 / 0.0 | 100.0 / 95.4 / 89.2 |
| SMI, housed | 1.5972e-03 | 6.19 | 97.3 | 43.6 | 6.40 | 6.21 | +0.19 | +3 | +0.34 | +0.69 | 0.0 / 8.7 / 15.3 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 5.2934e-03 | 20.51 | 97.2 | 46.9 | 6.95 | 4.63 | +2.32 | +50 | +2.85 | +3.66 | 100.0 / 83.7 / 69.5 | 0.0 / 0.0 / 0.0 | 100.0 / 83.7 / 69.2 |
| no SMI, housed | 1.7372e-02 | 67.29 | 95.8 | 46.6 | 6.61 | 6.52 | +0.09 | +1 | +0.15 | +0.29 | 0.0 / 5.0 / 8.3 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 3.1497e-03 | 12.20 | 96.8 | 45.6 | 8.35 | 6.47 | +1.88 | +29 | +2.42 | +3.34 | 48.9 / 50.8 / 51.1 | 0.0 / 0.0 / 0.0 | 100.0 / 95.4 / 89.2 |
| on the street, both | 6.8460e-03 | 26.52 | 97.0 | 47.1 | 7.72 | 5.11 | +2.61 | +51 | +3.24 | +4.20 | 100.0 / 86.3 / 73.9 | 0.0 / 0.0 / 0.0 | 100.0 / 86.3 / 73.6 |
| all (the four parts summed) | 2.5815e-02 | 100.00 | 96.2 | 46.6 | 6.89 | 6.13 | +0.76 | +12 | +0.98 | +1.35 | 26.4 / 26.7 / 26.0 | 0.0 / 0.0 / 0.0 | 100.0 / 86.3 / 73.6 |
| all (unsplit cohort lines) | 2.5815e-02 | 100.00 | 96.2 | 46.6 | 6.89 | 6.13 | +0.76 | +12 | +0.98 | +1.35 | 26.4 / 26.7 / 26.0 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 3.54 / 7.00 / 10.36 / 13.62 / 19.82 | 2.21 / 4.46 / 6.75 / 9.06 / 13.76 | 100.0, 100.0 / 81.2, 81.3 | 91.4, 89.9 | 4.2, 93.2 | 96.5 / 88.7 / 80.0 |
| SMI, housed | 2.11 / 4.25 / 6.40 / 8.56 / 12.85 | 2.11 / 4.17 / 6.21 / 8.22 / 12.17 | 100.0, 100.0 / 81.3, 81.3 | 90.3, 91.0 | 3.2, 70.4 | nan / nan / nan |
| no SMI, on the street | 2.41 / 4.73 / 6.95 / 9.10 / 13.24 | 1.51 / 3.05 / 4.63 / 6.25 / 9.58 | 0.0, 0.0 / 0.8, 0.8 | 88.1, 86.2 | 3.6, 77.0 | 97.6 / 79.8 / 64.4 |
| no SMI, housed | 2.24 / 4.45 / 6.61 / 8.73 / 12.82 | 2.24 / 4.42 / 6.52 / 8.57 / 12.53 | 0.0, 0.0 / 0.8, 0.8 | 85.9, 86.5 | 2.8, 59.7 | nan / nan / nan |
| SMI, both | 2.81 / 5.60 / 8.35 / 11.05 / 16.29 | 2.16 / 4.32 / 6.47 / 8.63 / 12.95 | 100.0, 100.0 / 81.3, 81.3 | 90.8, 90.5 | 3.7, 81.6 | 96.5 / 88.7 / 80.0 |
| on the street, both | 2.67 / 5.24 / 7.72 / 10.12 / 14.73 | 1.67 / 3.37 / 5.11 / 6.89 / 10.53 | 22.7, 22.7 / 18.5, 18.7 | 88.9, 87.0 | 3.7, 80.6 | 97.3 / 81.8 / 67.9 |

## year-3 cohort (revoked mass 2.097809e-02)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 1.1743e-03 | 5.60 | 96.3 | 48.0 | 10.49 | 6.84 | +3.65 | +53 | +4.60 | +6.12 | 100.0 / 95.2 / 89.3 | 0.0 / 0.0 / 0.0 | 100.0 / 95.2 / 89.0 |
| SMI, housed | 1.3567e-03 | 6.47 | 97.3 | 43.8 | 6.40 | 6.19 | +0.20 | +3 | +0.36 | +0.72 | 0.0 / 8.9 / 15.9 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 3.9122e-03 | 18.65 | 97.2 | 47.1 | 7.04 | 4.69 | +2.35 | +50 | +2.89 | +3.70 | 100.0 / 83.7 / 69.4 | 0.0 / 0.0 / 0.0 | 100.0 / 83.7 / 69.0 |
| no SMI, housed | 1.4535e-02 | 69.29 | 95.8 | 46.7 | 6.58 | 6.49 | +0.09 | +1 | +0.16 | +0.30 | 0.0 / 5.1 / 8.6 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 2.5309e-03 | 12.06 | 96.8 | 45.7 | 8.30 | 6.49 | +1.80 | +28 | +2.33 | +3.23 | 46.0 / 48.3 / 49.2 | 0.0 / 0.0 / 0.0 | 100.0 / 95.2 / 89.0 |
| on the street, both | 5.0865e-03 | 24.25 | 97.0 | 47.3 | 7.84 | 5.19 | +2.65 | +51 | +3.28 | +4.26 | 100.0 / 86.3 / 73.8 | 0.0 / 0.0 / 0.0 | 100.0 / 86.3 / 73.5 |
| all (the four parts summed) | 2.0978e-02 | 100.00 | 96.2 | 46.7 | 6.87 | 6.15 | +0.72 | +12 | +0.93 | +1.29 | 24.2 / 24.9 / 24.8 | 0.0 / 0.0 / 0.0 | 100.0 / 86.3 / 73.5 |
| all (unsplit cohort lines) | 2.0978e-02 | 100.00 | 96.2 | 46.7 | 6.87 | 6.15 | +0.72 | +12 | +0.93 | +1.29 | 24.2 / 24.9 / 24.8 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 3.59 / 7.09 / 10.49 / 13.78 / 20.06 | 2.24 / 4.53 / 6.84 / 9.18 / 13.94 | 100.0, 100.0 / 81.2, 81.3 | 91.4, 89.9 | 4.2, 93.2 | 96.4 / 88.4 / 79.7 |
| SMI, housed | 2.10 / 4.23 / 6.40 / 8.56 / 12.89 | 2.10 / 4.16 / 6.19 / 8.20 / 12.17 | 100.0, 100.0 / 81.3, 81.3 | 90.2, 91.0 | 3.3, 71.8 | nan / nan / nan |
| no SMI, on the street | 2.44 / 4.79 / 7.04 / 9.22 / 13.40 | 1.53 / 3.09 / 4.69 / 6.33 / 9.70 | 0.0, 0.0 / 0.8, 0.7 | 88.1, 86.1 | 3.6, 76.9 | 97.6 / 79.7 / 64.2 |
| no SMI, housed | 2.23 / 4.42 / 6.58 / 8.69 / 12.79 | 2.23 / 4.39 / 6.49 / 8.53 / 12.48 | 0.0, 0.0 / 0.8, 0.8 | 85.8, 86.5 | 2.9, 60.2 | nan / nan / nan |
| SMI, both | 2.79 / 5.56 / 8.30 / 10.99 / 16.22 | 2.17 / 4.33 / 6.49 / 8.66 / 12.99 | 100.0, 100.0 / 81.3, 81.3 | 90.8, 90.5 | 3.7, 81.7 | 96.4 / 88.4 / 79.7 |
| on the street, both | 2.71 / 5.32 / 7.84 / 10.27 / 14.93 | 1.69 / 3.42 / 5.19 / 6.99 / 10.68 | 23.1, 23.1 / 18.8, 19.0 | 88.9, 87.0 | 3.7, 80.6 | 97.3 / 81.7 / 67.8 |

HEADLINE SMI, on the street: 6.1 per cent of the revoked; three-year mortality 10.30 (a) against 6.71 (b), gap +3.59 pp (+54 per cent); homeless (a) 100.0, 95.4, 89.5 in years 1-3
HEADLINE SMI, housed: 6.1 per cent of the revoked; three-year mortality 6.39 (a) against 6.20 (b), gap +0.19 pp (+3 per cent); homeless (a) 0.0, 8.6, 15.0 in years 1-3
HEADLINE no SMI, on the street: 20.9 per cent of the revoked; three-year mortality 6.91 (a) against 4.60 (b), gap +2.30 pp (+50 per cent); homeless (a) 100.0, 83.8, 69.5 in years 1-3
HEADLINE no SMI, housed: 66.9 per cent of the revoked; three-year mortality 6.60 (a) against 6.51 (b), gap +0.09 pp (+1 per cent); homeless (a) 0.0, 4.9, 8.2 in years 1-3
HEADLINE all (unsplit cohort lines): 100.0 per cent of the revoked; three-year mortality 6.87 (a) against 6.11 (b), gap +0.77 pp (+13 per cent); homeless (a) 26.8, 26.9, 26.1 in years 1-3
AGAINST code/revoked_2c (re-solved arms): 6.87 / 6.11 / +0.77 against 6.92 / 6.12 / +0.80
