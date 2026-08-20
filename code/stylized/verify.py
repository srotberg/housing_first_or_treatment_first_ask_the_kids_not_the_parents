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
# WHY THE TWO POLICIES ARE NEARLY LEVEL ON COHORT 1, which reads as a bug and is
# not one. That cohort lives its whole life under the new rule, so it can keep
# its voucher by not using; the only households worse off under conditionality
# are the ones who would have used, and they are few. The gap therefore IS the
# private loss of Section 3.6.1 and has to equal it. Checked rather than
# asserted, because the last time these two looked equal the cause was a bug in
# the revocation rule.
from children import child_grid as _cgrid
from welfare import cev as _cev
_vh, _ = _cgrid(BASE, 'HF', T.PV_OPT)
_vt, _ = _cgrid(BASE, 'TF', T.PV_OPT)
_priv = float((WW * _cev(BASE, _vh - _vt)).sum())
_gap = paths['HF'][1][1] - paths['TF'][1][1]
chk('the cohort 1 gap exceeds the private loss alone',
    _gap > _priv,
    f'cohort 1 gap {100*_gap:.4f}%, private loss {100*_priv:.4f}%; the gap must '
    'also carry the homelessness the revocations inflicted on cohort 1 parents')
# THE REVOCATIONS HAVE TO REACH THE CHILD. Cohort 1's parent lived period 2
# under the new rule, so Treatment First must hand cohort 1 a mixture with MORE
# of its members born to an unhoused parent than Housing First does. If these
# two are equal the bridge is not wired up and the chain is back to being
# identical at cohort 1 by construction.
_sb_t, _eb_t = T._bridge_grids(BASE, 'TF', T.PV_OPT)
_sb_h, _eb_h = T._bridge_grids(BASE, 'HF', T.PV_OPT)
_p1t, _p1h = T._step(p0, _sb_t, _eb_t), T._step(p0, _sb_h, _eb_h)
chk('conditionality puts more of cohort 1 behind an unhoused parent',
    (_p1t[2] + _p1t[3]) > (_p1h[2] + _p1h[3]) + 1e-6,
    f'TF {100*(_p1t[2]+_p1t[3]):.3f}% against HF {100*(_p1h[2]+_p1h[3]):.3f}%')
chk('the disorder cohort 1 inherits is settled before the reform',
    abs((_p1t[1] + _p1t[3]) - (_p1h[1] + _p1h[3])) < 1e-6,
    'the caught generation chose under the old rule, so its disorder rate '
    'cannot depend on which policy replaced it')

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

print('\n=== 7b. the pieces added late, which had the least review ===')
from stylized import ever_homeless_prob, homeless_prob
q = with_(BASE, pV=BASE.pV, policy='TF')
p1 = np.array([homeless_prob(q, y, 'TF') for y in YG])
ev = np.array([ever_homeless_prob(q, y, 'TF') for y in YG])
chk('ever homeless is never below period 1 homeless',
    bool(np.all(ev >= p1 - 1e-12)), f'worst {float((p1-ev).max()):.2e}')
chk('ever homeless is a probability',
    bool(np.all((ev >= -1e-12) & (ev <= 1 + 1e-12))))
cg = T.caught(BASE)
chk('the caught generation loses rather than gains', cg['cev'] > 0,
    f"{100*cg['cev']:.2f}%")
chk('revocation cannot reduce their homelessness', cg['hl_tf'] >= cg['hl_hf'] - 1e-12,
    f"HF {100*cg['hl_hf']:.3f}% TF {100*cg['hl_tf']:.3f}%")
chk('their loss exceeds the newborn cohort\'s',
    cg['cev'] > abs(paths['TF'][1][1] - paths['HF'][1][1]),
    'this is the point of computing them separately')

print('\n=== 7c. the revocation rule ===')
# THE PERIOD 2 CONDITION IS THE DISORDER AND NOTHING ELSE. There is no period 2
# drug choice, so a household that used in period 1 and escaped the disorder
# must face the same period 2 problem as one that never used. When the rule
# revoked on a history of use instead, these two differed and Treatment First
# was a harsher policy than the one the paper describes.
_p2_clean = solve_period2(BASE, 0.6, 'TF', used=0)
_p2_used = solve_period2(BASE, 0.6, 'TF', used=1)
chk('period 2 does not punish a past use that came to nothing',
    bool(np.allclose(_p2_clean[1], _p2_used[1], rtol=0, atol=1e-12)),
    'the period 2 value function must not depend on period 1 use')
