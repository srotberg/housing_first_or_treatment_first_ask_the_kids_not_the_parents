#!/usr/bin/env python3
"""analyse.py <arm A dir> <arm B dir> <walk dir> [--json out]

Treatment First (Arm B) against Housing First (Arm A), both without externalities and at Arm A's
prices (README.md), household by household, weighted by ARM A's stationary distribution.

  dV_s = V_B(s) - V_A(s), from value_function<i>counter_arm.dat of each arm: the household's own
  lifetime utility, since omega_c = 0 leaves no child term in it and kappa_x enters no value function.

  better / worse / indifferent at a tolerance: |dV| against an absolute tolerance in utils (1e-3,
  shares.py's) and against 1e-6 |V_A| (value_shares.py's).

  CEV. The walk (patch_walk.py) gives W_s(x), each state's value under ARM A's policies with non-drug
  consumption scaled by (1+x), at the x listed in pe_walk.dat. The consumption equivalent of state s is
  the x at which V_A(s) + W_s(x) - W_s(0) = V_B(s) (piecewise-linear in x between grid points): the
  proportional change in Arm A's consumption, every period for the rest of life, worth the same as
  the move to Treatment First. Group CEVs solve the same equation for the Arm-A-weighted SUMS over the
  group: the population (every state alive at ages 26-85), those affected at the tolerance, and the
  newborn adult (age 26, model age 1; values on Arm A's newborn mix, so the newborns' productivity mix,
  which follows the parents', cannot enter).

  The childhood-inclusive newborn number (NOT externality-free: the childhood term is the child's
  utility from its parent's consumption and housing) uses each arm's printed
  average_welfare_with_childhood and Arm A's own lifetime curve from the walk, childhood(x) +
  beta^K * w_adult(x), with beta^K recovered from Arm A's log.
"""
import argparse, json, os, re, sys
import numpy as np

A = 61
TOLS_ABS = (1e-6, 1e-4, 1e-3, 1e-2)
RTOL = 1e-6


def vf(d, stem, i):
    p = os.path.join(d, f'{stem}{i}counter_arm.dat')
    if not os.path.exists(p):
        sys.exit(f'GUARD: {p} missing')
    return np.fromfile(p, sep=' ')


def last(log, key):
    v = None
    if not os.path.exists(log):
        return None
    for l in open(log, errors='replace'):
        s = l.strip()
        if s.startswith(key):
            try:
                v = float(s[len(key):].split()[0])
            except ValueError:
                pass
    return v


