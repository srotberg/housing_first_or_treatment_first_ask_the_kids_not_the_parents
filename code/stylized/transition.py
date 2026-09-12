"""
THE TRANSITION TO TREATMENT FIRST, generation by generation.

WHY THE MODEL HAS A TRANSITION AT ALL, when a household lives two periods. The
link across generations is not persistence of income, which the model
deliberately leaves out, but the PENALTY: a child's income is a fresh draw from
the same lognormal, multiplied by (1 - del_d) if its parent acquired the
disorder and by (1 - del_h) if its parent was homeless. So what a cohort
inherits from the one before it is not a level of income, it is a MIXTURE over
four penalty types,

    s in { 1,  1-del_d,  1-del_h,  (1-del_d)(1-del_h) },

and that mixture is a Markov chain: the share of a cohort carrying each penalty
is decided by how many of the previous cohort used and how many were unhoused,
which in turn depends on the incomes that cohort was born with. Change the
policy and the chain starts moving, geometrically, to a new rest point. It
settles in two or three cohorts, so five is enough to see all of it.

WHY THE PICTURE IS WORTH A SECTION. The paper's whole claim is that Treatment
First buys the child at the parent's expense, and a static comparison cannot
show that: it reports the sum. The transition separates them in time. The cohort
alive when the policy lands is the cohort that pays, since conditionality is a
cost to it and none of the benefit has arrived yet. The cohorts after it inherit
a cleaner and better housed parent generation, so they are born richer, and
their welfare climbs to a rest point above where it started. The two effects are
the same two terms as in the verdict table, seen one at a time.

WHAT IS PLOTTED: expected lifetime value of a NEWBORN cohort, V1 averaged over
the income distribution that cohort is actually born into, expressed as a
consumption equivalent against the pre reform rest point. Cohort 0 is the old
rest point by construction. Cohort 1 is the one the reform lands on.

Run:  python3 transition.py
"""

import json
import os
import math
import numpy as np

from stylized import P, with_, value1, use_prob, homeless_prob, terminal_homeless_prob
from calibrate import YG, W, stats
from welfare import cev
from children import DEL_D, DEL_H

WW = W / W.sum()
LY = np.log(YG)

BASE_POLICY = 'HF'      # the world as it is: rationed vouchers, no condition
PV_OPT = 1.0            # the optimal Treatment First programme is universal
# COMPUTE LONG, PLOT SHORT, and do not confuse the two. The chain settles in two
# or three cohorts here, but a horizon of five CANNOT ESTABLISH that: _settle
# measures each path against the LAST cohort computed, so if the path were still
# drifting at cohort five it would report five and read as converged. The claim
# that the economy has reached its rest point is only worth as much as the
# horizon behind it.
#
# So the chain is run out to GENERATIONS_LONG and the figure draws the first
# GENERATIONS_SHOW, extended automatically if the path has not settled inside
# them. Showing twenty would be seventeen flat markers; computing five would be
# an assumption wearing the clothes of a result.
#
# THE SAME APPLIES WITH FORCE TO THE QUANTITATIVE MODEL, where the transition is
# a genuine sequence of general equilibrium prices rather than a Markov chain on
# four penalty types, nothing redraws every generation, and the speed of
# convergence is not known in advance. That transition should be run for twenty
# periods or more and truncated for display only after the path is seen to be
# flat, never truncated at a horizon chosen first.
GENERATIONS_LONG = 20
GENERATIONS_SHOW = 5
GENERATIONS = GENERATIONS_LONG


def _at(vals, s):
    """
    vals evaluated at income y*s, interpolated in log income.

    INTERPOLATING THE ANSWER IS NOT GOOD ENOUGH FOR THE HOMELESSNESS GRIDS and
    this is kept only for the ones where it is. Whether a household is unhoused
    is very nearly a step in income, housed on one side of the rent and not on
    the other, and interpolating a step between two nodes understates it badly:
    measured against the same quantity solved AT the shifted income, this route
    put the initial old's terminal homelessness under Treatment First at 0.33
    per cent where the exact answer is 0.52, an error of well over half. The
    author caught it because the transition quoted both numbers in one
    paragraph and they did not line up.

    Use _solve_at for anything that keys on a threshold. This remains correct
    for smooth objects like V1.
    """
    return np.interp(LY + np.log(s), LY, vals, left=vals[0], right=vals[-1])


def _solve_at(fn, s):
    """
    fn evaluated at income y*s by SOLVING there, not by interpolating a grid
    solved elsewhere. Costs one model solve per node per shift, which is why it
    is used only where the interpolation error is first order.
    """
    return np.array([fn(float(y) * float(s)) for y in YG], dtype=float)


def _policy_grids(par, policy, pV):
    """V1, the probability of ending with the disorder, and the probability of
    being unhoused, at every income node under one policy."""
    q = with_(par, policy=policy, pV=pV)
    v1 = np.array([value1(q, y, policy) for y in YG])
    use = np.array([use_prob(q, y, policy) for y in YG], dtype=float)
    # TWO HOMELESSNESS OBJECTS, and they are not the same one. What a cohort
    # PASSES ON is whether the parent was ever unhoused, in either period, since
    # that is what the child's penalty is keyed on. What the figure REPORTS is
    # the realised period 1 rate, which is the rate the model is calibrated to
    # and the one comparable with the data. Using the first for both would
    # overstate the published homelessness rate; using the second for both would
    # switch off the channel by which conditionality's own revocations reach a
    # child.
    hl = np.array([homeless_prob(q, y, policy) for y in YG], dtype=float)
    ev = np.array([terminal_homeless_prob(q, y, policy) for y in YG], dtype=float)
    prog = stats(q)['prog']
    return (v1, np.clip(use * prog, 0.0, 1.0), np.clip(hl, 0.0, 1.0),
            np.clip(ev, 0.0, 1.0))



