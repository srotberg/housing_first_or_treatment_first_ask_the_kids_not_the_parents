"""export_ca.py -- the run in which households with a SUD cannot respond to the screen at all (the author, 14 October:
"add a footnote at the appropriate first location to say that we also ran the experiment in which those with SUD
cannot respond at all, and results continue to hold. So the results do not depend on them being in treatment and
stopping to use"). That run is CA (code/RULE_C_PLAN.md, 01:00 14 October): rule A's screen on rule C's build, any use
and the disorder itself fail whether the household is in treatment or not, the government still pays for treatment,
detection 0.20, the drug price and pi_V clearing -> results/counterfactuals_2c/tf_pdet20_CA/passes.txt.

Reads the last pass and writes the x_ca_* names into results_numbers.json, beside the main experiment's x_tf_*:
the long-run falls in drug use, the SUD and homelessness, and how the fall in homelessness compares with the main
experiment's ('by more than' / 'by less than' / 'by about as much as' in it, within one percentage point). x_ca_done is 1 once the pass
meets the counterfactual's tolerances (drug market 5e-3, budget 1e-3); until then the footnote is yellow.
Run after export_results.py, which rewrites results_numbers.json whole."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
F = os.path.join(ROOT, 'results', 'counterfactuals_2c', 'tf_pdet20_CA', 'passes.txt')
OUT = os.path.join(HERE, 'results_numbers.json')
rows = [l.split() for l in open(F) if re.match(r'\s*\d+\s+\d\.\d+\s', l)]
r = rows[-1]
# pass  price  pi_V  b(chg)  SUD(chg)  h_1(chg)  drug gap  budget gap  welfare  CEV ...
b, sud, h = (float(x.rstrip('%')) for x in r[3:6])
dgap, bgap = float(r[6]), float(r[7])
d = json.load(open(OUT))
tf_h = float(d['x_tf_h_pc'])
gap = abs(h) - tf_h
out = {
    'x_ca_b_pc': f'{abs(b):.0f}', 'x_ca_sud_pc': f'{abs(sud):.0f}', 'x_ca_h_pc': f'{abs(h):.0f}',
    'x_ca_h_cmp': 'by more than' if gap > 1 else 'by less than' if gap < -1 else 'by about as much as',
    'x_ca_done': '1' if dgap < 5e-3 and bgap < 1e-3 else '0',
    'x_ca_pass': r[0],
}
d.update(out); json.dump(d, open(OUT, 'w'), indent=1, sort_keys=True)
print('export_ca:', out)