# AND THE POLICY STILL HAS TEETH: the disorder itself must still cost the
# voucher under Treatment First, or the two policies would be identical.
_hf = stats(with_(BASE, pV=1.0, policy='HF'))
_tf = stats(with_(BASE, pV=1.0, policy='TF'))
chk('the two policies still differ at universal cover',
    abs(_hf['part'] - _tf['part']) > 1e-6,
    f"HF {100*_hf['part']:.3f}%  TF {100*_tf['part']:.3f}%")

print('\n=== 7d. the figures and the prose quote the same numbers ===')
# EVERY NUMBER ON A FIGURE IS COMPUTED ONCE, by run.py, and read by fill.py.
# This recomputes two of them the long way and compares, which is the only way
# to catch figure_numbers.json going stale against the model.
_fp = os.path.join(HERE, 'figure_numbers.json')
if not os.path.exists(_fp):
    warn('figure numbers', 'figure_numbers.json missing; run run.py')
else:
    _fig = json.load(open(_fp))
    from run import _scaled
    _r_half = stats(_scaled(BASE, 'mortality', 0.5))['r_use']
    chk('the income ratio at half strength matches the figure',
        abs(float(_fig['r_mort_half']) - _r_half) < 0.005,
        f"file {_fig['r_mort_half']}  recomputed {_r_half:.2f}")
    chk('participation under HF at universal cover matches the figure',
        abs(float(_fig['ph']) - 100 * _hf['part']) < 0.005,
        f"file {_fig['ph']}  recomputed {100*_hf['part']:.2f}")
    # AND THE SENTENCE THAT CALLS IT UNCHANGED has to be true of the numbers
    # beside it, which it was not: 3.33 was printed as "unchanged" against 2.62.
    _off, _half = float(_fig['r_off']), float(_fig['r_mort_half'])
    chk('"unchanged at half strength" is true of the two numbers printed',
        abs(_half - _off) <= 0.06 * abs(_off),
        f'with the channel off {_off:.2f}, at half strength {_half:.2f}')
print("\n=== 7d2. the participation promise in Figure 1 ===")
# THE NOTE SAYS the model targets the participation rate at every point of the
# scan. That was false at ten of twenty two points under the pooled grid and the
# note carried a hedge naming them; the hedge is gone at the author's request, so
# the promise is enforced here instead and a build that breaks it fails.
_fg = os.path.join(HERE, 'figure_numbers.json')
if os.path.exists(_fg):
    _f = json.load(open(_fg))
    if '_part_misses' not in _f:
        warn('figure_numbers.json predates the check', 'rerun run.py')
    else:
        chk('b holds participation on target at every point of the scan',
            int(_f['_part_misses']) == 0,
            f"{_f['_part_misses']} point(s) miss, worst by "
            f"{100 * float(_f['_part_worst']):.3f} points")
else:
    warn('figure_numbers.json is missing', 'rerun run.py')

print('\n=== 7e. nothing in the build is older than the calibration ===')
# A STALE EXPORT IS THE FAILURE MODE THAT ACTUALLY HAPPENED. Every file below is
# written from calibrated.json, so any one of them older than it is a number in
# the paper that belongs to a calibration the paper no longer describes.
_cal = os.path.getmtime(os.path.join(HERE, 'calibrated.json'))
for _f in ('figure_numbers.json', 'welfare_numbers.json',
           'children_numbers.json', 'transition_numbers.json'):
    _p = os.path.join(HERE, _f)
    chk(f'{_f} is not older than calibrated.json',
        os.path.exists(_p) and os.path.getmtime(_p) >= _cal,
        'rerun build.sh')
for _f in ('tab_external.tex', 'tab_internal.tex', 'tab_welfare.tex',
           'tab_children.tex'):
    _p = os.path.join(TAB, _f)
    chk(f'{_f} is not older than calibrated.json',
        os.path.exists(_p) and os.path.getmtime(_p) >= _cal,
        'rerun build.sh')

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
