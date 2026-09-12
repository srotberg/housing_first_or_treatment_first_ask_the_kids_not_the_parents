#!/usr/bin/env python3
"""FIGURE 1'S CONSTRUCTION, WITH THE CHILD CHANNEL ADDED.

The author, 12 September: *"I want the same figure you show in paper... Where
you change the penalty and readjust b to match the use rate"*, for *"the
employment penalty for Sud, for the death, and for omegac"*.

THE CONSTRUCTION IS run.fig_who_uses's, and the whole point of it is the refit.
Scaling a channel changes how attractive the drug is, so the amount of use
moves with it, and then users' income is being compared across populations of
different sizes.  Recalibrating b at every point holds participation at its
target all along every curve, so the only thing moving is WHO uses rather than
HOW MANY.  That is what makes the curves comparable with one another and with
the data.

WHAT IS NEW HERE is the third curve.  run.py's _off turns off mortality and the
resource channel, and its two curves therefore both run with omega_c live at
its calibrated value.  To put the child channel on the same axes it has to be
in the common baseline too, so _off here also sets omega_c to zero: at s = 0
every channel is off, and at s = 1 the channel being scanned is at its
calibrated value with the other two still off.  That makes the three curves
comparable with each other, and it means the two mortality and unemployment
curves here are NOT the ones in the paper -- they are drawn against a different
baseline.  Anything read off this figure has to say which.

h_hl TRAVELS WITH UNEMPLOYMENT, as run.py records: the street's housing
services are a resource consequence, and an earlier version that put h_hl in the
mortality group quietly placed an unemployment consequence inside the mortality
curve.
"""
import json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter, NullLocator, FixedLocator
sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code/stylized')
from stylized import with_, P
from calibrate import bracket, stats, TARGET
from recalibrate import FIXED

SCAN_HI = 1.25
NPTS = 9

d = json.load(open('best_vector_it1800.json'))
kw = {k: v for k, v in FIXED.items() if k not in ('kap', 'gam', 'omega', 'sigma')}
kw.update(d['_held_not_calibrated']); kw.update(d['parameters'])
base = with_(P(), **kw)


def _off(b):
    """Every channel off: no excess mortality, no employment penalty, the
    street no worse than the small unit, and no weight on the child."""
    return dict(kap=0.0, u1=b.u0, h_hl=b.h_sm, omega=0.0)


def _scaled(b, which, s):
    kw = _off(b)
    if which == 'mortality':
        kw.update(kap=s * b.kap)
    elif which == 'unemployment':
        kw.update(u1=b.u0 + s * (b.u1 - b.u0),
                  h_hl=b.h_sm * (b.h_hl / b.h_sm) ** s)
    else:
        kw.update(omega=s * b.omega)
    par = with_(b, **kw)
    # b RECALIBRATED AT EVERY POINT.  The ceiling is 20 rather than 0.6: with
    # the consequences off the drug is a pure luxury, so holding participation
    # down to target needs a very large Stone-Geary endowment, and a low ceiling
    # returns the ceiling and silently leaves participation far above target.
    q = with_(par, b=bracket(par, 'b', 'part', 1e-5, 20.0, iters=30))
    got = stats(q)['part']
    miss = abs(got - TARGET['part']) > 5e-4
    if miss:
        print(f"   NOTE: {which} at {s:.2f}: participation {100*got:.2f} per cent, "
              f"not {100*TARGET['part']:.2f}; no b delivers the target here")
    return q, got, miss


sc = np.linspace(0.0, SCAN_HI, NPTS)
fig, ax = plt.subplots(figsize=(7.4, 4.6))
rows = {}
for which, col, ls, mk, lab in (
        ('mortality',    '#2C6FAD', '-',  'o', 'excess mortality of users'),
        ('unemployment', '#D9822B', '--', 's', 'employment penalty with SUD'),
        ('child',        '#3F8F5B', '-.', '^', r'weight on the child, $\omega_c$')):
    r, bs, miss = [], [], []
    for s in sc:
        q, got, mi = _scaled(base, which, s)
        m = stats(q)
        r.append(m['r_use']); bs.append(q.b); miss.append(mi)
    rows[which] = (list(sc), r, bs, miss)
    ax.plot(100 * np.array(sc), r, ls, color=col, marker=mk, ms=4.5, label=lab)

ax.axhline(1.0, color='0.3', lw=1.1)
ax.axhline(TARGET['r_use'], color='#27ae60', lw=1.1, ls='-.')
ax.annotate('data, 0.74', xy=(2, TARGET['r_use']), va='bottom', fontsize=8,
            color='#27ae60')
ax.set_yscale('log')
ax.yaxis.set_minor_locator(NullLocator())
ax.yaxis.set_minor_formatter(NullFormatter())
ax.yaxis.set_major_locator(FixedLocator([0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0]))
ax.set_yticklabels(['0.1', '0.2', '0.5', '1.0', '2.0', '3.0', '5.0'])
ax.set_ylim(0.10, 5.6)
ax.grid(axis='y', which='major', color='0.88', lw=0.7, zorder=0)
ax.set_axisbelow(True)
ax.set_xlim(-3, 128)
ax.set_xticks([0, 25, 50, 75, 100, 125])
ax.axvline(100, color='black', lw=0.9, ls=':')
ax.annotate('calibrated', xy=(100, 0.115), ha='center', va='bottom', fontsize=8)
ax.set_xlabel('Strength of the channel, per cent of its calibrated value')
ax.set_ylabel('Mean income of users / population mean')
ax.legend(fontsize=8.5, loc='upper left', framealpha=0.93)
fig.tight_layout()
fig.savefig('fig_three_channels.png', dpi=160)
print("\nwrote fig_three_channels.png\n")

print(f"{'strength':>9}" + ''.join(f"{w[:11]:>24}" for w in rows))
print(f"{'':9}" + ''.join(f"{'r_use':>12}{'b':>12}" for _ in rows))
for i, s in enumerate(sc):
    line = f"{100*s:8.0f}%"
    for w in rows:
        _, r, bs, miss = rows[w]
        line += f"{r[i]:12.3f}{bs[i]:12.4f}" + ('*' if miss[i] else ' ')
    print(line)
print("\n* participation missed its target at that point; see the NOTE lines above.")
