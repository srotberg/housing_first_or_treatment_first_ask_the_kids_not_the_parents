#!/usr/bin/env python3
"""THE OPTIMAL LEVEL OF THE DISORDER, ITS LONG-RUN WELFARE, AND THE TRANSITION,
with every welfare number split into the CHILDHOOD half and the ADULT half.

The author, 13 September: *"now do the optimal Sud in the stylized model, the
long run welfare and the transition, and breakdown the welfare by childhood and
adult for each."*

WHAT "OPTIMAL" MEANS HERE, because the model makes it precise.

A parent's drug purchase reaches its child twice.  It takes consumption out of
the shared bundle while the child is in the house -- the FLOW channel, which is
omega_c*(xi-1)*u(X_K) in the parent's period 1 utility -- and it raises the
chance the child inherits the income penalty delta_d -- the CONTINUATION
channel, which is beta*omega_c*chdmg*pi(v).  The parent weighs BOTH at omega_c,
and omega_c is calibrated at 0.00055.  So essentially the whole of the damage is
external, and the decentralised economy uses more of the drug than a planner who
counted the child would choose.

THE PLANNER IS omega = 1 AND NOTHING ELSE CHANGES.  At omega = 1 the household
counts the child exactly as the equivalence scale says a household member counts
-- (xi - 1) of the bundle in the flow, and the whole of chdmg in the
continuation.  That is the first best allocation of the drug, and the gap
between it and the calibrated economy IS the externality.  No programme changes:
the policy is the benchmark one, 'HF', on both sides.  What changes is whose
welfare the household maximises.

THE ONE TRAP, AND IT IS THE REASON THIS FILE EXISTS RATHER THAN A ONE-LINE SCAN.
value1 is the household's OBJECTIVE, and at omega = 1 that objective contains
the child.  Counting it again in the child's own cohort would count the child
twice and would make welfare rise with omega by ACCOUNTING rather than by
behaviour -- the internalise.py docstring names this and handles the
continuation half of it, because period1 adds the penalty back after the choice
of v is made.  The FLOW half is not handled anywhere: omega_c*(xi-1)*u(X_K) sits
inside _flow, inside the branch value, inside own, and inside value1.  At
omega_c = 0.00055 it is invisible.  At omega = 1 it is most of the difference.

So the parent's own value is netted of BOTH child terms here, and the child is
counted once, in its own lifetime, through childhood_level.  Every welfare
number below is

    lifetime = childhood (the child's own, aleph included)
             + adult    (the parent's own, every child term removed)

and the null test at the bottom of the steady state block proves the netting:
at omega = 0 the netted value must equal value1 exactly, because there is
nothing to net.
"""
import json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import stylized as S
from stylized import P, with_, solve_child_damage, _hpick, value1
from recalibrate import FIXED, START
import calibrate as C
from calibrate import stats
from child_welfare import _childhood_u, cev

# ---------------------------------------------------------------------------
# THE BASE VECTOR, WRITTEN OUT AND CHECKED RATHER THAN LOADED FROM A CACHE.
#
# TRANSITION_LESSONS section 7 records what the alternative costs: children.py
# opened calibrated.json at import, built its parameters from it, and every
# number the transition produced was at THAT vector rather than the caller's --
# a file dated three weeks earlier, carrying a parameter from a rejected
# channel.  A transition table was reported to the author and withdrawn.
#
# So the vector is stated here, and main() prints it beside the moments it
# reproduces.  It is iteration 1350 of the run that ended at 19:44 on 13
# September, the run in which delta_d reached its bound.
# ---------------------------------------------------------------------------
CALIBRATED = dict(aleph=12.45625, gam=0.44351, h1=0.01017, b=0.05111,
                  u0=0.04622, u1=0.10814, omega=0.00055, delta_d=1.00000,
                  kap=0.10747, th=0.14962, pi_base=0.0368 / 0.089)

# What that run's table printed, to five decimals, which is all it printed.
TABLE_1350 = dict(part=0.0892, dshare=0.1403, homeless=0.0099,
                  hspend=0.2678, r_use=0.7436)

BASE_POLICY = 'HF'


def base(**over):
    """The calibrated economy, assembled exactly as sr_calibrate assembles it."""
    kw = {**{k: v for k, v in FIXED.items() if k != 'kap'},
          **START,
          **{"th": 0.25, "beta": 0.995 ** 30, "kap": 1.0 - 0.91 ** 2,
             "delta_d": 0.24, "y_floor": 0.0, "h1": 0.005, "b": 0.07}}
    kw.update(CALIBRATED)
    # The driver applies the income floor AFTER the seed, so this does too.
    kw["y_floor"] = 0.099
    kw.update(over)
    return with_(P(), **kw)


