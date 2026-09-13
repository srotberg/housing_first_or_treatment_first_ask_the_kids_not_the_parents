#!/usr/bin/env python3
"""TREATMENT FIRST: THE LONG RUN AND THE TRANSITION, SPLIT INTO CHILD AND ADULT.

The author, 13 September: *"show me the TF long run by child, adult, and
transition too"*, and before it *"can you show me the homelessness rate of TF?
and the impact on the children, and adult"*.

THREE HOMELESSNESS NUMBERS EXIST AND THEY ARE NOT THE SAME OBJECT.  Reporting
one of them as "the" rate is how a 7 per cent rise reads as 50:

  - the STEADY-STATE period-1 rate, which is what the model is calibrated to
    and what Table 1 reports;
  - the COHORT-PATH rate, the chance a cohort born into the transition mixture
    is ever unhoused, which is the object the child's penalty keys on;
  - CHILDHOOD STREET EXPOSURE, the share of children whose household is on the
    street while they are being raised, which is what enters childhood utility.

All three are printed, side by side, under both policies.

Nothing here writes to the paper.  It is a measurement.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transition as T
import transition_childhood as TC
import calibrate as C
from calibrate import stats
import stylized as S
from stylized import with_, P, _hpick
from child_welfare import (childhood_level, cev, solve_pv_scale,
                           voucher_coverage, _childhood_u)

HERE = os.path.dirname(os.path.abspath(__file__))


def calibrated(fn='calibrated_sep13.json'):
    from recalibrate import FIXED, START
    kw = {k: v for k, v in FIXED.items() if k != 'kap'}
    kw.update(START)
    d = json.load(open(os.path.join(HERE, fn)))
    kw.update({k: v for k, v in d.items() if not k.startswith('_')})
    return with_(P(), **kw), d


def childhood_detail(par, policy=None, pV=None):
    """The childhood level, and WHAT IS BEHIND IT: the child's own consumption
    and housing, and the share of children raised on the street."""
    q = with_(par, policy=policy) if policy is not None else par
    q = with_(q, pV=(par.pV if pV is None else pV))
    tot = mass = street_m = c_m = h_m = use_m = 0.0
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
            street_m += m * (1.0 if street > 0.5 else 0.0)
            c_m += m * c
            h_m += m * h
            use_m += m * (1.0 if uses else 0.0)
            mass += m
    return dict(level=tot / mass, street=street_m / mass, c=c_m / mass,
                h=h_m / mass, parent_uses=use_m / mass)


def main():
    par, meta = calibrated()
    print(f"the calibrated stylized model, {meta['_source'].splitlines()[0]}\n")

    scale, cov0, cov = solve_pv_scale(par)

    # ---- the pre-reform world, and the adult value it is scored against ----
    v1b, sudb, hlb, evb = T._policy_grids(par, T.BASE_POLICY, par.pV)
    p0 = T._rest_point(sudb, T._hl_by_shift(par, T.BASE_POLICY, par.pV), par)
    w0 = T._welfare(p0, v1b, par)

    rows = []
    for policy, lab in (('HF', 'Housing First (benchmark)'),
                        ('TF', 'Treatment First'),
                        ('RTF', 'rationed Treatment First')):
        q = with_(par, pv_scale=scale) if policy == 'RTF' else par
        st = stats(with_(q, policy=policy))
        kid = childhood_detail(q, policy, par.pV)
        v1, sud, hl, _ev = T._policy_grids(q, policy, par.pV)
        pss = T._rest_point(sud, T._hl_by_shift(q, policy, par.pV), q)
        adult = T._welfare(pss, v1, q)
        rows.append(dict(lab=lab, policy=policy, st=st, kid=kid,
                         adult=float(adult), pss=pss,
                         cohort_hl=T._outcome(pss, hl, q),
                         cohort_sud=T._outcome(pss, sud, q),
                         cov=voucher_coverage(with_(q, policy=policy))))

    base = rows[0]
    lvl0 = w0 + base['kid']['level']

    print("THE LONG RUN, steady state under each policy")
    print(f"   {'policy':>26}{'use':>9}{'SUD':>9}{'homeless':>10}"
          f"{'coverage':>10}{'child street':>14}")
    for r in rows:
        s = r['st']
        print(f"   {r['lab']:>26}{s['part']:9.4f}{s['sud']:9.4f}"
              f"{s['homeless']:10.4f}{r['cov']:10.4f}{r['kid']['street']:14.5f}")

    print("\n   WELFARE, split.  childhood is the child's own experienced")
    print("   utility while it is raised; adult is its lifetime value from the")
    print("   mixture its parents leave it.  CEV is on the sum.")
    print(f"   {'policy':>26}{'childhood':>11}{'adult':>11}{'total':>11}"
          f"{'CEV':>10}{'CEV child':>11}{'CEV adult':>11}")
    for r in rows:
        tot = r['adult'] + r['kid']['level']
        print(f"   {r['lab']:>26}{r['kid']['level']:11.5f}{r['adult']:11.5f}"
              f"{tot:11.5f}"
              f"{100*cev(par, tot - lvl0, lvl0):9.3f}%"
              f"{100*cev(par, r['kid']['level'] - base['kid']['level'], lvl0):10.3f}%"
              f"{100*cev(par, r['adult'] - w0, w0):10.3f}%")

    print("\n   WHAT IS BEHIND THE CHILDHOOD NUMBER")
    print(f"   {'policy':>26}{'child c':>10}{'child h':>10}"
          f"{'on street':>11}{'parent uses':>13}")
    for r in rows:
        k = r['kid']
        print(f"   {r['lab']:>26}{k['c']:10.5f}{k['h']:10.5f}"
              f"{k['street']:11.5f}{k['parent_uses']:13.5f}")

    # ---- the transition ----
    print("\n\nTHE TRANSITION, cohort by cohort")
    print(f"   rationed TF reallocation factor {scale:.4f}  "
          f"(coverage {cov0:.4f} -> {cov:.4f})")
    for policy, lab in (('HF', 'Housing First'),
                        ('TF', 'Treatment First'),
                        ('RTF', 'rationed Treatment First')):
        q = with_(par, pv_scale=scale) if policy == 'RTF' else par
        path, kid_old, kid_new, lvl = TC.path_with_childhood(
            q, policy, par.pV, p0, v1b, w0, 20)
        print(f"\n   {lab}")
        print(f"      childhood level: old regime {kid_old:.6f}, "
              f"under this policy {kid_new:.6f}")
        print(f"      {'cohort':>7}{'childhood':>11}{'adult':>11}{'total':>11}"
              f"{'CEV':>10}{'CEV adult':>11}{'cohort homeless':>17}"
              f"{'cohort SUD':>12}")
        for r in path:
            if r['cohort'] > 5 and r['cohort'] != 20:
                continue
            tag = f"{r['cohort']:7d}" if r['cohort'] != 20 else "     20"
            print(f"      {tag}{r['childhood']:11.5f}{r['adult']:11.5f}"
                  f"{r['total']:11.5f}{100*r['cev']:9.3f}%"
                  f"{100*r['cev_adult_only']:10.3f}%"
                  f"{r['homeless']:17.4f}{r['sud']:12.4f}")


if __name__ == '__main__':
    main()
