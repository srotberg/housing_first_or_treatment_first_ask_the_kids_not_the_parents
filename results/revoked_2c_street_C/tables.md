# GUARDS (T = 10, four threads; the tracked numbers are serial and exact, see code/revoked_2c)
  Treatment First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 3.73e-13 (rule 1e-10) PASS
  Treatment First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 4.0e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 1.1e-03 PASS
  Treatment First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Treatment First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Treatment First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Treatment First path: the four parts summed against the unsplit cohort, 192 comparisons (levels; shares times survivors): 17 bit for bit, worst relative difference 1.2e-13 (rule 1e-12); at the split, cell by cell, max |parts - cohort| = 0.0 over 3 splits (rule 0, a partition of cells) PASS
    (the parts move in separate passes through the same kernel and rejoin in the same cells, so a sum of four separately rounded passes can differ from the joint pass in the last bit; at the start the totals differ by 5.3e-14 relative, the order of summation over the same cells)
  Treatment First path: SMI share at revocation 1 in the SMI parts, 0 in the others (to 1e-12, the ratio of two sums): PASS
  Treatment First path: mass accounting in the parts, worst 4.4e-13 (rule 1e-10) PASS
    split of cohort 1 (at t = 2): no SMI housed 4.785602e-03, no SMI street 1.350082e-10, SMI housed 4.614199e-04, SMI street 4.968718e-08; cohort 5.247072e-03; at the last age (no choice, counted housed) 1.607e-05
    split of cohort 2 (at t = 3): no SMI housed 3.973235e-03, no SMI street 9.621703e-11, SMI housed 3.864253e-04, SMI street 4.512919e-08; cohort 4.359706e-03; at the last age (no choice, counted housed) 1.286e-05
    split of cohort 3 (at t = 4): no SMI housed 3.474269e-03, no SMI street 9.189889e-11, SMI housed 3.401732e-04, SMI street 4.087245e-08; cohort 3.814483e-03; at the last age (no choice, counted housed) 1.036e-05
  Housing First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 8.41e-14 (rule 1e-10) PASS
  Housing First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 8.3e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 1.4e-03 PASS
  Housing First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Housing First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Housing First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Housing First path: the four parts summed against the unsplit cohort, 192 comparisons (levels; shares times survivors): 38 bit for bit, worst relative difference 6.3e-14 (rule 1e-12); at the split, cell by cell, max |parts - cohort| = 0.0 over 3 splits (rule 0, a partition of cells) PASS
    (the parts move in separate passes through the same kernel and rejoin in the same cells, so a sum of four separately rounded passes can differ from the joint pass in the last bit; at the start the totals differ by 5.3e-14 relative, the order of summation over the same cells)
  Housing First path: SMI share at revocation 1 in the SMI parts, 0 in the others (to 1e-12, the ratio of two sums): PASS
  Housing First path: mass accounting in the parts, worst 1.6e-13 (rule 1e-10) PASS
    split of cohort 1 (at t = 2): no SMI housed 4.785602e-03, no SMI street 1.350082e-10, SMI housed 4.614199e-04, SMI street 4.968718e-08; cohort 5.247072e-03; at the last age (no choice, counted housed) 0.000e+00
    split of cohort 2 (at t = 3): no SMI housed 3.973235e-03, no SMI street 9.621703e-11, SMI housed 3.864253e-04, SMI street 4.512919e-08; cohort 4.359706e-03; at the last age (no choice, counted housed) 0.000e+00
    split of cohort 3 (at t = 4): no SMI housed 3.474269e-03, no SMI street 9.189889e-11, SMI housed 3.401732e-04, SMI street 4.087245e-08; cohort 3.814483e-03; at the last age (no choice, counted housed) 0.000e+00
  Treatment First path: the classification is the kernel's choice: one year after revocation the survivors' homeless share is 1 in every street part and 0 in every housed part, and the persistence mass equals the street part's survivors (12 parts) PASS
  cohort 1, no SMI, housed: starting mass 4.785602e-03 (a), 4.785602e-03 (b) PASS
  cohort 1, no SMI, on the street: starting mass 1.350082e-10 (a), 1.350082e-10 (b) PASS
  cohort 1, SMI, housed: starting mass 4.614199e-04 (a), 4.614199e-04 (b) PASS
  cohort 1, SMI, on the street: starting mass 4.968718e-08 (a), 4.968718e-08 (b) PASS
  cohort 2, no SMI, housed: starting mass 3.973235e-03 (a), 3.973235e-03 (b) PASS
  cohort 2, no SMI, on the street: starting mass 9.621703e-11 (a), 9.621703e-11 (b) PASS
  cohort 2, SMI, housed: starting mass 3.864253e-04 (a), 3.864253e-04 (b) PASS
  cohort 2, SMI, on the street: starting mass 4.512919e-08 (a), 4.512919e-08 (b) PASS
  cohort 3, no SMI, housed: starting mass 3.474269e-03 (a), 3.474269e-03 (b) PASS
  cohort 3, no SMI, on the street: starting mass 9.189889e-11 (a), 9.189889e-11 (b) PASS
  cohort 3, SMI, housed: starting mass 3.401732e-04 (a), 3.401732e-04 (b) PASS
  cohort 3, SMI, on the street: starting mass 4.087245e-08 (a), 4.087245e-08 (b) PASS
