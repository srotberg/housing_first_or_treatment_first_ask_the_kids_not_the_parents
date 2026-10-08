"""
THE REST POINT, EXACTLY, AND STAGE 2 CALIBRATED AT IT.

The author, 8 October, on Section 3's 'the rest point has more users than the calibrated 8.84 percent': "why are
we counting a different population?! are you claiming that the calibration ignored the full population?"

TWO THINGS WERE WRONG, AND THE SECOND WAS MOST OF IT.
  1. calibrate.stats measures every moment in one generation drawn from the base income distribution, so it
     leaves out the adults who inherited the penalty from a parent with a SUD (transition._shifts: income times
     exp(-delta_d)). At stage 2's parameters they are 3.7 per cent of adults, and counting them moves
     participation from 8.84 to about 8.89 per cent.
  2. The 9.66 per cent the paper reported for the Housing First rest point came from transition._outcome, which
     reads the disorder on the income NODES (use_prob(y) times the aggregate SUD-to-use ratio) and interpolates
     it at shifted incomes. Use is a step within a node's cell, which aggregates() integrates (threshold(): the
     share of the cell above the switch) and the node grid does not. At stage 2's parameters the node grid puts
     the base population's SUD rate at 4.02 per cent against an exact 3.65, and the penalised type's at 3.48
     against an exact 4.16 -- lower than the base, the wrong way round, because the shifted incomes run off the
     bottom of the grid. scratchpad test_rest2.py, 8 October.

WHAT THIS DOES. Each penalty type is aggregates() run exactly: the base type at the base incomes, the penalised
type at incomes, cell edges and income cdf all scaled by the penalty. The mixture is the fixed point of the
inheritance chain (transition._step: a child's income is a fresh base draw, cut by the penalty if the parent ends
with a SUD), which with two types is closed form: s = sud0 / (1 + sud0 - sud1). The two types' accumulators are
ADDED before any ratio is formed (aggregates(raw=True)), as fertility.mixed_stats does for parents and non-parents.

With par.rest = 1, calibrate.stats returns rest_stats(par), so every moment the calibration reads is the rest
point's. The omega = 0 experiment that identifies omega_c holds the mixture (par.rest_hold = 1): it switches off the
parent's concern with every other parameter held, and the population is one of them. vsl stays at income 1 and
bot50 is data.
"""
import numpy as np

_P = {'p': None}        # the last mixture of an unheld call, which a held call (the omega = 0 experiment) reuses


def _types(par):
    """The solved parameters, the penalty's income multiplier, and each type's raw accumulators at full weight."""
    import calibrate as C
    import transition as T
    from stylized import with_, aggregates, solve_child_damage
    q = solve_child_damage(with_(par, rest=0, rest_hold=0))
    sh = float(T._shifts(q)[1])
    cdf1 = (lambda y, _s=sh: C.CDF(y / _s)) if C.CDF is not None else None
    A = aggregates(q, C.YG, C.W, edges=C.EDGES, cdf=C.CDF, raw=True)
    B = aggregates(q, C.YG * sh, C.W, edges=None if C.EDGES is None else C.EDGES * sh, cdf=cdf1, raw=True)
    return q, sh, A, B


def mixture_of(A, B, wsum):
    """The rest point's [base, penalised] shares: the fixed point of s' = (1 - s) sud0 + s sud1."""
    s0, s1 = A['sud'] / wsum, B['sud'] / wsum
    s = s0 / (1.0 + s0 - s1)
    return np.array([1.0 - s, s])


def rest_stats(par, p=None):
    import calibrate as C
    from stylized import vsl, priced_out_share
    q, sh, A, B = _types(par)
    W = float(C.W.sum())
    if p is None:
        if getattr(par, 'rest_hold', 0) and _P['p'] is not None:
            p = _P['p']
        else:
            p = mixture_of(A, B, W)
            if not getattr(par, 'rest_hold', 0):
                _P['p'] = p
    t = {k: p[0] * A[k] + p[1] * B[k] for k in A if not isinstance(A[k], np.ndarray)}
    ybar = float((C.W / W * C.YG).sum()) * (p[0] + p[1] * sh)
    m = dict(part=float(t['part'] / W), sud=float(t['sud'] / W),
             dshare=float(t['spend'] / max(t['uinc'], 1e-12)),
             prog=float(t['sud'] / max(t['part'], 1e-12)),
             r_use=float(t['yuse'] / max(t['part'], 1e-12) / ybar),
             homeless=float(t['hl'] / max(t['mass'], 1e-12)),
             # period 1 alone, when the child is at home: what transition._outcome(p, hl) reported
             homeless1=float((t['hl'] - t['hl2']) / max(t['mass1'], 1e-12)),
             sud_of_homeless=float(t['hl_sud'] / max(t['hl'], 1e-12)),
             sud_of_homeless2=float(t['hl_sud'] / max(t['hl2'], 1e-12)),
             hl2=float(t['hl2']), hl_sud=float(t['hl_sud']),
             housing_share=float(t['hcost'] / max(t['hinc'], 1e-12)),
             hsmall=float(t['smallmass'] / max(t['housedmass'], 1e-12)),
             burden50=float(t['burden'] / max(t['mass1'], 1e-12)),
             networth=float(t['wealth'] * q.years / max(t['winc'], 1e-12)),
             hspend=float(t['hcost'] / max(t['hexp'], 1e-12)),
             fshare=float(t['fsp'] / max(t['lab'], 1e-12)),
             cost=float(t['cost'] / W))
    m['vsl'] = vsl(q)
    m['bot50'] = C._bottom_half_share(C.SIG)
    m['priced_out'] = float(p[0] * priced_out_share(q, C.YG, C.W) + p[1] * priced_out_share(q, C.YG * sh, C.W))
    m['rest_p'] = [float(x) for x in p]
    return m
