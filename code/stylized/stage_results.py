"""
What Section 3 reports at each stage of the stylized model, computed at that
stage's own calibration (stages.py), and written as s<stage>_<name> for fill.py.

usage:  STYLIZED_WORKERS=1 python3 stage_results.py 1 [--no-figure | --figure-only | --replot]
        -> merges into stage_numbers.json

STAGE 1, the baseline without the child, reports three things.

  WHO USES.  The income of users over the average as each consequence of the
  disorder is scaled from nothing to past its calibrated strength, with b refitted
  at every point so participation stays on target: run.fig_who_uses, which also
  draws Figure 1.  At zero strength drugs are a pure luxury and users sit at the
  top; the question is which consequence turns that round.

  THE GAP, which replaces Figure 2.  Participation, the SUD rate and homelessness
  with no programme, under Treatment First and under Housing First, at the
  benchmark rationing and at universal cover.  Treatment First less no programme is
  the value-of-life force; Housing First less Treatment First is the moral hazard.

  DOMINANCE.  Lifetime value under each policy at the same generosity, household
  by household, as a CEV.  cev() is called WITH the level of lifetime value and the
  onset probability, which it needs at sigma = 2; welfare.tab_welfare calls it
  without them and so raises, which is one reason the old build was broken.
"""
import json
import math
import os
import sys

import numpy as np

import stages                      # installs the exact zero child damage shortcut
import stylized as ST
from stylized import P, with_, value1, use_prob
import calibrate as C
from calibrate import stats
from welfare import cev

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'stage_numbers.json')
WW = C.W / C.W.sum()


def load(stage):
    v = json.load(open(os.path.join(HERE, f'calibrated_stage{stage}.json')))
    return with_(P(), **{k: x for k, x in v.items() if not k.startswith('_')}), v


def ready(q):
    """q with its child damage solved (zero where it is exactly zero)."""
    return stages._solve_or_zero(q, q.policy)


def pc(x, nd=2):
    return f'{100 * x:.{nd}f}'


def outcomes(par, policy, pV):
    q = ready(with_(par, policy=policy, pV=pV))
    m = stats(q)
    return {k: float(m[k]) for k in ('part', 'sud', 'homeless', 'cost', 'r_use', 'dshare')
            if k in m and m[k] is not None}


def dominance(par, pV):
    """TF against HF at the same pi_V, household by household, as a CEV."""
    qh = ready(with_(par, policy='HF', pV=pV))
    qt = ready(with_(par, policy='TF', pV=pV))
    vh = np.array([value1(qh, y, 'HF') for y in C.YG])
    vt = np.array([value1(qt, y, 'TF') for y in C.YG])
    # the level's aleph weight depends on survival, so on the chance of the
    # disorder under the policy the level is taken at
    pi = np.array([par.pi_base * use_prob(qh, y, 'HF') for y in C.YG])
    lam = cev(par, vh - vt, v_level=vh, pi=pi)          # what a household would give up
    hit = lam > 1e-7
    return dict(worse=float((WW * (vt < vh - 1e-9)).sum()),
                better=float((WW * (vt > vh + 1e-9)).sum()),
                cev_aff=float((WW * lam)[hit].sum() / max(WW[hit].sum(), 1e-12)),
                cev_pop=float((WW * lam).sum()),
                min_gap=float((vh - vt).min()))


def stage1(par, figure=True):
    d = {}
    for pV, tag in ((par.pV, 'b'), (1.0, 'u')):
        none = outcomes(par, 'HF', 0.0)
        tf = outcomes(par, 'TF', pV)
        hf = outcomes(par, 'HF', pV)
        for lab, m in (('none', none), ('tf', tf), ('hf', hf)):
            for k in ('part', 'sud', 'homeless'):
                d[f's1_{k}_{lab}_{tag}'] = pc(m[k], 2 if k == 'part' else 3)
            d[f's1_cost_{lab}_{tag}'] = f'{m["cost"]:.4f}'
        d[f's1_vol_{tag}'] = pc(tf['part'] - none['part'])
        d[f's1_mh_{tag}'] = pc(hf['part'] - tf['part'])
        d[f's1_net_{tag}'] = pc(hf['part'] - none['part'])
        dom = dominance(par, pV)
        d[f's1_worse_{tag}'] = pc(dom['worse'], 1)
        d[f's1_better_{tag}'] = pc(dom['better'], 1)
        d[f's1_cevaff_{tag}'] = pc(dom['cev_aff'], 2)
        d[f's1_cevpop_{tag}'] = pc(dom['cev_pop'], 3)
        d[f'_s1_mingap_{tag}'] = dom['min_gap']
    if figure:
        d.update(stage1_figure(par))
    return d


