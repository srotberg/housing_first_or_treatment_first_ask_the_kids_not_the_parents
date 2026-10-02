"""
Who gains from Treatment First in the long run, household by household (the author, 2 October:
"we might want to add numbers on share of newborns in favor of the tf policy... And share of all
household who gain from it").

usage: python3 shares.py <reform arm dir> <comparison dir> <comparison file tag> [<weights dir> <weights tag>]
  e.g. shares.py cfarm_tf_2c cfarm_null_2c counter_arm
       shares.py cfarm_tf_fix2_85 cfarm_tf_fix2_85 baseline_benchmark   (the Fortran's own frac_in_support)

Compares the reform's steady-state value function with the comparison's at every state, weighted by
the comparison's stationary distribution (the households as they are under Housing First), and
prints the share better off, worse off and within a tolerance, for all households, for those with a
SUD, and for the youngest adults (age index 1, the households entering adult life: a newborn's adult
life starts there).

WHY AGAINST THE NO-POLICY RUN AND WITH A TOLERANCE. The Fortran prints frac_in_support, the share
with V_reform > V_benchmark strictly, against the benchmark's own files. The no-policy run, which is
the same policy re-solved, scores 0.997 on it (results/counterfactuals_2c/nulltf/null), so a strict
comparison counts numerical drift as a gain. Against the no-policy run's own value function that
drift cancels, and a tolerance separates a gain from a tie.

THE FILES. save_vars_and_functions writes value_function<i><tag>.dat and
distribution_stationary<i><tag>.dat one number per line, Fortran order, from arrays allocated as
(transition_length=1, life_span+1, financial, unemployment, employment, housing, voucher): i = 1 the
renters (financial from renter_array_floor, housing lowest_housing_grid_point..2, voucher 0..max),
i = 2 the owners (financial 1.., one housing slot, voucher 0). Age is the fastest index after time,
so age_index = n mod 61 + 1; unemployment_index follows the financial block; a household carries a
SUD when unemployment_index > threshold_addiction_index (12, the run's own index map line).
"""
import os
import sys
import numpy as np

A, U, THR = 61, 18, 12                 # life_span + 1, unemployment grid, SUD threshold (index map)
F1, H1, V1 = 25, 4, 3                  # renters: financial 3..27, housing -1..2, voucher 0..2
F2, H2, V2 = 27, 1, 1                  # owners: financial 1..27, one housing slot, voucher 0
TOLS = (1e-3, 1e-2)                    # utils; 1 per cent of a newborn's lifetime consumption is about 0.34


def read(d, stem, i, tag):
    return np.fromfile(os.path.join(d, f'{stem}{i}{tag}.dat'), sep=' ')


def labels(n, F):
    """age index (1-based) and SUD flag of each element"""
    k = np.arange(n)
    age = k % A + 1
    u = (k // (A * F)) % U + 1
    return age, u > THR


def main():
    arm, cmp_dir, tag = sys.argv[1:4]
    wdir, wtag = (sys.argv[4], sys.argv[5]) if len(sys.argv) > 5 else (cmp_dir, tag)
    rows = []
    for i, F, H, V in ((1, F1, H1, V1), (2, F2, H2, V2)):
        vr = read(arm, 'value_function', i, 'counter_arm')
        vc = read(cmp_dir, 'value_function', i, tag)
        w = read(wdir, 'distribution_stationary', i, wtag)
        assert len(vr) == len(vc) == len(w), (i, len(vr), len(vc), len(w))
        E = len(vr) / (A * F * U * H * V)
        assert E == int(E), f'file {i}: {len(vr)} values do not factor with F={F}, H={H}, V={V}'
        age, sud = labels(len(vr), F)
        live = (w > 0) & (age <= A - 1) & (vr > -1e9) & (vc > -1e9)
        rows.append((vr[live] - vc[live], w[live], age[live], sud[live]))
        print(f'file {i}: {len(vr)} states, employment grid {int(E)}, mass {w[live].sum():.6f}')
    d = np.concatenate([r[0] for r in rows]); w = np.concatenate([r[1] for r in rows])
    age = np.concatenate([r[2] for r in rows]); sud = np.concatenate([r[3] for r in rows])
    groups = (('all households', np.ones_like(sud)), ('with a SUD', sud), ('without a SUD', ~sud),
              ('youngest adults (age index 1)', age == 1))
    print(f'reform {arm} against {cmp_dir} ({tag}), weights {wdir} ({wtag})')
    for name, g in groups:
        m = w[g].sum()
        line = f'  {name:32s} mass {m:.5f}  strict better {np.sum(w[g & (d > 0)]) / m:.4f}'
        for t in TOLS:
            line += (f' | tol {t:g}: better {np.sum(w[g & (d > t)]) / m:.4f}'
                     f' worse {np.sum(w[g & (d < -t)]) / m:.4f}')
        print(line)
    q = np.percentile(d, [1, 10, 50, 90, 99])
    print('  dV percentiles (1, 10, 50, 90, 99), unweighted over occupied states:', ' '.join(f'{x:+.4f}' for x in q))


if __name__ == '__main__':
    main()
