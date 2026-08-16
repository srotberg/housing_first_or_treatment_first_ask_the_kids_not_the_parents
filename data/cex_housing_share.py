"""
The housing share of spending, from the Consumer Expenditure Survey.

WHAT IT IS FOR

gamma, the Cobb-Douglas weight on housing, is set to 26.8 per cent of non drug
spending. This is where that number comes from, and it is worth computing rather
than asserting because the CEX offers three "housing" numbers that differ by more
than half and only one of them is the model's object.

It is also the TARGET the standard rental unit is calibrated to. gamma is a
preference weight and 26.8 per cent is the outcome of a choice, and with three
points on the housing grid, the street among them and a voucher covering part of
the rent, nothing makes the one deliver the other. Fixing gamma here and the unit
size from a separate SCF ratio aimed two external numbers at one object and hit
neither, so the unit size is now bracketed on realised spending instead.

    Shelter alone                   20.8 %
    Shelter and utilities           26.8 %   <- the model's h
    the whole Housing category      33.4 %

The model's h is a dwelling occupied for a period. Utilities belong in it, since
here the rent is what it costs to occupy the unit and there is no separate
utility bill. Household operations, housekeeping supplies and furnishings do not:
they are things bought to put inside a dwelling, not the dwelling.

OWNERS ENTER AT OUTLAY, NOT AT IMPUTED RENT, and that is the one caveat on the
number. CEX shelter for an owned dwelling is mortgage interest, property taxes
and maintenance, so an outright owner with no mortgage records almost no shelter
spending while consuming a full dwelling's worth of housing services. Sixty five
per cent of consumer units report owned dwelling spending. The imputed rent
figure is therefore HIGHER than 26.8 per cent, so the model's 26.8 is a lower
bound on the defensible range rather than the middle of it.

Everyone rents in the model, so owners are not excluded here: the object is what
a representative household spends on housing services, and an owner consumes
those too. That is also the convention the quantitative model's housing target
uses, all households with owner housing at imputed rent.

Run:  python3 cex_housing_share.py
"""

import os

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'raw', 'CEX_all_consumer_units_detailed_means_2024.xlsx')
TENURE = os.path.join(HERE, 'raw', 'CEX_housing_tenure_means_2024.xlsx')

# The workbook puts a label on one row and Mean, Share, SE, RSE on the rows
# under it, so a line is found by its label and read from the row below.
WANT = ['Average annual expenditures', 'Housing', 'Shelter',
        'Owned dwellings', 'Rented dwellings', 'Other lodging',
        'Utilities, fuels, and public services']


def read_row(path, label, ncol=6):
    """The Mean row under a label, across every column of the table."""
    ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(min_row=1, values_only=True))
    for i, r in enumerate(rows):
        if (str(r[0]) if r[0] else '').split('[')[0].strip() == label:
            for j in range(i + 1, min(i + 4, len(rows))):
                if (str(rows[j][0]) or '').strip() == 'Mean':
                    return [float(x) for x in rows[j][1:ncol]]
    return None


def read_means(path=SRC):
    ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(min_row=1, values_only=True))
    out = {}
    for i, r in enumerate(rows):
        label = (str(r[0]) if r[0] else '').split('[')[0].strip()
        if label in WANT and label not in out:
            for j in range(i + 1, min(i + 4, len(rows))):
                if (str(rows[j][0]) or '').strip() == 'Mean':
                    out[label] = float(rows[j][1])
                    break
    return out


if __name__ == '__main__':
    m = read_means()
    total = m['Average annual expenditures']
    shelter = m['Shelter']
    utilities = m['Utilities, fuels, and public services']

    print('CEX 2024, all consumer units, table 2500')
    print(f'  average annual expenditures      {total:10,.0f}')
    print(f'  shelter                          {shelter:10,.0f}   {shelter/total:6.1%}')
    print(f'    of which owned dwellings       {m["Owned dwellings"]:10,.0f}   '
          f'{m["Owned dwellings"]/total:6.1%}')
    print(f'    of which rented dwellings      {m["Rented dwellings"]:10,.0f}   '
          f'{m["Rented dwellings"]/total:6.1%}')
    print(f'  utilities, fuels, public services{utilities:10,.0f}   {utilities/total:6.1%}')
    print(f'  whole Housing category           {m["Housing"]:10,.0f}   {m["Housing"]/total:6.1%}')
    print()
    print(f'  THE MODEL OBJECT, shelter and utilities: {(shelter+utilities)/total:.1%}')
    print(f'  the model uses that as gamma/(1-theta) AND as the target the')
    print(f'  standard rental unit is calibrated to. It is a lower bound, because')
    print(f'  owners enter here at outlay rather than at imputed rent')
    print()

    cols = ['all', 'owner', 'owner, mortgage', 'owner, none', 'renter']
    tot = read_row(TENURE, 'Average annual expenditures')
    sh = read_row(TENURE, 'Shelter')
    ut = read_row(TENURE, 'Utilities, fuels, and public services')
    print('CEX 2024, table 1710, by housing tenure')
    print('  ' + ''.join(f'{c:>18s}' for c in cols))
    print('  ' + ''.join(f'{(sh[i]+ut[i])/tot[i]:17.1%}' for i in range(len(cols))))
    print()
    print('  Renters spend a THIRD of expenditure on shelter and utilities, owners')
    print('  a quarter, and owners without a mortgage the least of all at 21.2 per')
    print('  cent, which is the outlay problem in one number: they record almost no')
    print('  shelter spending while consuming a whole dwelling. So 26.8 is at the')
    print('  low end on every reading of this table, and well below the renter')
    print('  figure that the model\'s households, all of whom rent, most resemble.')