def stage1_figure(par):
    """Figure 1 and every number the prose reads off it. The reversal's start, the
    fraction of the channel it takes and the points where no b delivers the target
    participation are derived here from the curves, so they move with the scan."""
    import run
    sc, curves, parts = run.fig_who_uses(par)
    mort, unem = np.asarray(curves['mortality']), np.asarray(curves['unemployment'])

    def at(c, s):
        return float(c[int(np.argmin(np.abs(sc - s)))])
    d = dict(s1_r_off=f'{at(mort, 0.0):.2f}', s1_r_mort=f'{at(mort, 1.0):.2f}',
             s1_r_mort_half=f'{at(mort, 0.5):.2f}', s1_r_unemp=f'{at(unem, 1.0):.2f}',
             s1_r_mort_hi=f'{at(mort, run.SCAN_HI):.2f}',
             s1_r_unemp_hi=f'{at(unem, run.SCAN_HI):.2f}',
             s1_scanhi_pc=f'{100 * run.SCAN_HI:.0f}', s1_scanhi_x=f'{run.SCAN_HI:g}')
    hi = at(unem, run.SCAN_HI)
    d['s1_runemphidir'] = 'above' if hi > 1.0 else ('below' if hi < 1.0 else 'at')
    # where the fall begins: the last point at or below the calibrated strength still
    # within five per cent of the ratio with the channel off (run.figure_numbers' rule)
    off, start = at(mort, 0.0), 0.0
    for s_, r_ in zip(sc, mort):
        if s_ <= 1.0 + 1e-9 and abs(r_ - off) <= 0.05 * abs(off):
            start = float(s_)
    d['s1_revstart_pc'] = f'{100 * start:.0f}'
    d['s1_revfrac'] = run._fraction_word(max(1.0 - start, 0.0))
    # points where no b delivers the target participation, by channel
    misses = {w: [(float(s_), float(p_)) for s_, p_ in zip(sc, parts[w])
                  if abs(p_ - C.TARGET['part']) > 5e-4] for w in ('mortality', 'unemployment')}
    d['_s1_misses'] = misses
    if len(misses['mortality']) == 1 and not misses['unemployment']:
        s_, p_ = misses['mortality'][0]
        d['s1_miss_scale_pc'] = f'{100 * s_:.0f}'
        d['s1_miss_part'] = f'{100 * p_:.2f}'
    d['_s1_curves'] = {'scale': [float(x) for x in sc],
                       'mortality': [float(x) for x in mort],
                       'unemployment': [float(x) for x in unem],
                       'part': {k: [float(x) for x in v] for k, v in parts.items()}}
    return d


# ---------------------------------------------------------------------------
# STAGES 2 TO 4: THE CHILD, kappa_x, AND WHAT THE EXTERNALITIES CHANGE
# ---------------------------------------------------------------------------
#
# A NEWBORN'S LIFETIME IS ITS CHILDHOOD, THEN ITS ADULTHOOD A PERIOD LATER,
# discounted to birth as Section 6 states the criterion:
#
#     life = kid + beta * adult
#
# with kid and adult from optimal_sud.economy (the child's own childhood, aleph
# included, counted as xi - 1 of the household; the parent's own lifetime, every
# child term removed), each at the economy's own stationary mixture.
# optimal_sud.py SUMS the two undiscounted and its CEV's constant counts aleph
# for the adult years only, so the childhood aleph is treated as goods utility;
# both are corrected here, and both are reported to the author.
#
# THE CEV scales consumption in every bundle, so every U(X) term scales by
# (1+D)^(phi_c(1-sigma)) and the additive terms -- aleph, and -kappa_x H once it
# is in -- do not.  A is the lifetime count of those constants.

def _aw(par, pi):
    from child_welfare import aleph_weight
    return aleph_weight(par, pi)


