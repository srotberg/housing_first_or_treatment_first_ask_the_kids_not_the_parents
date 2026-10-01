"""
The long run under each policy, side by side: Table tab:longrun and the x_lr_* names.

usage: python3 code/paper/export_longrun.py [--freeze]
       -> writing/tables/tab_longrun.tex (the tabular; caption and note are in the paper)
       -> x_lr_* merged into code/paper/results_numbers.json
       --freeze snapshots the printed cells into tab_longrun_prev.json, the baseline a
       later run marks red against (no snapshot: every cell is red, the table is new)

Four steady states, each the one saved equilibrium of its arm (the exit pass):

  Housing First          results/counterfactuals_cf_fix2/null_share   the benchmark, re-solved
                                                                     on the counterfactual build
  Treatment First        tf85        85 per cent detection, pi_V clears the budget
  ... elastic supply     elast5_85   the same with a drug supply elasticity of 5
  Housing First, w_c=1   omega1      the parent weighs its child as itself; pi_V held at the
                                     benchmark's, so net revenue is NOT held (no CEV: the
                                     author asked for none on this arm, since omega_c changes
                                     the welfare function itself)

EACH ARM IS COMPARED WITH ITS OWN NO-POLICY RUN: tf85 with null_share, elast5_85 and omega1
with null_remote, the benchmark re-solved on the container they ran on (3.8e-7 relative from
null_share's).  The CEV is the arm's CEV off the benchmark's curve LESS its no-policy run's
(+0.027 per cent, what the counterfactual code produces with no policy at all), so that it is
measured against the same run as every other change here and as the childhood/adult split.

Children are households aged 26 to 50, the years a child is at home, mass-weighted, from the
last DIAG age profile each run printed (the definitions export_results.py uses):
  in a shelter        DIAG age homeless=
  parent using drugs  DIAG age sud=, which is drug CONSUMPTION (is_addicted = consumes)
  parent with a SUD   DIAG disorder rate, band k (26-34, 35-44, 45-54), each age its band's

The adult part of the newborn's gain splits in two (ADULTDECOMP, cf_fix2 build): the newborns
move out of the penalised productivity block (composition, at the no-policy values), and the
value at 26 rises at a given block (within).  The value at 26 by productivity node, benchmark
and Treatment First, is copied from code/cfarm_tf_fix2_85 (untracked) into tf85/ as
value_at_26_by_node_{benchmark,tf85}.txt: nodes 1-13 with a clean parent, 14-26 penalised.
"""
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
RES = os.path.join(ROOT, 'results', 'counterfactuals_cf_fix2')
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
TAB = os.path.join(ROOT, 'writing', 'tables', 'tab_longrun.tex')
PREV = os.path.join(HERE, 'tab_longrun_prev.json')
ARMS = (('null_share', None), ('tf85', 'null_share'), ('elast5_85', 'null_remote'),
        ('omega1', 'null_remote'))
# the columns of the table: the elastic supply is a footnote (the author, 30 September)
TABLE = (('null_share', None), ('tf85', 'null_share'), ('omega1', 'null_remote'))


def log(arm):
    with gzip.open(os.path.join(RES, arm, 'cf.log.gz'), 'rt', errors='replace') as f:
        return f.read().splitlines()


def final(arm):
    """the levels of an arm's final.txt, first column (the arm), by label"""
    rows = {}
    for l in open(os.path.join(RES, arm, 'final.txt')):
        m = re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l)
        if m:
            rows[m.group(1).strip()] = float(m.group(2))
        m = re.search(r'childhood ([+-]\S+), adult part ([+-]\S+), total ([+-]\S+)', l)
        if m:
            rows['split'] = tuple(float(m.group(i)) for i in (1, 2, 3))
    return rows


def steady(arm):
    L = log(arm)
    ages, band, cev, ad = {}, {}, None, {}
    for l in L:
        m = re.search(r'DIAG age\s+(\d+)\s+homeless=\s*(\S+).*sud=\s*(\S+)\s+mass=\s*(\S+)', l)
        if m:
            ages[int(m.group(1))] = tuple(float(m.group(i)) for i in (2, 3, 4))
        m = re.search(r'DIAG disorder rate, band\s+(\d)\s+=\s*(\S+)', l)
        if m:
            band[int(m.group(1))] = float(m.group(2))
        if 'CEV from the saved benchmark curve' in l:
            cev = float(l.split('x=')[1])
        if 'ADULTDECOMP mass type' in l:
            ad['mass'] = [float(x) for x in l.split()[4:]]
        if 'ADULTDECOMP vf type' in l:
            ad['vf'] = [float(x) for x in l.split()[4:]]
    hb = {}
    for l in L:
        m = re.search(r'UNTARGETED homelessness rate, band\s+(\d)\s+model=\s*(\S+)', l)
        if m:
            hb[int(m.group(1))] = float(m.group(2))
    P = [a for a in ages if 26 <= a <= 50]
    W = sum(ages[a][2] for a in P)
    k = lambda a: 1 if a <= 34 else 2 if a <= 44 else 3
    return dict(
        child_hl=sum(ages[a][0] * ages[a][2] for a in P) / W,
        par_use=sum(ages[a][1] * ages[a][2] for a in P) / W,
        par_sud=sum(band[k(a)] * ages[a][2] for a in P) / W,
        cev=cev, adult=ad, hl_band=hb)


