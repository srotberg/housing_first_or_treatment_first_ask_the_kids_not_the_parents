"""
The four experiments in the stylised model, and what each parameter controls.

Every table here is a comparative static, and each one maps to a rung of the
channel shutdown ladder in section 7 of the paper. The point of running the
small model first is not to preview the answer, it is to say which parameter is
responsible for which fact, so that when the ladder in the calibrated model
moves a number the reader already knows what it is evidence about.
"""

import numpy as np
from stylized import P, clone, profile, moments, solve_one, _V2, _fields, OUT
import os

# a lognormal income distribution, so the ratios mean what they mean in the data
YG = np.exp(np.linspace(np.log(0.15), np.log(5.0), 46))
W  = np.exp(-0.5 * ((np.log(YG) + 0.5 * 0.75**2) / 0.75)**2)


def with_(par, **kw):
    f = _fields(par); f.update(kw)
    return clone(**f)


def bcal(par, target=0.0513, lo=1e-4, hi=2.0, iters=30):
    """Bisect b on the participation rate, as the real calibration does."""
    for _ in range(iters):
        mid = np.sqrt(lo * hi)
        if moments(with_(par, b=mid), YG, W)['part'] > target:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi))


# ---------------------------------------------------------------------------
def exp1():
    print('\n' + '=' * 78)
    print('1. WHICH PENALTY PUTS DRUG USE AT THE BOTTOM')
    print('   b is recalibrated to a 5.13 per cent participation rate in every')
    print('   row, so the rows differ ONLY in which penalty is switched on.')
    print('=' * 78)
    print(f"{'case':22s}{'b':>9s}{'r_use':>9s}{'r_sud':>9s}{'slope':>10s}")
    rows = {}
    # There are two ways the disorder hurts: it kills you, directly through kap
    # and indirectly by making you homeless, and it makes you poor, directly
    # through xi and indirectly through the resource cost of homelessness. So
    # the MORTALITY channel is {kap, kapH} and the RESOURCE channel is
    # {xi, ellH}, and switching them requires moving both members of each pair.
    # Switching kap alone left the homelessness mortality penalty running in the
    # rows that were supposed to have no mortality channel at all.
    for name, kw in [('both channels',       dict()),
                     ('mortality only',      dict(xi=0.0, ellH=0.0)),
                     ('resource only',       dict(kap=0.0, kapH=0.0)),
                     ('neither',             dict(kap=0.0, kapH=0.0,
                                                  xi=0.0, ellH=0.0))]:
        par = with_(P(), **kw)
        b = bcal(par)
        m = moments(with_(par, b=b), YG, W)
        print(f'{name:22s}{b:9.4f}{m["r_use"]:9.3f}{m["r_sud"]:9.3f}'
              f'{m["slope"]:10.4f}')
        rows[name] = (b, m)
    print(f'\n   data (NSDUH, ages 26+)          {0.951:9.3f}{0.687:9.3f}')
    print('''
   Read the r_use column. With NEITHER penalty, drug preferences alone put the
   average user at 2.6 times mean income: the rich give up less utility per
   dollar of drugs, so use concentrates at the top. An INCOME penalty leaves
   that at 1.57, still far above one. It cannot flip the gradient, because it
   scales the cost of the disorder with income and so cannot outrun the same
   force. Only the MORTALITY penalty crosses one, at 0.91, and with both
   penalties on the model gives 0.92 and 0.57 against 0.95 and 0.69 in the data.

   This is Referee 1's comment 1(d) answered before the quantitative model is
   even solved. His rival hypothesis is that the labour market consequences of
   use could generate the low income concentration on their own. In the
   smallest environment where the question is well posed, they cannot.''')
    return rows