def _hl_by_shift(par, policy, pV):
    """
    Terminal homelessness SOLVED at each shifted income, one array per penalty
    type. See the note on _at: this quantity is a step in income and cannot be
    interpolated from a grid solved at unshifted incomes without losing more
    than half of it.
    """
    q = with_(par, policy=policy, pV=pV)
    return {float(s): np.clip(
        _solve_at(lambda y: terminal_homeless_prob(q, y, policy), s), 0.0, 1.0)
        for s in _shifts(par)}


def _bridge_hl_by_shift(par, new_policy, pv_new):
    """The same, for the generation the reform catches mid life."""
    from stylized import period1, solve_period2
    old = with_(par, pV=par.pV, policy=BASE_POLICY)
    new = with_(par, pV=pv_new, policy=new_policy)

    def one(y):
        ag, _, H2c, _, _, _ = solve_period2(new, y, new_policy, used=0)
        if new_policy == 'HF':
            H2u = H2c
        else:
            _, _, H2u, _, _, _ = solve_period2(new, y, new_policy, used=1)
        tot = 0.0
        for p, gain, v, bu, bn, _inc, _own in period1(old, y, BASE_POLICY):
            uses = gain > 0.0
            a = (bu if uses else bn)[0]
            pid = (1.0 - float(np.exp(-old.lam * v))) if uses else 0.0
            Hx = H2u if uses else H2c
            tot += p * sum(pd * float(np.interp(a, ag, Hx[:, d]))
                           for d, pd in ((1, pid), (0, 1.0 - pid)))
        return tot

    return {float(s): np.clip(_solve_at(one, s), 0.0, 1.0) for s in _shifts(par)}


def _bridge_grids(par, new_policy, pv_new):
    """
    The disorder and ever-unhoused grids for the generation the reform CATCHES
    MID LIFE: period 1 chosen under the OLD rule, period 2 lived under the NEW.

    THIS IS THE GENERATION THAT PARENTS COHORT 1, and until this existed the
    chain did not know it. path() handed cohort 1 the pre reform rest point,
    which is the mixture produced by a parent who lived its WHOLE life under the
    old rule. Cohort 1's parent did not: it was young before the reform and old
    when the reform landed, so its period 2 was lived under the new policy, and
    under Treatment First that is precisely when its voucher is taken away for a
    disorder acquired before the rule existed. Keyed on the old rest point, the
    homelessness that conditionality itself creates could never reach a child,
    and the two policies were identical on cohort 1 BY CONSTRUCTION rather than
    as a finding.

    This is the same mistake as the one recorded in TRANSITION_LESSONS section
    on the child's inherited penalty, in its last hiding place: fixed there for
    the rest points, still present here for the first step off them.

    The disorder is settled in period 1 and so does not depend on the new
    policy; being unhoused can happen in either period and so does.
    """
    from stylized import period1, solve_period2
    old = with_(par, pV=par.pV, policy=BASE_POLICY)
    new = with_(par, pV=pv_new, policy=new_policy)
    sud = np.zeros(len(YG))
    ev = np.zeros(len(YG))
    for i, y in enumerate(YG):
        ag, _, H2c, _, _, _ = solve_period2(new, y, new_policy, used=0)
        if new_policy == 'HF':
            H2u = H2c
        else:
            _, _, H2u, _, _, _ = solve_period2(new, y, new_policy, used=1)
        s_tot = e_tot = 0.0
        for p, gain, v, bu, bn, _inc, _own in period1(old, y, BASE_POLICY):
            uses = gain > 0.0
            a = (bu if uses else bn)[0]
            pid = (1.0 - float(np.exp(-old.lam * v))) if uses else 0.0
            Hx = H2u if uses else H2c
            street2 = sum(pd * float(np.interp(a, ag, Hx[:, d]))
                          for d, pd in ((1, pid), (0, 1.0 - pid)))
            s_tot += p * pid
            # PERIOD 2 ONLY, because that is when the household dies and when
            # conditionality acts. Counting period 1 as well had the initial old
            # transmitting a penalty picked up under the OLD rationed programme
            # even when the new universal one housed them for the whole of their
            # second period, so children were born behind a Housing First that
            # had housed their parents.
            e_tot += p * street2
        sud[i] = s_tot
        ev[i] = e_tot
    return np.clip(sud, 0.0, 1.0), np.clip(ev, 0.0, 1.0)


