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

The comparison above holds generosity fixed. Holding COST fixed instead changes
nothing, and that is worth knowing rather than assuming: the obvious conjecture
is that Housing First buys the same coverage at a higher price, because it pays
for households in the disorder state and, by insuring that state, puts more
households into it. The conjecture is false here. Treatment First is very
slightly MORE expensive at every generosity, and the reason is mortality. A
household in the disorder state draws only about 79 percent of the voucher
outlay a clean household draws, at every income level, because survival to
period 2 falls by the mortality penalty and the programme pays for it in fewer
states. The households the moral hazard adds to the rolls die sooner and stop
costing money.

A financing side was built here and removed. A proportional income tax balancing
each policy's budget separately came to 7.45 percent under Housing First and
7.46 under Treatment First, so it changed the ranking not at all, for the same
equal cost reason. It is gone because this model is for intuition and a
government that provably does nothing is machinery a reader has to carry for no
return.

So within this model conditionality has nothing to recommend it. What is left is
an EXTERNALITY, and the one thing this file can usefully do is say how large it
would have to be. That is what critical_externality computes.

Run:  python3 welfare.py
"""

import json
import numpy as np
from stylized import P, with_, value1
from calibrate import YG, W, stats
from tables import OUT

# Present value of income for a household at the mean, used only to express the
# critical externality in units a reader can weigh: period 1 earnings plus
# period 2 discounted at R and weighted by survival.
PV_INCOME = 1.0 + P.phi0 / P.R


def v1_pop(par, policy, pV):
    """V1 at every income node under a given policy and generosity."""
    q = with_(par, policy=policy, pV=pV)
    return np.array([value1(q, y, policy) for y in YG])


# Expected discounted periods lived by a clean household, used to turn a
# difference in lifetime utility into a consumption equivalent. Log utility
# means scaling consumption by (1+lam) in every period and state adds
# K*(1-gam-th)*log(1+lam) to lifetime value, so lam = exp(dV/K) - 1 with the
# weight on consumption carried in K. Two periods, the second reached only on
# survival.
def periods(par):
    """The LOG-utility coefficient, kept only so cev_log_old can reproduce what
    this module used to return.  It is wrong twice at sigma = 2: it is the log
    formula, and it uses 1 - gam - th where the consumption share is
    phi_c = (1 - gam)(1 - th).  Those differ by gam*th, 17 per cent at the
    calibrated values."""
    return (1.0 - par.gam - par.th) * (1.0 + par.beta * par.phi0)


def cev(par, dv, v_level=None, pi=0.0):
    """
    Consumption equivalent of a difference in lifetime value: the proportional
    change in consumption, in every period and state, worth the same as dv.

    v_level IS REQUIRED AT SIGMA != 1 AND THE FUNCTION RAISES WITHOUT IT.  Under
    CRRA, scaling consumption by (1+lam) scales BOTH bundles by (1+lam)^phi_c --
    X_P and X_K each carry c/xi with exponent phi_c -- so every
    X^(1-sigma)/(1-sigma) term scales by (1+lam)^(phi_c(1-sigma)) while the
    aleph terms do not move:

        V(lam) = (1+lam)^(phi_c(1-sigma)) * U + A ,   U = V - A
        lam    = (1 + dv/U)^(1/(phi_c(1-sigma))) - 1

    The answer depends on the LEVEL of V through U, which the log formula never
    did, and aleph at 10.6 per period is most of V.  So a caller that has only a
    difference cannot get a right answer, and RAISING is the point: this
    function returned a silently wrong number -- always too large, by an order
    of magnitude at small differences and by two at large ones -- at seventeen
    call sites for as long as sigma has been 2.  Measured, on identical dv:
    1.52 against 16.37 per cent, 7.57 against 106.46, 15.11 against 296.03,
    37.61 against 1906.47.

    Verified against _flow itself in child_welfare.py: the scaling property
    holds to 2.7e-16 and an applied lambda is recovered to 1e-14.

    A COMPENSATING VARIATION IN PERMANENT INCOME was tried first and abandoned.
    The voucher is means tested at y_V, so V1 jumps down as income crosses the
    threshold and a household just above it is worse off than one just below.
    V1 is therefore not monotone in y, and bisecting on income lands on spurious
    roots: at y = 0.94 it reported a 9.8 percent income equivalent between two
    policies whose values agree to eight decimals. The notch is a real feature
    of a means tested benefit and it stays in the model; it just cannot be used
    as a measuring rod.
    """
    if abs(par.sigma - 1.0) < 1e-12:
        return np.exp(dv / periods(par)) - 1.0
    if v_level is None:
        raise TypeError(
            "cev() needs the LEVEL of lifetime value as well as the difference "
            "when sigma != 1: the CRRA answer depends on where you start. "
            "Pass v_level (and pi, the onset probability, if it is not zero). "
            "See child_welfare.cev for the derivation and its verification.")
    phc = (1.0 - par.gam) * (1.0 - par.th)
    e = phc * (1.0 - par.sigma)
    s0 = par.phi0
    s1 = par.phi0 * (1.0 - par.kap)
    A = par.aleph * (1.0 + par.beta * ((1.0 - pi) * s0 + pi * s1))
    U = np.asarray(v_level, dtype=float) - A
    return np.power(1.0 + np.asarray(dv, dtype=float) / U, 1.0 / e) - 1.0


def cev_log_old(par, dv):
    """What this module returned before the sigma = 2 correction, kept so the
    two can be compared rather than the old numbers quietly vanishing."""
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


def critical_externality(par, pV=1.0):
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
    mh = stats(with_(par, pV=pV, policy='HF'))
    mt = stats(with_(par, pV=pV, policy='TF'))
    vh = v1_pop(par, 'HF', pV)
    vt = v1_pop(par, 'TF', pV)
    lam = float((ww * cev(par, vh - vt)).sum())      # consumption households lose
    scale = 1.0
    loss = lam
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


    # every cell in this table is a model output and every one of them moved
    pc = lambda x, n=2: '' + f'{x:.{n}f}' + '\\%'
    L = [r'\small', r'\begin{tabular}{@{}lcc@{}}', r'\toprule',
         r'& Housing First & Treatment First \\', r'\midrule',
         r'\multicolumn{3}{@{}l}{\emph{Panel A. Outcomes at universal cover}} \\',
         f'\\quad Drug participation rate & {pc(100*mh["part"])} '
         f'& {pc(100*mt["part"])} \\\\',
         f'\\quad Share with a SUD & {pc(100*mh["sud"],3)} '
         f'& {pc(100*mt["sud"],3)} \\\\',
         f'\\quad Homelessness rate & {pc(100*mh["homeless"],3)} '
         f'& {pc(100*mt["homeless"],3)} \\\\',
         f'\\quad Voucher outlay per household '
         f'& {mh["cost"]:.4f} '
         f'& {mt["cost"]:.4f} \\\\',
         r'\addlinespace',
         r'\multicolumn{3}{@{}l}{\emph{Panel B. Treatment First against Housing '
         r'First, no externality}} \\',
         f'\\quad Households strictly worse off & & {pc(100*worse,1)} \\\\',
         f'\\quad Households strictly better off & & {pc(100*better,1)} \\\\',
         f'\\quad CEV, those affected & '
         f'& {pc(100*among)} \\\\',
         f'\\quad CEV, whole population & '
         f'& {pc(100*avg,3)} \\\\',
         r'\bottomrule', r'\end{tabular}']
    from tablered import mark
    with open(os.path.join(OUT, 'tab_welfare.tex'), 'w') as f:
        f.write(mark('tab_welfare.tex', '\n'.join(L) + '\n'))
    print('   wrote tab_welfare.tex')

    # AND THE SAME NUMBERS FOR THE PROSE. Every one of these is a cell of the
    # table above, and fill.py used to compute each of them a second time. Two
    # computations of one number are two numbers: they agree until one of the
    # two code paths changes, and then the sentence contradicts the table it is
    # pointing at. The paragraph now quotes the table's own cells.
    import json as _json
    here = os.path.dirname(os.path.abspath(__file__))
    d = {'worse': f'{100 * worse:.1f}',
         'cev_aff': f'{100 * among:.2f}',
         'cev_pop': f'{100 * avg:.3f}',
         'betteroff': ('none is better off' if better < 5e-4
                       else f'{100 * better:.1f} percent are better off'),
         '_raw': {'priv': float(avg)}}
    with open(os.path.join(here, 'welfare_numbers.json'), 'w') as f:
        _json.dump(d, f, indent=1)
    print('   wrote welfare_numbers.json')


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
    critical_externality(base, 1.0)
    tab_welfare(base, 1.0)
