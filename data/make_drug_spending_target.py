#!/usr/bin/env python3
"""
The drug spending target, and the two population rates, from NSDUH 2024 and RAND.

WHY THIS EXISTS. All three numbers were typed into declarations, and two of them
were wrong in ways that do not announce themselves.

THE UNIVERSE. The model's households are aged 26 and over and the note says so
throughout, but the participation and SUD targets in use were the EIGHTEEN and
over figures: 10.13 and 4.54 per cent against the 8.90 and 3.68 the model's own
universe gives. AGE3 >= 7 is 26 and over in NSDUH's recode.

THE SPENDING SHARE HAD TWO ERRORS THAT PARTLY CANCELLED. It divided RAND's 136
billion of 2016 retail spending by NSDUH PERSONAL income in 2024 dollars and got
19.7 per cent. Both halves are wrong:

  - the model's y is a HOUSEHOLD's income, which is what pays rent and buys
    consumption in its budget constraint, so the denominator is family income;
  - 2016 spending cannot be divided by 2024 income, so the numerator is
    inflated by CPI-U, 240.007 to 313.689.

Correcting only the denominator gives 12.4 per cent and only the numerator 24.1,
which is why the uncorrected number looked reasonable. Correcting both gives
16.2.

THE ONE REMAINING ASSUMPTION is NSDUH's open top income band, 75,000 and over.
Its midpoint is set at 100,000, the same convention behind the personal income
figures already quoted in the note, and the band is varied from 75,000 to
125,000 to show what it is worth: the share runs 19.1 to 14.1 per cent.

Run:  python3 make_drug_spending_target.py
"""

import csv
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'drug_spending_target.csv')

# RAND / ONDCP, "What America's Users Spend on Illegal Drugs, 2006-2016", the
# retail total for cannabis, cocaine, heroin and methamphetamine done by the
# daily and near-daily users who account for almost all of it. 2016 dollars.
SPEND_2016_BN = 136.0

# CPI-U annual averages, BLS series CUUR0000SA0.
CPI_2016, CPI_2024 = 240.007, 313.689

# NSDUH income bands, midpoints. The top band is open at 75,000 and over.
BAND = {1: 5_000, 2: 15_000, 3: 25_000, 4: 35_000, 5: 45_000, 6: 62_500}
TOP_BANDS = (75_000, 100_000, 125_000)
# THE TOP BAND MIDPOINT IS 125,000, on the author's instruction of 5 September:
# *"ok, use 14% then for theta"*. NSDUH's top income band is OPEN at 75,000 and
# over, so its midpoint is an assumption and the only one in this construction.
# The conditional mean of an open top band sits well above a round number just
# past its threshold, so 100,000 was the conservative choice and biased the
# share UP. The sensitivity was always computed and written to the csv:
#
#     top band    75,000   ->  19.044 per cent
#     top band   100,000   ->  16.202 per cent
#     top band   125,000   ->  14.098 per cent
#
# 14.098 IS THE NUMBER, NOT 14. The share is generated from the data here and
# read into the Fortran declaration; nothing types a rounded version of it.
TOP_MAIN = 125_000


