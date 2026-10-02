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
        ('omega1', 'null_remote'), ('internalise', 'null_remote'))
# the columns of the table: the elastic supply is a footnote (the author, 30 September); optimal
# homelessness added as a fourth column (the author, 2 October: "You should also add the column for
# omega_c=1 and internalization of homelessness")
TABLE = (('null_share', None), ('tf85', 'null_share'), ('omega1', 'null_remote'),
         ('internalise', 'null_remote'))


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
    ages, band, cev, ad, wealth = {}, {}, None, {}, {}
    for l in L:
        m = re.search(r'DIAG age\s+(\d+)\s+homeless=\s*(\S+).*sud=\s*(\S+)\s+mass=\s*(\S+)', l)
        if m:
            ages[int(m.group(1))] = tuple(float(m.group(i)) for i in (2, 3, 4))
        m = re.search(r'DIAG age\s+(\d+)\s+homeless=.*renter wealth=\s*(\S+)', l)
        if m:
            wealth[int(m.group(1))] = float(m.group(2))
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
    # homelessness and renters' wealth after the child has left, ages 51 to 64, mass-weighted
    Q = [a for a in ages if 51 <= a <= 64 and ages[a][2] > 0]
    WQ = sum(ages[a][2] for a in Q)
    return dict(
        hl_after=sum(ages[a][0] * ages[a][2] for a in Q) / WQ,
        w_after=sum(wealth[a] * ages[a][2] for a in Q) / WQ,
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
        D[arm]['child_share'] = 100 * s[0] / s[2] if s and arm not in ('omega1', 'internalise') else None
    # no CEV for the two optimal arms: each changes the welfare function itself
    D['omega1']['cev_net'] = None
    D['internalise']['cev_net'] = None
    try:
        prev = json.load(open(PREV))
    except (OSError, ValueError):
        prev = {}
    cells, body = {}, []

    def hd(key, w):
        cells[key] = w
        return w if prev.get(key) == w else f'\\textcolor{{red}}{{{w}}}'
    heads = {1: '\\multicolumn{5}{@{}l}{\\emph{Adults}} \\\\',
             2: '\\multicolumn{5}{@{}l}{\\emph{Children}} \\\\',
             3: '\\multicolumn{5}{@{}l}{\\emph{Welfare}} \\\\'}
    for k in heads:
        title = re.search(r'\\emph\{([^}]*)\}', heads[k]).group(1)
        cells[f'panel/{k}'] = title
        if prev.get(f'panel/{k}') != title:
            heads[k] = heads[k].replace('\\emph{', '\\emph{\\textcolor{red}{', 1).replace('}} \\\\', '}}} \\\\', 1)
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
           '\\begin{tabular}{@{}L{170pt}rrrr@{}}', '\\toprule',
           ' & ' + ' & '.join(hd(f'h1/{k}', w) for k, w in enumerate(('Housing', 'Treatment', 'Optimal', 'Optimal'))) + ' \\\\',
           ' & ' + ' & '.join(hd(f'h2/{k}', w) for k, w in enumerate(('First', 'First', 'drug use', 'homelessness'))) + ' \\\\',
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
    # THE TWO OPTIMAL ARMS IN THE PROSE (the author, 2 October: titles for each simulation, the
    # optimal-homelessness column, and "explain more"): drug use, homelessness and pi_V, each with
    # its direction, and the pi_V sentence only when pi_V clears (it was held in the old arms)
    def piv_sentence(arm, base, why_fall):
        p0, p1 = D[base]['piv'], D[arm]['piv']
        if abs(p1 / p0 - 1) < 1e-6:
            return ''
        d = 'falls' if p1 < p0 else 'rises'
        return (f'$\\pi_V$ {d} from ${100 * p0:.2f}$ to ${100 * p1:.2f}$ percent to hold net government '
                f'revenue at its benchmark level' + (why_fall if p1 < p0 else '') + '.')
    out['x_lr_om_b_dir'] = 'falls' if D[o]['b'] < D['null_remote']['b'] else 'rises'
    out['x_lr_om_piv_sentence'] = piv_sentence(o, 'null_remote',
        ': a population that uses fewer drugs lives longer, so the government collects fewer '
        'accidental bequests and pays more in social security')
    # WHY HOMELESSNESS FALLS UNDER FULL ALTRUISM (the author, 2 October: "You need to explain why that is",
    # and then, of 'fewer parents acquire the disorder': "this is not a good explanation because this
    # happens also under TF"). What full altruism alone does is make a parent bear its child's shelter
    # in full, and the runs show it where that bites: homelessness falls at the ages a child is at home
    # (26 to 50) and not after, when renters hold less wealth (both omega_c = 1 runs, cf_fix2 and 2c)
    _kid = pc(o, 'child_hl', 'null_remote')
    _aft = pc(o, 'hl_after', 'null_remote')
    _wa = pc(o, 'w_after', 'null_remote')
    out['x_lr_om_h_why'] = (
        'Homelessness falls because a parent that counts its child as itself bears in full what a '
        'shelter costs the child, and spends what it has to keep the child housed, so the fall comes in '
        'the years a child lives at home: among households aged 51 to 64, whose children have left and '
        f'whose renters hold {abs(_wa):.0f} percent {"less" if _wa < 0 else "more"} wealth, homelessness '
        f'{"rises" if _aft > 0 else "falls"} by {abs(_aft):.0f} percent.'
        if D[o]['h'] < D['null_remote']['h'] and _kid < 0 else '')
    i = 'internalise'
    # OPTIMAL HOMELESSNESS IS FULL ALTRUISM PLUS THE HOMELESSNESS EXTERNALITY (the author, 2 October: "no,
    # it includes also omega_c=1"), so its changes are measured from the optimal-drug-use column when
    # the arm ran at omega_c = 1, and from the benchmark for the old arm, which did not
    _ho_i = dict(l.split()[:2] for l in open(os.path.join(RES, i, 'PARAM_HANDOVER.arm.txt')) if len(l.split()) >= 2)
    ib = o if abs(float(_ho_i.get('weight_on_child', 0)) - 1) < 1e-9 else 'null_remote'
    out['x_lr_in_base_word'] = 'optimal drug use' if ib == o else 'the benchmark'
    out['x_lr_in_dh_pc'] = f"{abs(pc(i, 'h', ib)):.0f}"
    out['x_lr_in_dh_dir'] = 'lower' if D[i]['h'] < D[ib]['h'] else 'higher'
    # the verb (the author, 2 October: 'leaves' -> 'reduces')
    out['x_lr_in_dh_verb'] = 'reduces' if D[i]['h'] < D[ib]['h'] else 'raises'
    # households can act on their housing, and many do when they weigh their child (the author, 2
    # October: "many do reduce homelessness when they weigh their child, so it's not that they cannot
    # afford to rent a place"): only when full altruism did lower homelessness
    out['x_lr_in_many_do'] = (', and many do when they weigh their child, as the optimal drug use column shows'
                              if D[o]['h'] < D['null_remote']['h'] else '')
    out['x_lr_in_b_pc'] = f"{abs(pc(i, 'b', 'null_remote')):.0f}"
    out['x_lr_in_b_dir'] = 'falls' if D[i]['b'] < D['null_remote']['b'] else 'rises'
    out['x_lr_in_h_pc'] = f"{abs(pc(i, 'h', 'null_remote')):.0f}"
    out['x_lr_in_h_dir'] = 'falls' if D[i]['h'] < D['null_remote']['h'] else 'rises'
    out['x_lr_in_h0'] = f"{100 * D['null_remote']['h']:.2f}"
    out['x_lr_in_h1'] = f"{100 * D[i]['h']:.2f}"
    out['x_lr_in_hchild_pc'] = f"{abs(pc(i, 'child_hl', 'null_remote')):.0f}"
    out['x_lr_in_hchild_dir'] = 'falls' if D[i]['child_hl'] < D['null_remote']['child_hl'] else 'rises'
    out['x_lr_in_piv_sentence'] = piv_sentence(i, 'null_remote', '')
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
    # WHY THE DRAW IS SO SMALL A PART (the author, 2 October: "how is that possible? i thought that the
    # productivity penalty is the rest of it"): a child spared the penalty gains the whole clean-penalised
    # gap, many times the within gain every child gets, but few are spared
    out['x_lr_pen0'] = f'{100 * m0[2] / (m0[0] + m0[2]):.2f}'
    out['x_lr_pen1'] = f'{100 * m1[2] / (m1[0] + m1[2]):.2f}'
    out['x_lr_pen_dir'] = 'falls' if m1[2] / (m1[0] + m1[2]) < m0[2] / (m0[0] + m0[2]) else 'rises'
    out['x_lr_pen_ratio'] = f'{gap / (tot - comp):.0f}'
    # WHERE THE GAIN AT A GIVEN DRAW COMES FROM (the author, 2 October: "the whole story is about taking an
    # option away and give nothing back. so how can the option taken away be welfare improving?!"): pi_V
    # clears the budget, so what users no longer cost the programme comes back as a higher pi_V, which the
    # dominance argument of Section 3, at a fixed pi_V, does not have; and demand falls, so the drug is cheaper
    _pv_up, _p_dn = D[t]['piv'] > D['null_share']['piv'], D[t]['price'] < D['null_share']['price']
    out['x_lr_v26_why'] = (
        'Treatment First takes an option away from users, but, unlike the comparison at a fixed $\\pi_V$ in '
        'Section~\\ref{sec:nox}, it also gives something back: what users no longer cost the programme '
        'returns to the eligible households that stay clean as a voucher that is easier to get' +
        (', and the fall in demand makes the drug cheaper.' if _p_dn else '.')
        if _pv_up else '')
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
