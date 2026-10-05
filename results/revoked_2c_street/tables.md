# GUARDS (T = 10, four threads; the tracked numbers are serial and exact, see code/revoked_2c)
  Treatment First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 4.03e-13 (rule 1e-10) PASS
  Treatment First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 1.4e-05 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 3.0e-03 PASS
  Treatment First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Treatment First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Treatment First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Treatment First path: the four parts summed against the unsplit cohort, 192 comparisons (levels; shares times survivors): 16 bit for bit, worst relative difference 1.7e-13 (rule 1e-12); at the split, cell by cell, max |parts - cohort| = 0.0 over 3 splits (rule 0, a partition of cells) PASS
    (the parts move in separate passes through the same kernel and rejoin in the same cells, so a sum of four separately rounded passes can differ from the joint pass in the last bit; at the start the totals differ by 5.6e-14 relative, the order of summation over the same cells)
  Treatment First path: SMI share at revocation 1 in the SMI parts, 0 in the others (to 1e-12, the ratio of two sums): PASS
  Treatment First path: mass accounting in the parts, worst 4.1e-13 (rule 1e-10) PASS
    split of cohort 1 (at t = 2): no SMI housed 9.156809e-02, no SMI street 3.126860e-02, SMI housed 8.201136e-03, SMI street 8.864066e-03; cohort 1.399019e-01; at the last age (no choice, counted housed) 6.829e-05
    split of cohort 2 (at t = 3): no SMI housed 1.395761e-02, no SMI street 4.105548e-03, SMI housed 1.269657e-03, SMI street 1.226504e-03; cohort 2.055932e-02; at the last age (no choice, counted housed) 1.025e-05
    split of cohort 3 (at t = 4): no SMI housed 4.253289e-03, no SMI street 8.691618e-04, SMI housed 3.985375e-04, SMI street 2.418961e-04; cohort 5.762885e-03; at the last age (no choice, counted housed) 1.757e-06
  Housing First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 9.75e-14 (rule 1e-10) PASS
  Housing First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 4.6e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 8.0e-04 PASS
  Housing First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Housing First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Housing First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Housing First path: the four parts summed against the unsplit cohort, 192 comparisons (levels; shares times survivors): 39 bit for bit, worst relative difference 8.7e-14 (rule 1e-12); at the split, cell by cell, max |parts - cohort| = 0.0 over 3 splits (rule 0, a partition of cells) PASS
    (the parts move in separate passes through the same kernel and rejoin in the same cells, so a sum of four separately rounded passes can differ from the joint pass in the last bit; at the start the totals differ by 5.6e-14 relative, the order of summation over the same cells)
  Housing First path: SMI share at revocation 1 in the SMI parts, 0 in the others (to 1e-12, the ratio of two sums): PASS
  Housing First path: mass accounting in the parts, worst 1.7e-13 (rule 1e-10) PASS
    split of cohort 1 (at t = 2): no SMI housed 9.156809e-02, no SMI street 3.126860e-02, SMI housed 8.201136e-03, SMI street 8.864066e-03; cohort 1.399019e-01; at the last age (no choice, counted housed) 0.000e+00
    split of cohort 2 (at t = 3): no SMI housed 1.395761e-02, no SMI street 4.105548e-03, SMI housed 1.269657e-03, SMI street 1.226504e-03; cohort 2.055932e-02; at the last age (no choice, counted housed) 0.000e+00
    split of cohort 3 (at t = 4): no SMI housed 4.253289e-03, no SMI street 8.691618e-04, SMI housed 3.985375e-04, SMI street 2.418961e-04; cohort 5.762885e-03; at the last age (no choice, counted housed) 0.000e+00
  Treatment First path: the classification is the kernel's choice: one year after revocation the survivors' homeless share is 1 in every street part and 0 in every housed part, and the persistence mass equals the street part's survivors (12 parts) PASS
  cohort 1, no SMI, housed: starting mass 9.156809e-02 (a), 9.156809e-02 (b) PASS
  cohort 1, no SMI, on the street: starting mass 3.126860e-02 (a), 3.126860e-02 (b) PASS
  cohort 1, SMI, housed: starting mass 8.201136e-03 (a), 8.201136e-03 (b) PASS
  cohort 1, SMI, on the street: starting mass 8.864066e-03 (a), 8.864066e-03 (b) PASS
  cohort 2, no SMI, housed: starting mass 1.395761e-02 (a), 1.395761e-02 (b) PASS
  cohort 2, no SMI, on the street: starting mass 4.105548e-03 (a), 4.105548e-03 (b) PASS
  cohort 2, SMI, housed: starting mass 1.269657e-03 (a), 1.269657e-03 (b) PASS
  cohort 2, SMI, on the street: starting mass 1.226504e-03 (a), 1.226504e-03 (b) PASS
  cohort 3, no SMI, housed: starting mass 4.253289e-03 (a), 4.253289e-03 (b) PASS
  cohort 3, no SMI, on the street: starting mass 8.691618e-04 (a), 8.691618e-04 (b) PASS
  cohort 3, SMI, housed: starting mass 3.985375e-04 (a), 3.985375e-04 (b) PASS
  cohort 3, SMI, on the street: starting mass 2.418961e-04 (a), 2.418961e-04 (b) PASS