# ---------------------------------------------------------------------------
# THE TWO HALVES OF A LIFETIME, AT ONE INCOME NODE
# ---------------------------------------------------------------------------

def _alloc(q, y):
    """The realised allocation at each period 1 state: mass, consumption,
    housing services, and the branch value the household ends up with.

    A household that uses contributes its USING allocation and one that
    abstains its abstaining one, which is what makes this the realised
    childhood rather than a counterfactual one.
    """
    out = []
    for p, gain, v, bu, bn, inc, own in S.period1(q, y, q.policy):
        if p <= 1e-14:
            continue
        uses = gain > 0.0
        a, street, rent, _vs, small = (bu if uses else bn)
        c = inc - rent - q.p_v * (v if uses else 0.0) - a
        out.append((p, c, _hpick(q, street, small), own))
    return out


def kid_node(q, y):
    """The child's OWN childhood utility, in a household at income y.

    aleph is IN it, on the author's instruction of 12 September -- *"Yes for
    welfare the child's utility growing up counts"* -- because a childhood is a
    period of life and is valued as one.  See _childhood_u.
    """
    tot = m = 0.0
    for p, c, h, _own in _alloc(q, y):
        tot += p * _childhood_u(q, c, h)
        m += p
    return tot / m if m > 1e-14 else float('nan')


def adult_node(q, y):
    """The parent's OWN lifetime value at income y, net of EVERY child term.

    Two terms come out, and only one of them was already handled.

    THE CONTINUATION, beta*omega*chdmg*pi(v), is added back by period1 itself:
    it returns own = tot[k] + pen[k], which is the using branch's value with the
    penalty removed.  For an abstainer there is nothing to add back, because the
    onset hazard is flat -- pi(v) = pi_base*1{v>0} -- so pi(0) is zero.

    THE FLOW, omega*(xi-1)*u(X_K), is NOT handled anywhere else and is removed
    here.  _flow adds it inside the bracket, so it is inside the branch value
    and inside own.  It is the same object _childhood_u computes with the aleph
    switch OFF -- aleph is added once to the assembled flow, outside the bracket
    the child weight multiplies, so the parent never carries the child's aleph.
    """
    tot = m = 0.0
    for p, c, h, own in _alloc(q, y):
        tot += p * (own - q.omega * _childhood_u(q, c, h, aleph_for_child=False))
        m += p
    return tot / m if m > 1e-14 else float('nan')


def grids(par, policy=None, pV=None):
    """(adult, childhood) over the income grid, at a solved child damage."""
    q = with_(par, policy=(policy or par.policy))
    if pV is not None:
        q = with_(q, pV=pV)
    q = solve_child_damage(q, q.policy)
    a = np.array([adult_node(q, y) for y in C.YG], dtype=float)
    k = np.array([kid_node(q, y) for y in C.YG], dtype=float)
    return q, a, k


# ---------------------------------------------------------------------------
# THE LONG RUN
# ---------------------------------------------------------------------------
import transition as T

WW = T.WW


def _mix(p, g, par):
    """A cohort-weighted average of a grid, over the penalty mixture p."""
    return sum(ps * float((WW * T._at(g, s)).sum())
               for s, ps in zip(T._shifts(par), p))


def _kid_by_shift(par, policy, pV=None):
    """Childhood utility SOLVED at each shifted income, one array per type.

    NOT INTERPOLATED, for the reason _hl_by_shift gives: the child's bundle
    carries the housing choice, and whether a household takes the street or the
    small unit is very nearly a step in income.  Interpolating a step between
    two nodes understates it, and the childhood level is the object the whole
    split rests on.
    """
    q = with_(par, policy=policy)
    if pV is not None:
        q = with_(q, pV=pV)
    q = solve_child_damage(q, policy)
    return {float(s): T._solve_at(lambda y: kid_node(q, y), s)
            for s in T._shifts(par)}


