"""
What Section 3 reports at each stage of the stylized model, computed at that
stage's own calibration (stages.py), and written as s<stage>_<name> for fill.py.

usage:  STYLIZED_WORKERS=1 python3 stage_results.py 1 [--no-figure]
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
        import run
        sc, curves, parts = run.fig_who_uses(par)
        mort, unem = np.asarray(curves['mortality']), np.asarray(curves['unemployment'])

        def at(c, s):
            return float(c[int(np.argmin(np.abs(sc - s)))])
        d.update(s1_r_off=f'{at(mort, 0.0):.2f}', s1_r_mort=f'{at(mort, 1.0):.2f}',
                 s1_r_mort_half=f'{at(mort, 0.5):.2f}', s1_r_unemp=f'{at(unem, 1.0):.2f}',
                 s1_r_unemp_hi=f'{at(unem, run.SCAN_HI):.2f}',
                 s1_scanhi_pc=f'{100 * run.SCAN_HI:.0f}')
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


def _const(par, pi, kx=0.0, H=0.0):
    """The additive part of a newborn's lifetime value: aleph and -kappa_x H,
    in childhood (xi - 1 of the household) and over the adult life."""
    per = (par.xi - 1.0) + par.beta * _aw(par, pi)
    return par.aleph * per - kx * H * per


def life(par, e, kx=0.0):
    pi = par.pi_base * e['part']
    per = (par.xi - 1.0) + par.beta * _aw(par, pi)
    return e['kid'] + par.beta * e['adult'] - kx * e['homeless_stat'] * per


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


def merge(d):
    old = json.load(open(OUT)) if os.path.exists(OUT) else {}
    old.update(d)
    json.dump(old, open(OUT, 'w'), indent=1, sort_keys=True)


if __name__ == '__main__':
    stage = int(sys.argv[1])
    par, raw = load(stage)
    print(f'stage {stage}: calibrated_stage{stage}.json, iteration {raw["_iteration"]}, '
          f'worst gap {raw["_worst_gap_pc"]} per cent')
    if stage == 1:
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