GUARD SUMMARY: PASS

# THE REVOKED BY SMI AT REVOCATION AND BY WHETHER THE REVOCATION PUTS THEM ON THE STREET

(a) Treatment First as it happened to them; (b) the same households, voucher kept, under Housing First's rules. 'On the street': Treatment First's first housing choice after the revocation (the step into the year after it) is the lowest housing grid point. Deaths include the end of life. Homeless, SUD and SMI shares are of the survivors. 'Still on the street': on the street in every year since the revocation, as a share of the survivors.

## pooled, years 1-3 (revoked mass 1.342126e-02)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 1.3569e-07 | 0.00 | 99.5 | 54.9 | 12.73 | 10.48 | +2.24 | +21 | +2.16 | +3.66 | 100.0 / 4.1 / 11.0 | 0.0 / 0.0 / 0.0 | 100.0 / 4.1 / 0.3 |
| SMI, housed | 1.1880e-03 | 8.85 | 97.9 | 48.1 | 11.41 | 11.41 | +0.00 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.6 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 3.2312e-10 | 0.00 | 97.9 | 64.7 | 18.35 | 14.71 | +3.64 | +25 | +3.59 | +3.47 | 100.0 / 27.3 / 0.0 | 0.0 / 0.0 / 0.0 | 100.0 / 27.3 / 0.0 |
| no SMI, housed | 1.2233e-02 | 91.15 | 97.0 | 49.5 | 12.50 | 12.50 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 1.1882e-03 | 8.85 | 97.9 | 48.1 | 11.41 | 11.41 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.6 | 0.0 / 0.0 / 0.0 | 100.0 / 4.1 / 0.3 |
| on the street, both | 1.3601e-07 | 0.00 | 99.5 | 54.9 | 12.74 | 10.49 | +2.25 | +21 | +2.16 | +3.66 | 100.0 / 4.1 / 11.0 | 0.0 / 0.0 / 0.0 | 100.0 / 4.1 / 0.3 |
| all (the four parts summed) | 1.3421e-02 | 100.00 | 97.1 | 49.4 | 12.41 | 12.40 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | 100.0 / 4.1 / 0.3 |
| all (unsplit cohort lines) | 1.3421e-02 | 100.00 | 97.1 | 49.4 | 12.41 | 12.40 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 5.57 / 9.08 / 12.73 / 16.14 / 24.60 | 3.48 / 6.98 / 10.48 / 13.98 / 20.95 | 100.0, 100.0 / 81.2, 81.2 | 92.1, 92.8 | 4.6, 96.2 | 94.4 / 3.7 / 0.2 |
| SMI, housed | 4.05 / 7.84 / 11.41 / 14.76 / 20.90 | 4.05 / 7.84 / 11.41 / 14.75 / 20.86 | 100.0, 100.0 / 81.3, 81.3 | 91.5, 91.6 | 2.5, 49.3 | nan / nan / nan |
| no SMI, on the street | 7.86 / 13.51 / 18.35 / 23.12 / 32.38 | 4.91 / 9.82 / 14.71 / 19.54 / 28.91 | 0.0, 0.0 / 0.3, 0.3 | 87.1, 83.2 | 4.5, 95.5 | 92.1 / 23.6 / 0.0 |
| no SMI, housed | 4.56 / 8.72 / 12.50 / 15.95 / 21.94 | 4.56 / 8.71 / 12.50 / 15.93 / 21.90 | 0.0, 0.0 / 0.9, 0.9 | 87.9, 88.0 | 2.5, 48.7 | nan / nan / nan |
| SMI, both | 4.05 / 7.84 / 11.41 / 14.76 / 20.90 | 4.05 / 7.84 / 11.41 / 14.75 / 20.86 | 100.0, 100.0 / 81.3, 81.3 | 91.5, 91.6 | 2.5, 49.3 | 94.4 / 3.7 / 0.2 |
| on the street, both | 5.57 / 9.10 / 12.74 / 16.16 / 24.62 | 3.48 / 6.98 / 10.49 / 14.00 / 20.96 | 99.8, 99.8 / 81.0, 81.1 | 92.1, 92.8 | 4.6, 96.2 | 94.4 / 3.8 / 0.2 |

