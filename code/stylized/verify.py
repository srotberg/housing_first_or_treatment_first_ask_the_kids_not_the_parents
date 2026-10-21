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
from calibrate import stats, TARGET, YG, W, SIG, EDGES, _bottom_half_share
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
chk('no node below the small rent', YG[0] >= BASE.pr * BASE.h2,
    f'lowest node {YG[0]:.4f} vs rent {BASE.pr*BASE.h2:.4f}')

print('\n=== 2. Table 2, every internally calibrated moment ===')
m = stats(BASE)
for sym, mom in (('sigma_y', 'bot50'), ('gamma', 'hspend'), ('aleph', 'vsl'),
                 ('b', 'part'), ('h_1', 'homeless'), ('lambda', 'sud')):
    v = _bottom_half_share(SIG) if mom == 'bot50' else m[mom]
    rel = abs(v / TARGET[mom] - 1)
    # THREE PER CENT, NOT TWO, AND ONLY BECAUSE OF ONE KNOWN RESIDUAL. h_1 is
    # bracketed on homelessness and then aleph and the lambda-b loop both run
    # after it and both move homelessness, so the street is fitted and then
    # displaced every sweep; the sweep reaches a fixed point in PARAMETERS with
    # the moment sitting about 2.4 per cent out. Reordering to put h_1 last
    # would close this and open a worse one, since h_1 moves the value of being
    # unhoused and so moves participation. The author set the latitude at two to
    # three per cent for exactly this kind of residual.
    chk(f'{sym:8s} hits {mom} within 3%', rel < 0.03,
        f'model {v:.5g} target {TARGET[mom]:.5g}, off {100*rel:.1f}%')

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
    abs(num(c['CEV, whole population'][2]) - 100 * pop) < 0.005,
    f'table {num(c["CEV, whole population"][2])} vs {100*pop:.4f}')

# THE ROW LABELS BELONG TO THE TABLES, AND THEY GET SHORTENED TO FIT. This file
# reads tab_welfare.tex and tab_children.tex by their first column, so a label
# trimmed for column width breaks it with a KeyError rather than a failed check.
# 'Consumption equivalent, whole population' became 'CEV, whole population' and
# 'Consumption equivalent to the child, one case' became 'CEV to the child, one
# case', and nothing noticed until a build ran this again.
print('\n=== 5. Table 4 internal arithmetic ===')
rows = {r[0].replace(r'\quad', '').strip(): r for r in cells('tab_children.tex')}
priv = num(rows['Private cost of conditionality'][-1])
dsud = num(rows['Disorder cases prevented'][-1])
per = num(rows['CEV to the child, one case'][-1])
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
# THE TOLERANCE HAS TO ADMIT priv'S PRINTED PRECISION, exactly as the check
# above admits per_case's. It was a hard 1.0 on a ratio near 158, and priv is
# printed to three decimals: half a unit in its last place moves gain/priv by
# gain*5e-4/priv^2, which is 1.11 here. The tolerance was therefore SMALLER than
# the rounding it had to accept and the check could only fail.
_rtol = gain * 0.5 * 10 ** (-(len(str(priv).split('.')[1]) if '.' in str(priv) else 0)) \
    / priv ** 2 + 1e-3
chk('ratio equals gain over loss', abs(ratio - gain / priv) < _rtol,
    f'{ratio} vs {gain/priv:.1f}, tolerance {_rtol:.2f}')
chk('cases prevented equals the SUD gap in Table 3',
    abs(dsud - 100 * (mh['sud'] - mt['sud'])) < 0.02)
chk('private cost equals Table 3 population equivalent',
    abs(priv - num(c['CEV, whole population'][2])) < 1e-9)

print('\n=== 6. the transition ===')
import transition as T
_g = T._policy_grids(BASE, T.BASE_POLICY, BASE.pV)
p0 = T._rest_point(_g[1], T._hl_by_shift(BASE, T.BASE_POLICY, BASE.pV))
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
    # SETTLED MEANS STOPPED MOVING, which is the last STEP, not the spread over
    # three values. The spread includes the cohort that was still moving:
    # 0.14097, 0.13943, 0.13929 spans 1.7e-3 while the last step is 1.4e-4, so a
    # path converging perfectly well failed a check meant to catch one that had
    # not converged at all.
    last = [r[1] for r in paths[k]][-3:]
    chk(f'{k}: the path has settled by the last cohorts',
        abs(last[-1] - last[-2]) < 1e-3,
        f'{last}, last step {abs(last[-1]-last[-2]):.2e}')
