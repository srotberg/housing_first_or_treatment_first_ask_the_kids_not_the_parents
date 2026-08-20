"""
THE TRANSITION TO TREATMENT FIRST, generation by generation.

WHY THE MODEL HAS A TRANSITION AT ALL, when a household lives two periods. The
link across generations is not persistence of income, which the model
deliberately leaves out, but the PENALTY: a child's income is a fresh draw from
the same lognormal, multiplied by (1 - del_d) if its parent acquired the
disorder and by (1 - del_h) if its parent was homeless. So what a cohort
inherits from the one before it is not a level of income, it is a MIXTURE over
four penalty types,

    s in { 1,  1-del_d,  1-del_h,  (1-del_d)(1-del_h) },

and that mixture is a Markov chain: the share of a cohort carrying each penalty
is decided by how many of the previous cohort used and how many were unhoused,
which in turn depends on the incomes that cohort was born with. Change the
policy and the chain starts moving, geometrically, to a new rest point. Five to
ten cohorts is enough to see all of it.

WHY THE PICTURE IS WORTH A SECTION. The paper's whole claim is that Treatment
First buys the child at the parent's expense, and a static comparison cannot
show that: it reports the sum. The transition separates them in time. The cohort
alive when the policy lands is the cohort that pays, since conditionality is a
cost to it and none of the benefit has arrived yet. The cohorts after it inherit
a cleaner and better housed parent generation, so they are born richer, and
their welfare climbs to a rest point above where it started. The two effects are
the same two terms as in the verdict table, seen one at a time.

WHAT IS PLOTTED: expected lifetime value of a NEWBORN cohort, V1 averaged over
the income distribution that cohort is actually born into, expressed as a
consumption equivalent against the pre reform rest point. Cohort 0 is the old
rest point by construction. Cohort 1 is the one the reform lands on.

Run:  python3 transition.py
"""

import json
import os
import numpy as np

from stylized import P, with_, value1, use_prob, homeless_prob
from calibrate import YG, W, stats
from welfare import cev
from children import DEL_D, DEL_H

WW = W / W.sum()
LY = np.log(YG)

BASE_POLICY = 'HF'      # the world as it is: rationed vouchers, no condition
PV_OPT = 1.0            # the optimal Treatment First programme is universal
GENERATIONS = 8


def _at(vals, s):
    """vals evaluated at income y*s on the grid, interpolated in log income.

    Outside the grid the end values are carried, which is the same convention
    children.shifted uses and matters only for the bottom pool, where the use
    and homelessness probabilities are already flat."""
    return np.interp(LY + np.log(s), LY, vals, left=vals[0], right=vals[-1])


def _policy_grids(par, policy, pV):
    """V1, the probability of ending with the disorder, and the probability of
    being unhoused, at every income node under one policy."""
    q = with_(par, policy=policy, pV=pV)
    v1 = np.array([value1(q, y, policy) for y in YG])
    use = np.array([use_prob(q, y, policy) for y in YG], dtype=float)
    hl = np.array([homeless_prob(q, y, policy) for y in YG], dtype=float)
    prog = stats(q)['prog']
    return v1, np.clip(use * prog, 0.0, 1.0), np.clip(hl, 0.0, 1.0)


def _shifts():
    return np.array([1.0, 1.0 - DEL_D, 1.0 - DEL_H,
                     (1.0 - DEL_D) * (1.0 - DEL_H)])


def _step(p, sud, hl):
    """One generation. p is the mixture over the four penalty types; the return
    is the mixture the CHILDREN of that cohort are born into.

    The disorder and homelessness are taken as independent given income, which
    is the same reduced form children.py uses: both are functions of the income
    the household was born with, and nothing else links them."""
    out = np.zeros(4)
    for s, ps in zip(_shifts(), p):
        if ps <= 0.0:
            continue
        d = _at(sud, s)
        h = _at(hl, s)
        out[0] += ps * float((WW * (1 - d) * (1 - h)).sum())
        out[1] += ps * float((WW * d * (1 - h)).sum())
        out[2] += ps * float((WW * (1 - d) * h).sum())
        out[3] += ps * float((WW * d * h).sum())
    return out / out.sum()


def _welfare(p, v1):
    """Expected lifetime value of a cohort born into the mixture p."""
    return sum(ps * float((WW * _at(v1, s)).sum())
               for s, ps in zip(_shifts(), p))


