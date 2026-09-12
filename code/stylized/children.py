"""
The intergenerational externality: what parental addiction and homelessness do
to a child, and how large the two penalties have to be.

WHY INCOME AND NOT TASTE OR SUSCEPTIBILITY

Two candidate channels were tested first and both fail, for opposite reasons.

    A HERITABLE TASTE, a lower b for the child of a user. This matches the
    target moment, since a lower b means more use. But b enters lifetime value
    only through theta*log(1 + v/b), which is higher at every v > 0 when b is
    lower and zero at v = 0, so the child's whole objective rises pointwise and
    its maximised value rises with it. Measured: V1 goes from 0.866 to 1.017 as
    b falls to a tenth. Inheriting a taste for drugs makes the child BETTER off,
    so the externality has the wrong sign. This is the standard problem with
    treating addiction as a preference.

    A HERITABLE SUSCEPTIBILITY, a higher lam for the child of a user. This has
    the right welfare sign but the wrong behavioural one. Higher lam makes using
    riskier, so the child uses LESS, not more: participation falls from 28.5 per
    cent at lam = 48 to 2.3 percent at lam = 388. It cannot generate
    intergenerational transmission of use at all.

    INCOME works on both counts. Lower permanent income is unambiguously bad to
    receive, and the model already puts drug users at the bottom of the income
    distribution, so a child born poorer is mechanically more likely to use. The
    income gradient the model already generates does the entire job, which means
    the model transmits addiction across generations WITHOUT transmitting any
    preference for drugs. That is the same claim the paper makes within a
    generation, extended across one.

THE SPECIFICATION

A child's baseline income is drawn from the same lognormal as everyone else,
independently of its parent, and the intergenerational link is ONLY the penalty:

    y_child = y_base * (1 - del_d)^{parent had the disorder}
                     * (1 - del_h)^{parent was homeless}

General income persistence is deliberately absent. It is not an externality:
it operates whether or not the parent uses drugs, so it changes the level of
intergenerational correlation without changing what the policy does to it.
Perfect persistence was also tried and is far too strong: parents who use are
all poor, so their children would use with probability near one.

The parent does not internalise any of this. That is what makes it an
externality rather than something already priced into V1.

THE CALIBRATION

    del_d   parental disorder    the ratio of a child's disorder rate to a
                                 child of a clean parent's. Target 2.5, the
                                 middle of the epidemiology: roughly 4x for
                                 children of parents with alcohol use disorder,
                                 lower in the McGovern et al. (2023) meta
                                 analysis of maternal and paternal use.

    del_h   parental homelessness   set from Chetty, Hendren and Katz (2016).
                                 Children moved to a low poverty neighbourhood
                                 before age 13 earned 31 percent more as
                                 adults. That is a housing intervention with
                                 experimental variation, and it is conservative
                                 here: growing up homeless is presumably worse
                                 than growing up in a high poverty
                                 neighbourhood.

Run:  python3 children.py
"""

import json
import numpy as np
from stylized import P, with_, value1, use_prob, terminal_homeless_prob
from calibrate import YG, W, stats
from welfare import cev

WW = W / W.sum()


def child_grid(par, policy, pV):
    """V1, the use indicator and the homelessness indicator on the income grid."""
    q = with_(par, policy=policy, pV=pV)
    v1 = np.array([value1(q, y, policy) for y in YG])
    # the probability of using at that income, over the period 1 employment and
    # voucher draws. It used to be a zero one indicator, which was right when
    # period 1 held no lotteries; now a household at a given income uses in some
    # draws and not in others.
    use = np.array([use_prob(q, y, policy) for y in YG], dtype=float)
    return v1, use


