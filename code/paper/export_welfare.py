#!/usr/bin/env python3
"""WHO GAINS, WHO PAYS, AND THE EXTERNALITY (10 October). The review: the externality is partly built into the newborn
criterion, which counts a child's childhood at full weight and its parent's loss only as the newborn's own future loss
behind beta^J_K. The author: "can't you just compute the welfare with equal weights on the child and parent and
average them out and compare those to the benchmark when you measure welfare the same way, and that is the
externality?", "you can then also isolate the adult lifetime utility in both", "which then isolates the size of the
externality in each period of life (childhood and adulthood)", "and the rest I suppose is just timing?", "drop that
column [the price-only run] and write it all into the paper in red".

For each Treatment First arm against the re-solved Housing First arm, on the benchmark's households, in utils of the
newborn's lifetime object and without the kappa_x * H term (welfare_nok.py):
  C   the child's childhood: the first term of the newborn's welfare, each arm's own, as the Fortran prints it
  A   the child's adult life: beta^J_K times the entrants' average value at 26, each arm's own entrants
  P   the parent's own lifetime value: the value at 26 by entry node under each policy (value_at_26_by_node.txt,
      nodes 1-13 with a clean parent, 14-26 penalised) weighted by the Housing First newborns' masses on those nodes
      (results/transition_2c/newborn/shares.txt), so the same households are valued under both policies. It is the
      value function as solved, so it carries omega_c times the child terms.
Because the entrants' value at 26 is the same function in A and in P, A splits exactly:
  A = beta^J_K [ sum_s m_HF(s) (V_TF(s) - V_HF(s)) + sum_s (m_TF(s) - m_HF(s)) V_TF(s) ] = beta^J_K P + E,
beta^J_K P being the child's own gain from living under the policy as an adult, the gain its parent has, discounted
to the child's birth, and E the gain from entering adult life on a better node: the earnings externality.
Three verdicts: the household's own, P; the newborn's, C + A; equal weights on the parent and the child, P + C + A.
The externality: (1 - omega_c (xi - 1)) C in childhood, E in adult life (the parent counts omega_c of the penalty
charge D, which the Fortran does not print and which is small because omega_c is).
Also: the orphan convention (stage E2's newborn run, results/transition_2c/newborn/shares.json: W sends the child
into adult life at the parent's death as the law of motion does, Wnd lets it finish childhood as Section 6.1 does),
and the largest change any long-run CEV makes when the kappa_x term is removed (footnote 4).
Writes x_wd_* into results_numbers.json and writing/tables/tab_whogains.tex (tab_welfare.tex is the stylized
model's, code/stylized/welfare.py).
usage: python3 code/paper/export_welfare.py
"""
import json
import os
import re

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
COUNTED = wn.OMEGA_C * (wn.XI - 1)            # the parent's weight on the child's flow, against the child's own 1
B25 = wn.BETA ** wn.CHILD_YEARS


def words_worse(pc):
    if pc > 99.5:
        return "every household's own value falls"
    if pc < 0.5:
        return "every household's own value rises"
    return f"the own value of {pc:.0f} percent of households falls"


