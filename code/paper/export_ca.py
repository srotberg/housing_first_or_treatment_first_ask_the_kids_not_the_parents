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
experiment is compared with (rulec_paths.NULL_DIR), not against the passes' base.

18 October, 01:30: the free-price run itself, results/counterfactuals_2c/tf_pdet20_CAu, was accepted at pass 49 (drug
market 5.3e-5, budget 8.6e-4), so the footnote reads it: the price clears in it, where tf_pdet20_CAbest was one pass of
it that happened to fall inside both rules."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import rulec_paths as RC
CA = os.path.join(ROOT, 'results', 'counterfactuals_2c', 'tf_pdet20_CAu')
OUT = os.path.join(HERE, 'results_numbers.json')
def levels(p):
    return {m.group(1).strip(): float(m.group(2)) for m in (re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l) for l in open(p)) if m}
x, y = levels(os.path.join(CA, 'tf', 'final.txt')), levels(os.path.join(RC.NULL_DIR, 'final.txt'))
b, sud, h = (100 * (x[k] / y[k] - 1) for k in ('drug use b', 'SUD lambda_d', 'homelessness h_1'))
P = open(os.path.join(CA, 'passes.txt')).read()
assert 'arm tf ACCEPTED' in P, f'{CA}/passes.txt: not accepted'
# the last pass of the tf section: pass price pi_V b SUD h_1 drug-gap budget-gap ...
_last = [l.split() for l in P.split('== tf')[1].splitlines() if re.match(r'\s*\d+\s+\d\.\d+\s', l)][-1]
dgap, bgap = float(_last[6]), float(_last[7])
d = json.load(open(OUT))
tf_h = float(d['x_tf_h_pc'])
gap = abs(h) - tf_h
out = {
    'x_ca_b_pc': f'{abs(b):.0f}', 'x_ca_sud_pc': f'{abs(sud):.0f}', 'x_ca_h_pc': f'{abs(h):.0f}',
    'x_ca_h_cmp': 'by more than' if gap > 1 else 'by less than' if gap < -1 else 'by about as much as',
    'x_ca_done': '1' if dgap < 5e-3 and bgap < 1e-3 else '0',
    'x_ca_pass': _last[0],
}
# THE NEWBORN, FOOTNOTE 36'S LAST CLAUSE (18 October, 23:00; it was yellow until a 20% no-escape end state landed): the
# newborn CEV of this cleared long run against the corrected Housing First, the main experiment's way (welfare_nok.cev_free,
# which gives x_tf_cev for the main arm); the clause keeps the author's 'at least as much' only while it is true
import welfare_nok
_nb = welfare_nok.cev_free(os.path.join(CA, 'tf')) - welfare_nok.cev_free(RC.NULL_DIR)
_tfc = float(d['x_tf_cev'])
out['x_ca_nb_cev'] = f'{_nb:.2f}'
out['x_ca_nb_clause'] = ('and a newborn gains at least as much' if round(_nb, 2) >= _tfc else
                         f'and a newborn gains ${_nb:.2f}$ percent, against ${_tfc:.2f}$ in the main experiment')
d.update(out); json.dump(d, open(OUT, 'w'), indent=1, sort_keys=True)
print('export_ca:', out)