# THE CHILD BEARS kappa_x H ONCE, NOT xi - 1 TIMES, as the quantitative model has
# it: its childhood utility is (xi - 1)(U(X_K) + aleph) -- f90 at child_flow_out,
# "THE VALUE OF LIFE IS INSIDE THE FACTOR" -- and own_childhood subtracts
# kappa_x * model_fraction_homeless once per year of childhood, outside that factor.


def _const(par, pi, kx=0.0, H=0.0):
    """The additive part of a newborn's lifetime value: aleph, counted as xi - 1
    of the household in childhood and once over the adult life, and -kappa_x H,
    once in childhood and once over the adult life."""
    aw = _aw(par, pi)
    return par.aleph * ((par.xi - 1.0) + par.beta * aw) - kx * H * (1.0 + par.beta * aw)


def life(par, e, kx=0.0):
    aw = _aw(par, par.pi_base * e['part'])
    return e['kid'] + par.beta * e['adult'] - kx * e['homeless_stat'] * (1.0 + par.beta * aw)


def cev_life(par, e_new, e_ref, kx=0.0):
    """What a newborn in e_ref would need in consumption, everywhere, to be as
    well off as a newborn in e_new."""
    from stylized import _shares
    ex = _shares(par)[0] * (1.0 - par.sigma)
    pi = par.pi_base * e_ref['part']
    U = life(par, e_ref, kx) - _const(par, pi, kx, e_ref['homeless_stat'])
    return (1.0 + (life(par, e_new, kx) - life(par, e_ref, kx)) / U) ** (1.0 / ex) - 1.0


def economy(par, label, policy='HF', pV=None):
    import optimal_sud as O
    return O.economy(par, label, policy=policy, pV=pV)


def kappa_x(par, e, wtp):
    """kappa_x from a willingness to pay of wtp of consumption, as the full
    model's probe: the disamenity per unit of homelessness, in utils per period
    alive, that costs an adult as much over its adult life as giving up wtp of
    its consumption in every period of it."""
    from stylized import _shares
    ex = _shares(par)[0] * (1.0 - par.sigma)
    pi = par.pi_base * e['part']
    aw = _aw(par, pi)
    U_adult = e['adult'] - par.aleph * aw
    loss = -U_adult * ((1.0 - wtp) ** ex - 1.0)
    return loss / (e['homeless_stat'] * aw)


WTP = 0.002          # Loubiere et al. (2020), as in the quantitative model


def stage2(par):
    d = {}
    q = ready(par)
    m = stats(q)
    m0 = stats(ready(with_(par, omega=0.0)))
    d['s2_r_use'] = f'{m["r_use"]:.2f}'
    d['s2_r_use_om0'] = f'{m0["r_use"]:.2f}'
    d['s2_part_om0'] = pc(m0['part'])
    d['s2_part'] = pc(m['part'])
    import children as CH
    d['s2_or_sud'] = f'{ST.child_sud_odds_ratio(q, C.YG, C.W):.2f}'
    d['s2_or_hl'] = f'{ST.child_homeless_odds_ratio(q, C.YG, C.W):.2f}'
    hf = economy(par, 'HF', 'HF')
    tf = economy(par, 'TF', 'TF')
    for tag, e in (('hf', hf), ('tf', tf)):
        d[f's2_sud_{tag}'] = pc(e['sud_stat'], 3)
        d[f's2_homeless_{tag}'] = pc(e['homeless_stat'], 3)
        d[f's2_part_{tag}'] = pc(e['part'])
    d['s2_cev_tf'] = pc(cev_life(par, tf, hf), 3)
    kid_only = dict(tf, adult=hf['adult'])
    adult_only = dict(tf, kid=hf['kid'])
    d['s2_cev_tf_kid'] = pc(cev_life(par, kid_only, hf), 3)
    d['s2_cev_tf_adult'] = pc(cev_life(par, adult_only, hf), 3)
    return d, hf, tf


def stage3(par, hf, tf):
    kx = kappa_x(par, hf, WTP)
    d = {'s3_kx': f'{kx:.3f}', 's3_wtp_pc': f'{100 * WTP:.1f}',
         's3_cev_tf': pc(cev_life(par, tf, hf, kx), 3),
         's3_cev_tf_nokx': pc(cev_life(par, tf, hf), 3)}
    return d, kx


