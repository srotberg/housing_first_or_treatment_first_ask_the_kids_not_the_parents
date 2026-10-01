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
import fill as F                   # compare(): direction words the prose takes from the numbers
from welfare import cev

HERE = os.path.dirname(os.path.abspath(__file__))
# STAGE_NUMBERS_OUT (30 September): stage 1 and stage 2 run in separate cloud workers, and
# each worker's rebase keeps its own version of a conflicting file, so two workers merging
# into one stage_numbers.json can drop each other's keys.  The second writes elsewhere and
# the two are merged afterwards.
OUT = os.path.join(HERE, os.environ.get('STAGE_NUMBERS_OUT', 'stage_numbers.json'))
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


def worse_share_exact(par, pV):
    """THE SHARE WORSE OFF UNDER TREATMENT FIRST, measured the way participation is.

    dominance() counts every income node whose lifetime value falls as worse off,
    WHOLE: a node whose cell straddles the use threshold counts in full, while
    participation (calibrate.stats) gives that cell only the fraction of itself
    inside the use region.  On 30 September that put 10.2 per cent worse off against
    8.92 per cent using, and the author asked twice how that could be.  A household is
    worse off exactly when it would use under Housing First in some period 1 draw
    (checked on the grid: no non-user worse off, no user indifferent), so the share
    is each cell's largest use fraction across its draws, on the same weights and
    boundaries as participation.  It is still above participation, because a
    household that uses in only some of its draws is worse off in full and counts in
    participation only in the draws in which it uses."""
    q = ready(with_(par, policy='HF', pV=pV))
    PR, frac, *_ = ST.threshold(q, C.YG, 'HF', C.EDGES, C.CDF)
    ww = np.asarray(C.W) / np.sum(C.W)
    return float((ww * np.max(np.where(PR > 0.0, frac, 0.0), axis=1)).sum())


def stage1(par, figure=True):
    d = {}
    for pV, tag in ((par.pV, 'b'),):          # rationed only (the author, 29 September)
        none = outcomes(par, 'HF', 0.0)
        tf = outcomes(par, 'TF', pV)
        hf = outcomes(par, 'HF', pV)
        for lab, m in (('none', none), ('tf', tf), ('hf', hf)):
            for k in ('part', 'sud', 'homeless'):
                d[f's1_{k}_{lab}_{tag}'] = pc(m[k], 2 if k == 'part' else 3)
            d[f's1_cost_{lab}_{tag}'] = f'{m["cost"]:.4f}'
        d[f's1_vol_{tag}'] = pc(tf['part'] - none['part'])
        d[f's1_vol_{tag}_abs'] = pc(abs(tf['part'] - none['part']))
        d[f's1_mh_{tag}'] = pc(hf['part'] - tf['part'])
        d[f's1_net_{tag}'] = pc(hf['part'] - none['part'])
        dom = dominance(par, pV)
        d[f's1_worse_{tag}'] = pc(worse_share_exact(par, pV), 1)
        d[f's1_worse_grid_{tag}'] = pc(dom['worse'], 1)          # the old whole-node count
        d[f's1_better_{tag}'] = pc(dom['better'], 1)
        d[f's1_cevaff_{tag}'] = pc(dom['cev_aff'], 2)
        d[f's1_cevpop_{tag}'] = pc(dom['cev_pop'], 3)
        d[f'_s1_mingap_{tag}'] = dom['min_gap']
    if figure:
        d.update(stage1_figure(par))
    return d


