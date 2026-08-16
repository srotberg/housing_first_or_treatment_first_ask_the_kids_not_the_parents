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
    cent at lam = 48 to 2.3 per cent at lam = 388. It cannot generate
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
                                 before age 13 earned 31 per cent more as
                                 adults. That is a housing intervention with
                                 experimental variation, and it is conservative
                                 here: growing up homeless is presumably worse
                                 than growing up in a high poverty
                                 neighbourhood.

Run:  python3 children.py
"""

import json
import numpy as np
from stylized import P, with_, value1, use_prob
from calibrate import YG, W, stats
from welfare import cev

WW = W / W.sum()


def child_grid(par, policy, pV):
    """V1 and the use indicator on the income grid, for interpolation."""
    q = with_(par, policy=policy, pV=pV)
    v1 = np.array([value1(q, y, policy) for y in YG])
    # the probability of using at that income, over the period 1 employment and
    # voucher draws. It used to be a zero one indicator, which was right when
    # period 1 held no lotteries; now a household at a given income uses in some
    # draws and not in others.
    use = np.array([use_prob(q, y, policy) for y in YG], dtype=float)
    return v1, use


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
    for d in (0.0, 0.10, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50):
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
    per_case = cev(par, shifted(v1h, 0.0) - shifted(v1h, del_d))
    gain = omega * kids * dsud * per_case
    print(f'\n   VERDICT at pi_V = {pV}, del_d = {del_d}, '
          f'{kids} child per household, weight {omega}')
    print(f'      private welfare loss from conditionality : {priv:.5f}')
    print(f'      disorder cases prevented                 : {100*dsud:.3f} pp')
    print(f'      damage per case, one child               : {100*per_case:.2f}%')
    print(f'      externality gain from conditionality     : {gain:.5f}')
    print(f'      ratio, gain over loss                    : {gain/max(priv,1e-12):.2f}')
    print(f'      Treatment First preferred?               : {gain > priv}')
    return priv, gain


DEL_D = 0.30      # parental disorder, from the transmission ratio
DEL_H = 0.31      # parental homelessness, from Chetty, Hendren and Katz (2016)


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
    for d in (0.0, 0.20, DEL_D, 0.40):
        u = shifted(use, d)
        rows.append((d, u * prog, u * prog / max(base, 1e-12),
                     cev(par, shifted(v1, 0.0) - shifted(v1, d))))
    v1u, _ = child_grid(par, 'HF', pV)
    per_case = cev(par, shifted(v1u, 0.0) - shifted(v1u, DEL_D))
    priv, gain = verdict(par, DEL_D, pV=pV)
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
         r'Loss to the child \\', r'\midrule']
    for d, sud, ratio, loss in rows:
        lab = f'{d:.2f}' + (r'\ \ (calibrated)' if abs(d - DEL_D) < 1e-9 else '')
        L.append(f'{lab} & & {100*sud:.2f}\\% & {ratio:.2f} & {100*loss:.1f}\\% \\\\')
    L += [r'\addlinespace',
          r'\multicolumn{5}{@{}l}{\emph{Panel B. Does the externality reverse '
          r'the ranking?}} \\',
          f'\\quad Private welfare loss from conditionality & & & & '
          f'{100*priv:.3f}\\% \\\\',
          f'\\quad Disorder cases prevented & & & & {100*dsud:.3f} pp \\\\',
          f'\\quad Damage to the child of one such case & & & & '
          f'{100*per_case:.0f}\\% \\\\',
          f'\\quad Externality gain from conditionality & & & & '
          f'{100*gain:.3f}\\% \\\\',
          f'\\quad Gain over loss & & & & {gain/max(priv,1e-12):.1f} \\\\',
          r'\bottomrule', r'\end{tabular}']
    with open(os.path.join(OUT, 'tab_children.tex'), 'w') as f:
        f.write('\n'.join(L) + '\n')
    print('   wrote tab_children.tex')


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
