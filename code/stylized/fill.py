"""
Fill the note's inline numbers straight from the model.

Every number quoted in the prose of housing_first_children_later.tex is written as a
placeholder @@name@@ in housing_first_children_later.src.tex, and this file computes each one
and writes housing_first_children_later.tex. Nothing in the note can then drift away from the
code, which is the same discipline the tables already follow.

Run:  python3 fill.py
"""

import json
import os
import numpy as np
from stylized import P, with_, value1
from calibrate import YG, W, stats, bracket, TARGET
from welfare import cev, v1_pop
from children import child_grid, shifted, DEL_D
from run import _scaled

HERE = os.path.dirname(os.path.abspath(__file__))
WRITE = os.path.normpath(os.path.join(HERE, '..', '..', 'writing'))
WW = W / W.sum()


def numbers(base):
    out = {}
    pc = lambda z, n=2: f'{100*z:.{n}f}'

    out['beta'] = f'{base.beta:.3f}'
    out['R'] = f'{base.R:.3f}'
    out['u0'] = f'{base.u0:.3f}'
    out['u1'] = f'{base.u1:.4f}'
    out['phi0'] = f'{base.phi0:.2f}'
    out['pV'] = f'{base.pV:.2f}'
    out['phi1'] = f'{base.phi0 * (1.0 - base.kap):.2f}'
    out['kap'] = f'{base.kap:.2f}'
    out['dth0'] = f'{100*(1.0 - base.phi0):.0f}'
    out['dth1'] = f'{100*(1.0 - base.phi0*(1.0 - base.kap)):.0f}'
    out['beta_ann'] = f'{base.beta_ann:.3f}'
    out['vsl_t'] = f'{TARGET["vsl"]:.0f}'
    mb = stats(base)
    out['dshare_m'] = f'{100*mb["dshare"]:.2f}'
    # the conversion from use to disorder is IMPLIED here rather than
    # targeted, so it is quoted from the model and never typed into the text
    out['prog_m'] = f'{100*mb["prog"]:.1f}'
    out['sudhl'] = f'{100*mb["sud_of_homeless"]:.0f}'
    out['r_base'] = f'{mb["r_use"]:.2f}'
    out['hshare_m'] = f'{100*mb["housing_share"]:.0f}'
    out['hspend_m'] = f'{100*mb["hspend"]:.1f}'
    # what gamma would have to be with a CONTINUOUS housing choice: the
    # Cobb-Douglas share of non drug spending times (1-theta)
    out['gam_naive'] = f'{0.268 * (1.0 - base.th):.3f}'
    out['th'] = f'{base.th:.2f}'
    out['gam'] = f'{base.gam:.3f}'
    out['lam'] = f'{base.lam:.0f}'

    # one rental size only: the model that fails to calibrate
    out['homeless1'] = pc(stats(with_(base, h_sm=base.h_lg))['homeless'])

    # the two channels, both ends
    out['r_off'] = f'{stats(_scaled(base, "mortality", 0.0))["r_use"]:.2f}'
    out['r_mort'] = f'{stats(_scaled(base, "mortality", 1.0))["r_use"]:.2f}'
    out['r_mort_half'] = f'{stats(_scaled(base, "mortality", 0.5))["r_use"]:.2f}'
    out['r_unemp'] = f'{stats(_scaled(base, "unemployment", 1.0))["r_use"]:.2f}'
    # past the calibrated point, which is what the figure now shows
    out['r_mort125'] = f'{stats(_scaled(base, "mortality", 1.25))["r_use"]:.2f}'
    out['r_unemp125'] = f'{stats(_scaled(base, "unemployment", 1.25))["r_use"]:.2f}'

    # the policy experiment
    m0 = stats(with_(base, pV=0.0, policy='HF'))
    mt = stats(with_(base, pV=1.0, policy='TF'))
    mh = stats(with_(base, pV=1.0, policy='HF'))
    out['p0'] = pc(m0['part'])
    out['pt'] = pc(mt['part'])
    out['ph'] = pc(mh['part'])
    out['vol'] = f'{100*(mt["part"]-m0["part"]):+.2f}'
    out['mh'] = f'{100*(mh["part"]-mt["part"]):+.2f}'
    out['net'] = f'{100*(mh["part"]-m0["part"]):+.2f}'
    out['hl0'] = pc(m0['homeless'])
    out['sudh'] = pc(mh['sud'], 3)
    out['sudt'] = pc(mt['sud'], 3)
    out['costh'] = f'{mh["cost"]:.4f}'
    out['costt'] = f'{mt["cost"]:.4f}'

    # welfare at universal cover
    vh = v1_pop(base, 'HF', 1.0)
    vt = v1_pop(base, 'TF', 1.0)
    lam = cev(base, vh - vt)
    hit = lam > 1e-6
    out['worse'] = f'{100*float((WW * (vt < vh - 1e-9)).sum()):.1f}'
    out['cev_aff'] = pc(float((WW * lam)[hit].sum() / max(WW[hit].sum(), 1e-12)))
    out['cev_pop'] = pc(float((WW * lam).sum()), 3)

    # the externality on children
    v1b, useb = child_grid(base, 'HF', base.pV)
    progb = stats(with_(base, policy='HF', pV=base.pV))['prog']
    ratio = shifted(useb, DEL_D) / max(shifted(useb, 0.0), 1e-12)
    out['ratio'] = f'{ratio:.1f}'
    v1u, _ = child_grid(base, 'HF', 1.0)
    per_case = cev(base, shifted(v1u, 0.0) - shifted(v1u, DEL_D))
    priv = float((WW * cev(base, vh - vt)).sum())
    dsud = mh['sud'] - mt['sud']
    gain = dsud * per_case
    out['percase'] = pc(per_case, 1)
    out['priv'] = pc(priv, 3)
    out['dsud'] = pc(dsud, 3)
    out['gain'] = pc(gain, 3)
    out['ratiogl'] = f'{gain / max(priv, 1e-12):.1f}'

    v1 = np.array([value1(base, y, 'HF') for y in YG])
    out['minv1'] = f'{v1.min():.2f}'
    return out