## year-1 cohort (revoked mass 5.247072e-03)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 4.9687e-08 | 0.00 | 99.5 | 54.8 | 12.71 | 10.47 | +2.24 | +21 | +2.15 | +3.63 | 100.0 / 4.2 / 11.0 | 0.0 / 0.0 / 0.0 | 100.0 / 4.2 / 0.3 |
| SMI, housed | 4.6142e-04 | 8.79 | 97.9 | 47.8 | 11.43 | 11.42 | +0.00 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 1.3501e-10 | 0.00 | 97.9 | 64.7 | 18.32 | 14.75 | +3.56 | +24 | +3.51 | +3.40 | 100.0 / 24.3 / 0.0 | 0.0 / 0.0 / 0.0 | 100.0 / 24.3 / 0.0 |
| no SMI, housed | 4.7856e-03 | 91.21 | 97.0 | 49.4 | 12.62 | 12.62 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 4.6147e-04 | 8.79 | 97.9 | 47.8 | 11.43 | 11.42 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | 100.0 / 4.2 / 0.3 |
| on the street, both | 4.9822e-08 | 0.00 | 99.5 | 54.9 | 12.73 | 10.48 | +2.24 | +21 | +2.15 | +3.63 | 100.0 / 4.2 / 10.9 | 0.0 / 0.0 / 0.0 | 100.0 / 4.2 / 0.3 |
| all (the four parts summed) | 5.2471e-03 | 100.00 | 97.1 | 49.2 | 12.52 | 12.51 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | 100.0 / 4.2 / 0.3 |
| all (unsplit cohort lines) | 5.2471e-03 | 100.00 | 97.1 | 49.2 | 12.52 | 12.51 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 5.56 / 9.08 / 12.71 / 16.12 / 24.55 | 3.48 / 6.97 / 10.47 / 13.97 / 20.92 | 100.0, 100.0 / 81.2, 81.2 | 92.1, 92.8 | 4.6, 96.2 | 94.4 / 3.8 / 0.2 |
| SMI, housed | 4.06 / 7.87 / 11.43 / 14.77 / 20.86 | 4.06 / 7.87 / 11.42 / 14.76 / 20.82 | 100.0, 100.0 / 81.3, 81.3 | 91.6, 91.6 | 2.5, 49.2 | nan / nan / nan |
| no SMI, on the street | 7.88 / 13.46 / 18.32 / 23.10 / 32.38 | 4.93 / 9.85 / 14.75 / 19.59 / 28.98 | 0.0, 0.0 / 0.3, 0.3 | 87.0, 83.2 | 4.6, 96.0 | 92.1 / 21.1 / 0.0 |
| no SMI, housed | 4.61 / 8.81 / 12.62 / 16.08 / 22.07 | 4.61 / 8.81 / 12.62 / 16.07 / 22.03 | 0.0, 0.0 / 0.9, 0.9 | 88.0, 88.1 | 2.5, 48.6 | nan / nan / nan |
| SMI, both | 4.06 / 7.87 / 11.43 / 14.77 / 20.87 | 4.06 / 7.87 / 11.42 / 14.76 / 20.82 | 100.0, 100.0 / 81.3, 81.3 | 91.6, 91.6 | 2.5, 49.2 | 94.4 / 3.8 / 0.2 |
| on the street, both | 5.57 / 9.09 / 12.73 / 16.14 / 24.57 | 3.48 / 6.98 / 10.48 / 13.98 / 20.94 | 99.7, 99.7 / 81.0, 81.0 | 92.1, 92.8 | 4.6, 96.2 | 94.4 / 3.8 / 0.2 |

