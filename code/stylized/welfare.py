"""
Welfare, qualitatively. Can Treatment First ever be the better policy here?

THE QUESTION

Households in this model are forward looking, face the true addiction hazard,
and make no mistakes. Drug use creates no externality, there is no government
budget constraint, and there is no equilibrium price. In an environment like
that, conditioning assistance on abstinence has nothing obvious to recommend
it, and the point of this file is to check whether that intuition is exactly
right or only roughly right.

THE ARGUMENT, BEFORE ANY ARITHMETIC

At the same generosity pi_V, Housing First pays the voucher in a strict superset
of the states in which Treatment First pays it: both pay when d = 0, only
Housing First pays when d = 1. So under Housing First the household's budget set
is weakly larger in every state and strictly larger in one. A household that
optimises therefore cannot be worse off, and is strictly better off whenever it
faces any chance of the disorder.

    V1(y; HF, pi_V)  >=  V1(y; TF, pi_V)     for every y, with equality only
                                             for households that never use

That is a dominance result, not a numerical one. It does not depend on the
calibration and it cannot be overturned by choosing different parameters. The
extra drug use under Housing First is not a distortion to be corrected: it is
the household optimally taking a risk it is now better able to bear. Calling it
moral hazard describes the behaviour correctly and its welfare content wrongly.

WHERE THAT LEAVES CONDITIONALITY

The comparison above holds generosity fixed, which is the wrong comparison if
vouchers have to be paid for. The obvious conjecture is that Housing First buys
the same coverage at a higher price, because it pays for households in the
disorder state and, by insuring that state, puts more households into it. A
fixed budget would then buy more coverage under Treatment First, and that would
be the one channel in this model favouring conditionality.

THAT CONJECTURE IS WRONG HERE, and the arithmetic below says so. Treatment First
is very slightly MORE expensive than Housing First at every generosity, 0.18077
against 0.18061 at universal cover. The reason is mortality. A household in the
disorder state draws only about 79 per cent of the voucher outlay a clean
household draws, at every income level, and it is not because it houses itself
worse: under universal cover nobody is on the street. It is because survival to
period 3 falls from 0.93 to 0.51, so the programme pays for it over fewer
periods. The households the moral hazard adds to the rolls die sooner and stop
costing money, which offsets the cost of covering them.

So within this model conditionality has nothing to recommend it at all. The case
for it has to rest on things this model does not contain: externalities from
drug use, internalities from present bias or from a household underestimating
the hazard, and public costs outside housing, which is where the fiscal argument
really lives. The last of these matters most for reading the result honestly:
the budget here is housing vouchers and nothing else, and healthcare, treatment
and incarceration all rise with the disorder.

Run:  python3 welfare.py
"""

import json
import numpy as np
from stylized import P, with_, value1
from calibrate import YG, W, stats
from tables import OUT


def v1_pop(par, policy, pV):
    """V1 at every income node under a given policy and generosity."""
    q = with_(par, policy=policy, pV=pV)
    return np.array([value1(q, y, policy) for y in YG])


# Expected discounted periods lived by a clean household, used to turn a
# difference in lifetime utility into a consumption equivalent. Log utility
# means scaling consumption by (1+lam) in every period and state adds
# K*log(1+lam) to lifetime value, so lam = exp(dV/K) - 1.
def periods(par):
    return 1.0 + par.beta * par.phi0 + par.beta**2 * par.phi0**2


def cev(par, dv):
    """
    Consumption equivalent of a difference in lifetime value: the proportional
    change in consumption, in every period and state, worth the same as dv.

    A compensating variation in PERMANENT INCOME was tried first and abandoned.
    The voucher is means tested at y_V, so V1 jumps down as income crosses the
    threshold and a household just above it is worse off than one just below.
    V1 is therefore not monotone in y, and bisecting on income lands on spurious
    roots: at y = 0.94 it reported a 9.8 per cent income equivalent between two
    policies whose values agree to eight decimals. The notch is a real feature
    of a means tested benefit and it stays in the model; it just cannot be used
    as a measuring rod.
    """
    return np.exp(dv / periods(par)) - 1.0


