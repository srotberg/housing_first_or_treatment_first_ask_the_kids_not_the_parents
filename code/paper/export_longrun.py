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
  Housing First, w_c=1   omega1      the parent weighs its child as itself; pi_V CLEARS the budget
                                     (Stage D, omega1_clear: 6.75 -> 5.84 percent; the old cf_fix2
                                     arm held it, and this line said so until 5 October, which put a
                                     wrong 'pi_V held' into the introduction in round r149). No CEV:
                                     the author asked for none, since omega_c changes the welfare
                                     function itself

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

import welfare_nok
import rulec_paths as RC   # the rule-C runs (14 October): every path below that moved reads from here
STEADY_WITH_TERM = []   # arms whose CEV still carries the kappa_x term (no final.txt/log pair)
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
RES = os.path.join(ROOT, 'results', 'counterfactuals_2c')
# STAGE D (2 October): the omega_c = 0.085 arms, pi_V clearing the budget in each; the arm names
# below are the old ones, mapped to the new runs here (export_results.py carries the same map)
# RULE C (14 October): the main arm is tf_pdet20_C/tf and Housing First is re-solved beside it on the rule-C build
# (RC.NULL_DIR); null_remote stays nulltf/null, the base of omega1 and internalise, which have no screen
TF_ARM = os.environ.get('TF_ARM', RC.TF_ARM)
ARMDIR = {'null_share': RC.NULL_DIR, 'null_remote': 'nulltf/null', 'tf85': TF_ARM,
          'omega1': 'omega1_clear/omega1', 'internalise': 'optimal_clear/internalise'}
# THE ELASTIC-SUPPLY ARM WAS NOT RE-RUN (the author, 2 October: "dont run the sensitivity analysis, we
# already know those answers"), so the x_lr_e5_* names keep the old arms' answer, each measured against
# the old arms' own no-policy runs and old Treatment First
RES_OLD = os.path.join(ROOT, 'results', 'counterfactuals_cf_fix2')
for _a in ('elast5_85', 'null_remote', 'null_share', 'tf85'):
    ARMDIR['old_' + _a] = os.path.join(RES_OLD, _a)
# TREATMENT FIRST WITHOUT THE EXTERNALITIES, the last column (the author, round r152, on Table 7: "I think you need to
# add one column on the right of this which if TF no externalities, right?"): results/pe_noext, Arm B (Treatment First,
# omega_c and both penalties at zero, the drug price and pi_V held at Arm A's) against Arm A (Housing First with the same
# switches, the price clearing). Its welfare rows come from the walk (analysis.json), not from the benchmark's curve
PE = RC.PE   # rule C (14 October); rule A's was results/pe_noext
ARMDIR['pe_a'] = os.path.join(PE, 'arm_A')
ARMDIR['pe_b'] = os.path.join(PE, 'arm_B')
# TREATMENT FIRST WITHOUT THE EXTERNALITIES, THE BUDGET REBALANCED (the author, 8 October: "get the full model with budget
# rebalance and p constant to see if the story is about moral hazard or about externalities", and that it goes "in the
# table with discussion"): results/noext_fixp, Arm D, the drug price held at Arm A's and pi_V clearing the budget against
# Arm A's net revenue. Its Arm A is a re-solve of pe_noext's (the same to five digits), so the table keeps pe_a as base
FX = RC.FX   # rule C; rule A's was results/noext_fixp
ARMDIR['fx_d'] = os.path.join(FX, 'arm_D')
# AND WITH THE DRUG PRICE CLEARING TOO (the author, 8 October: "go ahead with all 3"): results/noext_clear, Arm C,
# Treatment First without the externalities with the drug price and pi_V both clearing. Its Arm A is again a re-solve of
# pe_noext's (the same to five digits)
NC = RC.NC   # rule C, the nearer start; rule A's was results/noext_clear
ARMDIR['nc_c'] = os.path.join(NC, 'arm_C')
# AND WITH ONLY THE DRUG PRICE CLEARING (the author, 14 October: "Sure add the price clears only runs"): results/noext_pclear,
# Arm E, pi_V held at Housing First's and the budget not cleared, as the with-externality block's dc_pv; rule C's is
# results/noext_pclear_C (code/noext_clear/run_noext_pclear_C.sh)
NE = RC.NE   # rule C; rule A's was results/noext_pclear
ARMDIR['ne_e'] = os.path.join(NE, 'arm_E')
# THE DECOMPOSITION'S THREE RUNS AS COLUMNS (the author, 8 October, on Table 6: "can't you just add the experiments in
# Table to Table 5?", "the one missing can be added there"): Treatment First with the externalities and the drug price,
# pi_V or both held at Housing First's, each against null_share like tf85 (export_results.py reads the same runs for the
# x_dc_* names). Their runs saved no full value functions, so the two shares-better-off rows and the newborns' row
# print '--' for them, which the table note says
# rule C (14 October): each column re-solved beside Housing First, its arm in tf/ (results/decomp_2c_shares_C)
ARMDIR['dc_b'] = os.path.join(RC.DC['fixboth'], 'tf')
ARMDIR['dc_pv'] = os.path.join(RC.DC['fixpv'], 'tf')
ARMDIR['dc_p'] = os.path.join(RC.DC['fixp'], 'tf')
# A COLUMN WHOSE RULE-C RUN HAS NOT LANDED (14 October): its rule-A run stands in so that the code runs, and EVERY cell
# and name it feeds prints \tocheck{--} (yellow), never a number (see PENDING and the end of main)
_FALLBACK = {'dc_p': (os.path.join(ROOT, 'results', 'decomp_2c', 'arm_fixp'), 'fixp'),
             'dc_pv': (os.path.join(ROOT, 'results', 'decomp_2c', 'arm_fixpv'), 'fixpv'),
             'ne_e': (os.path.join(ROOT, 'results', 'noext_pclear', 'arm_E'), None)}
PENDING = set()
for _a, (_old, _k) in _FALLBACK.items():
    if not (os.path.exists(os.path.join(ARMDIR[_a], 'final.txt')) and os.path.exists(os.path.join(ARMDIR[_a], 'cf.log.gz'))):
        PENDING.add(_a)
        ARMDIR[_a] = _old
if 'ne_e' in PENDING:
    NE = os.path.join(ROOT, 'results', 'noext_pclear')
_NODES = {'dc_p': os.path.join(RC.DC['fixp'], 'tf'), 'dc_pv': os.path.join(RC.DC['fixpv'], 'tf')}
for _a in ('dc_p', 'dc_pv'):
    if _a in PENDING:
        _NODES[_a] = ARMDIR[_a]
# the prose names a pending column feeds (export_results.py writes the x_dc_p*/x_dcpv* family from the same runs)
_PENDING_NAMES = {'dc_p': ('x_dcp_', 'x_dc_p_'), 'dc_pv': ('x_dcpv_', 'x_dc_pv_'), 'ne_e': ('x_ne_',)}


def adir(arm):
    return os.path.join(RES, ARMDIR[arm])
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
TAB = os.path.join(ROOT, 'writing', 'tables', 'tab_longrun.tex')
PREV = os.path.join(HERE, 'tab_longrun_prev.json')
ARMS = (('null_share', None), ('tf85', 'null_share'),
        ('omega1', 'null_remote'), ('internalise', 'null_remote'),
        ('old_null_share', None), ('old_tf85', 'old_null_share'), ('old_elast5_85', 'old_null_remote'),
        ('dc_b', 'null_share'), ('dc_pv', 'null_share'), ('dc_p', 'null_share'))
# the columns of the table: the elastic supply is a footnote (the author, 30 September); optimal
# homelessness added as a fourth column (the author, 2 October: "You should also add the column for
# omega_c=1 and internalization of homelessness")
# (round r153, the author, on the last column: "should it be the first after HF?": second, as Section 6.2 now opens with it)
# (round r154, the author: "dont we then have to have HF, no externalities on the left? and HF on the right of it?":
# each experiment beside its own base, Housing First and Treatment First without the externalities first)
TABLE = (('pe_a', None), ('pe_b', 'pe_a'), ('null_share', None), ('tf85', 'null_share'), ('omega1', 'null_remote'),
         ('internalise', 'null_remote'))