GUARD SUMMARY: PASS

# THE REVOKED BY SMI AT REVOCATION AND BY WHETHER THE REVOCATION PUTS THEM ON THE STREET

(a) Treatment First as it happened to them; (b) the same households, voucher kept, under Housing First's rules. 'On the street': Treatment First's first housing choice after the revocation (the step into the year after it) is the lowest housing grid point. Deaths include the end of life. Homeless, SUD and SMI shares are of the survivors. 'Still on the street': on the street in every year since the revocation, as a share of the survivors.

## pooled, years 1-3 (revoked mass 1.662241e-01)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 1.0332e-02 | 6.22 | 96.2 | 47.5 | 10.20 | 6.63 | +3.57 | +54 | +4.54 | +6.18 | 100.0 / 95.5 / 91.1 | 0.0 / 0.0 / 0.0 | 100.0 / 95.5 / 90.8 |
| SMI, housed | 9.8693e-03 | 5.94 | 97.2 | 43.3 | 6.34 | 6.15 | +0.18 | +3 | +0.33 | +0.66 | 0.0 / 8.2 / 14.3 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 3.6243e-02 | 21.80 | 97.2 | 46.8 | 6.97 | 4.64 | +2.33 | +50 | +2.88 | +3.73 | 100.0 / 84.2 / 71.0 | 0.0 / 0.0 / 0.0 | 100.0 / 84.2 / 70.8 |
| no SMI, housed | 1.0978e-01 | 66.04 | 95.7 | 46.5 | 6.64 | 6.56 | +0.08 | +1 | +0.14 | +0.28 | 0.0 / 4.6 / 7.8 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 2.0202e-02 | 12.15 | 96.7 | 45.4 | 8.31 | 6.40 | +1.92 | +30 | +2.48 | +3.48 | 50.8 / 52.2 / 52.8 | 0.0 / 0.0 / 0.0 | 100.0 / 95.5 / 90.8 |
| on the street, both | 4.6576e-02 | 28.02 | 97.0 | 47.0 | 7.68 | 5.08 | +2.60 | +51 | +3.25 | +4.27 | 100.0 / 86.7 / 75.3 | 0.0 / 0.0 / 0.0 | 100.0 / 86.7 / 75.1 |
| all (the four parts summed) | 1.6622e-01 | 100.00 | 96.1 | 46.4 | 6.91 | 6.12 | +0.80 | +13 | +1.02 | +1.42 | 27.9 / 27.7 / 27.0 | 0.0 / 0.0 / 0.0 | 100.0 / 86.7 / 75.1 |
| all (unsplit cohort lines) | 1.6622e-01 | 100.00 | 96.1 | 46.4 | 6.91 | 6.12 | +0.80 | +13 | +1.02 | +1.42 | 27.9 / 27.7 / 27.0 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 3.48 / 6.88 / 10.20 / 13.44 / 19.70 | 2.17 / 4.39 / 6.63 / 8.90 / 13.52 | 100.0, 100.0 / 81.2, 81.3 | 91.4, 89.9 | 0.8, 93.3 | 96.5 / 88.9 / 81.5 |
| SMI, housed | 2.09 / 4.21 / 6.34 / 8.47 / 12.70 | 2.09 / 4.14 / 6.15 / 8.14 / 12.04 | 100.0, 100.0 / 81.3, 81.3 | 89.9, 91.0 | 0.7, 68.9 | nan / nan / nan |
| no SMI, on the street | 2.42 / 4.73 / 6.97 / 9.13 / 13.32 | 1.51 / 3.06 / 4.64 / 6.26 / 9.59 | 0.0, 0.0 / 0.8, 0.8 | 87.8, 86.2 | 0.7, 76.7 | 97.6 / 80.3 / 65.8 |
| no SMI, housed | 2.26 / 4.47 / 6.64 / 8.76 / 12.84 | 2.26 / 4.44 / 6.56 / 8.61 / 12.57 | 0.0, 0.0 / 0.8, 0.9 | 85.7, 86.5 | 0.7, 59.3 | nan / nan / nan |
| SMI, both | 2.80 / 5.57 / 8.31 / 11.01 / 16.28 | 2.13 / 4.26 / 6.40 / 8.53 / 12.80 | 100.0, 100.0 / 81.3, 81.3 | 90.7, 90.4 | 0.8, 81.3 | 96.5 / 88.9 / 81.5 |
| on the street, both | 2.65 / 5.21 / 7.68 / 10.09 / 14.74 | 1.66 / 3.35 / 5.08 / 6.84 / 10.46 | 22.2, 22.2 / 18.1, 18.3 | 88.5, 87.0 | 0.7, 80.4 | 97.3 / 82.2 / 69.3 |

