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


# ---------------------------------------------------------------------------
# THE CHILD'S LIFETIME UTILITY, CHILDHOOD INCLUDED
# ---------------------------------------------------------------------------

def _childhood_u(par, c, h, aleph_for_child=True):
    """The child's OWN experienced utility during childhood.

    X_K = (c/xi)^phi_c (h/xi)^phi_h (bbar)^phi_q -- the child's bundle, carrying
    the Stone-Geary shifter ALONE because the child consumes none of the drug.
    That asymmetry is the whole contemporaneous channel.

    THE WEIGHT IS (xi - 1) AND NOT omega_c (xi - 1).  omega_c is how much the
    PARENT cares; the child experiences its own childhood in full.  (xi - 1) is
    the equivalence-scale weight of a child in the household, which is the
    child's share of what the household consumes, and it is the same factor the
    parent's flow utility carries.

    ALEPH IS INCLUDED, on the author's instruction of 12 September: *"Yes for
    welfare the child's utility growing up counts"*.  A childhood is a period of
    life and is valued as one.  The switch is kept because the argument the
    other way is real and is recorded here.  aleph is added
    ONCE PER HOUSEHOLD, not per member -- the Fortran adds value_of_life to the
    assembled flow rather than inside the bracket the child weight multiplies --
    so the parent's flow already carries it for the household.  Counting it
    again for the child double counts; omitting it values a childhood at its
    goods alone.  There is no neutral answer, so it is a switch, it is off by
    default, and any number computed from it has to say which way it was set.
    """
    phc, phh, phq = _shares(par)
    s = par.sigma
    XK = ((max(c, 1e-12) / par.xi) ** phc
          * (h / par.xi) ** phh
          * par.b ** phq)
    u = XK ** (1.0 - s) / (1.0 - s)
    if aleph_for_child:
        u = u + par.aleph
    return (par.xi - 1.0) * u


def childhood_loss_within(par, policy=None, pV=None):
    """The childhood loss from the parent's drug purchase, WITHIN the household.

    THE FIRST VERSION COMPARED CHILDREN OF USERS WITH CHILDREN OF ABSTAINERS
    AND GOT THE SIGN BACKWARDS: -0.868 against -3.009, i.e. children of users
    apparently BETTER off.  That is selection, not causation.  Who uses is an
    equilibrium object -- at this calibration users are a small, particular
    slice of the distribution -- so a cross-household difference measures which
    households use, on top of what using does to them.  It is the same error as
    comparing the child gap across two branches, which cost most of a day.

    The right comparison is WITHIN the household: the same state, the same
    income, the child's bundle when the parent buys the drug against the same
    child's bundle when it does not.  period1 returns BOTH branches for every
    state -- bu is the using allocation and bn the abstaining one -- so the
    counterfactual needs no extra solve and no reweighting.

    Averaged over the states that actually use, weighted by their mass.
    """
    q = with_(par, policy=policy) if policy is not None else par
    pv = par.pV if pV is None else pV
    q = with_(q, pV=pv)
    loss = mass = 0.0
    for j, y in enumerate(C.YG):
        for p, gain, v, bu, bn, inc, _own in S.period1(q, y, q.policy):
            if p <= 1e-14 or gain <= 0.0:
                continue
            au, su, ru, _vsu, mu = bu
            an, sn, rn, _vsn, mn = bn
            c_use = inc - ru - q.p_v * v - au
            c_abs = inc - rn - an
            h_use = _hpick(q, su, mu)
            h_abs = _hpick(q, sn, mn)
            m = C.W[j] * p
            loss += m * (_childhood_u(q, c_abs, h_abs)
                         - _childhood_u(q, c_use, h_use))
            mass += m
    return (loss / mass if mass > 1e-14 else float('nan')), mass


def child_lifetime_loss(par, policy=None, pV=None):
    """The child's expected lifetime loss from a parent who acquired the
    disorder: the CHILDHOOD loss plus the ADULT loss.  This is what chdmg
    should be, and chdmg is currently zero.
    """
    import math
    q = with_(par, policy=policy) if policy is not None else par
    q = with_(q, pV=(par.pV if pV is None else pV))
    # ADULT: the child's own value1 at its inherited income, averaged over the
    # child's income distribution, with and without the delta_d shift.
    v1 = np.array([S.value1(q, y, q.policy) for y in C.YG])
    ly = np.log(C.YG)
    lb = math.log(1.0)                       # ybar, the mean, is one
    adult_clean = S._child_rate(q, ly, lb, C.W, C.YG, v1, 0.0)
    adult_dis = S._child_rate(q, ly, lb, C.W, C.YG, v1, q.delta_d)
    # CHILDHOOD: children of using parents against children of abstainers.
    kidloss, kidmass = childhood_loss_within(q, policy, pV)
    return dict(adult_clean=adult_clean, adult_dis=adult_dis,
                adult_loss=adult_clean - adult_dis,
                childhood_loss=kidloss, user_mass=kidmass,
                total_loss=(adult_clean - adult_dis) + kidloss)