def main():
    d = pd.read_stata(os.path.join(HERE, 'NSDUH_2024.dta'))
    d['age3n'] = pd.to_numeric(d['age3'], errors='coerce')
    d['sev'] = pd.to_numeric(d['svyrdudany'], errors='coerce')
    d['w'] = pd.to_numeric(d['analwt2_c'], errors='coerce')
    a = d[d.age3n >= 7]                      # 26 and over, the model's universe
    W = a.w.sum()

    mild = a.w[a.sev == 1].sum() / W
    modsev = a.w[a.sev.isin([2, 3])].sum() / W
    any_ = a.w[a.sev.isin([1, 2, 3])].sum() / W
    users = a[a.sev.isin([1, 2, 3])]
    n_users = users.w.sum()

    spend24 = SPEND_2016_BN * CPI_2024 / CPI_2016

    rows = []
    for top in TOP_BANDS:
        M = dict(BAND); M[7] = top
        fam = np.average(pd.to_numeric(users['irfamin3'], errors='coerce').map(M),
                         weights=users.w)
        per = np.average(pd.to_numeric(users['irpinc3'], errors='coerce').map(M),
                         weights=users.w)
        inc_bn = n_users * fam / 1e9
        rows.append(dict(top_band=top, family_income=round(fam),
                         personal_income=round(per),
                         user_income_bn=round(inc_bn, 1),
                         share=round(spend24 / inc_bn, 5)))

    main_row = next(r for r in rows if r['top_band'] == TOP_MAIN)
    with open(OUT, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['quantity', 'value', 'universe', 'source'])
        w.writerow(['participation', round(any_, 5),
                    'NSDUH 2024, 26+, any drug use disorder', 'svyrdudany in 1,2,3'])
        w.writerow(['sud_rate', round(modsev, 5),
                    'NSDUH 2024, 26+, moderate or severe', 'svyrdudany in 2,3'])
        w.writerow(['mild_rate', round(mild, 5),
                    'NSDUH 2024, 26+, mild', 'svyrdudany = 1'])
        w.writerow(['drug_spending_share', main_row['share'],
                    'RAND 2016 retail spending in 2024 dollars over user family income',
                    f'top band at {TOP_MAIN}'])
        w.writerow(['user_family_income', main_row['family_income'],
                    'NSDUH 2024, 26+, any disorder, mean family income',
                    f'top band at {TOP_MAIN}'])
        w.writerow(['user_personal_income', main_row['personal_income'],
                    'NSDUH 2024, 26+, any disorder, mean personal income',
                    f'top band at {TOP_MAIN}'])
        w.writerow(['n_users_m', round(n_users / 1e6, 1),
                    'NSDUH 2024, 26+, any disorder, millions', ''])
        w.writerow(['user_income_bn', main_row['user_income_bn'],
                    'family income of the using population, $bn', ''])
        w.writerow(['spend_2024_bn', round(spend24, 1),
                    'RAND 2016 retail spending carried to 2024 by CPI-U', ''])
        # WHAT EACH CORRECTION IS WORTH, so the note can say it rather than
        # assert that the two nearly cancel.
        per_bn = n_users * main_row['personal_income'] / 1e9
        w.writerow(['share_uncorrected', round(SPEND_2016_BN / per_bn, 5),
                    '2016 spending over personal income: neither correction', ''])
        w.writerow(['share_income_only', round(SPEND_2016_BN / main_row['user_income_bn'], 5),
                    'family income but 2016 dollars: income correction alone', ''])
        w.writerow(['share_price_only', round(spend24 / per_bn, 5),
                    'personal income in 2024 dollars: price correction alone', ''])
        for r in rows:
            w.writerow([f'share_top_{r["top_band"]}', r['share'],
                        'sensitivity to the open top income band', ''])

    print(f'adults 26+: {W/1e6:.1f}m; users {100*any_:.2f}% = {n_users/1e6:.1f}m')
    print(f'mild {100*mild:.2f}%   moderate or severe {100*modsev:.2f}%   '
          f'any {100*any_:.2f}%')
    print(f'spending {SPEND_2016_BN:.0f}bn in 2016 dollars = {spend24:.1f}bn in 2024')
    print(f'{"top band":>10s}{"family":>10s}{"income $bn":>12s}{"share":>9s}')
    for r in rows:
        mark = '  <- used' if r['top_band'] == TOP_MAIN else ''
        print(f'{r["top_band"]:10,}{r["family_income"]:10,}'
              f'{r["user_income_bn"]:12,.0f}{100*r["share"]:8.2f}%{mark}')
    print(f'\nwrote {OUT}')


if __name__ == '__main__':
    main()
