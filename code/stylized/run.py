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
    for name, kw in [('both penalties',      dict()),
                     ('mortality only',      dict(xi=0.0)),
                     ('income penalty only', dict(kap=0.0)),
                     ('neither',             dict(kap=0.0, xi=0.0))]:
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
        m0 = moments(with_(P(), b=b, kap=0.0), YG, W)
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
    print('4. CONDITIONALITY DETERS MORE WHEN THE BENEFIT IS GUARANTEED')
    print('=' * 78)
    b = bcal(P())
    print(f"{'pV':>7s}{'use, HF':>11s}{'use, TF':>11s}{'deterrent':>12s}"
          f"{'as % of HF':>13s}")
    pVs = np.array([0.05, 0.15, 0.27, 0.40, 0.55, 0.70, 0.85, 1.00])
    det = []
    for pv in pVs:
        par = with_(P(), b=b, pV=pv)
        h = moments(par, YG, W, 'HF')['part']
        t = moments(par, YG, W, 'TF')['part']
        det.append(h - t)
        pct = 100.0 * (h - t) / max(h, 1e-12)
        print(f'{pv:7.2f}{h:11.4f}{t:11.4f}{h - t:12.4f}{pct:13.2f}')
    print('''
   The deterrent is the gap between the two columns. It runs from essentially
   nothing under rationing to 20.6 per cent of participation under universal
   provision, and it is monotone throughout. Conditioning a benefit on sobriety
   is worth more when the benefit is guaranteed than when it is rationed,
   because the household forfeits more by acquiring the disorder.

   That is the paper's headline as a comparative static, and it explains the
   previous draft's weakest result. Experiment 1 imposed conditionality under
   rationing, which is the TOP ROW of this table, where the deterrent is close
   to zero while the cost of excluding people from a scarce benefit is first
   order.''')
    return pVs, np.array(det), b


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
    ax[2].set_title('(c) conditionality deters more when generous')

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
