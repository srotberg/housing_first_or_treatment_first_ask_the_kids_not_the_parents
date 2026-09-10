"""
Number of CHILDREN UNDER 18 by age of the household head, ages 26 to 85, the
model's sixty periods.

WHY TWO SOURCES. The model needs a single-year profile of the right concept, and
neither survey gives both.

  SCF 2022 has single-year age of head and a `kids` count, but `kids` is children
  in the household of ANY AGE. Against NSDUH's explicit under-18 count it runs
  1.02 to 1.19 times too high at 26-49 and 2.44 times too high at 50-64, which is
  adult children living at home. Its SHAPE is what is wanted, not its level.

  NSDUH 2024 has IRKI17_2, children under 18 in the household, which is exactly
  the right concept, but only five age bands: 26-29, 30-34, 35-49, 50-64, 65+.
  Its LEVEL is what is wanted, not its resolution.

So the SCF single-year profile is smoothed and then rescaled band by band to the
NSDUH under-18 mean. Within a band the shape is the SCF's; across bands the level
is NSDUH's.

WHY THIS REPLACES HOUSEHOLD SIZE. `actual_household_size` counts a spouse as well
as children. A spouse is an adult who chose into the household and the paper's
omega_c is a weight on the CHILD, so the externality should be scaled by children
and not by household size. The author's instruction, 10 September: "I think we
should use the number of children by age rather than family size."

Run:  python3 data/make_children_by_age.py
"""
import numpy as np, pandas as pd

NSDUH = '/tmp/claude-0/-home-user-housing-first-or-treatment-first/43825369-02f4-5759-bc82-a1a582111d14/scratchpad/nsduh24/NSDUH_2024_Tab.csv'
AGE_LO, AGE_HI = 26, 85              # the model's sixty periods
BANDS = {7: (26, 29), 8: (30, 34), 9: (35, 49), 10: (50, 64), 11: (65, 85)}


def nsduh_levels(path=NSDUH):
    cols = {'wt': 'ANALWT2+AF8-C', 'age3': 'AGE3', 'ki17': 'IRKI17+AF8-2'}
    with open(path) as f:
        hdr = f.readline().rstrip('\n').split('\t')
    pos = {k: hdr.index(v) for k, v in cols.items()}
    keys = list(pos)
    rows = []
    with open(path) as f:
        f.readline()
        for line in f:
            p = line.rstrip('\n').split('\t')
            rows.append([p[pos[k]] for k in keys])
    d = pd.DataFrame(rows, columns=keys).apply(pd.to_numeric, errors='coerce')
    # IRKI17_2: 1 none, 2 one, 3 two, 4 three or more (3+ counted as 3)
    d['nkid'] = d.ki17.map({1: 0, 2: 1, 3: 2, 4: 3})
    return {b: float(np.average(d[d.age3 == b].nkid, weights=d[d.age3 == b].wt))
            for b in BANDS}


def scf_shape(path='data/SCF_2022.dta', window=5):
    d = pd.read_stata(path, convert_categoricals=False)
    d = d[(d.age >= AGE_LO - window) & (d.age <= AGE_HI + window)]
    g = (d.assign(w=d.wgt, wk=d.wgt * d.kids).groupby('age')[['w', 'wk']].sum())
    raw = (g.wk / g.w)
    # centred moving average; single-year cells run about 100-550 households
    ages = np.arange(AGE_LO, AGE_HI + 1)
    out = []
    for a in ages:
        sel = raw[(raw.index >= a - window // 2) & (raw.index <= a + window // 2)]
        out.append(float(sel.mean()))
    return ages, np.array(out)


def build(iters=8):
    """
    Rescale the SCF shape to the NSDUH under-18 levels with a SMOOTHLY VARYING
    ratio rather than a step per band.

    Applying the ratio as a step puts a spurious cliff at every band boundary --
    the first version of this jumped from 1.00 children at age 49 to 0.49 at 50,
    purely because 35-49 and 50-64 are different NSDUH bands. The model would
    read that as a real kink in the age profile. So the band ratios are placed at
    band midpoints, interpolated linearly across single years, and then nudged a
    few times until each band mean matches its NSDUH target.
    """
    lev = nsduh_levels()
    ages, shape = scf_shape()
    mids = np.array([(lo + hi) / 2.0 for lo, hi in BANDS.values()])
    r = np.array([lev[b] / shape[(ages >= lo) & (ages <= hi)].mean()
                  for b, (lo, hi) in BANDS.items()])
    for _ in range(iters):
        ratio = np.interp(ages, mids, r)
        kids = shape * ratio
        for i, (b, (lo, hi)) in enumerate(BANDS.items()):
            m = (ages >= lo) & (ages <= hi)
            r[i] *= lev[b] / kids[m].mean()
    return ages, shape * np.interp(ages, mids, r), lev


if __name__ == '__main__':
    ages, kids, lev = build()
    print('NSDUH under-18 band levels:', {k: round(v, 4) for k, v in lev.items()})
    print(f'\n{"age":>5}{"children":>10}     {"age":>5}{"children":>10}')
    for i in range(30):
        j = i + 30
        print(f'{ages[i]:5d}{kids[i]:10.4f}     {ages[j]:5d}{kids[j]:10.4f}')
    print(f'\nmean over 26-85: {kids.mean():.4f}')
    print('\n--- Fortran, sixty values, to replace actual_household_size ---')
    for i in range(0, 60, 5):
        row = ','.join(f'{v:.7f}' for v in kids[i:i + 5])
        print(f'            {row},&')