def equal_generosity(par, pV=1.0):
    """Both policies at the same pi_V. The dominance result should show up."""
    ww = W / W.sum()
    vh = v1_pop(par, 'HF', pV)
    vt = v1_pop(par, 'TF', pV)
    lam = cev(par, vh - vt)          # consumption a household would give up
    print(f'\nEQUAL GENEROSITY, pi_V = {pV}')
    print(f"   {'income':>10s}{'weight':>9s}{'V1 under HF':>14s}"
          f"{'V1 under TF':>14s}{'cons equiv':>12s}")
    for i, y in enumerate(YG):
        if i % 3 == 0 or lam[i] > 1e-6:
            print(f'   {y:10.3f}{ww[i]:9.4f}{vh[i]:14.5f}{vt[i]:14.5f}'
                  f'{100*lam[i]:11.3f}%')
    worse = float((ww * (vt < vh - 1e-9)).sum())
    hit = lam > 1e-6
    print(f'   population average consumption equivalent : '
          f'{100*(ww*lam).sum():.4f}%')
    print(f'   average among households that are affected : '
          f'{100*(ww*lam)[hit].sum()/max(ww[hit].sum(),1e-12):.4f}%')
    print(f'   share of households strictly worse off under TF : {worse:.4f}')
    print(f'   any household better off under TF? '
          f'{bool((vt > vh + 1e-9).any())}')
    return lam, vh, vt


def cost_curve(par, policy, grid):
    out = []
    for p in grid:
        m = stats(with_(par, pV=p, policy=policy))
        out.append((p, m['cost'], m['part']))
        print(f'   {policy}  pi_V {p:5.2f}   cost {m["cost"]:.5f}   '
              f'participation {100*m["part"]:6.3f}%')
    return out


def equal_cost(par, pV_hf=1.0):
    """
    Match Treatment First's cost to Housing First's, then compare welfare.
    Treatment First is cheaper at any given pi_V, so it can be run at a higher
    one for the same money.
    """
    ww = W / W.sum()
    target = stats(with_(par, pV=pV_hf, policy='HF'))['cost']
    print(f'\nEQUAL COST')
    print(f'   Housing First at pi_V = {pV_hf} costs {target:.5f}')

    # Treatment First is cheaper, so its matching pi_V is above pV_hf. It may
    # not exist: if TF at pi_V = 1 still costs less, the budget cannot be spent.
    top = stats(with_(par, pV=1.0, policy='TF'))['cost']
    print(f'   Treatment First at pi_V = 1.0 costs {top:.5f}')
    if top < target:
        print('   Treatment First cannot spend the budget even at universal '
              'cover.')
        pv_tf = 1.0
    else:
        lo, hi = 0.0, 1.0
        for _ in range(24):
            mid = 0.5 * (lo + hi)
            if stats(with_(par, pV=mid, policy='TF'))['cost'] < target:
                lo = mid
            else:
                hi = mid
        pv_tf = 0.5 * (lo + hi)
        print(f'   Treatment First matches that cost at pi_V = {pv_tf:.4f}')

    vh = v1_pop(par, 'HF', pV_hf)
    vt = v1_pop(par, 'TF', pv_tf)
    lam = cev(par, vh - vt)
    print(f'   population average consumption equivalent of TF at equal cost : '
          f'{100*(ww*lam).sum():.4f}%')
    print(f'   share strictly better off under TF : '
          f'{float((ww * (vt > vh + 1e-9)).sum()):.4f}')
    ph = 100 * stats(with_(par, pV=pV_hf, policy='HF'))['part']
    pt = 100 * stats(with_(par, pV=pv_tf, policy='TF'))['part']
    print(f'   participation   HF {ph:.3f}%   TF {pt:.3f}%')
    return pv_tf, lam


