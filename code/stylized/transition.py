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
policy and the chain starts moving, geometrically, to a new rest point. It
settles in two or three cohorts, so five is enough to see all of it.

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

from stylized import P, with_, value1, use_prob, homeless_prob, ever_homeless_prob
from calibrate import YG, W, stats
from welfare import cev
from children import DEL_D, DEL_H

WW = W / W.sum()
LY = np.log(YG)

BASE_POLICY = 'HF'      # the world as it is: rationed vouchers, no condition
PV_OPT = 1.0            # the optimal Treatment First programme is universal
# FIVE COHORTS, because the chain settles in two or three. The mixture a cohort
# is born into depends on its parent's outcomes and nothing further back, since
# the base draw is redrawn every generation, so the path is at its new rest
# point almost immediately. Showing eight would be five flat markers.
GENERATIONS = 5


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
    # TWO HOMELESSNESS OBJECTS, and they are not the same one. What a cohort
    # PASSES ON is whether the parent was ever unhoused, in either period, since
    # that is what the child's penalty is keyed on. What the figure REPORTS is
    # the realised period 1 rate, which is the rate the model is calibrated to
    # and the one comparable with the data. Using the first for both would
    # overstate the published homelessness rate; using the second for both would
    # switch off the channel by which conditionality's own revocations reach a
    # child.
    hl = np.array([homeless_prob(q, y, policy) for y in YG], dtype=float)
    ev = np.array([ever_homeless_prob(q, y, policy) for y in YG], dtype=float)
    prog = stats(q)['prog']
    return (v1, np.clip(use * prog, 0.0, 1.0), np.clip(hl, 0.0, 1.0),
            np.clip(ev, 0.0, 1.0))


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


def _outcome(p, g):
    """A cohort's own realised rate of something, given the mixture it is born
    into: its homelessness, or its disorder rate. The welfare path says what the
    reform is worth; these say through what."""
    return sum(ps * float((WW * _at(g, s)).sum())
               for s, ps in zip(_shifts(), p))


def caught(par, pv_new=PV_OPT):
    """THE GENERATION THE REFORM CATCHES MID LIFE, which the cohort path cannot
    show and which is where conditionality's cost actually falls.

    Every cohort in the path lives its whole life under one policy. The
    households in period 2 when the policy changes did not: they chose whether
    to use under the OLD rule, period 2 is terminal so a disorder cannot be
    recovered from, and Treatment First now withdraws their voucher for a
    decision taken before the rule existed. They are the transition's cost, and
    a figure that omits them makes conditionality look nearly free.

    Returns the consumption equivalent they lose and the homelessness the
    revocation itself creates, integrating over the assets they actually saved
    and the disorder they actually drew under the old programme."""
    from stylized import period1, solve_period2
    old = with_(par, pV=par.pV, policy=BASE_POLICY)
    new_h = with_(par, pV=pv_new, policy='HF')
    new_t = with_(par, pV=pv_new, policy='TF')
    dv = mass = hl_h = hl_t = 0.0
    for i, y in enumerate(YG):
        for p, gain, v, bu, bn, inc, _own in period1(old, y, BASE_POLICY):
            uses = gain > 0.0
            a = (bu if uses else bn)[0]
            pid = (1.0 - np.exp(-old.lam * v)) if uses else 0.0
            for d, pd in ((1, pid), (0, 1.0 - pid)):
                m = WW[i] * p * pd
                if m <= 0.0:
                    continue
                agh, W2h, H2h, _, _ = solve_period2(new_h, y, 'HF', used=int(uses))
                agt, W2t, H2t, _, _ = solve_period2(new_t, y, 'TF', used=int(uses))
                dv += m * (float(np.interp(a, agh, W2h[:, d]))
                           - float(np.interp(a, agt, W2t[:, d])))
                hl_h += m * float(np.interp(a, agh, H2h[:, d]))
                hl_t += m * float(np.interp(a, agt, H2t[:, d]))
                mass += m
    dv /= max(mass, 1e-12)
    return dict(cev=float(cev(par, dv)), hl_hf=hl_h / max(mass, 1e-12),
                hl_tf=hl_t / max(mass, 1e-12))


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
    v1, sud, hl, ev = _policy_grids(par, policy, pV)
    v1b, sudb, hlb, evb = _policy_grids(par, BASE_POLICY, par.pV)
    out = [(0, 0.0, p0.copy(), _outcome(p0, hlb), _outcome(p0, sudb))]
    p = p0.copy()
    for t in range(1, n + 1):
        # the cohort BORN at t-1 lives under the new policy, and the mixture it
        # was born into is the one the previous cohort handed it. Cohort 1 is
        # therefore born into the OLD rest point and lives under the NEW rule.
        # It is NOT the cohort that pays for the reform: see caught().
        w = _welfare(p, v1)
        out.append((t, float(cev(par, w - w0)), p.copy(),
                    _outcome(p, hl), _outcome(p, sud)))
        p = _step(p, sud, ev)
    return out


