#!/usr/bin/env python3
"""THE delta_h TEST, FOR THE SECTION 2 FOOTNOTE (11 October; the author, 10 October: "Set deltad to 0 and replace it
instead with a two class model with deltah=0.31 that is a penalty for homelessness throughout childhood instead ...
Run the benchmark with all the parameters fixed but with deltad=0 and deltah=0.31. And then simulate the tf long run
in full ge with piv and pv adjusting", and 11 October: "put the deltah result as a footnote in section 2").

Reads results/deltah (code/deltah/remote_deltah.sh): the delta_h benchmark, its no-policy arm and its Treatment First
arm (detection 0.85, the $35 test, pi_V and the drug price clearing on the no-policy arm's net revenue), and the paper's
own two arms for the comparison. The newborn CEV is read the paper's way (round r293): childhood at xi - 1, without the
kappa_x term, off the delta_h benchmark's own welfare curve (welfare_nok.Bench with the curve file's path, since
results/deltah keeps it at the top level). Writes x_dh_* into results_numbers.json; direction words turn with the sign.
usage: python3 code/paper/export_deltah.py      (run by hand after export_results.py, like export_welfare.py)
"""
import gzip
import json
import os
import re

import welfare_nok as wn

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
R = lambda *p: os.path.join(ROOT, 'results', *p)
DH = R('deltah')
ARMS = {'null': (R('deltah', 'null'), R('counterfactuals_2c', 'nulltf', 'null')),
        'tf': (R('deltah', 'tf'), R('counterfactuals_2c', 'tf85_c35', 'tf'))}


def lv(p):
    """the arm's own values in finalstats.py's final.txt (the first number after the label)"""
    out = {}
    for l in open(p):
        m = re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l)
        if m:
            out[m.group(1).strip()] = float(m.group(2))
    return out


def avg_income(d):
    """the last 'avg labour income' the arm's log prints (its final statistics block)"""
    v = None
    for l in gzip.open(os.path.join(d, 'cf.log.gz'), 'rt', errors='replace'):
        if 'aleph denominator, avg labour income' in l:
            v = float(l.split('=')[-1])
    assert v is not None, d
    return v


def handover(d, key):
    for l in open(os.path.join(d, 'PARAM_HANDOVER.arm.txt')):
        if l.startswith(key + ' '):
            return float(l.split()[1])
    raise KeyError(key)