# FULL ALTRUISM AND FULL INTERNALISATION GO TO THE APPENDIX (the author, 8 October: "we need to keep the paper tighter,
# and i think the full altruism is more for the appendix"): the main table keeps the first four columns, and
# writing/tables/tab_longrun_altruism.tex carries Housing First beside the two benchmarks
# THE NO-EXTERNALITY 'BOTH CLEAR' COLUMN LEAVES THE TABLE (the author, 9 October: "remove that experiment and focus on
# the one that proves whether something is moral hazard", "the pv moving without externalities, can go into a footnote
# ... a price GE effect that has nothing to do with moral hazard"): nc_c is still read, for the footnote's x_nc_* names
# AND IT COMES BACK (the author, 14 October, once rule C's newborn loses there too: "Now we can show the price one as well
# in the table... Where both clear"): the no-externality block steps like the other, both held, pi_V clearing, both
# clearing, so the moral-hazard verdict reads across all three
# AND THE PRICE-CLEARS RUN BACK AS A COLUMN (the author, 14 October: "You can add all the combinations to table if they
# are actually useful. But make sure the table fits the page and doesn't become horizontal"): dc_pv isolates the
# drug price's own effect, the channel that takes back part of the screen's cut in use; 10 columns stay portrait
TABLE_MAIN = (('pe_a', None), ('pe_b', 'pe_a'), ('fx_d', 'pe_a'), ('ne_e', 'pe_a'), ('nc_c', 'pe_a'), ('null_share', None),
              ('dc_b', 'null_share'), ('dc_p', 'null_share'), ('dc_pv', 'null_share'), ('tf85', 'null_share'))
# full internalisation leaves the appendix too (the author, 8 October, on the aggregate homelessness externality: "it
# doesnt matter ... we can put it in a footnote"); the footnote in Section 5 quotes its one number, x_lr_in_dh_pc
TABLE_APP = (('null_share', None), ('omega1', 'null_remote'))
TAB_APP = os.path.join(ROOT, 'writing', 'tables', 'tab_longrun_altruism.tex')


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
            # WITHOUT the kappa_x * H term where the arm's files allow it (welfare_nok.py, 10 October)
            _v = welfare_nok.arm_values(adir(arm))
            if _v:
                cev = welfare_nok.cev_free(adir(arm)) / 100
            else:
                STEADY_WITH_TERM.append(arm)
        # the share of households entering adult life (age index 1) with a higher value than in the
        # benchmark, state by state, weighted by the benchmark's distribution (the Fortran's own check)
        if 'DIAG mean drug quantity, users' in l:
            ad['q_user'] = float(l.split('=')[1])
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