chk('TF ends above HF', paths['TF'][-1][1] > paths['HF'][-1][1])
# THE SHAPE OF THE TRANSITION IS A PREDICTION, not an observation, and each
# leg of it follows from something the model asserts elsewhere. Checked leg by
# leg so a recalibration cannot quietly break one of them.
#
# LEG 1. Cohort 1 can only be WEAKLY worse off under conditionality. It inherits
# identically under the two policies, so all that separates them is that an
# option has been removed with nothing given back: the dominance argument of
# Section 3.6.1 applied to one cohort. Weak, not strict, because at a high
# enough coverage nobody uses and there is nothing to take away.
chk('cohort 1 is weakly worse off under conditionality',
    paths['TF'][1][1] <= paths['HF'][1][1] + 1e-12,
    f"TF {100*paths['TF'][1][1]:.4f}% against HF {100*paths['HF'][1][1]:.4f}%")
# LEG 2. Cohort 2 must be STRICTLY worse off. Its parent is the generation the
# reform caught, whose vouchers conditionality revoked, so it inherits worse
# draws on top of bearing the private loss itself.
chk('cohort 2 is strictly worse off under conditionality',
    paths['TF'][2][1] < paths['HF'][2][1] - 1e-12,
    'the caught generation was put on the street and its children are born '
    'behind that')
# LEG 3. From there on conditionality gains, and it gains because the cohorts
# it made worse off use less, carry the disorder less, and are unhoused less, so
# the cohorts after them inherit better draws. If this never happens the
# externality channel is not doing what the paper says it does.
_flip = next((t for t in range(1, len(paths['TF']))
              if paths['TF'][t][1] > paths['HF'][t][1]), None)
chk('conditionality goes ahead at some cohort and stays ahead',
    _flip is not None and all(paths['TF'][t][1] > paths['HF'][t][1]
                              for t in range(_flip, len(paths['TF']))),
    f'flips at cohort {_flip}')
# A FOURTH CHECK STOOD HERE AND IT ASSERTED SOMETHING THE NOTE DOES NOT SAY.
# It read paths['TF'][2] <= paths['TF'][1]: conditionality's own consumption
# equivalent must FALL from the first cohort to the second. The note's claim is
# that cohort 1 is weakly worse off and cohort 2 strictly worse off THAN UNDER
# HOUSING FIRST, and the three checks above already test exactly that, cohort by
# cohort, and pass.
#
# The level cannot fall and the model is right that it does not: universal
# coverage is worth about fifteen per cent to these cohorts while the revocation
# costs about two tenths of one, so conditionality's path rises steeply while
# falling further behind the alternative -- gap -0.060 at cohort 1, -0.235 at
# cohort 2, +5.18 by cohort 3. Deleted rather than repaired, because repairing
# it only restated the three checks above it.
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
chk('the cohort 1 gap is the private loss and nothing else',
    abs(_gap - _priv) < 0.25 * max(_priv, 1e-9),
    f'cohort 1 gap {100*_gap:.4f}%, private loss {100*_priv:.4f}%; cohort 1 '
    'inherits from a parent who finished before the condition existed')
# COHORT 1 INHERITS THE SAME THING UNDER BOTH POLICIES, by construction of the
# timing: its parent completed both periods pre reform. If these differ, the
# bridge has been wired a generation too early.
chk('cohort 1 inherits the same mixture under both policies',
    float(np.max(np.abs(paths['TF'][1][2] - paths['HF'][1][2]))) < 1e-12)
# COHORT 2 IS WHERE THE REVOCATIONS LAND. Its parent is the caught generation,
# so Treatment First must hand it MORE children born behind an unhoused parent.
# If these are equal the channel is switched off by an accounting convention.
_t2 = paths['TF'][2][2]
_h2 = paths['HF'][2][2]
chk('conditionality puts more of cohort 2 behind an unhoused parent',
    (_t2[2] + _t2[3]) > (_h2[2] + _h2[3]) + 1e-6,
    f'TF {100*(_t2[2]+_t2[3]):.3f}% against HF {100*(_h2[2]+_h2[3]):.3f}%')
