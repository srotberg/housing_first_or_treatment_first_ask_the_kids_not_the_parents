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
RES = os.path.join(ROOT, 'results', 'counterfactuals_2c')
# STAGE D (2 October): the omega_c = 0.085 arms, pi_V clearing the budget in each; the arm names
# below are the old ones, mapped to the new runs here (export_results.py carries the same map)
TF_ARM = os.environ.get('TF_ARM', 'tf85_c35/tf')
ARMDIR = {'null_share': 'nulltf/null', 'null_remote': 'nulltf/null', 'tf85': TF_ARM,
          'omega1': 'omega1_clear/omega1', 'internalise': 'optimal_clear/internalise'}
# THE ELASTIC-SUPPLY ARM WAS NOT RE-RUN (the author, 2 October: "dont run the sensitivity analysis, we
# already know those answers"), so the x_lr_e5_* names keep the old arms' answer, each measured against
# the old arms' own no-policy runs and old Treatment First
RES_OLD = os.path.join(ROOT, 'results', 'counterfactuals_cf_fix2')
for _a in ('elast5_85', 'null_remote', 'null_share', 'tf85'):
    ARMDIR['old_' + _a] = os.path.join(RES_OLD, _a)


def adir(arm):
    return os.path.join(RES, ARMDIR[arm])
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
TAB = os.path.join(ROOT, 'writing', 'tables', 'tab_longrun.tex')
PREV = os.path.join(HERE, 'tab_longrun_prev.json')
ARMS = (('null_share', None), ('tf85', 'null_share'),
        ('omega1', 'null_remote'), ('internalise', 'null_remote'),
        ('old_null_share', None), ('old_tf85', 'old_null_share'), ('old_elast5_85', 'old_null_remote'))
# the columns of the table: the elastic supply is a footnote (the author, 30 September); optimal
# homelessness added as a fourth column (the author, 2 October: "You should also add the column for
# omega_c=1 and internalization of homelessness")
TABLE = (('null_share', None), ('tf85', 'null_share'), ('omega1', 'null_remote'),
         ('internalise', 'null_remote'))


def log(arm):
    with gzip.open(os.path.join(adir(arm), 'cf.log.gz'), 'rt', errors='replace') as f:
        return f.read().splitlines()


def final(arm):
    """the levels of an arm's final.txt, first column (the arm), by label, and the welfare split
    against the no-policy run (the new arms do not print it: total = the difference in welfare with
    childhood, childhood = the difference in childhood utility, adult = the rest)"""
    def lv(a):
        rows = {}
        for l in open(os.path.join(adir(a), 'final.txt')):
            m = re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l)
            if m:
                rows[m.group(1).strip()] = float(m.group(2))
        return rows
    rows, b = lv(arm), lv('old_null_share' if arm.startswith('old_') else 'null_share')
    tot = rows['welfare (with childhood)'] - b['welfare (with childhood)']
    kid = rows['childhood utility'] - b['childhood utility']
    rows['split'] = (kid, tot - kid, tot)
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
        # the share of households entering adult life (age index 1) with a higher value than in the
        # benchmark, state by state, weighted by the benchmark's distribution (the Fortran's own check)
        if 'frac_in_support_youngest(' in l:
            ad['young_better'] = float(l.split('=')[1])
        if 'ADULTDECOMP mass type' in l:
            ad['mass'] = [float(x) for x in l.split()[4:]]
        if 'ADULTDECOMP vf type' in l:
            ad['vf'] = [float(x) for x in l.split()[4:]]
    hb, hs, bud = {}, {}, {}
    for l in L:
        m = re.search(r'UNTARGETED homelessness rate, band\s+(\d)\s+model=\s*(\S+)', l)
        if m:
            hb[int(m.group(1))] = float(m.group(2))
        m = re.search(r'DIAG SUD share of the homeless, band\s+(\d)\s+=\s*(\S+)', l)
        if m:
            hs[int(m.group(1))] = float(m.group(2))
        # the government's budget, last print: revenue, social security, vouchers, the estates it keeps
        if l.startswith(' BUDGET '):
            for k, v in re.findall(r'(\w+)=\s*(\S+)', l):
                bud[k] = float(v)
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
        cev=cev, adult=ad, hl_band=hb, sud_hl_band=hs, sud_band=band, budget=bud, ages=ages)