def shares(tol='0.001', path=None):
    """WHO IS BETTER OFF IN THE LONG RUN (the author, round f4276e76, on Table 7: "add a row ... for those with
    SUD. I wonder if they are better off", and round 538f55b4 on drug users: "does their welfare rise?").
    results/transition_2c/shares.txt (transition_2c/shares.py, stage E): Treatment First's value against the
    no-policy run's in every state, weighted by the no-policy distribution, better when ahead by more than tol
    utils, so that numerical drift between two solves is not counted as a gain. Returns {group: (better, worse)}."""
    p = path or os.path.join(RC.DC['tf'], 'shares.txt')   # rule C; rule A's was results/transition_2c/shares.txt
    out = {}
    if not os.path.exists(p):
        return out
    for l in open(p):
        m = re.match(r'\s+(all households|with a SUD|without a SUD|youngest adults \(age index 1\))\s.*?tol ' + re.escape(tol)
                     + r': better (\S+) worse (\S+)', l)
        if m:
            out[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    return out


def age_split():
    """HOMELESSNESS BY 26-38 AND 39-50 (the author, 2 October, on 'The SUD figures are by ten-year band': "why not
    break it down to 26-38 and 39-50?", and "by doing it by 26-38 and 39-50, you can make this shorter and clearer").
    results/transition_2c/age_split.txt (transition_2c/age_split.py on stage E2's two re-solved arms, exact from the
    housing policy). Returns {'null'|'tf': {(lo, hi): dict(sud, h, h_sud, h_clean)}} in per cent, or {} unless both
    arms are exact."""
    p = RC.AGE_SPLIT   # rule C (14 October): finish_tf_Cu.sh's, else finish_tf_C.sh's; rule A's was transition_2c
    out, lab = {}, None
    if not os.path.exists(p):
        return {}
    for l in open(p):
        m = re.match(r'== (\w+): .*homeless from the housing policy \(exact\)', l)
        if l.startswith('=='):
            lab = m.group(1) if m else None
            if lab:
                out[lab] = {}
            continue
        m = re.match(r'\s+(\d+)-(\d+)\s+\S+\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', l)
        if lab and m:
            out[lab][(int(m.group(1)), int(m.group(2)))] = dict(
                sud=float(m.group(3)), h=float(m.group(4)), h_sud=float(m.group(5)), h_clean=float(m.group(6)))
    return out if {'null', 'tf'} <= set(out) else {}


def newborn_better(value='Wnd', tol='0.001', path=None):
    """NEWBORNS BETTER OFF BY THE HOUSEHOLD THEY ARE BORN INTO (the author, round f4276e76: "add a row for the newborn
    children"). results/transition_2c/newborn/shares.json (code/cf_kid on stage E2's arms): a newborn's lifetime value
    under Treatment First against Housing First in the same birth state, weighted by the Housing First newborns.
    Wnd, with no parental death before the child leaves home, is the paper's criterion (Section 6.1 replaces a dead
    parent rather than ending the childhood) and reproduces each arm's newborn welfare. Share in per cent, or None."""
    p = path or os.path.join(RC.DC['tf'], 'newborn_shares.json')   # rule C; rule A's was transition_2c/newborn/shares.json
    if not os.path.exists(p):
        return None
    return 100 * json.load(open(p))[value]['by_tolerance'][tol]['all newborns']['better']


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
    for arm in ('pe_a', 'pe_b', 'fx_d', 'ne_e', 'nc_c'):
        f = final(arm)
        D[arm] = dict(steady(arm), price=f['drug price'], piv=f['pi_V (voucher probability)'],
                      b=f['drug use b'], sud=f['SUD lambda_d'], h=f['homelessness h_1'],
                      sud_hl=f['SUD share of the homeless'], takeup=f['treatment take-up'],
                      net=f['net government revenue'], split=None, cev_net=None)
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
        ('Living with a parent who has a SUD', 'par_sud', lambda v: f'{100 * v:.2f}'),
        ('In a shelter', 'child_hl', lambda v: f'{100 * v:.2f}'),
        None,
        ('CEV of a newborn, percent of lifetime consumption', 'cev_net', lambda v: f'{v:.2f}'.replace('-', '$-$')),
        ('Share of the newborn\'s gain that comes in childhood', 'child_share', lambda v: f'{v:.0f}'),
        # APPROVAL (the author, 2 October, on Table 7: "can you add approval rates (fraction better off?) for
        # newborns and for adults entering at 26?"). Newborns are alike before birth (Section 6.1), so all or
        # none are better off, as the CEV's sign says; entering adults are compared state by state
        ('Households entering adult life at 26 better off', 'y26_better', lambda v: f'{v:.0f}'),
        ('All households better off', 'all_better', lambda v: v if isinstance(v, str) else f'{v:.0f}'),
        ('Households with a SUD better off', 'sud_better', lambda v: v if isinstance(v, str) else f'{v:.0f}'),
        # the newborns' row (the author, round f4276e76: "add a row for the newborn children"), a placeholder until
        # code/cf_kid's values from stage E2 (results/transition_2c/newborn/) are checked
        # ('Newborns better off, by the household they are born into', 'nb_hh_better', ...): OUT since 11 October --
        # stage E2's newborn run scored it with childhood at one and saved no per-cell parts, so it cannot be
        # rescored at the paper's xi - 1 until that stage is re-run with the parts saved
    ]
    for arm, base in [a for a in ARMS if a[1]]:
        s = D[arm]['split']
        D[arm]['child_share'] = 100 * s[0] / s[2] if s and arm not in ('omega1', 'internalise') else None
    # (11 October) the paper's criterion counts childhood at xi - 1: the three columns with by-node values take the
    # childhood rows of Table tab:whogains (welfare_nok.parts, in points of lifetime consumption)
    for _arm, _nodes in (('dc_b', os.path.join(RC.DC['fixboth'], 'tf')),
                         ('dc_p', _NODES['dc_p']),
                         ('dc_pv', _NODES['dc_pv']),
                         ('tf85', RC.TF_NODES)):
        D[_arm]['child_share'] = welfare_nok.parts(adir(_arm), _nodes, adir('null_share'),
                                                   RC.NULL_DIR)['pts']['child_share']
    for arm in D:
        D[arm]['nb_better'] = D[arm]['y26_better'] = D[arm]['all_better'] = D[arm]['sud_better'] = None
        D[arm]['nb_hh_better'] = None
    _nb = newborn_better()
    D['tf85']['nb_hh_better'] = _nb if _nb is not None else '\\updnum{update}'
    SH = shares()
    if SH:
        D['tf85']['all_better'] = 100 * SH['all households'][0]
        D['tf85']['sud_better'] = 100 * SH['with a SUD'][0]
    D['tf85']['nb_better'] = 100.0 if D['tf85']['cev_net'] > 0 else 0.0
    # ENTERING ADULT LIFE AT 26 (17 October, the author: "I want all the numbers to be corrected"): from the same
    # shares.txt as the other better-off rows, against the corrected Housing First at 1e-3 utils, as the columns without
    # the externalities do. The Fortran's own frac_in_support_youngest, read before, compares with the SAVED benchmark,
    # which predates the correction: the ninth column printed 17 where the corrected comparison gives 5.
    D['tf85']['y26_better'] = 100 * SH['youngest adults (age index 1)'][0] if SH else 100 * D['tf85']['adult']['young_better']
    # THE DECOMPOSITION COLUMNS' BETTER-OFF ROWS (the author, 9 October: "id like you to rerun them and remove that
    # sentence from the notes", and "make sure to put the missing things in the table in yellow, so you dont forget to
    # fill them"): from each column's re-solve (code/extra_2c/remote_decomp_shares.sh, results/decomp_2c_shares/), the
    # same measures as the last column's; \tocheck (yellow) until a column's files are in
    for _a, _k in (('dc_b', 'fixboth'), ('dc_pv', 'fixpv'), ('dc_p', 'fixp')):
        _dir = RC.DC[_k]   # rule C; rule A's was results/decomp_2c_shares/arm_<k>
        _sh = shares(path=RC.SHARES_FILE.get(_k, os.path.join(_dir, 'shares.txt')))   # (14 Oct) the corrected Housing First's
        _nbk = newborn_better(path=os.path.join(_dir, 'newborn_shares.json'))
        D[_a]['all_better'] = 100 * _sh['all households'][0] if _sh else '\\tocheck{--}'
        D[_a]['sud_better'] = 100 * _sh['with a SUD'][0] if _sh else '\\tocheck{--}'
        D[_a]['y26_better'] = 100 * _sh['youngest adults (age index 1)'][0] if _sh else '\\tocheck{--}'
        D[_a]['nb_hh_better'] = _nbk if _nbk is not None else '\\tocheck{--}'
    # the last column's welfare rows, from the walk on Arm A's distribution (results/pe_noext/RESULT.md): the CEV is the
    # newborn's adult value at 26, since its childhood is the externality the column switches off (the paragraph and the
    # table note say so); better off at the same tolerance as the Treatment First column, 1e-3 utils
    _pe = json.load(open(os.path.join(PE, 'analysis.json')))
    _ps = lambda g: 100 * _pe['shares'][g]['abs0.001']['better']
    D['pe_b'].update(cev_net=100 * _pe['cev']['newborn adult (age 26)']['cev_group'],
                     y26_better=_ps('age 26 (model age 1)'), all_better=_ps('all households'),
                     sud_better=_ps('with a SUD'))
    # the budget-rebalanced column, from its own walk on Arm A's distribution, the same way
    _fx = json.load(open(os.path.join(FX, 'analysis.json')))
    _fs = lambda g: 100 * _fx['shares'][g]['abs0.001']['better']
    D['fx_d'].update(cev_net=100 * _fx['cev']['newborn adult (age 26)']['cev_group'],
                     y26_better=_fs('age 26 (model age 1)'), all_better=_fs('all households'),
                     sud_better=_fs('with a SUD'))
    # and the column with the drug price clearing too, the same way
    _nc = json.load(open(os.path.join(NC, 'analysis.json')))
    _ns = lambda g: 100 * _nc['shares'][g]['abs0.001']['better']
    D['nc_c'].update(cev_net=100 * _nc['cev']['newborn adult (age 26)']['cev_group'],
                     y26_better=_ns('age 26 (model age 1)'), all_better=_ns('all households'),
                     sud_better=_ns('with a SUD'))
    # and the column with only the drug price clearing, the same way
    _ne = json.load(open(os.path.join(NE, 'analysis.json')))
    _es = lambda g: 100 * _ne['shares'][g]['abs0.001']['better']
    D['ne_e'].update(cev_net=100 * _ne['cev']['newborn adult (age 26)']['cev_group'],
                     y26_better=_es('age 26 (model age 1)'), all_better=_es('all households'),
                     sud_better=_es('with a SUD'))
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
    def hk(key, w):
        """a header cell: a plain key as hd(), or (old key, old text) for words the author saw under another layout"""
        if isinstance(key, str):
            return hd(key, w)
        cells[key[0]] = key[1]
        return w if prev.get(key[0]) == key[1] else f'\\textcolor{{red}}{{{w}}}'
    def table(cols, top):
        n = len(cols) + 1
        heads = {1: '\\multicolumn{%d}{@{}l}{\\emph{Adults}} \\\\' % n,
                 2: '\\multicolumn{%d}{@{}l}{\\emph{Children}} \\\\' % n,
                 3: '\\multicolumn{%d}{@{}l}{\\emph{Welfare}} \\\\' % n}
        for k in heads:
            title = re.search(r'\\emph\{([^}]*)\}', heads[k]).group(1)
            cells[f'panel/{k}'] = title
            if prev.get(f'panel/{k}') != title:
                heads[k] = heads[k].replace('\\emph{', '\\emph{\\textcolor{red}{', 1).replace('}} \\\\', '}}} \\\\', 1)
        body = [heads[1]]
        part = 1
        for r in rows:
            if r is None:
                part += 1
                body.append('\\addlinespace')
                body.append(heads[part])
                continue
            lab, key, fmt = r
            # a row the author has not seen: its label is red too
            new_row = all(f'{key}/{arm}' not in prev for arm, _ in cols)
            line = [f'\\textcolor{{red}}{{{lab}}}' if new_row and prev else lab]
            for arm, _ in cols:
                v = D[arm].get(key)
                c = '\\tocheck{--}' if arm in PENDING else '--' if v is None else fmt(v)   # pending: yellow
                # (14 October) better-off shares computed against the gated Housing First: yellow until re-solved
                if key in ('all_better', 'sud_better') and arm in RC.STALE_SHARES and v is not None:
                    c = '\\tocheck{--}'
                cells[f'{key}/{arm}'] = c
                line.append(c if prev.get(f'{key}/{arm}') == c else f'\\textcolor{{red}}{{{c}}}')
            body.append(' & '.join(line) + ' \\\\')
        return (['% Written by code/paper/export_longrun.py from results/counterfactuals_cf_fix2;',
                 '% edit the script, not this file. Caption and note are in the paper.',
                 # every row on one line (round 4ad85a30, the author: "can you put all rows in one line?")
                 '\\begin{tabular}{@{}l' + 'r' * len(cols) + '@{}}', '\\toprule'] + top +
                ['\\midrule'] + body + ['\\bottomrule', '\\end{tabular}'])
    # THE PRICE-CLEARS RUN (dc_pv) IS NO LONGER A COLUMN (the author, 9 October: "move it to a footnote"): the
    # with-externality block steps from both held to pi_V clearing to both clearing; 6.2 quotes dc_pv in a footnote
    # the two no-externality columns under one spanning head, so that no column is wider than its numbers need
    tab = table(TABLE_MAIN, [
        ' & \\multicolumn{5}{c}{' + hd('h0/0', 'No externalities') + '} & \\multicolumn{5}{c}{'
        + hd('h0/1', 'With externalities') + '} \\\\', '\\cmidrule(lr){2-6}\\cmidrule(lr){7-11}',
        # PORTRAIT (the author, 8 October: "any way to fit this table horizontally?"): one 'Treatment First' over each
        # block's Treatment First columns and their labels on two short lines, so that no column is wider than its
        # numbers need; with the paper's tabcolsep of 4pt it is 464pt against the 470pt text width
        ' & & \\multicolumn{4}{c}{' + hk(('h1/1', 'Treatment'), 'Treatment First') + '} & & \\multicolumn{4}{c}{'
        + hd('h4/1', 'Treatment First') + '} \\\\', '\\cmidrule(lr){3-6}\\cmidrule(lr){8-11}',
        # which Treatment First: the drug price and pi_V both held, one of them clearing, or both clearing. 'both held'
        # in place of the no-externality block's '$\\pi_V$ held' once 'price clears' sits in the same row
        # a label whose words the author has seen stays black: the key it had before the stacking, and its whole text
        ' & ' + ' & '.join(hk(k, w) for k, w in (
            (('h1/0', 'Housing'), 'Housing'), ('h5/1', 'Both'), (('h3/1', '$\\pi_V$ clears'), '$\\pi_V$'),
            ('h5/ne', 'Price'), ('h5/nc', 'Both'), (('h1/4', 'Housing'), 'Housing'), ('h5/5', 'Both'),
            ('h5/7', '$\\pi_V$'), ('h5/pv', 'Price'), ('h5/8', 'Both'))) + ' \\\\',
        ' & ' + ' & '.join(hk(k, w) for k, w in (
            (('h2/0', 'First'), 'First'), ('h6/1', 'held'), (('h3/1', '$\\pi_V$ clears'), 'clears'),
            ('h6/ne', 'clears'), ('h6/nc', 'clear'), (('h2/4', 'First'), 'First'), ('h6/5', 'held'),
            ('h6/7', 'clears'), ('h6/pv', 'clears'), ('h6/8', 'clear'))) + ' \\\\'])
    tab_app = table(TABLE_APP, [
        ' & ' + ' & '.join(hd(f'a1/{k}', w) for k, w in enumerate(('Housing', 'Full'))) + ' \\\\',
        ' & ' + ' & '.join(hd(f'a2/{k}', w) for k, w in enumerate(('First', 'altruism'))) + ' \\\\'])
    open(TAB_APP, 'w').write('\n'.join(tab_app) + '\n')
    open(TAB, 'w').write('\n'.join(tab) + '\n')
    if freeze:
        json.dump(cells, open(PREV, 'w'), indent=1)

    # ---- names for the prose
    t, e, o = 'tf85', 'old_elast5_85', 'omega1'
    # the last column against ITS base, Housing First without the externalities (Arm A), which the table does not show:
    # the paragraph that opens Section 6.2 and the table note
    A_, B_ = D['pe_a'], D['pe_b']
    for k, f in (('price', lambda v: f'{v:.2f}'), ('b', lambda v: f'{100 * v:.2f}'), ('sud', lambda v: f'{100 * v:.2f}'),
                 ('h', lambda v: f'{100 * v:.2f}'), ('par_use', lambda v: f'{100 * v:.2f}'),
                 ('par_sud', lambda v: f'{100 * v:.2f}'), ('child_hl', lambda v: f'{100 * v:.2f}')):
        out[f'x_pe_a_{k}'] = f(A_[k])
    for k in ('b', 'sud', 'h', 'child_hl'):
        ch = 100 * (B_[k] / A_[k] - 1)
        out[f'x_pe_{k}_pc'] = f'{abs(ch):.0f}'
        out[f'x_pe_{k}_dir'] = 'falls' if ch < 0 else 'rises'
    # the budget-rebalanced column against the same base (the discussion in the 'without externalities' paragraph)
    F_ = D['fx_d']
    for k in ('b', 'sud', 'h'):
        ch = 100 * (F_[k] / A_[k] - 1)
        out[f'x_fx_{k}_pc'] = f'{abs(ch):.0f}'
        out[f'x_fx_{k}_dir'] = 'falls' if ch < 0 else 'rises'
    out['x_fx_piv0_pc'] = f"{100 * A_['piv']:.2f}"
    out['x_fx_piv1_pc'] = f"{100 * F_['piv']:.2f}"
    out['x_fx_piv_dir'] = 'rises' if F_['piv'] > A_['piv'] else 'falls'
    assert F_['cev_net'] < 0, F_['cev_net']
    out['x_fx_newborn_cev'] = f"{abs(F_['cev_net']):.2f}"
    out['x_fx_all_better_pc'] = f"{F_['all_better']:.0f}"
    out['x_fx_sud_worse_pc'] = f"{100 * _fx['shares']['with a SUD']['abs0.001']['worse']:.0f}"
    out['x_fx_better_cev'] = f"{100 * _fx['cev']['better off (dV>0.001)']['cev_group']:.2f}"
    # the column with the drug price clearing too. Under rule A the cheaper drug turned the no-externality loss into a
    # gain (+0.39); under rule C the newborn still loses (-0.54), so the sign is a word and the number its size
    N_ = D['nc_c']
    assert N_['price'] < A_['price'], (N_['price'], A_['price'])
    out['x_nc_newborn_cev'] = f"{abs(N_['cev_net']):.2f}"
    out['x_nc_newborn_dir'] = 'gain' if N_['cev_net'] > 0 else 'still lose'   # r322, the author: "still lose"
    # (round r321) the Discussion's 'A cheaper drug can turn that into a small gain' was rule A's; under rule C the
    # newborn still loses with the drug price clearing too, so the cheaper drug only narrows the loss
    out['x_disc_cheaper'] = (
        'A cheaper drug can turn that into a small gain, but that is not a correction of moral hazard but rather the '
        "drug market's response, which depends on the elasticity of the drug's supply." if N_['cev_net'] > 0 else
        # r322, the author: 'without' -> "but does not reverse the conclusions", and the rest of the sentence "remove"
        'A cheaper drug narrows that loss but does not reverse the conclusions.')
    out['x_nc_price_pc'] = f"{100 * (1 - N_['price'] / A_['price']):.0f}"
    out['x_nc_piv1_pc'] = f"{100 * N_['piv']:.2f}"
    out['x_nc_b_pc'] = f"{100 * (1 - N_['b'] / A_['b']):.0f}"
    out['x_nc_all_better_pc'] = f"{N_['all_better']:.0f}"
    out['x_nc_sud_worse_pc'] = f"{100 * _nc['shares']['with a SUD']['abs0.001']['worse']:.0f}"
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
        'This is because a parent who counts their child as themselves bears in full what a '
        'shelter costs the child, and spends what they have to keep the child housed. Thus, the fall comes in '
        'the years a child lives at home, whereas among households aged 51 to 64, whose children have left, '
        f'homelessness {"rises" if _aft > 0 else "falls"} by {abs(_aft):.0f} percent.'
        if D[o]['h'] < D['null_remote']['h'] and _kid < 0 and _aft > 0 else
        'This is because a parent who counts their child as themselves bears in full what a '
        'shelter costs the child, and spends what they have to keep the child housed.'
        if D[o]['h'] < D['null_remote']['h'] and _kid < 0 else '')
    i = 'internalise'
    # OPTIMAL HOMELESSNESS IS FULL ALTRUISM PLUS THE HOMELESSNESS EXTERNALITY (the author, 2 October: "no,
    # it includes also omega_c=1"), so its changes are measured from the optimal-drug-use column when
    # the arm ran at omega_c = 1, and from the benchmark for the old arm, which did not
    _ho_i = dict(l.split()[:2] for l in open(os.path.join(adir(i), 'PARAM_HANDOVER.arm.txt')) if len(l.split()) >= 2)
    ib = o if abs(float(_ho_i.get('weight_on_child', 0)) - 1) < 1e-9 else 'null_remote'
    out['x_lr_in_base_word'] = 'full altruism' if ib == o else 'the benchmark'
    out['x_lr_in_dh_pc'] = f"{abs(pc(i, 'h', ib)):.0f}"
    out['x_lr_in_dh_dir'] = 'lower' if D[i]['h'] < D[ib]['h'] else 'higher'
    # the verb (the author, 2 October: 'leaves' -> 'reduces')
    out['x_lr_in_dh_verb'] = 'reduces' if D[i]['h'] < D[ib]['h'] else 'raises'
    # households can act on their housing, and many do when they weigh their child (the author, 2
    # October: "many do reduce homelessness when they weigh their child, so it's not that they cannot
    # afford to rent a place"): only when full altruism did lower homelessness
    out['x_lr_in_many_do'] = (', and many do when they weigh their child, as the full-altruism column shows'
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
    out['x_lr_in_piv_sentence'] = '$\\pi_V$ remains practically unchanged relative to full altruism.' if abs(_p1 / _p0 - 1) < 0.01 else (
        f"$\\pi_V$ {'rises' if _p1 > _p0 else 'falls'}, "
        f"from ${100 * _p0:.2f}$ percent {_pw} to ${100 * _p1:.2f}$ percent, to hold net government revenue at "
        'its benchmark level.')
    # homelessness by age band under Treatment First: 26-34 against 35-44
    hb0, hb1 = D['null_share']['hl_band'], D[t]['hl_band']
    out['x_lr_hl_b1_pc'] = f'{100 * (hb1[1] / hb0[1] - 1):.0f}'
    out['x_lr_hl_b2_pc'] = f'{100 * (hb1[2] / hb0[2] - 1):.0f}'
    # the newborn's gain: net CEV, and the adult part's composition share
    # THE DECOMPOSITION WALKED THROUGH COLUMN BY COLUMN (the author, 8 October: "explain in section 6 what experiments we
    # do and walk the reader through each of them"): each held/clearing run against Housing First, its direction word
    # turning with the number, 'is unchanged' when it rounds to zero
    def _ch(arm, k):
        v = pc(arm, k, 'null_share')
        return 'is unchanged' if round(abs(v)) == 0 else f"{'falls' if v < 0 else 'rises'} by ${abs(v):.0f}$ percent"
    for _a, _n in (('dc_b', 'dcb'), ('dc_pv', 'dcpv'), ('dc_p', 'dcp')):
        out[f'x_{_n}_b'] = _ch(_a, 'b')
        out[f'x_{_n}_h'] = _ch(_a, 'h')
    # THE RUN THAT ISOLATES THE EXTERNALITIES (the author, 9 October: "here you need to give the exact experiment that
    # shows it"): with both held, the children in a shelter and the share of the gain that comes in childhood
    out['x_dcb_hchild0'] = f"{100 * D['null_share']['child_hl']:.2f}"
    out['x_dcb_hchild1'] = f"{100 * D['dc_b']['child_hl']:.2f}"
    out['x_dcb_hchild_dir'] = 'rises' if D['dc_b']['child_hl'] > D['null_share']['child_hl'] else 'falls'
    # (14 October, rule C) the sentence that sets the held-pi_V column against the main one ('That holds with the
    # screen's savings recycled; with pi_V held, it ...'): when both fall, 'falls as well'
    out['x_dcb_hchild_also'] = ('rises' if D['dc_b']['child_hl'] > D['null_share']['child_hl'] else
                                'falls as well' if D[t]['child_hl'] < D['null_share']['child_hl'] else 'falls')
    # (14 October, rule C) the introduction's 'while the share of children in a shelter rises only from': the
    # 'only' belonged to a small rise, and printed 'falls only from 1.03 to 0.95' once the share fell
    out['x_dcb_hchild_dironly'] = 'rises only' if D['dc_b']['child_hl'] > D['null_share']['child_hl'] else 'actually falls'   # r324
    # (14 October, rule C) whose childhood homelessness the budget and earnings externalities outweigh: 'the few more
    # children the screen sends to a shelter' was rule A's, where the share rose; under rule C it falls
    out['x_dcb_hl_ext'] = ('of the few more children the screen sends to a shelter'
                           if D['dc_b']['child_hl'] > D['null_share']['child_hl'] else
                           'of the children of the users the screen puts out, who are fewer than the children it keeps '
                           'out of a shelter by cutting use')
    # (round r321, the author on that sentence: "well, here there is no trade off at all. you need to write it that
    # way", and "you can say there is no aggregate tradeoff, but for individuals there might be"): when the share of
    # children in a shelter falls, the whole sentence says so, in Section 6.2 (both held) and the introduction
    _dcb_up = D['dc_b']['child_hl'] > D['null_share']['child_hl']
    out['x_dcb_ext_sentence'] = (
        'These \\emph{budget and earnings externalities}, which Housing First leaves in place, therefore outweigh '
        'the \\emph{childhood homelessness externality} of the few more children the screen sends to a shelter.'
        if _dcb_up else
        'In the aggregate, these \\emph{budget and earnings externalities}, which Housing First leaves in place, come '
        'with no trade-off against the \\emph{childhood homelessness externality}: by cutting use, the screen keeps '
        'more children out of a shelter than it sends to one by putting their parents out.')   # (r345: the individual-child clause removed)
    out['x_intro_ext_sentence'] = (
        'Therefore, the \\emph{budget and earnings externalities} dominate both the \\emph{childhood homelessness '
        'externality} and the direct loss to the parent from the removal of an option.' if _dcb_up else
        'In the aggregate, then, there is no trade-off between the externalities: by cutting use, the screen keeps '
        'more children out of a shelter than it sends to one by putting their parents out. What the \\emph{budget, '
        'earnings and childhood homelessness externalities} have to outweigh is only the direct loss to the parent from '
        'the removal of an option. As I explain below, even the parent gains once general-equilibrium effects are '
        'taken into account.')   # 18 October, the author on the brackets: "not sure we need the brackets..."   # r324-r325, the author   # r322, the author on 'although a child whose parent it puts out can still lose its home': "remove"
    # the abstract, on the main experiment's long run
    out['x_abs_hchild_sentence'] = (
        "Sobriety conditions reduce these harms more than they expose screened-out users' children to homelessness."
        if D[t]['child_hl'] > D['null_share']['child_hl'] else
        'Sobriety conditions reduce these harms and, in aggregate, also childhood homelessness.')
    # (18 October, the author on the abstract: "merge this with the sentence after") the same verdict as a clause of the
    # long-run sentence, "In the long run, with the screen's savings recycled into vouchers, sobriety conditions ..."
    out['x_abs_hchild_clause'] = (
        "reduce these harms more than they expose screened-out users' children to homelessness"
        if D[t]['child_hl'] > D['null_share']['child_hl'] else
        'reduce these harms and, in aggregate, also childhood homelessness')
    out['x_dcb_child_pc'] = f"{D['dc_b']['child_share']:.0f}"
    _pp = pc('dc_pv', 'price', 'null_share')
    out['x_dcpv_price_verb'] = 'lowers' if _pp < 0 else 'raises'
    out['x_dcpv_price_pc'] = f'{abs(_pp):.0f}'
    out['x_dcp_piv_dir'] = 'rises' if D['dc_p']['piv'] > D['null_share']['piv'] else 'falls'
    # TABLE 5'S EIGHTH COLUMN DOES NOT BALANCE THE BUDGET (18 October, the author: "I want all the numbers to be
    # corrected"): no pi_V holds net revenue at its benchmark there (results/decomp_2c_fixp_clear, pi_V free for 15
    # passes: drug use flips between about -48 and -42 percent as pi_V crosses a threshold), so the note says so with
    # the column's own miss (its final.txt 'net government revenue ... change') and the threshold, the midpoint between
    # the highest pi_V of a pass on the lower-use side and the lowest of one on the higher-use side
    _rv = [l for l in open(os.path.join(RC.DC['fixp'], 'final.txt')) if l.strip().startswith('net government revenue')]
    _rvc = abs(float(re.search(r'change\s+([-+0-9.]+)%', _rv[0]).group(1)))
    out['x_dc_p_rev_pc'] = f'{_rvc:.2f}'
    _fc = open(os.path.join(ROOT, 'results', 'decomp_2c_fixp_clear', 'status.txt')).read()
    assert 'NOT CLEARED' in _fc, 'the free-pi_V test cleared: the column can clear, and the note should not say otherwise'
    _ps = [(float(r[2]), float(r[3].rstrip('%'))) for r in (l.split() for l in _fc.splitlines())
           if len(r) > 5 and re.fullmatch(r'\d+', r[0]) and re.fullmatch(r'1\.\d+', r[1])][1:]   # pass 1 is the start
    _lo = max(v for v, b in _ps if b < -45); _hi = min(v for v, b in _ps if b > -45)
    assert _lo < _hi, (_lo, _hi)
    out['x_dcp_jump_piv'] = f'{100 * (_lo + _hi) / 2:.1f}'
    # (round r287, the author: "what about childhood homelessness?", and "Childhood homelessness drops because of the
    # additional spending on vouchers lifts other non-user households out of homelessness")
    # (round r288, the author: "by X percent", and "of child-rearing age"; r289: "low-income households")
    out['x_dcp_hchild'] = _ch('dc_p', 'child_hl')
    out['x_dcp_hchild_why'] = ('Childhood homelessness falls because the additional spending on vouchers lifts other '
                               'low-income households of child-rearing age, which do not use drugs, out of homelessness.'
                               if D['dc_p']['child_hl'] < D['null_share']['child_hl'] else '')
    # (round r287, the author on what raises tax revenue: "I think it's mostly this [children inheriting higher
    # productivity draws] because in the no externality cases the increase in piv is very small which captures just the
    # unemployment channel"). The sentence says "mostly" while pi_V's rise at Housing First's drug price with the
    # externalities is more than twice its rise without them; the SUD share falls by about as much in both columns.
    assert D['dc_p']['piv'] - D['null_share']['piv'] > 2 * (F_['piv'] - A_['piv']), (D['dc_p']['piv'], F_['piv'])
    # WHY THE EIGHTH COLUMN CUTS DRUG USE MOST (the author, 9 October: "you should explain why. drug use falls more
    # because pi_v is higher and pi_v is higher because the higher drug price deters more use"). Against the sixth
    # column (both held) only pi_V differs; against Treatment First itself only the drug price does. The sentence
    # stands only while both comparisons go that way.
    _b_more = D['dc_p']['b'] < D['dc_b']['b']
    _pv_more = D['dc_p']['piv'] > D[t]['piv'] and D['dc_p']['price'] > D[t]['price']
    # (the author, 9 October: "receiving a voucher more likely, and thus staying clean worth more"; the clause on pi_V
    # rising by more than under Treatment First itself dropped, "the reader doesnt know this yet")
    # (14 October, rule C) with the screen exempting treatment, drug use falls by about as much with pi_V clearing as
    # with both held (-42 against -43 per cent): then the sentence says that, and nothing about why it falls more
    _b_close = abs(D['dc_p']['b'] / D['dc_b']['b'] - 1) < 0.05
    out['x_dcp_why'] = ('Drug use falls by more than with both held because the higher $\\pi_V$ makes receiving a '
                        'voucher more likely, and thus staying clean worth more.' if _b_more and not _b_close else
                        'Drug use falls by about as much as with both held.' if _b_close else '')
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
    # 45 TO 50 (round f4276e76, the author on 'At 35 to 44 the second force wins': "what about the 45-50? is it
    # the same as that?", and "should they not also have the second force being higher?"). It is higher: the SUD
    # share of the homeless is printed by ten-year band only, so the band 45 to 54 stands in for it. What turns
    # the sign there is the third force of the balance above, the revoked vouchers going to clean households:
    # homelessness among households without a SUD falls by a seventh at 45 to 54, against 1 or 2 percent younger
    _rc = lambda hb, qb, sb, k: (hb[k] - sb[k] * _rs(hb, qb, sb, k)) / (1 - sb[k])
    r3 = [_rs(hb0, q0b, s0b, 3), _rs(hb1, q1b, s1b, 3)]
    c3 = [_rc(hb0, q0b, s0b, 3), _rc(hb1, q1b, s1b, 3)]
    _cy = max(abs(_rc(hb1, q1b, s1b, k) / _rc(hb0, q0b, s0b, k) - 1) for k in (1, 2))
    _third = (c3[1] / c3[0] - 1 < -2 * _cy and r3[1] / r3[0] > r2[1] / r2[0] and s1b[3] < s0b[3] and _b45 < 0)
    _45 = (
        # (round r115, the author: "look for paragraphs that are too long... and break them down": one per age band)
        '\n\nAt 45 to 50 the second force is stronger still. The SUD figures are by ten-year band, and across ages 45 '
        f'to 54 the share of households with a SUD who are homeless rises from ${_f(r3[0])}$ to ${_f(r3[1])}$ '
        'percent. But at these ages the vouchers the reform revokes do more for everyone else. They go to other '
        'clean and eligible households, and homelessness among households without a SUD falls from '
        f'${_f(c3[0])}$ to ${_f(c3[1])}$ percent, against almost no change at younger ages. Together with the fall '
        f'in the share with a SUD, from ${_f(s0b[3])}$ to ${_f(s1b[3])}$ percent, this outweighs the second force, '
        f'so homelessness at 45 to 50 falls by ${abs(_b45):.0f}$ percent.' if _third else '')
    # TREATMENT (the author, 2 October: "you should also make a point about how treatment goes increase in TF....
    # put it in the resutls somwhere where it flows"). Treatment buys only the multiplier g on recovery
    # (Section 4), and under Treatment First a household that has recovered and does not use passes the screen
    _tk0, _tk1 = D['null_share']['takeup'], D[t]['takeup']
    out['x_lr_tf_treat'] = (
        # (14 October, rule C) treatment is now also how a household with a SUD keeps its voucher: in treatment and not
        # using, it passes the screen, which is the first reason; recovery's is the second
        # (round r324, the author: "a bit too long...break it down")
        'It also raises the share of households with a SUD who are in treatment, from '
        # (round r325, the author: '.' -> 'because', and the recovery sentence "can be removed")
        f'${100 * _tk0:.1f}$ to ${100 * _tk1:.1f}$ percent, because a household with a SUD that is in treatment and does '
        'not use passes the screen.' if _tk1 > _tk0 else '')
    # (round 0e3b2441, the author: 'only' -> 'only buys', 'voucher.' -> 'if eligible and offered a voucher', and on
    # 'household': "eligible household (check that you use that kind of language in the results section....the
    # eligibility is still key)": every 'more likely to get a voucher' now says the household is eligible)
    out['x_lr_children_hl'] = (
        'Children live with households aged 26 to 50. Across those ages the reform moves homelessness in '
        f'opposite directions: it falls by ${abs(_b1):.0f}$ percent among households aged 26 to 34, rises by '
        f'${abs(_b2):.0f}$ percent at 35 to 44 and falls by ${abs(_b45):.0f}$ percent at 45 to 50. The changes '
        'cancel out almost exactly. Which way it goes at a given age depends on the balance of the two forces above. Treatment First '
        'cuts the number of households with a SUD, but raises the risk of homelessness for those who still have '
        'one, because they lose their voucher.\n\nAt 26 to 34 the first force wins. The share of households with a SUD '
        f'falls from ${_f(s0b[1])}$ to ${_f(s1b[1])}$ percent, while the share of them who are homeless rises only '
        f'from ${_f(r1[0])}$ to ${_f(r1[1])}$ percent. So homelessness at these ages falls from ${_f(hb0[1])}$ to '
        f'${_f(hb1[1])}$ percent. This is because a disorder acquired young has not yet kept most of these '
        'households unemployed for long, so few of them depend on a voucher to stay housed.\n\nAt 35 to 44 the second '
        f"force wins. The share with a SUD falls {'by about as much' if abs(_d1 - _d2) < 5 else 'too'}, from "
        f'${_f(s0b[2])}$ to ${_f(s1b[2])}$ percent, but these households have carried the disorder longer, and more '
        'of them have remained unemployed because of it and depend on a voucher. Without the vouchers, the share of them who are homeless rises '
        f'from ${_f(r2[0])}$ to ${_f(r2[1])}$ percent, so homelessness at these ages rises from ${_f(hb0[2])}$ to '
        f'${_f(hb1[2])}$ percent.' + _45
        if _b2 > 0 > _b1 and _b45 < 0 and s1b[1] < s0b[1] and s1b[2] < s0b[2] and r2[0] > r1[0]
        and r2[1] / r2[0] > r1[1] / r1[0] > 1 and _u1 + _n1 < 0 < _u2 + _n2
        and abs(100 * (D[t]['child_hl'] - D['null_share']['child_hl'])) < 0.005 else '')
    # AT 26 TO 50 TAKEN TOGETHER (round r133, the author: "Why do we need to break it down by ages? cant we just talk
    # about the aggregate during these ages? i feel like it would be easier to follow, no?"; before that, 2 October, by
    # 26-38 and 39-50), from age_split()'s 26-50 row, the years a child lives at home. The three effects are
    # x_tf_h_sentence's, in its order: the change in homelessness is lam1 (rs1 - rs0), the higher risk of those who keep
    # a SUD, plus (lam1 - lam0)(rs0 - rc0), fewer with a SUD, plus (1 - lam1)(rc1 - rc0), the households without a SUD,
    # who get the revoked vouchers. It follows x_tf_hchild_sentence's unchanged shelter share
    AS = age_split()
    if AS:
        A0, A1 = AS['null'][(26, 50)], AS['tf'][(26, 50)]
        _ach = 100 * (A1['h'] / A0['h'] - 1)
        l0, l1 = A0['sud'] / 100, A1['sud'] / 100
        e1 = l1 * (A1['h_sud'] - A0['h_sud'])
        e2 = (l1 - l0) * (A0['h_sud'] - A0['h_clean'])
        e3 = (1 - l1) * (A1['h_clean'] - A0['h_clean'])
        _p = lambda x: f'{x:.2f}'
        # (round r137, the author: "why not just combine that paragraph about the children with the previous paragraph
        # and say that the same three effect basically net to zero also for households aged 26-50, which is the years
        # the children live them, and therefore childhood homelessness remains unchanged at 1.03 percent"): one
        # sentence closing x_tf_h_sentence's paragraph, in place of x_tf_hchild_sentence and the r133-r136 paragraph
        _c0, _c1 = 100 * D['null_share']['child_hl'], 100 * D[t]['child_hl']
        out['x_lr_children_hl'] = (
            'For households aged 26 to 50, the years a child lives with them, the same three effects nearly net to '
            f'zero, so the share of children in a shelter remains unchanged at ${_c0:.2f}$ percent.'
            if abs(_ach) < 1 and e1 > 0 > e2 and e3 < 0 and abs(e1 + e2 + e3) < 0.25 * e1
            and f'{_c0:.2f}' == f'{_c1:.2f}' else
            # (14 October, rule C) homelessness falls at these ages too, and with it the shelter share
            # (round r345, the author: 'so' -> 'with', 'falls' -> 'falling')
            'For households aged 26 to 50, the years a child lives with them, homelessness also falls by '   # r324
            f'${abs(_ach):.0f}$ percent, with the share of children in a shelter falling from ${_c0:.2f}$ to ${_c1:.2f}$ '
            'percent.' if _ach <= -1 and _c1 < _c0 else '')
        if not out['x_lr_children_hl']:
            print('WARNING: the 26-50 children paragraph does not match the split; check age_split.txt',
                  file=sys.stderr)
    _r = pc(t, 'b', 'null_share') / pc(o, 'b', 'null_remote')
    _tfb, _omb = out['x_lr_tf_b_pc'], out['x_lr_om_b_pc']
    out['x_lr_tf_vs_om'] = (
        f"Treatment First delivers ${out['x_lr_tf_of_om_pc']}$ percent of the fall in drug use that full "
        f"altruism would bring, ${_tfb}$ percent against ${_omb}$." if _r <= 1.05 else
        f"Treatment First cuts drug use by more than full altruism would, ${_tfb}$ percent against ${_omb}$.")
    _hless = abs(pc(t, 'h', 'null_share')) < abs(pc(o, 'h', 'null_remote'))
    out['x_lr_tf_vs_om2'] = (
        f"Treatment First (with externalities) cuts drug use by more than full altruism does, ${_tfb}$ percent against ${_omb}$, but "
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
                               + ('leaves the share of children in a shelter roughly constant' if _hflat else
                                  f"{'raises' if _hc_t > 0 else 'lowers'} the share of children in a shelter"))
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
    # (round r157, the author: 'it' -> 'but', after "With externalities, conditionality reduces ...")
    out['x_abs_tf_exposes'] = ('but also raises homelessness' if _trise else
                               'but also exposes those it screens out to homelessness')
    out['x_abs_om_adv'] = 'sharply ' if abs(pc(o, 'b', 'null_remote')) >= 25 else ''
    # the Discussion's recycled revenue (round 0e3b2441, the author on 'worth more': ", and homelessness actually
    # declines slgithy with chioldhood homelessness unaffected in the long run"): Section 6.2's balance credits the
    # vouchers that go to clean and eligible households with lowering homelessness
    out['x_disc_recycle_h'] = (', and homelessness actually declines slightly in the long run, with childhood '
                               'homelessness unaffected' if not _trise and _hflat and _tf_dh_abs < 3 else '')
    out['x_abs_tf_result'] = (
        'In the long run, conditioning assistance raises homelessness but cuts drug use' if _trise else
        # (round r120, the author: 'In the long run,' and 'substantially' moved: "drug use substantially ... in the long run, and")
        # (3 October, the author: "as government recycles excess revenues as vouchers to other poor households"; the
        # decomposition shows recycling is what lowers homelessness -- with pi_V held it would rise)
        # (round r140, the author on 'substantially': "remove")
        'Conditioning assistance cuts drug use in the long run, and, as excess revenues fund more vouchers '
        f"for clean poor households, lowers homelessness{' slightly' if _tf_dh_abs < 3 else ''}")
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
    # THE SPLIT OF ADULT LIFE (10 October): the same objects as Table tab:whogains (export_welfare.py), without the
    # kappa_x * H term, so that the prose and the table agree: comp is E / beta^J_K, the composition term over the 26
    # entry nodes at Treatment First's values, and tot - comp is P, the same-state gain of every household at 26.
    # Before, comp was the penalty class's share change at Housing First's gap alone (11 against 13 percent).
    _parts = welfare_nok.parts(adir(t), RC.TF_NODES, adir('null_share'), RC.NULL_DIR)
    comp = _parts['E'] / _parts['b25']
    tot = _parts['A'] / _parts['b25']
    _pts = _parts['pts']                 # the same split in points of lifetime consumption (Table tab:whogains)
    adult_utils = D[t]['split'][1]
    # (14 October) the check compares like with like: the final.txt split carries the kappa_x * H term and parts() does
    # not (the paper's criterion leaves it out). Under rule A homelessness barely moved, so the term's difference was
    # nil and A matched the split to 0.1 per cent; under rule C homelessness falls 11 per cent and it no longer is
    _A_with = (welfare_nok.components(welfare_nok.arm_values(adir(t)), with_term=True)[1]
               - welfare_nok.components(welfare_nok.arm_values(adir('null_share')), with_term=True)[1])
    assert abs(_A_with / adult_utils - 1) < 0.02, \
        f'ADULTDECOMP {_A_with:.4f} (with the term) does not reproduce the adult part {adult_utils:.4f}'
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
    _kid = _pts['child_share']                   # the childhood rows of Table tab:whogains, percent of the gain
    _draw = 100 * _pts['E'] / _pts['tot']        # better productivity at entry
    _val = 100 * _pts['own'] / _pts['tot']       # the newborn's own adult life under the policy
    # the penalty's share of the WHOLE gain, for Section 5's delta_d item (3 October: the ranking does not rest on it)
    out['x_lr_draw_whole_pc'] = f'{_draw:.0f}'
    _pvpc, _prpc = pc(t, 'piv', 'null_share'), pc(t, 'price', 'null_share')
    # (round f4276e76, the author on this sentence: "should this come where the point about the voucher comes about
    # 2 sentence bfore? can you make it read better?") it now follows the voucher sentence
    # HOW MUCH MORE AT THE BOTTOM (the author, 2 October: "if these are the newest numbers, yes"): the value of
    # entering adult life at 26 by productivity node, stage E's re-solved arms (results/transition_2c/arm_*/
    # value_at_26_by_node.txt, nodes 1-13 a clean parent): its gain at the lowest node over its gain at the highest
    # rule C (14 October): the main arm and Housing First re-solved side by side (results/decomp_2c_shares_C/arm_tf)
    _v26 = {'null': os.path.join(RC.NULL_DIR, 'value_at_26_by_node.txt'),
            'tf': os.path.join(RC.TF_NODES, 'value_at_26_by_node.txt')}
    _r26 = None
    if all(os.path.exists(_v26[a]) for a in ('null', 'tf')):
        _n0, _n1 = ([float(x) for x in open(_v26[a]).read().split()] for a in ('null', 'tf'))
        _g26 = [b - a for a, b in zip(_n0, _n1)][:13]
        _r26 = _g26[0] / _g26[-1] if min(_g26) > 0 else None
    _need = (', as the value of entering adult life rises about ${:.0f}$ times as much at the lowest productivity '
             'as at the highest'.format(_r26) if _r26 else '')
    _poor = (' And a voucher is worth most to a household that enters adult life with low productivity, because it is '
             f'the likeliest to need one{_need}. This part of the gain is therefore larger for a child whose own parent '
             'carried the disorder, since the penalty leaves it with lower productivity.' if _gp > _gc > 0 else '')
    # the drug users' line (the author: "are they better off too in welfare terms actually?" on 'Drug users gain
    # too', and "so they can consume more of it!"): stated as the channel, which is what the decomposition
    # measures, not as a claim that users are better off on net; the mean quantity per user rises
    _q = [D[a]['adult'].get('q_user') for a in ('null_share', t)]
    _qup = None not in _q and _q[1] > _q[0]
    out['x_lr_adult'] = (
        f"The other ${100 - _kid:.0f}$ percent comes in adult life, from two sources. The first, ${_draw:.0f}$ "
        'percent of the whole gain, is the better productivity node a child draws, mostly because its own parent does not carry the '
        f"disorder. Escaping the penalty is worth a lot to each child it spares, about ${out['x_lr_pen_ratio']}$ "
        'times what the average child gains at the same productivity. But it spares only about '
        f"${float(out['x_lr_pen0']) - float(out['x_lr_pen1']):.0f}$ percent of children, since the share of newborns who "
        f"enter adult life with the penalty {out['x_lr_pen_dir']} from ${out['x_lr_pen0']}$ to ${out['x_lr_pen1']}$ "
        # (round r114, the author: "new paragraph" before 'The second')
        f"percent.\n\nThe second, the remaining ${_val:.0f}$ percent, does not come from the child's productivity at "
        'all. It is a result of the better economy it lives its adult life in. A clean and eligible household is '
        # (3 October, "so it is less heavy": why pi_V rises is the first paragraph's, and is not repeated here)
        f'${_pvpc:.0f}$ percent more likely to draw a voucher.'
        if comp / tot < 0.5 and _gc > 0 and _gp > 0 and _pvpc > 0 > _prpc and _qup else '')
    # the moved sentence and the drug users' line are names of their own, so the move shows whole
    out['x_lr_adult_poor'] = _poor.strip() if out['x_lr_adult'] else ''
    out['x_lr_adult_drug'] = (
        f'Moreover, even a child who goes on to use drugs pays less for them: the drug is ${abs(_prpc):.0f}$ percent cheaper in '
        'equilibrium.' if out['x_lr_adult'] else '')
    # THE INTRODUCTION'S ACCOUNT OF THE GAIN (round 20b4ddb5, the author: "too long and not clear...i still dont
    # understand where the rest of the gains in adulthood come from"): the same three shares of the whole gain
    # (round 538f55b4, the author on 'Lastly, even drug users benefit from the lower equilibrium drug price': "does
    # their welfare rise?", and round 0e3b2441: "flagging to check"). The price helps them, but on net most households
    # that have a SUD lose: shares.txt, better by more than the tolerance against the no-policy run
    _SH = shares()
    _sb = 100 * _SH['with a SUD'][0] if _SH else None
    # (round 3350a58a, the author: 'although only' -> 'with', 'since they' -> 'despite losing')
    # (round 3672e7b1, the author: "is that about the transition or about the long run?": the long run, the
    # steady-state comparison of Table 7, so the sentence says so)
    _sud_net = (f', with ${_sb:.0f}$ percent of the households that have a SUD better off on net in the long run, '
                'despite losing access to vouchers' if _sb is not None and _sb < 50 else '')
    out['x_lr_better_tol'] = '0.001'
    # the share alone, for the introduction's list of what differs from the stylized model (the author, 5 October:
    # "maybe you can just state which results are different?"): in the stylized model no user gains
    out['x_lr_sud_better_pc'] = f'{_sb:.0f}' if _sb is not None else ''
    out['x_lr_all_better_pc'] = f"{100 * _SH['all households'][0]:.0f}" if _SH else ''
    # WHO IS NEITHER (8 October, the author on 76 against the transition's 97: "why not 76%?"): within the tolerance,
    # the rest are unaffected, and results/transition_2c/value_shares.txt puts none of them below 51 (ages 26-50:
    # better 0.9462, unchanged 0.0000), so the sentence says who they are
    out['x_lr_all_worse_pc'] = f"{100 * _SH['all households'][1]:.0f}" if _SH else ''
    out['x_lr_approve_sud'] = (
        f"Across all households, ${100 * _SH['all households'][0]:.0f}$ percent are better off and "
        # (14 October, rule C) who the rest are and why households with a SUD gain were rule A's findings (the value
        # shares by age, and the drug price as the only gain open to a household that cannot pass the screen); under
        # rule C one in treatment that stops passes it and draws the higher pi_V, so both clauses are yellow until checked
        # (round r325, the author on the two yellow clauses: "you dont have the asnwers to this?": the shares carry no
        # ages and no reason, so the clauses go and the numbers stay)
        f"${100 * _SH['all households'][1]:.0f}$ percent worse off, and the rest are essentially unaffected. Finally, "
        f"even ${_sb:.0f}$ percent of those that have a SUD are better off."
        if _SH and _sb is not None and _sb < 50 else '')
    out['x_intro_gain'] = (
        f"A newborn gains ${D[t]['cev_net']:.2f}$ percent of lifetime consumption. About ${_kid:.0f}$ percent of that "
        "gain comes in childhood, from a parent who spends more on the child's consumption and housing and less on "
        f'drugs, and is less likely to remain unemployed longer because of a SUD, further improving childhood consumption. About '
        f'${_draw:.0f}$ percent comes from the higher earnings of a child whose parent was free of the '
        f'disorder. The remaining ${_val:.0f}$ percent comes from a better economy to live in as an adult: whatever '
        f'its productivity, an eligible household that stays clean is ${_pvpc:.0f}$ percent more likely to get a voucher, paid '
        'for by the users the screen excludes and by the higher taxes paid by working-age households that no longer '
        'carry the earnings penalty or remain unemployed longer because of a SUD. Lastly, even some drug users benefit from the lower '
        'equilibrium drug price' + _sud_net + '.' if out['x_lr_adult'] else '')
    # (round f4276e76, the author: 'UD' -> ', further imporving childhood consumption', 'taxes' -> 'taxes paid by
    # working-age households', 'and' -> 'period. Lastly, even drug users benefit from the lower equilibrium drug
    # price (is that correct?)': correct as a channel, the price is 14 percent lower; whether a user is better off
    # on net is the separate question of the SUD row)
    # the introduction's account of the newborn's gain, consistent with 6.2's (round c88b1dda, the author: "make
    # sure that the explanations in intro ... are consistent with the results we have")
    out['x_intro_adult_rest'] = (', and the rest through adult life being worth more at the same productivity, chiefly '
                                 'because a voucher is easier to get' if out['x_lr_adult'] else '')
    # APPROVAL IN THE TEXT (round c88b1dda, the author: "also where are the results on approvals?")
    _y = D[t]['y26_better']
    out['x_lr_approve'] = (
        ('Every household that enters adult life at 26 is better off under Treatment First than it would be in '
         'the same state under Housing First' if _y > 99.95 else
         # (14 October) a share that rounds to 100 but is not all of them
         # (round r324, the author on 'Nearly': "why nearly? isnt it 100%?": it is 99.9, which the table rounds to 100)
         f'Of the households that enter adult life at 26, ${_y:.1f}$ percent are better off under Treatment First than '
         'they would be in the same state under Housing First' if _y >= 99.5 else
         f'Of the households that enter adult life at 26, ${_y:.0f}$ percent are better off under Treatment First '
         'than they would be in the same state under Housing First')
        + ' (Table~\\ref{tab:longrun}).')
    # the newborns, by the household they are born into (newborn_better(); the Table 7 row of the same name)
    _nb = newborn_better()
    # the same share as a number, for the transition's sentence on households entering at 26 (review item 9, 7 Oct)
    if _nb is not None:
        out['x_lr_nb_better_pc'] = f'{_nb:.0f}'
    _nb = None                                   # (11 October) the newborn shares are at childhood weight one; see the row's note
    out['x_lr_approve_nb'] = (
        '' if _nb is None else
        'So is every newborn, compared with itself born into the same household under Housing First.'
        if _nb > 99.95 else
        f'Of newborns (including childhood), ${_nb:.0f}$ percent are better off under Treatment First than they would be if born into the '
        'same household under Housing First.')
    # a pending column's names: yellow, never a number (its rule-A stand-in only kept the code running)
    for _a in PENDING:
        for _k in list(out):
            if _k.startswith(_PENDING_NAMES[_a]):
                out[_k] = '\\mbox{\\tocheck{--}}'
    if PENDING:
        print('PENDING (yellow):', ', '.join(sorted(PENDING)))
    d = json.load(open(OUT_JSON))
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    print(f'wrote {TAB} and {len(out)} x_lr_* names')
    for k, v in sorted(out.items()):
        print(f'  {k} = {v}')


if __name__ == '__main__':
    main()
