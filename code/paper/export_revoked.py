"""
The households whose voucher Treatment First revokes, against the same households had they kept it: the x_rv_* names
of the Validation section's comparison with Costantini (2025) (round r142; the author, 4 October: "add the constantini
stuff to the validation, in its own paragraph with explanations").

usage: python3 code/paper/export_revoked.py   -> x_rv_* merged into code/paper/results_numbers.json

Reads the two T = 10 paths of the revoked-voucher experiment (code/revoked_2c, results/revoked_2c): Treatment First
switched on with the drug price and pi_V held at the no-policy values, and the same machinery with Housing First at both
ends. Their REVK GROUP lines follow, for each tagged group, the same households under each kernel: groups 1-3 are the
holders whose voucher is revoked in years 1, 2 and 3; each line carries the starting mass, the cumulative deaths and,
AMONG THE SURVIVORS, the shares with a SUD and homeless, and their mean model age (model age 1 is age 26).

The pooled numbers weight each cohort by its mass at revocation and read each one the same number of years after its
own revocation.
"""
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
# RULE C (14 October): the rule-C revocation paths when both have landed; until then rule A's, and export_all_C.sh
# prints every x_rv_* name yellow (PENDING_C below)
_RC = os.path.join(ROOT, 'results', 'revoked_2c_C')
PENDING_C = not all(os.path.exists(os.path.join(_RC, f)) for f in ('tf10_run.log.gz', 'hf10_run.log.gz'))
RES = os.path.join(ROOT, 'results', 'revoked_2c') if PENDING_C else _RC
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
GROUPS = (1, 2, 3)            # revoked in year 1, 2, 3
AGE0 = 25                     # model age 1 is age 26

# Costantini, S. (2025), "Housing First or Treatment First? Evidence from the VA's homelessness programs", abstract:
# "nearly 300,000 unhoused, mentally ill Veterans"; enrolling in Housing First "reduces three-year mortality by 4.6
# percentage points relative to a no-program counterfactual" (related_lit/Costantini_2025_...pdf, page 1)
COSTANTINI_PP = '4.6'
COSTANTINI_N = '300{,}000'


def groups(f):
    G = {}
    for line in gzip.open(os.path.join(RES, f), 'rt', errors='replace'):
        if line.startswith(' REVK GROUP'):
            d = {k: float(v) for k, v in re.findall(r'(\w+)=\s*(\S+)', line)}
            G[(int(d['g']), int(d['t']))] = d
    return G


def pooled(G, years, key):
    """mass-weighted over the revoked cohorts, `years` after each one's revocation: deaths as a share of the mass at
    revocation, other keys as the survivors' share (weighted by survivors)"""
    if key == 'dead':
        num = sum(G[(g, g + years)]['cum_deaths_h'] + G[(g, g + years)]['cum_deaths_e'] for g in GROUPS)
        return num / sum(G[(g, g)]['mass0'] for g in GROUPS)
    w = [G[(g, g + years)]['alive'] for g in GROUPS]
    return sum(G[(g, g + years)][key] * x for g, x in zip(GROUPS, w)) / sum(w)


STREET = os.path.join(ROOT, 'results', 'revoked_2c_street_C', 'tables.md')   # rule C (14 October)
PENDING_STREET = not os.path.exists(STREET)
if PENDING_STREET:
    STREET = os.path.join(ROOT, 'results', 'revoked_2c_street', 'tables.md')


def street_smi():
    """THE COMPARISON THE PAPER USES (the author, 5 October: "condition on SMI for both voucher holder and those revoked,
    and then compare those who ended up on the street whose voucher was revoked", "that is exactly the constantini
    paper"): results/revoked_2c_street, the revoked split by SMI at revocation and by whether Treatment First's first
    housing choice after the revocation is the street, each followed under both kernels. The pooled row 'SMI, on the
    street' of tables.md: mass share, three-year deaths under (a) and (b), and their DIRECT gap, no Wald rescaling.
    Refuses unless the worker's guard summary passed."""
    T = open(STREET).read()
    assert 'GUARD SUMMARY: PASS' in T, 'the street split did not pass its guards'
    sec = T.split('## pooled, years 1-3')[1].split('## ')[0]
    row = [l for l in sec.splitlines() if l.startswith('| SMI, on the street |')][0]
    c = [x.strip() for x in row.strip('|').split('|')]
    return dict(share=float(c[2]), dead_a=float(c[5]), dead_b=float(c[6]), gap=float(c[7]))


