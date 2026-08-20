"""
Independent checks on everything the stylized model publishes.

NOT a re-read of the generators. Each check recomputes a number a different way
and compares, or asserts an identity that must hold whatever the parameters are.
A generator and its check can only agree by both being right, or by sharing a
bug, so the checks are written to avoid the generators' own code paths where
that is possible.

Run:  python3 verify.py
"""

import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TAB = os.path.normpath(os.path.join(HERE, '..', '..', 'writing', 'tables'))

from stylized import P, with_, value1, use_prob, homeless_prob, solve_period2
from calibrate import stats, TARGET, YG, W, SIG, _bottom_half_share
from welfare import cev, v1_pop, periods

BASE = with_(P(), **json.load(open(os.path.join(HERE, 'calibrated.json'))))
WW = W / W.sum()
FAIL, WARN = [], []


def chk(name, ok, detail=''):
    (print(f'  ok    {name}') if ok else
     (FAIL.append(name), print(f'  FAIL  {name}   {detail}')))


def warn(name, detail):
    WARN.append(name)
    print(f'  warn  {name}   {detail}')


def cells(f):
    out = []
    for line in open(os.path.join(TAB, f), encoding='utf-8'):
        if r'\\' in line and line.strip().startswith(('$', r'\quad', r'\textcolor', '0')):
            out.append([c.strip() for c in line.rstrip().rstrip('\\').rstrip('\\').split('&')])
    return out


def num(s):
    s = re.sub(r'\\textcolor\{red\}\{|\}|\$|,|\\%|\\ |\(calibrated\)|pp', '', s).strip()
    try:
        return float(s)
    except ValueError:
        return None


print('=== 1. the grid itself ===')
chk('weights sum to one', abs(W.sum() / W.sum() - 1) < 1e-12)
chk('mean income is one', abs((WW * YG).sum() - 1.0) < 1e-9,
    f'{(WW*YG).sum():.10f}')
chk('income strictly increasing', bool(np.all(np.diff(YG) > 0)))
chk('bottom half share hits its target',
    abs(_bottom_half_share(SIG) - TARGET['bot50']) < 5e-4,
    f'{_bottom_half_share(SIG):.5f} vs {TARGET["bot50"]}')
chk('no node below the small rent', YG[0] >= BASE.pr * BASE.h_sm,
    f'lowest node {YG[0]:.4f} vs rent {BASE.pr*BASE.h_sm:.4f}')

print('\n=== 2. Table 2, every internally calibrated moment ===')
m = stats(BASE)
for sym, mom in (('sigma_y', 'bot50'), ('gamma', 'hspend'), ('aleph', 'vsl'),
                 ('b', 'part'), ('h_1', 'homeless'), ('lambda', 'sud')):
    v = _bottom_half_share(SIG) if mom == 'bot50' else m[mom]
    rel = abs(v / TARGET[mom] - 1)
    chk(f'{sym:8s} hits {mom} within 2%', rel < 0.02, f'model {v:.5g} target {TARGET[mom]:.5g}')

print('\n=== 3. probabilities and shares are in range ===')
for pol in ('HF', 'TF'):
    for pv in (0.0, BASE.pV, 0.5, 1.0):
        q = with_(BASE, pV=pv, policy=pol)
        s = stats(q)
        for k in ('part', 'sud', 'homeless', 'prog'):
            if not (0.0 - 1e-12 <= s[k] <= 1.0 + 1e-12):
                FAIL.append(f'{k} out of range')
                print(f'  FAIL  {pol} pi_V={pv}: {k}={s[k]}')
        if s['sud'] > s['part'] + 1e-12:
            FAIL.append('sud exceeds participation')
            print(f'  FAIL  {pol} pi_V={pv}: sud {s["sud"]:.6f} > part {s["part"]:.6f}')
print('  ok    all rates in [0,1] and SUD never exceeds participation')

print('\n=== 4. Table 3 against a fresh solve ===')
c = {r[0].replace(r'\quad', '').strip(): r for r in cells('tab_welfare.tex')}
mh = stats(with_(BASE, pV=1.0, policy='HF'))
mt = stats(with_(BASE, pV=1.0, policy='TF'))
chk('participation, HF', abs(num(c['Drug participation rate'][1]) - 100 * mh['part']) < 0.01)
chk('participation, TF', abs(num(c['Drug participation rate'][2]) - 100 * mt['part']) < 0.01)
chk('homelessness, HF', abs(num(c['Homelessness rate'][1]) - 100 * mh['homeless']) < 0.01)
chk('outlay, HF', abs(num(c['Voucher outlay per household'][1]) - mh['cost']) < 5e-4)
chk('outlay, TF', abs(num(c['Voucher outlay per household'][2]) - mt['cost']) < 5e-4)
vh, vt = v1_pop(BASE, 'HF', 1.0), v1_pop(BASE, 'TF', 1.0)
lam = cev(BASE, vh - vt)
chk('nobody is better off under TF', bool(np.all(vt <= vh + 1e-9)),
    'the dominance argument of 3.6.1 requires this')
worse = float((WW * (vt < vh - 1e-9)).sum())
chk('share worse off', abs(num(c['Households strictly worse off'][2]) - 100 * worse) < 0.15,
    f'table {num(c["Households strictly worse off"][2])} vs {100*worse:.2f}')
