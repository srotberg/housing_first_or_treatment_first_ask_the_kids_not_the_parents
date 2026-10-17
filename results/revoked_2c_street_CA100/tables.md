# GUARDS (T = 10, four threads; the tracked numbers are serial and exact, see code/revoked_2c)
  Treatment First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 2.54e-13 (rule 1e-10) PASS
  Treatment First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 3.4e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 6.3e-04 PASS
  Treatment First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Treatment First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Treatment First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Treatment First path: the four parts summed against the unsplit cohort, 192 comparisons (levels; shares times survivors): 125 bit for bit, worst relative difference 8.4e-14 (rule 1e-12); at the split, cell by cell, max |parts - cohort| = 0.0 over 3 splits (rule 0, a partition of cells) PASS
    (the parts move in separate passes through the same kernel and rejoin in the same cells, so a sum of four separately rounded passes can differ from the joint pass in the last bit; at the start the totals differ by 6.0e-14 relative, the order of summation over the same cells)
  Treatment First path: SMI share at revocation 1 in the SMI parts, 0 in the others (to 1e-12, the ratio of two sums): PASS
  Treatment First path: mass accounting in the parts, worst 3.4e-13 (rule 1e-10) PASS
    split of cohort 1 (at t = 2): no SMI housed 1.078230e-01, no SMI street 3.641727e-02, SMI housed 9.704991e-03, SMI street 1.046222e-02; cohort 1.644075e-01; at the last age (no choice, counted housed) 7.876e-05
    split of cohort 2 (at t = 3): no SMI housed 0.000000e+00, no SMI street 0.000000e+00, SMI housed 0.000000e+00, SMI street 0.000000e+00; cohort 0.000000e+00; at the last age (no choice, counted housed) 0.000e+00
    split of cohort 3 (at t = 4): no SMI housed 0.000000e+00, no SMI street 0.000000e+00, SMI housed 0.000000e+00, SMI street 0.000000e+00; cohort 0.000000e+00; at the last age (no choice, counted housed) 0.000e+00
  Housing First path: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = 1.06e-13 (rule 1e-10) PASS
  Housing First path: shadow kernel against the model's own step (ages 2+), worst sum of |gap| / mass alive = 6.7e-06 (rule 1e-04; four threads: bounded by the model's race, exact on one thread at T = 3); worst single cell / largest cell 9.0e-04 PASS
  Housing First path: price printed in 9 years: [1.0001082]; pi_V: [0.067533863] PASS
  Housing First path: mass the model's reduction drops each year (below the last age's renter floor; booked as an end-of-life exit): t=1 0.00e+00, t=2 0.00e+00, t=3 0.00e+00, t=4 0.00e+00, t=5 0.00e+00, t=6 0.00e+00, t=7 0.00e+00, t=8 0.00e+00, t=9 0.00e+00
  Housing First path: one pass and stopped cleanly: True, runtime errors: 0 PASS
  Housing First path: the four parts summed against the unsplit cohort, 192 comparisons (levels; shares times survivors): 133 bit for bit, worst relative difference 7.0e-14 (rule 1e-12); at the split, cell by cell, max |parts - cohort| = 0.0 over 3 splits (rule 0, a partition of cells) PASS
    (the parts move in separate passes through the same kernel and rejoin in the same cells, so a sum of four separately rounded passes can differ from the joint pass in the last bit; at the start the totals differ by 6.0e-14 relative, the order of summation over the same cells)
  Housing First path: SMI share at revocation 1 in the SMI parts, 0 in the others (to 1e-12, the ratio of two sums): PASS
  Housing First path: mass accounting in the parts, worst 1.5e-13 (rule 1e-10) PASS
    split of cohort 1 (at t = 2): no SMI housed 1.078230e-01, no SMI street 3.641727e-02, SMI housed 9.704991e-03, SMI street 1.046222e-02; cohort 1.644075e-01; at the last age (no choice, counted housed) 0.000e+00
    split of cohort 2 (at t = 3): no SMI housed 0.000000e+00, no SMI street 0.000000e+00, SMI housed 0.000000e+00, SMI street 0.000000e+00; cohort 0.000000e+00; at the last age (no choice, counted housed) 0.000e+00
    split of cohort 3 (at t = 4): no SMI housed 0.000000e+00, no SMI street 0.000000e+00, SMI housed 0.000000e+00, SMI street 0.000000e+00; cohort 0.000000e+00; at the last age (no choice, counted housed) 0.000e+00
  Treatment First path: the classification is the kernel's choice: one year after revocation the survivors' homeless share is 1 in every street part and 0 in every housed part, and the persistence mass equals the street part's survivors (4 parts) PASS
  cohort 1, no SMI, housed: starting mass 1.078230e-01 (a), 1.078230e-01 (b) PASS
  cohort 1, no SMI, on the street: starting mass 3.641727e-02 (a), 3.641727e-02 (b) PASS
  cohort 1, SMI, housed: starting mass 9.704991e-03 (a), 9.704991e-03 (b) PASS
  cohort 1, SMI, on the street: starting mass 1.046222e-02 (a), 1.046222e-02 (b) PASS
  cohort 2, no SMI, housed: starting mass 0.000000e+00 (a), 0.000000e+00 (b) PASS
  cohort 2, no SMI, on the street: starting mass 0.000000e+00 (a), 0.000000e+00 (b) PASS
  cohort 2, SMI, housed: starting mass 0.000000e+00 (a), 0.000000e+00 (b) PASS
  cohort 2, SMI, on the street: starting mass 0.000000e+00 (a), 0.000000e+00 (b) PASS
  cohort 3, no SMI, housed: starting mass 0.000000e+00 (a), 0.000000e+00 (b) PASS
  cohort 3, no SMI, on the street: starting mass 0.000000e+00 (a), 0.000000e+00 (b) PASS
  cohort 3, SMI, housed: starting mass 0.000000e+00 (a), 0.000000e+00 (b) PASS
  cohort 3, SMI, on the street: starting mass 0.000000e+00 (a), 0.000000e+00 (b) PASS
