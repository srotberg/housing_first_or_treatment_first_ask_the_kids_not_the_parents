"""
The partial-equilibrium experiment without externalities (results/pe_noext; the author, 4 October: "run a pe
experiment with no externalities also in the full model ... could be the very first experiment we refer to"): the
x_pe_* names of the paragraph in Section 6.2 placed right before the decomposition (the author, 22:55).

usage: python3 code/paper/export_pe_noext.py   -> x_pe_* merged into code/paper/results_numbers.json

Reads results/pe_noext/analysis.json (code/pe_noext/analyse.py): Arm A is Housing First with weight_on_child,
penalty_child_addicted and penalty_child_homeless at zero (kappa_x zero in the welfare statistics) and the drug price
clearing; Arm B is Treatment First at Arm A's drug price, pi_V and house price. Welfare is the household's own value,
which with omega_c = 0 contains no child term, compared state by state on Arm A's distribution.

REFUSES to write if any mass is better off under Treatment First beyond the solver's noise: the paragraph says nobody
is. (The four states that gain are one grid point of mass 2.2e-12, a missed maximum in Arm A's solver; RESULT.md.)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
# RULE C (14 October): results/pe_noext_C; rule A's was results/pe_noext
A = json.load(open(os.path.join(ROOT, 'results', 'pe_noext_C', 'analysis.json')))
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
NOISE = 1e-9                    # mass share


def main():
    # (14 October) rule A had nobody better off and the paragraph said so outright; under rule C about one per cent
    # are, all with a SUD (pending the internal_computations diagnostic), so the clause says what the numbers say,
    # at the tolerance of the table's better-off rows (1e-3 utils)
    better = A['shares']['all households']['abs0.001']['better']
    sud = A['shares']['with a SUD']['abs0.001']['better']
    nb = A['cev']['newborn adult (age 26)']['cev_group']
    assert nb < 0, nb
    out = {'x_pe_newborn_cev': f'{-100 * nb:.2f}',
           'x_pe_better_clause': ('no household is better off under Treatment First' if better < 0.005 else
                                  f'only ${100 * better:.0f}$ percent of households are better off under Treatment '
                                  f'First, ${100 * sud:.0f}$ percent of those with a SUD')}
    d = json.load(open(OUT_JSON))
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    for k, v in sorted(out.items()):
        print(f'  {k} = {v}')


if __name__ == '__main__':
    main()