def revstart_names(sc, mort, part, ref):
    """Where the mortality curve's fall begins: the last point at or below the
    calibrated strength still within five per cent of its value at zero, COUNTING
    ONLY POINTS WHERE b HOLDS PARTICIPATION ON ITS REFERENCE.  A point where no b
    does is not on the same footing as the rest -- at 75 per cent it sat at 7.89
    per cent participation and 4.08 times average income -- and the figure no
    longer draws it (the author, 29 September: "smooth the blue line so there is
    not uptick before the 100%"), so the prose must not read off it either."""
    import run
    ok = [abs(p - ref) <= 5e-4 for p in part]
    off, start = mort[0], 0.0
    for s_, r_, k in zip(sc, mort, ok):
        if k and s_ <= 1.0 + 1e-9 and abs(r_ - off) <= 0.05 * abs(off):
            start = float(s_)
    # WHERE THE CURVE CROSSES ONE, between the last drawn point above it and the first
    # below, and what it does past the calibrated strength.  Once h1 was held at its
    # calibrated value (the author, 29 September) the curve fell from the first step
    # and the "hardly moves up to" reading had nothing left to describe.
    pts = [(float(s_), float(r_)) for s_, r_, k in zip(sc, mort, ok) if k]
    lo = max((s_ for s_, r_ in pts if r_ >= 1.0), default=0.0)
    hi = min((s_ for s_, r_ in pts if r_ < 1.0 and s_ > lo), default=float('nan'))
    r1 = next(r_ for s_, r_ in pts if abs(s_ - 1.0) < 1e-9)
    rh = pts[-1][1]
    hi_dir = ('stays at' if f'{rh:.2f}' == f'{r1:.2f}' else
              'falls further to' if rh < r1 else 'rises back to')
    return dict(s1_revstart_pc=f'{100 * start:g}',
                s1_revfrac=run._fraction_word(max(1.0 - start, 0.0)),
                s1_cross_lo_pc=f'{100 * lo:g}', s1_cross_hi_pc=f'{100 * hi:g}',
                s1_r_mort_hi_dir=hi_dir)