# ---------------------------------------------------------------------------
def exp2():
    print('\n' + '=' * 78)
    print('2. b SETS THE LEVEL, THE MORTALITY PENALTY SETS THE SLOPE')
    print('=' * 78)
    print(f"{'b':>9s}{'participation':>15s}{'r_use':>9s}"
          f"{'r_use if kap=0':>17s}")
    rows = []
    for b in [0.002, 0.004, 0.008, 0.016, 0.032, 0.064]:
        m1 = moments(with_(P(), b=b), YG, W)
        m0 = moments(with_(P(), b=b, kap=0.0, kapH=0.0), YG, W)
        print(f'{b:9.3f}{m1["part"]:15.3f}{m1["r_use"]:9.3f}'
              f'{m0["r_use"]:17.3f}')
        rows.append((b, m1['part'], m1['r_use'], m0['r_use']))
    print('''
   b moves participation from 95 per cent to nothing. Over that whole range
   r_use stays below one when the mortality penalty is on and rises from 1.00
   to 2.16 when it is off. So the two moments are separately informative: the
   participation RATE identifies b, and the income GRADIENT identifies the
   mortality penalty. Neither can substitute for the other, which is the
   identification argument stated as a comparative static.''')
    return rows


# ---------------------------------------------------------------------------
def exp3():
    print('\n' + '=' * 78)
    print('3. THE VALUE OF LIFE CONSTANT IS SQUEEZED FROM BOTH SIDES')
    print('=' * 78)
    print(f"{'aleph':>8s}{'VSL elast.':>13s}{'share V2<0':>13s}"
          f"{'r_use':>9s}{'b to hit 5.13%':>17s}")
    for al in [0.0, 1.0, 2.0, 2.5, 4.0, 8.0]:
        par = with_(P(), aleph=al)
        v = np.array([(_V2(par, y, 0.0, 0, 'HF') - _V2(par, y, 0.0, 1, 'HF'))
                      * y / (1.0 - par.th) for y in YG])
        e = float(np.polyfit(np.log(YG), np.log(np.maximum(v, 1e-12)), 1)[0])
        neg = float((W * np.array([_V2(par, y, 0.0, 0, 'HF') < 0
                                   for y in YG])).sum() / W.sum())
        b = bcal(par)
        m = moments(with_(par, b=b), YG, W)
        print(f'{al:8.1f}{e:13.3f}{neg:13.3f}{m["r_use"]:9.3f}{b:17.4f}')
    print('''
   The mechanism needs the value of life to be SUPERLINEAR in income, and it is,
   through the log term. Two things then bound aleph from opposite directions.
   Below 2, the continuation value goes negative for 9 to 61 per cent of
   households, and for them dying more is a BENEFIT, which inverts the paper's
   central mechanism for exactly the population the policy targets. Above 2, the
   constant swamps the log term and the elasticity falls toward one.

   And note the r_use column barely moves across the admissible range. That is
   the operative point: a gradient moment CANNOT identify aleph. It fixes the
   effect of aleph on who uses and says nothing about its level. This is why the
   paper pins aleph on the model implied value of a statistical life, and it is
   how the previous version ended up with 64.6 per cent of households preferring
   to be dead without any moment registering a complaint.''')