def stage4(par, hf, kx):
    d = {}
    opt = economy(with_(par, omega=1.0), 'omega = 1', 'HF')
    d['s4_part_opt'] = pc(opt['part'])
    d['s4_sud_opt'] = pc(opt['sud_stat'], 3)
    d['s4_dshare_opt'] = pc(opt['dshare']) if opt['dshare'] is not None else 'n.a.'
    d['s4_homeless_opt'] = pc(opt['homeless_stat'], 3)
    d['s4_cev_opt'] = pc(cev_life(par, opt, hf, kx), 3)
    return d


# ---------------------------------------------------------------------------
# THE CALIBRATION: Tables 1 and 2 and the names the calibration prose quotes
# ---------------------------------------------------------------------------
TAB = os.path.join(HERE, '..', '..', 'writing', 'tables')


def _smr(par):
    """kap is the proportional fall in thirty-year survival; the rate ratio it
    implies is what the literature and the quantitative model quote."""
    return 1.0 + math.log(1.0 - par.kap) / math.log(par.phi0)


def calibration_names(p1, r1, p2, r2):
    T = C.TARGET
    th_t = stages.DSHARE_TARGET
    d = dict(s_beta=f'{p1.beta:.3f}', s_beta_ann=f'{p1.beta ** (1 / p1.years):.3f}',
             s_sigma=f'{p1.sigma:.0f}', s_phi0=f'{p1.phi0:.2f}', s_yfloor=f'{p1.y_floor:.3f}',
             s_h2=f'{p1.h2:.2f}', s_h3=f'{p1.h3:.2f}', s_kr_pc=f'{100 * p1.kappa_r:.0f}',
             s_kv=f'{p1.kV:.2f}', s_pv=f'{p1.pV:.3f}', s_u1=f'{p1.u1:.3f}',
             s_pid=f'{p1.pi_base:.3f}', s_rho=f'{p2.rho:.2f}',
             s_deltad_pc=f'{100 * (1 - math.exp(-p2.delta_d)):.0f}', s_deltad=f'{p2.delta_d:.3f}',
             s_t_sud=f'{100 * T["sud"]:.2f}', s_t_part=f'{100 * T["part"]:.2f}',
             s_t_bot50=f'{100 * T["bot50"]:.1f}', s_t_vsl=f'{T["vsl"]:.0f}',
             s_t_hspend=f'{100 * T["hspend"]:.1f}', s_t_dshare=f'{100 * th_t:.1f}',
             s_t_ruse=f'{T["r_use"]:.2f}', s_t_homeless=f'{100 * T["homeless"]:.2f}',
             s_t_unemp=f'{100 * 0.0485:.2f}', s_t_sudhl=f'{100 * T["sud_of_homeless2"]:.1f}',
             s_t_gap=f'{100 * 0.1834:.1f}', s_sigy=f'{C.SIG:.3f}')
    for tag, par, raw in (('s1', p1, r1), ('s2', p2, r2)):
        m = raw['_moments']
        d.update({f'{tag}_v_aleph': f'{par.aleph:.2f}', f'{tag}_v_gam': f'{par.gam:.3f}',
                  f'{tag}_v_b': f'{par.b:.4f}', f'{tag}_v_th': f'{par.th:.3f}',
                  f'{tag}_v_smr': f'{_smr(par):.2f}', f'{tag}_v_h1': f'{par.h1:.4f}',
                  f'{tag}_v_u0': f'{par.u0:.4f}', f'{tag}_iter': f'{raw["_iteration"]}',
                  f'{tag}_worst': f'{raw["_worst_gap_pc"]:.1f}'})
        for k in ('vsl', 'hspend', 'part', 'dshare', 'r_use', 'homeless', 'unemployment',
                  'sud_of_homeless2', 'child_gap', 'child_sud_or', 'child_hl_or', 'sud'):
            if m.get(k) is not None:
                d[f'{tag}_m_{k}'] = (f'{m[k]:.1f}' if k == 'vsl' else f'{m[k]:.2f}'
                                     if k in ('r_use', 'child_sud_or', 'child_hl_or')
                                     else f'{100 * m[k]:.2f}')
    d['s2_v_omega'] = f'{p2.omega:.4f}'
    return d


