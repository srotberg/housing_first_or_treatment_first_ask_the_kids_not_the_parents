"""
Homelessness and the SUD by any age range, read off a steady state's stationary distribution (the author,
2 October, on Section 6.2's 'The SUD figures are by ten-year band': "why not break it down to 26-38 and
39-50? why cant you compute it from the equilibirum we have?"). The log prints the SUD share of the homeless
only by the Fortran's five fixed bands; the distribution carries it at every age.

usage: python3 age_split.py <label>=<dir>:<tag> [<label>=<dir>:<tag> ...]
  e.g. age_split.py null=cfarm_null_2c:counter_arm tf=cfarm_tf_2c:counter_arm
       age_split.py bench=results/reference/hf_2c_omega_0.085/files:baseline_benchmark   (the check)

For each run and age range it prints the mass, the share carrying a SUD, the homelessness rate, and the
homelessness rate among households with a SUD and among those without. The 26-34, 35-44 and 45-54 rows
are the Fortran's bands 1 to 3, so they must reproduce the log's 'UNTARGETED homelessness rate, band k',
'DIAG disorder rate, band k' and 'DIAG SUD share of the homeless, band k' lines: that is the check that
the layout below is read right.

THE LAYOUT (as in shares.py): distribution_stationary<i><tag>.dat, one number per line, Fortran order,
age fastest (age index 1 is age 26, A = life_span + 1 = 61), then financial, unemployment, employment,
housing, voucher. i = 1 the renters (housing -1..2, the first slot, -1, is the shelter; voucher 0..2),
i = 2 the owners (one housing slot).
Homelessness is counted as the Fortran counts it, from policy_function_housing_status_index<i><tag>.dat (same
layout) when that file is there; without it the script falls back on the state's shelter slot and says so. A household carries a SUD when its unemployment
index exceeds threshold_addiction_index = 12, the Fortran's own test for val_sud_band. Files may be gzipped.
"""
import gzip
import os
import sys
import numpy as np

A, U, THR = 61, 18, 12
F1, H1, V1 = 25, 4, 3
F2, H2, V2 = 27, 1, 1
RANGES = ((26, 34), (35, 44), (45, 54), (26, 38), (39, 50), (45, 50), (26, 50))


def read(d, i, tag, stem='distribution_stationary'):
    p = os.path.join(d, f'{stem}{i}{tag}.dat')
    if not os.path.exists(p) and os.path.exists(p + '.gz'):
        with gzip.open(p + '.gz', 'rt') as f:
            return np.array(f.read().split(), dtype=float)
    return np.fromfile(p, sep=' ')


def load(d, tag):
    out, exact = [], [True]
    for i, F, H, V in ((1, F1, H1, V1), (2, F2, H2, V2)):
        w = read(d, i, tag)
        E = len(w) / (A * F * U * H * V)
        assert E == int(E), f'{d} file {i}: {len(w)} values do not factor'
        w = w.reshape((V, H, int(E), U, F, A))          # Fortran order reversed
        mass = w.sum(axis=(0, 1, 2, 4))                  # (U, A)
        pol = os.path.join(d, f'policy_function_housing_status_index{i}{tag}.dat')
        if os.path.exists(pol) or os.path.exists(pol + '.gz'):
            # EXACT: the Fortran counts a household as homeless when the housing it CHOOSES this period is the
            # shelter (housing_status_index_used, the policy at its state), weighted by the distribution
            h = read(d, i, tag, 'policy_function_housing_status_index').reshape(w.shape)
            home = (w * (h == -1)).sum(axis=(0, 1, 2, 4))
            exact[0] = exact[0] and True
        else:
            # APPROXIMATE: the shelter slot of the state, the housing a household ENTERS the period with
            home = w[:, 0].sum(axis=(0, 1, 3)) if i == 1 else np.zeros_like(mass)
            exact[0] = False
        out.append((mass, home))
    mass = out[0][0] + out[1][0]
    home = out[0][1] + out[1][1]
    sud = np.arange(1, U + 1) > THR
    return mass, home, sud, exact[0]


def row(mass, home, sud, lo, hi):
    a = slice(lo - 26, hi - 26 + 1)
    m, h = mass[:, a].sum(), home[:, a].sum()
    ms, hs = mass[sud, a].sum(), home[sud, a].sum()
    return dict(mass=m, sud=ms / m, h=h / m, h_sud=hs / ms, h_clean=(h - hs) / (m - ms), sud_of_h=hs / h)


def main():
    for arg in sys.argv[1:]:
        label, spec = arg.split('=', 1)
        d, tag = spec.rsplit(':', 1)
        mass, home, sud, exact = load(d, tag)
        print(f'== {label}: {d} ({tag}), total mass {mass[:, :A - 1].sum():.6f}, homeless from '
              + ('the housing policy (exact)' if exact else 'the state\'s shelter slot (APPROXIMATE: no policy file)'))
        print(f'   {"ages":8s} {"mass":>9s} {"SUD %":>7s} {"homeless %":>10s} {"of SUD %":>9s} '
              f'{"of rest %":>9s} {"SUD share of homeless":>22s}')
        for lo, hi in RANGES:
            r = row(mass, home, sud, lo, hi)
            print(f'   {lo}-{hi:<5d} {r["mass"]:9.4f} {100 * r["sud"]:7.3f} {100 * r["h"]:10.4f} '
                  f'{100 * r["h_sud"]:9.4f} {100 * r["h_clean"]:9.4f} {r["sud_of_h"]:22.4f}')


if __name__ == '__main__':
    main()