# ---------------------------------------------------------------------------
def exp4():
    print('\n' + '=' * 78)
    print('4. THE TWO FORCES: MORAL HAZARD AND THE VALUE OF LIFE')
    print('   A voucher removes the risk of homelessness. Under Housing First it')
    print('   arrives whatever the disorder status; under Treatment First only if')
    print('   the household is clean. So the two columns ARE the decomposition:')
    print('     TF minus no voucher  = the value of life effect, on its own')
    print('     HF minus TF          = the moral hazard, on its own')
    print('   because the only thing HF adds to TF is cover in the disorder state.')
    print('=' * 78)
    b = bcal(P())
    pVs = np.array([0.0, 0.10, 0.20, 0.27, 0.40, 0.55, 0.70, 0.85, 1.00])
    H, T = [], []
    for pv in pVs:
        par = with_(P(), b=b, pV=pv)
        H.append(moments(par, YG, W, 'HF')['part'])
        T.append(moments(par, YG, W, 'TF')['part'])
    H, T = np.array(H), np.array(T)
    print(f"{'pV':>7s}{'use HF':>10s}{'use TF':>10s}"
          f"{'value of life':>15s}{'moral hazard':>15s}{'net, HF':>11s}")
    for k, pv in enumerate(pVs):
        vol = 100.0 * (T[k] / T[0] - 1.0)
        mh  = 100.0 * (H[k] / T[k] - 1.0)
        net = 100.0 * (H[k] / H[0] - 1.0)
        print(f'{pv:7.2f}{H[k]:10.4f}{T[k]:10.4f}{vol:14.2f}%{mh:14.2f}%'
              f'{net:10.2f}%')
    print("""
   Both forces are present and they have opposite signs, which is the reason the
   paper needs a quantitative model: the net effect of housing assistance on
   drug use is not signed by theory.

   The value of life effect is the smaller one here. Guaranteeing housing to the
   clean raises the value of staying clean and pulls use DOWN, by about one and
   a half per cent at universal provision. The moral hazard is larger. Extending
   the same guarantee to households that already have the disorder cushions the
   downside of acquiring it and pushes use UP, by about seven per cent. Under
   Housing First the second dominates and use rises with generosity.

   Treatment First keeps the first force and switches off the second. That is
   the whole policy, stated in one line, and it is why the gap between the two
   columns WIDENS in generosity: what conditionality removes is proportional to
   how much cover is on offer. Under rationing there is almost nothing to
   remove, which is why the previous draft's Experiment 1, conditionality at
   pV = 0.27, was the weakest of its four regimes.""")
    return pVs, H - T, b


# ---------------------------------------------------------------------------
def figures(r1, r2, cross):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 9, 'figure.dpi': 160,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, ax = plt.subplots(1, 3, figsize=(10.6, 3.15))

    for name, st in [('mortality only', '-'), ('income penalty only', '--'),
                     ('neither', ':')]:
        b, m = r1[name]
        ax[0].plot(YG, m['ev'], st, lw=1.6, label=name)
    ax[0].set_xscale('log')
    ax[0].set_xlabel('permanent income, mean = 1')
    ax[0].set_ylabel('drug use $v$')
    ax[0].set_title('(a) which penalty puts use at the bottom')
    ax[0].legend(frameon=False, fontsize=7.5)

    bs = [r[0] for r in r2]
    ax[1].plot(bs, [r[1] for r in r2], 'o-', lw=1.6)
    ax[1].set_xscale('log')
    ax[1].set_xlabel('Stone Geary parameter $b$')
    ax[1].set_ylabel('participation rate')
    ax[1].set_title('(b) $b$ sets the level, not the slope')
    a2 = ax[1].twinx()
    a2.plot(bs, [r[2] for r in r2], 's--', color='C3', lw=1.4)
    a2.plot(bs, [r[3] for r in r2], 's:', color='0.5', lw=1.4)
    a2.axhline(1.0, color='0.8', lw=0.8)
    a2.set_ylabel('income of users / average', color='C3')
    a2.spines['top'].set_visible(False)

    pVs, det, _ = cross
    ax[2].plot(pVs, det, 'o-', lw=1.6, color='C2')
    ax[2].set_xlabel('voucher generosity $\\pi_V$')
    ax[2].set_ylabel('participation, HF minus TF')
    ax[2].set_title('(c) the moral hazard grows with generosity')

    fig.tight_layout()
    p = os.path.join(OUT, 'stylized_model.pdf')
    fig.savefig(p, bbox_inches='tight')
    fig.savefig(p.replace('.pdf', '.png'), bbox_inches='tight')
    print(f'\nwrote {p}')


if __name__ == '__main__':
    r1 = exp1()
    r2 = exp2()
    exp3()
    cr = exp4()
    figures(r1, r2, cr)