def red(x):
    return r'\textcolor{red}{%s}' % x


def write_tables(p1, r1, p2, r2):
    """Tables 1 and 2, every cell red: both were rebuilt for the staged model."""
    ext = [('Preferences and demographics', [
        (r'$\beta$', 'Discount factor over a thirty-year period',
         f'${p1.beta ** (1 / p1.years):.3f}$ annually, compounded', f'${p1.beta:.3f}$'),
        (r'$R$', 'Gross return on saving', 'No interest', f'${p1.R:.2f}$'),
        (r'$\sigma$', 'Risk aversion', 'As in the quantitative model', f'${p1.sigma:.0f}$'),
        (r'$\bar\phi$', 'Survival over a period, no SUD', 'SSA period life table, ages 26--55',
         f'${p1.phi0:.2f}$')]),
        ('The SUD', [
        (r'$\pi_d$', 'Chance that use starts a SUD', 'NSDUH 2024: SUD rate over participation',
         f'${p1.pi_base:.3f}$')]),
        ('Income', [
        (r'$\psi_{ui}$', 'Income support replacement rate', 'DOL, statutory UI rates', f'${p1.repl:.2f}$'),
        (r'$\bar y$', 'Cap on the earnings base', 'DOL, state benefit maxima', f'${p1.ycap:.2f}$')]),
        ('Housing, drugs and the voucher', [
        (r'$p_r$', 'Rent per unit of housing services', 'Normalisation', f'${p1.pr:.2f}$'),
        (r'$p_v$', 'Price of a unit of drugs', 'Normalisation', f'${p1.p_v:.2f}$'),
        (r'$h_2$', 'Small rental unit', 'Set', f'${p1.h2:.2f}$'),
        (r'$h_3$', 'Standard rental unit', 'Set', f'${p1.h3:.2f}$'),
        (r'$\kappa_r$', "Tenant's share of the rent", 'HUD voucher rules', f'${p1.kappa_r:.2f}$'),
        (r'$\kappa_V$', 'Voucher means test', 'HUD income limits', f'${p1.kV:.2f}$'),
        (r'$\pi_V$', 'Chance of drawing a voucher', 'HUD 2023, recipients over eligible', f'${p1.pV:.3f}$')]),
        ('The child, stage 2 onward', [
        (r'$\xi$', 'Equivalence scale while the child is at home', 'Square-root scale', f'${p2.xi:.2f}$'),
        (r'$\rho$', 'Persistence of productivity across generations', 'As in the quantitative model',
         f'${p2.rho:.2f}$'),
        (r'$\delta_d$', "Child's income, parent's SUD, in logs",
         f'Nilsson (2017), a {100 * (1 - math.exp(-p2.delta_d)):.0f} percent cut', f'${p2.delta_d:.3f}$')])]
    L = [r'\footnotesize', r'\begin{tabular}{@{}lL{6.4cm}L{5.4cm}r@{}}', r'\toprule',
         r'Parameter & Description & Source or rationale & Value \\', r'\midrule']
    for i, (hd, rows) in enumerate(ext):
        if i:
            L.append(r'\addlinespace')
        L.append(r'\multicolumn{4}{@{}l}{\emph{%s}} \\' % red(hd))
        for r in rows:
            L.append(' & '.join(red(c) for c in r) + r' \\')
    L += [r'\bottomrule', r'\end{tabular}']
    open(os.path.join(TAB, 'tab_external.tex'), 'w').write(
        '% Generated by code/stylized/stage_results.py from the stage calibrations.\n'
        + '\n'.join(L) + '\n')

    T = C.TARGET
    m1, m2 = r1['_moments'], r2['_moments']

    def mm(m, k, fmt):
        return fmt(m[k]) if m.get(k) is not None else '--'
    pct = lambda x: f'{100 * x:.1f}\\%'
    rows = [
        (r'$\sigma_y$', "Bottom half's share of earnings, SCF 2022", pct(T['bot50']),
         pct(T['bot50']), f'{C.SIG:.3f}', pct(T['bot50']), f'{C.SIG:.3f}'),
        (r'$\gamma$', 'Housing over non-drug expenditure, CEX 2024', pct(T['hspend']),
         mm(m1, 'hspend', pct), f'{p1.gam:.3f}', mm(m2, 'hspend', pct), f'{p2.gam:.3f}'),
        (r'$\aleph$', 'Value of a statistical life over income', f'{T["vsl"]:.0f}',
         mm(m1, 'vsl', lambda x: f'{x:.1f}'), f'{p1.aleph:.2f}', mm(m2, 'vsl', lambda x: f'{x:.1f}'),
         f'{p2.aleph:.2f}'),
        (r'$b$', 'Drug participation, NSDUH 2024', pct(T['part']),
         mm(m1, 'part', pct), f'{p1.b:.4f}', mm(m2, 'part', pct), f'{p2.b:.4f}'),
        (r'$\theta$', 'Drug spending over users\' income', pct(stages.DSHARE_TARGET),
         mm(m1, 'dshare', pct), f'{p1.th:.3f}', mm(m2, 'dshare', pct), f'{p2.th:.3f}'),
        (r'$\kappa_{\phi d}$', "Users' income over the average, NSDUH 2024", f'{T["r_use"]:.2f}',
         mm(m1, 'r_use', lambda x: f'{x:.2f}'), f'{_smr(p1):.2f}', mm(m2, 'r_use', lambda x: f'{x:.2f}'),
         f'{_smr(p2):.2f}'),
        (r'$h_1$', 'Homelessness rate', pct(T['homeless']),
         mm(m1, 'homeless', pct), f'{p1.h1:.4f}', mm(m2, 'homeless', pct), f'{p2.h1:.4f}'),
        (r'$u_0$', 'Unemployment rate, BLS CPS 2014--24', pct(0.0485),
         mm(m1, 'unemployment', pct), f'{p1.u0:.4f}', mm(m2, 'unemployment', pct), f'{p2.u0:.4f}'),
        (r'$u_1$', 'SUD share of the homeless, Gutwinski et al.\\ (2021)',
         pct(T['sud_of_homeless2']), mm(m1, 'sud_of_homeless2', pct), f'{p1.u1:.3f}',
         mm(m2, 'sud_of_homeless2', pct), f'{p2.u1:.3f}'),
        (r'$\omega_c$', 'Use of non-parents over parents, less one, NSDUH 2024', pct(0.1834),
         '--', '--', mm(m2, 'child_gap', pct), f'{p2.omega:.4f}'),
    ]
    # ONE LINE A ROW (the author, 29 September): the target column is l, not a
    # fixed-width paragraph column that wrapped the longer moments onto two lines.
    L = [r'\footnotesize\setlength{\tabcolsep}{4pt}',
         r'\begin{tabular}{@{}llrrrrr@{}}', r'\toprule',
         r' & & & \multicolumn{2}{c}{Stage 1} & \multicolumn{2}{c}{Stage 2} \\',
         r'\cmidrule(lr){4-5}\cmidrule(l){6-7}',
         r'Parameter & Target moment & Data & Model & Value & Model & Value \\', r'\midrule']
    for r in rows:
        L.append(' & '.join(red(c) for c in r) + r' \\')
    L += [r'\bottomrule', r'\end{tabular}']
    open(os.path.join(TAB, 'tab_internal.tex'), 'w').write(
        '% Generated by code/stylized/stage_results.py from the stage calibrations.\n'
        + '\n'.join(L) + '\n')


