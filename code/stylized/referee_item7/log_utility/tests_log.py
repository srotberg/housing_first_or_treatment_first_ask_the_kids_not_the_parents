"""Steps 2 and 3: every Section 3 number gradient.py produces, at the sigma = 2 benchmark (gradient.json) and at
the log calibration (log_calibration.json from calibrate_log.py), side by side; the Figure 1 scans for both;
the value-of-life checks and where users sit.  Nothing in gradient.py is changed: gradient.numbers() and
gradient.draw() write into the paper's directories, so the numbers are recomputed here with numbers()'s own
rules and draw() is pointed at results/referee_item7/log_utility/ before it is called.

usage: python3 code/stylized/referee_item7/log_utility/tests_log.py   (uses every core)
"""
import json
import os
from multiprocessing import Pool

import numpy as np
from scipy.special import ndtri

from common import G, BENCH, OUT, y_zero, load_log

SPECS = None


def specs():
    return dict(bench=dict(BENCH), log=load_log())


def run_scan(job):
    spec, save, which = job
    q = {**specs()[spec], 'save': save}
    try:
        sc, r = G.scan(q, which)
        return job, dict(sc=sc.tolist(), r=r.tolist())
    except (AssertionError, ValueError) as e:
        return job, dict(error=repr(e))


def fig_numbers(panels):
    """gradient.numbers()'s scan entries, without writing gradient_numbers.json."""
    d = {}
    for tag, curves in zip(('', '_ns'), panels.values()):
        if any('error' in c for c in curves.values()):
            d[f'error{tag}'] = {w: c.get('error') for w, c in curves.items()}
            continue
        cv = {w: (np.array(c['sc']), np.array(c['r'])) for w, c in curves.items()}
        at = lambda which, x: cv[which][1][int(np.argmin(np.abs(cv[which][0] - x)))]
        cm, cu = G._cross(*cv['mortality']), G._cross(*cv['unemployment'])
        d.update({f'g_r_none{tag}': G.tn(cv['mortality'][1][0]),
                  f'g_rm_cal{tag}': G.tn(at('mortality', 1.0)), f'g_rm_hi{tag}': G.tn(at('mortality', G.SCAN_HI)),
                  f'g_ru_cal{tag}': G.tn(at('unemployment', 1.0)), f'g_ru_hi{tag}': G.tn(at('unemployment', G.SCAN_HI)),
                  f'g_cross_m_pc{tag}': f'{100 * cm:.0f}' if cm is not None else '',
                  f'g_cross_u_pc{tag}': f'{100 * cu:.0f}' if cu is not None else ''})
    return d