def balanced_tax(par, policy, pV, iters=25):
    """
    The proportional income tax that pays for the programme, policy by policy.

    Income here is exogenous, so a proportional tax on it is not distortionary
    in the usual sense; it still matters, because it takes resources from the
    same households the vouchers are given to, and because it changes what a
    poor household can afford in the states where housing is at stake.
    """
    q = with_(par, policy=policy, pV=pV, tau=0.0)
    t = 0.0
    for _ in range(iters):
        m = stats(with_(q, tau=t))
        new = m['cost'] / m['tax_base']
        if abs(new - t) < 1e-6:
            t = new
            break
        t = 0.5 * t + 0.5 * new          # damped, the map is close to linear
    return t


def financed(par, pV=1.0):
    """Both policies with their own budgets balanced. Does the ranking move?"""
    ww = W / W.sum()
    th = balanced_tax(par, 'HF', pV)
    tt = balanced_tax(par, 'TF', pV)
    print(f'\nBALANCED BUDGET, pi_V = {pV}')
    print(f'   tax rate that pays for Housing First   : {100*th:.3f}%')
    print(f'   tax rate that pays for Treatment First : {100*tt:.3f}%')
    vh = v1_pop(with_(par, tau=th), 'HF', pV)
    vt = v1_pop(with_(par, tau=tt), 'TF', pV)
    lam = cev(par, vh - vt)
    print(f'   population average consumption equivalent of TF : '
          f'{100*float((ww*lam).sum()):.4f}%')
    print(f'   share strictly worse off under TF  : '
          f'{float((ww * (vt < vh - 1e-9)).sum()):.4f}')
    print(f'   share strictly better off under TF : '
          f'{float((ww * (vt > vh + 1e-9)).sum()):.4f}')
    return th, tt, lam


def critical_externality(par, pV=1.0, tau_h=0.0, tau_t=0.0):
    """
    How large must the social cost of a case of the disorder be before
    Treatment First is the better policy?

    The externality is deliberately kept OUT of the household's problem: that is
    what makes it an externality. It enters only the planner's objective, as a
    cost chi per household in the disorder state, measured in units of a
    household's lifetime income. The critical chi is the one at which the
    private welfare loss from conditionality is exactly offset by the disorder
    cases it avoids.
    """
    ww = W / W.sum()
    mh = stats(with_(par, pV=pV, policy='HF', tau=tau_h))
    mt = stats(with_(par, pV=pV, policy='TF', tau=tau_t))
    vh = v1_pop(with_(par, tau=tau_h), 'HF', pV)
    vt = v1_pop(with_(par, tau=tau_t), 'TF', pV)
    lam = float((ww * cev(par, vh - vt)).sum())      # consumption households lose
    scale = mh['tax_base']                           # lifetime income per household
    loss = lam * scale                               # in units of income
    d_sud = mh['sud'] - mt['sud']                    # disorder cases avoided
    chi = loss / max(d_sud, 1e-12)
    print(f'\nCRITICAL EXTERNALITY, pi_V = {pV}')
    print(f'   households with the disorder   HF {100*mh["sud"]:.3f}%'
          f'   TF {100*mt["sud"]:.3f}%')
    print(f'   cases avoided by conditionality : {100*d_sud:.3f} pp')
    print(f'   private welfare loss, consumption equivalent : {100*lam:.4f}%')
    print(f'   lifetime income per household : {scale:.4f}')
    print(f'   critical chi : {chi:.4f} of one household\'s lifetime income')
    print(f'                  per additional case of the disorder')
    return chi, d_sud, lam


