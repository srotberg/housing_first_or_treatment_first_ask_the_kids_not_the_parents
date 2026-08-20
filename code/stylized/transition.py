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
import numpy as np

from stylized import P, with_, value1, use_prob, homeless_prob, ever_homeless_prob
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
    """vals evaluated at income y*s on the grid, interpolated in log income.

    Outside the grid the end values are carried, which is the same convention
    children.shifted uses and matters only for the bottom pool, where the use
    and homelessness probabilities are already flat."""
    return np.interp(LY + np.log(s), LY, vals, left=vals[0], right=vals[-1])


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
    ev = np.array([ever_homeless_prob(q, y, policy) for y in YG], dtype=float)
    prog = stats(q)['prog']
    return (v1, np.clip(use * prog, 0.0, 1.0), np.clip(hl, 0.0, 1.0),
            np.clip(ev, 0.0, 1.0))



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
        ag, _, H2c, _, _ = solve_period2(new, y, new_policy, used=0)
        if new_policy == 'HF':
            H2u = H2c
        else:
            _, _, H2u, _, _ = solve_period2(new, y, new_policy, used=1)
        s_tot = e_tot = 0.0
        for p, gain, v, bu, bn, _inc, _own in period1(old, y, BASE_POLICY):
            uses = gain > 0.0
            a, street1 = (bu if uses else bn)[0], (bu if uses else bn)[1]
            pid = (1.0 - float(np.exp(-old.lam * v))) if uses else 0.0
            Hx = H2u if uses else H2c
            street2 = sum(pd * float(np.interp(a, ag, Hx[:, d]))
                          for d, pd in ((1, pid), (0, 1.0 - pid)))
            s_tot += p * pid
            e_tot += p * (street1 + (1.0 - street1) * street2)
        sud[i] = s_tot
        ev[i] = e_tot
    return np.clip(sud, 0.0, 1.0), np.clip(ev, 0.0, 1.0)


def _shifts():
    return np.array([1.0, 1.0 - DEL_D, 1.0 - DEL_H,
                     (1.0 - DEL_D) * (1.0 - DEL_H)])


def _step(p, sud, hl):
    """One generation. p is the mixture over the four penalty types; the return
    is the mixture the CHILDREN of that cohort are born into.

    The disorder and homelessness are taken as independent given income, which
    is the same reduced form children.py uses: both are functions of the income
    the household was born with, and nothing else links them."""
    out = np.zeros(4)
    for s, ps in zip(_shifts(), p):
        if ps <= 0.0:
            continue
        d = _at(sud, s)
        h = _at(hl, s)
        out[0] += ps * float((WW * (1 - d) * (1 - h)).sum())
        out[1] += ps * float((WW * d * (1 - h)).sum())
        out[2] += ps * float((WW * (1 - d) * h).sum())
        out[3] += ps * float((WW * d * h).sum())
    return out / out.sum()


def _welfare(p, v1):
    """Expected lifetime value of a cohort born into the mixture p."""
    return sum(ps * float((WW * _at(v1, s)).sum())
               for s, ps in zip(_shifts(), p))


def _outcome(p, g):
    """A cohort's own realised rate of something, given the mixture it is born
    into: its homelessness, or its disorder rate. The welfare path says what the
    reform is worth; these say through what."""
    return sum(ps * float((WW * _at(g, s)).sum())
               for s, ps in zip(_shifts(), p))


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
    p_mix = _rest_point(sudb, evb)
    dv = mass = hl_h = hl_t = 0.0
    for sft, psft in zip(_shifts(), p_mix):
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
                agh, W2h, H2h, _, _ = solve_period2(new_h, y, 'HF', used=int(uses))
                agt, W2t, H2t, _, _ = solve_period2(new_t, y, 'TF', used=int(uses))
                for d, pd in ((1, pid), (0, 1.0 - pid)):
                    m = psft * WW[i] * p * pd
                    if m <= 0.0:
                        continue
                    dv += m * (float(np.interp(a, agh, W2h[:, d]))
                               - float(np.interp(a, agt, W2t[:, d])))
                    hl_h += m * float(np.interp(a, agh, H2h[:, d]))
                    hl_t += m * float(np.interp(a, agt, H2t[:, d]))
                    mass += m
    dv /= max(mass, 1e-12)
    return dict(cev=float(cev(par, dv)), hl_hf=hl_h / max(mass, 1e-12),
                hl_tf=hl_t / max(mass, 1e-12))


def _rest_point(sud, hl, iters=400, tol=1e-14):
    p = np.array([1.0, 0.0, 0.0, 0.0])
    for _ in range(iters):
        q = _step(p, sud, hl)
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
    sud_b, ev_b = _bridge_grids(par, policy, pV)
    p = p0.copy()
    for t in range(1, n + 1):
        w = _welfare(p, v1)
        out.append((t, float(cev(par, w - w0)), p.copy(),
                    _outcome(p, hl), _outcome(p, sud)))
        p = _step(p, sud_b, ev_b) if t == 1 else _step(p, sud, ev)
    return out


def run(par=None, n=GENERATIONS):
    here = os.path.dirname(os.path.abspath(__file__))
    par = par or with_(P(), **json.load(open(os.path.join(here, 'calibrated.json'))))

    v1b, sudb, hlb, evb = _policy_grids(par, BASE_POLICY, par.pV)
    p0 = _rest_point(sudb, evb)
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
        ax.set_xlabel('cohort, generations after the reform')
        ax.set_ylabel(ylab)
        ax.set_title(ttl, loc='left', fontsize=11, fontweight='bold')
    axes[0].axhline(0.0, color='0.35', lw=1.0, ls=':')
    if cg is not None:
        # the generation already in period 2 at the switch, on the same axis but
        # marked apart, since it is measured over its remaining period only
        axes[0].plot([0], [-100 * cg['cev']], marker='v', ms=9, color='#b2182b',
                     ls='none',
                     label='caught mid life, Treatment First')
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
    d['tr_flip'] = _words(_fl) if _fl else 'no'
    d['tr_t1_gap'] = f'{100*_gap:.2f}'
    d['tr_gen_vs_cond'] = (f'{_rise / _gap:.0f}' if _gap > 1e-9 else 'many')
    # WHICH OF THE TWO THE COHORT AT THE SWITCH PREFERS. The gap is under a
    # tenth of a point, so which way it falls is not robust to a recalibration.
    d['tr_t1_dir'] = _dir(tf[1][1], hf[1][1], 'above', 'below', tol=1e-6,
                          same='level with')
    if cg is not None:
        d['tr_caught'] = f'{100*cg["cev"]:.1f}'
        d['tr_caught_hl'] = f'{100*cg["hl_tf"]:.2f}'
        # HOW MUCH WORSE THE CAUGHT GENERATION HAS IT than the cohort born at
        # the switch. The text called this "two orders of magnitude", which was
        # true of one run and is not a thing to leave typed.
        born = abs(tf[1][1] - hf[1][1])
        d['tr_caught_ratio'] = (f'{abs(cg["cev"]) / born:.0f}'
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
