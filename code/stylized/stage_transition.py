"""
Stage 4's transition: Housing First to Treatment First at the benchmark pi_V, in
the model with the child (stage 2's calibration), for EVERY generation alive at
the reform and every one after it.

usage:  STYLIZED_WORKERS=2 python3 stage_transition.py   -> merges s4_tr_* into stage_numbers.json
                                                          and draws writing/figures/stylized_transition

WHO IS ALIVE WHEN THE RULE CHANGES (TRANSITION_LESSONS section 1: a cohort path
is not a transition).  The rule lands at the start of a period.

  THE OLD, in period 2.  They chose whether to use under the old rule, carry
  whatever disorder that choice left them, and cannot recover in a terminal
  period; under Treatment First the condition now withdraws the voucher from
  those carrying one.  Their loss is over period 2 alone.

  THE YOUNG, in period 1, with their children at home.  Their own draw was set by
  their parents, the old, before the reform, so they are born into the old
  mixture; they choose under the new rule.  Their loss is over their adult life.

  THE NEWBORN COHORTS.  Cohort 1 is the young's children: its childhood is lived
  under the new rule in its parents' household, and its own draw is the first to
  depend on choices made under the new rule, since the penalty keys on the
  disorder a parent acquires by the end of period 1.  From cohort 2 the chain is
  under the new rule throughout.  optimal_sud.transition computes these rows.

WELFARE is each group's own remaining life, as a CEV against what the old rule
would have given it, with the corrected accounting of stage_results.py: a
newborn's life is childhood plus beta times adulthood, and every additive
constant is in A.  transition.caught computes the old's value difference but
calls cev() without the level cev() needs at sigma = 2, so it raises; the level
is carried here.

kappa_x IS LEFT OUT OF THE PATH.  Along a transition H is an aggregate over two
generations at every date, and in the long run kappa_x moves the Treatment First
CEV by about one hundredth of a point (stage_results s3), so the path is
reported without it and the text says so.
"""
import json
import os
import sys

import numpy as np

import stages                      # the exact zero child-damage shortcut
import stylized as ST
from stylized import with_, period1, solve_period2, _pid, _shares
import calibrate as C
import transition as T
import optimal_sud as O
import stage_results as R

HERE = os.path.dirname(os.path.abspath(__file__))
WW = C.W / C.W.sum()


def _ex(par):
    return _shares(par)[0] * (1.0 - par.sigma)


def old_generation(par, pv_new):
    """The old at the reform: E[W2] under the old rule and under each new one,
    integrating over the assets they saved and the disorder they drew under it."""
    old = T._ready(par, 'HF', par.pV)
    new_h = T._ready(par, 'HF', pv_new)
    new_t = T._ready(par, 'TF', pv_new)
    v1b, sudb, hlb, evb = T._policy_grids(par, 'HF', par.pV)
    p_mix = T._rest_point(sudb, T._hl_by_shift(par, 'HF', par.pV), par)
    acc = dict(wo=0.0, wh=0.0, wt=0.0, hlo=0.0, hlh=0.0, hlt=0.0, m=0.0)
    for sft, psft in zip(T._shifts(par), p_mix):
        if psft <= 0.0:
            continue
        for i, y0 in enumerate(C.YG):
            y = y0 * sft
            for p, gain, v, bu, bn, inc, _own in period1(old, y, 'HF'):
                uses = gain > 0.0
                a = (bu if uses else bn)[0]
                pid = float(_pid(old, v)) if uses else 0.0
                agh, W2h, H2h, _, _, _ = solve_period2(new_h, y, 'HF', used=int(uses))
                agt, W2t, H2t, _, _, _ = solve_period2(new_t, y, 'TF', used=int(uses))
                ago, W2o, H2o, _, _, _ = solve_period2(old, y, 'HF', used=int(uses))
                for d, pd in ((1, pid), (0, 1.0 - pid)):
                    m = psft * WW[i] * p * pd
                    if m <= 0.0:
                        continue
                    acc['wo'] += m * float(np.interp(a, ago, W2o[:, d]))
                    acc['wh'] += m * float(np.interp(a, agh, W2h[:, d]))
                    acc['wt'] += m * float(np.interp(a, agt, W2t[:, d]))
                    acc['hlo'] += m * float(np.interp(a, ago, H2o[:, d]))
                    acc['hlh'] += m * float(np.interp(a, agh, H2h[:, d]))
                    acc['hlt'] += m * float(np.interp(a, agt, H2t[:, d]))
                    acc['m'] += m
    M = acc.pop('m')
    a = {k: v / M for k, v in acc.items()}
    U = a['wo'] - par.aleph                   # period 2 carries aleph once
    cev = lambda w: (1.0 + (w - a['wo']) / U) ** (1.0 / _ex(par)) - 1.0
    return dict(cev_tf=cev(a['wt']), cev_hf=cev(a['wh']),
                hl_old=a['hlo'], hl_hf=a['hlh'], hl_tf=a['hlt'])