def checks(q):
    """Value of life (as ab_value_of_life_and_band.py) and where users sit, on 400,000 equal-mass nodes."""
    m = G.moments(q)
    dist = m['dist']
    N = 400000
    p = (np.arange(N) + 0.5) / N
    y = np.exp(dist.s * ndtri(dist.Ft + p * (1 - dist.Ft)) - 0.5 * dist.s ** 2) / dist.M
    au, Vu = G.plan(y, q, True)
    an, Vn = G.plan(y, q, False)
    use = Vu > Vn
    V1 = np.where(use, Vu, Vn)
    a = np.where(use, au, an)
    f = G.FA(y, q)
    pi, pf, k = q['pi_d'], q['phibar'], q['kappa']
    flow1 = np.where(use, G._U1(y - a + f, q), G._U0(y - a + f, q)) + q['aleph']
    s_clean = np.where(use, (1 - pi) * pf, pf)
    s_sud = np.where(use, pi * pf ** k, 0.0)
    tot = negW = negF = 0.0
    neg_states = []
    for d, sw in ((0, s_clean), (1, s_sud)):
        u = q['u1'] if d else q['u0']
        Wd = G.W(a, y, q, d)
        fe = G._U0(y + a + f, q) + q['aleph']
        fu = G._U0(a + q['cbar'], q) + q['aleph']
        tot += sw.sum()
        negW += (sw * (Wd < 0)).sum()
        negF += (sw * ((1 - u) * (fe < 0) + u * (fu < 0))).sum()
        for lab, fl, pr in (('employed', fe, 1 - u), ('out of work', fu, u)):
            bad = (fl < 0) & (sw > 0)
            if bad.any():
                neg_states.append(dict(d=d, state=lab, pct_lo=100 * p[bad].min(), pct_hi=100 * p[bad].max(),
                                       y_lo=float(y[bad].min()), y_hi=float(y[bad].max()),
                                       share=float((sw * pr * bad).sum())))
    for s in neg_states:
        s['share'] /= tot
    yu = y[use]
    return dict(
        moments={k: float(m[k]) for k in ('vsl', 'part', 'dshare', 'r_use', 'fshare')},
        v1_ymin=float(G.V1(q['y_min'], q)[0]), v1_min=float(V1.min()), v1_share_neg=float(np.mean(V1 < 0)),
        flow1_min=float(flow1.min()), flow1_share_neg=float(np.mean(flow1 < 0)),
        W2_share_neg=float(negW / tot), flow2_share_neg=float(negF / tot), neg_states=neg_states,
        y_zero=float(y_zero(q)),
        bands=[dict(y_lo=float(lo), y_hi=float(hi), pct_lo=100 * float(dist.F(lo)), pct_hi=100 * float(dist.F(hi)))
               for lo, hi in m['intervals']],
        users_mean=float(m['r_use']), users_median=float(np.median(yu)) if use.any() else None,
        pop_median=float(dist.quantile(0.5)), grid_part=float(use.mean()))


def channel_alone(q):
    """Participation and users' income at the calibrated parameters (b NOT refitted) with each channel alone,
    and with saving off."""
    out = {}
    for save in (True, False):
        for which in ('both', 'mortality', 'unemployment', 'none'):
            g = {**q, 'save': save}
            g = G.channel(g, 'both' if which == 'both' else which, 0.0 if which == 'none' else 1.0)
            if which == 'none':
                g = G.channel({**q, 'save': save}, 'mortality', 0.0)
            m = G.moments(g)
            out[f'{which}|save={save}'] = dict(part=float(m['part']), r_use=float(m['r_use']) if m['part'] > 0 else None)
    return out


if __name__ == '__main__':
    S = specs()
    jobs = [(s, save, w) for s in S for save in (True, False) for w in ('mortality', 'unemployment')]
    with Pool(os.cpu_count()) as pool:
        ch = pool.map_async(checks, [S['bench'], S['log']])
        ca = pool.map_async(channel_alone, [S['bench'], S['log']])
        sc = dict(pool.map(run_scan, jobs, chunksize=1))
        ch, ca = ch.get(), ca.get()
    res = {}
    for i, s in enumerate(S):
        panels = {'With saving (the model)': {w: sc[(s, True, w)] for w in ('mortality', 'unemployment')},
                  'Saving switched off': {w: sc[(s, False, w)] for w in ('mortality', 'unemployment')}}
        res[s] = dict(q={k: S[s][k] for k in G.FREE}, checks=ch[i], channel_alone=ca[i], fig=fig_numbers(panels),
                      scans={f'{t}|{w}': c for t, cs in panels.items() for w, c in cs.items()})
        if s == 'log' and not any('error' in c for cs in panels.values() for c in cs.values()):
            G.FIGURES = OUT          # draw() writes FIGURES/stylized_who_uses.{pdf,png}; pointed away from writing/
            G.draw({t: {w: (np.array(c['sc']), np.array(c['r'])) for w, c in cs.items()} for t, cs in panels.items()})
            for ext in ('.pdf', '.png'):
                os.replace(os.path.join(OUT, 'stylized_who_uses' + ext), os.path.join(OUT, 'stylized_who_uses_log' + ext))
    json.dump(res, open(os.path.join(OUT, 'tests_log.json'), 'w'), indent=1)
    for s in res:
        print('==', s, res[s]['q'])
        print('  fig', res[s]['fig'])
        print('  checks', {k: v for k, v in res[s]['checks'].items()})
        print('  channel alone', res[s]['channel_alone'])