def run(par=None, n=GENERATIONS):
    here = os.path.dirname(os.path.abspath(__file__))
    par = par or with_(P(), **json.load(open(os.path.join(here, 'calibrated.json'))))

    v1b, sudb, hlb, evb = _policy_grids(par, BASE_POLICY, par.pV)
    p0 = _rest_point(sudb, evb)
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
              f'{"born unhoused":>16s}{"homeless":>11s}{"has a SUD":>12s}')
        for t, c, p, hl, sud in paths[lab]:
            print(f'   {t:7d}{100*c:12.4f}%{100*(p[1]+p[3]):13.3f}%'
                  f'{100*(p[2]+p[3]):15.3f}%{100*hl:10.3f}%{100*sud:11.3f}%')
    return paths


def figure(paths, cg=None):
    """Three panels: what the reform is worth to each cohort, and through what.

    The welfare panel alone invites the reading that conditionality is nearly
    free, because the cohorts in it all choose not to use and so never lose a
    voucher. The homelessness and disorder panels show the mechanism doing the
    work, and the marker on the welfare panel shows the generation the reform
    catches mid life, which no cohort line can carry.
    """
    from run import style, save
    plt = style()
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 3.9))
    S = (('TF', 'Treatment First', dict(color='#b2182b', marker='o')),
         ('HF', 'Housing First', dict(color='#2166ac', marker='s', ls='--')))
    for ax, idx, ttl, ylab in (
            (axes[0], 1, 'A. Newborn welfare', 'consumption equivalent (\%)'),
            (axes[1], 3, 'B. Homelessness', 'rate (\%)'),
            (axes[2], 4, 'C. Share with a SUD', 'rate (\%)')):
        for lab, name, sty in S:
            t = [r[0] for r in paths[lab]]
            y = [100 * r[idx] for r in paths[lab]]
            ax.plot(t, y, label=name, markersize=5, **sty)
        ax.set_xlabel('cohort, generations after the reform')
        ax.set_ylabel(ylab)
        ax.set_title(ttl, loc='left', fontsize=11, fontweight='bold')
    axes[0].axhline(0.0, color='0.35', lw=1.0, ls=':')
    if cg is not None:
        # the generation already in period 2 at the switch, on the same axis but
        # marked apart, since it is measured over its remaining period only
        axes[0].plot([0], [-100 * cg['cev']], marker='v', ms=8, color='#b2182b',
                     ls='none', label='caught mid life, TF')
        axes[0].annotate('caught\nmid life', xy=(0, -100 * cg['cev']),
                         xytext=(0.35, -100 * cg['cev'] * 0.72), fontsize=8.5,
                         color='#b2182b')
    axes[0].legend(loc='center right', fontsize=9)
    save(fig, 'stylized_transition')
    return fig


def numbers(paths, par=None, cg=None):
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
    if cg is not None:
        d['tr_caught'] = f'{100*cg["cev"]:.1f}'
        d['tr_caught_hl'] = f'{100*cg["hl_tf"]:.2f}'
    out = os.path.join(here, 'transition_numbers.json')
    _json.dump(d, open(out, 'w'), indent=1)
    print('   wrote transition_numbers.json')
    for k, v in d.items():
        print(f'      {k:12s} {v}')
    return d


if __name__ == '__main__':
    paths = run()
    import json as _j, os as _o
    par = with_(P(), **_j.load(open(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)), 'calibrated.json'))))
    cg = caught(par)
    print('\ncaught mid life: loses %.2f%% of consumption; homeless %.3f%% under HF, %.3f%% under TF'
          % (100*cg['cev'], 100*cg['hl_hf'], 100*cg['hl_tf']))
    figure(paths, cg)
    numbers(paths, cg=cg)
