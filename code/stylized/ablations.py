#!/usr/bin/env python3
"""WHICH CHANNEL REVERSES THE INCOME GRADIENT?

The author, 12 September: *"examine kappa, employment risk, and omega_c to show
which one is the reason the income of users declines"*, and earlier, *"i just
want to examine whether kappa, employment risk, or omega_c control the grid
reversal"*.

THE MOMENT THAT MATTERS IS r_use, users' income over the mean.  In the data it
is 0.74; a model with no channel at all puts users ABOVE the mean, because the
drug is a normal good and the rich can afford more of it.  Something has to
push the users' income down, and the question is which of the three does it.

THE ABLATIONS ARE AT FIXED PARAMETERS, which is the right design HERE and is
not the frozen-parameter trap recorded elsewhere in this repository.  That trap
is about REACHABILITY -- asking whether a target can be hit with one dial while
the rest are held, which understates what the joint rule can do.  This asks a
different question: what does each channel CONTRIBUTE at the calibrated point.
For that, holding everything else is exactly right, because recalibrating would
let the other parameters absorb the channel being removed and the decomposition
would measure the absorption rather than the channel.

A RECALIBRATED ablation is a separate and also useful exercise -- it answers
"can the model still match the data without this channel" rather than "what
does this channel do" -- and it is not what this script runs.

THE THREE CHANNELS
  kappa       excess mortality of users.  kap = 0 is SMR 1: using carries no
              extra death risk at all.
  employment  the higher job-loss rate carried by the disorder.  u1 = u0
              removes the differential, leaving one unemployment rate.
  omega_c     the child in the parent's utility, BOTH the contemporaneous term
              and the continuation, since omega_c multiplies both and nothing
              else.
"""
import json, sys
sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code/stylized')
from stylized import with_, P, child_sud_odds_ratio, child_homeless_odds_ratio
from recalibrate import FIXED
import calibrate as C

d = json.load(open('best_vector_it1800.json'))
kw = {k: v for k, v in FIXED.items() if k not in ('kap', 'gam', 'omega', 'sigma')}
kw.update(d['_held_not_calibrated'])
kw.update(d['parameters'])
base = with_(P(), **kw)

ABL = [
    ('BASELINE',            {}),
    ('kappa off (SMR 1)',   {'kap': 0.0}),
    ('employment risk off', {'u1': base.u0}),
    ('omega_c off',         {'omega': 0.0}),
    ('all three off',       {'kap': 0.0, 'u1': base.u0, 'omega': 0.0}),
]

rows = []
for name, kwargs in ABL:
    par = with_(base, **kwargs) if kwargs else base
    m = C.stats(par)
    m['child_sud_or'] = child_sud_odds_ratio(par, C.YG, C.W)
    m['child_hl_or'] = child_homeless_odds_ratio(par, C.YG, C.W)
    rows.append((name, m))

b = rows[0][1]
print("THE INCOME GRADIENT, and what each channel contributes to it")
print("at the iteration-1800 calibration, every other parameter held\n")
h = f"{'':22}{'r_use':>9}{'vs base':>9}{'part':>9}{'dshare':>9}{'sud':>9}{'homeless':>10}"
print(h); print('-' * len(h))
for name, m in rows:
    dv = '' if name == 'BASELINE' else f"{m['r_use'] - b['r_use']:+9.4f}"
    print(f"{name:22}{m['r_use']:9.4f}{dv:>9}{m['part']:9.4f}{m['dshare']:9.4f}"
          f"{m['sud']:9.4f}{m['homeless']:10.4f}")
print('-' * len(h))
print(f"{'DATA TARGET':22}{0.7400:9.4f}{'':>9}{0.0890:9.4f}{0.1410:9.4f}"
      f"{0.0368:9.4f}{0.0100:10.4f}")

print("\nTHE CHILD, reported only\n")
h2 = f"{'':22}{'child SUD OR':>14}{'child homeless OR':>19}{'child gap':>11}"
print(h2); print('-' * len(h2))
cf = C.stats(with_(base, omega=0.0))
for name, m in rows:
    gap = ''
    if name == 'BASELINE':
        gap = f"{cf['part'] / m['part'] - 1.0:11.4f}"
    print(f"{name:22}{m['child_sud_or']:14.4f}{m['child_hl_or']:19.4f}{gap:>11}")