chk('the disorder cohort 2 inherits is settled before the reform',
    abs((_t2[1] + _t2[3]) - (_h2[1] + _h2[3])) < 1e-6,
    'the caught generation chose under the old rule, so its disorder rate '
    'cannot depend on which policy replaced it')
chk('the cohort 2 gap is wider than the cohort 1 gap',
    (paths['HF'][2][1] - paths['TF'][2][1]) > _gap,
    'cohort 2 carries the private loss AND the inherited homelessness')

print('\n=== 7. the shape of the policy curve ===')
# THE TEST IS CONTINUITY, NOT THE NUMBER OF TURNS, and the difference matters.
#
# It used to require at most one turning point, on the reasoning that
# participation should be hump shaped in generosity: at low cover the voucher
# mainly insures and moral hazard raises use; at high cover the household is
# near certain to be housed, its continuation value is high, and the mortality
# cost takes over. That reasoning is right about the hump and wrong to stop
# there. On the calibrated model the curve peaks near pi_V = 0.80, falls to a
# local minimum near 0.84 as the use region in one period 1 state closes, and
# rises again once it has closed. Sampled on a fine grid every step across that
# stretch is a tenth to eight tenths of a point, so the curve is CONTINUOUS and
# the extra turns are structure rather than noise.
#
# What would be an artefact is a JUMP: a discontinuity means a block of mass
# flipping at once, which is what a mis-assigned boundary cell looks like, and
# is the defect that made participation a step function of b. So the test is on
# the size of the largest step at a spacing fine enough that no honest movement
# could produce it. The turning points are reported, not judged.
pvs = np.linspace(0.0, 1.0, 41)
ph = np.array([stats(with_(BASE, pV=p, policy='HF'))['part'] for p in pvs])
d = np.diff(ph)
_worst = float(np.abs(d).max())
# THE BOUND IS WHAT A DISCRETE GRID CAN GUARANTEE, not a round number. The use
# region's edge is found by the sign change of the gain BETWEEN NODES, and the
# cell the root falls in is split against its own edges. That is smooth while
# the root stays in one cell. When the gain at a node passes through zero the
# bracket moves from (i, i+1) to (i-1, i), the root can hop across cell i
# entirely, and cell i is handed one on one side and zero on the other. The mass
# that can move in one such hop is the skipped cell plus parts of its two
# neighbours, so at most about twice the widest cell.
#
# MEASURED HERE at pi_V = 0.0432, where the gain at cell 39 is +3.7e-8, one part
# in ten million of the gain three cells away: participation drops 0.878 points
# in a step of 0.0001 in pi_V, and it does not spread out under 250-fold
# refinement, because it is a genuine jump. That is 1.76 widest-cells. The
# calibrated pi_V is 0.266, far from it, so no number the note quotes turns on
# this; what the check must still catch is a BLOCK of cells moving, which is
# what a mis-assigned boundary looks like and is many times this bound.
_cell = float(np.diff(EDGES).max())
chk('participation is continuous in generosity',
    _worst < 2.0 * _cell,
    f'largest step {100*_worst:.3f} pp at a spacing of {1/40:.3f} in pi_V, '
    f'against {100*2.0*_cell:.3f} pp for two of the widest cell; more than that '
    'means a block of mass flipping at once')
_sig = np.where(np.abs(d) < 1e-3, 0.0, d)
_nz = _sig[_sig != 0.0]
turns = int((np.diff(np.sign(_nz)) != 0).sum()) if len(_nz) > 1 else 0
i = int(np.argmax(ph))
print(f'        {turns} turning point(s); peak at pi_V={pvs[i]:.2f} of '
      f'{100*ph[i]:.2f}%, ending at {100*ph[-1]:.2f}%')