GUARD SUMMARY: PASS

# THE REVOKED BY SMI AT REVOCATION AND BY WHETHER THE REVOCATION PUTS THEM ON THE STREET

(a) Treatment First as it happened to them; (b) the same households, voucher kept, under Housing First's rules. 'On the street': Treatment First's first housing choice after the revocation (the step into the year after it) is the lowest housing grid point. Deaths include the end of life. Homeless, SUD and SMI shares are of the survivors. 'Still on the street': on the street in every year since the revocation, as a share of the survivors.

(cohorts with no revoked mass, left out: 2, 3)

## pooled, years 1-3 (revoked mass 1.644075e-01)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 1.0462e-02 | 6.36 | 96.2 | 47.5 | 10.20 | 6.62 | +3.57 | +54 | +4.55 | +6.20 | 100.0 / 95.5 / 91.4 | 0.0 / 0.0 / 0.0 | 100.0 / 95.5 / 91.1 |
| SMI, housed | 9.7050e-03 | 5.90 | 97.3 | 43.3 | 6.37 | 6.18 | +0.18 | +3 | +0.33 | +0.66 | 0.0 / 8.2 / 14.3 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 3.6417e-02 | 22.15 | 97.2 | 46.7 | 6.87 | 4.57 | +2.30 | +50 | +2.85 | +3.71 | 100.0 / 84.3 / 71.4 | 0.0 / 0.0 / 0.0 | 100.0 / 84.3 / 71.2 |
| no SMI, housed | 1.0782e-01 | 65.58 | 95.7 | 46.4 | 6.58 | 6.50 | +0.08 | +1 | +0.14 | +0.27 | 0.0 / 4.5 / 7.6 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 2.0167e-02 | 12.27 | 96.7 | 45.5 | 8.35 | 6.41 | +1.94 | +30 | +2.52 | +3.54 | 51.5 / 52.9 / 53.5 | 0.0 / 0.0 / 0.0 | 100.0 / 95.5 / 91.1 |
| on the street, both | 4.6879e-02 | 28.51 | 97.0 | 46.9 | 7.61 | 5.03 | +2.58 | +51 | +3.23 | +4.27 | 100.0 / 86.8 / 75.7 | 0.0 / 0.0 / 0.0 | 100.0 / 86.8 / 75.5 |
| all (the four parts summed) | 1.6441e-01 | 100.00 | 96.2 | 46.4 | 6.86 | 6.06 | +0.80 | +13 | +1.03 | +1.43 | 28.4 / 28.1 / 27.3 | 0.0 / 0.0 / 0.0 | 100.0 / 86.8 / 75.5 |
| all (unsplit cohort lines) | 1.6441e-01 | 100.00 | 96.2 | 46.4 | 6.86 | 6.06 | +0.80 | +13 | +1.03 | +1.43 | 28.4 / 28.1 / 27.3 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 3.48 / 6.87 / 10.20 / 13.45 / 19.72 | 2.17 / 4.38 / 6.62 / 8.90 / 13.51 | 100.0, 100.0 / 81.2, 81.3 | 91.4, 89.9 | 0.3, 93.3 | 96.5 / 88.9 / 81.8 |
| SMI, housed | 2.10 / 4.23 / 6.37 / 8.50 / 12.75 | 2.10 / 4.16 / 6.18 / 8.18 / 12.09 | 100.0, 100.0 / 81.3, 81.3 | 90.0, 91.0 | 0.3, 68.6 | nan / nan / nan |
| no SMI, on the street | 2.38 / 4.66 / 6.87 / 9.01 / 13.17 | 1.49 / 3.01 / 4.57 / 6.16 / 9.45 | 0.0, 0.0 / 0.8, 0.8 | 87.8, 86.2 | 0.3, 76.9 | 97.6 / 80.4 / 66.3 |
| no SMI, housed | 2.24 / 4.43 / 6.58 / 8.68 / 12.74 | 2.24 / 4.40 / 6.50 / 8.54 / 12.47 | 0.0, 0.0 / 0.8, 0.9 | 85.8, 86.5 | 0.3, 59.0 | nan / nan / nan |
| SMI, both | 2.81 / 5.60 / 8.35 / 11.07 / 16.37 | 2.14 / 4.27 / 6.41 / 8.55 / 12.83 | 100.0, 100.0 / 81.3, 81.3 | 90.7, 90.4 | 0.3, 81.4 | 96.5 / 88.9 / 81.8 |
| on the street, both | 2.62 / 5.16 / 7.61 / 10.00 / 14.63 | 1.64 / 3.32 / 5.03 / 6.77 / 10.36 | 22.3, 22.3 / 18.2, 18.4 | 88.6, 87.0 | 0.3, 80.5 | 97.4 / 82.3 / 69.7 |