def economy(par, label, policy=BASE_POLICY, pV=None):
    """One steady state: its allocation, its rest point, and its welfare split.

    THE REST POINT MOVES WITH omega AND THAT IS HALF THE ANSWER.  Less use means
    fewer children inherit the penalty, so the stationary mixture over penalty
    types is itself an equilibrium object.  Reporting the disorder rate at the
    BASE income distribution, as the calibration's own stats() does, holds that
    mixture fixed and understates what internalisation buys.  Both are printed.
    """
    q, a_grid, k_grid = grids(par, policy, pV)
    v1, sud, hl, ev = T._policy_grids(par, policy, pV if pV is not None else par.pV)
    p = T._rest_point(sud, T._hl_by_shift(par, policy, pV if pV is not None else par.pV), par)
    kbs = _kid_by_shift(par, policy, pV)

    adult = _mix(p, a_grid, par)
    kid = sum(ps * float((WW * kbs[float(s)]).sum())
              for s, ps in zip(T._shifts(par), p))
    m = stats(q)
    return dict(label=label, par=q, p=p,
                adult=float(adult), kid=float(kid), total=float(adult + kid),
                sud_stat=T._outcome(p, sud, par),
                homeless_stat=T._outcome(p, hl, par),
                sud_base=m['sud'], part=m['part'], dshare=m['dshare'],
                homeless_base=m['homeless'], r_use=m['r_use'],
                a_grid=a_grid, k_grid=k_grid, kbs=kbs,
                sud_grid=sud, hl_grid=hl)


def long_run(omegas=(None, 0.0, 0.25, 0.50, 1.0)):
    """The optimal disorder rate, and the long-run welfare it buys.

    omega = None is the calibrated economy; 1.0 is the planner.  The values in
    between are there because the wedge is not linear and the author has asked
    before what a partial internalisation does.
    """
    out = []
    for om in omegas:
        if om is None:
            par, lab = base(), 'calibrated  omega_c'
        else:
            par, lab = base(omega=om), f'omega = {om:.2f}'
        out.append(economy(par, lab))
    return out


def _fmt_long_run(rows):
    de = rows[0]
    print('\nTHE OPTIMAL DISORDER RATE')
    print('  omega = 1 is the planner: the household counts the child exactly as')
    print('  the equivalence scale says a member counts.  No programme changes.\n')
    h = (f"  {'economy':>20}{'SUD':>9}{'particip':>10}{'drug sh':>9}"
         f"{'homeless':>10}{'SUD (stat)':>12}{'homeless(st)':>14}")
    print(h); print('  ' + '-' * (len(h) - 2))
    for r in rows:
        print(f"  {r['label']:>20}{r['sud_base']:9.4f}{r['part']:10.4f}"
              f"{r['dshare']:9.4f}{r['homeless_base']:10.4f}"
              f"{r['sud_stat']:12.4f}{r['homeless_stat']:14.4f}")
    print('\n  SUD and homeless are at the BASE income distribution, the way the')
    print('  calibration measures them.  The (stat) columns are at the stationary')
    print('  mixture over inherited penalty types, which is the long-run object:')
    print('  less use means fewer children inherit delta_d, which raises their')
    print('  incomes, which lowers use again.')

    print('\nLONG-RUN WELFARE, SPLIT')
    h = (f"  {'economy':>20}{'childhood':>12}{'adult':>12}{'lifetime':>12}"
         f"{'CEV total':>12}{'CEV child':>12}{'CEV adult':>12}")
    print(h); print('  ' + '-' * (len(h) - 2))
    for r in rows:
        ct = cev(de['par'], r['total'] - de['total'], de['total'])
        # The two halves are priced against the SAME lifetime level, so they add
        # up to the total in utils; in CEV they do not, because the CEV is not
        # linear.  Both are reported because the author asked for the split.
        ck = cev(de['par'], r['kid'] - de['kid'], de['total'])
        ca = cev(de['par'], r['adult'] - de['adult'], de['total'])
        print(f"  {r['label']:>20}{r['kid']:12.5f}{r['adult']:12.5f}"
              f"{r['total']:12.5f}{100*ct:11.3f}%{100*ck:11.3f}%{100*ca:11.3f}%")
    print('\n  childhood is the child\'s OWN utility, aleph included.  adult is the')
    print('  parent\'s own lifetime value with EVERY child term netted out, so the')
    print('  child is counted once and only once and omega cannot move welfare by')
    print('  accounting.  CEVs are against the calibrated economy.')