## year-1 cohort (revoked mass 1.399019e-01)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 8.8641e-03 | 6.34 | 96.2 | 47.5 | 10.19 | 6.62 | +3.57 | +54 | +4.54 | +6.17 | 100.0 / 95.5 / 91.1 | 0.0 / 0.0 / 0.0 | 100.0 / 95.5 / 90.8 |
| SMI, housed | 8.2011e-03 | 5.86 | 97.2 | 43.3 | 6.37 | 6.19 | +0.18 | +3 | +0.33 | +0.66 | 0.0 / 8.2 / 14.2 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 3.1269e-02 | 22.35 | 97.2 | 46.8 | 6.95 | 4.63 | +2.32 | +50 | +2.87 | +3.72 | 100.0 / 84.2 / 71.0 | 0.0 / 0.0 / 0.0 | 100.0 / 84.2 / 70.7 |
| no SMI, housed | 9.1568e-02 | 65.45 | 95.7 | 46.5 | 6.68 | 6.60 | +0.08 | +1 | +0.14 | +0.28 | 0.0 / 4.6 / 7.8 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 1.7065e-02 | 12.20 | 96.7 | 45.5 | 8.35 | 6.41 | +1.94 | +30 | +2.51 | +3.52 | 51.6 / 52.9 / 53.4 | 0.0 / 0.0 / 0.0 | 100.0 / 95.5 / 90.8 |
| on the street, both | 4.0133e-02 | 28.69 | 97.0 | 47.0 | 7.67 | 5.07 | +2.60 | +51 | +3.24 | +4.26 | 100.0 / 86.6 / 75.3 | 0.0 / 0.0 / 0.0 | 100.0 / 86.6 / 75.0 |
| all (the four parts summed) | 1.3990e-01 | 100.00 | 96.1 | 46.4 | 6.95 | 6.13 | +0.81 | +13 | +1.04 | +1.44 | 28.6 / 28.2 / 27.4 | 0.0 / 0.0 / 0.0 | 100.0 / 86.6 / 75.0 |
| all (unsplit cohort lines) | 1.3990e-01 | 100.00 | 96.1 | 46.4 | 6.95 | 6.13 | +0.81 | +13 | +1.04 | +1.44 | 28.6 / 28.2 / 27.4 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 3.47 / 6.87 / 10.19 / 13.43 / 19.68 | 2.17 / 4.38 / 6.62 / 8.89 / 13.50 | 100.0, 100.0 / 81.2, 81.3 | 91.4, 89.9 | 0.8, 93.3 | 96.5 / 88.9 / 81.5 |
| SMI, housed | 2.10 / 4.23 / 6.37 / 8.51 / 12.75 | 2.10 / 4.16 / 6.19 / 8.18 / 12.10 | 100.0, 100.0 / 81.3, 81.3 | 90.0, 91.0 | 0.7, 68.5 | nan / nan / nan |
| no SMI, on the street | 2.41 / 4.73 / 6.95 / 9.12 / 13.30 | 1.51 / 3.05 / 4.63 / 6.25 / 9.58 | 0.0, 0.0 / 0.8, 0.8 | 87.8, 86.2 | 0.7, 76.8 | 97.6 / 80.2 / 65.8 |
| no SMI, housed | 2.27 / 4.50 / 6.68 / 8.81 / 12.91 | 2.27 / 4.47 / 6.60 / 8.66 / 12.63 | 0.0, 0.0 / 0.8, 0.8 | 85.7, 86.4 | 0.7, 59.2 | nan / nan / nan |
| SMI, both | 2.81 / 5.60 / 8.35 / 11.06 / 16.35 | 2.14 / 4.28 / 6.41 / 8.55 / 12.83 | 100.0, 100.0 / 81.3, 81.3 | 90.7, 90.4 | 0.8, 81.4 | 96.5 / 88.9 / 81.5 |
| on the street, both | 2.65 / 5.20 / 7.67 / 10.07 / 14.71 | 1.66 / 3.35 / 5.07 / 6.83 / 10.44 | 22.1, 22.1 / 18.1, 18.3 | 88.5, 87.0 | 0.7, 80.4 | 97.4 / 82.1 / 69.3 |

