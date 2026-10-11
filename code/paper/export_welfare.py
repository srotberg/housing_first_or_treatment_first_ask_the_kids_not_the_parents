#!/usr/bin/env python3
"""WHERE THE NEWBORN'S GAIN COMES FROM (10-11 October). The review: the externality is partly built into the newborn
criterion, which counts a child's childhood at full weight and its parent's loss only through the child's own
future. The author: "can't you just compute the welfare with equal weights on the child and parent ... and that is
the externality?", "isolate the adult lifetime utility in both", "the externality in each period of life",
"give it in percent", "a table that more clearly breaks the gains into childhood externality and earnings
externality, and adult gain on its own", and the child's childhood counted at xi - 1 (welfare_nok.py).

For each Treatment First column of Table tab:longrun against Housing First, in points of the newborn's lifetime
consumption (welfare_nok.parts): the newborn's gain, and its four parts, which sum to it:
  childhood its parent does not count   (1 - omega_c) of the change in the child's childhood flow at xi - 1
  better productivity at entry          E: hold the policy, change who enters adult life (the earnings externality)
  its own adult life under the policy   beta^J_K P: hold who enters, change the policy; the parent's gain, discounted
  childhood its parent does count       omega_c of the childhood change
plus the parent's own gain P as a percent of ITS lifetime consumption (the adult curve), and the externality's share.
Also the largest change the kappa_x term would make (footnote 4).
Writes x_wd_* into results_numbers.json and writing/tables/tab_whogains.tex (tab_welfare.tex is the stylized
model's, code/stylized/welfare.py).
usage: python3 code/paper/export_welfare.py
"""
import json
import os

import welfare_nok as wn

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
TAB = os.path.join(ROOT, 'writing', 'tables', 'tab_whogains.tex')

R = lambda *p: os.path.join(ROOT, 'results', *p)
# the paper's arms (welfare) and the same economies' by-node values at 26 (the transition's re-solved arms and the
# decomposition arms, which carry value_at_26_by_node.txt; the re-solves agree with the accepted runs to 1e-5)
ARMS = {'b': (R('decomp_2c_both', 'arm_fixboth'), R('decomp_2c_both', 'arm_fixboth')),
        'p': (R('decomp_2c', 'arm_fixp'), R('decomp_2c', 'arm_fixp')),
        'tf': (R('counterfactuals_2c', 'tf85_c35', 'tf'), R('transition_2c', 'arm_tf'))}
BASE = (R('counterfactuals_2c', 'nulltf', 'null'), R('transition_2c', 'arm_null'))


def share_word(pc):
    """a share of the gain in words, for the prose (two decimals never, the author's rule on numbers in text)"""
    if pc > 105:
        return 'more than all of it'
    if pc > 95:
        return 'all of it'
    if pc >= 85:
        return 'nine tenths of it'
    if pc >= 70:
        return 'three quarters of it'
    if pc >= 60:
        return 'two thirds of it'
    if pc >= 45:
        return 'about half of it'
    if pc >= 28:
        return 'a third of it'
    if pc >= 20:
        return 'a quarter of it'
    return f'{pc:.0f} percent of it'