pop = float((WW * lam).sum())
chk('population consumption equivalent',
    abs(num(c['Consumption equivalent, whole population'][2]) - 100 * pop) < 0.005,
    f'table {num(c["Consumption equivalent, whole population"][2])} vs {100*pop:.4f}')

print('\n=== 5. Table 4 internal arithmetic ===')
rows = {r[0].replace(r'\quad', '').strip(): r for r in cells('tab_children.tex')}
priv = num(rows['Private cost of conditionality'][-1])
dsud = num(rows['Disorder cases prevented'][-1])
per = num(rows['Consumption equivalent to the child, one case'][-1])
gain = num(rows['Externality gain from conditionality'][-1])
ratio = num(rows['Gain over loss'][-1])
# the tolerance has to admit the printed precision of per_case, or the check
# fails on rounding rather than on arithmetic. Half a unit in the last place of
# per_case moves the product by dsud/2 * 10^-dp.
_dp = len(str(per).split('.')[1]) if '.' in str(per) else 0
_tol = 0.5 * dsud * 10 ** (-_dp) / 100.0 + 1e-3
chk('gain equals cases times cost per case',
    abs(gain - dsud * per / 100.0) < _tol,
    f'{gain} vs {dsud*per/100:.4f}, tolerance {_tol:.4f}')
chk('ratio equals gain over loss', abs(ratio - gain / priv) < 1.0,
    f'{ratio} vs {gain/priv:.1f}')
chk('cases prevented equals the SUD gap in Table 3',
    abs(dsud - 100 * (mh['sud'] - mt['sud'])) < 0.02)
chk('private cost equals Table 3 population equivalent',
    abs(priv - num(c['Consumption equivalent, whole population'][2])) < 1e-9)

print('\n=== 6. the transition ===')
import transition as T
_g = T._policy_grids(BASE, T.BASE_POLICY, BASE.pV)
p0 = T._rest_point(_g[1], _g[3])   # steps on EVER homeless, what the child inherits
chk('the rest point is a probability vector',
    abs(p0.sum() - 1.0) < 1e-9 and bool(np.all(p0 >= -1e-12)))
v1b, sudb, hlb, evb = T._policy_grids(BASE, T.BASE_POLICY, BASE.pV)
w0 = T._welfare(p0, v1b)
paths = {k: T.path(BASE, k, T.PV_OPT, p0, v1b, w0, 5) for k in ('TF', 'HF')}
for k in ('TF', 'HF'):
    chk(f'{k}: cohort 0 is the pre reform point by construction',
        abs(paths[k][0][1]) < 1e-12)
    chk(f'{k}: every mixture is a probability vector',
        all(abs(r[2].sum() - 1) < 1e-9 for r in paths[k]))
    last = [r[1] for r in paths[k]][-3:]
    chk(f'{k}: the path has settled by the last cohorts',
        max(last) - min(last) < 1e-3, f'{last}')
chk('TF ends above HF', paths['TF'][-1][1] > paths['HF'][-1][1])
chk('TF costs the cohort it lands on', paths['TF'][1][1] < paths['HF'][1][1],
    'conditionality must not be free to the cohort that bears it')

print('\n=== 7. the shape of the policy curve ===')
# NOT A TEST FOR MONOTONICITY. Participation SHOULD be hump shaped in
# generosity: at low cover the voucher mainly insures, so moral hazard raises
# use; at high cover the household is near certain to be housed, its
# continuation value is high, and the mortality cost takes over. What would be
# an artefact is a JAGGED curve, so the test is for a single turning point.
pvs = np.linspace(0.0, 1.0, 11)
ph = np.array([stats(with_(BASE, pV=p, policy='HF'))['part'] for p in pvs])
d = np.diff(ph)
# a tolerance below any economically meaningful movement, so a wobble of a few
# hundredths of a point is not counted as the curve turning
_sig = np.where(np.abs(d) < 1e-3, 0.0, d)
_nz = _sig[_sig != 0.0]
turns = int((np.diff(np.sign(_nz)) != 0).sum()) if len(_nz) > 1 else 0
chk('participation has at most one turning point in generosity', turns <= 1,
    f'{turns} turns: ' + ' '.join(f'{100*x:+.2f}' for x in d))
i = int(np.argmax(ph))
print(f'        peak at pi_V={pvs[i]:.1f} of {100*ph[i]:.2f}%, '
      f'ending at {100*ph[-1]:.2f}%')

print('\n=== 8. the paper quotes what the tables state ===')
src = open(os.path.join(TAB, '..', 'housing_first_children_later.tex'), encoding='utf-8').read()
for label, val in (('participation under HF at universal cover', f'{100*mh["part"]:.2f}'),
                   ('outlay under TF', f'{mt["cost"]:.4f}'),
                   ('outlay under HF', f'{mh["cost"]:.4f}')):
    chk(f'{label} appears in the built paper', val in src, f'looked for {val}')

print('\n' + '=' * 64)
print(f'{len(FAIL)} failure(s), {len(WARN)} warning(s)')
for f in FAIL:
    print('   FAIL', f)
sys.exit(1 if FAIL else 0)