## year-2 cohort (revoked mass 2.055932e-02)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 1.2265e-03 | 5.97 | 96.2 | 47.8 | 10.41 | 6.77 | +3.64 | +54 | +4.62 | +6.28 | 100.0 / 95.4 / 91.1 | 0.0 / 0.0 / 0.0 | 100.0 / 95.4 / 90.7 |
| SMI, housed | 1.2697e-03 | 6.18 | 97.2 | 43.5 | 6.39 | 6.19 | +0.19 | +3 | +0.35 | +0.70 | 0.0 / 8.5 / 15.3 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 4.1055e-03 | 19.97 | 97.2 | 47.2 | 7.14 | 4.75 | +2.39 | +50 | +2.95 | +3.83 | 100.0 / 84.6 / 71.4 | 0.0 / 0.0 / 0.0 | 100.0 / 84.6 / 71.2 |
| no SMI, housed | 1.3958e-02 | 67.89 | 95.7 | 46.7 | 6.68 | 6.60 | +0.08 | +1 | +0.15 | +0.29 | 0.0 / 4.6 / 8.2 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 2.4962e-03 | 12.14 | 96.7 | 45.6 | 8.36 | 6.48 | +1.89 | +29 | +2.45 | +3.44 | 48.8 / 50.5 / 51.7 | 0.0 / 0.0 / 0.0 | 100.0 / 95.4 / 90.7 |
| on the street, both | 5.3321e-03 | 25.93 | 97.0 | 47.3 | 7.89 | 5.21 | +2.68 | +51 | +3.34 | +4.39 | 100.0 / 87.0 / 75.8 | 0.0 / 0.0 / 0.0 | 100.0 / 87.0 / 75.6 |
| all (the four parts summed) | 2.0559e-02 | 100.00 | 96.1 | 46.6 | 6.98 | 6.21 | +0.76 | +12 | +0.99 | +1.38 | 25.8 / 26.1 / 26.0 | 0.0 / 0.0 / 0.0 | 100.0 / 87.0 / 75.6 |
| all (unsplit cohort lines) | 2.0559e-02 | 100.00 | 96.1 | 46.6 | 6.98 | 6.21 | +0.76 | +12 | +0.99 | +1.38 | 25.8 / 26.1 / 26.0 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 3.55 / 7.02 / 10.41 / 13.71 / 20.08 | 2.22 / 4.48 / 6.77 / 9.09 / 13.80 | 100.0, 100.0 / 81.2, 81.3 | 91.4, 89.8 | 0.8, 93.2 | 96.4 / 88.7 / 81.3 |
| SMI, housed | 2.10 / 4.23 / 6.39 / 8.54 / 12.83 | 2.10 / 4.16 / 6.19 / 8.19 / 12.13 | 100.0, 100.0 / 81.3, 81.3 | 89.8, 91.0 | 0.7, 70.5 | nan / nan / nan |
| no SMI, on the street | 2.48 / 4.85 / 7.14 / 9.35 / 13.63 | 1.55 / 3.13 / 4.75 / 6.40 / 9.81 | 0.0, 0.0 / 0.7, 0.7 | 87.7, 86.0 | 0.7, 76.2 | 97.5 / 80.5 / 66.1 |
| no SMI, housed | 2.27 / 4.50 / 6.68 / 8.82 / 12.94 | 2.27 / 4.47 / 6.60 / 8.67 / 12.65 | 0.0, 0.0 / 0.8, 0.8 | 85.7, 86.5 | 0.7, 60.2 | nan / nan / nan |
| SMI, both | 2.81 / 5.60 / 8.36 / 11.08 / 16.39 | 2.16 / 4.32 / 6.48 / 8.63 / 12.95 | 100.0, 100.0 / 81.3, 81.3 | 90.6, 90.4 | 0.8, 81.6 | 96.4 / 88.7 / 81.3 |
| on the street, both | 2.72 / 5.35 / 7.89 / 10.36 / 15.12 | 1.70 / 3.44 / 5.21 / 7.02 / 10.72 | 23.0, 23.0 / 18.8, 19.0 | 88.5, 86.9 | 0.7, 80.1 | 97.3 / 82.4 / 69.6 |