def run(par, policy_new, n=8):
    """The young at the reform and the newborn cohorts, against the old rule."""
    rows, b = O.transition(par, n=n, par_old=par, policy_new=policy_new, policy_old='HF')
    ex = _ex(par)
    pi = par.pi_base * R.stats(R.ready(par))['part']
    aw = R._aw(par, pi)
    # the young at the reform: adult life only, at the OLD mixture p0
    _q, a_old, _k = O.grids(par, 'HF', par.pV)
    _q, a_new, _k = O.grids(par, policy_new, par.pV)
    v1o, sud_o, hl_o, ev_o = T._policy_grids(par, 'HF', par.pV)
    p0 = T._rest_point(sud_o, T._hl_by_shift(par, 'HF', par.pV), par)
    ad_old = O._mix(p0, a_old, par)
    ad_new = O._mix(p0, a_new, par)
    U_ad = ad_old - par.aleph * aw
    young = (1.0 + (ad_new - ad_old) / U_ad) ** (1.0 / ex) - 1.0
    # the newborn cohorts: childhood plus beta times adulthood, against the old rest point
    life0 = b['kid0'] + par.beta * b['adult0']
    U0 = life0 - par.aleph * ((par.xi - 1.0) + par.beta * aw)
    coh = []
    for r in rows:
        life = r['childhood'] + par.beta * r['adult']
        coh.append(dict(cohort=r['cohort'], cev=(1.0 + (life - life0) / U0) ** (1.0 / ex) - 1.0,
                        cev_kid=(1.0 + (r['childhood'] - b['kid0']) / U0) ** (1.0 / ex) - 1.0,
                        cev_adult=(1.0 + par.beta * (r['adult'] - b['adult0']) / U0) ** (1.0 / ex) - 1.0,
                        sud=r['sud'], homeless=r['homeless']))
    return young, coh, b


def paths(par, n=8):
    """What each cohort does on the path: drug use, the SUD and homelessness of the
    adults in period 1 from the young at the reform (cohort 0, born into the old
    mixture, choosing under the new rule) onward, with the Housing First rest point
    beside them. The mixture steps exactly as optimal_sud.transition steps it."""
    q_o = T._ready(par, 'HF', par.pV)
    q_n = T._ready(par, 'TF', par.pV)
    use_o = np.array([ST.use_prob(q_o, y, 'HF') for y in C.YG], dtype=float)
    use_n = np.array([ST.use_prob(q_n, y, 'TF') for y in C.YG], dtype=float)
    v1o, sud_o, hl_o, ev_o = T._policy_grids(par, 'HF', par.pV)
    v1n, sud_n, hl_n, ev_n = T._policy_grids(par, 'TF', par.pV)
    hls_n = T._hl_by_shift(par, 'TF', par.pV)
    p0 = T._rest_point(sud_o, T._hl_by_shift(par, 'HF', par.pV), par)
    base = dict(part=T._outcome(p0, use_o, par), sud=T._outcome(p0, sud_o, par),
                homeless=T._outcome(p0, hl_o, par))
    rows, p = [], p0.copy()
    for t in range(0, n + 1):
        rows.append(dict(cohort=t, part=T._outcome(p, use_n, par),
                         sud=T._outcome(p, sud_n, par), homeless=T._outcome(p, hl_n, par)))
        p = T._step(p, sud_n, hls_n, par)
    return rows, base


