"""A lower floor and partial insurance under a SUD: can users' income, u1 above u0 and no
negative value of life at the drug decision all hold together?

Why (29 September, stage 1 on the floor of 0.235 with no insurance under a SUD): after
2,550 iterations users' income sat at 0.41 against 0.74, and u1 had drifted to its floor,
0.0486 against u0 0.0485.  Two causes, one each:
  - holding the bottom half at 17.2 per cent of earnings with the floor at 0.235 needs
    sigma_y 1.71, so median income is half the mean (0.61 at the old floor, about 0.65 in
    the data), and users around the median look poor against the mean;
  - with NO insurance, the SUD share of the homeless is already about 21.7 per cent at
    u1 = u0, so nothing asks u1 to rise.
The author: "yes, run the scan".  This takes a floor (TRUNC_FLOOR) and the fraction of the
replacement a household with a SUD keeps (ui_sud), refits everything as the u1 scan does
with u1 FITTED on the rising branch of the SUD share (bottom_bound.fit_u1), and reports:
the targets, where users sit, the median over the mean, the SUD share around the fitted
u1, the period-1 value of life at the drug decision, the aleph and VSL that would clear
it with the rest held, and the Figure 1 gradient check.  theta is held.  Log only.

usage:  STYLIZED_WORKERS=<n> python3 scan_bottom_ui.py <TRUNC_FLOOR> <ui_sud | excess> [keepsig]
"""
import sys
import numpy as np
import calibrate as C
import stylized as ST
import stage_results as R
from stylized import with_
from calibrate import stats, bracket, TARGET
import scan_u1_uninsured as SC
from negative_value_of_life import period1_negative_values

tf = float(sys.argv[1])
# ui: a number is ui_sud, the fraction of the replacement a household with a SUD keeps;
# 'excess' is stylized.P.ui_sud_excess, no insurance for the job loss the disorder causes
# and the usual insurance for the rest (the author: "half is just random").
EXCESS = sys.argv[2] == 'excess'
ui = 1.0 if EXCESS else float(sys.argv[2])


def fit_u1(q, iters=10):
    """bottom_bound.fit_u1: u1 on the SUD share of the homeless, on the rising branch."""
    def share(v):
        return stats(SC.with_b(with_(q, u1=v)))['sud_of_homeless2']
    tgt = TARGET['sud_of_homeless2']
    grid = sorted({max(g, q.u0 + 1e-3) for g in (q.u0 + 1e-3, 0.06, 0.08, 0.10, 0.13, 0.16, 0.20)})
    sh = [share(g) for g in grid]
    k = int(np.argmax(sh))
    print('     u1 curve: ' + '  '.join(f'{g:.3f}:{100*v:.1f}' for g, v in zip(grid, sh)) +
          f'  (target {100*tgt:.1f}; peak at u1 {grid[k]:.3f})', flush=True)
    if sh[0] >= tgt:
        print(f'     share already at or above target at u1 = u0 + 0.001; u1 kept at {grid[0]:.4f}', flush=True)
        return SC.with_b(with_(q, u1=grid[0]))
    if sh[k] < tgt:
        print(f'     TARGET ABOVE THE PEAK; u1 kept at the peak {grid[k]:.4f}', flush=True)
        return SC.with_b(with_(q, u1=grid[k]))
    j = next(i for i in range(1, k + 1) if sh[i] >= tgt)
    lo, hi = grid[j - 1], grid[j]
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if share(mid) >= tgt:
            hi = mid
        else:
            lo = mid
    return SC.with_b(with_(q, u1=0.5 * (lo + hi)))


# KEEPSIG (optional third argument): raise the floor but HOLD sigma_y at its value on the
# original floor (17.2 per cent there), rather than refitting it to keep the bottom half at
# 17.2.  Refitting stretched the top -- median over mean 0.50 at the 0.235 floor -- and
# users' income then jumped between about 0.45 and 0.95 with kappa, never 0.74.  Held,
# the median stays at 0.62-0.65 of the mean and the bottom half's share rises instead:
# 18.2 / 19.1 / 21.1 per cent at floors 0.15 / 0.18 / 0.24.  The author: "What is your
# solution".
KEEPSIG = len(sys.argv) > 3 and sys.argv[3] == 'keepsig'
if KEEPSIG:
    C.TRUNC_FLOOR = 1.08
    SIG_HELD = C._solve_sig()
    C.TRUNC_FLOOR = tf
    C.SIG = SIG_HELD
    C.YG, _W0 = C._grid(C.SIG)
    C.EDGES = np.concatenate(([0.0], np.cumsum(_W0)))
    C.W = _W0 * len(_W0)
    C.Q_F = C._ndtr((np.log(C._trunc_level(C.SIG, tf * ST.P().pr * ST.P().h2)) + 0.5 * C.SIG ** 2) / C.SIG)
    C.GRID_MEAN = (1.0 - C._tail_mean(C.SIG, C.Q_F)) / max(1.0 - C.Q_F, 1e-14)
    yV = 0.5 * C._median_of(C.YG, _W0)