def stage1_figure(par):
    """Figure 1 and every number the prose reads off it.  Under run.OTHER_CHANNEL =
    'off' (the author, 29 September: "remove the other channel and just scale the
    penalty itself") each curve scans ONE channel with the other switched off, so both
    start from the economy with neither channel and each curve's 100 per cent point is
    that channel acting alone; the calibrated economy, both channels on, is the circle
    on the dotted line.  Under 'calibrated' both curves pass through the calibrated
    economy instead.  Names mean the same thing either way."""
    import run
    from calibrate import stats
    sc, curves, parts = run.fig_who_uses(par)
    mort, unem = np.asarray(curves['mortality']), np.asarray(curves['unemployment'])

    def at(c, s):
        return float(c[int(np.argmin(np.abs(sc - s)))])
    if run.OTHER_CHANNEL == 'off':
        r_none, r_mort, r_unem = at(mort, 0.0), at(mort, 1.0), at(unem, 1.0)
        r_cal = float(stats(par)['r_use'])
    else:
        saved = run.OTHER_CHANNEL
        try:
            run.OTHER_CHANNEL = 'off'
            r_none = float(stats(run._scaled(par, 'mortality', 0.0))['r_use'])
        finally:
            run.OTHER_CHANNEL = saved
        r_mort, r_unem, r_cal = at(unem, 0.0), at(mort, 0.0), at(mort, 1.0)
    d = dict(s1_r_none=f'{r_none:.2f}',
             s1_r_mortonly=f'{r_mort:.2f}',             # mortality alone, full strength
             s1_r_jobonly=f'{r_unem:.2f}',              # job loss alone, full strength
             s1_r_cal=f'{r_cal:.2f}',                   # both on: the calibrated economy
             s1_r_mort_half=f'{at(mort, 0.5):.2f}',
             s1_r_mort_hi=f'{at(mort, run.SCAN_HI):.2f}',
             s1_r_unemp_hi=f'{at(unem, run.SCAN_HI):.2f}',
             s1_scanhi_pc=f'{100 * run.SCAN_HI:.0f}', s1_scanhi_x=f'{run.SCAN_HI:g}')
    # which side of one the job-loss channel leaves users at, at full and at twice
    # its strength: the prose says it never reverses the gradient, so the word turns
    # if it ever does
    d['s1_rjobdir'] = 'above' if r_unem > 1.0 else 'below'
    d['s1_runemphidir'] = 'above' if at(unem, run.SCAN_HI) > 1.0 else 'below'
    d.update(revstart_names(sc, mort, parts['mortality'], run.PART_REF))
    # points where no b delivers the target participation, by channel
    misses = {w: [(float(s_), float(p_)) for s_, p_ in zip(sc, parts[w])
                  if abs(p_ - run.PART_REF) > 5e-4] for w in ('mortality', 'unemployment')}
    d['s1_part_ref'] = pc(run.PART_REF)
    d['s1_nmiss'] = str(sum(len(v) for v in misses.values()))
    d['_s1_misses'] = misses
    d['_s1_curves'] = {'scale': [float(x) for x in sc],
                       'mortality': [float(x) for x in mort],
                       'unemployment': [float(x) for x in unem],
                       'part': {k: [float(x) for x in v] for k, v in parts.items()},
                       'other_channel': run.OTHER_CHANNEL, 'r_cal': r_cal,
                       'part_ref': float(run.PART_REF)}
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
    d['s2_ruse_dir'] = 'richer' if m0['r_use'] > m['r_use'] else 'poorer'
    # WHAT THE CHILD CHANGES BEFORE ANY REFIT: stage 1's parameters with the shared
    # bundle alone (xi), then with omega_c and delta_d on top at stage 2's values
    p1, _r1 = load(1)
    mx = stats(ready(with_(p1, xi=par.xi)))
    mc = stats(ready(with_(p1, xi=par.xi, omega=par.omega, delta_d=par.delta_d)))
    d['s2_xi_part'] = pc(mx['part'], 1)
    d['s2_xi_vsl'] = f'{mx["vsl"]:.0f}'
    d['s2_xi_ruse'] = f'{mx["r_use"]:.2f}'
    d['s2_child_part'] = pc(mc['part'], 1)
    import children as CH
    d['s2_or_sud'] = f'{ST.child_sud_odds_ratio(q, C.YG, C.W):.2f}'
    d['s2_or_hl'] = f'{ST.child_homeless_odds_ratio(q, C.YG, C.W):.2f}'
    hf = economy(par, 'HF', 'HF')
    tf = economy(par, 'TF', 'TF')
    for tag, e in (('hf', hf), ('tf', tf)):
        d[f's2_sud_{tag}'] = pc(e['sud_stat'], 3)
        d[f's2_homeless_{tag}'] = pc(e['homeless_stat'], 3)
        d[f's2_part_{tag}'] = pc(e['part'])
    # WHICH WAY TREATMENT FIRST MOVES CHILDHOOD HOMELESSNESS here, as a word the prose
    # takes rather than types: homeless_stat is period 1, when the child is at home,
    # and the quantitative model moves it the other way, so the sentence has to turn
    # with the numbers.
    d.update(F.compare(tf['homeless_stat'], hf['homeless_stat'], 's2_homeless_',
                       more='raises', less='lowers'))
    d['s2_homeless_chg_pc'] = f"{100 * abs(tf['homeless_stat'] / hf['homeless_stat'] - 1):.0f}"
    d['s2_cev_tf'] = pc(cev_life(par, tf, hf), 3)
    kid_only = dict(tf, adult=hf['adult'])
    adult_only = dict(tf, kid=hf['kid'])
    d['s2_cev_tf_kid'] = pc(cev_life(par, kid_only, hf), 3)
    d['s2_cev_tf_adult'] = pc(cev_life(par, adult_only, hf), 3)
    return d, hf, tf


def consumption_share(par):
    """Consumption c (the good the CEV scales, housing and drugs apart) over income, at
    the Housing First benchmark: rent over income times non-drug spending over rent,
    less the rent, both from calibrate.stats."""
    m = stats(ready(with_(par, policy='HF')))
    return float(m['housing_share'] * (1.0 / m['hspend'] - 1.0))