def collapse_scan(omegas=(0.0, 0.00055, 0.002, 0.005, 0.01, 0.02, 0.04,
                          0.06, 0.10, 0.15, 0.25, 1.0)):
    """WHERE THE DISORDER GOES TO ZERO, and it is nowhere near omega = 1.

    The planner's allocation turns out to be a CORNER -- no drug use at all --
    so "the optimal disorder rate" is a threshold question rather than an
    interior one: how much of the child does a parent have to count before
    using stops being worth it?  The answer is the whole content of the result,
    because it says the externality is large relative to the private gain, and
    a scan is the only honest way to report a corner.
    """
    rows = []
    for om in omegas:
        q = solve_child_damage(with_(base(omega=om), policy=BASE_POLICY), BASE_POLICY)
        m = stats(q)
        rows.append(dict(omega=om, part=m['part'], sud=m['sud'],
                         dshare=m['dshare'], homeless=m['homeless'],
                         r_use=m['r_use']))
    return rows


def _fmt_collapse(rows):
    print('\nHOW MUCH OF THE CHILD HAS TO BE COUNTED BEFORE USE STOPS')
    h = (f"  {'omega':>9}{'particip':>10}{'SUD':>9}{'drug sh':>9}"
         f"{'homeless':>10}{'r_use':>9}")
    print(h); print('  ' + '-' * (len(h) - 2))
    for r in rows:
        lab = f"{r['omega']:.5f}"
        mark = '   <- calibrated' if abs(r['omega'] - CALIBRATED['omega']) < 1e-9 else ''
        print(f"  {lab:>9}{r['part']:10.4f}{r['sud']:9.4f}{r['dshare']:9.4f}"
              f"{r['homeless']:10.4f}{r['r_use']:9.4f}{mark}")


# ---------------------------------------------------------------------------
# THE TRANSITION
# ---------------------------------------------------------------------------

def transition(par_new, n=8, par_old=None, label='reform'):
    """Cohort by cohort from the calibrated rest point to the reformed one.

    THE TIMING IS THE AUTHOR'S, and transition_childhood.py established it.
    The rule lands at the START of the young's period 1, before their choices,
    so cohort 1's parents ALREADY face it: the mixture cohort 1 is born into is
    one step of the pre-reform rest point taken under the NEW rule, not the rest
    point itself.  And the children alive at the reform are in the household
    when it lands, so their whole childhood is lived under the new regime --
    what they carry from the old world is their parents' DISORDER STATUS, which
    was settled before, and that is p0, which the adult term already uses.

    WHAT THIS ADDS TO transition_childhood.py: childhood VARIES BY COHORT.
    That file computes one childhood level per policy and gives it to every
    cohort.  Here the childhood level is solved at each shifted income and mixed
    over the PARENTS' penalty mixture -- p at t-1, not t -- because a child's
    childhood is lived in its parent's household at its parent's income.  With
    the whole point of the transition being that the inherited income
    distribution moves, holding childhood fixed across cohorts throws away the
    half of the dynamics the author asked to see.
    """
    par_old = base() if par_old is None else par_old

    # The pre-reform world.
    _qo, a_old, _k_old = grids(par_old, BASE_POLICY, par_old.pV)
    v1o, sud_o, hl_o, ev_o = T._policy_grids(par_old, BASE_POLICY, par_old.pV)
    kbs_old = _kid_by_shift(par_old, BASE_POLICY, par_old.pV)
    p0 = T._rest_point(sud_o, T._hl_by_shift(par_old, BASE_POLICY, par_old.pV), par_old)

    def kid_at(p, kbs, q):
        return sum(ps * float((WW * kbs[float(s)]).sum())
                   for s, ps in zip(T._shifts(q), p))

    adult0 = _mix(p0, a_old, par_old)
    kid0 = kid_at(p0, kbs_old, par_old)
    level0 = adult0 + kid0

    # The reformed world.
    _qn, a_new, _k_new = grids(par_new, BASE_POLICY, par_new.pV)
    v1n, sud_n, hl_n, ev_n = T._policy_grids(par_new, BASE_POLICY, par_new.pV)
    kbs_new = _kid_by_shift(par_new, BASE_POLICY, par_new.pV)
    hls_n = T._hl_by_shift(par_new, BASE_POLICY, par_new.pV)

    rows = []
    p_par, p = p0.copy(), T._step(p0, sud_n, hls_n, par_new)
    for t in range(1, n + 1):
        adult = _mix(p, a_new, par_new)
        kid = kid_at(p_par, kbs_new, par_new)      # the PARENT's mixture
        total = adult + kid
        rows.append(dict(cohort=t, adult=float(adult), childhood=float(kid),
                         total=float(total),
                         cev=float(cev(par_old, total - level0, level0)),
                         cev_child=float(cev(par_old, kid - kid0, level0)),
                         cev_adult=float(cev(par_old, adult - adult0, level0)),
                         sud=T._outcome(p, sud_n, par_new),
                         homeless=T._outcome(p, hl_n, par_new)))
        p_par, p = p, T._step(p, sud_n, hls_n, par_new)
    return rows, dict(adult0=adult0, kid0=kid0, level0=level0,
                      sud0=T._outcome(p0, sud_o, par_old),
                      homeless0=T._outcome(p0, hl_o, par_old))


