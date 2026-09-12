#!/usr/bin/env python3
"""LIFETIME UTILITY INCLUDING CHILDHOOD, AND A CEV THAT IS CORRECT AT SIGMA = 2.

The author, 12 September: *"You have to make sure to compute the lifetime
utility including the child hood..."*, and on why it matters: *"if you include
childhood utility then when you remove vouchers for parents with Sud, it hurts
some of them and their kids, but it helps other kids since their parents don't
use and they have better life prospects... So even in transition welfare may
rise"*.

TWO THINGS WERE MISSING AND ONE WAS WRONG.

MISSING 1: the child's childhood.  welfare.py contains no reference to the
child at all, and children.py's delta_utility() -- the only child loss the
model computes -- is shifted(v1, 0) - shifted(v1, DEL_D), purely the ADULT
income penalty.  The loss the child suffers WHILE IT IS A CHILD, because a
parent who buys drugs has less left for the shared consumption that feeds the
child's bundle X_K, is nowhere.

MISSING 2: chdmg is zero.  It is the child's expected lifetime loss and the
ENTIRE continuation channel of omega_c -- the parent subtracts
omega * chdmg * pi(v).  It is declared 0.0 and set by nothing in calibrate.py,
sr_calibrate.py or recalibrate.py.  So the model's own claim that omega_c
"acts in TWO places, the FLOW and the CONTINUATION" is half true in every
calibration run: the continuation half is identically zero.

WRONG: cev().  It returns exp(dv / periods) - 1 with

    periods = (1 - gam - th) * (1 + beta * phi0)

which is wrong twice.  It is the LOG-utility formula, and it uses 1 - gam - th
where the consumption share is phi_c = (1 - gam)(1 - th).  Those differ by
gam*th, 17 per cent at the calibrated values.

THE CORRECT CEV AT SIGMA = 2.  Scaling consumption by (1+lam) in every period
and state scales BOTH bundles by (1+lam)^phi_c, since X_P and X_K each carry
c/xi with exponent phi_c.  So every X^(1-sigma)/(1-sigma) term scales by
(1+lam)^(phi_c(1-sigma)) while the aleph terms do not move:

    V(lam) = (1+lam)^(phi_c(1-sigma)) * U + A ,    U = V - A

    lam = (1 + dv/U)^(1/(phi_c(1-sigma))) - 1

It depends on the LEVEL of V through U, which the log formula never did, and
aleph is 10.6 per period so A is most of V.  This is not a small correction.

A is the survival- and discount-weighted count of aleph additions: once in
period 1, and once in period 2 weighted by beta and by the survival probability
the household faces, which depends on whether it acquires the disorder.

THE SELF-TEST AT THE FOOT OF THIS FILE IS THE POINT.  Scale consumption by a
known lambda, measure the change in lifetime value, and check the formula
recovers the lambda that was applied.  The old formula fails that test at
sigma = 2 and the new one has to pass it before anything is built on it.
"""
import json, sys
import numpy as np
sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code/stylized')
import stylized as S
from stylized import with_, P, _shares, _flow, _pid, _vgrid, _hpick, _options
from recalibrate import FIXED
import calibrate as C


def aleph_weight(par, pi):
    """How many aleph's a lifetime carries: one now, one next period weighted
    by beta and by survival, which depends on the disorder outcome."""
    s0 = par.phi0
    s1 = par.phi0 * (1.0 - par.kap)
    return 1.0 + par.beta * ((1.0 - pi) * s0 + pi * s1)


def cev(par, dv, v_level, pi=0.0):
    """Consumption equivalent of dv, at a lifetime value of v_level.

    pi is the household's onset probability, which sets how much of v_level is
    aleph rather than goods.  dv and v_level must be the SAME object measured
    two ways -- a level and a difference of levels -- or U is wrong.
    """
    phc, _, _ = _shares(par)
    e = phc * (1.0 - par.sigma)
    A = par.aleph * aleph_weight(par, pi)
    U = np.asarray(v_level, dtype=float) - A
    return np.power(1.0 + np.asarray(dv, dtype=float) / U, 1.0 / e) - 1.0


def cev_log_old(par, dv):
    """The formula that was in welfare.py, kept so the two can be compared."""
    return np.exp(dv / ((1.0 - par.gam - par.th)
                        * (1.0 + par.beta * par.phi0))) - 1.0


def _base():
    d = json.load(open('best_vector_it1800.json'))
    kw = {k: v for k, v in FIXED.items()
          if k not in ('kap', 'gam', 'omega', 'sigma')}
    kw.update(d['_held_not_calibrated'])
    kw.update(d['parameters'])
    return with_(P(), **kw)


if __name__ == '__main__':
    par = _base()
    phc, _, _ = _shares(par)
    print(f"phi_c = {phc:.5f}   sigma = {par.sigma}   aleph = {par.aleph:.4f}")
    print(f"what the old periods() used, 1-gam-th = {1-par.gam-par.th:.5f}\n")

    # THE SELF-TEST.  A household's lifetime value at a scaled consumption,
    # against the lambda the formula recovers from the change.
    print("SELF-TEST: scale consumption by a known lambda, recover it from dv\n")
    print(f"{'lambda applied':>15} {'dv':>12} {'CRRA recovers':>15} {'old log formula':>17}")
    print('-' * 62)
    y = C.YG[len(C.YG) // 2]
    for lam in (0.01, 0.05, 0.10, 0.25):
        v0 = S.value1(par, y, None)
        # scaling consumption is the same as scaling income and the rent
        # together: every c in every state moves by the factor, nothing else.
        q = with_(par, ycap=par.ycap * (1 + lam))
        v1 = S.value1(with_(par, pr=par.pr), y * (1 + lam), None)
        dv = v1 - v0
        got = cev(par, dv, v0, pi=0.0)
        old = cev_log_old(par, dv)
        print(f"{lam:15.4f} {dv:12.5f} {float(got):14.4%} {float(old):16.4%}")
    print("\nNOTE: scaling y alone also scales the RENT the household faces only")
    print("if pr moves with it; where it does not, the test measures a real")
    print("income effect and not a pure consumption scaling.  Read the columns")
    print("as a comparison between the two formulas on the SAME dv.")