def stage3(par, hf, tf):
    # THE WILLINGNESS TO PAY IS A SHARE OF INCOME (the author, 30 September: "0.2 of
    # income, which is translated to consumption based on the share of income spent on
    # consumption").  It was applied as 0.2 per cent of consumption.
    cs = consumption_share(par)
    kx = kappa_x(par, hf, WTP / cs)
    d = {'s3_kx': f'{kx:.3f}', 's3_wtp_pc': f'{100 * WTP:.1f}',
         's3_cshare_pc': f'{100 * cs:.0f}', 's3_wtp_c_pc': f'{100 * WTP / cs:.2f}',
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
    # its fall against the Housing First economy the optimum is compared with
    d['s4_homeless_opt_pc'] = f"{100 * abs(opt['homeless_stat'] / hf['homeless_stat'] - 1):.0f}"
    d.update(F.compare(opt['homeless_stat'], hf['homeless_stat'], 's4_homeless_opt_',
                       more='rises', less='drops'))
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


# MEAN HOUSEHOLD INCOME, the dollar anchor for the VSL sentence in Section 3.3: CPS ASEC
# mean household income, in the dollars the text quotes.  One place, so the dollar value
# of the VSL moves with the target rather than being typed beside it.
MEAN_HH_INCOME_USD = 113000.0


def _floor_names():
    """The raised floor and what it does to the distribution: the lowest income, the floor
    as a multiple of the small unit's rent, and the bottom half's share of earnings and the
    median over the mean on the grid actually solved (sigma_y is fitted at SIG_FIT_FLOOR
    and held, so the share is no longer the target)."""
    import numpy as np
    y = np.asarray(C.YG, dtype=float)
    w = np.asarray(C.W, dtype=float); w = w / w.sum()
    o = np.argsort(y); y, w = y[o], w[o]
    mean = float((w * y).sum())
    cw = np.cumsum(w); k = int(np.searchsorted(cw, 0.5))
    bottom = float((w * y)[:k].sum() + (0.5 - (cw[k - 1] if k else 0.0)) * y[k])
    return dict(s_ylow=f'{y[0]:.2f}', s_floor_mult=f'{C.TRUNC_FLOOR:.1f}',
                s_bot50_real=f'{100 * bottom / mean:.1f}', s_med_mean=f'{y[k] / mean:.2f}')


def _sudhl_up(par, du=0.005):
    """The SUD share of the homeless with u1 raised by du, b refit so participation is
    where it was: the local answer to "does u1 raise the SUD share of the homeless"."""
    from calibrate import stats, bracket
    from stylized import with_
    ref = stats(par)['part']
    g = with_(par, u1=par.u1 + du)
    g = with_(g, b=bracket(g, 'b', 'part', 1e-5, 1.0, iters=20, tgt=ref))
    return stats(g)['sud_of_homeless2']


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
    # THE 30 SEPTEMBER SPECIFICATION: food assistance, the raised floor with sigma_y held,
    # the stylized VSL of 84 against the quantitative model's 80, and the dollar value.
    d.update(_floor_names())
    d.update(s_rho_fs=f'{p1.rho_fs:.2f}', s_fs_t_pc=f'{100 * stages.FS_TARGET:.2f}',
             s_t_vsl_musd=f'{T["vsl"] * MEAN_HH_INCOME_USD / 1e6:.1f}',
             s_mean_hh_usd=f'{MEAN_HH_INCOME_USD:,.0f}')
    for tag, par, raw in (('s1', p1, r1), ('s2', p2, r2)):
        m = raw['_moments']
        d.update({f'{tag}_v_aleph': f'{par.aleph:.2f}', f'{tag}_v_gam': f'{par.gam:.3f}',
                  f'{tag}_v_b': f'{par.b:.4f}', f'{tag}_v_th': f'{par.th:.3f}',
                  f'{tag}_v_smr': f'{_smr(par):.2f}', f'{tag}_v_h1': f'{par.h1:.4f}',
                  f'{tag}_v_u0': f'{par.u0:.4f}', f'{tag}_iter': f'{raw["_iteration"]}',
                  f'{tag}_worst': f'{raw["_worst_gap_pc"]:.1f}',
                  # u1 and its moment, which the text quotes per stage: in stage 2
                  # u1 sits on its floor, u0, and the share falls short there
                  f'{tag}_v_u1': f'{par.u1:.4f}',
                  f'{tag}_v_cbar': f'{par.cbar:.3f}',
                  # the share of the job losses of households with a SUD that the disorder
                  # causes and income support does not cover, (u1 - u0)/u1, and u1 over u0
                  f'{tag}_unins_pc': f'{100 * max(par.u1 - par.u0, 0.0) / par.u1:.0f}',
                  f'{tag}_u1_over_u0': f'{par.u1 / par.u0:.1f}'})
        if m.get('sud_of_homeless2') is not None:
            d[f'{tag}_m_sudhl_pc'] = f'{100 * m["sud_of_homeless2"]:.1f}'
            d[f'{tag}_sudhl_up_pc'] = f'{100 * _sudhl_up(par):.1f}'
        for k in ('vsl', 'hspend', 'part', 'dshare', 'r_use', 'homeless', 'unemployment',
                  'sud_of_homeless2', 'child_gap', 'child_sud_or', 'child_hl_or', 'sud', 'fshare'):
            if m.get(k) is not None:
                d[f'{tag}_m_{k}'] = (f'{m[k]:.1f}' if k == 'vsl' else f'{m[k]:.2f}'
                                     if k in ('r_use', 'child_sud_or', 'child_hl_or')
                                     else f'{100 * m[k]:.2f}')
    d['s2_v_omega'] = f'{p2.omega:.4f}'
    return d


# TABLES: TWO DECIMALS UNLESS THE THIRD MATTERS (the author, 29 September; NUMBERS.md,
# "Decimals").  Values below 0.1 keep two significant figures, since two decimals
# would print u0 = 0.0474 and u1 = 0.0486 alike and omega_c = 0.0014 as nothing.
def tn(x):
    import math
    x = float(x)
    if x == 0.0 or abs(x) >= 0.1:
        return f'{x:.2f}'
    return f'{x:.{1 - int(math.floor(math.log10(abs(x))))}f}'


def red(x):
    return r'\textcolor{red}{%s}' % x


def _prev_rows(name):
    """The rows of the table as the author last saw it, red stripped, keyed by the
    parameter cell. The snapshot is <name>_prev.tex beside this file; without one
    every cell is new."""
    import re as _re
    f = os.path.join(HERE, f'{name}_prev.tex')
    out = {}
    if not os.path.exists(f):
        return out
    for line in open(f):
        line = line.strip()
        if not line.endswith('\\\\') or line.startswith(('Parameter', ' &', '&')):
            continue
        cells = [_re.sub(r'\\textcolor\{red\}\{(.*)\}$', r'\1', c.strip())
                 for c in line[:-2].split(' & ')]
        out[cells[0]] = cells
    return out


def _row(r, prev):
    """RED MARKS WHAT MOVED (the author reads a round by its red): a cell is red only
    if it differs from the snapshot, and a row the snapshot lacks is red throughout."""
    old = prev.get(r[0])
    return ' & '.join(red(c) if (old is None or i >= len(old) or old[i] != c) else c
                      for i, c in enumerate(r)) + r' \\'


def write_tables(p1, r1, p2, r2):
    """Tables 1 and 2, red where a cell moved against the snapshot the author saw."""
    prev_ext, prev_int = _prev_rows('tab_external'), _prev_rows('tab_internal')
    ext = [('Preferences and demographics', [
        (r'$\beta$', 'Discount factor over a thirty-year period',
         f'${p1.beta ** (1 / p1.years):.3f}$ annually, compounded', f'${tn(p1.beta)}$'),
        (r'$R$', 'Gross return on saving', 'Zero percent interest', f'${p1.R:.2f}$'),
        (r'$\sigma$', 'Risk aversion', 'Standard; Attanasio and Weber (2010)', f'${p1.sigma:.0f}$'),
        (r'$\bar\phi$', 'Survival over a period, no SUD', 'SSA period life table, ages 26--55',
         f'${p1.phi0:.2f}$')]),
        ('The SUD', [
        (r'$\pi_d$', 'Chance that use starts a SUD', 'NSDUH 2024: SUD rate over participation',
         f'${tn(p1.pi_base)}$')]),
        ('Income', [
        (r'$\psi_{ui}$', 'Income support replacement rate', 'DOL, statutory UI rates', f'${p1.repl:.2f}$'),
        (r'$\bar y$', 'Cap on the earnings base', 'DOL, state benefit maxima', f'${p1.ycap:.2f}$'),
        (r'$\rho_F$', 'Food assistance taper', 'SNAP benefit reduction rate', f'${p1.rho_fs:.2f}$')]),
        # y_min's row removed, the author 30 September ("remove"): the floor on income is
        # not reported, in the table or in the text.
        ('Housing, drugs and the voucher', [
        (r'$p_r$', 'Rent per unit of housing services', 'Normalisation', f'${p1.pr:.2f}$'),
        (r'$p_v$', 'Price of a unit of drugs', 'Normalisation', f'${p1.p_v:.2f}$'),
        (r'$h_2$', 'Small rental unit', 'Externally set', f'${p1.h2:.2f}$'),
        (r'$h_3$', 'Standard rental unit', 'Externally set', f'${p1.h3:.2f}$'),
        (r'$\kappa_r$', "Tenant's share of the rent", 'HUD voucher rules', f'${p1.kappa_r:.2f}$'),
        (r'$\kappa_V$', 'Voucher means test', 'HUD income limits', f'${p1.kV:.2f}$'),
        (r'$\pi_V$', 'Chance of drawing a voucher', 'HUD 2023, recipients over eligible', f'${tn(p1.pV)}$')]),
        ('The child, stage 2 onward', [
        (r'$\xi$', 'Equivalence scale while the child is at home', 'Square-root scale', f'${p2.xi:.2f}$'),
        (r'$\rho$', 'Persistence of productivity across generations', 'Solon (1992); Mazumder (2005)',
         f'${p2.rho:.2f}$'),
        (r'$\delta_d$', "Child's productivity penalty, parent had a SUD",
         f'Nilsson (2017), a {100 * (1 - math.exp(-p2.delta_d)):.0f} percent cut', f'${tn(p2.delta_d)}$')])]
    L = [r'\footnotesize', r'\begin{tabular}{@{}lllr@{}}', r'\toprule',
         r'Parameter & Description & Source or rationale & Value \\', r'\midrule']
    for i, (hd, rows) in enumerate(ext):
        if i:
            L.append(r'\addlinespace')
        L.append(r'\multicolumn{4}{@{}l}{\emph{%s}} \\' % hd)
        for r in rows:
            L.append(_row(r, prev_ext))
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
        # the model column is the share on the grid actually solved: sigma_y is fitted at
        # the original floor and held when the floor is raised (calibrate.SIG_FIT_FLOOR)
        (r'$\sigma_y$', "Bottom half's share of earnings, SCF 2022", pct(T['bot50']),
         f"{_floor_names()['s_bot50_real']}\\%", tn(C.SIG), f"{_floor_names()['s_bot50_real']}\\%", tn(C.SIG)),
        (r'$\gamma$', 'Housing over non-drug expenditure, CEX 2024', pct(T['hspend']),
         mm(m1, 'hspend', pct), tn(p1.gam), mm(m2, 'hspend', pct), tn(p2.gam)),
        # THE TARGET COLUMN SAYS 80, THE QUANTITATIVE MODEL'S vsl_data, although aleph is
        # fitted to 84 (calibrate.TARGET): the author, 30 September, "just say 80, and the
        # calibration numbers are a bit off" / "put 80".  The model columns report what the
        # model delivers.
        (r'$\aleph$', 'VSL over income', f'{float(stages._fc()["vsl_data"]):.0f}',
         mm(m1, 'vsl', lambda x: f'{x:.1f}'), f'{p1.aleph:.2f}', mm(m2, 'vsl', lambda x: f'{x:.1f}'),
         f'{p2.aleph:.2f}'),
        (r'$b$', 'Drug participation, NSDUH 2024', pct(T['part']),
         mm(m1, 'part', pct), tn(p1.b), mm(m2, 'part', pct), tn(p2.b)),
        (r'$\theta$', 'Drug spending over users\' income', pct(stages.DSHARE_TARGET),
         mm(m1, 'dshare', pct), tn(p1.th), mm(m2, 'dshare', pct), tn(p2.th)),
        (r'$\kappa_{\phi d}$', "Users' income over the average, NSDUH 2024", f'{T["r_use"]:.2f}',
         mm(m1, 'r_use', lambda x: f'{x:.2f}'), f'{_smr(p1):.2f}', mm(m2, 'r_use', lambda x: f'{x:.2f}'),
         f'{_smr(p2):.2f}'),
        (r'$h_1$', 'Homelessness rate', pct(T['homeless']),
         mm(m1, 'homeless', pct), tn(p1.h1), mm(m2, 'homeless', pct), tn(p2.h1)),
        (r'$u_0$', 'Unemployment rate, BLS CPS 2014--24', pct(0.0485),
         mm(m1, 'unemployment', pct), tn(p1.u0), mm(m2, 'unemployment', pct), tn(p2.u0)),
        (r'$u_1$', 'SUD share of the homeless, Gutwinski et al.\\ (2021)',
         pct(T['sud_of_homeless2']), mm(m1, 'sud_of_homeless2', pct), tn(p1.u1),
         mm(m2, 'sud_of_homeless2', pct), tn(p2.u1)),
        (r'$\bar c$', 'Food stamp spending over labour income', f'{100 * stages.FS_TARGET:.2f}\\%',
         mm(m1, 'fshare', lambda x: f'{100 * x:.2f}\\%'), tn(p1.cbar),
         mm(m2, 'fshare', lambda x: f'{100 * x:.2f}\\%'), tn(p2.cbar)),
        (r'$\omega_c$', 'Use of non-parents over parents, less one, NSDUH 2024', pct(0.1834),
         '--', '--', mm(m2, 'child_gap', pct), tn(p2.omega)),
    ]
    # ONE LINE A ROW (the author, 29 September): the target column is l, not a
    # fixed-width paragraph column that wrapped the longer moments onto two lines.
    L = [r'\footnotesize\setlength{\tabcolsep}{4pt}',
         r'\begin{tabular}{@{}llrrrrr@{}}', r'\toprule',
         r' & & & \multicolumn{2}{c}{Stage 1} & \multicolumn{2}{c}{Stage 2} \\',
         r'\cmidrule(lr){4-5}\cmidrule(l){6-7}',
         r'Parameter & Target moment & Data & Model & Value & Model & Value \\', r'\midrule']
    for r in rows:
        L.append(_row(r, prev_int))
    L += [r'\bottomrule', r'\end{tabular}']
    open(os.path.join(TAB, 'tab_internal.tex'), 'w').write(
        '% Generated by code/stylized/stage_results.py from the stage calibrations.\n'
        + '\n'.join(L) + '\n')