# WHAT CHANGED SINCE THE LAST VERSION THE READER SAW, marked rather than
# described. numbers_prev.json holds this same dictionary computed at the
# previous calibration, so a number is red if and only if it actually moved.
# Refresh it with `python3 fill.py --freeze` once a version has been sent out,
# so the next round's red marks what moved since THAT version and not since
# some older one. (The comment here used to point at scratchpad/baseline.py,
# which does not exist.)
PREV = os.path.join(HERE, 'numbers_prev.json')


def mark(new, prev):
    """Wrap every value that moved in \new{}, and leave the rest black."""
    out, moved = {}, []
    for k, v in new.items():
        # a key MISSING from prev is a number the reader has not seen either, so
        # it is red for the same reason a changed one is
        if prev is not None and (k not in prev or prev[k] != v):
            out[k] = r'\new{' + v + '}'
            moved.append(f'{k}: {prev.get(k, "new")} -> {v}')
        else:
            out[k] = v
    return out, moved


if __name__ == '__main__':
    import sys
    base = with_(P(), **json.load(open(os.path.join(HERE, 'calibrated.json'))))
    n = numbers(base)
    if '--freeze' in sys.argv:
        json.dump(n, open(PREV, 'w'), indent=1)
        print(f'   froze {len(n)} numbers into numbers_prev.json; '
              'the next run marks what moves from here')
        raise SystemExit
    prev = json.load(open(PREV)) if os.path.exists(PREV) else None
    if prev is None:
        print('   numbers_prev.json missing: nothing will be marked red')
    n, moved = mark(n, prev)
    src = open(os.path.join(WRITE, 'housing_first_children_later.src.tex')).read()
    missing = set()
    for k in sorted(n, key=len, reverse=True):
        src = src.replace(f'@@{k}@@', n[k])
    import re
    for m in re.findall(r'@@[a-zA-Z_0-9]+@@', src):
        missing.add(m)
    open(os.path.join(WRITE, 'housing_first_children_later.tex'), 'w').write(src)
    for k in sorted(n):
        print(f'   {k:12s} {n[k]}')
    print(f'\n   {len(moved)} number(s) moved and are marked red:')
    for m in moved:
        print(f'      {m}')
    if missing:
        print('\n   UNFILLED PLACEHOLDERS:', ' '.join(sorted(missing)))
    else:
        print('\n   wrote housing_first_children_later.tex, every placeholder filled')