def _rest_point(sud, hl, iters=400, tol=1e-14):
    p = np.array([1.0, 0.0, 0.0, 0.0])
    for _ in range(iters):
        q = _step(p, sud, hl)
        if np.abs(q - p).max() < tol:
            return q
        p = q
    return p


def path(par, policy, pV, p0, v1_base, w0, n=GENERATIONS):
    """Newborn welfare for n cohorts after the reform lands, as a consumption
    equivalent against the pre reform rest point."""
    v1, sud, hl = _policy_grids(par, policy, pV)
    out = [(0, 0.0, p0.copy())]
    p = p0.copy()
    for t in range(1, n + 1):
        # the cohort BORN at t-1 lives under the new policy, and the mixture it
        # was born into is the one the previous cohort handed it. Cohort 1 is
        # therefore born into the OLD rest point and lives under the NEW rule,
        # which is exactly the cohort that pays for the reform.
        w = _welfare(p, v1)
        out.append((t, float(cev(par, w - w0)), p.copy()))
        p = _step(p, sud, hl)
    return out


def run(par=None, n=GENERATIONS):
    here = os.path.dirname(os.path.abspath(__file__))
    par = par or with_(P(), **json.load(open(os.path.join(here, 'calibrated.json'))))

    v1b, sudb, hlb = _policy_grids(par, BASE_POLICY, par.pV)
    p0 = _rest_point(sudb, hlb)
    w0 = _welfare(p0, v1b)
    print(f'PRE REFORM REST POINT, {BASE_POLICY} at pi_V = {par.pV}')
    print(f'   share of children born to a parent with the disorder : '
          f'{100*(p0[1]+p0[3]):.3f}%')
    print(f'   share born to a parent who was unhoused              : '
          f'{100*(p0[2]+p0[3]):.3f}%')
    print(f'   del_d = {DEL_D:.4f}   del_h = {DEL_H:.4f}')

    paths = {}
    for lab, pol in (('TF', 'TF'), ('HF', 'HF')):
        paths[lab] = path(par, pol, PV_OPT, p0, v1b, w0, n)
        print(f'\n{lab} at pi_V = {PV_OPT}')
        print(f'   {"cohort":>7s}{"cons equiv":>13s}{"born to SUD":>14s}'
              f'{"born unhoused":>16s}')
        for t, c, p in paths[lab]:
            print(f'   {t:7d}{100*c:12.4f}%{100*(p[1]+p[3]):13.3f}%'
                  f'{100*(p[2]+p[3]):15.3f}%')
    return paths


def figure(paths):
    from run import style, save
    plt = style()
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    for lab, sty in (('TF', dict(color='#b2182b', marker='o')),
                     ('HF', dict(color='#2166ac', marker='s', ls='--'))):
        t = [r[0] for r in paths[lab]]
        c = [100 * r[1] for r in paths[lab]]
        ax.plot(t, c, label='Treatment First' if lab == 'TF' else 'Housing First',
                markersize=5, **sty)
    ax.axhline(0.0, color='0.35', lw=1.0, ls=':')
    ax.set_xlabel('cohort, generations after the reform')
    ax.set_ylabel('newborn welfare, consumption equivalent (\\%)')
    ax.legend(loc='best')
    save(fig, 'stylized_transition')
    return fig


def numbers(paths, par=None):
    """The placeholders Section 3.7 of the paper reads."""
    import json as _json
    here = os.path.dirname(os.path.abspath(__file__))
    par = par or with_(P(), **_json.load(open(os.path.join(here, 'calibrated.json'))))
    tf, hf = paths['TF'], paths['HF']
    d = {'pvbase': f'{par.pV:.3f}',
         'tr_t1_tf': f'{100*tf[1][1]:.2f}',
         'tr_t1_hf': f'{100*hf[1][1]:.2f}',
         'tr_inf_tf': f'{100*tf[-1][1]:.2f}',
         'tr_inf_hf': f'{100*hf[-1][1]:.2f}',
         'tr_sud0': f'{100*(tf[0][2][1]+tf[0][2][3]):.2f}',
         'tr_sudtf': f'{100*(tf[-1][2][1]+tf[-1][2][3]):.2f}',
         'tr_sudhf': f'{100*(hf[-1][2][1]+hf[-1][2][3]):.2f}'}
    out = os.path.join(here, 'transition_numbers.json')
    _json.dump(d, open(out, 'w'), indent=1)
    print('   wrote transition_numbers.json')
    for k, v in d.items():
        print(f'      {k:12s} {v}')
    return d


if __name__ == '__main__':
    paths = run()
    figure(paths)
    numbers(paths)