def child_homeless_grid(par, policy, pV):
    """The probability of being on the street in EITHER period, at each income.

    IT USED TO BE PERIOD 1 ALONE, by analogy with the use grid, on the grounds
    that period 1 is where the household's own draws are realised. That reason
    holds for use, since v is only chosen in period 1, and does not hold for
    homelessness: a household can lose its roof in either period, and under
    Treatment First the ones that lose it are exactly those whose voucher is
    withdrawn after they acquire the disorder, which happens at the transition
    into period 2. Keyed on period 1 alone, the homelessness that conditionality
    itself causes could never reach a child, so the channel was switched off by
    a timing assumption rather than by economics."""
    q = with_(par, policy=policy, pV=pV)
    return np.array([terminal_homeless_prob(q, y, policy) for y in YG], dtype=float)


def shifted(vals, delta):
    """
    E[f(y_base * (1-delta))] over the income distribution.

    Interpolation is in LOG income, which is where the grid is evenly spaced.
    Below the grid the value is extrapolated linearly in log y; those states
    carry almost no mass but the drug use indicator there is one, so clipping
    instead would understate the externality.
    """
    ly = np.log(YG)
    return float((WW * np.interp(ly + np.log(1.0 - delta), ly, vals,
                                 left=vals[0], right=vals[-1])).sum())


def transmission(par, policy='HF', pV=None):
    """Child's disorder rate relative to a child of a clean parent, by delta."""
    pV = par.pV if pV is None else pV
    v1, use = child_grid(par, policy, pV)
    m = stats(with_(par, policy=policy, pV=pV))
    prog = m['prog']
    base = shifted(use, 0.0) * prog
    print(f'   child of a clean parent: use {100*shifted(use,0.0):.2f}%'
          f'   disorder {100*base:.3f}%')
    print(f'   {"delta":>8s}{"child use":>12s}{"child disorder":>16s}'
          f'{"ratio":>9s}{"cons. loss":>13s}')
    out = []
    for d in (0.0, 0.10, 0.20, 0.30, DEL_D, 0.50, 0.60, 0.70):
        u = shifted(use, d)
        sud = u * prog
        # welfare damage to the child, in units of one lifetime income
        dv = shifted(v1, 0.0) - shifted(v1, d)
        loss = cev(par, dv)
        out.append((d, u, sud, sud / max(base, 1e-12), loss))
        print(f'   {d:8.2f}{100*u:11.2f}%{100*sud:15.3f}%'
              f'{sud/max(base,1e-12):9.2f}{100*loss:12.2f}%')
    return out


def verdict(par, del_d, pV=1.0, omega=1.0, kids=1.0):
    """
    Does the intergenerational externality reverse the policy ranking?

    Compares the private welfare loss from conditionality with the value of the
    disorder cases it prevents, each case costing one child the income penalty
    del_d for life.
    """
    v1h, _ = child_grid(par, 'HF', pV)
    v1t, _ = child_grid(par, 'TF', pV)
    priv = float((WW * cev(par, v1h - v1t)).sum())
    mh = stats(with_(par, pV=pV, policy='HF'))
    mt = stats(with_(par, pV=pV, policy='TF'))
    dsud = mh['sud'] - mt['sud']
    # THE PER CASE VALUE IS AN AVERAGE OF CEVs, not the CEV of an average, so
    # that it is the same kind of object as priv above and the ratio of the two
    # is like for like. cev is exp(dv/periods) - 1, so the order matters: taking
    # the CEV of the averaged value difference reported 231.8 per cent where
    # averaging each child's own CEV gives 264.3, and the gain over loss ratio
    # moved from 362 to 413 on that alone.
    #
    # WHY A PRODUCT IS EXACT HERE and does not need a separate numerical solve.
    # A child's baseline income is an independent draw from the same lognormal
    # as everyone else, so a spared child's expected value does not depend on
    # WHICH parent was spared, and the per case value is the same number for
    # every case. The child generation's value is then linear in the share of
    # parents carrying the disorder, and the difference between two policies is
    # exactly that share difference times the per case value. The only channel
    # this misses is delta_h, and at universal cover both policies drive
    # homelessness to zero, so it contributes nothing.
    ly = np.log(YG)
    v_pen = np.interp(ly + np.log(1.0 - del_d), ly, v1h,
                      left=v1h[0], right=v1h[-1])
    per_case = float((WW * cev(par, v1h - v_pen)).sum())
    gain = omega * kids * dsud * per_case
    print(f'\n   VERDICT at pi_V = {pV}, del_d = {del_d}, '
          f'{kids} child per household, weight {omega}')
    print(f'      private welfare loss from conditionality : {priv:.5f}')
    print(f'      disorder cases prevented                 : {100*dsud:.3f} pp')
    print(f'      consumption equivalent to the child, one case: {100*per_case:.2f}%')
    print(f'      externality gain from conditionality     : {gain:.5f}')
    print(f'      ratio, gain over loss                    : {gain/max(priv,1e-12):.2f}')
    print(f'      Treatment First preferred?               : {gain > priv}')
    return priv, gain, per_case