## year-2 cohort (revoked mass 4.359706e-03)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 4.5129e-08 | 0.00 | 99.5 | 54.9 | 12.68 | 10.44 | +2.24 | +21 | +2.15 | +3.65 | 100.0 / 4.0 / 11.1 | 0.0 / 0.0 / 0.0 | 100.0 / 4.0 / 0.3 |
| SMI, housed | 3.8643e-04 | 8.86 | 97.9 | 48.2 | 11.46 | 11.45 | +0.00 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.6 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 9.6217e-11 | 0.00 | 97.9 | 64.7 | 18.35 | 14.71 | +3.64 | +25 | +3.59 | +3.47 | 100.0 / 27.5 / 0.0 | 0.0 / 0.0 / 0.0 | 100.0 / 27.5 / 0.0 |
| no SMI, housed | 3.9732e-03 | 91.14 | 97.0 | 49.6 | 12.55 | 12.54 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 3.8647e-04 | 8.86 | 97.9 | 48.2 | 11.46 | 11.45 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.6 | 0.0 / 0.0 / 0.0 | 100.0 / 4.0 / 0.3 |
| on the street, both | 4.5225e-08 | 0.00 | 99.5 | 54.9 | 12.69 | 10.45 | +2.24 | +21 | +2.15 | +3.65 | 100.0 / 4.1 / 11.0 | 0.0 / 0.0 / 0.0 | 100.0 / 4.1 / 0.3 |
| all (the four parts summed) | 4.3597e-03 | 100.00 | 97.1 | 49.5 | 12.45 | 12.45 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | 100.0 / 4.1 / 0.3 |
| all (unsplit cohort lines) | 4.3597e-03 | 100.00 | 97.1 | 49.5 | 12.45 | 12.45 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 5.54 / 9.05 / 12.68 / 16.08 / 24.52 | 3.47 / 6.95 / 10.44 / 13.93 / 20.87 | 100.0, 100.0 / 81.2, 81.2 | 92.1, 92.8 | 4.6, 96.2 | 94.5 / 3.7 / 0.3 |
| SMI, housed | 4.06 / 7.88 / 11.46 / 14.82 / 20.99 | 4.06 / 7.88 / 11.45 / 14.81 / 20.94 | 100.0, 100.0 / 81.3, 81.3 | 91.5, 91.6 | 2.5, 49.4 | nan / nan / nan |
| no SMI, on the street | 7.86 / 13.51 / 18.35 / 23.13 / 32.38 | 4.91 / 9.82 / 14.71 / 19.53 / 28.90 | 0.0, 0.0 / 0.3, 0.3 | 87.1, 83.2 | 4.5, 95.4 | 92.1 / 23.8 / 0.0 |
| no SMI, housed | 4.58 / 8.75 / 12.55 / 16.01 / 22.02 | 4.58 / 8.75 / 12.54 / 15.99 / 21.98 | 0.0, 0.0 / 0.9, 0.9 | 87.9, 88.0 | 2.5, 48.8 | nan / nan / nan |
| SMI, both | 4.06 / 7.88 / 11.46 / 14.82 / 20.99 | 4.06 / 7.88 / 11.45 / 14.81 / 20.94 | 100.0, 100.0 / 81.3, 81.3 | 91.5, 91.6 | 2.5, 49.4 | 94.5 / 3.7 / 0.3 |
| on the street, both | 5.55 / 9.06 / 12.69 / 16.09 / 24.54 | 3.47 / 6.96 / 10.45 / 13.94 / 20.89 | 99.8, 99.8 / 81.0, 81.1 | 92.1, 92.8 | 4.6, 96.2 | 94.5 / 3.7 / 0.3 |