def _shifts(par=None):
    """The four penalty types, as MULTIPLIERS on the child's income.

    READS par.delta_d WHEN GIVEN ONE.  The author, 12 September: *"calibrate the
    child's Sud penalty to match the Sud ratio"*.  Until now this used the
    module constant DEL_D, so the transition's penalty mixture did not move when
    the calibration moved the penalty: the cohort CEV read 1.773 per cent at
    delta_d of 0.24, 0.40, 0.57 AND 0.75 while the child SUD odds ratio moved
    1.36 to 2.47.  A transition table was reported on that and withdrawn.

    THE TWO ARE IN DIFFERENT UNITS AND THE CONVERSION IS NOT OPTIONAL.
    par.delta_d is a LOG income shift -- stylized.py sets
    log y_child = rho log y_parent + (1-rho) log ybar - delta_d -- so it enters
    as exp(-delta_d).  DEL_D is a FRACTIONAL cut and enters as (1 - DEL_D).
    Substituting one for the other unconverted changes the penalty by 19 per
    cent at the current values: 0.36 in logs is a 30.2 per cent cut, while 0.24
    as a fraction is a 0.274 log shift.

    delta_h is NOT a parameter -- the author dropped it -- so the homelessness
    leg keeps the external DEL_H it has always had.
    """
    dd = DEL_D if par is None else 1.0 - math.exp(-par.delta_d)
    return np.array([1.0, 1.0 - dd, 1.0 - DEL_H,
                     (1.0 - dd) * (1.0 - DEL_H)])


def _step(p, sud, hl, par=None):
    """One generation. p is the mixture over the four penalty types; the return
    is the mixture the CHILDREN of that cohort are born into.

    The disorder and homelessness are taken as independent given income, which
    is the same reduced form children.py uses: both are functions of the income
    the household was born with, and nothing else links them."""
    out = np.zeros(4)
    for s, ps in zip(_shifts(par), p):
        if ps <= 0.0:
            continue
        d = _at(sud, s)
        # SOLVED at the shifted income, not interpolated: see _at.
        h = hl[float(s)] if isinstance(hl, dict) else _at(hl, s)
        out[0] += ps * float((WW * (1 - d) * (1 - h)).sum())
        out[1] += ps * float((WW * d * (1 - h)).sum())
        out[2] += ps * float((WW * (1 - d) * h).sum())
        out[3] += ps * float((WW * d * h).sum())
    return out / out.sum()


def _welfare(p, v1, par=None):
    """Expected lifetime value of a cohort born into the mixture p.

    par is threaded through only so _shifts can read par.delta_d; omitting it
    falls back to the module constant, which is what every caller did before
    the penalty became a calibrated parameter."""
    return sum(ps * float((WW * _at(v1, s)).sum())
               for s, ps in zip(_shifts(par), p))


def _outcome(p, g, par=None):
    """A cohort's own realised rate of something, given the mixture it is born
    into: its homelessness, or its disorder rate. The welfare path says what the
    reform is worth; these say through what."""
    return sum(ps * float((WW * _at(g, s)).sum())
               for s, ps in zip(_shifts(par), p))


def caught(par, pv_new=PV_OPT):
    """THE GENERATION THE REFORM CATCHES MID LIFE, which the cohort path cannot
    show and which is where conditionality's cost actually falls.

    Every cohort in the path lives its whole life under one policy. The
    households in period 2 when the policy changes did not: they chose whether
    to use under the OLD rule, period 2 is terminal so a disorder cannot be
    recovered from, and Treatment First now withdraws the voucher from those of
    them carrying a disorder they acquired before the rule existed, with no
    period left in which to shed it. They are the transition's cost, and
    a figure that omits them makes conditionality look nearly free.

    Returns the consumption equivalent they lose and the homelessness the
    revocation itself creates, integrating over the assets they actually saved
    and the disorder they actually drew under the old programme."""
    from stylized import period1, solve_period2
    old = with_(par, pV=par.pV, policy=BASE_POLICY)
    new_h = with_(par, pV=pv_new, policy='HF')
    new_t = with_(par, pV=pv_new, policy='TF')
    # THEY ARE NOT DRAWN FROM THE BASE DISTRIBUTION. This generation was itself
    # born into the pre reform rest point, so its income carries whatever
    # penalty its own parent handed it. Iterating over the unshifted grid
    # treated them as richer than they are, and they are the households the
    # answer is about.
    v1b, sudb, hlb, evb = _policy_grids(par, BASE_POLICY, par.pV)
    p_mix = _rest_point(sudb, _hl_by_shift(par, BASE_POLICY, par.pV), par)
    dv = dv_h = dv_t = mass = hl_h = hl_t = hl_o = 0.0
    for sft, psft in zip(_shifts(par), p_mix):
        if psft <= 0.0:
            continue
        for i, y0 in enumerate(YG):
            y = y0 * sft
            for p, gain, v, bu, bn, inc, _own in period1(old, y, BASE_POLICY):
                uses = gain > 0.0
                a = (bu if uses else bn)[0]
                pid = (1.0 - np.exp(-old.lam * v)) if uses else 0.0
                # solved ONCE per (income, use) pair, not once per disorder
                # draw: the period 2 problem does not depend on d, which only
                # selects a column of the answer.
                agh, W2h, H2h, _, _, _ = solve_period2(new_h, y, 'HF', used=int(uses))
                agt, W2t, H2t, _, _, _ = solve_period2(new_t, y, 'TF', used=int(uses))
                # AND THE COUNTERFACTUAL WHERE NOTHING CHANGES, so each policy
                # can be priced against the pre reform world the way every
                # cohort in the figure is, rather than only against each other.
                ago, W2o, H2o, _, _, _ = solve_period2(old, y, BASE_POLICY,
                                                    used=int(uses))
                for d, pd in ((1, pid), (0, 1.0 - pid)):
                    m = psft * WW[i] * p * pd
                    if m <= 0.0:
                        continue
                    _wh = float(np.interp(a, agh, W2h[:, d]))
                    _wt = float(np.interp(a, agt, W2t[:, d]))
                    _wo = float(np.interp(a, ago, W2o[:, d]))
                    dv += m * (_wh - _wt)
                    dv_h += m * (_wh - _wo)
                    dv_t += m * (_wt - _wo)
                    hl_h += m * float(np.interp(a, agh, H2h[:, d]))
                    hl_t += m * float(np.interp(a, agt, H2t[:, d]))
                    # the benchmark: what this generation's homelessness would
                    # have been had the old rationed programme simply continued
                    hl_o += m * float(np.interp(a, ago, H2o[:, d]))
                    mass += m
    dv /= max(mass, 1e-12)
    dv_h /= max(mass, 1e-12)
    dv_t /= max(mass, 1e-12)
    return dict(cev=float(cev(par, dv)),
                # each policy against the pre reform world, which is the axis
                # every cohort line is already drawn on
                cev_hf=float(cev(par, dv_h)), cev_tf=float(cev(par, dv_t)),
                hl_hf=hl_h / max(mass, 1e-12),
                hl_tf=hl_t / max(mass, 1e-12),
                hl_old=hl_o / max(mass, 1e-12))