def write_stage1_table():
    """Table 3: the two forces and dominance at stage 1, which replaces Figure 2.
    Every cell red: the table is new."""
    d = json.load(open(OUT))
    g = lambda k: d[k]
    # THE RATIONED CASE ONLY (the author, 29 September: "in table 3 there is no need
    # to do universal coverage case", "just TF vs HF with rationing").  None stays,
    # because the value-of-life force is Treatment First against no programme.
    # ...and no column head naming the rationing: both programmes are rationed.
    L = [r'\footnotesize', r'\begin{tabular}{@{}lccc@{}}', r'\toprule',
         r' & None & TF & HF \\', r'\midrule',
         r'\multicolumn{4}{@{}l}{\emph{Panel A. Outcomes, percent of households}} \\']
    # "Drug use", not "Drug participation" (the author, 29 September).  Cells carry the
    # prose's precision (fill.text_precision), so 3.752 in the text is 3.75 here too.
    from fill import text_precision as _tp
    g = lambda k: _tp(k, d[k])
    for lab, k in (('Drug use', 'part'), ('Carrying a SUD', 'sud'), ('Homeless', 'homeless')):
        L.append(r'\quad ' + lab + ' & ' + ' & '.join(g(f's1_{k}_{p}_b')
                                                   for p in ('none', 'tf', 'hf')) + r' \\')
    L += [r'\addlinespace',
          r'\multicolumn{4}{@{}l}{\emph{Panel B. The two forces on participation, percentage points}} \\',
          r'\quad Value of life, TF less none & & ' + g('s1_vol_b') + r' & \\',
          r'\quad Moral hazard, HF less TF & & & ' + g('s1_mh_b') + r' \\',
          r'\addlinespace',
          r'\multicolumn{4}{@{}l}{\emph{Panel C. Treatment First against Housing First}} \\',
          r'\quad Households strictly worse off, percent & & ' + g('s1_worse_b') + r' & \\',
          r'\quad Households strictly better off, percent & & ' + g('s1_better_b') + r' & \\',
          r'\quad CEV of those affected, percent & & $-' + g('s1_cevaff_b') + r'$ & \\',
          r'\quad CEV of the population, percent & & $-' + g('s1_cevpop_b') + r'$ & \\',
          r'\bottomrule', r'\end{tabular}']
    # RED MARKS WHAT MOVED, cell by cell against the table as the author last saw it
    # (tab_stage1_prev.tex), matched by ROW POSITION so a relabelled row keeps its
    # unchanged numbers black.  It used to be red throughout because it was new.
    import re as _re
    def _cells(line):
        return [_re.sub(r'\\textcolor\{red\}\{(.*)\}$', r'\1', c.strip())
                for c in line.rstrip()[:-2].split('&')]
    def _is_row(line):
        return (line.rstrip().endswith('\\\\') and not line.startswith('\\multicolumn')
                and not line.startswith(' &'))
    pf = os.path.join(HERE, 'tab_stage1_prev.tex')
    prev = [_cells(l) for l in open(pf) if _is_row(l)] if os.path.exists(pf) else []
    out, i = [], 0
    for line in L:
        if not _is_row(line):
            out.append(line)
            continue
        cur = _cells(line)
        old = prev[i] if i < len(prev) else None
        i += 1
        def one(j, c):
            if not c:
                return ''
            if _re.fullmatch(r'-[0-9.]+', c):
                c = f'${c}$'
            same = old is not None and j < len(old) and old[j] == c
            return c if same else red(c)
        out.append(' & '.join(one(j, c) for j, c in enumerate(cur)) + r' \\')
    body = '\n'.join(out) + '\n'
    open(os.path.join(TAB, 'tab_stage1.tex'), 'w').write(
        '% Generated by code/stylized/stage_results.py from stage 1.\n' + body)


# THE INTRODUCTION QUOTES TWO DECIMALS, the author, 29 September: "no need to have 3
# decimals in the intro. i am referring to all numbers not just this".  Each name the
# introduction reads at more than two decimals gets an '_i' twin here, so the sections
# that quote the same number keep their precision and the two can never disagree.
INTRO_2DP = ('s2_homeless_hf', 's2_homeless_tf', 's4_tr_c1')


def merge(d):
    old = json.load(open(OUT)) if os.path.exists(OUT) else {}
    old.update(d)
    for k in INTRO_2DP:
        if k in old:
            old[k + '_i'] = f'{float(old[k]):.2f}'
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
        run.draw_who_uses(c['scale'], c, r_cal=c.get('r_cal'), part_ref=c.get('part_ref'))
        if c.get('part_ref') is not None:
            merge(revstart_names(c['scale'], c['mortality'], c['part']['mortality'],
                                 c['part_ref']))
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
        # how much of the distance to the omega_c = 1 allocation Treatment First closes
        import run
        d['s4_close_frac'] = run._fraction_word(float(d['s3_cev_tf']) / float(d['s4_cev_opt']))
    merge(d)
    for k in sorted(d):
        if not k.startswith('_'):
            print(f'   {k:22s} {d[k]}')