else:
    yV = SC.set_grid(tf)
par0, _ = R.load(1)
q = with_(par0, **{**SC.SPEC, 'ui_sud': ui, 'cbar': 0.09}, ui_sud_excess=int(EXCESS), u1=0.07, yV=yV, h1=0.03)
med = C._median_of(C.YG, np.diff(C.EDGES))
mean = float(np.sum(np.asarray(C.W) * np.asarray(C.YG)) / np.sum(C.W))
_o = np.argsort(C.YG); _y = np.asarray(C.YG)[_o]; _w = np.asarray(C.W)[_o] / np.sum(C.W); _cw = np.cumsum(_w)
_k = int(np.searchsorted(_cw, 0.5))
_bh = float(((_w * _y)[:_k].sum() + (0.5 - (_cw[_k - 1] if _k else 0.0)) * _y[_k]) / mean)
print(f'floor TRUNC_FLOOR {tf}: lowest income {C.YG[0]:.3f}, sigma_y {C.SIG:.4f}, median {med:.3f}, '
      f'mean {mean:.3f}, median / mean {med / mean:.3f}, bottom-half share {100*_bh:.1f}% ({"sigma HELD" if KEEPSIG else "sigma refitted to 17.2"}); ' + ('uninsured SUD-caused job loss (ui_sud_excess)' if EXCESS else f'ui_sud {ui}') + f'; VSL target {TARGET["vsl"]}', flush=True)
for r in range(3):
    q = SC.fit(q, rounds=1)
    q = SC.unemployment_u0(fit_u1(q))
    m = stats(q)
    print(f'   after u1, round {r}: u1 {q.u1:.4f} u0 {q.u0:.4f} SUD share of homeless {100*m["sud_of_homeless2"]:.2f} '
          f'homeless {100*m["homeless"]:.3f} part {100*m["part"]:.2f} r_use {m["r_use"]:.3f}', flush=True)
SC.report(q)
q = ST.solve_child_damage(q)
ref = stats(q)['part']
row = []
for du in (-0.005, 0.0, 0.005, 0.01):
    u = max(q.u1 + du, q.u0 + 1e-4)
    g = with_(q, u1=u)
    g = with_(g, b=bracket(g, 'b', 'part', 1e-5, 1.0, iters=20, tgt=ref))
    row.append((u, stats(g)['sud_of_homeless2']))
print('  SUD share around the fitted u1 (b refit): ' + '  '.join(f'u1 {u:.4f}: {100*s:.2f}' for u, s in row),
      flush=True)
print(f'  u1 above u0 by {q.u1 - q.u0:+.4f}; raising u1 {"RAISES" if row[2][1] > row[1][1] > row[0][1] else "does NOT raise"} '
      f'the SUD share of the homeless here', flush=True)
# the aleph (and VSL) that clears the period-1 value of life, the rest held
neg0 = period1_negative_values(q, 'HF')['cells']
if neg0 == 0:
    print('  value of life at the drug decision already clear at the fitted aleph', flush=True)
else:
    lo, hi = q.aleph, q.aleph + 12.0
    if period1_negative_values(ST.solve_child_damage(with_(q, aleph=hi)), 'HF')['cells'] > 0:
        print(f'  aleph + 12 does not clear it', flush=True)
    else:
        for _ in range(8):
            mid = 0.5 * (lo + hi)
            if period1_negative_values(ST.solve_child_damage(with_(q, aleph=mid)), 'HF')['cells'] > 0:
                lo = mid
            else:
                hi = mid
        print(f'  CLEARING aleph {hi:.3f} (fitted {q.aleph:.3f}) gives a VSL of '
              f'{stats(with_(q, aleph=hi))["vsl"]:.1f} with the rest held', flush=True)
SC.gradient_check(q)