## year-3 cohort (revoked mass 5.762885e-03)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 2.4190e-04 | 4.20 | 96.2 | 46.7 | 9.65 | 6.27 | +3.38 | +54 | +4.31 | +5.90 | 100.0 / 95.0 / 90.9 | 0.0 / 0.0 / 0.0 | 100.0 / 95.0 / 90.4 |
| SMI, housed | 3.9854e-04 | 6.92 | 97.3 | 42.0 | 5.46 | 5.31 | +0.16 | +3 | +0.29 | +0.61 | 0.0 / 7.2 / 13.5 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 8.6916e-04 | 15.08 | 97.2 | 46.1 | 6.62 | 4.40 | +2.22 | +50 | +2.75 | +3.58 | 100.0 / 84.5 / 71.4 | 0.0 / 0.0 / 0.0 | 100.0 / 84.5 / 71.1 |
| no SMI, housed | 4.2533e-03 | 73.80 | 96.0 | 45.1 | 5.65 | 5.58 | +0.07 | +1 | +0.13 | +0.25 | 0.0 / 4.1 / 7.5 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 6.4043e-04 | 11.11 | 96.9 | 43.8 | 7.04 | 5.67 | +1.37 | +24 | +1.81 | +2.60 | 37.4 / 39.8 / 41.9 | 0.0 / 0.0 / 0.0 | 100.0 / 95.0 / 90.4 |
| on the street, both | 1.1111e-03 | 19.28 | 97.0 | 46.2 | 7.28 | 4.81 | +2.47 | +51 | +3.09 | +4.08 | 100.0 / 86.7 / 75.6 | 0.0 / 0.0 / 0.0 | 100.0 / 86.7 / 75.2 |
| all (the four parts summed) | 5.7629e-03 | 100.00 | 96.3 | 45.1 | 5.95 | 5.42 | +0.54 | +10 | +0.71 | +1.02 | 19.2 / 20.1 / 20.9 | 0.0 / 0.0 / 0.0 | 100.0 / 86.7 / 75.2 |
| all (unsplit cohort lines) | 5.7629e-03 | 100.00 | 96.3 | 45.1 | 5.95 | 5.42 | +0.54 | +10 | +0.71 | +1.02 | 19.2 / 20.1 / 20.9 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 3.29 / 6.50 / 9.65 / 12.73 / 18.71 | 2.05 / 4.14 / 6.27 / 8.42 / 12.81 | 100.0, 100.0 / 81.3, 81.3 | 91.4, 89.9 | 0.8, 93.5 | 96.7 / 88.9 / 81.7 |
| SMI, housed | 1.78 / 3.61 / 5.46 / 7.34 / 11.14 | 1.78 / 3.55 / 5.31 / 7.05 / 10.53 | 100.0, 100.0 / 81.4, 81.4 | 89.9, 91.1 | 0.7, 70.5 | nan / nan / nan |
| no SMI, on the street | 2.29 / 4.49 / 6.62 / 8.68 / 12.69 | 1.43 / 2.90 / 4.40 / 5.93 / 9.11 | 0.0, 0.0 / 0.8, 0.8 | 87.9, 86.4 | 0.7, 76.8 | 97.7 / 80.7 / 66.4 |
| no SMI, housed | 1.89 / 3.78 / 5.65 / 7.51 / 11.17 | 1.89 / 3.76 / 5.58 / 7.39 / 10.92 | 0.0, 0.0 / 0.9, 0.9 | 86.0, 86.9 | 0.6, 59.6 | nan / nan / nan |
| SMI, both | 2.35 / 4.70 / 7.04 / 9.38 / 14.00 | 1.89 / 3.77 / 5.67 / 7.57 / 11.39 | 100.0, 100.0 / 81.3, 81.3 | 90.5, 90.7 | 0.7, 79.1 | 96.7 / 88.9 / 81.7 |
| on the street, both | 2.51 / 4.93 / 7.28 / 9.56 / 14.00 | 1.57 / 3.17 / 4.81 / 6.48 / 9.91 | 21.8, 21.8 / 17.9, 18.1 | 88.6, 87.2 | 0.7, 80.4 | 97.5 / 82.5 / 69.8 |