def main():
    out = {}
    vb = wn.arm_values(BASE[0])
    cev0 = wn.cev_free(BASE[0])
    rows = {}
    for a, (dw, dn) in ARMS.items():
        r = wn.parts(dw, dn, BASE[0], BASE[1])
        r.update(own=r['P'], extc=(1 - COUNTED) * r['C'], exta=r['E'], cev=wn.cev_free(dw) - cev0,
                 cev_with=wn.cev_with(dw) - wn.cev_with(BASE[0]))
        rows[a] = r
        P = r['P']
        r['ext'] = r['extc'] + r['exta']
        r['ext_share'] = 100 * r['ext'] / r['nb']
        for k in ('C', 'A', 'Aown', 'E', 'P', 'eq', 'nb', 'extc', 'exta', 'ext'):
            out[f'x_wd_{k}_{a}'] = f"{r[k]:.2f}"
        out[f'x_wd_Pabs_{a}'] = f"{abs(P):.2f}"
        out[f'x_wd_cev_{a}'] = f"{r['cev']:.2f}"
        out[f'x_wd_ext_share_{a}'] = f"{r['ext_share']:.0f}"
        out[f'x_wd_worse_{a}'] = words_worse(r['worse'])
        out[f'x_wd_P_dir_{a}'] = 'loses' if P < 0 else 'gains'
        out[f'x_wd_eq_dir_{a}'] = 'falls' if r['eq'] < 0 else 'rises'
    assert rows['tf']['eq'] > 0 and rows['tf']['P'] > 0 and rows['b']['eq'] > 0, 'the verdicts no longer agree'
    out['x_wd_pc'] = f"{100 * COUNTED:.1f}"                       # the parent's weight on the child's flow, per cent
    out['x_wd_ext_pc'] = f"{100 * (1 - COUNTED):.0f}"            # what it leaves out
    out['x_wd_b25'] = f"{B25:.2f}"
    # utils per percent of lifetime consumption, from the main experiment
    out['x_wd_unit'] = f"{rows['tf']['nb'] / rows['tf']['cev']:.2f}"
    # the orphan convention: W sends the child into adult life at the parent's death; Wnd lets it finish childhood
    s = json.load(open(R('transition_2c', 'newborn', 'shares.json')))
    gW = s['W']['avg_W_tf_own_weights'] - s['W']['avg_W_hf']
    gWnd = s['Wnd']['avg_W_tf_own_weights'] - s['Wnd']['avg_W_hf']
    assert abs(gWnd - rows['tf']['nb']) < 0.02, (gWnd, rows['tf']['nb'])
    Wb = vb['W'] + wn.term(vb)
    out['x_wd_orphan_cev'] = f"{100 * (wn.cev_of(Wb + gW, wn.WS_FREE) - wn.cev_of(Wb, wn.WS_FREE)):.2f}"
    out['_wd_orphan_gains_utils'] = f"W {gW:.4f}  Wnd {gWnd:.4f}  (Wnd reproduces the newborn criterion's {rows['tf']['nb']:.4f})"
    # the largest change the kappa_x term makes to a long-run gain, over the arms in the table
    out['x_wd_kx_max'] = f"{max(abs(r['cev'] - r['cev_with']) for r in rows.values()):.2f}"
    # the table (black: a table change goes in the prose and the \why note)
    f = lambda x: f"{x:+.2f}".replace('-', '$-$').replace('+', '')
    row = lambda lab, k: f"{lab} & {f(rows['b'][k])} & {f(rows['p'][k])} & {f(rows['tf'][k])} \\\\"
    L = [r'\begin{table}[!tb]\centering\small',
         r"\caption{The newborn's gain, who pays for it, and the externality}\label{tab:whogains}",
         r'\begin{tabular}{@{}lccc@{}}', r'\toprule',
         r' & both held & $\pi_V$ clears & both clear \\', r'\midrule',
         r'\multicolumn{4}{@{}l}{\emph{The three parts, in lifetime utility}} \\',
         row(r"Child's childhood, $C$", 'C'),
         row(r"Child's adult life, $A$", 'A'),
         row(r"\quad living under Treatment First as an adult, $\beta^{J_K}P$", 'Aown'),
         row(r"\quad starting adult life more productive, $E=A-\beta^{J_K}P$", 'E'),
         row(r"Parent's own lifetime value, $P$", 'P'),
         r'\midrule', r'\multicolumn{4}{@{}l}{\emph{Three verdicts}} \\',
         row(r"The household's own, $P$", 'own'),
         row(r"The newborn's, $C+A$", 'nb'),
         f"\\quad as a CEV, percent of lifetime consumption & {rows['b']['cev']:.2f} & {rows['p']['cev']:.2f} & {rows['tf']['cev']:.2f} \\\\",
         row(r"Equal weights on parent and child, $P+C+A$", 'eq'),
         r'\midrule', r'\multicolumn{4}{@{}l}{\emph{The externality}} \\',
         row(r"In childhood, $(1-\omega_c(\xi-1))\,C$", 'extc'),
         row(r"In adult life, $E$", 'exta'),
         f"\\quad share of the newborn's gain, percent & {rows['b']['ext_share']:.0f} & {rows['p']['ext_share']:.0f} & {rows['tf']['ext_share']:.0f} \\\\",
         r'\bottomrule', r'\end{tabular}', r'\begin{minipage}{0.97\textwidth}\footnotesize\vspace{2pt}',
         f"Notes: Treatment First against Housing First in the long run, in utils of a newborn's lifetime value, "
         f"without the homelessness disamenity of footnote~\\ref{{fn:kappax}}; {out['x_wd_unit']} utils are about one "
         r"percent of lifetime consumption. The columns are the fifth, sixth and seventh columns of "
         r"Table~\ref{tab:longrun}. $C$ and $A$ are the two terms of~\eqref{eq:newbornw}, each policy's own. $P$ "
         r"is the value at 26 of~\eqref{eq:fbellman} by entry node under each policy, weighted by the Housing First "
         r"entrants, so the same households are valued under both; it carries the child terms at the parent's "
         r"weight $\omega_c$. $A$ splits exactly into $\beta^{J_K}P$, the child's own gain from living under the "
         r"policy as an adult, and $E$, its gain from entering adult life on a better productivity node. The "
         r"parent counts $\omega_c(\xi-1)$ of its child's flow and $\omega_c$ of the charge $D$, so the externality "
         r"is the rest of $C$ and, up to that charge, $E$.",
         r'\end{minipage}', r'\end{table}']
    open(TAB, 'w').write('\n'.join(L) + '\n')
    d = json.load(open(OUT_JSON))
    # the childhood part of the externality against the adult part, in words that turn with the numbers
    out['x_wd_ext_bigger'] = ('the childhood part is the larger in every column' if all(r['extc'] > r['exta'] for r in rows.values())
                              else 'the adult part is the larger in every column' if all(r['extc'] < r['exta'] for r in rows.values())
                              else 'which part is the larger differs across the columns')
    out['x_wd_P_p_vs_tf'] = 'falls to' if rows['tf']['P'] < rows['p']['P'] else 'rises to'
    # THE PRICE RESPONSE UNDER THE SCREEN in percentage points of households, against what the benchmark's
    # participation elasticity (export_elasticity.py) gives for the same price fall (the review's elasticity point)
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
        r = rows[a]
        print(f"  {a:3s} C {r['C']:+.3f} A {r['A']:+.3f} (= b25 P {r['Aown']:+.3f} + E {r['E']:+.3f}) P {r['P']:+.3f} | "
              f"own {r['own']:+.3f} nb {r['nb']:+.3f} (CEV {r['cev']:.2f}; with kappa_x {r['cev_with']:.2f}) eq {r['eq']:+.3f} | "
              f"ext {r['extc']:+.3f} {r['exta']:+.3f} = {r['ext_share']:.0f}% of nb | {words_worse(r['worse'])}")
    print('  orphan:', out['_wd_orphan_gains_utils'], '-> CEV', out['x_wd_orphan_cev'], '; kappa_x max', out['x_wd_kx_max'],
          '; unit', out['x_wd_unit'], 'utils per percent')


if __name__ == '__main__':
    main()