def main():
    tf, hf = groups('tf10_run.log.gz'), groups('hf10_run.log.gz')
    assert all((g, g) in tf and (g, g + 3) in tf and (g, g + 3) in hf for g in GROUPS), 'missing REVK GROUP lines'
    # the same households: identical at revocation under both kernels
    for g in GROUPS:
        assert abs(tf[(g, g)]['mass0'] / hf[(g, g)]['mass0'] - 1) < 1e-10, g
    d3t, d3h = pooled(tf, 3, 'dead'), pooled(hf, 3, 'dead')
    d6t, d6h = pooled(tf, 6, 'dead'), pooled(hf, 6, 'dead')
    hl = [pooled(tf, y, 'homeless') - pooled(hf, y, 'homeless') for y in (1, 2, 3)]
    tl = [pooled(tf, y, 'homeless') for y in (1, 2, 3)]
    gap = d3t - d3h
    out = {
        'x_rv_costantini_pp': COSTANTINI_PP,
        'x_rv_costantini_n': COSTANTINI_N,
        'x_rv_age': f"{pooled(tf, 0, 'mean_age') + AGE0:.0f}",
        'x_rv_sud0': f"{100 * pooled(tf, 0, 'sud'):.0f}",
        'x_rv_dead_tf': f'{100 * d3t:.2f}',
        'x_rv_dead_hf': f'{100 * d3h:.2f}',
        'x_rv_gap_pp': f'{100 * gap:.2f}',
        'x_rv_gap_rel': f'{100 * (d3t / d3h - 1):.0f}',
        'x_rv_gap6_pp': f'{100 * (d6t - d6h):.2f}',
        'x_rv_hl_lo': f'{100 * min(tl):.0f}',
        'x_rv_hl_hi': f'{100 * max(tl):.0f}',
        'x_rv_sud_tf3': f"{100 * pooled(tf, 3, 'sud'):.1f}",
        'x_rv_sud_hf3': f"{100 * pooled(hf, 3, 'sud'):.1f}",
        # the gap per household the revocation puts on the street: the three-year mortality gap over the average
        # rise in the survivors' homelessness across the three years (a Wald-style rescaling, not a model output)
        'x_rv_wald_pp': f'{100 * gap / (sum(hl) / len(hl)):.1f}',
    }
    st = street_smi()
    assert abs(st['dead_a'] - st['dead_b'] - st['gap']) < 0.011, st
    out.update({
        'x_rv_street_smi_share': f"{st['share']:.1f}",
        'x_rv_street_smi_dead_tf': f"{st['dead_a']:.2f}",
        'x_rv_street_smi_dead_hf': f"{st['dead_b']:.2f}",
        # one decimal, as Costantini's 4.6 beside it
        'x_rv_street_smi_pp': f"{st['gap']:.1f}",
    })
    # BLOCK 7'S CLOSING LINE (the author, 14 October, yes to changing it under rule C): of the revoked households with
    # SMI, the share the revocation puts on the street, from the Treatment First path's split masses in tables.md; under
    # rule C almost none (about 0.01 percent), so 'the main cost it imposes on those it screens out' no longer stands
    T = open(STREET).read().split('Housing First path')[0]
    sm = [(float(a), float(b)) for a, b in re.findall(r'SMI housed ([0-9.eE+-]+), SMI street ([0-9.eE+-]+)', T)]
    _sh = 100 * sum(b for _, b in sm) / sum(a + b for a, b in sm) if sm else None
    out['x_rv_street_close'] = (
        'Under the rule of Section~\\ref{sec:fvoucher}, however, almost no household with SMI whose voucher is revoked '
        'ends up on the street: nearly all find housing on their own. For the few who do, a higher risk of death is the '
        'cost, and the model does not understate it.' if _sh is not None and _sh < 1 else
        'A higher risk of death is the main cost Treatment First imposes on those it screens out, and the model does '
        'not understate it.')
    d = json.load(open(OUT_JSON))
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    for k, v in sorted(out.items()):
        print(f'  {k} = {v}')


if __name__ == '__main__':
    main()