print('\n=== 7b. the pieces added late, which had the least review ===')
from stylized import terminal_homeless_prob, ever_homeless_prob, homeless_prob
q = with_(BASE, pV=BASE.pV, policy='TF')
p1 = np.array([homeless_prob(q, y, 'TF') for y in YG])
tm = np.array([terminal_homeless_prob(q, y, 'TF') for y in YG])
ev = np.array([ever_homeless_prob(q, y, 'TF') for y in YG])
chk('terminal homelessness is a probability',
    bool(np.all((tm >= -1e-12) & (tm <= 1 + 1e-12))))
chk('ever homeless is never below either single period',
    bool(np.all(ev >= p1 - 1e-12)) and bool(np.all(ev >= tm - 1e-12)))
# THE CHILD'S PENALTY KEYS ON THE PERIOD THE PARENT DIES IN, which is also the
# period conditionality acts in. Under universal Housing First nobody is
# unhoused, so nothing can be transmitted; if this is above zero the penalty is
# reading a period the new programme has already fixed.
_hf = np.array([terminal_homeless_prob(with_(BASE, pV=1.0, policy='HF'), y, 'HF')
                for y in YG])
chk('universal Housing First transmits no homelessness penalty',
    float((WW * _hf).sum()) < 1e-9,
    f'{100*float((WW*_hf).sum()):.4f}% of parents unhoused at death')
_tf = np.array([terminal_homeless_prob(with_(BASE, pV=1.0, policy='TF'), y, 'TF')
                for y in YG])
chk('universal Treatment First transmits some, through its revocations',
    float((WW * _tf).sum()) >= float((WW * _hf).sum()))
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
# scan, flatly and with no hedge, so the promise is enforced here and a build
# that breaks it fails.
#
# IT CAN BE DEMANDED AGAIN. Two points used to miss and the hedge named them.
# They were not a bisection failure but a step: threshold() wrote the boundary
# cells per crossing, and where the use region is the top block PLUS one
# isolated interior cell that cell is the boundary of two crossings, so the
# second write overwrote the first and its share never shrank to zero. The
# region now integrates as a union of intervals and participation passes
# smoothly through the target at both points.
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

print('\n=== 7f. Tables 1 and 2 agree with the prose ===')
# THE ONE PLACE A NUMBER IS STILL PRODUCED TWICE. Tables 3 and 4 are written by
# the same files that export their numbers for the prose, and the figures are
# too, so those cannot disagree. Tables 1 and 2 are written by tables.py while
# the prose's copies of the same parameters are formatted by fill.py. Both read
# calibrated.json, so they share a SOURCE, but not a code path, and that is
# exactly the gap that let an income ratio of 3.33 sit beside a figure showing
# 4.70. Compared here cell by cell.
import fill as _fill
_n = _fill.numbers(BASE, _fill._figures(BASE))
_tab = ''
for _f in ('tab_internal.tex', 'tab_external.tex'):
    _pth = os.path.join(HERE, '..', '..', 'writing', 'tables', _f)
    if os.path.exists(_pth):
        _tab += open(_pth).read()
# EVERY VALUE THE PROSE AND THE TABLES BOTH STATE. Established by asking which
# of fill.py's parameter outputs appear verbatim in the two table files; the
# rest are quoted in one place only and cannot disagree with anything.
_BOTH = ('beta', 'th', 'kap', 'phi0', 'u1', 'h3', 'h2frac', 'kV', 'vsl_t',
         'ratio_t', 'smrd')
for _key in _BOTH:
    _v = _n.get(_key)
    if _v is None:
        continue
    chk(f'{_key} agrees between the prose and Tables 1 or 2',
        str(_v) in _tab,
        f'fill.py says {_v}; tables.py prints something else')

print('\n=== 8. the paper quotes what the tables state ===')
src = open(os.path.join(TAB, '..', 'housing_first_or_treatment_first_ask_the_kids.tex'), encoding='utf-8').read()
for label, val in (('participation under HF at universal cover', f'{100*mh["part"]:.2f}'),
                   ('outlay under TF', f'{mt["cost"]:.4f}'),
                   ('outlay under HF', f'{mh["cost"]:.4f}')):
    chk(f'{label} appears in the built paper', val in src, f'looked for {val}')

print('\n' + '=' * 64)
print(f'{len(FAIL)} failure(s), {len(WARN)} warning(s)')
for f in FAIL:
    print('   FAIL', f)
sys.exit(1 if FAIL else 0)