def caught_coverage(par, pv_new=PV_OPT):
    """
    The share of the INITIAL OLD actually holding a voucher in period 2, under
    the old rule and under each new one.

    WHY THIS IS NOT pi_V. pi_V is recipients over the INCOME ELIGIBLE, and
    eligibility is capped at kappa_V times median income, so the population
    share covered is pi_V times the eligible share. And under Treatment First it
    is smaller again: an eligible household that carries the disorder fails the
    condition and holds no voucher however generous the programme is. Quoting
    the eligible share as though universal coverage reached all of it is true of
    Housing First and false of Treatment First, which is the whole point of the
    section.
    """
    from stylized import period1, _states
    old = with_(par, pV=par.pV, policy=BASE_POLICY)
    v1b, sudb, hlb, evb = _policy_grids(par, BASE_POLICY, par.pV)
    p_mix = _rest_point(sudb, _hl_by_shift(par, BASE_POLICY, par.pV), par)
    out = {}
    for lab, pol, pv in (('old', BASE_POLICY, par.pV),
                         ('hf', 'HF', pv_new), ('tf', 'TF', pv_new)):
        new = with_(par, pV=pv, policy=pol)
        cov = mass = 0.0
        for sft, psft in zip(_shifts(par), p_mix):
            if psft <= 0.0:
                continue
            for i, y0 in enumerate(YG):
                y = y0 * sft
                for p, gain, v, bu, bn, inc, _own in period1(old, y, BASE_POLICY):
                    uses = gain > 0.0
                    pid = (1.0 - float(np.exp(-old.lam * v))) if uses else 0.0
                    for d, pd in ((1, pid), (0, 1.0 - pid)):
                        m = psft * WW[i] * p * pd
                        if m <= 0.0:
                            continue
                        for p2, inc2, _ in _states(new, d, pol, y, uses):
                            elig = 1.0 if inc2 <= new.yV else 0.0
                            ok = elig * (1.0 if (pol == 'HF' or d == 0) else 0.0)
                            cov += m * p2 * ok * pv
                            mass += m * p2
        out[lab] = cov / max(mass, 1e-12)
    return out


def _rest_point(sud, hl, par=None, iters=400, tol=1e-14):
    p = np.array([1.0, 0.0, 0.0, 0.0])
    for _ in range(iters):
        q = _step(p, sud, hl, par)
        if np.abs(q - p).max() < tol:
            return q
        p = q
    return p


def path(par, policy, pV, p0, v1_base, w0, n=GENERATIONS):
    """Newborn welfare for n cohorts after the reform lands, as a consumption
    equivalent against the pre reform rest point."""
    v1, sud, hl, ev = _policy_grids(par, policy, pV)
    v1b, sudb, hlb, evb = _policy_grids(par, BASE_POLICY, par.pV)
    out = [(0, 0.0, p0.copy(), _outcome(p0, hlb), _outcome(p0, sudb))]
    # WHO PARENTS WHOM, and the timing is the whole content of this loop.
    #
    # COHORT 1 IS NOT WORSE OFF THROUGH INHERITANCE, and should not be. Its
    # income draw was settled by a parent who completed BOTH periods before the
    # condition existed, so there is nothing about the new policy in what it
    # inherits. What separates the two policies for cohort 1 is only the private
    # loss: its own members who would have used, and now cannot without losing
    # the voucher.
    #
    # COHORT 2 IS THE ONE THAT INHERITS THE REFORM. Its parent is the generation
    # the reform caught mid life: young under the old rule, old when the reform
    # landed, and under Treatment First stripped of the voucher for a disorder
    # acquired before the condition existed. That generation's extra
    # homelessness is transmitted here and nowhere else, so this is the step
    # where conditionality's own revocations first reach a child.
    #
    # From cohort 3 on the parent lived its whole life under the new rule and
    # the chain is stationary in the policy.
    sud_b, _ev_b = _bridge_grids(par, policy, pV)
    # SOLVED AT EACH SHIFTED INCOME. Interpolating these off the unshifted grid
    # lost more than half of the initial old's terminal homelessness, 0.33
    # against an exact 0.52, because being unhoused is a step in income.
    ev_b = _bridge_hl_by_shift(par, policy, pV)
    ev_s = _hl_by_shift(par, policy, pV)
    p = p0.copy()
    for t in range(1, n + 1):
        w = _welfare(p, v1)
        out.append((t, float(cev(par, w - w0)), p.copy(),
                    _outcome(p, hl), _outcome(p, sud)))
        p = _step(p, sud_b, ev_b, par) if t == 1 else _step(p, sud, ev_s, par)
    return out


