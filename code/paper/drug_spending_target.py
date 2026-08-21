"""
What share of income users spend on drugs: the arithmetic, with every input named.

WHY THIS EXISTS. drug_spending_share_data is 0.35 in the Fortran, built as a
weighted average of 0.11 for users without a disorder and 0.44 for users with
one, and the note attributes both to NSDUH 2024. NSDUH does not collect
expenditure, so whatever those two numbers are, that citation is wrong. This
rebuilds the target from sources that do measure spending, and shows what the
answer turns on.

WHAT IT TURNS ON: which population the model's 5.13 per cent participation rate
is. The model's own numbers say 72 per cent of its users carry a disorder, which
is not what "any use" gives, so the problem-use reading is the one its internals
support. The two readings differ by about a factor of two.

THE WEAK LINK IS THE DENOMINATOR, and it is flagged as an assumption rather than
buried: the aggregates give spending per user directly, but the INCOME of users
has to be assumed, so the answer is reported across a range of it.

Run:  python3 drug_spending_target.py
"""

# ---------------------------------------------------------------- inputs
# RAND / ONDCP, "What America's Users Spend on Illegal Drugs, 2006-2016",
# retail expenditure in 2016. DATA.
SPEND_2016_BN = {'cannabis': 52.0, 'heroin': 43.0, 'meth': 27.0, 'cocaine': 24.0}

# US adults 26 and over, 2016, the universe the model's rates are quoted on.
# DATA, rounded.
ADULTS_26_PLUS = 216e6

# The model's own two rates, from the Fortran declarations. DATA (as targets).
PARTICIPATION = 0.0513
SUD_RATE = 0.0368

# RAND finds spending is concentrated in daily and near-daily users, who are a
# minority of past-year users. This is the share of CANNABIS spending done by
# them, and so the share that belongs to a problem-use population. ASSUMPTION,
# from RAND's qualitative finding rather than a published number.
CANNABIS_PROBLEM_SHARE = 0.80

# Surveys undercount chronic hard-drug users; RAND says so explicitly and uses
# other methods. This is how much larger the true user base may be than the
# survey rate implies. ASSUMPTION, reported as a range.
UNDERCOUNT = (1.0, 1.5, 2.0)

# Annual income of the using population. THE WEAKEST INPUT, reported as a range.
# US mean personal income for adults was near 45,000 in 2016 and the median near
# 31,000; users skew lower than both.
INCOMES = (30_000, 40_000, 50_000)


def main():
    hard = sum(v for k, v in SPEND_2016_BN.items() if k != 'cannabis') * 1e9
    cann = SPEND_2016_BN['cannabis'] * 1e9
    users = PARTICIPATION * ADULTS_26_PLUS
    dis = SUD_RATE * ADULTS_26_PLUS

    print(__doc__)
    print(f'RAND 2016 retail spending: ' +
          ', '.join(f'{k} ${v:.0f}bn' for k, v in SPEND_2016_BN.items()))
    print(f'   hard drugs (excluding cannabis)        = ${hard/1e9:.0f}bn')
    print(f'   cannabis at {CANNABIS_PROBLEM_SHARE:.0%} (problem users only) = ${cann*CANNABIS_PROBLEM_SHARE/1e9:.0f}bn')
    print()
    print(f'Model population on {ADULTS_26_PLUS/1e6:.0f}M adults 26+:')
    print(f'   users     {PARTICIPATION:.4f} -> {users/1e6:5.1f}M')
    print(f'   disorder  {SUD_RATE:.4f} -> {dis/1e6:5.1f}M   = {dis/users:.0%} of users')
    print(f'   a {dis/users:.0%} conversion is a PROBLEM-USE definition, not any-use')
    print()

    for label, total in (('A  other than marijuana (no cannabis)', hard),
                         ('B  problem use, severe cannabis included',
                          hard + cann * CANNABIS_PROBLEM_SHARE)):
        print(f'{label}   total = ${total/1e9:.0f}bn')
        print(f'{"":>6}{"users":>10}{"$/user/yr":>12}' +
              ''.join(f'{f"@${i//1000}k":>9}' for i in INCOMES))
        for m in UNDERCOUNT:
            u = users * m
            per = total / u
            row = f'{m:>5.1f}x{u/1e6:>9.1f}M{per:>12,.0f}'
            row += ''.join(f'{per/i:>9.0%}' for i in INCOMES)
            print(row)
        print()

    print('Micro estimates that measure BOTH sides, for comparison:')
    print('   heroin-dependent sample: income $723/mo, ~75% of it spent on heroin')
    print('   homeless cocaine users : ~$400 in the last month, ~50% of income')
    print('   -> both are far more dependent than the average user in either reading,')
    print('      so they are an upper bound on a population-wide share, not an estimate of it.')
    print()
    print('Composition point, which cuts against reading A only:')
    print('   prescription pain reliever misuse is a large part of "other than marijuana",')
    print('   and NSDUH finds 50-55% obtain it FREE from a friend or relative, ~71% from')
    print('   friends and family in some form, and only 4.8% buy from a dealer.')


if __name__ == '__main__':
    main()