HEADLINE SMI, on the street: 6.2 per cent of the revoked; three-year mortality 10.20 (a) against 6.63 (b), gap +3.57 pp (+54 per cent); homeless (a) 100.0, 95.5, 91.1 in years 1-3
HEADLINE SMI, housed: 5.9 per cent of the revoked; three-year mortality 6.34 (a) against 6.15 (b), gap +0.18 pp (+3 per cent); homeless (a) 0.0, 8.2, 14.3 in years 1-3
HEADLINE no SMI, on the street: 21.8 per cent of the revoked; three-year mortality 6.97 (a) against 4.64 (b), gap +2.33 pp (+50 per cent); homeless (a) 100.0, 84.2, 71.0 in years 1-3
HEADLINE no SMI, housed: 66.0 per cent of the revoked; three-year mortality 6.64 (a) against 6.56 (b), gap +0.08 pp (+1 per cent); homeless (a) 0.0, 4.6, 7.8 in years 1-3
HEADLINE all (unsplit cohort lines): 100.0 per cent of the revoked; three-year mortality 6.91 (a) against 6.12 (b), gap +0.80 pp (+13 per cent); homeless (a) 27.9, 27.7, 27.0 in years 1-3
AGAINST code/revoked_2c (re-solved arms): 6.91 / 6.12 / +0.80 against 6.92 / 6.12 / +0.80