def write_stage1_table():
    """Table 3: the two forces and dominance at stage 1, which replaces Figure 2.
    Every cell red: the table is new."""
    d = json.load(open(OUT))
    g = lambda k: d[k]
    L = [r'\footnotesize', r'\begin{tabular}{@{}lcccccc@{}}', r'\toprule',
         r' & \multicolumn{3}{c}{At $\pi_V=' + d['s_pv'] + r'$} & \multicolumn{3}{c}{Universal cover} \\',
         r'\cmidrule(lr){2-4}\cmidrule(l){5-7}',
         r' & None & TF & HF & None & TF & HF \\', r'\midrule',
         r'\multicolumn{7}{@{}l}{\emph{Panel A. Outcomes, percent of households}} \\']
    for lab, k in (('Drug participation', 'part'), ('Carrying a SUD', 'sud'), ('Homeless', 'homeless')):
        L.append(r'\quad ' + lab + ' & ' + ' & '.join(g(f's1_{k}_{p}_{t}') for t in ('b', 'u')
                                                   for p in ('none', 'tf', 'hf')) + r' \\')
    L += [r'\addlinespace',
          r'\multicolumn{7}{@{}l}{\emph{Panel B. The two forces on participation, percentage points}} \\',
          r'\quad Value of life, TF less none & & ' + g('s1_vol_b') + r' & & & ' + g('s1_vol_u') + r' & \\',
          r'\quad Moral hazard, HF less TF & & & ' + g('s1_mh_b') + r' & & & ' + g('s1_mh_u') + r' \\',
          r'\addlinespace',
          r'\multicolumn{7}{@{}l}{\emph{Panel C. Treatment First against Housing First}} \\',
          r'\quad Households strictly worse off, percent & & ' + g('s1_worse_b') + r' & & & ' + g('s1_worse_u') + r' & \\',
          r'\quad Households strictly better off, percent & & ' + g('s1_better_b') + r' & & & ' + g('s1_better_u') + r' & \\',
          r'\quad CEV of those affected, percent & & $-' + g('s1_cevaff_b') + r'$ & & & $-' + g('s1_cevaff_u') + r'$ & \\',
          r'\quad CEV of the population, percent & & $-' + g('s1_cevpop_b') + r'$ & & & $-' + g('s1_cevpop_u') + r'$ & \\',
          r'\bottomrule', r'\end{tabular}']
    body = '\n'.join(L) + '\n'
    # every cell red
    import re as _re
    def _redcells(line):
        if not line.rstrip().endswith('\\\\') or line.startswith('\\multicolumn') or 'cmidrule' in line:
            return line
        cells = line.rstrip()[:-2].split('&')
        def one(c):
            c = c.strip()
            if not c:
                return ''
            if c.startswith('\\multicolumn'):
                return c.replace('}{', '}{\\textcolor{red}{', 2).rstrip('}') + '}}}' if False else c
            if _re.fullmatch(r'-[0-9.]+', c):
                c = f'${c}$'
            return red(c)
        return ' & '.join(one(c) for c in cells) + r' \\'
    body = '\n'.join(_redcells(l) for l in body.splitlines()) + '\n'
    open(os.path.join(TAB, 'tab_stage1.tex'), 'w').write(
        '% Generated by code/stylized/stage_results.py from stage 1.\n' + body)