def main():
    out = {}
    f = {a: (lv(os.path.join(dh, 'final.txt')), lv(os.path.join(mn, 'final.txt'))) for a, (dh, mn) in ARMS.items()}
    dh_null, mn_null = f['null']
    dh_tf, mn_tf = f['tf']
    pc = lambda x, y: 100 * (x / y - 1)
    # the two changes, from the file the run read
    dd = handover(ARMS['tf'][0], 'penalty_child_addicted')
    dhv = handover(ARMS['tf'][0], 'penalty_child_homeless')
    assert dd == 0 and 0 < dhv < 1, (dd, dhv)
    out['x_dh_dh_pc'] = f'{100 * dhv:.0f}'
    # the welfare numbers, the paper's way, off this economy's own curve
    B = wn.Bench(DH, curve=os.path.join(DH, 'welfare_curvebaseline_benchmark.dat.gz'))
    cev = {a: wn.cev_free(dh, bench=B) for a, (dh, _) in ARMS.items()}
    v = {a: wn.arm_values(dh) for a, (dh, _) in ARMS.items()}
    comp = {a: wn.components_free(v[a], B) for a in ARMS}            # (childhood at one, adult), without the term
    ws = B.lifetime_curve(weight=wn.CHILD_WEIGHT, with_term=False)
    w = wn.CHILD_WEIGHT
    # cev_of returns the fraction; the paper's numbers are in percent
    tot = 100 * (B.cev_of(w * comp['tf'][0] + comp['tf'][1], ws) - B.cev_of(w * comp['null'][0] + comp['null'][1], ws))
    child = 100 * (B.cev_of(w * comp['tf'][0] + comp['null'][1], ws) - B.cev_of(w * comp['null'][0] + comp['null'][1], ws))
    adult = tot - child
    assert abs(tot - (cev['tf'] - cev['null'])) < 1e-6, (tot, cev)
    g = cev['tf']                                                    # against the benchmark, as x_tf_cev is
    out['x_dh_cev'] = f'{g:.2f}'
    out['x_dh_cev_abs'] = f'{abs(g):.2f}'
    out['x_dh_dir'] = 'lowers' if g < 0 else 'raises'
    out['x_dh_sign_word'] = 'a loss' if g < 0 else 'a gain'
    out['x_dh_child_pts'] = f'{child:.2f}'
    out['x_dh_adult_pts'] = f'{adult:.2f}'
    out['x_dh_parts_clause'] = ('both the childhood and the adult part of a newborn\'s value fall' if child < 0 and adult < 0 else
                                'the childhood part of a newborn\'s value falls while the adult part rises' if child < 0 else
                                'the adult part of a newborn\'s value falls while the childhood part rises' if adult < 0 else
                                'both parts of a newborn\'s value rise')
    out['_dh_cev_fortran'] = v['tf']['cev_logged']
    out['_dh_cev_null'] = round(cev['null'], 4)
    # the long run against Housing First in the same economy, and the paper's arm beside it
    k = {'b': 'drug use b', 'sud': 'SUD lambda_d', 'h': 'homelessness h_1', 'pv': 'pi_V (voucher probability)',
         'vs': 'voucher spending', 'p': 'drug price'}
    for n, lab in k.items():
        out[f'x_dh_{n}_chg'] = f"{pc(dh_tf[lab], dh_null[lab]):.1f}"
        out[f'x_dh_{n}_pc'] = f"{abs(pc(dh_tf[lab], dh_null[lab])):.0f}"
        out[f'_dh_main_{n}_chg'] = round(pc(mn_tf[lab], mn_null[lab]), 2)
    out['x_dh_h_dir'] = 'rises' if dh_tf[k['h']] > dh_null[k['h']] else 'falls'
    out['x_dh_vs_dir'] = 'falls' if dh_tf[k['vs']] < dh_null[k['vs']] else 'rises'
    out['x_dh_price'] = f"{dh_tf[k['p']]:.2f}"
    # earnings: average labour income under each arm, from the logs
    inc = {a: (avg_income(dh), avg_income(mn)) for a, (dh, mn) in ARMS.items()}
    dh_inc, mn_inc = pc(inc['tf'][0], inc['null'][0]), pc(inc['tf'][1], inc['null'][1])
    out['x_dh_inc_pc'] = f'{abs(dh_inc):.1f}'
    out['x_dh_main_inc_pc'] = f'{abs(mn_inc):.1f}'
    word = lambda x: 'falls' if x < 0 else 'rises'
    wordg = lambda x: 'falling' if x < 0 else 'rising'
    out['x_dh_inc_clause'] = (f"{word(dh_inc)} by ${abs(dh_inc):.1f}$ percent instead of {wordg(mn_inc)} by ${abs(mn_inc):.1f}$"
                              if (dh_inc < 0) != (mn_inc < 0) else f"{word(dh_inc)} by ${abs(dh_inc):.1f}$ percent against ${abs(mn_inc):.1f}$")
    out['x_dh_main_vs_pc'] = f"{abs(pc(mn_tf[k['vs']], mn_null[k['vs']])):.0f}"
    # the benchmark it was solved against, for the record (not recalibrated: every parameter fixed)
    for l in gzip.open(os.path.join(DH, 'bench.log.gz'), 'rt', errors='replace'):
        m = re.search(r'INVARIANT PASS\s+(drug users|disorder rate|homelessness rate)\s+=\s+(\S+)', l)
        if m:
            out[{'drug users': '_dh_bench_users', 'disorder rate': '_dh_bench_sud', 'homelessness rate': '_dh_bench_h'}[m.group(1)]] = float(m.group(2))
    d = json.load(open(OUT_JSON))
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    print(f'export_deltah: {len(out)} names')
    print(f"  delta_h {out['x_dh_dh_pc']} percent, delta_d 0: newborn CEV {g:+.2f} (null {cev['null']:+.3f}; Fortran {v['tf']['cev_logged']:+.2f}) "
          f"= childhood {child:+.2f} + adult {adult:+.2f} | drug use {out['x_dh_b_chg']}% SUD {out['x_dh_sud_chg']}% h_1 {out['x_dh_h_chg']}% "
          f"pi_V {out['x_dh_pv_chg']}% (paper {out['_dh_main_pv_chg']}) voucher spending {out['x_dh_vs_chg']}% (paper {out['_dh_main_vs_chg']}) "
          f"income {dh_inc:+.2f}% (paper {mn_inc:+.2f}) price {out['x_dh_price']}")


if __name__ == '__main__':
    main()