## year-1 cohort (revoked mass 1.644075e-01)

| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % | 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMI, on the street | 1.0462e-02 | 6.36 | 96.2 | 47.5 | 10.20 | 6.62 | +3.57 | +54 | +4.55 | +6.20 | 100.0 / 95.5 / 91.4 | 0.0 / 0.0 / 0.0 | 100.0 / 95.5 / 91.1 |
| SMI, housed | 9.7050e-03 | 5.90 | 97.3 | 43.3 | 6.37 | 6.18 | +0.18 | +3 | +0.33 | +0.66 | 0.0 / 8.2 / 14.3 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| no SMI, on the street | 3.6417e-02 | 22.15 | 97.2 | 46.7 | 6.87 | 4.57 | +2.30 | +50 | +2.85 | +3.71 | 100.0 / 84.3 / 71.4 | 0.0 / 0.0 / 0.0 | 100.0 / 84.3 / 71.2 |
| no SMI, housed | 1.0782e-01 | 65.58 | 95.7 | 46.4 | 6.58 | 6.50 | +0.08 | +1 | +0.14 | +0.27 | 0.0 / 4.5 / 7.6 | 0.0 / 0.0 / 0.0 | nan / nan / nan |
| SMI, both | 2.0167e-02 | 12.27 | 96.7 | 45.5 | 8.35 | 6.41 | +1.94 | +30 | +2.52 | +3.54 | 51.5 / 52.9 / 53.5 | 0.0 / 0.0 / 0.0 | 100.0 / 95.5 / 91.1 |
| on the street, both | 4.6879e-02 | 28.51 | 97.0 | 46.9 | 7.61 | 5.03 | +2.58 | +51 | +3.23 | +4.27 | 100.0 / 86.8 / 75.7 | 0.0 / 0.0 / 0.0 | 100.0 / 86.8 / 75.5 |
| all (the four parts summed) | 1.6441e-01 | 100.00 | 96.2 | 46.4 | 6.86 | 6.06 | +0.80 | +13 | +1.03 | +1.43 | 28.4 / 28.1 / 27.3 | 0.0 / 0.0 / 0.0 | 100.0 / 86.8 / 75.5 |
| all (unsplit cohort lines) | 1.6441e-01 | 100.00 | 96.2 | 46.4 | 6.86 | 6.06 | +0.80 | +13 | +1.03 | +1.43 | 28.4 / 28.1 / 27.3 | 0.0 / 0.0 / 0.0 | nan / nan / nan |

| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % | SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |
|---|---|---|---|---|---|---|
| SMI, on the street | 3.48 / 6.87 / 10.20 / 13.45 / 19.72 | 2.17 / 4.38 / 6.62 / 8.90 / 13.51 | 100.0, 100.0 / 81.2, 81.3 | 91.4, 89.9 | 0.3, 93.3 | 96.5 / 88.9 / 81.8 |
| SMI, housed | 2.10 / 4.23 / 6.37 / 8.50 / 12.75 | 2.10 / 4.16 / 6.18 / 8.18 / 12.09 | 100.0, 100.0 / 81.3, 81.3 | 90.0, 91.0 | 0.3, 68.6 | nan / nan / nan |
| no SMI, on the street | 2.38 / 4.66 / 6.87 / 9.01 / 13.17 | 1.49 / 3.01 / 4.57 / 6.16 / 9.45 | 0.0, 0.0 / 0.8, 0.8 | 87.8, 86.2 | 0.3, 76.9 | 97.6 / 80.4 / 66.3 |
| no SMI, housed | 2.24 / 4.43 / 6.58 / 8.68 / 12.74 | 2.24 / 4.40 / 6.50 / 8.54 / 12.47 | 0.0, 0.0 / 0.8, 0.9 | 85.8, 86.5 | 0.3, 59.0 | nan / nan / nan |
| SMI, both | 2.81 / 5.60 / 8.35 / 11.07 / 16.37 | 2.14 / 4.27 / 6.41 / 8.55 / 12.83 | 100.0, 100.0 / 81.3, 81.3 | 90.7, 90.4 | 0.3, 81.4 | 96.5 / 88.9 / 81.8 |
| on the street, both | 2.62 / 5.16 / 7.61 / 10.00 / 14.63 | 1.64 / 3.32 / 5.03 / 6.77 / 10.36 | 22.3, 22.3 / 18.2, 18.4 | 88.6, 87.0 | 0.3, 80.5 | 97.4 / 82.3 / 69.7 |

HEADLINE SMI, on the street: 6.4 per cent of the revoked; three-year mortality 10.20 (a) against 6.62 (b), gap +3.57 pp (+54 per cent); homeless (a) 100.0, 95.5, 91.4 in years 1-3
HEADLINE SMI, housed: 5.9 per cent of the revoked; three-year mortality 6.37 (a) against 6.18 (b), gap +0.18 pp (+3 per cent); homeless (a) 0.0, 8.2, 14.3 in years 1-3
HEADLINE no SMI, on the street: 22.2 per cent of the revoked; three-year mortality 6.87 (a) against 4.57 (b), gap +2.30 pp (+50 per cent); homeless (a) 100.0, 84.3, 71.4 in years 1-3
HEADLINE no SMI, housed: 65.6 per cent of the revoked; three-year mortality 6.58 (a) against 6.50 (b), gap +0.08 pp (+1 per cent); homeless (a) 0.0, 4.5, 7.6 in years 1-3
HEADLINE all (unsplit cohort lines): 100.0 per cent of the revoked; three-year mortality 6.86 (a) against 6.06 (b), gap +0.80 pp (+13 per cent); homeless (a) 28.4, 28.1, 27.3 in years 1-3
AGAINST code/revoked_2c (re-solved arms): 6.86 / 6.06 / +0.80 against 6.92 / 6.12 / +0.80