def run(par=None, n=GENERATIONS):
    here = os.path.dirname(os.path.abspath(__file__))
    par = par or with_(P(), **json.load(open(os.path.join(here, 'calibrated.json'))))

    v1b, sudb, hlb, evb = _policy_grids(par, BASE_POLICY, par.pV)
    p0 = _rest_point(sudb, _hl_by_shift(par, BASE_POLICY, par.pV), par)
    w0 = _welfare(p0, v1b)
    print(f'PRE REFORM REST POINT, {BASE_POLICY} at pi_V = {par.pV}')
    print(f'   share of children born to a parent with the disorder : '
          f'{100*(p0[1]+p0[3]):.3f}%')
    print(f'   share born to a parent who was unhoused              : '
          f'{100*(p0[2]+p0[3]):.3f}%')
    print(f'   del_d = {DEL_D:.4f}   del_h = {DEL_H:.4f}')

    paths = {}
    for lab, pol in (('TF', 'TF'), ('HF', 'HF')):
        paths[lab] = path(par, pol, PV_OPT, p0, v1b, w0, n)
        print(f'\n{lab} at pi_V = {PV_OPT}')
        print(f'   {"cohort":>7s}{"cons equiv":>13s}{"born to SUD":>14s}'
              f'{"born unhoused":>16s}{"homeless":>11s}{"has a SUD":>12s}')
        for t, c, p, hl, sud in paths[lab]:
            print(f'   {t:7d}{100*c:12.4f}%{100*(p[1]+p[3]):13.3f}%'
                  f'{100*(p[2]+p[3]):15.3f}%{100*hl:10.3f}%{100*sud:11.3f}%')
    return paths