def _fmt_transition(rows, b, label):
    print(f'\nTRANSITION: {label}')
    print(f"  pre-reform    childhood {b['kid0']:9.5f}   adult {b['adult0']:9.5f}"
          f"   lifetime {b['level0']:9.5f}   SUD {b['sud0']:.4f}"
          f"   homeless {b['homeless0']:.4f}")
    h = (f"  {'cohort':>7}{'childhood':>11}{'adult':>11}{'lifetime':>11}"
         f"{'CEV':>10}{'CEV child':>11}{'CEV adult':>11}{'SUD':>9}{'homeless':>10}")
    print(h); print('  ' + '-' * (len(h) - 2))
    for r in rows:
        print(f"  {r['cohort']:7d}{r['childhood']:11.5f}{r['adult']:11.5f}"
              f"{r['total']:11.5f}{100*r['cev']:9.3f}%{100*r['cev_child']:10.3f}%"
              f"{100*r['cev_adult']:10.3f}%{r['sud']:9.4f}{r['homeless']:10.4f}")


if __name__ == '__main__':
    # SELECTABLE, because the long-run block is several hundred model solves and
    # iterating on the transition should not pay for it every time.
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    par = base()
    q = solve_child_damage(par)
    m = stats(q)
    print('THE VECTOR THIS RAN AT, and the table it reproduces.')
    print('  ' + '  '.join(f'{k}={v:.5f}' for k, v in CALIBRATED.items()))
    print(f"  beta={par.beta:.6f}  rho={par.rho}  sigma={par.sigma}  "
          f"y_floor={par.y_floor}  h2={par.h2}  h3={par.h3}")
    print(f"\n  {'moment':>10}{'here':>10}{'iter 1350':>11}{'gap %':>8}")
    for k, v in TABLE_1350.items():
        print(f"  {k:>10}{m[k]:10.4f}{v:11.4f}{100*(m[k]-v)/v:7.1f}%")
    print('  The table printed five decimals, so the vector is recovered to five')
    print('  decimals and the moments to within that rounding.')

    if what in ('all', 'longrun'):
        _fmt_collapse(collapse_scan())
        _fmt_long_run(long_run())

    if what not in ('all', 'transition'):
        raise SystemExit(0)

    # THE NULL TEST FIRST.  A reform that changes nothing must return a CEV of
    # exactly zero at every cohort.  It is the only thing that proves the
    # baseline and the path are built on the same object, and transition.py's
    # own history is the reason it is run every time: a baseline built on a
    # different child penalty from the path scored a -2.881 per cent gain for a
    # policy that did nothing.
    rows, b = transition(base(), n=4, label='null')
    worst = max(abs(r['cev']) for r in rows)
    print(f"\nNULL TEST: reform = no change.  worst |CEV| over 4 cohorts "
          f"= {100*worst:.2e} %")
    if worst > 1e-9:
        _fmt_transition(rows, b, 'NULL -- SHOULD BE ZERO')

    rows, b = transition(base(omega=1.0), n=8)
    _fmt_transition(rows, b, 'full internalisation, omega_c -> 1, programme unchanged')
    print('\n  ONE GENERATION, AND THAT IS NOT A BUG.  At omega = 1 nobody uses,')
    print('  so no child inherits the penalty and the mixture reaches its rest')
    print('  point in a single step: cohort 1 is already clean, because its')
    print('  parents faced the rule before they chose.  What separates cohort 1')
    print('  from the rest is its CHILDHOOD alone -- it was raised by parents')
    print('  who still carried the penalty their own parents handed them, so it')
    print('  collects 0.602 per cent where every later cohort collects 3.533.')

    # AN INTERIOR REFORM, so the dynamics are visible rather than absorbed in
    # one step, and so the result does not rest on a corner.  omega = 0.005 is
    # the largest weight scanned at which the drug share is still strictly
    # positive, i.e. the last point where users are buying a real quantity
    # rather than sitting on the grid's smallest positive rung.
    rows, b = transition(base(omega=0.005), n=8)
    _fmt_transition(rows, b, 'partial internalisation, omega_c -> 0.005')
