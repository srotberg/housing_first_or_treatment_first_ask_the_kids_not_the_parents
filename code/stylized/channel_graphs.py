#!/usr/bin/env python3
"""THE THREE CHANNELS, SWEPT RATHER THAN SWITCHED.

The author, 12 September: *"I want to see the graph for the employment penalty
for Sud, for the death, and for omegac"*.

The ablation table switches each channel OFF and reports one number.  That
hides the shape: whether the gradient responds smoothly over the whole range or
only near one end, and where the calibrated value sits on that curve.  Each
panel here sweeps ONE channel with every other parameter held at the
iteration-1800 calibration.

CORNER POINTS ARE MARKED AND NOT JOINED.  Beyond some settings the model leaves
the interior branch: the drug share collapses to the grid floor, every "user"
sits on the smallest positive quantity available, and r_use flatlines near 0.145
whatever the parameter does.  Measured: dshare / v_lo = 1.000 across three
orders of magnitude of the floor, so that value is a property of the grid, not
of the model.  Joining those points to the interior curve would draw a line
through two different economies -- the same mistake that produced a child gap
of 1.4984 against a target of 0.1834 this morning.
"""
import json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code/stylized')
from stylized import with_, P
from recalibrate import FIXED
import calibrate as C

CORNER = 0.02
d = json.load(open('best_vector_it1800.json'))
kw = {k: v for k, v in FIXED.items() if k not in ('kap', 'gam', 'omega', 'sigma')}
kw.update(d['_held_not_calibrated']); kw.update(d['parameters'])
base = with_(P(), **kw)
phi0 = base.phi0

def smr_to_kap(s): return 1.0 - phi0 ** (s - 1.0)
def kap_to_smr(k): return 1.0 + np.log(1.0 - k) / np.log(phi0)

# RANGES CONFINED TO THE INTERIOR WINDOW PLUS A LITTLE BEYOND.
# The first version of this figure swept each channel over what looked like a
# generous range and produced two panels with no curve in them at all: beyond a
# narrow window every point is a corner, so there was nothing to join.  Measured
# at this vector, the interior branch ends at about SMR 2.3, u1 0.053 and
# omega_c 0.023 -- and the calibrated values are 2.32, 0.0537 and 0.0233.  The
# calibration sits ON THE EDGE of the interior branch in all three channels,
# which is the single most important thing these panels show, and a range wide
# enough to hide the curve is a range that hides it.
PANELS = [
    ("Excess mortality of users",
     "standardised mortality ratio",
     np.linspace(1.0, 2.5, 16), lambda v: {'kap': smr_to_kap(v)},
     kap_to_smr(base.kap), 1.0),
    ("Employment penalty with the disorder",
     "job-loss rate with SUD  (clean rate = %.3f)" % base.u0,
     np.linspace(base.u0, 0.057, 16), lambda v: {'u1': v},
     base.u1, base.u0),
    ("Weight on the child",
     r"$\omega_c$",
     np.linspace(0.0, 0.028, 16), lambda v: {'omega': v},
     base.omega, 0.0),
]

fig, ax = plt.subplots(2, 3, figsize=(13.5, 7.2), sharey='row')
for j, (title, xlab, grid, mk, cal, off) in enumerate(PANELS):
    xs, ru, pt, corner = [], [], [], []
    for v in grid:
        m = C.stats(with_(base, **mk(v)))
        xs.append(v); ru.append(m['r_use']); pt.append(m['part'])
        corner.append(m['dshare'] <= CORNER)
    xs = np.array(xs); ru = np.array(ru); pt = np.array(pt)
    good = ~np.array(corner); bad = np.array(corner)

    for i, (y, lab) in enumerate(((ru, "users' income / mean"),
                                  (pt, "share of households using"))):
        a = ax[i][j]
        a.plot(xs[good], y[good], '-', lw=2.2, color='#1f4e79', zorder=3)
        if bad.any():
            a.plot(xs[bad], y[bad], 'x', ms=6, color='#b0b0b0', zorder=2)
        a.axvline(cal, color='#c0392b', lw=1.2, ls='--', zorder=1)
        a.axvline(off, color='#7f8c8d', lw=1.0, ls=':', zorder=1)
        if i == 0:
            a.axhline(0.74, color='#27ae60', lw=1.2, ls='-.', zorder=1)
            a.set_title(title, fontsize=10.5, pad=8)
        else:
            a.axhline(0.089, color='#27ae60', lw=1.2, ls='-.', zorder=1)
            a.set_xlabel(xlab, fontsize=9.5)
        if j == 0:
            a.set_ylabel(lab, fontsize=9.5)
        a.grid(alpha=0.25, lw=0.6)
        a.tick_params(labelsize=8.5)

ax[0][0].plot([], [], '-', color='#1f4e79', lw=2.2, label='interior branch')
ax[0][0].plot([], [], 'x', color='#b0b0b0', ms=6, label='corner (drug share = grid floor)')
ax[0][0].plot([], [], '--', color='#c0392b', lw=1.2, label='calibrated value')
ax[0][0].plot([], [], ':', color='#7f8c8d', lw=1.0, label='channel off')
ax[0][0].plot([], [], '-.', color='#27ae60', lw=1.2, label='data')
ax[0][0].legend(fontsize=7.6, loc='upper right', framealpha=0.92)

fig.suptitle("What each channel does to the income gradient — "
             "one channel swept, all other parameters at the iteration-1800 calibration",
             fontsize=11.5, y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig('channel_graphs.png', dpi=150)
print("wrote channel_graphs.png")
