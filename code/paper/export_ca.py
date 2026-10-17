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
Run after export_results.py, which rewrites results_numbers.json whole.

17 October (the author: "you need to fix your mistakes, rerun them correctly", "double check that the long run runs
allowed the prices to clear"): tf_pdet20_CA cleared both markets but against the OLD Housing First's net revenue
(net_govt_revenue_constraint 5.8275447063 in its cf.log, the corrected one being 5.8371628), so the footnote compared a
run on the old budget with the corrected main experiment. It now reads the corrected no-escape run at detection 0.20,
results/counterfactuals_2c/tf_pdet20_CAbest (pass 13 of tf_pdet20_CAu, NET_TARGET 5.8371628, both markets inside their
tolerances: drug 3.87e-3, budget 3.08e-4), and takes its changes against the corrected Housing First the main
experiment is compared with (rulec_paths.NULL_DIR), not against the passes' base."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import rulec_paths as RC
CA = os.path.join(ROOT, 'results', 'counterfactuals_2c', 'tf_pdet20_CAbest')
OUT = os.path.join(HERE, 'results_numbers.json')
def levels(p):
    return {m.group(1).strip(): float(m.group(2)) for m in (re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l) for l in open(p)) if m}
x, y = levels(os.path.join(CA, 'tf', 'final.txt')), levels(os.path.join(RC.NULL_DIR, 'final.txt'))
b, sud, h = (100 * (x[k] / y[k] - 1) for k in ('drug use b', 'SUD lambda_d', 'homelessness h_1'))
P = open(os.path.join(CA, 'passes.txt')).read()
assert 'arm tf ACCEPTED' in P, f'{CA}/passes.txt: not accepted'
dgap, bgap = (float(v) for v in re.search(r'drug-market gap\s+(\S+) against 5e-3, budget gap\s+(\S+) against 1e-3', P).groups())
d = json.load(open(OUT))
tf_h = float(d['x_tf_h_pc'])
gap = abs(h) - tf_h
out = {
    'x_ca_b_pc': f'{abs(b):.0f}', 'x_ca_sud_pc': f'{abs(sud):.0f}', 'x_ca_h_pc': f'{abs(h):.0f}',
    'x_ca_h_cmp': 'by more than' if gap > 1 else 'by less than' if gap < -1 else 'by about as much as',
    'x_ca_done': '1' if dgap < 5e-3 and bgap < 1e-3 else '0',
    'x_ca_pass': re.search(r'pass (\d+) of', P).group(1),
}
d.update(out); json.dump(d, open(OUT, 'w'), indent=1, sort_keys=True)
print('export_ca:', out)