def main():
    out = {}
    rows = {a: wn.parts(dw, dn, BASE[0], BASE[1]) for a, (dw, dn) in ARMS.items()}
    f2 = lambda x: f"{x:.2f}"
    for a, r in rows.items():
        p = r['pts']
        for k in ('tot', 'extc', 'E', 'own', 'cnt', 'ext', 'P'):
            out[f'x_wd_{k}_{a}'] = f2(p[k])
            out[f'x_wd_{k}abs_{a}'] = f2(abs(p[k]))
        out[f'x_wd_extsh_{a}'] = f"{p['ext_share']:.0f}"
        out[f'x_wd_extsh_word_{a}'] = share_word(p['ext_share'])
        out[f'x_wd_nonext_word_{a}'] = share_word(100 - p['ext_share']) if p['ext_share'] < 100 else 'none of it'
        out[f'x_wd_child_pc_{a}'] = f"{p['child_share']:.0f}"
        out[f'x_wd_child_word_{a}'] = share_word(p['child_share'])
        # capitalised, for a sentence start
        out[f'x_wd_extsh_Word_{a}'] = share_word(p['ext_share'])[0].upper() + share_word(p['ext_share'])[1:]
        out[f'x_wd_child_Word_{a}'] = share_word(p['child_share'])[0].upper() + share_word(p['child_share'])[1:]
        out[f'x_wd_own_dir_{a}'] = 'gain' if p['own'] > 0 else 'loss'
        out[f'x_wd_P_dir_{a}'] = 'gains' if p['P'] > 0 else 'loses'
        out[f'x_wd_worse_{a}'] = ("every parent's own value falls" if r['worse'] > 99.5 else
                                 "every parent's own value rises" if r['worse'] < 0.5 else
                                 f"the own value of {r['worse']:.0f} percent of parents falls")
        # the lifetime value in utils, for the record
        out[f'_wd_utils_{a}'] = {k: round(r[k], 4) for k in ('C', 'Cw', 'A', 'P', 'Aown', 'E', 'nb', 'eq', 'extc', 'cnt')}
    assert rows['tf']['pts']['tot'] > 0 and rows['tf']['pts']['P'] > 0, 'the main experiment no longer favours Treatment First'
    out['x_wd_omega_pc'] = f"{100 * wn.OMEGA_C:.1f}"                  # the share of the child's flow the parent counts
    out['x_wd_ext_pc'] = f"{100 * (1 - wn.OMEGA_C):.0f}"              # and the share it leaves out
    out['x_wd_child_weight'] = f"{wn.CHILD_WEIGHT:.2f}"
    # the externality's childhood part against its adult part, in words that turn with the numbers
    out['x_wd_ext_bigger'] = ('the childhood part is the larger in every column'
                              if all(r['pts']['extc'] > r['pts']['E'] for r in rows.values()) else
                              'the adult part is the larger in every column'
                              if all(r['pts']['extc'] < r['pts']['E'] for r in rows.values()) else
                              'which part is the larger differs across the columns')
    # the largest change the kappa_x term would make to a long-run gain, at the paper's weight
    cev0 = wn.cev_free(BASE[0])
    cev0t = wn.cev_at(BASE[0], wn.CHILD_WEIGHT, with_term=True)
    out['x_wd_kx_max'] = f2(max(abs((wn.cev_free(dw) - cev0) - (wn.cev_at(dw, wn.CHILD_WEIGHT, with_term=True) - cev0t))
                                for dw, _ in ARMS.values()))
    # the table, in points (black: the prose carries the reading)
    s = lambda x: f"{x:.2f}".replace('-', '$-$')
    row = lambda lab, k: f"{lab} & {s(rows['b']['pts'][k])} & {s(rows['p']['pts'][k])} & {s(rows['tf']['pts'][k])} \\\\"
    L = [r'\begin{table}[!htb]\centering',
         r"\caption{Where the newborn's gain comes from}\label{tab:whogains}",
         r'\begingroup\small',
         r'\sbox{\ntbox}{\begin{tabular}{@{}lccc@{}}', r'\toprule',
         r' & both held & $\pi_V$ clears & both clear \\', r'\midrule',
         row(r"The newborn's gain $\Delta W$, percent of lifetime consumption", 'tot'),
         row(r"\quad Childhood its parent does not count, $(1-\omega_c)\Delta C$", 'extc'),
         row(r"\quad Better productivity at entry, $E$", 'E'),
         row(r"\quad The newborn's own adult life under the policy, $\beta^{J_K}\Delta P$", 'own'),
         row(r"\quad Childhood its parent does count, $\omega_c\Delta C$", 'cnt'),
         r'\midrule',
         f"The externality, the first two parts, percent of the gain & {rows['b']['pts']['ext_share']:.0f} & "
         f"{rows['p']['pts']['ext_share']:.0f} & {rows['tf']['pts']['ext_share']:.0f} \\\\",
         row(r"The parent's own gain $\Delta P$, percent of the parent's lifetime consumption", 'P'),
         r'\bottomrule', r'\end{tabular}}', r'\usebox{\ntbox}',
         r"\tabnote{Notes: Treatment First against Housing First in the long run; the columns are the fifth, sixth "
         r"and seventh of Table~\ref{tab:longrun}. The first row is the CEV of~\eqref{eq:cev}. The four rows under it "
         r"sum to it: each is read off the benchmark's welfare curve after the ones above it. Childhood is the change "
         r"in the child's flow at its weight $\xi-1$, split into the share $\omega_c$ its parent counts and the share "
         r"$1-\omega_c$ it does not. Better productivity at entry holds the policy and changes only who enters adult life; "
         r"the newborn's own adult life holds who enters and changes only the policy, and equals the parent's own gain "
         r"discounted to the child's birth. The parent's own gain is the change in its value at $j=1$ when the policy "
         r"switches from Housing First to Treatment First, with the distribution of entrants held at Housing First's, "
         r"for the households Housing First's newborns are born into, as a percent of the parent's own "
         r"lifetime consumption, undiscounted. It is larger than the newborn's own adult life because the newborn "
         r"receives the same gain $J_K$ years later, discounted, and because a percent of a newborn's lifetime "
         r"consumption, most of which is itself far off, is a smaller sum than a percent of an adult's.}",
         r'\endgroup', r'\end{table}']
    open(TAB, 'w').write('\n'.join(L) + '\n')
    d = json.load(open(OUT_JSON))
    # THE PRICE RESPONSE UNDER THE SCREEN in percentage points of households, against what the benchmark's
    # participation elasticity (export_elasticity.py) gives for the same price fall (the review's elasticity point;
    # the price-only footnote of Section 6.2)
    pp_s = d['_dcpv_b1_raw'] - d['_dcb_b1_raw']
    pp_b = float(d['x_b0']) * abs(float(d['x_el_part'])) * d['_dcpv_price_fall']
    out['x_tf_arc_pp'] = f"{pp_s:.1f}"
    out['x_bench_arc_pp'] = f"{pp_b:.1f}"
    _r = pp_s / pp_b
    out['x_tf_arc_pp_vs'] = ('about the same as' if 0.8 <= _r < 1.25 else 'half again' if 1.25 <= _r < 1.7 else 'about twice'
                             if 1.7 <= _r < 2.4 else 'about three times' if 2.4 <= _r < 3.5 else f'{_r:.1f} times')
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    print(f'export_welfare: {len(out)} names; table -> {TAB}')
    for a in ('b', 'p', 'tf'):
        p = rows[a]['pts']
        print(f"  {a:3s} total {p['tot']:6.2f} = childhood ext {p['extc']:+.2f} + earnings ext {p['E']:+.2f} + own adult "
              f"{p['own']:+.2f} + counted {p['cnt']:+.2f} | externality {p['ext_share']:.0f}% | parent's own {p['P']:+.2f}% "
              f"| childhood {p['child_share']:.0f}% | {out[f'x_wd_worse_{a}']}")
    print('  kappa_x max', out['x_wd_kx_max'], '; omega_c', out['x_wd_omega_pc'], 'percent counted')


if __name__ == '__main__':
    main()
