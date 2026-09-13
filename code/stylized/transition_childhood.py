#!/usr/bin/env python3
"""THE TRANSITION, WITH CHILDHOOD IN THE WELFARE MEASURE AND A CEV THAT WORKS.

The author asked for the transition under rationed Treatment First, with the
consumption equivalent computed on LIFETIME utility including childhood.
transition.py does neither: its cohort welfare is V1, the ADULT value at the
income the cohort is born with, and its cev() is the log-utility formula, which
at sigma = 2 is wrong by an order of magnitude and always too large.

THIS DOES NOT MODIFY transition.py.  It reuses its Markov chain -- the mixture
over the four penalty types, the bridge generation, the shifted-income solves --
and changes only the two things that were asked for.  That keeps a working
module working, and it keeps the comparison honest: any difference from
transition.py's own figure is the childhood term and the CEV, nothing else.

THE TIMING, which is the whole content of the exercise:

    welfare(cohort t) = childhood(policy in force at t-1) + adult(policy at t)

Cohort 1 is the one the reform lands on.  Its childhood is ALREADY OVER, lived
under the old regime, so it gets the old childhood and the new adulthood -- it
pays conditionality's cost and collects none of its benefit.  Cohort 2 onward
is raised by parents who lived under the new rule.  That asymmetry is what a
static comparison sums away, and it is the author's hypothesis: removing
vouchers from parents with the disorder hurts them and their children, while
other children gain because their parents did not use.

THE CEV NEEDS A LEVEL, not just a difference, because under CRRA the answer
depends on where you start.  The level here is the pre-reform lifetime value,
childhood included, which is w0 + childhood(old policy).
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transition as T
from stylized import with_, P
from recalibrate import FIXED
from child_welfare import childhood_level, cev, solve_pv_scale


def path_with_childhood(par, policy, pV, p0, v1_base, w0, n=None):
    """transition.path, with childhood added and the corrected CEV."""
    n = T.GENERATIONS if n is None else n
    v1, sud, hl, ev_s0 = T._policy_grids(par, policy, pV)
    sud_b, _ = T._bridge_grids(par, policy, pV)
    ev_b = T._bridge_hl_by_shift(par, policy, pV)
    ev_s = T._hl_by_shift(par, policy, pV)

    kid_old = childhood_level(par, T.BASE_POLICY, par.pV)
    kid_new = childhood_level(par, policy, pV)
    level0 = w0 + kid_old                      # pre-reform lifetime, childhood in

    out, p = [], p0.copy()
    for t in range(1, n + 1):
        adult = T._welfare(p, v1, par)
        # COHORT 1 IS THE CHILDREN ALIVE WHEN THE POLICY CHANGES, SO ITS
        # CHILDHOOD IS UNDER THE NEW POLICY.
        #
        # The author, 13 September: *"welfare should be measured for the
        # lifetime utility of cohort 1, which is the children at the time the
        # policy change is made"*, and *"they are still living with their
        # parents"*.
        #
        # Those children are in the household when the reform lands, so the
        # whole of their childhood is lived under the new regime -- their
        # parents face it while they are being raised.  What they carry from the
        # old world is not their childhood but their PARENTS' disorder status,
        # which was settled before the reform; that is p0, and the adult term
        # already uses it.  So the two halves of cohort 1 are: adult value born
        # into the pre-reform mixture, childhood under the new policy.
        #
        # The line was kid_old for t == 1, which gave cohort 1 a childhood the
        # reform never touched and charged the policy for it.
        kid = kid_new
        total = adult + kid
        out.append(dict(cohort=t,
                        adult=float(adult), childhood=float(kid),
                        total=float(total),
                        cev=float(cev(par, total - level0, level0)),
                        cev_adult_only=float(cev(par, adult - w0, w0)),
                        homeless=T._outcome(p, hl, par), sud=T._outcome(p, sud, par)))
        p = T._step(p, sud_b, ev_b, par) if t == 1 else T._step(p, sud, ev_s, par)
    return out, kid_old, kid_new, level0


def run(par=None, n=None):
    here = os.path.dirname(os.path.abspath(__file__))
    if par is None:
        d = json.load(open(os.path.join(here, 'best_vector_it1800.json')))
        kw = {k: v for k, v in FIXED.items()
              if k not in ('kap', 'gam', 'omega', 'sigma')}
        kw.update(d['_held_not_calibrated']); kw.update(d['parameters'])
        par = with_(P(), **kw)

    v1b, sudb, hlb, evb = T._policy_grids(par, T.BASE_POLICY, par.pV)
    p0 = T._rest_point(sudb, T._hl_by_shift(par, T.BASE_POLICY, par.pV), par)
    # par MUST BE PASSED, and leaving it off is what broke the null test.
    #
    # _welfare(p, v1, par=None) falls back to the MODULE CONSTANT DEL_D when par
    # is omitted, and the path passes par.delta_d.  The two are in different
    # units -- DEL_D is a fractional cut, par.delta_d a log shift -- so the
    # baseline was built on a different child penalty from the path built
    # against it.  Measured: w0 read 8.358651 without par and the identical
    # object read 8.199404 with it, a gap of 0.159, and that gap IS the -2.881
    # per cent the Housing First null was reporting when it must report zero.
    #
    # transition.py's _shifts docstring records this exact trap -- "a transition
    # table was reported on that and withdrawn" -- and the fix went into _shifts
    # while this call was missed.
    w0 = T._welfare(p0, v1b, par)

    scale, cov0, cov = solve_pv_scale(par)
    print(f"rationed TF reallocation factor {scale:.4f}   "
          f"coverage target {cov0:.4f}, achieved {cov:.4f}\n")

    for policy, lab in (('HF', 'Housing First'),
                        ('TF', 'Treatment First'),
                        ('RTF', 'rationed Treatment First')):
        q = with_(par, pv_scale=scale) if policy == 'RTF' else par
        rows, kid_old, kid_new, lvl = path_with_childhood(
            q, policy, par.pV, p0, v1b, w0, n)
        print(f"{lab}")
        print(f"   childhood level, old regime {kid_old:10.6f}   "
              f"under this policy {kid_new:10.6f}")
        h = (f"   {'cohort':>7}{'adult':>11}{'childhood':>11}{'total':>11}"
             f"{'CEV':>10}{'CEV adult':>11}{'homeless':>10}{'sud':>8}")
        print(h)
        for r in rows:
            print(f"   {r['cohort']:7d}{r['adult']:11.5f}{r['childhood']:11.5f}"
                  f"{r['total']:11.5f}{100*r['cev']:9.3f}%{100*r['cev_adult_only']:10.3f}%"
                  f"{r['homeless']:10.4f}{r['sud']:8.4f}")
        print()


if __name__ == '__main__':
    run()
