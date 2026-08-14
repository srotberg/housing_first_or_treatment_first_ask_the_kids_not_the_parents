"""
The stylised two period model behind section 3 of the paper.

WHAT THIS IS FOR

The full model has too many moving parts for a reader to see which one does the
work. This strips it to the smallest environment in which the paper's claims are
still true, solves it numerically, and reports what each parameter controls. It
is not a summary of the big model. It is a separate object whose job is to say
what the channel shutdown ladder in section 7 is a test OF.

THE ENVIRONMENT

Two periods. A household has permanent income y, fixed and heterogeneous.

  period 1   receives y, chooses non drug consumption c, drug use v >= 0 and
             saving a >= 0, subject to c + p_v v + a = y
             flow utility  (1-th) log c + th [ log(b+v) - log b ]
             using raises the chance of carrying a substance use disorder into
             period 2:  pi_d(v) = 1 - exp(-lam v)

  period 2   resources W = R a + y (1 - xi d) + Delta * 1{voucher}
             survival    phi(d) = phi0 (1 - kap d)
             value alive (1-th) log W + aleph

Two penalties for carrying the disorder, kept SEPARATE on purpose:

    kap   mortality penalty   you die more
    xi    income penalty      you earn less

A voucher worth Delta arrives with probability pV. Under Housing First it
arrives whatever d is; under Treatment First only if d = 0. That is the smallest
representation of conditionality there is.

THE EXACT CONDITION EVERYTHING TURNS ON

At v -> 0, in CONSUMPTION units, the household uses if and only if

    (th/b) c/(1-th)      >      p_v  +  beta lam VSL(y)
    ---------------             ------------------------
    marginal willingness        price plus the mortality
    to pay, grows like y        cost of the marginal unit

with  VSL(y) = phi0 kap c [ log W + aleph/(1-th) ].

VSL/y rises in y through the log term, so the right hand side grows
SUPERLINEARLY in income while the left grows linearly. That is the entire
mechanism. It also says immediately that the mechanism is a RACE, won by
mortality only if lam is large enough and aleph is not so large that the
constant swamps the log term. Both are checked in search.py.
"""

import os
import numpy as np

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', '..', 'writing', 'figures'))


class P:
    th    = 0.05      # Cobb Douglas weight on drugs
    b     = 0.010     # Stone Geary subsistence; th/b is the pull of the first unit
    p_v   = 1.0       # price of drugs, the numeraire
    beta  = 0.96
    R     = 1.03
    phi0  = 0.90      # survival through period 2, clean
    kap   = 0.45      # mortality penalty, phi(1) = phi0 (1 - kap)
    xi    = 0.31      # income penalty, y -> y (1 - xi)
    lam   = 6.00      # addiction hazard per unit of use
    aleph = 2.50      # flow value of being alive
    # HOMELESSNESS, which is what the voucher actually insures.
    #
    # An earlier version had the voucher simply add resources in period 2. That
    # cannot produce moral hazard, and did not: use under Housing First was flat
    # in generosity. Moral hazard here is not about a transfer relaxing a budget
    # constraint, it is about assistance CUSHIONING THE DOWNSIDE OF THE DISORDER,
    # and the downside is homelessness. With no homelessness state there is
    # nothing for the voucher to insure, so the only force left was the value of
    # life effect and use could only fall.
    pH0   = 0.02      # P(homeless) without the disorder
    pH1   = 0.35      # P(homeless) with it, absent a voucher
    ellH  = 0.80      # flow utility cost of being homeless
    kapH  = 0.35      # mortality penalty of being homeless
    pV    = 0.27      # probability of receiving a voucher
    # Dispersion in the TASTE for drugs, th_i = th exp(sig e - sig^2/2), e ~ N(0,1).
    #
    # Some smoothing is needed. With households differing only in y they all
    # cross the extensive margin at nearly the same b, and participation jumps
    # from one to zero over a factor of two in b, which makes every comparative
    # static here degenerate. That is an artefact of having one source of
    # heterogeneity; the full model has six state variables and does not need it.
    #
    # It has to be dispersion in the TASTE and not an additive shock on the
    # choice. An additive shock sends participation to one half whenever the two
    # conditional values are close, so participation cannot fall to the 5 per
    # cent in the data no matter how large b is, and the calibration of b fails
    # at its upper bound. Taste dispersion has no such floor.
    #
    # Note this is dispersion INDEPENDENT of income. The paper's claim is that it
    # does not need taste heterogeneity CONDITIONAL on income to put use at the
    # bottom, and that claim is untouched.
    sig   = 0.55
    nq    = 25        # Gauss Hermite nodes; too few makes participation step visibly


def clone(**kw):
    q = P()
    for k, v in kw.items():
        setattr(q, k, v)
    return q