# DELTA_D IS CALIBRATED, NOT SET, and it is calibrated to the MIDDLE of the
# epidemiological range rather than to its bottom. McGovern et al. (2023) put the
# child of a parent with a disorder at two to four times the risk of acquiring
# one; delta_d = 0.30 delivered 2.1, which is the bottom of that range while the
# note claimed the middle. It is now solved for the ratio of 3.
#
# The solve is cheap because the ratio does not depend on anything the solve
# moves: shifted() reads the same use grid at a shifted income, so child_grid is
# computed once and the bisection is arithmetic on it. prog cancels out of the
# ratio, so the disorder ratio and the use ratio are the same number.
# TWO, NOT THREE, and the quantitative model's child_sud_ratio_data moved
# with it. Three was the midpoint of a two-to-four range that mixes studies
# of one affected parent with studies of two; a child here has one parent.
# On one-parent estimates the register evidence gives 1.44 (Mellentin et
# al. 2016) and the US population-based study 2.51 (Yoon et al. 2013),
# whose midpoint is 1.98.
RATIO_TARGET = 2.0


# DELTA_H IS CALIBRATED TOO, on the transmission of homelessness, so that both
# channels are quantified inside the model on the same footing rather than one
# matched to a ratio and the other lifted from a coefficient.
#
# THE TARGET IS 2.0 AND THE EVIDENCE FOR IT IS THINNER THAN FOR DELTA_D. There is
# no homelessness counterpart to McGovern et al.'s two to four times. What exists
# runs from a 40 per cent increase in the odds of adult homelessness after a
# single childhood episode (UCSF Benioff Homelessness and Housing Initiative) to
# the much larger ratio implied by the 34 per cent of homeless parents in
# Minnesota who were themselves homeless as children, which depends on a base
# rate the source does not give. Two is inside that range.
#
# THE RATIO IS REPORTED, NOT TARGETED, AND THAT IS THE POINT. An earlier version
# calibrated delta_h on a child homelessness ratio of 2, which was a number with
# no source behind it. The one real measurement, Flatau et al. (2013), reports
# that 43 per cent of non-Indigenous homelessness assistance clients in Australia
# had parents who had themselves experienced homelessness. That cannot be this
# model's target for a structural reason worth recording: it conditions on
# receiving homelessness assistance over a lifetime, while the model's homeless
# are the 0.4 per cent literally on the street at a point in time. Matching 43
# per cent against a parental rate of 0.35 per cent needs a transmission ratio
# near 214. The data moment and the model object are different populations.
#
# Converting Flatau to a ratio needs the share of the population whose parents
# were ever homeless, which the report does not give, and the answer swings with
# it: 14.3 at a base rate of 5 per cent, 4.3 at 15 and 2.3 at 25. So delta_h
# stays external, at the 31 per cent earnings gain Chetty et al. (2016) measure
# directly, and the ratio the model produces at that value is reported as an
# untargeted moment instead. The asymmetry with delta_d is then principled: no
# study measures the parent SUD to child earnings link, so delta_d must be
# calibrated, while the housing to child earnings link IS measured, so delta_h
# need not be.
# DELTA_H IS CALIBRATED, LIKE DELTA_D, AND ON THE SAME KIND OF MOMENT. It used to
# be set from the 31 per cent earnings gain in Chetty et al. (2016), with the
# transmission ratio the model then produced reported as a check. That had the
# dependence backwards. delta_h exists to price the intergenerational transmission
# of homelessness, and Bassuk et al. (1997) measure exactly that: a case control
# study of 220 homeless mothers and 216 low income housed mothers, in which 14.2
# against 8.3 per cent had a primary female caretaker who had been homeless and
# 10.3 against 4.4 a male one, which are odds ratios of 1.80 and 2.41. Both arms
# are poor, so the comparison isolates transmission from the poverty that comes
# with it and needs no population base rate.
#
# Calibrating to the midpoint of those two, 2.1, is what makes delta_h parallel to
# delta_d, which is calibrated to the transmission of ITS own condition. And it
# turns Chetty into an over identifying check rather than the target: the model
# reproduces an earnings penalty it was never shown. That is a stronger claim than
# the agreement the old ordering asserted, since there the two agreed by
# construction.
#
# The honest caveat is that Bassuk is observational and single city where Chetty is
# quasi experimental, so the identification is weaker for the target and stronger
# for the check. The two land within two points of each other either way.
RATIO_H_TARGET = 2.1   # midpoint of Bassuk et al. (1997), 1.80 and 2.41