def nodes(name):
    return [float(x) for x in open(os.path.join(RES, 'tf85', f'value_at_26_by_node_{name}.txt'))
            if x.strip()]


def main():
    freeze = '--freeze' in sys.argv
    D = {}
    for arm, base in ARMS + (('null_remote', None),):
        f = final(arm)
        D[arm] = dict(steady(arm), price=f['drug price'], piv=f['pi_V (voucher probability)'],
                      b=f['drug use b'], sud=f['SUD lambda_d'], h=f['homelessness h_1'],
                      sud_hl=f['SUD share of the homeless'], takeup=f['treatment take-up'],
                      net=f['net government revenue'], split=f.get('split'))
    for arm, base in ARMS[1:]:
        D[arm]['cev_net'] = 100 * (D[arm]['cev'] - D[base]['cev'])
    # beta^25, the discount on the adult part, from the calibrated factor the run used
    beta = [float(l.split('=')[1]) for l in log('tf85') if l.startswith(' discount_factor=')][-1]
    beta25 = beta ** 25

    out = {}
    pc = lambda arm, key, base: 100 * (D[arm][key] / D[base][key] - 1)
    # the table: levels, per cent unless the row says otherwise
    rows = [
        ('Drug price, benchmark $=1$', 'price', lambda v: f'{v:.2f}'),
        ('Voucher probability $\\pi_V$', 'piv', lambda v: f'{100 * v:.2f}'),
        ('Drug use', 'b', lambda v: f'{100 * v:.2f}'),
        ('Carrying a SUD', 'sud', lambda v: f'{100 * v:.2f}'),
        ('Homelessness', 'h', lambda v: f'{100 * v:.2f}'),
        ('SUD share of the homeless', 'sud_hl', lambda v: f'{100 * v:.1f}'),
        ('In treatment, of those with a SUD', 'takeup', lambda v: f'{100 * v:.1f}'),
        None,
        ('Living with a parent who uses drugs', 'par_use', lambda v: f'{100 * v:.2f}'),
        ('Living with a parent who carries a SUD', 'par_sud', lambda v: f'{100 * v:.2f}'),
        ('In a shelter', 'child_hl', lambda v: f'{100 * v:.2f}'),
        None,
        ('CEV of a newborn, percent of lifetime consumption', 'cev_net', lambda v: f'{v:.2f}'),
        ('Share of the newborn\'s gain that comes in childhood', 'child_share', lambda v: f'{v:.0f}'),
    ]
    for arm, base in ARMS[1:]:
        s = D[arm]['split']
        D[arm]['child_share'] = 100 * s[0] / s[2] if s and arm != 'omega1' else None
    D['omega1']['cev_net'] = None
    try:
        prev = json.load(open(PREV))
    except (OSError, ValueError):
        prev = {}
    cells, body = {}, []
    heads = {1: '\\multicolumn{4}{@{}l}{\\emph{Adults}} \\\\',
             2: '\\multicolumn{4}{@{}l}{\\emph{Children, households aged 26 to 50}} \\\\',
             3: '\\multicolumn{4}{@{}l}{\\emph{Welfare}} \\\\'}
    body.append(heads[1])
    part = 1
    for r in rows:
        if r is None:
            part += 1
            body.append('\\addlinespace')
            body.append(heads[part])
            continue
        lab, key, fmt = r
        line = [lab]
        for arm, _ in TABLE:
            v = D[arm].get(key)
            c = '--' if v is None else fmt(v)
            cells[f'{key}/{arm}'] = c
            line.append(c if prev.get(f'{key}/{arm}') == c else f'\\textcolor{{red}}{{{c}}}')
        body.append(' & '.join(line) + ' \\\\')
    tab = ['% Written by code/paper/export_longrun.py from results/counterfactuals_cf_fix2;',
           '% edit the script, not this file. Caption and note are in the paper.',
           '\\begin{tabular}{@{}L{190pt}rrr@{}}', '\\toprule',
           ' & Housing & Treatment & Housing First, \\\\',
           ' & First & First & $\\omega_c=1$ \\\\',
           '\\midrule'] + body + ['\\bottomrule', '\\end{tabular}']
    open(TAB, 'w').write('\n'.join(tab) + '\n')
    if freeze:
        json.dump(cells, open(PREV, 'w'), indent=1)

    # ---- names for the prose
    t, e, o = 'tf85', 'elast5_85', 'omega1'
    out['x_lr_om_b_pc'] = f"{abs(pc(o, 'b', 'null_remote')):.0f}"
    out['x_lr_tf_b_pc'] = f"{abs(pc(t, 'b', 'null_share')):.0f}"
    # how much of full altruism's fall in drug use Treatment First delivers
    out['x_lr_tf_of_om_pc'] = f"{100 * pc(t, 'b', 'null_share') / pc(o, 'b', 'null_remote'):.0f}"
    out['x_lr_om_h_pc'] = f"{abs(pc(o, 'h', 'null_remote')):.0f}"
    out['x_lr_om_h_dir'] = 'falls' if D[o]['h'] < D['null_remote']['h'] else 'rises'
    out['x_lr_om_hchild_pc'] = f"{abs(pc(o, 'child_hl', 'null_remote')):.0f}"
    out['x_lr_om_hchild_dir'] = 'falls' if D[o]['child_hl'] < D['null_remote']['child_hl'] else 'rises'
    out['x_lr_om_net_pc'] = f"{abs(pc(o, 'net', 'null_remote')):.1f}"
    # homelessness by age band under Treatment First: 26-34 against 35-44
    hb0, hb1 = D['null_share']['hl_band'], D[t]['hl_band']
    out['x_lr_hl_b1_pc'] = f'{100 * (hb1[1] / hb0[1] - 1):.0f}'
    out['x_lr_hl_b2_pc'] = f'{100 * (hb1[2] / hb0[2] - 1):.0f}'
    # the newborn's gain: net CEV, and the adult part's composition share
    out['x_lr_e5_cev'] = f"{D[e]['cev_net']:.2f}"
    out['x_lr_e5_b_pc'] = f"{abs(pc(e, 'b', 'null_remote')):.0f}"
    out['x_lr_e5_h_pc'] = f"{abs(pc(e, 'h', 'null_remote')):.0f}"
    out['x_lr_e5_price_pc'] = f"{abs(pc(e, 'price', 'null_remote')):.0f}"
    out['x_lr_e5_child_pc'] = f"{D[e]['child_share']:.0f}"
    out['x_lr_e5_cev_dir'] = 'rises' if D[e]['cev_net'] > D[t]['cev_net'] else 'falls'
    # the supply elasticity the arm ran at, from its handover (the benchmark's is f_drug_supply_elasticity)
    ho = dict(l.split()[:2] for l in open(os.path.join(RES, e, 'PARAM_HANDOVER.arm.txt')) if len(l.split()) >= 2)
    out['x_lr_e5_elast'] = f"{float(ho['drug_supply_elasticity']):g}"
    out['x_lr_paruse_dir'] = 'falls' if D[t]['par_use'] < D['null_share']['par_use'] else 'rises'
    out['x_lr_paruse0'] = f"{100 * D['null_share']['par_use']:.2f}"
    out['x_lr_paruse1'] = f"{100 * D[t]['par_use']:.2f}"
    out['x_lr_hl_b2_dir'] = 'rises' if hb1[2] > hb0[2] else 'falls'
    out['x_lr_e5_h_dir'] = 'rises' if D[e]['h'] > D['null_remote']['h'] else 'falls'
    # whether full altruism and Treatment First move homelessness the same way
    same = (D[o]['h'] > D['null_remote']['h']) == (D[t]['h'] > D['null_share']['h'])
    out['x_lr_h_split'] = 'move together on' if same else 'part ways on'
    m0, v0 = D['null_share']['adult']['mass'], D['null_share']['adult']['vf']
    m1, v1 = D[t]['adult']['mass'], D[t]['adult']['vf']
    # blocks: [clean parent, -, penalised, -]
    gap = v0[0] - v0[2]
    comp = (m0[2] - m1[2]) * gap
    tot = (m1[0] * v1[0] + m1[2] * v1[2]) / (m1[0] + m1[2]) - (m0[0] * v0[0] + m0[2] * v0[2]) / (m0[0] + m0[2])
    adult_utils = D[t]['split'][1]
    assert abs(tot * beta25 / adult_utils - 1) < 0.02, \
        f'ADULTDECOMP {tot * beta25:.4f} does not reproduce the adult part {adult_utils:.4f}'
    out['x_lr_draw_pc'] = f'{100 * comp / tot:.0f}'
    out['x_lr_draw_rest'] = 'larger' if comp / tot < 0.5 else 'smaller'
    # the value of entering adult life, by productivity node: bottom against top, clean parent
    nb, nt = nodes('benchmark'), nodes('tf85')
    g = [a - b for a, b in zip(nt, nb)]
    out['x_lr_v26_ratio'] = f'{g[0] / g[12]:.0f}'
    out['x_lr_v26_all_up'] = 'every' if min(g) > 0 else 'not every'

    d = json.load(open(OUT_JSON))
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    print(f'wrote {TAB} and {len(out)} x_lr_* names')
    for k, v in sorted(out.items()):
        print(f'  {k} = {v}')


if __name__ == '__main__':
    main()