def solve_x(xs, g, target):
    """x with g(x) = target, g increasing on the grid xs; nan if outside"""
    if target < g[0] or target > g[-1]:
        return np.nan
    return float(np.interp(target, g, xs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('a'); ap.add_argument('b'); ap.add_argument('walk')
    ap.add_argument('--json')
    o = ap.parse_args()
    xs = np.array([float(l) for l in open(os.path.join(o.walk, 'pe_walk.dat')).read().split()[1:]])
    order = np.argsort(xs); xs_sorted = xs[order]
    k0 = int(np.argmin(np.abs(xs)))
    assert abs(xs[k0]) < 1e-12, 'the walk grid lacks x = 0'

    VA, VB, W, AGE, IDX = [], [], [], [], []
    for i in (1, 2):
        va, vb, w = vf(o.a, 'value_function', i), vf(o.b, 'value_function', i), vf(o.a, 'distribution_stationary', i)
        assert len(va) == len(vb) == len(w), (i, len(va), len(vb), len(w))
        age = np.arange(len(va)) % A + 1
        live = (w > 0) & (age <= A - 1) & (va > -1e9) & (vb > -1e9)
        walks = []
        for k in range(len(xs)):
            g = np.fromfile(os.path.join(o.walk, f'walk_V{i}_{k + 1:02d}.bin'), dtype=np.float64)
            assert len(g) == len(va), (i, k, len(g), len(va))
            walks.append(g[live])
        walks = np.array(walks)                     # (n_x, n_live)
        live_w = walks.min(axis=0) > -1e9           # states the walk could evaluate at every x
        VA.append(va[live][live_w]); VB.append(vb[live][live_w]); W.append(w[live][live_w])
        AGE.append(age[live][live_w]); IDX.append(walks[:, live_w])
        print(f'file {i}: {len(va)} states, {live.sum()} occupied, mass {w[live].sum():.6f}, '
              f'walk could not evaluate mass {w[live][~live_w].sum():.3e}')
    va = np.concatenate(VA); vb = np.concatenate(VB); w = np.concatenate(W); age = np.concatenate(AGE)
    g = np.concatenate(IDX, axis=1)                 # W_s(x_k)
    m = w.sum(); w = w / m
    d = vb - va
    out = {'mass_dropped_note': 'states the walk could not evaluate are left out (printed above)'}

    # the walk against Arm A's own value function at x = 0
    disc = g[k0] - va
    print(f'walk at x=0 minus V_A: weighted mean {np.sum(w * disc):+.4e}, weighted mean |.| '
          f'{np.sum(w * np.abs(disc)):.4e}, max |.| {np.abs(disc).max():.4e} (utils)')
    out['walk_disc'] = dict(mean=float(np.sum(w * disc)), mean_abs=float(np.sum(w * np.abs(disc))),
                            max_abs=float(np.abs(disc).max()))
    gs = (g - g[k0])[order]                         # W_s(x) - W_s(0), x ascending
    mono = np.all(np.diff(gs, axis=0) >= -1e-9, axis=0)
    print(f'walk increasing in x at {np.sum(w[mono]):.6f} of the mass')

    print('\nSHARES (weights: Arm A distribution)')
    groups = (('all households', np.ones_like(age, bool)), ('age 26 (model age 1)', age == 1))
    out['shares'] = {}
    for name, sel in groups:
        ms = w[sel].sum()
        row = {}
        line = f'  {name:22s} mass {ms:.5f} | strict: better {w[sel & (d > 0)].sum() / ms:.4f} worse {w[sel & (d < 0)].sum() / ms:.4f}'
        for t in TOLS_ABS:
            b_, wo = w[sel & (d > t)].sum() / ms, w[sel & (d < -t)].sum() / ms
            row[f'abs{t:g}'] = dict(better=b_, worse=wo, indifferent=1 - b_ - wo)
            line += f' | tol {t:g}: better {b_:.4f} worse {wo:.4f} same {1 - b_ - wo:.4f}'
        tr = RTOL * np.abs(va)
        b_, wo = w[sel & (d > tr)].sum() / ms, w[sel & (d < -tr)].sum() / ms
        row['rel1e-6'] = dict(better=b_, worse=wo, indifferent=1 - b_ - wo)
        line += f' | rtol 1e-6: better {b_:.4f} worse {wo:.4f} same {1 - b_ - wo:.4f}'
        print(line)
        out['shares'][name] = row
    i_max = int(np.argmax(d))
    print(f'  largest gain dV {d[i_max]:+.4e} utils (age {age[i_max]}, V_A {va[i_max]:.4f}, mass {w[i_max] * m:.3e}); '
          f'largest loss {d.min():+.4e}')
    out['max_gain'] = dict(dV=float(d[i_max]), age=int(age[i_max]), VA=float(va[i_max]), mass=float(w[i_max] * m))
    out['max_loss'] = float(d.min())
    q = np.percentile(d, [1, 10, 50, 90, 99])
    print('  dV percentiles (1,10,50,90,99), unweighted over occupied states:', ' '.join(f'{x:+.3e}' for x in q))

    print('\nCEV (per cent of Arm A consumption, every period for life; negative = Treatment First worse)')
    cev_s = np.array([solve_x(xs_sorted, gs[:, j], d[j]) if mono[j] else np.nan for j in range(len(d))])
    out['cev'] = {}
    for t in (1e-6, 1e-3):
        aff = np.abs(d) > t
        for name, sel in (('population', np.ones_like(aff)), (f'affected (|dV|>{t:g})', aff),
                          (f'worse off (dV<-{t:g})', d < -t), (f'better off (dV>{t:g})', d > t),
                          ('newborn adult (age 26)', age == 1), (f'newborn adult, affected (|dV|>{t:g})', (age == 1) & aff)):
            if not sel.any():
                print(f'  {name:40s} none'); continue
            ws = w[sel]
            x = solve_x(xs_sorted, (ws[:, None] * gs[:, sel].T).sum(0) / ws.sum(), np.sum(ws * d[sel]) / ws.sum())
            ok = ~np.isnan(cev_s[sel])
            mean_s = np.sum(ws[ok] * cev_s[sel][ok]) / max(ws[ok].sum(), 1e-300)
            print(f'  {name:40s} share {ws.sum():.4f}  CEV of the group {100 * x:+.4f}%   mean of state CEVs {100 * mean_s:+.4f}%'
                  f'  (state CEV off the grid for {ws[~ok].sum() / ws.sum():.2e} of the group)')
            out['cev'][name] = dict(share=float(ws.sum()), cev_group=x, cev_mean_states=float(mean_s))

    # the childhood-inclusive newborn number, NOT externality-free
    la, lb = os.path.join(o.a, 'cf.log'), os.path.join(o.b, 'cf.log')
    wa, wb = last(la, 'average_welfare_with_childhood='), last(lb, 'average_welfare_with_childhood=')
    ya, ca = last(la, 'average_welfare_of_youngest_cohort='), last(la, 'average_childhood_utility=')
    curve = []
    for l in open(os.path.join(o.walk, 'walk.log'), errors='replace'):
        mm = re.search(r'PE WALK k=\s*\d+\s+x=\s*(\S+)\s+w_adult=\s*(\S+)\s+childhood=\s*(\S+)', l)
        if mm:
            curve.append(tuple(map(float, mm.groups())))
    if None not in (wa, wb, ya, ca) and curve:
        bk = (wa - ca) / ya
        curve.sort()
        cx = np.array([c[0] for c in curve]); cl = np.array([c[2] + bk * c[1] for c in curve])
        c0 = cl[np.argmin(np.abs(cx))]
        x = solve_x(cx, cl - c0, wb - wa)
        print(f'\n  newborn, childhood-inclusive (NOT externality-free): W_A {wa:.6f} W_B {wb:.6f} '
              f'(beta^K {bk:.6f}) CEV {100 * x:+.4f}%')
        out['cev_newborn_with_childhood'] = dict(WA=wa, WB=wb, betaK=bk, cev=x)
    if o.json:
        json.dump(out, open(o.json, 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