# ----------------------------------------------------------------------------
# solver, vectorised over (v, saving rate)
# ----------------------------------------------------------------------------
def _V2(par, y, a, d, policy):
    """
    Period 2 value in disorder state d.

    A voucher arrives with probability pV and, when it does, it removes the risk
    of homelessness. Under Housing First it arrives whatever d is. Under
    Treatment First it arrives only if d = 0.

    That single difference is both of the paper's forces at once:

      moral hazard   under HF, more generosity lowers P(homeless | disorder),
                     which makes acquiring the disorder LESS costly, so use rises
      deterrence     under TF, more generosity raises the value of staying clean
                     without touching the disorder branch, so use falls

    and neither exists if the voucher is modelled as a transfer rather than as
    insurance against a bad state.
    """
    inc  = par.R * a + y * (1.0 - par.xi * d)
    u    = (1.0 - par.th) * np.log(np.maximum(inc, 1e-12))
    covered = (policy == 'HF') or (d == 0)
    ph   = (par.pH1 if d == 1 else par.pH0) * (1.0 - (par.pV if covered else 0.0))
    phi  = par.phi0 * (1.0 - par.kap * d)
    v_ho = phi * (u + par.aleph)                               # housed
    v_hl = phi * (1.0 - par.kapH) * (u - par.ellH + par.aleph)  # homeless
    return (1.0 - ph) * v_ho + ph * v_hl


def _best(par, y, policy, vgrid, ns=81):
    """Best value over the saving rate, for each v on the supplied grid."""
    v   = vgrid[:, None]
    s   = np.linspace(0.0, 0.85, ns)[None, :]
    res = y - par.p_v * v
    a   = res * s
    c   = res * (1.0 - s)
    ok  = (res > 1e-9) & (c > 1e-9)
    pid = 1.0 - np.exp(-par.lam * v)
    val = (1.0 - par.th) * np.log(np.maximum(c, 1e-12)) \
        + par.th * (np.log(par.b + v) - np.log(par.b)) \
        + par.beta * ((1.0 - pid) * _V2(par, y, a, 0, policy)
                      +        pid  * _V2(par, y, a, 1, policy))
    val = np.where(ok, val, -np.inf)
    j   = np.argmax(val, axis=1)
    return val[np.arange(val.shape[0]), j]


def _quad(par):
    x, w = np.polynomial.hermite_e.hermegauss(par.nq)
    return x, w / w.sum()


def solve_one(par, y, policy='HF', nv=200):
    """
    Integrates over the taste draw. Returns (participation probability at this
    income, expected use per household at this income).
    """
    x, qw = _quad(par)
    vg = np.linspace(1e-4, 0.55 * y, nv)
    p, ev = 0.0, 0.0
    for xi_, wi in zip(x, qw):
        q = clone(**{**_fields(par),
                     'th': par.th * np.exp(par.sig * xi_ - 0.5 * par.sig**2)})
        v_no = _best(q, y, policy, np.array([0.0]))[0]
        vals = _best(q, y, policy, vg)
        k = int(np.argmax(vals))
        if np.isfinite(vals[k]) and vals[k] > v_no:
            p  += wi
            ev += wi * vg[k]
    return float(p), float(ev)


def profile(par, ygrid, policy='HF'):
    """(participation, expected use) by income."""
    out = [solve_one(par, y, policy) for y in ygrid]
    return np.array([o[0] for o in out]), np.array([o[1] for o in out])


# ----------------------------------------------------------------------------
# the moments, measured the way the DATA measure them
# ----------------------------------------------------------------------------
def moments(par, ygrid, w, policy='HF'):
    """
    r_use is the income of users relative to the average, in period 1.
    r_sud is the income of households WITH the disorder relative to the average,
    measured in period 2, so AFTER the earnings penalty has landed. That is what
    NSDUH sees. Measuring it on pre penalty income was an error in the first
    version of this script: it forced the two ratios to move together, which is
    exactly the thing the data say they do not do.
    """
    p_use, ev = profile(par, ygrid, policy)
    vbar = np.where(p_use > 1e-9, ev / np.maximum(p_use, 1e-9), 0.0)
    pid  = p_use * (1.0 - np.exp(-par.lam * vbar))
    w    = w / w.sum()

    r_use = (w * p_use * ygrid).sum() / max((w * p_use).sum(), 1e-12) \
          / (w * ygrid).sum()

    y2    = ygrid * (1.0 - par.xi)             # income once the disorder lands
    ybar2 = (w * (pid * y2 + (1.0 - pid) * ygrid)).sum()
    r_sud = (w * pid * y2).sum() / max((w * pid).sum(), 1e-12) / ybar2

    x = np.log(ygrid) - (w * np.log(ygrid)).sum()
    slope = float((w * x * (ev - (w * ev).sum())).sum() / (w * x * x).sum())
    v = vbar

    return dict(part=float((w * p_use).sum()), sud=float((w * pid).sum()),
                r_use=float(r_use), r_sud=float(r_sud), slope=slope,
                p_use=p_use, v=v, ev=ev, pid=pid)


def _fields(par):
    return {k: getattr(par, k) for k in dir(par)
            if not k.startswith('_') and not callable(getattr(par, k))}