def solve_del_h(par, target=RATIO_H_TARGET, lo=0.0, hi=0.95, iters=50):
    """The income penalty that puts the child of a homeless parent at `target`
    times the risk of being homeless itself."""
    hl = child_homeless_grid(par, 'HF', par.pV)
    base = shifted(hl, 0.0)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if shifted(hl, mid) / max(base, 1e-12) > target:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def ratio_h(par, del_h=None):
    """The child homelessness ratio the model PRODUCES at delta_h: how much
    likelier the child of a homeless parent is to be homeless itself. Untargeted,
    and reported for validation."""
    hl = child_homeless_grid(par, 'HF', par.pV)
    base = shifted(hl, 0.0)
    return shifted(hl, DEL_H if del_h is None else del_h) / max(base, 1e-12)


def ratio_d(par, del_d=None):
    """The child SUD ratio the model PRODUCES at delta_d: how much likelier the
    child of a user is to use itself. Untargeted now, and reported for
    validation, because the ratio is not reachable through an income channel at
    any earnings penalty the evidence supports."""
    _, use = child_grid(par, 'HF', par.pV)
    base = shifted(use, 0.0)
    return shifted(use, DEL_D if del_d is None else del_d) / max(base, 1e-12)


def solve_del_d(par, target=RATIO_TARGET, lo=0.0, hi=0.95, iters=44):
    """The income penalty that puts the child of a user at `target` times the
    risk of the child of a clean parent."""
    _, use = child_grid(par, 'HF', par.pV)
    base = shifted(use, 0.0)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if shifted(use, mid) / max(base, 1e-12) > target:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
# SET EXTERNALLY, NOT SOLVED, exactly as the quantitative model now sets them.
# These are earnings penalties, and the transmission ratios are not reachable
# through an income channel at any earnings penalty the evidence supports: the
# quantitative model's elasticity of SUD risk to log productivity is 0.73 and
# the data's own gradient is 0.23 to 0.39, so a ratio of 2 needs a 61 to 90 per
# cent earnings cut. DEL_D is Nilsson (2017)'s estimate for children exposed in
# utero to the Swedish alcohol experiment; DEL_H keeps the value it had.
#
# solve_del_d and solve_del_h are kept, because the ratios they invert are now
# reported as untargeted moments and the solvers are how the note computes what
# penalty WOULD be needed.
DEL_D = 0.24
DEL_H = 0.31