def merge(d):
    old = json.load(open(OUT)) if os.path.exists(OUT) else {}
    old.update(d)
    json.dump(old, open(OUT, 'w'), indent=1, sort_keys=True)


if __name__ == '__main__':
    if sys.argv[1] == 'tables':
        p1, r1 = load(1)
        p2, r2 = load(2)
        write_tables(p1, r1, p2, r2)
        if os.path.exists(OUT) and 's1_part_none_b' in json.load(open(OUT)):
            write_stage1_table()
        d = calibration_names(p1, r1, p2, r2)
        merge(d)
        for k in sorted(d):
            print(f'   {k:22s} {d[k]}')
        raise SystemExit
    stage = int(sys.argv[1])
    par, raw = load(stage)
    print(f'stage {stage}: calibrated_stage{stage}.json, iteration {raw["_iteration"]}, '
          f'worst gap {raw["_worst_gap_pc"]} per cent')
    if stage == 1 and '--replot' in sys.argv:
        import run
        c = json.load(open(OUT))['_s1_curves']
        run.draw_who_uses(c['scale'], c)
        raise SystemExit
    if stage == 1 and '--figure-only' in sys.argv:
        d = stage1_figure(par)
    elif stage == 1:
        d = stage1(par, figure='--no-figure' not in sys.argv)
    else:
        # stages 2, 3 and 4 are one calibration: kappa_x moves no choice, and
        # stage 4's experiments are run on stage 3's economy
        d, hf, tf = stage2(par)
        d3, kx = stage3(par, hf, tf)
        d.update(d3)
        d.update(stage4(par, hf, kx))
    merge(d)
    for k in sorted(d):
        if not k.startswith('_'):
            print(f'   {k:22s} {d[k]}')