def figure(paths, cg=None):
    """Three panels: what the reform is worth to each cohort, and through what.

    The welfare panel alone invites the reading that conditionality is nearly
    free, because the cohorts in it all choose not to use and so never lose a
    voucher. The homelessness and disorder panels show the mechanism doing the
    work, and the marker on the welfare panel shows the generation the reform
    catches mid life, which no cohort line can carry.
    """
    from run import style, save
    plt = style()
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 3.9))
    S = (('TF', 'Treatment First', dict(color='#b2182b', marker='o')),
         ('HF', 'Housing First', dict(color='#2166ac', marker='s', ls='--')))
    # DRAW ONLY WHAT IS WORTH LOOKING AT, having computed far more. The cut is
    # the settling cohort plus two, floored at GENERATIONS_SHOW, so a path that
    # turns out to be slow extends the figure rather than being clipped into
    # looking fast.
    show = max(GENERATIONS_SHOW, _settle_index(paths['TF'], paths['HF']) + 2)
    show = min(show, len(paths['TF']) - 1)
    for ax, idx, ttl, ylab in (
            (axes[0], 1, '(a) Newborn welfare', 'consumption equivalent (\%)'),
            (axes[1], 3, '(b) Homelessness', 'rate (\%)'),
            (axes[2], 4, '(c) Share with a SUD', 'rate (\%)')):
        for lab, name, sty in S:
            t = [r[0] for r in paths[lab]][:show + 1]
            y = [100 * r[idx] for r in paths[lab]][:show + 1]
            ax.plot(t, y, label=name, markersize=5, **sty)
        ax.set_xlabel('cohort of newborns after the reform')
        ax.set_ylabel(ylab)
        ax.set_title(ttl, loc='left', fontsize=11, fontweight='bold')
        # THE SAME X AXIS ON ALL THREE PANELS. Panels (a) and (b) carry the
        # initial old to the left of cohort 0 and had their limits widened to
        # make room; panel (c) kept matplotlib's default, so the three sets of
        # ticks sat at different places across the figure and cohort 3 in one
        # panel was not above cohort 3 in the next.
        ax.set_xlim(-0.45, show + 0.35)
        ax.set_xticks(list(range(show + 1)))
    axes[0].axhline(0.0, color='0.35', lw=1.0, ls=':')
    if cg is not None:
        # THE INITIAL OLD, UNDER BOTH POLICIES, drawn where they can be read.
        # There used to be one marker, Treatment First only, priced against
        # Housing First rather than against the pre reform world, sitting half
        # off the bottom of the axis beside an arrow annotation. Neither what
        # the loss was nor what it was a loss AGAINST could be read off it, and
        # the obvious question, what the same generation gets under Housing
        # First, had no answer on the figure at all.
        #
        # Both are now priced against the pre reform rest point, the axis every
        # cohort line already uses, so the initial old can be compared with the
        # initial newborns directly. They sit at cohort 0, offset so they do not
        # collide, in their policies' own colours, each labelled with its value.
        # PANEL (a) KEEPS A SMALL OFFSET, panel (b) does not, and the reason is
        # the value labels. Here each marker is annotated with its own number,
        # and two labels on one vertical line run into each other; there the
        # markers are bare, so they sit exactly on the cohort 0 gridline where
        # they can be read against the tick.
        for dx, key, col in ((-0.17, 'cev_tf', '#b2182b'),
                             (0.17, 'cev_hf', '#2166ac')):
            yv = 100 * cg[key]
            axes[0].plot([dx], [yv], marker='v', ms=11, color=col, ls='none',
                         markeredgecolor='white', markeredgewidth=0.9, zorder=6)
            axes[0].annotate(f'{yv:+.1f}', xy=(dx, yv), xytext=(0, -14),
                             textcoords='offset points', ha='center',
                             fontsize=8.5, color=col, fontweight='bold')
        axes[0].plot([], [], marker='v', ms=9, color='0.35', ls='none',
                     label='initial old, at cohort 0')
        # THE INITIAL OLD IN PANEL (b) TOO, with the benchmark they are measured
        # against. Panel (a) showed what the reform is worth to them and panel
        # (b) did not show what it does to their housing, which is the channel
        # the welfare number runs through and the one that reaches their
        # children. The open marker is the counterfactual: their homelessness
        # had the old rationed programme simply continued.
        for dx, key, col in ((0.0, 'hl_tf', '#b2182b'),
                             (0.0, 'hl_hf', '#2166ac')):
            axes[1].plot([dx], [100 * cg[key]], marker='v', ms=11, color=col,
                         ls='none', markeredgecolor='white',
                         markeredgewidth=0.9, zorder=6)
        axes[1].plot([0.0], [100 * cg['hl_old']], marker='o', ms=8,
                     mfc='none', mec='0.35', mew=1.3, ls='none', zorder=6)
        axes[1].annotate('no reform', xy=(0.0, 100 * cg['hl_old']),
                         xytext=(6, 4), textcoords='offset points',
                         fontsize=8, color='0.35')
        # ROOM BELOW ZERO for the markers and their labels, so nothing is
        # clipped by the axis the way the single marker used to be.
        _lo = min(100 * cg['cev_tf'], 100 * cg['cev_hf'], 0.0)
        _hi = max(100 * r[1] for lab in paths for r in paths[lab][:show + 1])
        axes[0].set_ylim(_lo - max(1.0, 0.10 * (_hi - _lo)), _hi * 1.10)
    # A ZOOM ON THE COHORTS WHERE CONDITIONALITY IS BEHIND. The whole point of
    # the first two cohorts is that Treatment First is below Housing First
    # there, by 0.07 and 0.19 points, and on an axis that has to carry a swing
    # of twenty five points those two lines are the same line. The main panel
    # stays to scale, which is what makes the long run gap honest, and an inset
    # magnifies the region where the short run gap lives. Its limits come from
    # the data, so it cannot end up empty or clipped on the next calibration.
    if cg is not None and show >= 2:
        _y12 = [100 * paths[k][t][1] for k in ('TF', 'HF') for t in (1, 2)]
        _pad = max(0.06 * (max(_y12) - min(_y12)), 0.02)
        ins = axes[0].inset_axes([0.40, 0.10, 0.56, 0.34])
        for lab, name, sty in S:
            ins.plot([r[0] for r in paths[lab]][1:3],
                     [100 * r[1] for r in paths[lab]][1:3],
                     markersize=4, **sty)
        ins.set_xlim(0.85, 2.15)
        ins.set_ylim(min(_y12) - _pad, max(_y12) + _pad)
        ins.set_xticks([1, 2])
        ins.tick_params(labelsize=7.5)
        ins.set_title('detail: cohorts 1 and 2', fontsize=8, pad=2)
        for sp in ins.spines.values():
            sp.set_linewidth(0.6)
        axes[0].indicate_inset_zoom(ins, edgecolor='0.55', lw=0.8, alpha=0.85)

    # ONE LEGEND, UNDER THE FIGURE. It used to sit inside panel (a) at centre
    # right, unframed, which put it on top of the Housing First line: the dashed
    # series ran straight through the labels and neither could be read. There is
    # no reliably empty corner inside a panel whose two series cross and then
    # separate, so the legend goes outside the axes altogether, where it cannot
    # collide with data whatever the numbers do on the next calibration.
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=len(labels),
               fontsize=9.5, frameon=False,
               bbox_to_anchor=(0.5, -0.02), columnspacing=2.4)
    fig.subplots_adjust(bottom=0.30)
    save(fig, 'stylized_transition')
    return fig


def _dir(now, was, up, down, tol=5e-5, same='holds'):
    """The word for which way a share moved, so a sentence turns with it.

    `same` is what to say when the two are within tol, and it has to be given
    wherever the sentence around the word would not read as English with the
    default: "Treatment First is the holds of the two" is not a sentence."""
    return up if now > was + tol else (down if now < was - tol else same)




