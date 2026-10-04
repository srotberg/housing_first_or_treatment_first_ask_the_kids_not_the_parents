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
RES = os.path.join(ROOT, 'results', 'revoked_2c')
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
    d = json.load(open(OUT_JSON))
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    for k, v in sorted(out.items()):
        print(f'  {k} = {v}')


if __name__ == '__main__':
    main()
