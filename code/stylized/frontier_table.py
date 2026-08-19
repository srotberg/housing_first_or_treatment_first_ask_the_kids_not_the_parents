"""
Collect the frontier points and CHECK EACH ONE IS ACTUALLY CALIBRATED before
reading a screen off it.

Each point is a calibration at a fixed theta run for two sweeps rather than five,
which is a deliberate trade of accuracy for coverage. Two sweeps may not converge,
and a screen read off a model whose moments are not on target is not evidence
about the model: that mistake has been made once in this project already, when a
diagnostic was read off a file another process was overwriting. So every point is
reconstructed from its checkpoint, every targeted moment is recomputed, and the
worst relative gap is printed beside the screen. A point with a large gap is
reported as NOT CONVERGED rather than ranked.

Run:  python3 frontier_table.py
"""
import glob
import json
import os
import re
import numpy as np
from stylized import P, with_, value1
from calibrate import stats, TARGET, YG
from run import _scaled

PAT = re.compile(r'checkpoint_front_([0-9.]+)_([0-9.]+)\.json$')


def par_of(path):
    ba = float(PAT.search(path).group(1))
    kw = json.load(open(path))
    return with_(P(), beta_ann=ba, beta=ba**30, R=1.0/ba**30, **kw)


if __name__ == '__main__':
    rows = []
    for f in sorted(glob.glob('checkpoint_front_*.json')):
        q = par_of(f)
        m = stats(q)
        gap = max(abs(m[k] / TARGET[k] - 1.0) for k in TARGET)
        rm = stats(_scaled(q, 'mortality', 1.0))['r_use']
        ru = stats(_scaled(q, 'unemployment', 1.0))['r_use']
        mv = float(min(value1(q, y, 'HF') for y in YG))
        ok = bool(rm < 1.0 and ru > 1.0 and m['r_use'] < 1.0 and mv > 0.0)
        rows.append(dict(beta_ann=q.beta_ann, th=q.th, gap=gap,
                         dshare=m['dshare'], part=m['part'], sud=m['sud'],
                         homeless=m['homeless'], vsl=m['vsl'],
                         r_use=m['r_use'], r_mort=rm, r_unemp=ru, minv1=mv,
                         ok=ok, lam=q.lam, gam=q.gam, aleph=q.aleph, b=q.b))

    rows.sort(key=lambda r: (r['beta_ann'], r['th']))
    print(f'{"beta":>7}{"theta":>7}{"gap":>7}{"dshare":>9}{"part":>7}{"sud":>7}'
          f'{"r_use":>7}{"r_mort":>8}{"r_unemp":>9}{"minv1":>7}  screen')
    for r in rows:
        tag = ('NOT CONVERGED' if r['gap'] > 0.02
               else ('PASSES' if r['ok'] else 'fails'))
        print(f'{r["beta_ann"]:7.4f}{r["th"]:7.3f}{r["gap"]:7.3f}'
              f'{100*r["dshare"]:8.2f}%{100*r["part"]:6.2f}%{100*r["sud"]:6.2f}%'
              f'{r["r_use"]:7.2f}{r["r_mort"]:8.2f}{r["r_unemp"]:9.2f}'
              f'{r["minv1"]:7.2f}  {tag}')

    good = [r for r in rows if r['ok'] and r['gap'] <= 0.02]
    print()
    if good:
        best = max(good, key=lambda r: r['dshare'])
        print(f'BEST: beta_ann {best["beta_ann"]}, theta {best["th"]:.3f}, '
              f'drug spending {100*best["dshare"]:.2f} per cent, '
              f'mortality alone {best["r_mort"]:.2f}')
    else:
        print('NO POINT PASSES every screen at a converged calibration yet.')
    json.dump(rows, open('frontier_all.json', 'w'), indent=1)