# What the externally set penalties actually deliver, for the untargeted table.
#
# LAZY, AND AT THE CALLER'S VECTOR.  These were computed AT IMPORT from
# `_BASE = with_(P(), **json.load(open('calibrated.json')))`, so importing this
# module solved a model straight off disk.  That file is dated 27 August and is
# a DIFFERENT MODEL: it carries lam = 106.8, the susceptibility parameter from
# before the hazard was flattened and which this module's own docstring records
# as a rejected channel; aleph 2.86 against a current 10.62; and no pi_base,
# omega, kap, u0 or u1 at all.  It is gitignored, so its contents are not even
# in the repository.
#
# transition.py imports this module, so the whole cohort chain inherited that
# vector.  A transition table was reported to the author on numbers computed
# there rather than at the vector passed in, and had to be withdrawn.
#
# Both were computed at import and read by NOTHING -- no other module in the
# package references either name -- so the stale solve was pure dead weight.
# They are functions now, they take the vector they are asked about, and
# importing this module no longer solves anything.
def ratio_d_model(par):
    return ratio_d(par)


def ratio_h_model(par):
    return ratio_h(par)


def tab_children(par, pV=1.0):
    """The intergenerational table for the note."""
    import os
    from tables import OUT
    # PANEL A IS CALIBRATED AT THE BASELINE POLICY, not at universal cover:
    # the transmission ratio in the data comes from the world as it is, with a
    # rationed programme, so that is where del_d has to be matched.
    v1, use = child_grid(par, 'HF', par.pV)
    m = stats(with_(par, policy='HF', pV=par.pV))
    prog = m['prog']
    base = shifted(use, 0.0) * prog
    rows = []
    # SORTED, because the calibrated value is inserted among fixed ones and
    # lands wherever it falls. At del_d = 0.61 the panel read 0.00, 0.20, 0.61
    # (calibrated), 0.60, which invites the reader to check a ratio that is not
    # monotone down the column when in fact it is.
    for d in sorted({0.0, 0.20, DEL_D, 0.60}):
        u = shifted(use, d)
        rows.append((d, u * prog, u * prog / max(base, 1e-12),
                     cev(par, shifted(v1, 0.0) - shifted(v1, d))))
    # PER CASE COMES FROM verdict(), NOT FROM A SECOND CALCULATION HERE. It used
    # to be recomputed on this line as cev of the averaged value difference,
    # while the gain below came from verdict() using the average of individual
    # equivalents. The panel then printed a per case figure and a gain that were
    # not the same object, and its own arithmetic did not check out: 9.489
    # points at 101.9 per cent each multiplies to 9.67, against a printed gain
    # of 11.158.
    priv, gain, per_case = verdict(par, DEL_D, pV=pV)
    # WHERE THE NUMBER COMES FROM, because it is large enough to want checking.
    # A permanent income cut of del_d costs a household with log utility exactly
    # log(1-del_d) of flow utility in every period, so the consumption equivalent
    # of the INCOME alone is (1-del_d)^-1 - 1 with no behaviour in it at all. The
    # gap between that and per_case is the behavioural response: the poorer child
    # uses more, is likelier to lose its housing and likelier to acquire the
    # disorder, and each of those costs it again.
    income_only = 1.0 / (1.0 - DEL_D) - 1.0
    print(f'\n   PER CASE, decomposed at del_d = {DEL_D:.4f}')
    print(f'      consumption equivalent, total          : {100*per_case:.1f}%')
    print(f'      of which the income cut alone          : {100*income_only:.1f}%')
    print(f'      of which the behavioural response      : '
          f'{100*(per_case-income_only):.1f}%')
    # Panel B is entirely at pV, the policy comparison. Panel A is entirely at
    # the baseline. Mixing the two silently reported a 1.68 pp gap where the
    # universal cover gap is 0.25.
    mhu = stats(with_(par, pV=pV, policy='HF'))
    mtu = stats(with_(par, pV=pV, policy='TF'))
    dsud = mhu['sud'] - mtu['sud']

    L = [r'\footnotesize', r'\begin{tabular}{@{}lcccc@{}}', r'\toprule',
         r'\multicolumn{5}{@{}l}{\emph{Panel A. Transmission: what each income '
         r'penalty implies}} \\',
         r"$\delta_d$ & & Child's SUD rate & Ratio & "
         r'CEV \\', r'\midrule']
    R = lambda x: x
    for d, sud, ratio, loss in rows:
        # NOT "(calibrated)". delta_d is set from Nilsson (2017), not solved
        # for a transmission ratio, so the row that carries it is the baseline
        # of the panel rather than the fitted one. The old label survived the
        # change that made the penalty external and said the opposite of what
        # the model now does.
        lab = f'{d:.2f}' + (r'\ \ (baseline)' if abs(d - DEL_D) < 1e-9 else '')
        L.append(f'{lab} & & {R(f"{100*sud:.2f}")}\\% & {R(f"{ratio:.2f}")} '
                 f'& {R(f"{100*loss:.1f}")}\\% \\\\')
    L += [r'\addlinespace',
          r'\multicolumn{5}{@{}l}{\emph{Panel B. Does the externality reverse '
          r'the ranking?}} \\',
          f'\\quad Private cost of conditionality & & & & '
          f'{R(f"{100*priv:.3f}")}\\% \\\\',
          f'\\quad Disorder cases prevented & & & & {R(f"{100*dsud:.3f}")} pp \\\\',
          f'\\quad CEV to the child, one case & & & & '
          # ONE DECIMAL, so the panel's arithmetic can be checked from the
          # panel. At a whole percent the row read 9.209 points at 197 per
          # cent each, which multiplies to 18.14 against a printed gain of
          # 18.119: the true figure is 196.75 and the rounding hid it.
          f'{R(f"{100*per_case:.1f}")}\\% \\\\',
          f'\\quad Externality gain from conditionality & & & & '
          f'{R(f"{100*gain:.3f}")}\\% \\\\',
          f'\\quad Gain over loss & & & & {R(f"{gain/max(priv,1e-12):.1f}")} \\\\',
          r'\bottomrule', r'\end{tabular}']
    from tablered import mark
    with open(os.path.join(OUT, 'tab_children.tex'), 'w') as f:
        f.write(mark('tab_children.tex', '\n'.join(L) + '\n'))
    print('   wrote tab_children.tex')

    # AND THE SAME NUMBERS FOR THE PROSE, for the reason set out in welfare.py:
    # the paragraph beside a table quotes that table's cells rather than a second
    # computation of them. The smallest gain-over-loss ratio anywhere in Panel A
    # other than at the zero penalty is here too, because the sentence that says
    # the ranking survives every penalty shown is an assertion about this panel
    # and has to break loudly if it stops being true.
    import json as _json
    ratios = []
    for d in sorted({0.20, DEL_D, 0.60}):
        # the calibrated penalty has already been solved a few lines above, so
        # it is reused rather than solved again: verdict() is minutes, not
        # milliseconds.
        p_, g = ((priv, gain) if abs(d - DEL_D) < 1e-12
                 else verdict(par, d, pV=pV)[:2])
        ratios.append(g / max(p_, 1e-12))
    here = os.path.dirname(os.path.abspath(__file__))
    dd = {'priv': f'{100 * priv:.3f}',
          'dsud': f'{100 * dsud:.3f}',
          'percase': f'{100 * per_case:.1f}',
          'gain': f'{100 * gain:.3f}',
          'ratiogl': f'{gain / max(priv, 1e-12):.1f}',
          'ratiomin': f'{min(ratios):.0f}',
          'ratiominword': 'exceeds' if min(ratios) > 1.0 else 'does not exceed'}
    with open(os.path.join(here, 'children_numbers.json'), 'w') as f:
        _json.dump(dd, f, indent=1)
    print('   wrote children_numbers.json')


if __name__ == '__main__':
    base = with_(P(), **json.load(open('calibrated.json')))
    print('=' * 76)
    print('THE INTERGENERATIONAL EXTERNALITY')
    print('=' * 76)
    print('\nTRANSMISSION: how large must the income penalty be?')
    transmission(base)
    for d in (0.20, 0.30, 0.40):
        verdict(base, d)
    print()
    tab_children(base)