# ---------------------------------------------------------------------------
# RATIONED TREATMENT FIRST: fixed supply, reallocated away from users
# ---------------------------------------------------------------------------

def voucher_coverage(par, policy=None):
    """Share of households that ACTUALLY hold a voucher in period 1.

    Not the share that draws one: under any conditional policy a household can
    draw a voucher and then lose it by using, and what the programme spends is
    on the ones that keep it.  period1's records carry the voucher saving in
    slot 3 of each branch, which is positive exactly when a voucher is held.
    """
    got = mass = 0.0
    for j, y in enumerate(C.YG):
        for p, gain, v, bu, bn, inc, _own in S.period1(par, y, par.policy):
            if p <= 1e-14:
                continue
            vs = (bu if gain > 0.0 else bn)[3]
            m = C.W[j] * p
            mass += m
            got += m * (1.0 if vs > 1e-12 else 0.0)
    return got / mass


def solve_pv_scale(par, target_cov=None, iters=24, tol=1e-6):
    """Find the reallocation factor that holds voucher SUPPLY fixed.

    The author's rationed Treatment First houses the same fraction of eligible
    households as the benchmark, while refusing anyone with the disorder or
    with v > 0.  The vouchers that refusal frees are reissued, so the clean draw
    against a larger pool -- and how many are freed depends on how many use,
    which depends on the voucher.  That is a fixed point, not a parameter.

    Solved by damped iteration on the ratio of realised coverage to target,
    which is monotone in the scale and converges in a handful of passes.  The
    scale is capped so that pV * scale cannot exceed one.
    """
    base = with_(par, policy='HF')
    cov0 = voucher_coverage(base) if target_cov is None else target_cov
    scale = 1.0
    for _ in range(iters):
        q = with_(par, policy='RTF', pv_scale=scale)
        cov = voucher_coverage(q)
        if abs(cov - cov0) < tol:
            break
        # damped, because coverage responds to the scale through behaviour too
        scale = min(scale * (1.0 + 0.6 * (cov0 / max(cov, 1e-12) - 1.0)),
                    1.0 / max(par.pV, 1e-12))
    return scale, cov0, cov


def childhood_level(par, policy=None, pV=None):
    """Expected childhood utility under a policy -- a LEVEL, not a difference.

    THIS IS WHAT THE TRANSITION NEEDS AND DOES NOT HAVE.  transition.py's
    _welfare is `expected lifetime value of a cohort born into the mixture p`,
    and that value is V1 -- the ADULT value at the income the cohort is born
    with.  A cohort's childhood is nowhere in it.

    THE TIMING IS THE WHOLE POINT, and it is what makes the author's hypothesis
    testable: *"when you remove vouchers for parents with Sud, it hurts some of
    them and their kids, but it helps other kids since their parents don't use
    and they have better life prospects... So even in transition welfare may
    rise"*.  A cohort's childhood is lived under the policy in force while its
    PARENTS were adults, and its own adulthood under the policy in force later:

        welfare(cohort t) = childhood(policy at t-1) + adult(policy at t)

    So the cohort the reform lands on pays in full -- its childhood is already
    over, under the old regime, and conditionality costs it as an adult -- while
    every cohort after it is raised by parents who used less.  That is the
    asymmetry a static comparison sums away and a transition can separate.

    Averaged over ALL children, using each household's realised allocation, so
    a parent who uses contributes its using allocation and one who abstains its
    abstaining one.  Compare with childhood_loss_within, which is the
    counterfactual difference WITHIN a household and answers a different
    question.
    """
    q = with_(par, policy=policy) if policy is not None else par
    q = with_(q, pV=(par.pV if pV is None else pV))
    tot = mass = 0.0
    for j, y in enumerate(C.YG):
        for p, gain, v, bu, bn, inc, _own in S.period1(q, y, q.policy):
            if p <= 1e-14:
                continue
            uses = gain > 0.0
            a, street, rent, _vs, small = (bu if uses else bn)
            c = inc - rent - q.p_v * (v if uses else 0.0) - a
            h = _hpick(q, street, small)
            m = C.W[j] * p
            tot += m * _childhood_u(q, c, h)
            mass += m
    return tot / mass