def figure(tr, out='stylized_transition'):
    """The stage 4 transition in four panels: drug use, the SUD and homelessness by
    cohort against the Housing First rest point, and the CEV of every generation,
    the old and the young at the reform included."""
    import run
    plt = run.style()
    fig, axs = plt.subplots(2, 2, figsize=(8.6, 6.0))
    rows, base = tr['rows'], tr['base']
    t = [r['cohort'] for r in rows]
    for ax, key, title in ((axs[0, 0], 'part', '(a) Drug use'),
                           (axs[0, 1], 'sud', '(b) Carrying a SUD'),
                           (axs[1, 0], 'homeless', '(c) Homeless')):
        ax.plot(t, [100 * r[key] for r in rows], '-o', color='#2C6FAD', ms=4.5,
                label='Treatment First, by cohort')
        ax.axhline(100 * base[key], color='#D9822B', ls='--', lw=1.6,
                   label='Housing First')
        ax.set_title(title, fontsize=10.5, loc='left')
        ax.set_ylabel('percent of adults')
        ax.set_xticks(t)
        ax.set_xticklabels(['young\nat reform' if c == 0 else str(c) for c in t], fontsize=8.5)
        lo = min(min(100 * r[key] for r in rows), 100 * base[key])
        hi = max(max(100 * r[key] for r in rows), 100 * base[key])
        pad = 0.15 * (hi - lo) if hi > lo else 0.5
        ax.set_ylim(max(0.0, lo - pad), hi + pad)
    axs[0, 0].legend(fontsize=8, loc='best')
    ax = axs[1, 1]
    labs = ['old', 'young'] + [str(c['cohort']) for c in tr['cohorts']]
    vals = [tr['old'], tr['young']] + [c['cev'] for c in tr['cohorts']]
    cols = ['#B5443B' if v < 0 else '#2C6FAD' for v in vals]
    ax.bar(range(len(vals)), [100 * v for v in vals], color=cols, width=0.62)
    ax.axhline(0.0, color='0.3', lw=1.0)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labs, fontsize=8.5)
    ax.set_title('(d) Welfare, CEV', fontsize=10.5, loc='left')
    ax.set_ylabel('percent of consumption')
    for ax in (axs[1, 0], axs[1, 1]):
        ax.set_xlabel('generation: alive at the reform, then cohorts born after it')
    fig.tight_layout()
    run.save(fig, out)


def main():
    par, raw = R.load(2)
    print(f'stage 2 calibration, iteration {raw["_iteration"]}')
    # THE NULL TEST FIRST: Housing First to Housing First must be zero for everyone
    y0, c0, _ = run(par, 'HF', n=4)
    o0 = old_generation(par, par.pV)
    worst = max([abs(y0), abs(o0['cev_hf'])] + [abs(c['cev']) for c in c0])
    print(f'NULL TEST, HF to HF: worst |CEV| = {100 * worst:.2e} per cent')
    if worst > 1e-8:
        print('   young', y0, 'old', o0['cev_hf'], 'cohorts', [c['cev'] for c in c0])
        raise SystemExit('NULL TEST FAILED: not reporting a transition')
    young, coh, b = run(par, 'TF', n=8)
    old = old_generation(par, par.pV)
    d = {'s4_tr_old': R.pc(old['cev_tf'], 3), 's4_tr_old_abs': R.pc(abs(old['cev_tf']), 2),
         's4_tr_young_abs': R.pc(abs(young), 3),
         's4_tr_old_hl_tf': R.pc(old['hl_tf'], 3),
         's4_tr_old_hl_hf': R.pc(old['hl_old'], 3), 's4_tr_young': R.pc(young, 3)}
    for c in coh:
        t = c['cohort']
        d[f's4_tr_c{t}'] = R.pc(c['cev'], 3)
        d[f's4_tr_c{t}_kid'] = R.pc(c['cev_kid'], 3)
        d[f's4_tr_c{t}_adult'] = R.pc(c['cev_adult'], 3)
        d[f's4_tr_c{t}_sud'] = R.pc(c['sud'], 3)
        d[f's4_tr_c{t}_hl'] = R.pc(c['homeless'], 3)
    d['s4_tr_sud0'] = R.pc(b['sud0'], 3)
    # THE FIGURE (the author, 29 September: "you can show homelessness, drug use,
    # SUD, CEV"), from the same path, with its series kept for a redraw
    rows, base = paths(par, n=8)
    tr = dict(rows=rows, base=base, old=old['cev_tf'], young=young,
              cohorts=[dict(cohort=c['cohort'], cev=c['cev']) for c in coh])
    d['_s4_tr_figure'] = tr
    figure(tr)
    d['s4_tr_hl0'] = R.pc(b['homeless0'], 3)
    R.merge(d)
    for k in sorted(d):
        print(f'   {k:22s} {d[k]}')


if __name__ == '__main__':
    main()