def tab_welfare(par, pV=1.0):
    """The welfare table for the note, written straight to LaTeX."""
    import os
    ww = W / W.sum()
    mh = stats(with_(par, pV=pV, policy='HF'))
    mt = stats(with_(par, pV=pV, policy='TF'))
    vh = v1_pop(par, 'HF', pV)
    vt = v1_pop(par, 'TF', pV)
    lam = cev(par, vh - vt)
    hit = lam > 1e-6
    worse = float((ww * (vt < vh - 1e-9)).sum())
    better = float((ww * (vt > vh + 1e-9)).sum())
    avg = float((ww * lam).sum())
    among = float((ww * lam)[hit].sum() / max(ww[hit].sum(), 1e-12))

    th = balanced_tax(par, 'HF', pV)
    tt = balanced_tax(par, 'TF', pV)
    chi0, dsud0, _ = critical_externality(par, pV)
    chi1, dsud1, lam1 = critical_externality(par, pV, th, tt)

    pc = lambda x, n=2: f'{x:.{n}f}\\%'
    L = [r'\small', r'\begin{tabular}{@{}lcc@{}}', r'\toprule',
         r'& Housing First & Treatment First \\', r'\midrule',
         r'\multicolumn{3}{@{}l}{\emph{Panel A. Outcomes at universal cover}} \\',
         f'\\quad Drug participation rate & {pc(100*mh["part"])} '
         f'& {pc(100*mt["part"])} \\\\',
         f'\\quad Share with the disorder & {pc(100*mh["sud"],3)} '
         f'& {pc(100*mt["sud"],3)} \\\\',
         f'\\quad Homelessness rate & {pc(100*mh["homeless"],3)} '
         f'& {pc(100*mt["homeless"],3)} \\\\',
         f'\\quad Voucher outlay per household & {mh["cost"]:.4f} '
         f'& {mt["cost"]:.4f} \\\\',
         f'\\quad Tax rate that pays for it & {pc(100*th)} & {pc(100*tt)} \\\\',
         r'\addlinespace',
         r'\multicolumn{3}{@{}l}{\emph{Panel B. Treatment First against Housing '
         r'First, no externality}} \\',
         f'\\quad Households strictly worse off & & {pc(100*worse,1)} \\\\',
         f'\\quad Households strictly better off & & {pc(100*better,1)} \\\\',
         f'\\quad Consumption equivalent loss, those affected & '
         f'& {pc(100*among)} \\\\',
         f'\\quad Consumption equivalent loss, whole population & '
         f'& {pc(100*avg,3)} \\\\',
         f'\\quad \\emph{{the same, with the budget balanced}} & '
         f'& {pc(100*lam1,3)} \\\\',
         r'\addlinespace',
         r'\multicolumn{3}{@{}l}{\emph{Panel C. How large an externality would '
         r'reverse this}} \\',
         f'\\quad Disorder cases avoided by conditionality & '
         f'& {100*dsud1:.3f} pp \\\\',
         f'\\quad Critical social cost per case, no financing & '
         f'& {chi0:.2f} \\\\',
         f'\\quad Critical social cost per case, budget balanced & '
         f'& {chi1:.2f} \\\\',
         r'\bottomrule', r'\end{tabular}']
    with open(os.path.join(OUT, 'tab_welfare.tex'), 'w') as f:
        f.write('\n'.join(L) + '\n')
    print('   wrote tab_welfare.tex')


if __name__ == '__main__':
    base = with_(P(), **json.load(open('calibrated.json')))
    print('=' * 74)
    print('WELFARE IN THE STYLIZED MODEL')
    print('=' * 74)
    equal_generosity(base, 1.0)
    print('\nPROGRAMME COST, expected present value per household')
    cost_curve(base, 'HF', [0.25, 0.5, 0.75, 1.0])
    cost_curve(base, 'TF', [0.25, 0.5, 0.75, 1.0])
    equal_cost(base, 1.0)
    print()
    th, tt, _ = financed(base, 1.0)
    critical_externality(base, 1.0)
    critical_externality(base, 1.0, th, tt)
    tab_welfare(base, 1.0)