def nodes(name):
    return [float(x) for x in open(os.path.join(adir('tf85'), f'value_at_26_by_node_{name}.txt'))
            if x.strip()]


def main():
    freeze = '--freeze' in sys.argv
    D = {}
    for arm, base in ARMS + (('null_remote', None), ('old_null_remote', None)):
        f = final(arm)
        D[arm] = dict(steady(arm), price=f['drug price'], piv=f['pi_V (voucher probability)'],
                      b=f['drug use b'], sud=f['SUD lambda_d'], h=f['homelessness h_1'],
                      sud_hl=f['SUD share of the homeless'], takeup=f['treatment take-up'],
                      net=f['net government revenue'], split=f.get('split'))
    for arm, base in ARMS:
        if base:
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
        # APPROVAL (the author, 2 October, on Table 7: "can you add approval rates (fraction better off?) for
        # newborns and for adults entering at 26?"). Newborns are alike before birth (Section 6.1), so all or
        # none are better off, as the CEV's sign says; entering adults are compared state by state
        ('Households entering adult life at 26 better off', 'y26_better', lambda v: f'{v:.0f}'),
    ]
    for arm, base in [a for a in ARMS if a[1]]:
        s = D[arm]['split']
        D[arm]['child_share'] = 100 * s[0] / s[2] if s and arm not in ('omega1', 'internalise') else None
    for arm in D:
        D[arm]['nb_better'] = D[arm]['y26_better'] = None
    D['tf85']['nb_better'] = 100.0 if D['tf85']['cev_net'] > 0 else 0.0
    D['tf85']['y26_better'] = 100 * D['tf85']['adult']['young_better']
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
        # a row the author has not seen: its label is red too
        new_row = all(f'{key}/{arm}' not in prev for arm, _ in TABLE)
        line = [f'\\textcolor{{red}}{{{lab}}}' if new_row and prev else lab]
        for arm, _ in TABLE:
            v = D[arm].get(key)
            c = '--' if v is None else fmt(v)
            cells[f'{key}/{arm}'] = c
            line.append(c if prev.get(f'{key}/{arm}') == c else f'\\textcolor{{red}}{{{c}}}')
        body.append(' & '.join(line) + ' \\\\')
    tab = ['% Written by code/paper/export_longrun.py from results/counterfactuals_cf_fix2;',
           '% edit the script, not this file. Caption and note are in the paper.',
           # every row on one line (round 4ad85a30, the author: "can you put all rows in one line?")
           '\\begin{tabular}{@{}lrrrr@{}}', '\\toprule',
           ' & ' + ' & '.join(hd(f'h1/{k}', w) for k, w in enumerate(('Housing', 'Treatment', 'Optimal', 'Optimal'))) + ' \\\\',
           ' & ' + ' & '.join(hd(f'h2/{k}', w) for k, w in enumerate(('First', 'First', 'drug use', 'homelessness'))) + ' \\\\',
           '\\midrule'] + body + ['\\bottomrule', '\\end{tabular}']
    open(TAB, 'w').write('\n'.join(tab) + '\n')
    if freeze:
        json.dump(cells, open(PREV, 'w'), indent=1)

    # ---- names for the prose
    t, e, o = 'tf85', 'old_elast5_85', 'omega1'
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
    # WHY pi_V FALLS HERE AND RISES UNDER TREATMENT FIRST (round 4ad85a30, the author: "i think it pays more
    # in SS but also each voucher holder lives longer so they hold onto it longer. but isnt this effect also
    # present in the TF case? how is this differnt here?"). From the budget each run printed: the voucher
    # bill at the benchmark's pi_V (spending scaled by pi_V0/pi_V1), and the estates the government keeps
    B0, Bo, Bt = (D[a]['budget'] for a in ('null_remote', o, t))
    _vb = lambda a, B: B['vouchers_2'] * D['null_remote']['piv'] / D[a]['piv'] / B0['vouchers_2'] - 1
    _vo, _vt = _vb(o, Bo), _vb(t, Bt)
    # the Discussion's 'where the savings go' (round 20b4ddb5): the voucher bill the excluded users save, at a given pi_V
    out['x_lr_om_vt_pc'] = f'{100 * abs(_vt):.0f}'
    _eo = Bo['bequest_residual'] / B0['bequest_residual'] - 1
    _et = Bt['bequest_residual'] / B0['bequest_residual'] - 1
    _ss = Bo['ss'] > B0['ss'] and Bt['ss'] > B0['ss']
    out['x_lr_om_piv_why'] = (
        'A population that uses fewer drugs lives longer, so the government pays more in social security and '
        'each voucher holder holds its voucher for longer. Hence, at the benchmark\'s $\\pi_V$ the programme would cost '
        f'${100 * _vo:.0f}$ percent more. The same happens under Treatment First, but there the users the screen '
        f'takes out of the programme outweigh it, and at the benchmark\'s $\\pi_V$ the programme would cost '
        f'${100 * abs(_vt):.0f}$ percent less.'
        if D[o]['piv'] < D['null_remote']['piv'] and D[t]['piv'] > D['null_share']['piv'] and _ss
        and _vo > 0 > _vt else '')
    out['x_lr_om_piv_sentence'] = piv_sentence(o, 'null_remote', '')
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
        'shelter costs the child, and spends what it has to keep the child housed. So the fall comes in '
        'the years a child lives at home, whereas among households aged 51 to 64, whose children have left, '
        f'homelessness {"rises" if _aft > 0 else "falls"} by {abs(_aft):.0f} percent.'
        if D[o]['h'] < D['null_remote']['h'] and _kid < 0 and _aft > 0 else
        'Homelessness falls because a parent that counts its child as itself bears in full what a '
        'shelter costs the child, and spends what it has to keep the child housed.'
        if D[o]['h'] < D['null_remote']['h'] and _kid < 0 else '')
    i = 'internalise'
    # OPTIMAL HOMELESSNESS IS FULL ALTRUISM PLUS THE HOMELESSNESS EXTERNALITY (the author, 2 October: "no,
    # it includes also omega_c=1"), so its changes are measured from the optimal-drug-use column when
    # the arm ran at omega_c = 1, and from the benchmark for the old arm, which did not
    _ho_i = dict(l.split()[:2] for l in open(os.path.join(adir(i), 'PARAM_HANDOVER.arm.txt')) if len(l.split()) >= 2)
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
    # (round 4ad85a30, the author: "you have to compare it to the piv in omegac=1"): from its own base
    _p0, _p1 = D[ib]['piv'], D[i]['piv']
    _pw = 'under ' + out['x_lr_in_base_word'] if ib == o else 'in the benchmark'
    out['x_lr_in_piv_sentence'] = '$\\pi_V$ remains practically unchanged.' if abs(_p1 / _p0 - 1) < 0.01 else (
        f"$\\pi_V$ {'rises' if _p1 > _p0 else 'falls'}, "
        f"from ${100 * _p0:.2f}$ percent {_pw} to ${100 * _p1:.2f}$ percent, to hold net government revenue at "
        'its benchmark level.')
    # homelessness by age band under Treatment First: 26-34 against 35-44
    hb0, hb1 = D['null_share']['hl_band'], D[t]['hl_band']
    out['x_lr_hl_b1_pc'] = f'{100 * (hb1[1] / hb0[1] - 1):.0f}'
    out['x_lr_hl_b2_pc'] = f'{100 * (hb1[2] / hb0[2] - 1):.0f}'
    # the newborn's gain: net CEV, and the adult part's composition share
    out['x_lr_e5_cev'] = f"{D[e]['cev_net']:.2f}"
    out['x_lr_e5_b_pc'] = f"{abs(pc(e, 'b', 'old_null_remote')):.0f}"
    out['x_lr_e5_h_pc'] = f"{abs(pc(e, 'h', 'old_null_remote')):.0f}"
    out['x_lr_e5_price_pc'] = f"{abs(pc(e, 'price', 'old_null_remote')):.0f}"
    out['x_lr_e5_child_pc'] = f"{D[e]['child_share']:.0f}"
    # against the old Treatment First, the run it was a sensitivity of
    out['x_lr_e5_cev_dir'] = 'rises' if D[e]['cev_net'] > D['old_tf85']['cev_net'] else 'falls'
    # the supply elasticity the arm ran at, from its handover (the benchmark's is f_drug_supply_elasticity)
    ho = dict(l.split()[:2] for l in open(os.path.join(adir(e), 'PARAM_HANDOVER.arm.txt')) if len(l.split()) >= 2)
    out['x_lr_e5_elast'] = f"{float(ho['drug_supply_elasticity']):g}"
    out['x_lr_paruse_dir'] = 'falls' if D[t]['par_use'] < D['null_share']['par_use'] else 'rises'
    out['x_lr_paruse0'] = f"{100 * D['null_share']['par_use']:.2f}"
    out['x_lr_paruse1'] = f"{100 * D[t]['par_use']:.2f}"
    out['x_lr_hl_b2_dir'] = 'rises' if hb1[2] > hb0[2] else 'falls'
    out['x_lr_e5_h_dir'] = 'rises' if D[e]['h'] > D['old_null_remote']['h'] else 'falls'
    # whether full altruism and Treatment First move homelessness the same way
    same = (D[o]['h'] > D['null_remote']['h']) == (D[t]['h'] > D['null_share']['h'])
    out['x_lr_h_split'] = 'move together on' if same else 'part ways on'
    # STAGE D: THE SENTENCES THAT TURN WITH THE NEW ARMS (Treatment First lowers homelessness on the
    # omega_c = 0.085 benchmark, and cuts drug use by more than full altruism does). The first branch of
    # each is the text the paper had.
    _b1, _b2 = 100 * (hb1[1] / hb0[1] - 1), 100 * (hb1[2] / hb0[2] - 1)
    _b3 = 100 * (hb1[3] / hb0[3] - 1)
    _trise = D[t]['h'] > D['null_share']['h']
    _w = lambda x: 'rises' if x > 0 else 'falls'
    out['x_lr_hl_band_sentence'] = (
        'Broken down by the age of the household, the rise in homelessness is largest among households '
        'aged 35 to 44, whose children are still part of their household: their homelessness '
        f'{_w(_b2)} by ${abs(_b2):.0f}$ percent, against ${_b1:.0f}$ percent at 26 to 34.'
        if _trise and _b2 > _b1 and _b2 > 0 and _b1 >= 0 else
        f'Broken down by the age of the household, homelessness {_w(_b2)} by ${abs(_b2):.0f}$ percent among '
        'households aged 35 to 44, whose children are still part of their household, '
        f"{'but' if (_b1 > 0) != (_b2 > 0) else 'and'} {_w(_b1)} by ${abs(_b1):.0f}$ percent at 26 to 34"
        + (f' and by ${abs(_b3):.0f}$ percent at 45 to 54.' if (_b3 > 0) == (_b1 > 0) else
           f' and {_w(_b3)} by ${abs(_b3):.0f}$ percent at 45 to 54.'))
    # WHY THE SHELTER SHARE HOLDS AND THE BANDS SPLIT (round 4ad85a30, the author: "explain why!" on the
    # unchanged share, ", explain why" on the bands): by band, the share with a SUD and the share of them
    # homeless (band rate x SUD share of the homeless / SUD share of households)
    s0b, s1b = D['null_share']['sud_band'], D[t]['sud_band']
    q0b, q1b = D['null_share']['sud_hl_band'], D[t]['sud_hl_band']
    _rs = lambda hb, qb, sb, k: hb[k] * qb[k] / sb[k]
    r1 = [_rs(hb0, q0b, s0b, 1), _rs(hb1, q1b, s1b, 1)]
    r2 = [_rs(hb0, q0b, s0b, 2), _rs(hb1, q1b, s1b, 2)]
    _f = lambda x: f'{100 * x:.2f}'
    out['x_tf_hchild_why'] = (
        'It does not move because the reform moves homelessness in opposite directions at the ages a child is at '
        'home, and the moves cancel.'
        if _b2 > 0 > _b1 and _b3 < 0 and abs(100 * (D[t]['child_hl'] - D['null_share']['child_hl'])) < 0.005
        else '')
    # (round c88b1dda, the author: "not clear at all. can you make this easier to understand?", 'households in
    # the benchmark', 'and' -> 'but it still raises', 'only a' -> 'a', and "I want better explanations"): at each
    # age the change splits into fewer with a SUD and a higher risk for those who still carry one
    def _split(k):
        lam0, lam1, rs0, rs1 = s0b[k], s1b[k], _rs(hb0, q0b, s0b, k), _rs(hb1, q1b, s1b, k)
        rc0 = (hb0[k] - lam0 * rs0) / (1 - lam0)
        return lam1 * (rs1 - rs0), (lam1 - lam0) * (rs0 - rc0)
    _u1, _n1 = _split(1)
    _u2, _n2 = _split(2)
    _d1, _d2 = 100 * (s1b[1] / s0b[1] - 1), 100 * (s1b[2] / s0b[2] - 1)
    # (round e1fffcf0: 45 to 50 rather than 54, 'but raises', the overall rates at each age, '. This is because',
    # 'has not had enough time to cost most of these households their jobs')
    def _hage(arm, lo, hi):
        A = D[arm]['ages']
        return sum(A[a][0] * A[a][2] for a in range(lo, hi + 1)) / sum(A[a][2] for a in range(lo, hi + 1))
    _h45 = [_hage('null_share', 45, 50), _hage(t, 45, 50)]
    _b45 = 100 * (_h45[1] / _h45[0] - 1)
    out['x_lr_children_hl'] = (
        'Children live with households aged 26 to 50. Across those ages the reform moves homelessness in '
        f'opposite directions: it falls by ${abs(_b1):.0f}$ percent among households aged 26 to 34, rises by '
        f'${abs(_b2):.0f}$ percent at 35 to 44 and falls by ${abs(_b45):.0f}$ percent at 45 to 50. The changes '
        'cancel. Which way it goes at a given age depends on the balance of the two forces above. Treatment First '
        'cuts the number of households with a SUD, but raises the risk of homelessness for those who still have '
        'one, because they lose their voucher. At 26 to 34 the first force wins. The share of households with a SUD '
        f'falls from ${_f(s0b[1])}$ to ${_f(s1b[1])}$ percent, while the share of them who are homeless rises only '
        f'from ${_f(r1[0])}$ to ${_f(r1[1])}$ percent. So homelessness at these ages falls from ${_f(hb0[1])}$ to '
        f'${_f(hb1[1])}$ percent. This is because a disorder acquired young has not had enough time to cost most of '
        'these households their jobs, so few of them depended on a voucher to stay housed. At 35 to 44 the second '
        f"force wins. The share with a SUD falls {'by about as much' if abs(_d1 - _d2) < 5 else 'too'}, from "
        f'${_f(s0b[2])}$ to ${_f(s1b[2])}$ percent. But these households have carried the disorder longer, and more '
        'of them have lost their jobs and depend on a voucher. Without it, the share of them who are homeless rises '
        f'from ${_f(r2[0])}$ to ${_f(r2[1])}$ percent, so homelessness at these ages rises from ${_f(hb0[2])}$ to '
        f'${_f(hb1[2])}$ percent.'
        if _b2 > 0 > _b1 and _b45 < 0 and s1b[1] < s0b[1] and s1b[2] < s0b[2] and r2[0] > r1[0]
        and r2[1] / r2[0] > r1[1] / r1[0] > 1 and _u1 + _n1 < 0 < _u2 + _n2
        and abs(100 * (D[t]['child_hl'] - D['null_share']['child_hl'])) < 0.005 else '')
    _r = pc(t, 'b', 'null_share') / pc(o, 'b', 'null_remote')
    _tfb, _omb = out['x_lr_tf_b_pc'], out['x_lr_om_b_pc']
    out['x_lr_tf_vs_om'] = (
        f"Treatment First delivers ${out['x_lr_tf_of_om_pc']}$ percent of the fall in drug use that full "
        f"altruism would bring, ${_tfb}$ percent against ${_omb}$." if _r <= 1.05 else
        f"Treatment First cuts drug use by more than full altruism would, ${_tfb}$ percent against ${_omb}$.")
    _hless = abs(pc(t, 'h', 'null_share')) < abs(pc(o, 'h', 'null_remote'))
    out['x_lr_tf_vs_om2'] = (
        f"Treatment First cuts drug use by more than full altruism would, ${_tfb}$ percent against ${_omb}$, but "
        'homelessness by less' if _r > 1.05 and _hless else
        out['x_lr_tf_vs_om'].rstrip('.') + ', and homelessness')
    out['x_lr_tf_of_om_disc'] = (f"Treatment First delivers ${out['x_lr_tf_of_om_pc']}$ percent of that fall"
                                 if _r <= 1.05 else f"Treatment First cuts it by more, ${_tfb}$ percent")
    # Treatment First on the two housing margins, beside full altruism's
    _hc_t = D[t]['child_hl'] - D['null_share']['child_hl']
    _hflat = abs(100 * _hc_t) < 0.005
    if _trise and _hc_t > 0:
        out['x_lr_tf_both'] = 'raises both'
    elif not _trise and _hc_t < 0 and not _hflat:
        out['x_lr_tf_both'] = 'lowers both'
    else:
        out['x_lr_tf_both'] = (f"{'raises' if _trise else 'lowers'} homelessness by only "
                               f"${abs(pc(t, 'h', 'null_share')):.0f}$ percent and "
                               + ('leaves the share in a shelter where it was' if _hflat else
                                  f"{'raises' if _hc_t > 0 else 'lowers'} the share in a shelter"))
    _drug = ('gets the drug margin roughly right' if 0.85 <= _r <= 1.15 else
             'goes further than full altruism on the drug margin' if _r > 1.15 else
             'falls short of full altruism on the drug margin')
    _om_dh = pc(o, 'h', 'null_remote')
    _tf_dh = pc(t, 'h', 'null_share')
    _house = (('the housing margin wrong' if _drug.startswith('gets') else 'gets the housing margin wrong')
              if _tf_dh > 0 else
              'falls short of it on the housing margin' if _tf_dh > _om_dh else
              'matches it on the housing margin')
    out['x_lr_margins'] = (f"Conditionality {_drug} and {_house}, because it works by taking housing away."
                           if _tf_dh > _om_dh else f"Conditionality {_drug} and {_house}.")
    # THE WHOLE TEXT CONSISTENT WITH THE NEW ARMS (the author, 2 October: "make sure the prose everywhere is
    # consistent ... homelessness drops a bit under tf"). The abstract: the first branch of each is the
    # text it had, for a Treatment First that raises homelessness
    _tf_dh_abs = abs(_tf_dh)
    out['x_abs_tf_exposes'] = ('it also raises homelessness' if _trise else
                               'it also exposes the households it screens out to homelessness')
    out['x_abs_om_adv'] = 'sharply ' if abs(pc(o, 'b', 'null_remote')) >= 25 else ''
    out['x_abs_tf_result'] = (
        'Conditioning assistance raises homelessness but substantially cuts drug use' if _trise else
        'Conditioning assistance substantially cuts drug use and, as the vouchers it revokes go to other '
        f"poor households, lowers homelessness{' slightly' if _tf_dh_abs < 3 else ''}")
    # the Discussion's 'which channel' sentence, as Section 6.2 now explains it (x_lr_v26_why): what users
    # no longer cost the programme comes back as a higher pi_V, and demand falls, so the drug is cheaper
    _pv_up, _p_dn = D[t]['piv'] > D['null_share']['piv'], D[t]['price'] < D['null_share']['price']
    out['x_disc_economy'] = (
        'the rest is a better economy to enter: what users no longer cost the programme returns to the '
        'households that stay clean as a voucher that is easier to get' +
        (', and the drug is cheaper' if _p_dn else '')
        if _pv_up else 'the rest is a better economy to enter')
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
    # the value at 26 by node: the Fortran's welfare_by_employment_youngest{baseline_benchmark,counter_arm}.txt
    # from the Treatment First arm's run directory. The new arms' workers did not publish it and could
    # not be asked to (no cross-session message reaches a cloud worker from here), so without it the
    # clause falls back on the two blocks ADULTDECOMP prints, a child of a clean parent and of a
    # penalised one, each at its own draw distribution: the within gains v1 - v0 of each block.
    if os.path.exists(os.path.join(adir('tf85'), 'value_at_26_by_node_tf85.txt')):
        nb, nt = nodes('benchmark'), nodes('tf85')
        g = [a - b for a, b in zip(nt, nb)]
        out['x_lr_v26_ratio'] = f'{g[0] / g[12]:.0f}'
        out['x_lr_v26_all_up'] = 'every' if min(g) > 0 else 'not every'
        out['x_lr_v26_clause'] = (f"the value of entering the economy at 26 rises at {out['x_lr_v26_all_up']} "
                                  f"level of productivity, about ${out['x_lr_v26_ratio']}$ times as much at the "
                                  "lowest as at the highest")
    else:
        _gc, _gp = v1[0] - v0[0], v1[2] - v0[2]
        out['x_lr_v26_clause'] = (
            'the value of entering the economy at 26 rises both for a child whose parent was free of the '
            f"disorder and, by {'more' if _gp > _gc else 'less'}, for one whose parent carried it"
            if _gc > 0 and _gp > 0 else
            f"the value of entering the economy at 26 {'rises' if _gc > 0 else 'falls'} for a child whose "
            f"parent was free of the disorder and {'rises' if _gp > 0 else 'falls'} for one whose parent "
            'carried it')

    # THE ADULT PART, SPELLED OUT (round 4ad85a30, the author: "the rest is intergenerational persistence
    # over more than 1 generation?", "not clear to me...", "ie, the grandfather of that child? ... make it
    # clear", and of what Treatment First gives back: "remove"). The larger part first, the one that does
    # not depend on the draw, then the draw and why it is so small a part; 'parent' is the child's own
    _gc, _gp = v1[0] - v0[0], v1[2] - v0[2]
    _within = (f"with the same productivity, adult life is worth more under Treatment First than under "
               f"Housing First, at {out['x_lr_v26_all_up']} level of productivity and about "
               f"${out['x_lr_v26_ratio']}$ times as much at the lowest as at the highest"
               if 'x_lr_v26_ratio' in out else
               'with the same productivity, adult life is worth more under Treatment First than under Housing '
               f"First, both for a child whose own parent was free of the disorder and, by "
               f"{'more' if _gp > _gc else 'less'}, for a child whose own parent carried it, whom the penalty "
               'leaves with lower productivity'
               if _gc > 0 and _gp > 0 else '')
    _sp = D[t]['split']
    _kid = 100 * _sp[0] / _sp[2]
    _draw = (100 - _kid) * comp / tot
    _val = 100 - _kid - _draw
    _pvpc, _prpc = pc(t, 'piv', 'null_share'), pc(t, 'price', 'null_share')
    _poor = ('The higher voucher probability is worth most to households that enter adult life with low '
             'productivity, who are the likeliest '
             'to need a voucher. So this gain is larger for a child whose own parent carried the disorder, whom the '
             'penalty leaves with lower productivity.' if _gp > _gc > 0 else '')
    out['x_lr_adult'] = (
        f"The other ${100 - _kid:.0f}$ percent comes in adult life, from two sources. The first, ${_draw:.0f}$ "
        'percent of the whole gain, is the better productivity a child draws when its own parent does not carry the '
        f"disorder. Escaping the penalty is worth a lot to each child it spares, about ${out['x_lr_pen_ratio']}$ "
        'times what the average child gains at the same productivity. But it spares only about '
        f"${float(out['x_lr_pen0']) - float(out['x_lr_pen1']):.0f}$ percent of children: the share of newborns who "
        f"enter adult life with the penalty {out['x_lr_pen_dir']} from ${out['x_lr_pen0']}$ to ${out['x_lr_pen1']}$ "
        f"percent. The second, the remaining ${_val:.0f}$ percent, does not depend on the child's productivity at "
        'all. It is a result of the better economy it lives its adult life in. A clean household is '
        f'${_pvpc:.0f}$ percent more likely to draw a voucher. The users the screen excludes no longer cost '
        'the programme, and tax revenue rises, mostly as fewer adults carry the earnings penalty and partly '
        'as fewer lose their jobs to a SUD. Drug users gain too, because the drug is '
        f'${abs(_prpc):.0f}$ percent cheaper in equilibrium. {_poor}'
        if comp / tot < 0.5 and _gc > 0 and _gp > 0 and _pvpc > 0 > _prpc else '')
    # THE INTRODUCTION'S ACCOUNT OF THE GAIN (round 20b4ddb5, the author: "too long and not clear...i still dont
    # understand where the rest of the gains in adulthood come from"): the same three shares of the whole gain
    out['x_intro_gain'] = (
        f"A newborn gains ${D[t]['cev_net']:.2f}$ percent of lifetime consumption. About ${_kid:.0f}$ percent of that "
        "gain comes in childhood, from a parent who spends more on the child's consumption and housing and less on "
        f'drugs, and is less likely to lose its job to a SUD. About ${_draw:.0f}$ percent comes from the higher earnings of a child whose parent was free of the '
        f'disorder. The remaining ${_val:.0f}$ percent comes from a better economy to live in as an adult: whatever '
        f'its productivity, a household that stays clean is ${_pvpc:.0f}$ percent more likely to get a voucher, paid '
        'for by the users the screen excludes and by the higher taxes of adults who no longer carry the earnings '
        'penalty or lose their jobs to a SUD, and the drug is cheaper in equilibrium.' if out['x_lr_adult'] else '')
    # the introduction's account of the newborn's gain, consistent with 6.2's (round c88b1dda, the author: "make
    # sure that the explanations in intro ... are consistent with the results we have")
    out['x_intro_adult_rest'] = (', and the rest through adult life being worth more at the same productivity, chiefly '
                                 'because a voucher is easier to get' if out['x_lr_adult'] else '')
    # APPROVAL IN THE TEXT (round c88b1dda, the author: "also where are the results on approvals?")
    _y = D[t]['y26_better']
    out['x_lr_approve'] = (
        ('Every household that enters adult life at 26 is better off under Treatment First than it would be in '
         'the same state under Housing First' if _y > 99.95 else
         f'Of the households that enter adult life at 26, ${_y:.0f}$ percent are better off under Treatment First '
         'than they would be in the same state under Housing First')
        + ' (Table~\\ref{tab:longrun}).')
    d = json.load(open(OUT_JSON))
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    print(f'wrote {TAB} and {len(out)} x_lr_* names')
    for k, v in sorted(out.items()):
        print(f'  {k} = {v}')


if __name__ == '__main__':
    main()