def _ordinal(n):
    """Small integers as ordinal words. The prose says "from the third cohort",
    so a cardinal here reads as "from the three cohort"."""
    return {1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth',
            6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth'}.get(n, f'{n}th')


def _words(n):
    """Small integers as words, which is how the prose states them."""
    return {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
            6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}.get(n, str(n))


def _settle_index(tf, hf, tol=1e-3):
    """
    The first cohort after which BOTH paths stay within tol of their rest point.

    Counted from cohort 1, the first born under the new rule, so the answer is
    the number of cohorts the transition takes and not an index into the array.

    THIS IS ONLY AS GOOD AS THE HORIZON. It measures every cohort against the
    LAST one computed, so on a short run a path still drifting at the end
    reports the end and reads as converged. That is why the chain is run to
    GENERATIONS_LONG and only the figure is truncated.
    """
    n = min(len(tf), len(hf))
    last = n - 1
    k = last
    for i in range(1, n):
        if all(abs(p[j][1] - p[last][1]) <= tol for p in (tf, hf)
               for j in range(i, n)):
            k = i
            break
    return max(k, 1)


def _settle(tf, hf, tol=1e-3):
    """_settle_index as the word the prose uses."""
    k = _settle_index(tf, hf, tol)
    # SPELLED OUT, because the paper spells small numerals in prose.
    word = ('one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
            'nine', 'ten')
    return word[k - 1] if k <= len(word) else str(k)


def numbers(paths, par=None, cg=None):
    """The placeholders Section 3.7 of the paper reads."""
    import json as _json
    here = os.path.dirname(os.path.abspath(__file__))
    par = par or with_(P(), **_json.load(open(os.path.join(here, 'calibrated.json'))))
    tf, hf = paths['TF'], paths['HF']
    d = {'pvbase': f'{par.pV:.3f}',
         'tr_t1_tf': f'{100*tf[1][1]:.2f}',
         'tr_t1_hf': f'{100*hf[1][1]:.2f}',
         'tr_inf_tf': f'{100*tf[-1][1]:.2f}',
         'tr_inf_hf': f'{100*hf[-1][1]:.2f}',
         'tr_sud0': f'{100*(tf[0][2][1]+tf[0][2][3]):.2f}',
         'tr_sudtf': f'{100*(tf[-1][2][1]+tf[-1][2][3]):.2f}',
         'tr_sudhf': f'{100*(hf[-1][2][1]+hf[-1][2][3]):.2f}'}
    # THE DIRECTION WORDS, so the two sentences in Section 3.7 that assert which
    # way the parent generation's disorder rate moves turn when the numbers do.
    # Both are results, and the Housing First one in particular is the sign of a
    # difference between two rest points, not a fact of arithmetic.
    # THE HOMELESSNESS PANEL'S OWN NUMBERS. Panel B was drawn and never read:
    # the prose worked through welfare and the disorder share and left the
    # middle panel to the reader. These are its three points.
    d['tr_hl0'] = f'{100*tf[0][3]:.2f}'
    d['tr_hltf'] = f'{100*tf[-1][3]:.2f}'
    d['tr_hlhf'] = f'{100*hf[-1][3]:.2f}'
    d['tr_hltf_dir'] = _dir(tf[-1][3], tf[0][3], 'rises', 'falls')
    d['tr_hlhf_dir'] = _dir(hf[-1][3], hf[0][3], 'rises', 'falls')
    d['tr_hl_cmp'] = _dir(tf[-1][3], hf[-1][3], 'above', 'below',
                          tol=5e-5, same='level with')
    s0 = tf[0][2][1] + tf[0][2][3]
    d['tr_sudtf_dir'] = _dir(tf[-1][2][1] + tf[-1][2][3], s0, 'rises', 'falls')
    d['tr_sudhf_dir'] = _dir(hf[-1][2][1] + hf[-1][2][3], s0, 'rises', 'falls')
    # WHICH COHORT THE PATHS HAVE SETTLED BY, to a tenth of a point of the rest
    # point, rather than the "two or three" the text used to assert.
    d['tr_settle'] = _settle(tf, hf)
    # HOW MANY COHORTS THE FIGURE ACTUALLY DRAWS, which is not how many were
    # computed. The chain runs to GENERATIONS_LONG so that the settling claim
    # has a horizon behind it; the figure shows the settling cohort plus two.
    d['tr_gens'] = _words(min(max(GENERATIONS_SHOW,
                                  _settle_index(tf, hf) + 2), len(tf) - 1))
    # THE HORIZON THE CLAIM RESTS ON, so the note can say what was computed.
    d['tr_horizon'] = _words(len(tf) - 1)
    # HOW FAR THE LAST TWO COHORTS ARE APART, the honest test that the path has
    # actually stopped moving rather than merely reached the end of the array.
    d['tr_drift'] = f'{100*max(abs(tf[-1][1]-tf[-2][1]), abs(hf[-1][1]-hf[-2][1])):.4f}'
    # THE GENEROSITY MARGIN AGAINST THE CONDITIONALITY MARGIN, on the one
    # cohort that bears the reform. The experiment moves two dials at once:
    # coverage from the observed pi_V to universal, and, under Treatment First,
    # the sobriety condition. Cohort 1's RISE is what the first dial is worth;
    # the GAP between the two policies is what the second one costs. The ratio
    # is the paper's answer to why the two paths are nearly on top of each other
    # at the reform, and it is a result, so it is computed rather than typed.
    _rise = 0.5 * (tf[1][1] + hf[1][1])
    _gap = abs(tf[1][1] - hf[1][1])
    d['tr_gen_rise'] = f'{100*_rise:.2f}'
    # HOW MUCH OF COHORT 2 IS BORN BEHIND AN UNHOUSED PARENT under each policy.
    # Cohort 2's parent is the generation the reform caught mid life, so this is
    # where conditionality's own revocations first reach a child. Cohort 1's
    # parent completed both periods before the condition existed, which is why
    # the two policies hand cohort 1 the SAME mixture and its gap is the private
    # loss alone.
    d['tr_c2_hl_tf'] = f'{100*(tf[2][2][2]+tf[2][2][3]):.3f}'
    d['tr_c2_hl_hf'] = f'{100*(hf[2][2][2]+hf[2][2][3]):.3f}'
    d['tr_c2_hl_dir'] = _dir(tf[2][2][2]+tf[2][2][3], hf[2][2][2]+hf[2][2][3],
                             'more', 'fewer', tol=1e-6, same='as many')
    d['tr_c1_gap'] = f'{100*abs(tf[1][1]-hf[1][1]):.3f}'
    d['tr_c2_gap'] = f'{100*abs(tf[2][1]-hf[2][1]):.3f}'
    # WHICH COHORT THE RANKING FLIPS ON, which is a result and moves with the
    # calibration: the first cohort at which Treatment First is ahead.
    _fl = next((t for t in range(1, len(tf)) if tf[t][1] > hf[t][1]), None)
    d['tr_flip'] = _ordinal(_fl) if _fl else 'no'
    d['tr_t1_gap'] = f'{100*_gap:.2f}'
    d['tr_gen_vs_cond'] = (f'{_rise / _gap:.0f}' if _gap > 1e-9 else 'many')
    # WHICH OF THE TWO THE COHORT AT THE SWITCH PREFERS. The gap is under a
    # tenth of a point, so which way it falls is not robust to a recalibration.
    d['tr_t1_dir'] = _dir(tf[1][1], hf[1][1], 'above', 'below', tol=1e-6,
                          same='level with')
    if cg is not None:
        d['tr_caught_hl'] = f'{100*cg["hl_tf"]:.2f}'
        # EACH POLICY AGAINST THE PRE REFORM WORLD, so the prose can quote the
        # initial old on the same axis the figure now draws them on.
        d['tr_caught_tf'] = f'{100*cg["cev_tf"]:+.1f}'
        d['tr_caught_hf'] = f'{100*cg["cev_hf"]:+.1f}'
        # WHAT CONDITIONALITY TAKES FROM THEM IS THE GAP BETWEEN THE TWO
        # NUMBERS THE FIGURE PLOTS, and it has to be computed that way rather
        # than as cev of the value difference. cev is exp(dv/periods) - 1, so
        # cev(A - B) is not cev(A) - cev(B): the first route reported 2.1 per
        # cent beside a panel showing +10.8 and +8.5, whose difference is 2.3,
        # and a reader checking the figure against the sentence found neither.
        _gap = cg['cev_hf'] - cg['cev_tf']
        d['tr_caught'] = f'{100*_gap:.1f}'
        d['tr_caught_hl_old'] = f'{100*cg["hl_old"]:.2f}'
        _cv = caught_coverage(par, PV_OPT)
        d['tr_cov_old'] = f'{100*_cv["old"]:.1f}'
        d['tr_cov_hf'] = f'{100*_cv["hf"]:.1f}'
        d['tr_cov_tf'] = f'{100*_cv["tf"]:.1f}'
        d['tr_caught_hl_hf'] = f'{100*cg["hl_hf"]:.2f}'
        # HOW MUCH WORSE THE CAUGHT GENERATION HAS IT than the cohort born at
        # the switch. The text called this "two orders of magnitude", which was
        # true of one run and is not a thing to leave typed.
        # BUILT FROM THE SAME GAP THE SENTENCE ABOVE QUOTES, so the two cannot
        # disagree. It used to divide cev of the value difference by the
        # newborns' gap, which is a ratio of two objects measured differently.
        born = abs(tf[1][1] - hf[1][1])
        d['tr_caught_ratio'] = (f'{abs(_gap) / born:.0f}'
                                if born > 1e-9 else 'many')
    out = os.path.join(here, 'transition_numbers.json')
    _json.dump(d, open(out, 'w'), indent=1)
    print('   wrote transition_numbers.json')
    for k, v in d.items():
        print(f'      {k:12s} {v}')
    return d


if __name__ == '__main__':
    paths = run()
    import json as _j, os as _o
    par = with_(P(), **_j.load(open(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)), 'calibrated.json'))))
    cg = caught(par)
    print('\ncaught mid life: loses %.2f%% of consumption; homeless %.3f%% under HF, %.3f%% under TF'
          % (100*cg['cev'], 100*cg['hl_hf'], 100*cg['hl_tf']))
    figure(paths, cg)
    numbers(paths, cg=cg)
