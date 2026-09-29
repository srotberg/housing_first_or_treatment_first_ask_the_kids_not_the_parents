"""Why does, or doesn't, a household at income y use?  The period-1 gain from using,
taken apart term by term from the model's own pieces (stylized.period1, _branch,
_flow), and checked to add up to the gain period1 reports.  The author, 29 September:
"the poor should use more and with Sud be homeless" -- is a term wrong in size or sign?

  drug      flow utility of the drug at the user's own c and h
  c,h       flow utility of the consumption and housing given up to buy it
  savings   beta*s0*[W2(a_u,0) - W2(a_0,0)]            (a different saving choice)
  SUD p2    beta*pi*s0*[W2(a_u,1) - W2(a_u,0)]         (job loss, homelessness...)
  death     beta*pi*(s1 - s0)*W2(a_u,1)                (the mortality penalty)
  child     -beta*omega*chdmg*pi                       (the child's penalty)
usage: STYLIZED_WORKERS=1 python3 decompose_use.py [TRUNC_FLOOR h1 kap b] -- y1 y2 ...
"""
import sys
import numpy as np
import calibrate as C
import stylized as ST
import stage_results as R
from stylized import with_

args = sys.argv[1:]
cut = args.index('--')
pre, ys = args[:cut], [float(x) for x in args[cut + 1:]]
par, _ = R.load(2)
if pre:
    tf, h1, kap, b = map(float, pre)
    C.TRUNC_FLOOR = tf; C.SIG = C._solve_sig(); C.YG, W0 = C._grid(C.SIG)
    C.EDGES = np.concatenate(([0.0], np.cumsum(W0))); C.W = W0 * len(W0)
    C.Q_F = C._ndtr((np.log(C._trunc_level(C.SIG, tf * ST.P().pr * ST.P().h2)) + 0.5 * C.SIG ** 2) / C.SIG)
    C.GRID_MEAN = (1.0 - C._tail_mean(C.SIG, C.Q_F)) / max(1.0 - C.Q_F, 1e-14)
    par = with_(par, yV=0.5 * C._median_of(C.YG, W0), h1=h1, kap=kap, b=b)
par = ST.solve_child_damage(par)
pol = par.policy
s0, s1 = par.phi0, par.phi0 * (1.0 - par.kap)
print(f'grid bottom {C.YG.min():.3f}; b {par.b:.4f} theta {par.th:.3f} kap {par.kap:.4f} h1 {par.h1:.4f} '
      f'u0 {par.u0:.4f} u1 {par.u1:.4f} pi_d {par.pi_base:.3f} aleph {par.aleph:.2f} omega {par.omega:.4f}')
for y in ys:
    ag, W2c, *_ = ST.solve_period2(par, y, pol, used=0)
    W2u = W2c if pol == 'HF' else ST.solve_period2(par, y, pol, used=1)[1]
    res = ST.period1(par, y, pol)
    print(f'\ny {y:.3f}  (chdmg {ST._chdmg_at(par, y):.3f})')
    for (p, inc, rmul), r in zip(ST._states(par, 0, pol, y, used=0), res):
        if p < 1e-3:
            continue
        _, gain, v, (au, su, ru, gu, mu), (a0, s_0, r0, g0, m0), inc_, own = r
        pi = float(ST._pid(par, v))
        hu, h0 = ST._hpick(par, su, mu), ST._hpick(par, s_0, m0)
        cu = inc - par.p_v * v - au - ru
        c0 = inc - a0 - r0
        W = lambda a, d, M=W2u: float(np.interp(a, ag, M[:, d]))
        drug = ST._flow(par, cu, hu, v) - ST._flow(par, cu, hu, 0.0)
        ch = ST._flow(par, cu, hu, 0.0) - ST._flow(par, c0, h0, 0.0)
        sav = par.beta * s0 * (W(au, 0) - W(a0, 0, W2c))
        sud = par.beta * pi * s0 * (W(au, 1) - W(au, 0))
        death = par.beta * pi * (s1 - s0) * W(au, 1)
        child = -par.beta * par.omega * ST._chdmg_at(par, y) * pi
        tot = drug + ch + sav + sud + death + child
        print(f'  state p {p:.3f} income {inc:.3f} rent-mult {rmul:.2f}: best v {v:.4f} ({100*par.p_v*v/inc:.1f}% of income)  '
              f'GAIN {gain:+.4f}  [sum {tot:+.4f}]  {"USES" if gain > 0 else "abstains"}')
        print(f'     drug {drug:+.4f}  c,h {ch:+.4f}  savings {sav:+.4f}  SUD p2 {sud:+.4f}  '
              f'death {death:+.4f}  child {child:+.4f}   housing if use/not: '
              f'{"street" if su > .5 else ("small" if mu > .5 else "std")}/{"street" if s_0 > .5 else ("small" if m0 > .5 else "std")}'
              f'   W2 clean {W(au,0):.2f} SUD {W(au,1):.2f}')