## year-3 cohort (revoked mass 3.814483e-03)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 4.0872e-08 | 0.00 | 99.5 | 55.0 | 12.80 | 10.54 | +2.26 | +21 | +2.17 | +3.69 | 100.0 / 4.0 / 11.0 | 0.0 / 0.0 / 0.0 | 100.0 / 4.0 / 0.3 |
| SMI, housed | 3.4017e-04 | 8.92 | 97.9 | 48.3 | 11.33 | 11.33 | +0.00 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.6 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 9.1899e-11 | 0.00 | 97.9 | 64.6 | 18.39 | 14.65 | +3.74 | +26 | +3.69 | +3.57 | 100.0 / 31.3 / 0.0 | 0.0 / 0.0 / 0.0 | 100.0 / 31.3 / 0.0 |
| no SMI, housed | 3.4743e-03 | 91.08 | 96.9 | 49.7 | 12.28 | 12.27 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 3.4021e-04 | 8.92 | 97.9 | 48.3 | 11.33 | 11.33 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.6 | 0.0 / 0.0 / 0.0 | 100.0 / 4.0 / 0.3 |
| on the street, both | 4.0964e-08 | 0.00 | 99.5 | 55.0 | 12.82 | 10.55 | +2.26 | +21 | +2.17 | +3.69 | 100.0 / 4.1 / 11.0 | 0.0 / 0.0 / 0.0 | 100.0 / 4.1 / 0.3 |
| all (the four parts summed) | 3.8145e-03 | 100.00 | 97.0 | 49.6 | 12.20 | 12.19 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | 100.0 / 4.1 / 0.3 |
| all (unsplit cohort lines) | 3.8145e-03 | 100.00 | 97.0 | 49.6 | 12.20 | 12.19 | +0.01 | +0 | +0.01 | +0.04 | 0.0 / 0.1 / 0.7 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 5.60 / 9.14 / 12.80 / 16.23 / 24.75 | 3.50 / 7.02 / 10.54 / 14.06 / 21.06 | 100.0, 100.0 / 81.2, 81.2 | 92.2, 92.8 | 4.6, 96.2 | 94.4 / 3.7 / 0.2 |
| SMI, housed | 4.01 / 7.78 / 11.33 / 14.69 / 20.85 | 4.01 / 7.78 / 11.33 / 14.68 / 20.81 | 100.0, 100.0 / 81.3, 81.3 | 91.5, 91.6 | 2.5, 49.5 | nan / nan / nan |
| no SMI, on the street | 7.83 / 13.57 / 18.39 / 23.15 / 32.38 | 4.89 / 9.78 / 14.65 / 19.47 / 28.81 | 0.0, 0.0 / 0.3, 0.3 | 87.2, 83.2 | 4.5, 95.1 | 92.2 / 27.0 / 0.0 |
| no SMI, housed | 4.46 / 8.55 / 12.28 / 15.70 / 21.67 | 4.46 / 8.54 / 12.27 / 15.68 / 21.64 | 0.0, 0.0 / 0.9, 0.9 | 87.8, 87.9 | 2.5, 48.8 | nan / nan / nan |
| SMI, both | 4.01 / 7.78 / 11.33 / 14.69 / 20.85 | 4.01 / 7.78 / 11.33 / 14.68 / 20.81 | 100.0, 100.0 / 81.3, 81.3 | 91.5, 91.6 | 2.5, 49.5 | 94.4 / 3.7 / 0.2 |
| on the street, both | 5.60 / 9.15 / 12.82 / 16.25 / 24.76 | 3.50 / 7.02 / 10.55 / 14.08 / 21.08 | 99.8, 99.8 / 81.0, 81.1 | 92.2, 92.8 | 4.6, 96.2 | 94.4 / 3.7 / 0.2 |

HEADLINE SMI, on the street: 0.0 per cent of the revoked; three-year mortality 12.73 (a) against 10.48 (b), gap +2.24 pp (+21 per cent); homeless (a) 100.0, 4.1, 11.0 in years 1-3
HEADLINE SMI, housed: 8.9 per cent of the revoked; three-year mortality 11.41 (a) against 11.41 (b), gap +0.00 pp (+0 per cent); homeless (a) 0.0, 0.1, 0.6 in years 1-3
HEADLINE no SMI, on the street: 0.0 per cent of the revoked; three-year mortality 18.35 (a) against 14.71 (b), gap +3.64 pp (+25 per cent); homeless (a) 100.0, 27.3, 0.0 in years 1-3
HEADLINE no SMI, housed: 91.1 per cent of the revoked; three-year mortality 12.50 (a) against 12.50 (b), gap +0.01 pp (+0 per cent); homeless (a) 0.0, 0.1, 0.7 in years 1-3
HEADLINE all (unsplit cohort lines): 100.0 per cent of the revoked; three-year mortality 12.41 (a) against 12.40 (b), gap +0.01 pp (+0 per cent); homeless (a) 0.0, 0.1, 0.7 in years 1-3
AGAINST code/revoked_2c (re-solved arms): 12.41 / 12.40 / +0.01 against 6.92 / 6.12 / +0.80
